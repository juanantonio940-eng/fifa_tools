#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PÁGINA UEFA OTP
===============
Consulta de códigos OTP de UEFA desde correos de iCloud
"""

import streamlit as st
import requests
from datetime import datetime

# URL del webhook UEFA
WEBHOOK_URL = "https://fastapi-fastapi-uefa.6nzk5m.easypanel.host/webhook"

# === TRADUCCIONES ===
TRANSLATIONS = {
    "es": {
        "title": "Consultar OTP UEFA",
        "subtitle": "Obtén el código OTP de UEFA desde iCloud",
        "email_label": "Email de iCloud",
        "email_placeholder": "ejemplo@icloud.com",
        "email_help": "Ingresa el email de iCloud asociado a la cuenta UEFA",
        "btn_search": "Consultar Código OTP",
        "warning_empty": "Por favor ingresa un email",
        "warning_invalid": "Por favor ingresa un email válido",
        "searching": "Consultando código OTP...",
        "no_messages": "No se encontraron mensajes de UEFA no leídos",
        "possible_reasons": "Posibles razones",
        "reason_1": "No hay correos de UEFA del día de hoy",
        "reason_2": "Todos los correos ya fueron leídos",
        "reason_3": "El correo aún no ha llegado",
        "otp_code": "Código OTP",
        "click_to_copy": "Haz clic en el código para copiarlo",
        "no_otp_in_msg": "No se encontró código OTP",
        "error_http": "Error HTTP {code}",
        "detail": "Detalle",
        "error_timeout": "Timeout - El servidor no respondió a tiempo",
        "error_connection": "Error de conexión - No se pudo conectar al servidor",
        "error_generic": "Error",
        "query_time": "Consulta realizada",
        "info_title": "Información",
        "how_it_works": "¿Cómo funciona?",
        "step_1": "Ingresa el email de iCloud asociado a la cuenta UEFA",
        "step_2": "El sistema consulta los correos no leídos de UEFA",
        "step_3": "Extrae automáticamente el código OTP",
        "step_4": "Copia el código y úsalo antes de que expire",
        "btn_clear": "Limpiar",
    },
    "en": {
        "title": "Query UEFA OTP",
        "subtitle": "Get UEFA OTP code from iCloud",
        "email_label": "iCloud Email",
        "email_placeholder": "example@icloud.com",
        "email_help": "Enter the iCloud email associated with the UEFA account",
        "btn_search": "Query OTP Code",
        "warning_empty": "Please enter an email",
        "warning_invalid": "Please enter a valid email",
        "searching": "Querying OTP code...",
        "no_messages": "No unread UEFA messages found",
        "possible_reasons": "Possible reasons",
        "reason_1": "No UEFA emails from today",
        "reason_2": "All emails have been read",
        "reason_3": "The email has not arrived yet",
        "otp_code": "OTP Code",
        "click_to_copy": "Click on the code to copy it",
        "no_otp_in_msg": "No OTP code found",
        "error_http": "HTTP Error {code}",
        "detail": "Detail",
        "error_timeout": "Timeout - Server did not respond in time",
        "error_connection": "Connection error - Could not connect to server",
        "error_generic": "Error",
        "query_time": "Query performed",
        "info_title": "Information",
        "how_it_works": "How does it work?",
        "step_1": "Enter the iCloud email associated with the UEFA account",
        "step_2": "The system queries unread UEFA emails",
        "step_3": "Automatically extracts the OTP code",
        "step_4": "Copy the code and use it before it expires",
        "btn_clear": "Clear",
    },
    "hi": {
        "title": "UEFA OTP प्राप्त करें",
        "subtitle": "iCloud से UEFA OTP कोड प्राप्त करें",
        "email_label": "iCloud ईमेल",
        "email_placeholder": "example@icloud.com",
        "email_help": "UEFA खाते से जुड़ा iCloud ईमेल दर्ज करें",
        "btn_search": "OTP कोड खोजें",
        "warning_empty": "कृपया ईमेल दर्ज करें",
        "warning_invalid": "कृपया एक वैध ईमेल दर्ज करें",
        "searching": "OTP कोड खोज रहे हैं...",
        "no_messages": "कोई अपठित UEFA संदेश नहीं मिला",
        "possible_reasons": "संभावित कारण",
        "reason_1": "आज के UEFA ईमेल नहीं हैं",
        "reason_2": "सभी ईमेल पढ़े जा चुके हैं",
        "reason_3": "ईमेल अभी तक नहीं आया है",
        "otp_code": "OTP कोड",
        "click_to_copy": "कॉपी करने के लिए कोड पर क्लिक करें",
        "no_otp_in_msg": "कोई OTP कोड नहीं मिला",
        "error_http": "HTTP त्रुटि {code}",
        "detail": "विवरण",
        "error_timeout": "टाइमआउट - सर्वर ने समय पर जवाब नहीं दिया",
        "error_connection": "कनेक्शन त्रुटि - सर्वर से कनेक्ट नहीं हो सका",
        "error_generic": "त्रुटि",
        "query_time": "क्वेरी की गई",
        "info_title": "जानकारी",
        "how_it_works": "यह कैसे काम करता है?",
        "step_1": "UEFA खाते से जुड़ा iCloud ईमेल दर्ज करें",
        "step_2": "सिस्टम अपठित UEFA ईमेल खोजता है",
        "step_3": "स्वचालित रूप से OTP कोड निकालता है",
        "step_4": "कोड कॉपी करें और समाप्त होने से पहले उपयोग करें",
        "btn_clear": "साफ़ करें",
    }
}


def t(key):
    """Obtiene la traducción para la clave dada"""
    lang = st.session_state.get("language", "es")
    return TRANSLATIONS[lang].get(key, key)


def render():
    """Renderiza la página de OTP UEFA"""

    # === ESTILOS CSS ===
    st.markdown("""
    <style>
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
    </style>
    """, unsafe_allow_html=True)

    # === HEADER ===
    st.title(f"🔑 {t('title')}")
    st.markdown(f"{t('subtitle')}")

    st.markdown("---")

    # === FORMULARIO DE CONSULTA ===
    def clear_email():
        st.session_state.email_field_uefa_otp = ""

    email = st.text_input(
        f"📧 {t('email_label')}",
        placeholder=t('email_placeholder'),
        help=t('email_help'),
        key="email_field_uefa_otp"
    )

    col_btn1, col_btn2 = st.columns([3, 1])

    with col_btn1:
        consultar = st.button(f"🔍 {t('btn_search')}", type="primary", use_container_width=True, key="btn_consultar_uefa")

    with col_btn2:
        st.button("🗑️", use_container_width=True, help=t('btn_clear'), on_click=clear_email, key="btn_clear_uefa")

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
                    response = requests.post(
                        WEBHOOK_URL,
                        json={"email": email},
                        headers={"Content-Type": "application/json"},
                        timeout=30
                    )

                    if response.status_code == 200:
                        data = response.json()

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
        """)
