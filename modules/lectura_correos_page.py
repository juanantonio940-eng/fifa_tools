#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PAGINA LECTURA CORREOS v4
=========================
Lectura de correos IMAP con filtros robustos, extraccion FIFA avanzada,
descarga de adjuntos y gestion de cuentas via CSV.

Basado en Lectura_grafico_webhookv4.py (sin funciones webhook/monitor).
"""

import streamlit as st
import imaplib
import email
import email.utils
from email.header import decode_header
from email.utils import getaddresses
import ssl
import re
import csv
import time
import io
import os
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, date, timedelta
from io import BytesIO
from typing import Dict, List, Optional, Tuple

# === TRADUCCIONES ===
TRANSLATIONS = {
    "es": {
        "title": "Lectura de Correos",
        "subtitle": "Lee correos de multiples cuentas IMAP con filtros avanzados",
        "tab_accounts": "Cuentas",
        "tab_search": "Busqueda",
        "tab_results": "Resultados",
        "tab_fifa": "FIFA",
        "tab_logs": "Logs",
        # Tab Cuentas
        "accounts_upload": "Subir archivo CSV de cuentas",
        "accounts_upload_help": "CSV con formato: email,password (una cuenta por linea, sin cabecera)",
        "accounts_manual": "O pega las cuentas manualmente",
        "accounts_placeholder": "usuario1@icloud.com,password1\nusuario2@gmail.com,password2",
        "accounts_help": "Formato: email,password (una por linea)",
        "btn_load_accounts": "Cargar Cuentas",
        "btn_connect_selected": "Conectar Seleccionadas",
        "btn_connect_all": "Conectar Todas",
        "btn_disconnect": "Desconectar Todas",
        "select_accounts": "Selecciona las cuentas a conectar",
        "connecting": "Conectando",
        "connected": "Conectada",
        "disconnected": "Desconectada",
        "failed": "Error",
        "no_accounts": "No hay cuentas cargadas",
        "connection_status": "Estado de Conexiones",
        "accounts_connected": "cuentas conectadas",
        "accounts_loaded": "cuentas cargadas",
        "create_example": "Descargar CSV de ejemplo",
        # Tab Busqueda
        "search_title": "Criterios de Busqueda",
        "filter_subject": "Asunto contiene",
        "filter_sender": "Remitente contiene",
        "filter_recipient": "Destinatario contiene",
        "filter_content": "Contenido contiene (filtro local)",
        "filter_date_from": "Fecha desde",
        "filter_status": "Estado de lectura",
        "filter_folder": "Carpeta IMAP",
        "filter_limit": "Limite por cuenta",
        "status_all": "Todos",
        "status_unread": "No leidos",
        "status_read": "Leidos",
        "btn_search": "Buscar en Todas",
        "btn_search_unread": "Solo No Leidos",
        "btn_search_read": "Solo Leidos",
        "searching": "Buscando correos...",
        "search_account": "Buscando en",
        "no_connections": "No hay cuentas conectadas. Ve a la pestana Cuentas primero.",
        "search_results": "correos encontrados",
        "filtered_local": "filtrados localmente",
        # Tab Resultados
        "no_results": "No hay resultados. Realiza una busqueda primero.",
        "results_count": "correos encontrados",
        "col_account": "Cuenta",
        "col_from": "De",
        "col_to": "Para",
        "col_subject": "Asunto",
        "col_date": "Fecha",
        "col_status": "Estado",
        "col_preview": "Vista previa",
        "btn_mark_read": "Marcar como Leido",
        "btn_mark_selected_read": "Marcar Seleccionados como Leidos",
        "btn_export_csv": "Exportar CSV",
        "btn_export_all_csv": "Exportar Todos a CSV",
        "btn_download_attachments": "Descargar Adjuntos",
        "btn_clear_results": "Limpiar Resultados",
        "marking": "Marcando como leido...",
        "marked_success": "correos marcados como leidos",
        "view_details": "Ver detalles",
        "email_body": "Contenido",
        "email_html": "HTML Original",
        "attachments": "Adjuntos",
        "no_attachments": "Sin adjuntos",
        # FIFA
        "fifa_section": "Extraccion FIFA World Cup 2026",
        "fifa_description": "Extrae informacion detallada de tickets FIFA: partido, categoria, cantidad, precio, titular, equipo",
        "btn_extract_fifa": "Extraer Datos FIFA",
        "btn_extract_fifa_all": "Extraer de Todos",
        "btn_extract_fifa_unread": "Extraer de No Leidos",
        "extracting_fifa": "Extrayendo datos FIFA...",
        "fifa_no_data": "No se encontraron datos FIFA en los correos",
        "fifa_found": "tickets FIFA encontrados",
        "btn_export_excel": "Exportar Excel",
        "btn_export_fifa_csv": "Exportar CSV",
        "fifa_mark_read": "Marcar como leido al extraer",
        "fifa_filter": "Filtrar por estado",
        "fifa_col_email_madre": "Email Madre",
        "fifa_col_cuenta": "Cuenta FIFA",
        "fifa_col_applicant": "Solicitante",
        "fifa_col_team": "Equipo",
        "fifa_col_date": "Fecha Email",
        "fifa_col_match": "Partido",
        "fifa_col_type": "Tipo Ticket",
        "fifa_col_category": "Categoria",
        "fifa_col_holder": "Titular",
        "fifa_col_quantity": "Cantidad",
        "fifa_col_price": "Precio USD",
        # Logs
        "logs_title": "Log de Actividad",
        "btn_clear_logs": "Limpiar Logs",
        "btn_download_logs": "Descargar Logs",
        # Errores
        "error_connect": "Error al conectar",
        "error_search": "Error al buscar",
        "error_generic": "Error",
        "reconnecting": "Reconectando",
        "reconnected": "Reconectado",
        "reconnect_failed": "Fallo reconexion",
    },
    "en": {
        "title": "Email Reader",
        "subtitle": "Read emails from multiple IMAP accounts with advanced filters",
        "tab_accounts": "Accounts",
        "tab_search": "Search",
        "tab_results": "Results",
        "tab_fifa": "FIFA",
        "tab_logs": "Logs",
        # Tab Accounts
        "accounts_upload": "Upload accounts CSV file",
        "accounts_upload_help": "CSV format: email,password (one account per line, no header)",
        "accounts_manual": "Or paste accounts manually",
        "accounts_placeholder": "user1@icloud.com,password1\nuser2@gmail.com,password2",
        "accounts_help": "Format: email,password (one per line)",
        "btn_load_accounts": "Load Accounts",
        "btn_connect_selected": "Connect Selected",
        "btn_connect_all": "Connect All",
        "btn_disconnect": "Disconnect All",
        "select_accounts": "Select accounts to connect",
        "connecting": "Connecting",
        "connected": "Connected",
        "disconnected": "Disconnected",
        "failed": "Failed",
        "no_accounts": "No accounts loaded",
        "connection_status": "Connection Status",
        "accounts_connected": "accounts connected",
        "accounts_loaded": "accounts loaded",
        "create_example": "Download example CSV",
        # Tab Search
        "search_title": "Search Criteria",
        "filter_subject": "Subject contains",
        "filter_sender": "Sender contains",
        "filter_recipient": "Recipient contains",
        "filter_content": "Content contains (local filter)",
        "filter_date_from": "Date from",
        "filter_status": "Read status",
        "filter_folder": "IMAP Folder",
        "filter_limit": "Limit per account",
        "status_all": "All",
        "status_unread": "Unread",
        "status_read": "Read",
        "btn_search": "Search All",
        "btn_search_unread": "Only Unread",
        "btn_search_read": "Only Read",
        "searching": "Searching emails...",
        "search_account": "Searching in",
        "no_connections": "No accounts connected. Go to Accounts tab first.",
        "search_results": "emails found",
        "filtered_local": "filtered locally",
        # Tab Results
        "no_results": "No results. Perform a search first.",
        "results_count": "emails found",
        "col_account": "Account",
        "col_from": "From",
        "col_to": "To",
        "col_subject": "Subject",
        "col_date": "Date",
        "col_status": "Status",
        "col_preview": "Preview",
        "btn_mark_read": "Mark as Read",
        "btn_mark_selected_read": "Mark Selected as Read",
        "btn_export_csv": "Export CSV",
        "btn_export_all_csv": "Export All to CSV",
        "btn_download_attachments": "Download Attachments",
        "btn_clear_results": "Clear Results",
        "marking": "Marking as read...",
        "marked_success": "emails marked as read",
        "view_details": "View details",
        "email_body": "Content",
        "email_html": "Original HTML",
        "attachments": "Attachments",
        "no_attachments": "No attachments",
        # FIFA
        "fifa_section": "FIFA World Cup 2026 Extraction",
        "fifa_description": "Extract detailed FIFA ticket info: match, category, quantity, price, holder, team",
        "btn_extract_fifa": "Extract FIFA Data",
        "btn_extract_fifa_all": "Extract from All",
        "btn_extract_fifa_unread": "Extract from Unread",
        "extracting_fifa": "Extracting FIFA data...",
        "fifa_no_data": "No FIFA data found in emails",
        "fifa_found": "FIFA tickets found",
        "btn_export_excel": "Export Excel",
        "btn_export_fifa_csv": "Export CSV",
        "fifa_mark_read": "Mark as read when extracting",
        "fifa_filter": "Filter by status",
        "fifa_col_email_madre": "Parent Email",
        "fifa_col_cuenta": "FIFA Account",
        "fifa_col_applicant": "Applicant",
        "fifa_col_team": "Team",
        "fifa_col_date": "Email Date",
        "fifa_col_match": "Match",
        "fifa_col_type": "Ticket Type",
        "fifa_col_category": "Category",
        "fifa_col_holder": "Holder",
        "fifa_col_quantity": "Quantity",
        "fifa_col_price": "Price USD",
        # Logs
        "logs_title": "Activity Log",
        "btn_clear_logs": "Clear Logs",
        "btn_download_logs": "Download Logs",
        # Errors
        "error_connect": "Connection error",
        "error_search": "Search error",
        "error_generic": "Error",
        "reconnecting": "Reconnecting",
        "reconnected": "Reconnected",
        "reconnect_failed": "Reconnect failed",
    },
    "hi": {
        "title": "ईमेल रीडर",
        "subtitle": "उन्नत फिल्टर के साथ कई IMAP खातों से ईमेल पढ़ें",
        "tab_accounts": "खाते",
        "tab_search": "खोज",
        "tab_results": "परिणाम",
        "tab_fifa": "FIFA",
        "tab_logs": "लॉग",
        "accounts_upload": "खाता CSV फाइल अपलोड करें",
        "accounts_upload_help": "CSV प्रारूप: email,password (प्रति पंक्ति एक खाता)",
        "accounts_manual": "या मैन्युअल रूप से खाते पेस्ट करें",
        "accounts_placeholder": "user1@icloud.com,password1\nuser2@gmail.com,password2",
        "accounts_help": "प्रारूप: email,password (प्रति पंक्ति एक)",
        "btn_load_accounts": "खाते लोड करें",
        "btn_connect_selected": "चयनित कनेक्ट करें",
        "btn_connect_all": "सभी कनेक्ट करें",
        "btn_disconnect": "सभी डिस्कनेक्ट करें",
        "select_accounts": "कनेक्ट करने के लिए खाते चुनें",
        "connecting": "कनेक्ट हो रहा है",
        "connected": "कनेक्टेड",
        "disconnected": "डिस्कनेक्टेड",
        "failed": "विफल",
        "no_accounts": "कोई खाता लोड नहीं",
        "connection_status": "कनेक्शन स्थिति",
        "accounts_connected": "खाते कनेक्ट हैं",
        "accounts_loaded": "खाते लोड हैं",
        "create_example": "उदाहरण CSV डाउनलोड करें",
        "search_title": "खोज मानदंड",
        "filter_subject": "विषय में शामिल है",
        "filter_sender": "प्रेषक में शामिल है",
        "filter_recipient": "प्राप्तकर्ता में शामिल है",
        "filter_content": "सामग्री में शामिल है (स्थानीय फिल्टर)",
        "filter_date_from": "तारीख से",
        "filter_status": "पठन स्थिति",
        "filter_folder": "IMAP फोल्डर",
        "filter_limit": "प्रति खाता सीमा",
        "status_all": "सभी",
        "status_unread": "अपठित",
        "status_read": "पठित",
        "btn_search": "सभी में खोजें",
        "btn_search_unread": "केवल अपठित",
        "btn_search_read": "केवल पठित",
        "searching": "ईमेल खोज रहे हैं...",
        "search_account": "खोज रहे हैं",
        "no_connections": "कोई खाता कनेक्ट नहीं। पहले खाते टैब पर जाएं।",
        "search_results": "ईमेल मिले",
        "filtered_local": "स्थानीय रूप से फिल्टर किए गए",
        "no_results": "कोई परिणाम नहीं। पहले खोज करें।",
        "results_count": "ईमेल मिले",
        "col_account": "खाता",
        "col_from": "से",
        "col_to": "को",
        "col_subject": "विषय",
        "col_date": "तारीख",
        "col_status": "स्थिति",
        "col_preview": "पूर्वावलोकन",
        "btn_mark_read": "पठित चिह्नित करें",
        "btn_mark_selected_read": "चयनित को पठित चिह्नित करें",
        "btn_export_csv": "CSV निर्यात",
        "btn_export_all_csv": "सभी CSV निर्यात करें",
        "btn_download_attachments": "अटैचमेंट डाउनलोड",
        "btn_clear_results": "परिणाम साफ करें",
        "marking": "पठित चिह्नित कर रहे हैं...",
        "marked_success": "ईमेल पठित चिह्नित",
        "view_details": "विवरण देखें",
        "email_body": "सामग्री",
        "email_html": "मूल HTML",
        "attachments": "अटैचमेंट",
        "no_attachments": "कोई अटैचमेंट नहीं",
        "fifa_section": "FIFA विश्व कप 2026 निष्कर्षण",
        "fifa_description": "FIFA टिकट की विस्तृत जानकारी निकालें",
        "btn_extract_fifa": "FIFA डेटा निकालें",
        "btn_extract_fifa_all": "सभी से निकालें",
        "btn_extract_fifa_unread": "अपठित से निकालें",
        "extracting_fifa": "FIFA डेटा निकाल रहे हैं...",
        "fifa_no_data": "ईमेल में FIFA डेटा नहीं मिला",
        "fifa_found": "FIFA टिकट मिले",
        "btn_export_excel": "Excel निर्यात",
        "btn_export_fifa_csv": "CSV निर्यात",
        "fifa_mark_read": "निकालते समय पठित चिह्नित करें",
        "fifa_filter": "स्थिति से फिल्टर करें",
        "fifa_col_email_madre": "मूल ईमेल",
        "fifa_col_cuenta": "FIFA खाता",
        "fifa_col_applicant": "आवेदक",
        "fifa_col_team": "टीम",
        "fifa_col_date": "ईमेल तारीख",
        "fifa_col_match": "मैच",
        "fifa_col_type": "टिकट प्रकार",
        "fifa_col_category": "श्रेणी",
        "fifa_col_holder": "धारक",
        "fifa_col_quantity": "मात्रा",
        "fifa_col_price": "कीमत USD",
        "logs_title": "गतिविधि लॉग",
        "btn_clear_logs": "लॉग साफ करें",
        "btn_download_logs": "लॉग डाउनलोड करें",
        "error_connect": "कनेक्शन त्रुटि",
        "error_search": "खोज त्रुटि",
        "error_generic": "त्रुटि",
        "reconnecting": "पुन: कनेक्ट हो रहा है",
        "reconnected": "पुन: कनेक्ट हुआ",
        "reconnect_failed": "पुन: कनेक्ट विफल",
    }
}

# === IMAP PRESETS ===
IMAP_PRESETS = {
    "gmail.com": ("imap.gmail.com", 993),
    "googlemail.com": ("imap.gmail.com", 993),
    "icloud.com": ("imap.mail.me.com", 993),
    "me.com": ("imap.mail.me.com", 993),
    "mac.com": ("imap.mail.me.com", 993),
    "outlook.com": ("outlook.office365.com", 993),
    "hotmail.com": ("outlook.office365.com", 993),
    "live.com": ("outlook.office365.com", 993),
    "yahoo.com": ("imap.mail.yahoo.com", 993),
    "yahoo.es": ("imap.mail.yahoo.com", 993),
    "zoho.eu": ("imap.zoho.eu", 993),
}

DEFAULT_FOLDER = "INBOX"

# === Criterios IMAP (para imap_search_safe) ===
_IMAP_FLAGS = {'SEEN', 'UNSEEN', 'ALL', 'ANSWERED', 'DELETED', 'DRAFT', 'FLAGGED',
               'NEW', 'OLD', 'RECENT', 'UNANSWERED', 'UNDELETED', 'UNDRAFT', 'UNFLAGGED'}
_IMAP_KEYED = {'FROM', 'SUBJECT', 'TO', 'CC', 'BCC', 'BODY', 'TEXT',
               'SINCE', 'BEFORE', 'ON', 'SENTBEFORE', 'SENTON', 'SENTSINCE',
               'LARGER', 'SMALLER', 'HEADER', 'KEYWORD', 'UNKEYWORD'}

# FIFA regex
_ROUND_KW_RE = re.compile(
    r'(Bronze[- ]?final|Semi[- ]?final\s*\d*|Final|Quarter[- ]?final\s*\d*|'
    r'Round\s+of\s+16|Group\s+Stage|Group\s+[A-H]|Match\s+\d+|3rd[- ]?[Pp]lace|'
    r'Opening\s+[Mm]atch|Play[- ]?off)',
    re.IGNORECASE
)


# ==================== FUNCIONES UTILIDAD ====================

def t(key):
    """Obtiene la traduccion para la clave dada"""
    lang = st.session_state.get("language", "es")
    return TRANSLATIONS.get(lang, TRANSLATIONS["es"]).get(key, key)


def infer_imap_server(email_addr):
    """Infiere el servidor IMAP basado en el dominio del email"""
    domain = email_addr.split("@")[-1].lower()
    preset = IMAP_PRESETS.get(domain)
    if preset:
        return preset[0]
    return f"imap.{domain}"


def get_ssl_context():
    """Crea un contexto SSL para conexiones IMAP"""
    ctx = ssl.create_default_context()
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.check_hostname = True
    return ctx


def decode_header_text(header_value):
    """Decodifica un header de email"""
    if not header_value:
        return ""
    try:
        parts = decode_header(header_value)
        out = ""
        for frag, enc in parts:
            if isinstance(frag, bytes):
                out += frag.decode(enc or "utf-8", errors="replace")
            else:
                out += str(frag)
        return out
    except Exception:
        return str(header_value)


def extract_text_content(msg):
    """Extrae el contenido de texto de un mensaje (texto plano o HTML limpio)"""
    try:
        if msg.is_multipart():
            text = ""
            for part in msg.walk():
                ctype = part.get_content_type()
                disp = str(part.get("Content-Disposition", "")).lower()
                if ctype == "text/plain" and "attachment" not in disp:
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or "utf-8"
                    try:
                        text += payload.decode(charset, errors="replace")
                    except (UnicodeDecodeError, LookupError):
                        text += payload.decode("utf-8", errors="replace")
                elif ctype == "text/html" and not text:
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or "utf-8"
                    try:
                        html = payload.decode(charset, errors="replace")
                    except (UnicodeDecodeError, LookupError):
                        html = payload.decode("utf-8", errors="replace")
                    text = re.sub(r"<[^>]+>", "", html)
            return text.strip()
        else:
            payload = msg.get_payload(decode=True)
            charset = msg.get_content_charset() or "utf-8"
            try:
                return payload.decode(charset, errors="replace").strip() if isinstance(payload, bytes) else str(payload).strip()
            except (UnicodeDecodeError, LookupError):
                return payload.decode("utf-8", errors="replace").strip() if isinstance(payload, bytes) else str(payload).strip()
    except Exception:
        return "[Error extrayendo contenido]"


def extract_html_content(msg):
    """Extrae el contenido HTML sin modificar"""
    try:
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                disp = str(part.get("Content-Disposition", "")).lower()
                if "attachment" in disp:
                    continue
                if ctype == "text/html":
                    payload = part.get_payload(decode=True)
                    if payload is None:
                        continue
                    charset = part.get_content_charset() or "utf-8"
                    try:
                        return payload.decode(charset, errors="replace")
                    except (UnicodeDecodeError, LookupError):
                        return payload.decode("utf-8", errors="replace")
            return ""
        else:
            if msg.get_content_type() == "text/html":
                payload = msg.get_payload(decode=True)
                charset = msg.get_content_charset() or "utf-8"
                try:
                    return payload.decode(charset, errors="replace") if isinstance(payload, bytes) else str(payload)
                except (UnicodeDecodeError, LookupError):
                    return payload.decode("utf-8", errors="replace") if isinstance(payload, bytes) else str(payload)
            return ""
    except Exception:
        return ""


def to_imap_date(d) -> Optional[str]:
    """Convierte date a formato IMAP (DD-Mon-YYYY)"""
    try:
        if isinstance(d, str):
            dt = datetime.strptime(d.strip(), "%d/%m/%Y")
        elif isinstance(d, date):
            dt = d
        else:
            return None
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return f"{dt.day:02d}-{months[dt.month - 1]}-{dt.year}"
    except Exception:
        return None


def extract_email_only(header_value: str) -> str:
    """Extrae solo la direccion de email de un header"""
    if not header_value:
        return ""
    pairs = getaddresses([header_value])
    if pairs:
        _, addr = pairs[0]
        if addr:
            return addr.strip()
    m = re.search(r'<([^>]+@[^>]+)>', header_value)
    if m:
        return m.group(1).strip()
    if '@' in header_value and '<' not in header_value:
        return header_value.strip()
    return header_value.strip()


# ==================== IMAP SEARCH SEGURO (v4) ====================

def imap_search_safe(conn, parts, log_fn=None):
    """
    Ejecuta SEARCH de forma segura. Intenta con CHARSET UTF-8 primero,
    si falla reintenta sin charset.
    """
    _log = log_fn or (lambda s: None)
    try:
        search_parts = []
        i = 0
        while i < len(parts):
            token = parts[i].upper()
            if token in _IMAP_FLAGS:
                search_parts.append(token)
                i += 1
            elif token in _IMAP_KEYED:
                if i + 1 < len(parts):
                    value = parts[i + 1]
                    search_parts.append(f'{token} "{value}"')
                    i += 2
                else:
                    search_parts.append(token)
                    i += 1
            else:
                search_parts.append(parts[i])
                i += 1
        search_string = ' '.join(search_parts)

        typ, data = None, None
        try:
            typ, data = conn.search('UTF-8', search_string)
        except Exception:
            typ, data = conn.search(None, search_string)

    except Exception as e:
        _log(f"Error en busqueda IMAP: {e}")
        return []

    if typ != "OK" or not data:
        return []
    first = data[0]
    if first in (None, b"", ""):
        return []
    try:
        return first.split()
    except Exception:
        return []


# ==================== FIFA EXTRACTION (v4 avanzado) ====================

def _html_to_text(html: str) -> str:
    """Convierte HTML a texto limpio para extraccion FIFA"""
    text = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
    text = re.sub(r'</(?:td|tr|th|p|div|li|h\d)>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&#8239;', ' ')
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n[ \t]*', '\n', text)
    text = re.sub(r'\n{2,}', '\n', text)
    return text


def extract_fifa_tickets(html_content: str) -> List[dict]:
    """
    Extrae informacion de tickets FIFA del contenido del email.
    Soporta formatos nuevos (Supporter Tier) y antiguos (Match XX / Category N).
    Retorna lista de dicts con: match_info, ticket_type, category, quantity, price_usd, holder_name
    """
    tickets = []
    if not html_content:
        return tickets

    text = _html_to_text(html_content)

    # Bloques: "(Conditional|Confirmed) Tickets" seguido de "N tickets"
    block_re = re.compile(
        r'(Conditional|Confirmed)\s+Tickets\s+(\d+)\s+tickets',
        re.IGNORECASE
    )

    for bm in block_re.finditer(text):
        ticket_type = bm.group(1).strip().title()
        quantity = int(bm.group(2))

        # Match description: buscar hacia atras (max 600 chars)
        before = text[max(0, bm.start() - 600):bm.start()]
        match_info = ""
        for rm in _ROUND_KW_RE.finditer(before):
            rest = before[rm.start():]
            first_line = rest.split('\n')[0].strip()
            match_info = re.sub(r'\s+', ' ', first_line)

        if not match_info:
            match_info = "Partido no identificado"

        # Tier/categoria y precio: buscar hacia adelante (max 600 chars)
        after = text[bm.end():bm.end() + 600]

        tier_m = re.search(
            r'(Supporter\s+[\w ]+?Tier|Category\s+\d+)',
            after, re.IGNORECASE
        )
        category = re.sub(r'\s+', ' ', tier_m.group(1)).strip() if tier_m else ""

        price_m = re.search(r'([\d,]+\.\d{2})\s*(?:USD|\$|€|EUR)', after)
        price = float(price_m.group(1).replace(',', '')) if price_m else 0.0

        # Nombre del titular: entre tier y precio
        holder_name = ""
        if tier_m and price_m:
            between = after[tier_m.end():price_m.start()]
            between = re.sub(r'\s+', ' ', between).strip()
            if len(between) > 2:
                holder_name = between

        tickets.append({
            'match_info': match_info,
            'ticket_type': ticket_type,
            'category': category,
            'quantity': quantity,
            'price_usd': price,
            'holder_name': holder_name,
        })

    # Fallback: formato antiguo "Match XX" + "Category N"
    if not tickets:
        old_pattern = (
            r'Match\s+(\d+)\s+([^<\n]+?)(?:&nbsp;|-)\s*([^<\n]+?)\s.*?'
            r'(\d+)\s*tickets.*?Category\s+(\d+).*?'
            r'([\d,]+\.?\d*)\s*(?:USD|\$|€|EUR)'
        )
        for m in re.finditer(old_pattern, html_content, re.IGNORECASE | re.DOTALL):
            tickets.append({
                'match_info': f"Match {m.group(1)} {m.group(2).strip()} - {m.group(3).strip()}",
                'ticket_type': '',
                'category': f"Category {m.group(5).strip()}",
                'quantity': int(m.group(4).strip()),
                'price_usd': float(m.group(6).replace(',', '')) if m.group(6) else 0.0,
                'holder_name': '',
            })

    return tickets


def extract_fifa_application_number(html_content: str) -> str:
    """Extrae el numero de aplicacion FIFA del email"""
    m = re.search(r'application\s+number\s+(?:is[:\s]*)?\s*(?:<[^>]*>)*\s*(\d{4,})',
                  html_content, re.IGNORECASE)
    if m:
        return m.group(1)
    text = _html_to_text(html_content)
    m = re.search(r'application\s+number[:\s]+(\d{4,})', text, re.IGNORECASE)
    if m:
        return m.group(1)
    return ""


def extract_fifa_applicant_name(html_content: str) -> str:
    """Extrae el nombre del solicitante del email FIFA"""
    m = re.search(r'(?:Hi|Dear|Hola)\s+([^,<\n]{2,60})', html_content, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    text = _html_to_text(html_content)
    m = re.search(r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,4})\s*,\s*Congratulations', text)
    if m:
        return m.group(1).strip()
    return ""


def extract_fifa_team(html_content: str) -> str:
    """Extrae el equipo solicitado: 'My Team - France' -> 'France'"""
    text = _html_to_text(html_content)
    m = re.search(
        r'My\s+Team\s*[-\u2013:]\s*([A-Z][a-zA-Z\s]+?)(?:\s*$|\s*\n|\s+(?:Please|Conditional|Confirmed|Your|This|Note))',
        text, re.IGNORECASE | re.MULTILINE
    )
    if m:
        team = m.group(1).strip()
        if len(team) < 40:
            return team
    return ""


# ==================== ADJUNTOS ====================

def extract_attachments_info(msg) -> List[dict]:
    """Extrae informacion de adjuntos de un mensaje (nombre, tipo, tamaño)"""
    attachments = []
    for part in msg.walk():
        disp = str(part.get("Content-Disposition", "")).lower()
        if "attachment" not in disp and "inline" not in disp:
            continue
        filename = part.get_filename()
        if not filename:
            ext = {
                "image/jpeg": ".jpg", "image/png": ".png",
                "application/pdf": ".pdf", "application/zip": ".zip",
            }.get(part.get_content_type(), "")
            if not ext:
                continue
            filename = f"adjunto{ext}"
        filename = decode_header_text(filename) if filename else "adjunto"
        payload = part.get_payload(decode=True)
        if payload is None:
            continue
        attachments.append({
            "filename": filename,
            "content_type": part.get_content_type(),
            "size": len(payload),
            "data": payload,
        })
    return attachments


# ==================== IMAP MANAGER (v4) ====================

class ImapManager:
    """Gestor de conexiones IMAP con reconexion y busqueda robusta"""

    def __init__(self):
        self.connections: Dict[str, imaplib.IMAP4_SSL] = {}
        self.credentials: Dict[str, Tuple[str, str]] = {}  # email -> (password, type)
        self.status: Dict[str, bool] = {}
        self.errors: Dict[str, str] = {}

    def connect(self, email_addr: str, password: str) -> Tuple[bool, str]:
        """Conecta a una cuenta IMAP"""
        try:
            host = infer_imap_server(email_addr)
            conn = imaplib.IMAP4_SSL(host, 993, ssl_context=get_ssl_context())
            conn.login(email_addr, password)
            try:
                conn._simple_command("ENABLE", "UTF8=ACCEPT")
            except Exception:
                pass
            self.connections[email_addr] = conn
            self.credentials[email_addr] = (password, 'normal')
            self.status[email_addr] = True
            self.errors[email_addr] = ""
            return True, f"Conectado a {email_addr}"
        except imaplib.IMAP4.error as e:
            self.status[email_addr] = False
            self.errors[email_addr] = str(e)
            return False, f"IMAP error en {email_addr}: {e}"
        except Exception as e:
            self.status[email_addr] = False
            self.errors[email_addr] = str(e)
            return False, f"Error conectando {email_addr}: {e}"

    def connect_oauth2(self, email_addr: str, access_token: str) -> Tuple[bool, str]:
        """Conecta usando XOAUTH2 (Gmail/Outlook)"""
        try:
            host = infer_imap_server(email_addr)
            conn = imaplib.IMAP4_SSL(host, 993, ssl_context=get_ssl_context())
            auth_string = f"user={email_addr}\1auth=Bearer {access_token}\1\1"
            conn.authenticate("XOAUTH2", lambda _: auth_string.encode())
            try:
                conn._simple_command("ENABLE", "UTF8=ACCEPT")
            except Exception:
                pass
            self.connections[email_addr] = conn
            self.credentials[email_addr] = (access_token, 'oauth2')
            self.status[email_addr] = True
            self.errors[email_addr] = ""
            return True, f"Conectado OAuth2: {email_addr}"
        except Exception as e:
            self.status[email_addr] = False
            self.errors[email_addr] = str(e)
            return False, f"Error OAuth2 {email_addr}: {e}"

    def reconnect(self, email_addr: str) -> Tuple[bool, str]:
        """Intenta reconectar una cuenta que perdio conexion"""
        if email_addr not in self.credentials:
            return False, f"No hay credenciales para {email_addr}"

        password, auth_type = self.credentials[email_addr]

        # Cerrar conexion antigua
        if email_addr in self.connections:
            try:
                self.connections[email_addr].logout()
            except Exception:
                pass
            del self.connections[email_addr]

        if auth_type == 'oauth2':
            return self.connect_oauth2(email_addr, password)
        else:
            return self.connect(email_addr, password)

    def disconnect_all(self):
        """Desconecta todas las cuentas"""
        for addr, conn in list(self.connections.items()):
            try:
                conn.logout()
            except Exception:
                pass
        self.connections.clear()
        self.status.clear()
        self.errors.clear()

    def _select_folder_safe(self, conn, folder: str) -> bool:
        """Selecciona carpeta con fallback a INBOX"""
        try:
            ok, _ = conn.select(folder)
            if ok != "OK":
                if folder != "INBOX":
                    ok, _ = conn.select("INBOX")
                    if ok != "OK":
                        return False
            return True
        except Exception:
            return False

    def search(self, email_addr: str, criteria: dict, folder: str = "INBOX",
               retry_on_error: bool = True, log_fn=None) -> List[dict]:
        """
        Busca correos con estrategia v4: enviar solo 1 keyword al servidor IMAP
        por campo y filtrar localmente para coincidencia exacta.
        """
        results: List[dict] = []
        _log = log_fn or (lambda s: None)

        try:
            connection = self.connections.get(email_addr)
            if not connection:
                _log(f"No hay conexion para {email_addr}")
                return results

            if not self._select_folder_safe(connection, folder):
                _log(f"No se pudo seleccionar carpeta '{folder}' en {email_addr}")
                return results

            # Construir criterios IMAP: solo 1 keyword por campo
            parts: List[str] = []

            sender_crit = criteria.get("sender", "").strip()
            subject_crit = criteria.get("subject", "").strip()

            if sender_crit:
                parts.append("FROM")
                if '@' in sender_crit:
                    user_part, domain_part = sender_crit.rsplit('@', 1)
                    parts.append(user_part if len(user_part) >= len(domain_part) else sender_crit)
                else:
                    parts.append(sender_crit)

            if subject_crit:
                words = [w for w in subject_crit.split() if len(w) > 2]
                if words:
                    keyword = max(words, key=len)
                    parts.append("SUBJECT")
                    parts.append(keyword)

            if criteria.get("read_status"):
                parts.append(criteria["read_status"])

            if criteria.get("date_since"):
                parts.append("SINCE")
                parts.append(criteria["date_since"])

            if not parts:
                parts = ["ALL"]

            _log(f"Buscando en {email_addr} — IMAP: {parts}")

            message_ids = imap_search_safe(connection, parts, log_fn=_log)

            if not message_ids:
                _log(f"{email_addr}: 0 mensajes")
                return []

            _log(f"{email_addr}: {len(message_ids)} del servidor, aplicando filtros...")

            limit = int(criteria.get("limit") or 25)
            message_ids = message_ids[-limit:][::-1]

            filtered_out = 0
            for msg_id in message_ids:
                try:
                    typ, msg_data = connection.fetch(msg_id, "(BODY.PEEK[] FLAGS)")
                    if typ != "OK" or not msg_data:
                        continue

                    raw = None
                    flags_line = None
                    for elt in msg_data:
                        if isinstance(elt, tuple) and b"BODY[" in elt[0]:
                            raw = elt[1]
                        if isinstance(elt, tuple) and b"FLAGS" in elt[0]:
                            flags_line = elt[0]
                        if isinstance(elt, bytes) and b"FLAGS" in elt:
                            flags_line = elt

                    if not raw:
                        continue

                    parsed = email.message_from_bytes(raw)
                    is_read = bool(flags_line and b"\\Seen" in flags_line)
                    from_addr = decode_header_text(parsed.get("From", ""))
                    to_addr = decode_header_text(parsed.get("To", ""))
                    subject_text = decode_header_text(parsed.get("Subject", ""))
                    date_text = parsed.get("Date", "")
                    content = extract_text_content(parsed)
                    html_content = extract_html_content(parsed)

                    # Filtros locales post-fetch
                    content_crit = criteria.get("content", "").strip()
                    recipient_crit = criteria.get("recipient", "").strip()

                    if content_crit and content_crit.lower() not in content.lower():
                        filtered_out += 1
                        continue

                    if recipient_crit and recipient_crit.lower() not in to_addr.lower():
                        filtered_out += 1
                        continue

                    if subject_crit:
                        crit_words = [w.lower() for w in subject_crit.replace('-', ' ').split() if len(w) > 2]
                        subj_lower = subject_text.lower()
                        if crit_words and not all(w in subj_lower for w in crit_words):
                            filtered_out += 1
                            continue

                    if sender_crit and sender_crit.lower() not in from_addr.lower():
                        filtered_out += 1
                        continue

                    # Parsear fecha
                    try:
                        date_parsed = email.utils.parsedate_to_datetime(date_text)
                        date_formatted = date_parsed.strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        date_formatted = date_text[:20] if date_text else ""

                    results.append({
                        "account": email_addr,
                        "msg_id": msg_id,
                        "from": from_addr,
                        "to": to_addr,
                        "subject": subject_text,
                        "date": date_text,
                        "date_fmt": date_formatted,
                        "content": content,
                        "html_content": html_content,
                        "is_read": is_read,
                        "conn": connection,
                    })
                except Exception:
                    continue

            if filtered_out:
                _log(f"  {email_addr}: {filtered_out} filtrados, {len(results)} coinciden")

        except Exception as e:
            error_str = str(e).lower()
            if retry_on_error and any(k in error_str for k in ('socket', 'eof', 'broken', 'connection', 'abort', 'reset')):
                _log(f"{t('reconnecting')} {email_addr}...")
                ok, reconn_msg = self.reconnect(email_addr)
                if ok:
                    _log(f"{t('reconnected')} {email_addr}")
                    time.sleep(0.5)
                    return self.search(email_addr, criteria, folder,
                                       retry_on_error=False, log_fn=log_fn)
                else:
                    _log(f"{t('reconnect_failed')} {email_addr}: {reconn_msg}")
            else:
                _log(f"{t('error_search')}: {email_addr}: {e}")

        return results

    def mark_seen(self, email_addr: str, msg_id) -> bool:
        """Marca un correo como leido"""
        try:
            conn = self.connections.get(email_addr)
            if not conn:
                return False
            typ, _ = conn.store(msg_id, "+FLAGS", r"\Seen")
            return typ == "OK"
        except Exception:
            return False


# ==================== SESSION STATE ====================

def _log(msg: str):
    """Agrega un mensaje al log"""
    ts = datetime.now().strftime("%H:%M:%S")
    if "lectura_logs" not in st.session_state:
        st.session_state.lectura_logs = []
    st.session_state.lectura_logs.append(f"[{ts}] {msg}")


def init_session_state():
    """Inicializa el session state"""
    if "lectura_imap" not in st.session_state:
        st.session_state.lectura_imap = ImapManager()
    if "lectura_accounts" not in st.session_state:
        st.session_state.lectura_accounts = []  # lista de (email, password)
    if "lectura_results" not in st.session_state:
        st.session_state.lectura_results = []
    if "lectura_fifa_data" not in st.session_state:
        st.session_state.lectura_fifa_data = []
    if "lectura_logs" not in st.session_state:
        st.session_state.lectura_logs = []


# ==================== RENDER PRINCIPAL ====================

def render():
    """Renderiza la pagina de lectura de correos"""
    init_session_state()

    st.title(f"📧 {t('title')}")
    st.markdown(f"*{t('subtitle')}*")
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        f"👥 {t('tab_accounts')}",
        f"🔍 {t('tab_search')}",
        f"📋 {t('tab_results')}",
        f"⚽ {t('tab_fifa')}",
        f"📝 {t('tab_logs')}",
    ])

    with tab1:
        render_accounts_tab()
    with tab2:
        render_search_tab()
    with tab3:
        render_results_tab()
    with tab4:
        render_fifa_tab()
    with tab5:
        render_logs_tab()


# ==================== TAB CUENTAS ====================

def render_accounts_tab():
    """Pestana de gestion de cuentas con CSV upload y seleccion"""
    imap_manager = st.session_state.lectura_imap

    # --- CSV de ejemplo para descargar ---
    example_csv = "usuario1@icloud.com,app-password-1\nusuario2@gmail.com,app-password-2\nusuario3@outlook.com,app-password-3\n"
    st.download_button(
        label=f"📄 {t('create_example')}",
        data=example_csv,
        file_name="cuentas_ejemplo.csv",
        mime="text/csv",
    )

    st.markdown("---")

    # --- Subir CSV ---
    st.subheader(f"📁 {t('accounts_upload')}")
    uploaded_file = st.file_uploader(
        t("accounts_upload_help"),
        type=["csv", "txt"],
        key="lectura_csv_upload"
    )

    if uploaded_file is not None:
        # Cargar automaticamente al subir (usar hash para no recargar si es el mismo archivo)
        file_hash = hash(uploaded_file.getvalue())
        if st.session_state.get("_lectura_csv_hash") != file_hash:
            content = uploaded_file.getvalue().decode("utf-8", errors="replace")
            accounts = _parse_accounts_text(content)
            if accounts:
                st.session_state.lectura_accounts = accounts
                st.session_state._lectura_csv_hash = file_hash
                _log(f"Cuentas cargadas desde CSV: {len(accounts)}")
                st.success(f"✅ {len(accounts)} {t('accounts_loaded')}")
                st.rerun()
            else:
                st.error("No se encontraron cuentas validas en el archivo")

    st.markdown("---")

    # --- Pegar manualmente ---
    st.subheader(f"✏️ {t('accounts_manual')}")
    accounts_text = st.text_area(
        t("accounts_help"),
        placeholder=t("accounts_placeholder"),
        height=120,
        key="lectura_accounts_text"
    )

    if st.button(f"📥 {t('btn_load_accounts')}", key="load_manual_btn"):
        if accounts_text.strip():
            accounts = _parse_accounts_text(accounts_text)
            if accounts:
                st.session_state.lectura_accounts = accounts
                _log(f"Cuentas cargadas manualmente: {len(accounts)}")
                st.success(f"✅ {len(accounts)} {t('accounts_loaded')}")
                st.rerun()
            else:
                st.error("No se encontraron cuentas validas")

    st.markdown("---")

    # --- Cuentas cargadas y seleccion ---
    accounts = st.session_state.lectura_accounts
    if accounts:
        st.subheader(f"📋 {len(accounts)} {t('accounts_loaded')}")

        # Multiselect para elegir cuentas
        account_emails = [a[0] for a in accounts]
        selected = st.multiselect(
            t("select_accounts"),
            options=account_emails,
            default=account_emails,
            key="lectura_selected_accounts"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(f"🔗 {t('btn_connect_selected')}", type="primary",
                         use_container_width=True):
                if selected:
                    _connect_accounts(imap_manager, accounts, selected)
                else:
                    st.warning("Selecciona al menos una cuenta")

        with col2:
            if st.button(f"🔗 {t('btn_connect_all')}", use_container_width=True):
                _connect_accounts(imap_manager, accounts, account_emails)

        with col3:
            if st.button(f"🔌 {t('btn_disconnect')}", use_container_width=True):
                imap_manager.disconnect_all()
                st.session_state.lectura_results = []
                st.session_state.lectura_fifa_data = []
                _log("Todas las conexiones cerradas")
                st.rerun()

        # --- Estado de conexiones ---
        st.markdown("---")
        st.subheader(f"📊 {t('connection_status')}")

        connected_count = sum(1 for v in imap_manager.status.values() if v)
        if connected_count > 0:
            st.info(f"✅ {connected_count} {t('accounts_connected')}")

        for email_addr, _ in accounts:
            is_conn = imap_manager.status.get(email_addr, False)
            error = imap_manager.errors.get(email_addr, "")
            server = infer_imap_server(email_addr)

            if is_conn:
                st.success(f"🟢 {email_addr} — {server}")
            elif email_addr in imap_manager.status:
                st.error(f"🔴 {email_addr} — {error}")
            else:
                st.markdown(f"⚪ {email_addr} — {t('disconnected')} — {server}")
    else:
        st.info(f"ℹ️ {t('no_accounts')}")


def _parse_accounts_text(text: str) -> List[Tuple[str, str]]:
    """Parsea texto con cuentas en formato email,password"""
    accounts = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "," in line:
            parts = line.split(",", 1)
            if len(parts) == 2:
                email_addr = parts[0].strip()
                password = parts[1].strip()
                if email_addr and password and "@" in email_addr:
                    accounts.append((email_addr, password))
    return accounts


def _connect_accounts(imap_manager, accounts, selected_emails):
    """Conecta las cuentas seleccionadas en PARALELO con ThreadPoolExecutor"""
    to_connect = [(e, p) for e, p in accounts if e in selected_emails]
    if not to_connect:
        return

    total = len(to_connect)
    MAX_WORKERS = min(10, total)

    progress = st.progress(0)
    status_container = st.empty()
    status_container.info(f"🔄 Conectando {total} cuentas en paralelo (max {MAX_WORKERS} simultaneas)...")

    connected = 0
    failed = 0
    completed = 0

    def connect_single(email_addr, password):
        return imap_manager.connect(email_addr, password)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(connect_single, addr, pwd): addr
            for addr, pwd in to_connect
        }

        for future in as_completed(futures):
            addr = futures[future]
            try:
                ok, msg = future.result()
                if ok:
                    connected += 1
                else:
                    failed += 1
                _log(msg)
            except Exception as e:
                failed += 1
                _log(f"Error conectando {addr}: {e}")

            completed += 1
            progress.progress(completed / total)
            status_container.info(
                f"🔄 Conectadas: {connected} | Fallidas: {failed} | {completed}/{total}"
            )

    status_container.empty()
    progress.empty()

    if connected > 0:
        st.success(f"✅ {connected} {t('accounts_connected')}")
    if failed > 0:
        st.warning(f"⚠️ {failed} fallidas")
    _log(f"Conexion paralela completada: {connected} OK, {failed} fallidas de {total}")
    st.rerun()


# ==================== TAB BUSQUEDA ====================

def render_search_tab():
    """Pestana de busqueda con filtros avanzados"""
    imap_manager = st.session_state.lectura_imap

    connected_accounts = [e for e, s in imap_manager.status.items() if s]
    if not connected_accounts:
        st.warning(f"⚠️ {t('no_connections')}")
        return

    st.info(f"✅ {len(connected_accounts)} {t('accounts_connected')}")

    st.subheader(f"🎯 {t('search_title')}")

    col1, col2 = st.columns(2)
    with col1:
        subject_filter = st.text_input(
            f"📋 {t('filter_subject')}", key="lectura_filter_subject"
        )
        sender_filter = st.text_input(
            f"👤 {t('filter_sender')}", key="lectura_filter_sender"
        )
        recipient_filter = st.text_input(
            f"📮 {t('filter_recipient')}", key="lectura_filter_recipient"
        )

    with col2:
        content_filter = st.text_input(
            f"📄 {t('filter_content')}", key="lectura_filter_content"
        )
        date_from = st.date_input(
            f"📅 {t('filter_date_from')}",
            value=datetime.now() - timedelta(days=7),
            key="lectura_filter_date"
        )
        status_options = {
            "all": t("status_all"),
            "unread": t("status_unread"),
            "read": t("status_read")
        }
        status_filter = st.selectbox(
            f"📬 {t('filter_status')}",
            options=list(status_options.keys()),
            format_func=lambda x: status_options[x],
            key="lectura_filter_status"
        )

    col_a, col_b = st.columns(2)
    with col_a:
        folder = st.text_input(
            f"📁 {t('filter_folder')}", value="INBOX", key="lectura_filter_folder"
        )
    with col_b:
        limit = st.slider(
            f"🔢 {t('filter_limit')}",
            min_value=5, max_value=500, value=25, step=5,
            key="lectura_filter_limit"
        )

    # Botones de busqueda
    col1, col2, col3 = st.columns(3)

    def _do_search(force_status=None):
        read_status = None
        if force_status == "unread":
            read_status = "UNSEEN"
        elif force_status == "read":
            read_status = "SEEN"
        elif status_filter == "unread":
            read_status = "UNSEEN"
        elif status_filter == "read":
            read_status = "SEEN"

        date_since = to_imap_date(date_from) if date_from else None

        criteria = {
            "subject": subject_filter,
            "sender": sender_filter,
            "recipient": recipient_filter,
            "content": content_filter,
            "read_status": read_status,
            "date_since": date_since,
            "limit": limit,
        }

        all_results = []
        total = len(connected_accounts)
        MAX_SEARCH_WORKERS = min(10, total)
        progress = st.progress(0)
        status_container = st.empty()
        status_container.info(f"🔄 Buscando en paralelo en {total} cuentas...")

        completed = 0

        def search_single(addr):
            return imap_manager.search(
                addr, criteria, folder=folder or "INBOX",
                log_fn=_log
            )

        with ThreadPoolExecutor(max_workers=MAX_SEARCH_WORKERS) as executor:
            futures = {
                executor.submit(search_single, addr): addr
                for addr in connected_accounts
            }

            for future in as_completed(futures):
                addr = futures[future]
                try:
                    items = future.result()
                    all_results.extend(items)
                except Exception as e:
                    _log(f"Error buscando en {addr}: {e}")

                completed += 1
                progress.progress(completed / total)
                status_container.info(
                    f"🔄 Buscando... {completed}/{total} cuentas | {len(all_results)} correos"
                )

        status_container.empty()
        progress.empty()

        # Ordenar por fecha
        def parse_date(dtstr):
            try:
                return email.utils.parsedate_to_datetime(dtstr)
            except Exception:
                return datetime.min

        all_results.sort(key=lambda m: parse_date(m["date"]), reverse=True)
        st.session_state.lectura_results = all_results
        _log(f"Busqueda completada: {len(all_results)} correos encontrados")
        st.success(f"✅ {len(all_results)} {t('search_results')}")

    with col1:
        if st.button(f"🔍 {t('btn_search')}", type="primary", use_container_width=True):
            _do_search()

    with col2:
        if st.button(f"📩 {t('btn_search_unread')}", use_container_width=True):
            _do_search(force_status="unread")

    with col3:
        if st.button(f"📖 {t('btn_search_read')}", use_container_width=True):
            _do_search(force_status="read")


# ==================== TAB RESULTADOS ====================

def render_results_tab():
    """Pestana de resultados con detalles, marcar leido, exportar"""
    results = st.session_state.lectura_results
    imap_manager = st.session_state.lectura_imap

    if not results:
        st.info(f"ℹ️ {t('no_results')}")
        return

    st.success(f"📧 {len(results)} {t('results_count')}")

    # --- Acciones superiores ---
    col1, col2, col3 = st.columns(3)

    with col1:
        # Exportar CSV
        csv_data = _generate_csv(results)
        st.download_button(
            label=f"📥 {t('btn_export_all_csv')}",
            data=csv_data,
            file_name=f"correos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col2:
        if st.button(f"✅ {t('btn_mark_selected_read')}", use_container_width=True,
                      key="mark_all_read_btn"):
            unread = [r for r in results if not r.get("is_read")]
            if unread:
                marked = 0
                progress = st.progress(0)
                for i, r in enumerate(unread):
                    if imap_manager.mark_seen(r.get("account"), r.get("msg_id")):
                        r["is_read"] = True
                        marked += 1
                    progress.progress((i + 1) / len(unread))
                progress.empty()
                _log(f"{marked} {t('marked_success')}")
                st.success(f"✅ {marked} {t('marked_success')}")
                st.rerun()
            else:
                st.info("Todos ya estan leidos")

    with col3:
        if st.button(f"🧹 {t('btn_clear_results')}", use_container_width=True,
                      key="clear_results_btn"):
            st.session_state.lectura_results = []
            st.session_state.lectura_fifa_data = []
            _log("Resultados limpiados")
            st.rerun()

    st.markdown("---")

    # --- Tabla resumen ---
    import pandas as pd
    df_data = []
    for r in results:
        df_data.append({
            t("col_account"): r.get("account", ""),
            t("col_from"): r.get("from", "")[:40],
            t("col_to"): extract_email_only(r.get("to", ""))[:40],
            t("col_subject"): r.get("subject", "")[:60],
            t("col_date"): r.get("date_fmt", ""),
            t("col_status"): "📖" if r.get("is_read") else "📩",
        })

    if df_data:
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, height=300)

    st.markdown("---")

    # --- Detalle de cada correo ---
    for i, r in enumerate(results):
        status_icon = "📖" if r.get("is_read") else "📩"
        label = f"{status_icon} {r.get('subject', 'Sin asunto')[:60]} — {r.get('date_fmt', '')} — {r.get('account', '')}"

        with st.expander(label):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**{t('col_account')}:** {r.get('account', '')}")
                st.markdown(f"**{t('col_from')}:** {r.get('from', '')}")
                st.markdown(f"**{t('col_to')}:** {r.get('to', '')}")
            with col_b:
                st.markdown(f"**{t('col_date')}:** {r.get('date_fmt', '')}")
                st.markdown(f"**{t('col_status')}:** {'📖 Leido' if r.get('is_read') else '📩 No leido'}")

            # Contenido
            st.markdown(f"**{t('email_body')}:**")
            content = r.get("content", "")
            if content:
                st.text_area("", value=content[:3000], height=200,
                             key=f"content_{i}", disabled=True)
            else:
                html = r.get("html_content", "")
                if html:
                    clean = re.sub(r'<[^>]+>', ' ', html)
                    clean = re.sub(r'\s+', ' ', clean).strip()
                    st.text_area("", value=clean[:3000], height=200,
                                 key=f"content_{i}", disabled=True)

            # Adjuntos
            html_content = r.get("html_content", "")
            if r.get("conn") and r.get("msg_id"):
                try:
                    conn = r["conn"]
                    mid = r["msg_id"]
                    typ, data = conn.fetch(mid, "(BODY.PEEK[])")
                    if typ == "OK" and data and isinstance(data[0], tuple):
                        msg_obj = email.message_from_bytes(data[0][1])
                        attachments = extract_attachments_info(msg_obj)
                        if attachments:
                            st.markdown(f"**📎 {t('attachments')}:** {len(attachments)}")
                            for att in attachments:
                                st.download_button(
                                    label=f"📎 {att['filename']} ({att['size'] // 1024} KB)",
                                    data=att['data'],
                                    file_name=att['filename'],
                                    key=f"att_{i}_{att['filename']}"
                                )
                except Exception:
                    pass

            # Boton marcar como leido
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                if not r.get("is_read"):
                    if st.button(f"✅ {t('btn_mark_read')}", key=f"mark_{i}"):
                        if imap_manager.mark_seen(r.get("account"), r.get("msg_id")):
                            st.session_state.lectura_results[i]["is_read"] = True
                            _log(f"Marcado leido: {r.get('subject', '')[:50]}")
                            st.rerun()


def _generate_csv(results: list) -> str:
    """Genera CSV de resultados"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Cuenta", "De", "Para", "Asunto", "Fecha", "Estado", "Contenido"])
    for r in results:
        writer.writerow([
            r.get("account", ""),
            r.get("from", ""),
            r.get("to", ""),
            r.get("subject", ""),
            r.get("date_fmt", ""),
            "LEIDO" if r.get("is_read") else "NO LEIDO",
            r.get("content", "").replace("\n", " ").replace("\r", " ")[:2000],
        ])
    return output.getvalue()


