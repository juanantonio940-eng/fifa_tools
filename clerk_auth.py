#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CLERK AUTHENTICATION - OTP CONSULTOR
====================================
Integración de Clerk para autenticación
"""

import streamlit as st
import os
import requests
import base64
import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# Configurar logger de seguridad
LOGS_DIR = Path(__file__).parent / 'logs'
LOGS_DIR.mkdir(parents=True, exist_ok=True)
SECURITY_LOG_FILE = LOGS_DIR / 'security.log'

security_logger = logging.getLogger('security_otp')
security_logger.setLevel(logging.INFO)
if not security_logger.handlers:
    file_handler = logging.FileHandler(SECURITY_LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    security_logger.addHandler(file_handler)


def log_security_event(event_type, details="", success=True):
    """Registra eventos de seguridad"""
    status = "SUCCESS" if success else "FAILED"
    message = f"{event_type} | Status: {status}"
    if details:
        message += f" | {details}"
    if success:
        security_logger.info(message)
    else:
        security_logger.warning(message)

# Configuración de Clerk
CLERK_PUBLISHABLE_KEY = os.getenv('CLERK_PUBLISHABLE_KEY', '')
CLERK_SECRET_KEY = os.getenv('CLERK_SECRET_KEY', '')
CLERK_DOMAIN = os.getenv('CLERK_DOMAIN', 'pleasant-ringtail-37.accounts.dev')
USE_CLERK_AUTH = os.getenv('USE_CLERK_AUTH', 'true').lower() == 'true'


def verify_clerk_user(user_id: str) -> dict:
    """Verifica un usuario de Clerk con el backend"""
    if not CLERK_SECRET_KEY:
        return None

    try:
        headers = {
            'Authorization': f'Bearer {CLERK_SECRET_KEY}',
            'Content-Type': 'application/json'
        }

        response = requests.get(
            f'https://api.clerk.com/v1/users/{user_id}',
            headers=headers
        )

        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error verifying Clerk user: {e}")
        return None


def decode_jwt_payload(token: str) -> dict:
    """Decodifica el payload de un JWT sin verificar firma"""
    try:
        # JWT tiene 3 partes separadas por punto: header.payload.signature
        parts = token.split('.')
        if len(parts) != 3:
            return None

        # El payload es la segunda parte, codificada en base64url
        payload_b64 = parts[1]
        # Agregar padding si es necesario
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += '=' * padding

        # Reemplazar caracteres base64url por base64 estándar
        payload_b64 = payload_b64.replace('-', '+').replace('_', '/')

        payload_json = base64.b64decode(payload_b64).decode('utf-8')
        return json.loads(payload_json)
    except Exception as e:
        print(f"[JWT] Error decodificando: {e}")
        return None


def get_user_from_handshake(handshake: str) -> dict:
    """
    Extrae el user_id del __clerk_handshake y obtiene datos del usuario.
    El handshake contiene tokens codificados que incluyen el JWT de sesión.
    """
    if not CLERK_SECRET_KEY:
        return None

    try:
        # El handshake puede ser un JWT o datos codificados en base64
        # Intentar decodificar como base64 primero
        try:
            # Agregar padding si es necesario
            padding = 4 - len(handshake) % 4
            if padding != 4:
                handshake_padded = handshake + '=' * padding
            else:
                handshake_padded = handshake

            handshake_padded = handshake_padded.replace('-', '+').replace('_', '/')
            decoded = base64.b64decode(handshake_padded).decode('utf-8')
            handshake_data = json.loads(decoded)
            print(f"[Clerk Handshake] Decodificado como JSON: {list(handshake_data.keys()) if isinstance(handshake_data, dict) else type(handshake_data)}")
        except:
            # Si no es JSON base64, puede ser un JWT directamente
            handshake_data = None

        user_id = None

        # Buscar el token de sesión en el handshake
        if isinstance(handshake_data, dict):
            # Buscar en diferentes ubicaciones posibles
            session_token = None

            # Formato 1: cookies con __session
            if 'cookies' in handshake_data:
                cookies = handshake_data.get('cookies', {})
                session_token = cookies.get('__session')

            # Formato 2: directo en el handshake
            if not session_token and '__session' in handshake_data:
                session_token = handshake_data.get('__session')

            # Formato 3: token directo
            if not session_token and 'token' in handshake_data:
                session_token = handshake_data.get('token')

            # Formato 4: session_token
            if not session_token and 'session_token' in handshake_data:
                session_token = handshake_data.get('session_token')

            if session_token:
                print(f"[Clerk Handshake] Token de sesion encontrado")
                payload = decode_jwt_payload(session_token)
                if payload:
                    user_id = payload.get('sub')
                    print(f"[Clerk Handshake] User ID desde sesion: {user_id}")

        # Si no encontramos en el handshake, intentar decodificar como JWT directamente
        if not user_id:
            payload = decode_jwt_payload(handshake)
            if payload:
                user_id = payload.get('sub')
                print(f"[Clerk Handshake] User ID desde JWT directo: {user_id}")

        # Si tenemos user_id, obtener los datos completos del usuario
        if user_id:
            return verify_clerk_user(user_id)

    except Exception as e:
        print(f"[Clerk Handshake] Error: {e}")

    return None


def get_user_from_dev_browser_token(token: str) -> dict:
    """
    Obtiene el usuario desde un token de desarrollo (dvb_).
    Usa el endpoint de clients de Clerk para verificar el token.
    """
    if not CLERK_SECRET_KEY:
        return None

    try:
        headers = {
            'Authorization': f'Bearer {CLERK_SECRET_KEY}',
            'Content-Type': 'application/json'
        }

        # Verificar el client token con Clerk
        verify_url = 'https://api.clerk.com/v1/clients/verify'
        response = requests.post(
            verify_url,
            headers=headers,
            json={'token': token}
        )
        print(f"[Clerk DVB] Verificacion cliente: {response.status_code}")

        if response.status_code == 200:
            client_data = response.json()
            print(f"[Clerk DVB] Cliente verificado: {client_data.get('id', 'N/A')}")

            # Buscar sesiones activas del cliente
            sessions = client_data.get('sessions', [])
            if sessions:
                # Tomar la sesion mas reciente
                active_session = None
                for session in sessions:
                    if session.get('status') == 'active':
                        active_session = session
                        break

                if not active_session and sessions:
                    active_session = sessions[0]

                if active_session:
                    user_id = active_session.get('user_id')
                    print(f"[Clerk DVB] User ID desde sesion: {user_id}")
                    if user_id:
                        user_data = verify_clerk_user(user_id)
                        if user_data:
                            email = user_data.get('email_addresses', [{}])[0].get('email_address', 'N/A')
                            print(f"[Clerk DVB] Email accediendo: {email}")
                        return user_data
        else:
            print(f"[Clerk DVB] Error verificacion: {response.text}")

    except Exception as e:
        print(f"[Clerk DVB] Excepcion: {e}")

    return None


def get_user_from_clerk_token(token: str) -> dict:
    """
    Intenta extraer el user_id del token y obtener datos del usuario.
    Soporta tokens JWT y tokens de desarrollo (dvb_).
    """
    if not CLERK_SECRET_KEY:
        return None

    try:
        # Si es un token de desarrollo (dvb_), usar metodo especifico
        if token.startswith('dvb_'):
            print(f"[Clerk Token] Token de desarrollo detectado (dvb_)")
            user_data = get_user_from_dev_browser_token(token)
            if user_data:
                return user_data

        # Intentar decodificar como JWT
        payload = decode_jwt_payload(token)
        if payload:
            user_id = payload.get('sub')
            if user_id:
                print(f"[Clerk Token] User ID desde JWT: {user_id}")
                user_data = verify_clerk_user(user_id)
                if user_data:
                    email = user_data.get('email_addresses', [{}])[0].get('email_address', 'N/A')
                    print(f"[Clerk Token] Email accediendo: {email}")
                    return user_data

        # NO usar fallback de "usuario reciente" - es incorrecto
        print(f"[Clerk Token] No se pudo obtener usuario del token")

    except Exception as e:
        print(f"[Clerk API] Excepcion: {e}")

    return None


def clerk_login(lang="es"):
    """
    Muestra la pantalla de login de Clerk.
    Retorna True si está autenticado, False si no.
    """

    if not USE_CLERK_AUTH:
        return True  # Si Clerk está deshabilitado, permitir acceso

    # Verificar si ya hay usuario en session_state
    if st.session_state.get('clerk_authenticated', False):
        return True

    # Verificar si viene token de Clerk en la URL
    try:
        # Debug: ver todos los parámetros
        all_params = dict(st.query_params)
        print(f"[Clerk] Query params: {all_params}")

        clerk_token = st.query_params.get('__clerk_db_jwt')
        clerk_handshake = st.query_params.get('__clerk_handshake')

        # Intentar obtener user_id del handshake JWT (más confiable)
        user_data = None
        if clerk_handshake:
            print(f"[Clerk] Handshake found, decoding...")
            user_data = get_user_from_handshake(clerk_handshake)

        # Fallback al método anterior
        if not user_data and clerk_token:
            print(f"[Clerk] Token: {clerk_token[:30]}...")
            user_data = get_user_from_clerk_token(clerk_token)

        print(f"[Clerk] User data: {user_data.get('id') if user_data else None}")

        if user_data:
            email = ''
            if user_data.get('email_addresses') and len(user_data['email_addresses']) > 0:
                email = user_data['email_addresses'][0].get('email_address', '')

            st.session_state.clerk_authenticated = True
            st.session_state.clerk_user = {
                'id': user_data.get('id'),
                'email': email,
                'firstName': user_data.get('first_name', ''),
                'lastName': user_data.get('last_name', ''),
                'imageUrl': user_data.get('image_url', ''),
            }

            # Log de seguridad - Login exitoso
            log_security_event("LOGIN", f"Usuario: {email}", success=True)

            # Limpiar el token de la URL
            st.query_params.clear()
            st.rerun()
            return True

    except Exception as e:
        print(f"[Clerk] Error: {e}")
        log_security_event("LOGIN", f"Error: {str(e)}", success=False)

    # Textos según idioma
    texts = {
        "es": {
            "title": "FIFA Tools",
            "subtitle": "Herramientas para gestión FIFA",
            "login": "Iniciar Sesión",
            "signup": "Crear Cuenta",
            "or": "o",
            "secure": "Autenticación Segura",
            "secure_desc": "Usa Face ID, Touch ID o Windows Hello para acceder de forma segura."
        },
        "en": {
            "title": "FIFA Tools",
            "subtitle": "FIFA management tools",
            "login": "Sign In",
            "signup": "Create Account",
            "or": "or",
            "secure": "Secure Authentication",
            "secure_desc": "Use Face ID, Touch ID or Windows Hello to access securely."
        },
        "hi": {
            "title": "FIFA Tools",
            "subtitle": "FIFA प्रबंधन उपकरण",
            "login": "साइन इन करें",
            "signup": "खाता बनाएं",
            "or": "या",
            "secure": "सुरक्षित प्रमाणीकरण",
            "secure_desc": "सुरक्षित पहुंच के लिए Face ID, Touch ID या Windows Hello का उपयोग करें।"
        }
    }

    t = texts.get(lang, texts["es"])

    # URLs de Clerk
    clerk_signin_url = f"https://{CLERK_DOMAIN}/sign-in"
    clerk_signup_url = f"https://{CLERK_DOMAIN}/sign-up"

    # Mostrar pantalla de login
    st.markdown("""
        <style>
            [data-testid="stAppViewContainer"] {
                background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
            }
            [data-testid="stHeader"] {
                background: transparent !important;
            }
            .block-container {
                padding-top: 50px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Contenedor central
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(f"""
            <div style='background: white; padding: 40px; border-radius: 20px;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3); text-align: center;'>
                <div style='font-size: 48px; margin-bottom: 10px;'>🔑</div>
                <h1 style='color: #2c3e50; margin-bottom: 10px; font-size: 28px;'>{t['title']}</h1>
                <p style='color: #7f8c8d; margin-bottom: 30px;'>{t['subtitle']}</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Botón de login
        st.link_button(
            f"🔐 {t['login']}",
            clerk_signin_url,
            use_container_width=True,
            type="primary"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"""
            <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;
                        text-align: center; color: white;'>
                <strong>🔐 {t['secure']}</strong><br>
                <small>{t['secure_desc']}</small>
            </div>
        """, unsafe_allow_html=True)

    return False


def clerk_logout():
    """Cierra la sesión de Clerk"""
    user = st.session_state.get('clerk_user', {})
    email = user.get('email', 'unknown') if user else 'unknown'
    log_security_event("LOGOUT", f"Usuario: {email}", success=True)
    st.session_state.clerk_authenticated = False
    st.session_state.clerk_user = None
    st.rerun()


def show_user_info():
    """Muestra información del usuario y botón de logout"""
    if st.session_state.get('clerk_authenticated', False):
        user = st.session_state.get('clerk_user', {})

        col1, col2 = st.columns([3, 1])

        with col2:
            name = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
            if name:
                st.caption(f"👤 {name}")

            if st.button("🚪", help="Logout", key="logout_btn"):
                clerk_logout()


def is_clerk_enabled():
    """Verifica si Clerk está habilitado"""
    return USE_CLERK_AUTH and CLERK_PUBLISHABLE_KEY
