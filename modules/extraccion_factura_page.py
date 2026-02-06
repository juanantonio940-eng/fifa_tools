#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MÓDULO EXTRACCIÓN FACTURA - Streamlit
======================================
Extrae datos de facturas PDF con detección de moneda ISO 4217
y detección de anomalías/erratas.
"""

import streamlit as st
import re
import csv
import os
import io
import tempfile
from collections import defaultdict

try:
    import pdfplumber
    PDFPLUMBER_OK = True
except ImportError:
    PDFPLUMBER_OK = False

import pandas as pd


# =============================================================================
# TRADUCCIONES
# =============================================================================

TRADUCCIONES = {
    "es": {
        "titulo": "Extracción de Facturas PDF",
        "subtitulo": "Extrae datos de facturas FIFA con detección de moneda y anomalías",
        "subir_pdfs": "Subir archivos PDF",
        "modo_debug": "Modo debug (mostrar detalles)",
        "btn_procesar": "Procesar PDFs",
        "procesando": "Procesando...",
        "progreso": "Progreso",
        "resultados": "Resultados",
        "anomalias": "Anomalías",
        "log": "Log de procesamiento",
        "descargar_csv": "Descargar CSV",
        "descargar_reporte": "Descargar Reporte Anomalías",
        "total_pdfs": "PDFs procesados",
        "total_items": "Items extraídos",
        "total_anomalias": "Anomalías detectadas",
        "sin_datos": "No se extrajeron datos de los PDFs subidos",
        "sin_anomalias": "No se detectaron anomalías",
        "sin_pdfs": "Sube uno o más archivos PDF para comenzar",
        "error_pdfplumber": "pdfplumber no está instalado. Ejecuta: pip install pdfplumber",
        "archivo": "Archivo",
        "factura": "Factura",
        "entidad": "Entidad",
        "moneda": "Moneda",
        "items": "Items",
        "resumen_por_pdf": "Resumen por PDF",
    },
    "en": {
        "titulo": "PDF Invoice Extraction",
        "subtitulo": "Extract FIFA invoice data with currency detection and anomaly detection",
        "subir_pdfs": "Upload PDF files",
        "modo_debug": "Debug mode (show details)",
        "btn_procesar": "Process PDFs",
        "procesando": "Processing...",
        "progreso": "Progress",
        "resultados": "Results",
        "anomalias": "Anomalies",
        "log": "Processing log",
        "descargar_csv": "Download CSV",
        "descargar_reporte": "Download Anomaly Report",
        "total_pdfs": "PDFs processed",
        "total_items": "Items extracted",
        "total_anomalias": "Anomalies detected",
        "sin_datos": "No data extracted from uploaded PDFs",
        "sin_anomalias": "No anomalies detected",
        "sin_pdfs": "Upload one or more PDF files to begin",
        "error_pdfplumber": "pdfplumber is not installed. Run: pip install pdfplumber",
        "archivo": "File",
        "factura": "Invoice",
        "entidad": "Entity",
        "moneda": "Currency",
        "items": "Items",
        "resumen_por_pdf": "Summary per PDF",
    },
    "hi": {
        "titulo": "PDF चालान निष्कर्षण",
        "subtitulo": "मुद्रा पहचान और विसंगति पहचान के साथ FIFA चालान डेटा निकालें",
        "subir_pdfs": "PDF फ़ाइलें अपलोड करें",
        "modo_debug": "डिबग मोड (विवरण दिखाएं)",
        "btn_procesar": "PDFs प्रोसेस करें",
        "procesando": "प्रोसेसिंग...",
        "progreso": "प्रगति",
        "resultados": "परिणाम",
        "anomalias": "विसंगतियाँ",
        "log": "प्रोसेसिंग लॉग",
        "descargar_csv": "CSV डाउनलोड करें",
        "descargar_reporte": "विसंगति रिपोर्ट डाउनलोड करें",
        "total_pdfs": "PDFs प्रोसेस किए गए",
        "total_items": "आइटम निकाले गए",
        "total_anomalias": "विसंगतियाँ पाई गईं",
        "sin_datos": "अपलोड किए गए PDFs से कोई डेटा नहीं निकाला गया",
        "sin_anomalias": "कोई विसंगति नहीं पाई गई",
        "sin_pdfs": "शुरू करने के लिए एक या अधिक PDF फ़ाइलें अपलोड करें",
        "error_pdfplumber": "pdfplumber इंस्टॉल नहीं है। चलाएं: pip install pdfplumber",
        "archivo": "फ़ाइल",
        "factura": "चालान",
        "entidad": "संस्था",
        "moneda": "मुद्रा",
        "items": "आइटम",
        "resumen_por_pdf": "PDF के अनुसार सारांश",
    },
}


# =============================================================================
# DETECTOR DE ANOMALÍAS
# =============================================================================

class DetectorAnomalias:
    def __init__(self):
        self.anomalias = []
        self.estadisticas = defaultdict(int)

    def reset(self):
        self.anomalias = []
        self.estadisticas = defaultdict(int)

    def detectar_variables_sin_expandir(self, texto, contexto=""):
        patrones = [
            (r'\$[a-zA-Z_][a-zA-Z0-9_]*', 'Variable sin expandir tipo $variable'),
            (r'\${[^}]+}', 'Variable sin expandir tipo ${variable}'),
            (r'%[a-zA-Z_][a-zA-Z0-9_]*%', 'Variable sin expandir tipo %variable%'),
            (r'{{[^}]+}}', 'Variable sin expandir tipo {{variable}}'),
            (r'\[\[[^\]]+\]\]', 'Variable sin expandir tipo [[variable]]'),
        ]
        anomalias_encontradas = []
        for patron, tipo in patrones:
            for match in re.finditer(patron, texto):
                anomalia = {
                    'tipo': 'ERRATA_VARIABLE', 'descripcion': tipo,
                    'valor': match.group(), 'contexto': contexto, 'posicion': match.start()
                }
                anomalias_encontradas.append(anomalia)
                self.estadisticas[tipo] += 1
        return anomalias_encontradas

    def detectar_erratas_comunes(self, texto, contexto=""):
        anomalias_encontradas = []
        erratas = {
            r'\b(\w+)\s+\1\b': 'Palabra duplicada',
            r'[^\s]\s{3,}[^\s]': 'Espaciado excesivo',
            r'\bnull\b|\bNULL\b|\bNone\b': 'Valores null no procesados',
            r'undefined|UNDEFINED': 'Valores undefined',
            r'#N/A|#REF!|#VALUE!|#NAME\?': 'Errores de Excel/fórmula',
        }
        for patron, descripcion in erratas.items():
            for match in re.finditer(patron, texto, re.IGNORECASE):
                anomalia = {
                    'tipo': 'ERRATA_PATRON', 'descripcion': descripcion,
                    'valor': match.group(), 'contexto': contexto, 'posicion': match.start()
                }
                anomalias_encontradas.append(anomalia)
                self.estadisticas[descripcion] += 1
        return anomalias_encontradas

    def validar_consistencia_match(self, descripcion):
        anomalias_encontradas = []
        if 'MATCH' in descripcion.upper():
            if '$' in descripcion:
                anomalias_encontradas.append({
                    'tipo': 'MATCH_INVALIDO',
                    'descripcion': 'Variable sin expandir en descripción de MATCH',
                    'valor': descripcion, 'contexto': 'Validación de MATCH'
                })
            elif re.search(r'MATCH\s*$', descripcion):
                anomalias_encontradas.append({
                    'tipo': 'MATCH_INCOMPLETO',
                    'descripcion': 'MATCH sin número ordinal',
                    'valor': descripcion, 'contexto': 'Validación de MATCH'
                })
        return anomalias_encontradas

    def validar_montos(self, item):
        anomalias_encontradas = []
        try:
            cantidad = float(item.get('cantidad', '0') or '0')
            precio_unitario = self._limpiar_monto(item.get('precio_unitario', '0'))
            neto = self._limpiar_monto(item.get('neto', '0'))
            impuesto = self._limpiar_monto(item.get('impuesto', '0'))
            total = self._limpiar_monto(item.get('total', '0'))

            neto_calculado = cantidad * precio_unitario
            if abs(neto_calculado - neto) > 0.01 and neto > 0:
                anomalias_encontradas.append({
                    'tipo': 'CALCULO_INCORRECTO',
                    'descripcion': f'Neto incorrecto: {cantidad} x {precio_unitario} = {neto_calculado}, pero muestra {neto}',
                    'valor': item.get('descripcion', ''), 'contexto': 'Validación de montos'
                })
            total_calculado = neto + impuesto
            if abs(total_calculado - total) > 0.01 and total > 0:
                anomalias_encontradas.append({
                    'tipo': 'TOTAL_INCORRECTO',
                    'descripcion': f'Total incorrecto: {neto} + {impuesto} = {total_calculado}, pero muestra {total}',
                    'valor': item.get('descripcion', ''), 'contexto': 'Validación de totales'
                })
            if precio_unitario > 10000:
                anomalias_encontradas.append({
                    'tipo': 'MONTO_SOSPECHOSO',
                    'descripcion': f'Precio unitario muy alto: ${precio_unitario}',
                    'valor': item.get('descripcion', ''), 'contexto': 'Validación de rangos'
                })
        except (ValueError, TypeError) as e:
            anomalias_encontradas.append({
                'tipo': 'ERROR_CONVERSION',
                'descripcion': f'Error al convertir montos: {e}',
                'valor': item.get('descripcion', ''), 'contexto': 'Validación de montos'
            })
        return anomalias_encontradas

    def _limpiar_monto(self, monto_str):
        if not monto_str or monto_str == '-':
            return 0.0
        monto_limpio = re.sub(r'[$,]', '', str(monto_str))
        monto_limpio = re.sub(r'\s*[A-Z]{3}\s*$', '', monto_limpio)
        try:
            return float(monto_limpio)
        except:
            return 0.0

    def generar_reporte(self):
        reporte = []
        reporte.append("=" * 80)
        reporte.append("REPORTE DE ANOMALÍAS Y ERRATAS EN FACTURAS")
        reporte.append("=" * 80)
        reporte.append(f"Total de anomalías encontradas: {len(self.anomalias)}\n")

        por_tipo = defaultdict(list)
        for anomalia in self.anomalias:
            por_tipo[anomalia['tipo']].append(anomalia)

        reporte.append("RESUMEN POR TIPO DE ANOMALÍA:")
        reporte.append("-" * 40)
        for tipo, items in por_tipo.items():
            reporte.append(f"{tipo}: {len(items)} ocurrencias")

        reporte.append("\n" + "=" * 80)
        reporte.append("DETALLES DE ANOMALÍAS:")
        reporte.append("=" * 80)

        for tipo, items in por_tipo.items():
            reporte.append(f"\n{tipo} ({len(items)} ocurrencias):")
            reporte.append("-" * 40)
            for i, item in enumerate(items[:10], 1):
                reporte.append(f"{i}. {item['descripcion']}")
                reporte.append(f"   Valor: {item['valor'][:100]}")
                reporte.append(f"   Contexto: {item['contexto']}")
                reporte.append("")
            if len(items) > 10:
                reporte.append(f"   ... y {len(items) - 10} más\n")

        return "\n".join(reporte)


# =============================================================================
# FUNCIONES DE EXTRACCIÓN
# =============================================================================

MONEDAS_VALIDAS = ['USD', 'EUR', 'GBP', 'CAD', 'MXN', 'CHF', 'AUD', 'JPY', 'CNY', 'BRL', 'ARS', 'COP', 'CLP', 'PEN']

CAMPOS_CSV = [
    'fecha_archivo', 'email_orden',
    'numero_factura', 'entidad_vendedora', 'fecha_factura',
    'referencia_cliente', 'referencia_orden',
    'descripcion', 'tax_rate',
    'categoria', 'cantidad', 'precio_unitario', 'neto', 'impuesto', 'total'
]


def extraer_info_factura(texto):
    info = {}
    match_factura = re.search(r'FU-\d+-[A-Z]+|FM-\d+-[A-Z]+', texto)
    if match_factura:
        info['numero_factura'] = match_factura.group()

    if 'FWC2026 Mexico' in texto:
        info['entidad_vendedora'] = 'FWC2026 Mexico, S. de R.L. de C.V.'
    elif 'FWC2026 US' in texto:
        info['entidad_vendedora'] = 'FWC2026 US, Inc.'
    elif 'FWC26 Canada' in texto:
        info['entidad_vendedora'] = 'FWC26 Canada Football Ltd.'

    match_fecha = re.search(r'Invoice Date:\s*(\d{1,2}\s+\w+\s+\d{4})', texto)
    if match_fecha:
        info['fecha_factura'] = match_fecha.group(1)

    match_customer = re.search(r'Our Customer Reference:\s*(\d+)', texto)
    if match_customer:
        info['referencia_cliente'] = match_customer.group(1)

    match_order = re.search(r'Our Order Reference:\s*(\d+)', texto)
    if match_order:
        info['referencia_orden'] = match_order.group(1)

    info['moneda'] = ''

    if 'ALL AMOUNTS IN MEXICAN PESOS' in texto.upper():
        info['moneda'] = 'MXN'
        return info
    elif 'ALL AMOUNTS IN US DOLLARS' in texto.upper() or 'ALL AMOUNTS IN USD' in texto.upper():
        info['moneda'] = 'USD'
        return info
    elif 'ALL AMOUNTS IN CANADIAN DOLLARS' in texto.upper():
        info['moneda'] = 'CAD'
        return info

    match_moneda = re.search(r'(?:GROSS|TOTAL|AMOUNT|NETO|NET|PRICE)\s+([A-Z]{3})\b', texto)
    if match_moneda:
        moneda_candidata = match_moneda.group(1)
        if moneda_candidata in MONEDAS_VALIDAS:
            info['moneda'] = moneda_candidata

    if not info['moneda']:
        texto_inicio = texto[:int(len(texto) * 0.66)]
        match_monto = re.search(r'[\d,]+\.\d{2}\s+([A-Z]{3})\b', texto_inicio)
        if match_monto:
            moneda_candidata = match_monto.group(1)
            if moneda_candidata in MONEDAS_VALIDAS:
                info['moneda'] = moneda_candidata

    if not info['moneda']:
        texto_inicio = texto[:int(len(texto) * 0.66)]
        for moneda in MONEDAS_VALIDAS:
            if re.search(r'(?<![A-Z])' + moneda + r'(?![A-Z])', texto_inicio):
                info['moneda'] = moneda
                break

    return info


def limpiar_celda(celda):
    if celda is None:
        return ''
    texto = str(celda).replace('\n', ' ').strip()
    texto = re.sub(r'\s+', ' ', texto)
    return texto


def normalizar_tax_rate(tax_rate):
    if not tax_rate or tax_rate == '-':
        return tax_rate
    if '.' in tax_rate and '%' in tax_rate:
        return tax_rate
    if '%' not in tax_rate:
        if 'USD' in tax_rate or 'usd' in tax_rate.lower():
            return tax_rate
        try:
            float(tax_rate.replace(',', ''))
            tax_rate = tax_rate + '%'
        except:
            return tax_rate
    if '%' in tax_rate and '.' not in tax_rate:
        numeros = ''.join([c for c in tax_rate if c.isdigit()])
        if not numeros:
            return tax_rate
        if len(numeros) == 4:
            tax_rate = f"{numeros[0]}.{numeros[1:]}%"
        elif len(numeros) == 3:
            primeros_dos = int(numeros[0:2])
            if primeros_dos >= 10:
                tax_rate = f"{primeros_dos}.{numeros[2]}%"
            else:
                tax_rate = f"{numeros[0]}.{numeros[1:]}%"
        elif len(numeros) == 2:
            primer_numero = int(numeros)
            if primer_numero >= 10:
                tax_rate = f"{numeros}.0%"
            else:
                tax_rate = f"{numeros[0]}.{numeros[1]}%"
        elif len(numeros) == 1:
            tax_rate = f"{numeros}.0%"
    return tax_rate


def extraer_moneda_de_pagina_resumen(page):
    texto = page.extract_text()
    if texto:
        texto_upper = texto.upper()
        lineas = texto_upper.split('\n')
        for i, linea in enumerate(lineas):
            if 'GROSS' in linea:
                for moneda in MONEDAS_VALIDAS:
                    if moneda in linea:
                        return moneda
                if i + 1 < len(lineas):
                    linea_siguiente = lineas[i + 1].strip()
                    if linea_siguiente in MONEDAS_VALIDAS:
                        return linea_siguiente
        for moneda in MONEDAS_VALIDAS:
            for patron in [f"GROSS\n{moneda}", f"GROSS {moneda}", f"GROSS\t{moneda}"]:
                if patron in texto_upper:
                    return moneda

    configs = [
        {"vertical_strategy": "lines", "horizontal_strategy": "lines", "snap_tolerance": 5, "join_tolerance": 5},
        {"vertical_strategy": "text", "horizontal_strategy": "lines", "snap_tolerance": 8},
        {"vertical_strategy": "lines", "horizontal_strategy": "text", "snap_tolerance": 5}
    ]
    for config in configs:
        tablas = page.extract_tables(table_settings=config)
        if not tablas:
            continue
        for tabla in tablas:
            if not tabla:
                continue
            tiene_gross = any(
                fila and any('GROSS' in str(celda).upper() if celda else False for celda in fila)
                for fila in tabla
            )
            if not tiene_gross:
                continue
            for i, fila in enumerate(tabla):
                if not fila:
                    continue
                for j, celda in enumerate(fila):
                    if not celda:
                        continue
                    celda_str = str(celda).upper().strip()
                    if 'GROSS' in celda_str:
                        for parte in celda_str.replace('\n', ' ').split():
                            if parte in MONEDAS_VALIDAS:
                                return parte
                        if i + 1 < len(tabla) and j < len(tabla[i + 1]):
                            celda_siguiente = str(tabla[i + 1][j]).upper().strip() if tabla[i + 1][j] else ''
                            if celda_siguiente in MONEDAS_VALIDAS:
                                return celda_siguiente
    return ''


def extraer_moneda_de_tabla(tabla):
    for fila in tabla[:3]:
        if not fila:
            continue
        for celda in fila:
            if not celda:
                continue
            celda_str = str(celda).upper()
            match = re.search(r'(?:GROSS|TOTAL|AMOUNT|NETO|NET|PRICE)\s+([A-Z]{3})\b', celda_str)
            if match and match.group(1) in MONEDAS_VALIDAS:
                return match.group(1)
            if celda_str.strip() in MONEDAS_VALIDAS:
                return celda_str.strip()
            for moneda_valida in MONEDAS_VALIDAS:
                if re.search(r'(?<![A-Z])' + moneda_valida + r'(?![A-Z])', celda_str):
                    return moneda_valida
    return ''


def extraer_items_tabla(page, detector):
    items = []
    moneda_encontrada = ''
    configs = [
        {"vertical_strategy": "lines", "horizontal_strategy": "lines",
         "snap_tolerance": 5, "join_tolerance": 5, "edge_min_length": 50, "intersection_tolerance": 10},
        {"vertical_strategy": "text", "horizontal_strategy": "lines", "snap_tolerance": 8},
        {"vertical_strategy": "lines", "horizontal_strategy": "text", "snap_tolerance": 5}
    ]
    for config in configs:
        tablas = page.extract_tables(table_settings=config)
        if not tablas:
            continue
        items_temp = []
        for tabla in tablas:
            if not tabla or len(tabla) < 2:
                continue
            if not moneda_encontrada:
                moneda_temp = extraer_moneda_de_tabla(tabla)
                if moneda_temp in MONEDAS_VALIDAS:
                    moneda_encontrada = moneda_temp
            header_idx = None
            for i, fila in enumerate(tabla):
                if fila and any('YOUR PURCHASES' in str(cell) for cell in fila if cell):
                    header_idx = i
                    break
            if header_idx is None:
                continue
            for j in range(header_idx + 1, len(tabla)):
                row = tabla[j]
                if not row or len(row) < 4:
                    continue
                row_limpia = [limpiar_celda(cell) for cell in row]
                descripcion = row_limpia[0] if row_limpia else ''
                if descripcion and detector:
                    detector.anomalias.extend(detector.detectar_variables_sin_expandir(descripcion, "Item de factura"))
                    detector.anomalias.extend(detector.detectar_erratas_comunes(descripcion, "Item de factura"))
                    detector.anomalias.extend(detector.validar_consistencia_match(descripcion))
                if not descripcion or descripcion.startswith('*') or 'Amounts include value-added' in descripcion:
                    continue
                if descripcion.strip() == 'TST: MEXICO':
                    continue
                es_match = 'MATCH' in descripcion and ':' in descripcion
                es_tst = 'TST:' in descripcion and 'MEXICO' in descripcion
                if not (es_match or es_tst):
                    continue
                tax_rate = normalizar_tax_rate(row_limpia[1] if len(row_limpia) > 1 else '')
                categoria = row_limpia[2] if len(row_limpia) > 2 else ''
                cantidad = row_limpia[3] if len(row_limpia) > 3 else ''
                precio_unitario = row_limpia[4] if len(row_limpia) > 4 else ''
                neto = row_limpia[5] if len(row_limpia) > 5 else ''
                impuesto = row_limpia[6] if len(row_limpia) > 6 else ''
                total = row_limpia[7] if len(row_limpia) > 7 else ''
                if not cantidad or cantidad == '-':
                    continue
                try:
                    int(cantidad)
                except:
                    continue
                item = {
                    'descripcion': descripcion, 'tax_rate': tax_rate, 'categoria': categoria,
                    'cantidad': cantidad, 'precio_unitario': precio_unitario,
                    'neto': neto, 'impuesto': impuesto if impuesto != '-' else '',
                    'total': total, 'moneda_temp': moneda_encontrada
                }
                if detector:
                    detector.anomalias.extend(detector.validar_montos(item))
                items_temp.append(item)
        if items_temp:
            items = items_temp
            break
    return items


def extraer_info_nombre_archivo(nombre_archivo):
    info = {'fecha_archivo': '', 'email_orden': ''}
    nombre_sin_ext = nombre_archivo.replace('.pdf', '').replace('.PDF', '')
    match_fecha = re.match(r'^(\d{7,8})_', nombre_sin_ext)
    if match_fecha:
        fecha = match_fecha.group(1)
        try:
            if len(fecha) == 8:
                a, m, d = int(fecha[0:4]), int(fecha[4:6]), int(fecha[6:8])
                if 2020 <= a <= 2030 and 1 <= m <= 12 and 1 <= d <= 31:
                    info['fecha_archivo'] = f"{fecha[0:4]}-{fecha[4:6]}-{fecha[6:8]}"
            elif len(fecha) == 7:
                a, m, d = int(fecha[0:4]), int(fecha[4:6]), int(fecha[6:7])
                if 2020 <= a <= 2030 and 1 <= m <= 12 and 1 <= d <= 9:
                    info['fecha_archivo'] = f"{fecha[0:4]}-{fecha[4:6]}-0{fecha[6:7]}"
        except:
            pass
    if '@' in nombre_sin_ext:
        match_email = re.search(r'^\d{7,8}_\d{6,7}_([\w\.\-]+@[\w\.\-]+\.[a-zA-Z]{2,})', nombre_sin_ext)
        if match_email:
            info['email_orden'] = match_email.group(1)
        else:
            match_fb = re.search(r'([a-zA-Z0-9][\w\.\-]*@[\w\.\-]+\.[a-zA-Z]{2,})', nombre_sin_ext)
            if match_fb:
                info['email_orden'] = match_fb.group(1)
    return info


def procesar_pdf(ruta_pdf, nombre_archivo, detector):
    resultados = []
    moneda_global = ''
    info_archivo = extraer_info_nombre_archivo(nombre_archivo)

    with pdfplumber.open(ruta_pdf) as pdf:
        if len(pdf.pages) > 0:
            moneda_global = extraer_moneda_de_pagina_resumen(pdf.pages[0])
            if not moneda_global:
                texto_resumen = pdf.pages[0].extract_text()
                if texto_resumen:
                    info_r = extraer_info_factura(texto_resumen)
                    if info_r.get('moneda') and info_r['moneda'] in MONEDAS_VALIDAS:
                        moneda_global = info_r['moneda']
            if detector:
                texto_resumen = pdf.pages[0].extract_text()
                if texto_resumen:
                    detector.anomalias.extend(
                        detector.detectar_variables_sin_expandir(texto_resumen, f"Resumen de {nombre_archivo}")
                    )

        for i, page in enumerate(pdf.pages):
            if i == 0:
                continue
            texto = page.extract_text()
            if texto and detector:
                detector.anomalias.extend(
                    detector.detectar_variables_sin_expandir(texto, f"Página {i + 1} de {nombre_archivo}")
                )
            info_factura = extraer_info_factura(texto)
            if info_factura.get('moneda') and info_factura['moneda'] in MONEDAS_VALIDAS:
                if not moneda_global:
                    moneda_global = info_factura['moneda']
            elif moneda_global:
                info_factura['moneda'] = moneda_global

            items = extraer_items_tabla(page, detector)

            for item in items:
                moneda_a_usar = ''
                if item.get('moneda_temp') and item['moneda_temp'] in MONEDAS_VALIDAS:
                    moneda_a_usar = item['moneda_temp']
                elif info_factura.get('moneda') and info_factura['moneda'] in MONEDAS_VALIDAS:
                    moneda_a_usar = info_factura['moneda']
                else:
                    moneda_a_usar = moneda_global
                if moneda_a_usar not in MONEDAS_VALIDAS:
                    moneda_a_usar = ''
                if moneda_a_usar and item.get('precio_unitario') and item['precio_unitario'] != '-':
                    item['precio_unitario'] = f"{item['precio_unitario']} {moneda_a_usar}"

                registro = {
                    'fecha_archivo': info_archivo['fecha_archivo'],
                    'email_orden': info_archivo['email_orden'],
                    'numero_factura': info_factura.get('numero_factura', ''),
                    'entidad_vendedora': info_factura.get('entidad_vendedora', ''),
                    'fecha_factura': info_factura.get('fecha_factura', ''),
                    'referencia_cliente': info_factura.get('referencia_cliente', ''),
                    'referencia_orden': info_factura.get('referencia_orden', ''),
                    'descripcion': item.get('descripcion', ''),
                    'tax_rate': item.get('tax_rate', ''),
                    'categoria': item.get('categoria', ''),
                    'cantidad': item.get('cantidad', ''),
                    'precio_unitario': item.get('precio_unitario', ''),
                    'neto': item.get('neto', ''),
                    'impuesto': item.get('impuesto', ''),
                    'total': item.get('total', '')
                }
                resultados.append(registro)

    return resultados


# =============================================================================
# RENDER STREAMLIT
# =============================================================================

def render():
    lang = st.session_state.get("language", "es")
    t = TRADUCCIONES.get(lang, TRADUCCIONES["es"])

    st.title(f"📄 {t['titulo']}")
    st.caption(t['subtitulo'])

    if not PDFPLUMBER_OK:
        st.error(t['error_pdfplumber'])
        return

    # Subida de archivos
    uploaded_files = st.file_uploader(
        t['subir_pdfs'],
        type=["pdf"],
        accept_multiple_files=True,
        key="ef_uploader"
    )

    debug = st.checkbox(t['modo_debug'], key="ef_debug")

    if not uploaded_files:
        st.info(t['sin_pdfs'])
        return

    if st.button(t['btn_procesar'], type="primary", key="ef_procesar"):
        detector = DetectorAnomalias()
        todos_resultados = []
        log_mensajes = []
        resumen_pdfs = []

        progress_bar = st.progress(0, text=t['procesando'])
        total = len(uploaded_files)

        for idx, uploaded_file in enumerate(uploaded_files):
            nombre = uploaded_file.name
            progress_bar.progress((idx) / total, text=f"{t['procesando']} {nombre}")
            log_mensajes.append(f"Procesando: {nombre}")

            try:
                # Guardar en temporal para pdfplumber
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name

                anomalias_antes = len(detector.anomalias)
                resultados = procesar_pdf(tmp_path, nombre, detector)
                todos_resultados.extend(resultados)
                anomalias_nuevas = len(detector.anomalias) - anomalias_antes

                # Info resumen
                factura = resultados[0].get('numero_factura', '') if resultados else ''
                entidad = resultados[0].get('entidad_vendedora', '') if resultados else ''
                moneda = ''
                if resultados:
                    pu = resultados[0].get('precio_unitario', '')
                    for m in MONEDAS_VALIDAS:
                        if m in pu:
                            moneda = m
                            break

                resumen_pdfs.append({
                    t['archivo']: nombre,
                    t['factura']: factura,
                    t['entidad']: entidad,
                    t['moneda']: moneda,
                    t['items']: len(resultados),
                    t['anomalias']: anomalias_nuevas
                })

                log_mensajes.append(f"  > {len(resultados)} registros extraídos")
                if anomalias_nuevas > 0:
                    log_mensajes.append(f"  ! {anomalias_nuevas} anomalías")

                # Limpiar temporal
                os.unlink(tmp_path)

            except Exception as e:
                log_mensajes.append(f"  X Error: {e}")
                resumen_pdfs.append({
                    t['archivo']: nombre,
                    t['factura']: 'ERROR',
                    t['entidad']: '',
                    t['moneda']: '',
                    t['items']: 0,
                    t['anomalias']: '-'
                })
                if debug:
                    import traceback
                    log_mensajes.append(traceback.format_exc())

        progress_bar.progress(1.0, text="Completado")

        # Métricas
        col1, col2, col3 = st.columns(3)
        col1.metric(t['total_pdfs'], total)
        col2.metric(t['total_items'], len(todos_resultados))
        col3.metric(t['total_anomalias'], len(detector.anomalias))

        st.markdown("---")

        # Pestañas de resultados
        tab_res, tab_anom, tab_log = st.tabs([t['resultados'], t['anomalias'], t['log']])

        with tab_res:
            # Resumen por PDF
            if resumen_pdfs:
                st.subheader(t['resumen_por_pdf'])
                st.dataframe(pd.DataFrame(resumen_pdfs), use_container_width=True, hide_index=True)

            # Tabla completa de datos
            if todos_resultados:
                st.subheader(t['resultados'])
                df = pd.DataFrame(todos_resultados)
                st.dataframe(df, use_container_width=True, hide_index=True)

                # Botón descargar CSV
                csv_buffer = io.StringIO()
                writer = csv.DictWriter(csv_buffer, fieldnames=CAMPOS_CSV)
                writer.writeheader()
                writer.writerows(todos_resultados)
                st.download_button(
                    t['descargar_csv'],
                    csv_buffer.getvalue(),
                    file_name="facturas_extraidas.csv",
                    mime="text/csv",
                    key="ef_download_csv"
                )
            else:
                st.warning(t['sin_datos'])

        with tab_anom:
            if detector.anomalias:
                reporte = detector.generar_reporte()
                st.text(reporte)
                st.download_button(
                    t['descargar_reporte'],
                    reporte,
                    file_name="anomalias_detectadas.txt",
                    mime="text/plain",
                    key="ef_download_report"
                )
            else:
                st.success(t['sin_anomalias'])

        with tab_log:
            st.code("\n".join(log_mensajes), language=None)