# ==================== TAB FIFA ====================

def render_fifa_tab():
    """Pestana de extraccion FIFA avanzada"""
    results = st.session_state.lectura_results
    imap_manager = st.session_state.lectura_imap

    st.subheader(f"⚽ {t('fifa_section')}")
    st.markdown(f"*{t('fifa_description')}*")

    if not results:
        st.info(f"ℹ️ {t('no_results')}")
        return

    # Opciones
    col1, col2 = st.columns(2)
    with col1:
        fifa_filter = st.selectbox(
            t("fifa_filter"),
            options=["all", "unread", "read"],
            format_func=lambda x: {"all": t("status_all"), "unread": t("status_unread"),
                                    "read": t("status_read")}[x],
            key="fifa_filter_select"
        )
    with col2:
        mark_read = st.checkbox(t("fifa_mark_read"), value=True, key="fifa_mark_read_cb")

    # Botones
    col1, col2 = st.columns(2)

    def _extract_fifa(filter_mode):
        # Filtrar correos
        if filter_mode == "unread":
            filtered = [r for r in results if not r.get("is_read", False)]
        elif filter_mode == "read":
            filtered = [r for r in results if r.get("is_read", False)]
        else:
            filtered = results

        if not filtered:
            st.warning(f"No hay correos '{filter_mode}' para procesar")
            return

        all_data = []
        progress = st.progress(0)
        status_container = st.empty()
        marked_count = 0

        fifa_keywords = ('ticket application', 'fifa', 'random selection',
                         'world cup', 'ticket allocation', 'congratulations')

        for i, r in enumerate(filtered):
            status_container.info(f"Procesando {i + 1}/{len(filtered)}...")

            html_content = r.get("html_content", "") or r.get("content", "")
            subject = r.get("subject", "")
            to_addr = r.get("to", "")
            account = r.get("account", "")
            email_date = r.get("date_fmt", "")

            # Filtro FIFA
            subj_lower = subject.lower()
            body_lower = (html_content or "")[:500].lower()
            is_fifa = any(kw in subj_lower or kw in body_lower for kw in fifa_keywords)

            if is_fifa:
                tickets = extract_fifa_tickets(html_content)
                app_number = extract_fifa_application_number(html_content)
                applicant_name = extract_fifa_applicant_name(html_content)
                team = extract_fifa_team(html_content)

                for ticket in tickets:
                    all_data.append({
                        t('fifa_col_email_madre'): account,
                        t('fifa_col_cuenta'): extract_email_only(to_addr),
                        t('fifa_col_applicant'): applicant_name,
                        t('fifa_col_team'): team,
                        t('fifa_col_date'): email_date,
                        t('fifa_col_match'): ticket['match_info'],
                        t('fifa_col_type'): ticket.get('ticket_type', ''),
                        t('fifa_col_category'): ticket['category'],
                        t('fifa_col_holder'): ticket.get('holder_name', ''),
                        t('fifa_col_quantity'): ticket['quantity'],
                        t('fifa_col_price'): ticket['price_usd'],
                    })

                # Marcar como leido
                if mark_read and tickets and not r.get("is_read", False):
                    if imap_manager.mark_seen(r.get("account"), r.get("msg_id")):
                        r["is_read"] = True
                        marked_count += 1

            progress.progress((i + 1) / len(filtered))

        status_container.empty()
        progress.empty()

        st.session_state.lectura_fifa_data = all_data
        if all_data:
            msg = f"✅ {len(all_data)} {t('fifa_found')}"
            if marked_count > 0:
                msg += f" | {marked_count} marcados como leidos"
            st.success(msg)
            _log(f"FIFA: {len(all_data)} tickets extraidos de {len(filtered)} correos")
        else:
            st.warning(t("fifa_no_data"))
            _log(f"FIFA: sin tickets en {len(filtered)} correos")

    with col1:
        if st.button(f"🎫 {t('btn_extract_fifa')}", type="primary",
                      use_container_width=True, key="extract_fifa_btn"):
            _extract_fifa(fifa_filter)

    with col2:
        if st.button(f"📩 {t('btn_extract_fifa_unread')}", use_container_width=True,
                      key="extract_fifa_unread_btn"):
            _extract_fifa("unread")

    st.markdown("---")

    # --- Mostrar datos FIFA ---
    fifa_data = st.session_state.lectura_fifa_data

    if fifa_data:
        import pandas as pd
        df = pd.DataFrame(fifa_data)
        st.dataframe(df, use_container_width=True)

        st.markdown(f"**Total:** {len(fifa_data)} tickets")

        col1, col2 = st.columns(2)
        with col1:
            # Export Excel
            try:
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='FIFA Tickets')
                st.download_button(
                    label=f"📊 {t('btn_export_excel')}",
                    data=output.getvalue(),
                    file_name=f"fifa_tickets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            except ImportError:
                st.warning("openpyxl no instalado")

        with col2:
            # Export CSV
            csv_output = io.StringIO()
            df.to_csv(csv_output, index=False)
            st.download_button(
                label=f"📄 {t('btn_export_fifa_csv')}",
                data=csv_output.getvalue(),
                file_name=f"fifa_tickets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
            )


# ==================== TAB LOGS ====================

def render_logs_tab():
    """Pestana de logs"""
    st.subheader(f"📝 {t('logs_title')}")

    logs = st.session_state.get("lectura_logs", [])

    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"🧹 {t('btn_clear_logs')}", key="clear_logs_btn"):
            st.session_state.lectura_logs = []
            st.rerun()
    with col2:
        if logs:
            log_text = "\n".join(logs)
            st.download_button(
                label=f"💾 {t('btn_download_logs')}",
                data=log_text,
                file_name=f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
            )

    if logs:
        # Mostrar logs en orden inverso (mas reciente primero)
        log_text = "\n".join(reversed(logs))
        st.text_area("", value=log_text, height=400, disabled=True, key="logs_display")
    else:
        st.info("No hay logs todavia")
