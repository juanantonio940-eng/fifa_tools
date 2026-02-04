#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PÁGINA COMPROBANTES ANYTICKETS
==============================
Subir comprobantes a Anytickets - Individual y Masivo
"""

import streamlit as st
import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv, set_key

# Importar cliente de Anytickets
from modules.anytickets_client import AnyTicketsClient

# Rutas de configuración
ENV_PATH = Path(__file__).parent.parent / '.env'
CONFIG_PATH = Path(__file__).parent.parent / 'anytickets_config.json'

# Cargar variables de entorno
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)


def load_saved_tokens():
    """Cargar tokens guardados desde config JSON o .env"""
    # Primero intentar desde JSON (prioridad)
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                return config.get('bearer_token', ''), config.get('dev_token', '')
        except:
            pass

    # Fallback a .env
    return os.getenv('ANYTICKETS_BEARER_TOKEN', ''), os.getenv('ANYTICKETS_DEV_TOKEN', '')


def save_tokens(bearer_token, dev_token):
    """Guardar tokens en archivo JSON"""
    config = {
        'bearer_token': bearer_token,
        'dev_token': dev_token,
        'updated_at': datetime.now().isoformat()
    }
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
    return True

# === TRADUCCIONES ===
TRANSLATIONS = {
    "es": {
        "title": "Comprobantes Anytickets",
        "subtitle": "Subir comprobantes de transferencia a Anytickets",
        "config_section": "Configuracion API",
        "bearer_token": "Bearer Token",
        "dev_token": "Dev Token",
        "tokens_help": "Los tokens se cargan automaticamente si fueron guardados",
        "btn_save_tokens": "Guardar Tokens",
        "tokens_saved": "Tokens guardados correctamente",
        "tokens_loaded": "Tokens cargados desde configuracion guardada",
        "mode_section": "Modo de Subida",
        "mode_individual": "Individual",
        "mode_masivo": "Masivo (carpeta)",
        "config_options": "Opciones",
        "marketplace": "Marketplace",
        "transfer_source": "Transfer Source",
        "transfer_source_help": "Solo requerido para GoTickets",
        "individual_section": "Subida Individual",
        "invoice_id": "Invoice ID",
        "invoice_id_help": "ID numerico de la factura",
        "select_image": "Seleccionar Imagen",
        "masivo_section": "Subida Masiva",
        "upload_images": "Subir Imagenes",
        "upload_images_help": "Los archivos deben tener nombre numerico (ej: 12345.png)",
        "images_found": "imagenes validas encontradas",
        "btn_upload": "Subir Comprobante",
        "btn_upload_all": "Subir Todo",
        "btn_clear": "Limpiar",
        "result_section": "Resultado",
        "uploading": "Subiendo...",
        "success": "Exito",
        "error": "Error",
        "completed": "Completado",
        "progress": "Progreso",
        "summary": "Resumen",
        "total_processed": "Total procesados",
        "successful": "Exitosos",
        "failed": "Fallidos",
        "error_details": "Detalles de errores",
        "warning_tokens": "Configura los tokens de API",
        "warning_invoice": "Invoice ID es requerido",
        "warning_invoice_num": "Invoice ID debe ser un numero",
        "warning_image": "Selecciona una imagen",
        "warning_no_images": "No se encontraron imagenes validas",
        "info_title": "Informacion",
        "how_it_works": "Como funciona",
        "step_1": "Configura los tokens de API (Bearer y Dev)",
        "step_2": "Selecciona el marketplace (general o gotickets)",
        "step_3": "Para subida individual: ingresa Invoice ID y selecciona imagen",
        "step_4": "Para subida masiva: sube imagenes con nombre numerico (invoice_id.png)",
        "step_5": "El sistema sube la imagen y confirma el fulfillment",
    },
    "en": {
        "title": "Anytickets Receipts",
        "subtitle": "Upload transfer receipts to Anytickets",
        "config_section": "API Configuration",
        "bearer_token": "Bearer Token",
        "dev_token": "Dev Token",
        "tokens_help": "Tokens are loaded automatically if saved",
        "btn_save_tokens": "Save Tokens",
        "tokens_saved": "Tokens saved successfully",
        "tokens_loaded": "Tokens loaded from saved configuration",
        "mode_section": "Upload Mode",
        "mode_individual": "Individual",
        "mode_masivo": "Bulk (folder)",
        "config_options": "Options",
        "marketplace": "Marketplace",
        "transfer_source": "Transfer Source",
        "transfer_source_help": "Only required for GoTickets",
        "individual_section": "Individual Upload",
        "invoice_id": "Invoice ID",
        "invoice_id_help": "Numeric invoice ID",
        "select_image": "Select Image",
        "masivo_section": "Bulk Upload",
        "upload_images": "Upload Images",
        "upload_images_help": "Files must have numeric names (e.g., 12345.png)",
        "images_found": "valid images found",
        "btn_upload": "Upload Receipt",
        "btn_upload_all": "Upload All",
        "btn_clear": "Clear",
        "result_section": "Result",
        "uploading": "Uploading...",
        "success": "Success",
        "error": "Error",
        "completed": "Completed",
        "progress": "Progress",
        "summary": "Summary",
        "total_processed": "Total processed",
        "successful": "Successful",
        "failed": "Failed",
        "error_details": "Error details",
        "warning_tokens": "Configure API tokens",
        "warning_invoice": "Invoice ID is required",
        "warning_invoice_num": "Invoice ID must be a number",
        "warning_image": "Select an image",
        "warning_no_images": "No valid images found",
        "info_title": "Information",
        "how_it_works": "How it works",
        "step_1": "Configure API tokens (Bearer and Dev)",
        "step_2": "Select marketplace (general or gotickets)",
        "step_3": "For individual upload: enter Invoice ID and select image",
        "step_4": "For bulk upload: upload images with numeric names (invoice_id.png)",
        "step_5": "The system uploads the image and confirms fulfillment",
    },
    "hi": {
        "title": "Anytickets रसीदें",
        "subtitle": "Anytickets पर ट्रांसफर रसीदें अपलोड करें",
        "config_section": "API कॉन्फ़िगरेशन",
        "bearer_token": "Bearer Token",
        "dev_token": "Dev Token",
        "tokens_help": "टोकन स्वचालित रूप से लोड होते हैं यदि सहेजे गए हैं",
        "btn_save_tokens": "टोकन सहेजें",
        "tokens_saved": "टोकन सफलतापूर्वक सहेजे गए",
        "tokens_loaded": "सहेजे गए कॉन्फ़िगरेशन से टोकन लोड किए गए",
        "mode_section": "अपलोड मोड",
        "mode_individual": "व्यक्तिगत",
        "mode_masivo": "थोक (फ़ोल्डर)",
        "config_options": "विकल्प",
        "marketplace": "मार्केटप्लेस",
        "transfer_source": "Transfer Source",
        "transfer_source_help": "केवल GoTickets के लिए आवश्यक",
        "individual_section": "व्यक्तिगत अपलोड",
        "invoice_id": "Invoice ID",
        "invoice_id_help": "संख्यात्मक चालान ID",
        "select_image": "छवि चुनें",
        "masivo_section": "थोक अपलोड",
        "upload_images": "छवियाँ अपलोड करें",
        "upload_images_help": "फ़ाइलों में संख्यात्मक नाम होना चाहिए (जैसे: 12345.png)",
        "images_found": "मान्य छवियाँ मिलीं",
        "btn_upload": "रसीद अपलोड करें",
        "btn_upload_all": "सभी अपलोड करें",
        "btn_clear": "साफ़ करें",
        "result_section": "परिणाम",
        "uploading": "अपलोड हो रहा है...",
        "success": "सफल",
        "error": "त्रुटि",
        "completed": "पूर्ण",
        "progress": "प्रगति",
        "summary": "सारांश",
        "total_processed": "कुल प्रोसेस",
        "successful": "सफल",
        "failed": "विफल",
        "error_details": "त्रुटि विवरण",
        "warning_tokens": "API टोकन कॉन्फ़िगर करें",
        "warning_invoice": "Invoice ID आवश्यक है",
        "warning_invoice_num": "Invoice ID एक संख्या होनी चाहिए",
        "warning_image": "एक छवि चुनें",
        "warning_no_images": "कोई मान्य छवि नहीं मिली",
        "info_title": "जानकारी",
        "how_it_works": "यह कैसे काम करता है",
        "step_1": "API टोकन कॉन्फ़िगर करें (Bearer और Dev)",
        "step_2": "मार्केटप्लेस चुनें (general या gotickets)",
        "step_3": "व्यक्तिगत अपलोड के लिए: Invoice ID दर्ज करें और छवि चुनें",
        "step_4": "थोक अपलोड के लिए: संख्यात्मक नाम वाली छवियाँ अपलोड करें",
        "step_5": "सिस्टम छवि अपलोड करता है और fulfillment की पुष्टि करता है",
    }
}


def t(key):
    """Obtiene la traducción para la clave dada"""
    lang = st.session_state.get("language", "es")
    return TRANSLATIONS[lang].get(key, key)


def get_valid_images(uploaded_files):
    """Filtrar archivos con nombre numérico válido"""
    valid_images = []
    for file in uploaded_files:
        # Obtener nombre sin extensión
        name = Path(file.name).stem
        if name.isdigit():
            valid_images.append(file)
    return sorted(valid_images, key=lambda x: int(Path(x.name).stem))


def render():
    """Renderiza la página de Comprobantes Anytickets"""

    st.title(f"📤 {t('title')}")
    st.markdown(f"{t('subtitle')}")

    st.markdown("---")

    # === CONFIGURACIÓN API ===
    with st.expander(f"🔑 {t('config_section')}", expanded=True):
        # Cargar tokens guardados
        saved_bearer, saved_dev = load_saved_tokens()

        col1, col2 = st.columns(2)

        with col1:
            bearer_token = st.text_input(
                t('bearer_token'),
                value=saved_bearer,
                type="password",
                key="anytickets_bearer"
            )

        with col2:
            dev_token = st.text_input(
                t('dev_token'),
                value=saved_dev,
                type="password",
                key="anytickets_dev"
            )

        # Botón para guardar tokens
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button(f"💾 {t('btn_save_tokens')}", use_container_width=True):
                if bearer_token and dev_token:
                    save_tokens(bearer_token, dev_token)
                    st.success(f"✅ {t('tokens_saved')}")
                else:
                    st.warning(f"⚠️ {t('warning_tokens')}")

        if saved_bearer or saved_dev:
            st.caption(f"ℹ️ {t('tokens_loaded')}")

    st.markdown("---")

    # === MODO DE SUBIDA ===
    st.subheader(f"📁 {t('mode_section')}")

    upload_mode = st.radio(
        t('mode_section'),
        [t('mode_individual'), t('mode_masivo')],
        horizontal=True,
        label_visibility="collapsed"
    )

    # === OPCIONES COMUNES ===
    st.subheader(f"⚙️ {t('config_options')}")

    col1, col2 = st.columns(2)

    with col1:
        marketplace = st.selectbox(
            t('marketplace'),
            ['general', 'gotickets'],
            key="anytickets_marketplace"
        )

    with col2:
        transfer_source = st.text_input(
            t('transfer_source'),
            help=t('transfer_source_help'),
            key="anytickets_transfer_source"
        )

    st.markdown("---")

    # === SUBIDA INDIVIDUAL ===
    if upload_mode == t('mode_individual'):
        st.subheader(f"📄 {t('individual_section')}")

        col1, col2 = st.columns([1, 2])

        with col1:
            invoice_id = st.text_input(
                t('invoice_id'),
                help=t('invoice_id_help'),
                key="anytickets_invoice_id"
            )

        with col2:
            uploaded_file = st.file_uploader(
                t('select_image'),
                type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
                key="anytickets_single_file"
            )

        if uploaded_file:
            st.image(uploaded_file, caption=uploaded_file.name, width=300)

        # Botón subir
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            btn_upload = st.button(f"📤 {t('btn_upload')}", type="primary", use_container_width=True)

        with col2:
            if st.button(f"🗑️ {t('btn_clear')}", use_container_width=True):
                st.rerun()

        # Procesar subida individual
        if btn_upload:
            # Validaciones
            if not bearer_token or not dev_token:
                st.warning(f"⚠️ {t('warning_tokens')}")
            elif not invoice_id:
                st.warning(f"⚠️ {t('warning_invoice')}")
            elif not invoice_id.isdigit():
                st.warning(f"⚠️ {t('warning_invoice_num')}")
            elif not uploaded_file:
                st.warning(f"⚠️ {t('warning_image')}")
            else:
                st.markdown("---")
                st.subheader(f"📋 {t('result_section')}")

                with st.spinner(f"🔄 {t('uploading')}"):
                    try:
                        # Leer bytes del archivo
                        image_bytes = uploaded_file.read()

                        with AnyTicketsClient(bearer_token, dev_token) as client:
                            result = client.complete_fulfillment(
                                invoice_id=int(invoice_id),
                                image_source=image_bytes,
                                source_type='bytes',
                                marketplace=marketplace,
                                transfer_source=transfer_source if transfer_source else None,
                                skip_confirm=True
                            )

                        if result.get('success'):
                            st.success(f"✅ {t('success')}")
                            st.write(f"**Invoice ID:** {invoice_id}")
                            st.write(f"**URL:** {result.get('proof_url', 'N/A')}")
                        else:
                            st.error(f"❌ {t('error')}: {result.get('error', 'Unknown')}")

                    except Exception as e:
                        st.error(f"❌ {t('error')}: {str(e)}")

                st.caption(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    # === SUBIDA MASIVA ===
    else:
        st.subheader(f"📁 {t('masivo_section')}")

        uploaded_files = st.file_uploader(
            t('upload_images'),
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
            accept_multiple_files=True,
            help=t('upload_images_help'),
            key="anytickets_bulk_files"
        )

        valid_images = []
        if uploaded_files:
            valid_images = get_valid_images(uploaded_files)
            st.info(f"📷 **{len(valid_images)}** {t('images_found')}")

            if valid_images:
                with st.expander("👁️ Vista previa", expanded=False):
                    cols = st.columns(4)
                    for i, img in enumerate(valid_images[:8]):
                        with cols[i % 4]:
                            st.image(img, caption=img.name, width=100)
                    if len(valid_images) > 8:
                        st.caption(f"... y {len(valid_images) - 8} más")

        # Botones
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            btn_upload_all = st.button(
                f"📤 {t('btn_upload_all')}",
                type="primary",
                use_container_width=True,
                disabled=len(valid_images) == 0
            )

        with col2:
            if st.button(f"🗑️ {t('btn_clear')}", use_container_width=True):
                st.rerun()

        # Procesar subida masiva
        if btn_upload_all:
            # Validaciones
            if not bearer_token or not dev_token:
                st.warning(f"⚠️ {t('warning_tokens')}")
            elif not valid_images:
                st.warning(f"⚠️ {t('warning_no_images')}")
            else:
                st.markdown("---")
                st.subheader(f"📋 {t('result_section')}")

                total = len(valid_images)
                exitosos = 0
                fallidos = []

                progress_bar = st.progress(0)
                status_text = st.empty()
                log_container = st.container()

                with AnyTicketsClient(bearer_token, dev_token) as client:
                    for i, img_file in enumerate(valid_images):
                        invoice_id = int(Path(img_file.name).stem)
                        status_text.text(f"🔄 {t('uploading')} {i+1}/{total} - Invoice {invoice_id}")

                        try:
                            # Leer bytes
                            image_bytes = img_file.read()

                            result = client.complete_fulfillment(
                                invoice_id=invoice_id,
                                image_source=image_bytes,
                                source_type='bytes',
                                marketplace=marketplace,
                                transfer_source=transfer_source if transfer_source else None,
                                skip_confirm=True
                            )

                            if result.get('success'):
                                exitosos += 1
                                with log_container:
                                    st.write(f"✅ Invoice {invoice_id} - OK")
                            else:
                                fallidos.append((invoice_id, result.get('error', 'Unknown')))
                                with log_container:
                                    st.write(f"❌ Invoice {invoice_id} - {result.get('error', 'Unknown')}")

                        except Exception as e:
                            fallidos.append((invoice_id, str(e)))
                            with log_container:
                                st.write(f"❌ Invoice {invoice_id} - {str(e)}")

                        # Actualizar progreso
                        progress_bar.progress((i + 1) / total)

                # Resumen final
                status_text.text(f"✅ {t('completed')}")

                st.markdown("---")
                st.subheader(f"📊 {t('summary')}")

                col1, col2, col3 = st.columns(3)
                col1.metric(t('total_processed'), f"{exitosos + len(fallidos)}/{total}")
                col2.metric(t('successful'), exitosos)
                col3.metric(t('failed'), len(fallidos))

                if fallidos:
                    with st.expander(f"❌ {t('error_details')}", expanded=True):
                        for inv_id, error in fallidos:
                            st.write(f"• **Invoice {inv_id}:** {error}")

                st.caption(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    # === INFORMACIÓN ===
    st.markdown("---")

    with st.expander(f"ℹ️ {t('info_title')}"):
        st.markdown(f"""
        ### {t('how_it_works')}

        1. {t('step_1')}
        2. {t('step_2')}
        3. {t('step_3')}
        4. {t('step_4')}
        5. {t('step_5')}

        ---

        **API Endpoints:**
        - Upload: `POST /api/v1/fulfillment/upload/static`
        - Confirm: `POST /api/v1/fulfillment/confirm`

        **Marketplaces:**
        - `general` - Marketplace general
        - `gotickets` - GoTickets (requiere Transfer Source)
        """)
