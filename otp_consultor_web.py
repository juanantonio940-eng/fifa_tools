#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OTP CONSULTOR WEB
=================
Consulta de códigos OTP de FIFA y UEFA desde correos de iCloud
Versión Streamlit con autenticación Clerk
"""

import streamlit as st
import requests
from datetime import datetime
from clerk_auth import clerk_login, clerk_logout, is_clerk_enabled

st.set_page_config(
    page_title="OTP Consultor",
    page_icon="🔑",
    layout="centered"
)

# URLs de los webhooks
WEBHOOK_URLS = {
    "FIFA": "https://fastapi-fastapi-webhook.6nzk5m.easypanel.host/webhook",
    "UEFA": "https://fastapi-fastapi-uefa.6nzk5m.easypanel.host/webhook"
}

# === TRADUCCIONES ===
TRANSLATIONS = {
    "es": {
        "title": "OTP Consultor",
        "subtitle": "Consulta códigos OTP desde correos de iCloud",
        "service_label": "Servicio",
        "email_label": "Email de iCloud",
        "email_placeholder": "ejemplo@icloud.com",
        "email_help": "Ingresa el email de iCloud asociado a la cuenta",
        "btn_search": "Consultar Código OTP",
        "warning_empty": "Por favor ingresa un email",
        "warning_invalid": "Por favor ingresa un email válido",
        "searching": "Consultando código OTP...",
        "no_messages": "No se encontraron mensajes no leídos",
        "possible_reasons": "Posibles razones",
        "reason_1": "No hay correos del día de hoy",
        "reason_2": "Todos los correos ya fueron leídos",
        "reason_3": "El correo aún no ha llegado",
        "messages_found": "Se encontraron {n} mensaje(s)",
        "message_num": "Mensaje #{n}",
        "from": "De",
        "subject": "Asunto",
        "date": "Fecha",
        "otp_code": "Código OTP",
        "click_to_copy": "Haz clic en el código para copiarlo",
        "no_otp_in_msg": "No se encontró código OTP en este mensaje",
        "error_http": "Error HTTP {code}",
        "detail": "Detalle",
        "error_timeout": "Timeout - El servidor no respondió a tiempo",
        "error_connection": "Error de conexión - No se pudo conectar al servidor",
        "error_generic": "Error",
        "query_time": "Consulta realizada",
        "info_title": "Información",
        "how_it_works": "¿Cómo funciona?",
        "step_1": "Selecciona el servicio (FIFA o UEFA)",
        "step_2": "Ingresa el email de iCloud asociado a la cuenta",
        "step_3": "El sistema consulta los correos no leídos",
        "step_4": "Extrae automáticamente el código OTP",
        "step_5": "Copia el código y úsalo antes de que expire",
        "btn_clear": "Limpiar",
        "logout": "Cerrar Sesión",
    },
    "en": {
        "title": "OTP Consultor",
        "subtitle": "Query OTP codes from iCloud emails",
        "service_label": "Service",
        "email_label": "iCloud Email",
        "email_placeholder": "example@icloud.com",
        "email_help": "Enter the iCloud email associated with the account",
        "btn_search": "Query OTP Code",
        "warning_empty": "Please enter an email",
        "warning_invalid": "Please enter a valid email",
        "searching": "Querying OTP code...",
        "no_messages": "No unread messages found",
        "possible_reasons": "Possible reasons",
        "reason_1": "No emails from today",
        "reason_2": "All emails have been read",
        "reason_3": "The email has not arrived yet",
        "messages_found": "Found {n} message(s)",
        "message_num": "Message #{n}",
        "from": "From",
        "subject": "Subject",
        "date": "Date",
        "otp_code": "OTP Code",
        "click_to_copy": "Click on the code to copy it",
        "no_otp_in_msg": "No OTP code found in this message",
        "error_http": "HTTP Error {code}",
        "detail": "Detail",
        "error_timeout": "Timeout - Server did not respond in time",
        "error_connection": "Connection error - Could not connect to server",
        "error_generic": "Error",
        "query_time": "Query performed",
        "info_title": "Information",
        "how_it_works": "How does it work?",
        "step_1": "Select the service (FIFA or UEFA)",
        "step_2": "Enter the iCloud email associated with the account",
        "step_3": "The system queries unread emails",
        "step_4": "Automatically extracts the OTP code",
        "step_5": "Copy the code and use it before it expires",
        "btn_clear": "Clear",
        "logout": "Logout",
    },
    "hi": {
        "title": "OTP कंसल्टर",
        "subtitle": "iCloud ईमेल से OTP कोड प्राप्त करें",
        "service_label": "सेवा",
        "email_label": "iCloud ईमेल",
        "email_placeholder": "example@icloud.com",
        "email_help": "खाते से जुड़ा iCloud ईमेल दर्ज करें",
        "btn_search": "OTP कोड खोजें",
        "warning_empty": "कृपया ईमेल दर्ज करें",
        "warning_invalid": "कृपया एक वैध ईमेल दर्ज करें",
        "searching": "OTP कोड खोज रहे हैं...",
        "no_messages": "कोई अपठित संदेश नहीं मिला",
        "possible_reasons": "संभावित कारण",
        "reason_1": "आज के ईमेल नहीं हैं",
        "reason_2": "सभी ईमेल पढ़े जा चुके हैं",
        "reason_3": "ईमेल अभी तक नहीं आया है",
        "messages_found": "{n} संदेश मिले",
        "message_num": "संदेश #{n}",
        "from": "प्रेषक",
        "subject": "विषय",
        "date": "तारीख",
        "otp_code": "OTP कोड",
        "click_to_copy": "कॉपी करने के लिए कोड पर क्लिक करें",
        "no_otp_in_msg": "इस संदेश में कोई OTP कोड नहीं मिला",
        "error_http": "HTTP त्रुटि {code}",
        "detail": "विवरण",
        "error_timeout": "टाइमआउट - सर्वर ने समय पर जवाब नहीं दिया",
        "error_connection": "कनेक्शन त्रुटि - सर्वर से कनेक्ट नहीं हो सका",
        "error_generic": "त्रुटि",
        "query_time": "क्वेरी की गई",
        "info_title": "जानकारी",
        "how_it_works": "यह कैसे काम करता है?",
        "step_1": "सेवा चुनें (FIFA या UEFA)",
        "step_2": "खाते से जुड़ा iCloud ईमेल दर्ज करें",
        "step_3": "सिस्टम अपठित ईमेल खोजता है",
        "step_4": "स्वचालित रूप से OTP कोड निकालता है",
        "step_5": "कोड कॉपी करें और समाप्त होने से पहले उपयोग करें",
        "btn_clear": "साफ़ करें",
        "logout": "लॉग आउट",
    }
}

# Inicializar idioma
if "language" not in st.session_state:
    st.session_state.language = "es"

def t(key):
    """Obtiene la traducción para la clave dada"""
    lang = st.session_state.get("language", "es")
    return TRANSLATIONS[lang].get(key, key)

# === VERIFICAR AUTENTICACIÓN ===
if is_clerk_enabled():
    if not clerk_login(st.session_state.language):
        st.stop()

# === ESTILOS CSS ===
st.markdown("""
<style>
    .main-title {
        text-align: center;
        padding: 20px 0;
    }
    .otp-box {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .otp-code {
        font-size: 48px;
        font-weight: bold;
        color: #4ade80;
        font-family: 'Courier New', monospace;
        letter-spacing: 8px;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# === BARRA SUPERIOR: IDIOMA Y LOGOUT ===
col_spacer, col_lang, col_logout = st.columns([3, 1, 1])

with col_lang:
    lang_names = {"es": "Español", "en": "English", "hi": "हिन्दी"}
    lang_options = ["es", "en", "hi"]

    language = st.selectbox(
        "🌐",
        options=lang_options,
        format_func=lambda x: lang_names.get(x, x),
        index=lang_options.index(st.session_state.language) if st.session_state.language in lang_options else 0,
        label_visibility="collapsed"
    )

    if language != st.session_state.language:
        st.session_state.language = language
        st.rerun()

with col_logout:
    if st.session_state.get('clerk_authenticated', False):
        if st.button("🚪", help=t('logout'), use_container_width=True):
            clerk_logout()

# === HEADER ===
st.markdown(f"<h1 class='main-title'>🔑 {t('title')}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center;'>{t('subtitle')}</p>", unsafe_allow_html=True)

# Mostrar usuario autenticado
if st.session_state.get('clerk_authenticated', False):
    user = st.session_state.get('clerk_user', {})
    name = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
    email = user.get('email', '')
    if name or email:
        st.markdown(f"<p style='text-align: center; color: #666;'>👤 {name or email}</p>", unsafe_allow_html=True)

st.markdown("---")

# === FORMULARIO DE CONSULTA ===
def clear_email():
    st.session_state.email_field = ""

# Inicializar servicio seleccionado
if "selected_service" not in st.session_state:
    st.session_state.selected_service = "FIFA"

# Selector de servicio
service = st.selectbox(
    f"🎮 {t('service_label')}",
    options=["FIFA", "UEFA"],
    index=["FIFA", "UEFA"].index(st.session_state.selected_service),
    key="service_selector"
)

if service != st.session_state.selected_service:
    st.session_state.selected_service = service

email = st.text_input(
    f"📧 {t('email_label')}",
    placeholder=t('email_placeholder'),
    help=t('email_help'),
    key="email_field"
)

col_btn1, col_btn2 = st.columns([3, 1])

with col_btn1:
    consultar = st.button(f"🔍 {t('btn_search')}", type="primary", use_container_width=True)

with col_btn2:
    st.button("🗑️", use_container_width=True, help=t('btn_clear'), on_click=clear_email)

# === RESULTADOS ===
if consultar:
    if not email:
        st.warning(f"⚠️ {t('warning_empty')}")
    elif "@" not in email or "." not in email:
        st.warning(f"⚠️ {t('warning_invalid')}")
    else:
        st.markdown("---")

        with st.spinner(f"🔄 {t('searching')}"):
            try:
                # Obtener URL del webhook según el servicio seleccionado
                webhook_url = WEBHOOK_URLS[st.session_state.selected_service]

                # Hacer petición POST
                response = requests.post(
                    webhook_url,
                    json={"email": email},
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()

                    # Procesar respuesta según el servicio
                    if st.session_state.selected_service == "UEFA":
                        # UEFA usa SimpleResponse: {otp_code, error}
                        otp_code = data.get("otp_code")
                        error = data.get("error")

                        if error:
                            st.warning(f"⚠️ {error}")
                            with st.expander(f"ℹ️ {t('possible_reasons')}"):
                                st.markdown(f"""
                                - {t('reason_1')}
                                - {t('reason_2')}
                                - {t('reason_3')}
                                """)
                        elif otp_code:
                            st.markdown(f"### 🔑 {t('otp_code')}")
                            st.markdown(
                                f"""
                                <div class="otp-box">
                                    <span class="otp-code">{otp_code}</span>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            st.code(otp_code, language=None)
                            st.caption(f"👆 {t('click_to_copy')}")
                        else:
                            st.warning(f"⚠️ {t('no_otp_in_msg')}")
                    else:
                        # FIFA usa messages: [{otp_code, from_, subject, date}, ...]
                        messages = data.get("messages", [])

                        if not messages:
                            st.warning(f"⚠️ {t('no_messages')}")

                            with st.expander(f"ℹ️ {t('possible_reasons')}"):
                                st.markdown(f"""
                                - {t('reason_1')}
                                - {t('reason_2')}
                                - {t('reason_3')}
                                """)
                        else:
                            for msg in messages:
                                otp_code = msg.get('otp_code')

                                if otp_code:
                                    st.markdown(f"### 🔑 {t('otp_code')}")

                                    # Mostrar código grande y destacado
                                    st.markdown(
                                        f"""
                                        <div class="otp-box">
                                            <span class="otp-code">{otp_code}</span>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )

                                    # Código copiable
                                    st.code(otp_code, language=None)
                                    st.caption(f"👆 {t('click_to_copy')}")
                                    break

                                else:
                                    st.warning(f"⚠️ {t('no_otp_in_msg')}")

                else:
                    st.error(f"❌ {t('error_http').format(code=response.status_code)}")
                    try:
                        error_data = response.json()
                        st.error(f"{t('detail')}: {error_data.get('detail', 'Error')}")
                    except:
                        st.error(f"Response: {response.text}")

            except requests.exceptions.Timeout:
                st.error(f"❌ {t('error_timeout')}")

            except requests.exceptions.ConnectionError:
                st.error(f"❌ {t('error_connection')}")

            except Exception as e:
                st.error(f"❌ {t('error_generic')}: {str(e)}")

        st.caption(f"🕐 {t('query_time')}: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

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
    """)

# Footer
st.caption(f"OTP Consultor v2.0 | {datetime.now().strftime('%d/%m/%Y')}")
