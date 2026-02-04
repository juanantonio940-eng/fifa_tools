#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
APLICACION PRINCIPAL - MENU LATERAL
====================================
FIFA OTP + UEFA OTP + Mundial Comprobantes
Con sistema de permisos por usuario
"""

import streamlit as st
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# Configuración
SKIP_AUTH = os.getenv('SKIP_AUTH', 'false').lower() == 'true'
ADMIN_PASSWORD = "74674764Cc$"
PERMISOS_FILE = Path(__file__).parent / 'permisos_usuarios.json'

# Opciones disponibles
TODAS_LAS_OPCIONES = ["🔑 FIFA OTP", "🔑 UEFA OTP", "📋 Mundial Comprobantes", "📤 Comprobantes Anytickets"]

st.set_page_config(
    page_title="FIFA Tools",
    page_icon="⚽",
    layout="wide"
)

# === FUNCIONES DE PERMISOS ===
def cargar_permisos():
    """Carga los permisos de usuarios desde el archivo JSON"""
    if PERMISOS_FILE.exists():
        try:
            with open(PERMISOS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def guardar_permisos(permisos):
    """Guarda los permisos de usuarios en el archivo JSON"""
    with open(PERMISOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(permisos, f, ensure_ascii=False, indent=2)


def obtener_permisos_usuario(email):
    """Obtiene los permisos de un usuario específico"""
    if not email:
        return TODAS_LAS_OPCIONES  # Sin auth, todas las opciones

    permisos = cargar_permisos()
    email_lower = email.lower().strip()

    # Si el usuario no está en la lista, tiene todas las opciones por defecto
    if email_lower not in permisos:
        return TODAS_LAS_OPCIONES

    return permisos[email_lower].get('opciones', TODAS_LAS_OPCIONES)


def obtener_email_usuario():
    """Obtiene el email del usuario autenticado"""
    user = st.session_state.get('clerk_user', {})
    return user.get('email', '').lower().strip() if user else ''


# Importar autenticación
from clerk_auth import clerk_login, clerk_logout, is_clerk_enabled

# === VERIFICAR AUTENTICACIÓN ===
if "language" not in st.session_state:
    st.session_state.language = "es"

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if "show_config" not in st.session_state:
    st.session_state.show_config = False

if "edit_email_target" not in st.session_state:
    st.session_state.edit_email_target = ""

# Si hay un email para editar, limpiar las keys de los widgets para forzar reinicio
if st.session_state.edit_email_target:
    # Eliminar keys de widgets para que se reinicialicen con nuevos valores
    keys_to_clear = ["nuevo_usuario_email", "check_fifa", "check_uefa", "check_mundial", "check_anytickets"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

if not SKIP_AUTH and is_clerk_enabled():
    if not clerk_login(st.session_state.language):
        st.stop()
elif SKIP_AUTH:
    st.sidebar.warning("⚠️ Modo Debug: Auth desactivada")

# === MENU LATERAL ===
st.sidebar.title("⚽ FIFA Tools")
st.sidebar.markdown("---")

# Obtener email del usuario actual
email_usuario = obtener_email_usuario()

# Obtener opciones permitidas para este usuario
opciones_permitidas = obtener_permisos_usuario(email_usuario)

# Filtrar solo las opciones que el usuario tiene permitidas
opciones_menu = [op for op in TODAS_LAS_OPCIONES if op in opciones_permitidas]

# Si no tiene ninguna opción permitida, mostrar mensaje
if not opciones_menu:
    st.sidebar.warning("⚠️ No tienes acceso a ninguna herramienta")
    pagina = None
else:
    # Selector de página (solo opciones permitidas)
    pagina = st.sidebar.radio(
        "Selecciona herramienta:",
        opciones_menu,
        label_visibility="collapsed"
    )

st.sidebar.markdown("---")

# Selector de idioma
lang_names = {"es": "Español", "en": "English", "hi": "हिन्दी"}
lang_options = ["es", "en", "hi"]

language = st.sidebar.selectbox(
    "🌐 Idioma",
    options=lang_options,
    format_func=lambda x: lang_names.get(x, x),
    index=lang_options.index(st.session_state.language) if st.session_state.language in lang_options else 0
)

if language != st.session_state.language:
    st.session_state.language = language
    st.rerun()

st.sidebar.markdown("---")

# Botón de Configuración (Admin)
if st.sidebar.button("⚙️ Configuración", use_container_width=True):
    st.session_state.show_config = True
    st.rerun()

st.sidebar.markdown("---")

# Logout
if st.session_state.get('clerk_authenticated', False):
    user = st.session_state.get('clerk_user', {})
    name = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
    email = user.get('email', '')
    st.sidebar.markdown(f"👤 **{name or email}**")

    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        clerk_logout()

# === PÁGINA DE CONFIGURACIÓN (ADMIN) ===
if st.session_state.show_config:
    st.title("⚙️ Configuración de Permisos")

    # Si no está autenticado como admin, pedir contraseña
    if not st.session_state.admin_authenticated:
        st.warning("🔒 Esta sección requiere contraseña de administrador")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            password = st.text_input("Contraseña:", type="password", key="admin_password_input")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🔓 Acceder", type="primary", use_container_width=True):
                    if password == ADMIN_PASSWORD:
                        st.session_state.admin_authenticated = True
                        st.rerun()
                    else:
                        st.error("❌ Contraseña incorrecta")

            with col_btn2:
                if st.button("↩️ Volver", use_container_width=True):
                    st.session_state.show_config = False
                    st.rerun()

    else:
        # Admin autenticado - mostrar configuración
        st.success("✅ Acceso de administrador")

        # Botón para cerrar sesión de admin
        col1, col2, col3 = st.columns([2, 1, 1])
        with col3:
            if st.button("🔒 Cerrar Admin", use_container_width=True):
                st.session_state.admin_authenticated = False
                st.session_state.show_config = False
                st.rerun()
        with col2:
            if st.button("↩️ Volver", use_container_width=True):
                st.session_state.show_config = False
                st.rerun()

        st.markdown("---")

        # Cargar permisos actuales
        permisos = cargar_permisos()

        # === AGREGAR NUEVO USUARIO ===
        st.subheader("➕ Agregar/Editar Usuario")

        col1, col2 = st.columns([2, 1])

        with col1:
            nuevo_email = st.text_input(
                "Email del usuario:",
                value=st.session_state.edit_email_target,
                placeholder="usuario@ejemplo.com",
                key="nuevo_usuario_email"
            ).lower().strip()
            # Limpiar el target después de usarlo
            if st.session_state.edit_email_target:
                st.session_state.edit_email_target = ""

        # Mostrar checkboxes para las opciones
        st.write("**Opciones permitidas:**")

        # Si el email ya existe, cargar sus permisos actuales
        permisos_actuales = []
        if nuevo_email and nuevo_email in permisos:
            permisos_actuales = permisos[nuevo_email].get('opciones', [])

        col1, col2 = st.columns(2)

        with col1:
            fifa_otp = st.checkbox(
                "🔑 FIFA OTP",
                value="🔑 FIFA OTP" in permisos_actuales if permisos_actuales else True,
                key="check_fifa"
            )
            mundial = st.checkbox(
                "📋 Mundial Comprobantes",
                value="📋 Mundial Comprobantes" in permisos_actuales if permisos_actuales else True,
                key="check_mundial"
            )

        with col2:
            uefa_otp = st.checkbox(
                "🔑 UEFA OTP",
                value="🔑 UEFA OTP" in permisos_actuales if permisos_actuales else True,
                key="check_uefa"
            )
            anytickets = st.checkbox(
                "📤 Comprobantes Anytickets",
                value="📤 Comprobantes Anytickets" in permisos_actuales if permisos_actuales else True,
                key="check_anytickets"
            )

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("💾 Guardar Usuario", type="primary", use_container_width=True):
                if nuevo_email:
                    opciones_seleccionadas = []
                    if fifa_otp:
                        opciones_seleccionadas.append("🔑 FIFA OTP")
                    if uefa_otp:
                        opciones_seleccionadas.append("🔑 UEFA OTP")
                    if mundial:
                        opciones_seleccionadas.append("📋 Mundial Comprobantes")
                    if anytickets:
                        opciones_seleccionadas.append("📤 Comprobantes Anytickets")

                    permisos[nuevo_email] = {
                        'opciones': opciones_seleccionadas
                    }
                    guardar_permisos(permisos)
                    st.success(f"✅ Permisos guardados para {nuevo_email}")
                    st.rerun()
                else:
                    st.warning("⚠️ Ingresa un email válido")

        with col2:
            if st.button("🗑️ Eliminar Usuario", use_container_width=True):
                if nuevo_email and nuevo_email in permisos:
                    del permisos[nuevo_email]
                    guardar_permisos(permisos)
                    st.success(f"✅ Usuario {nuevo_email} eliminado")
                    st.rerun()
                elif nuevo_email:
                    st.warning("⚠️ Usuario no encontrado")
                else:
                    st.warning("⚠️ Ingresa un email")

        st.markdown("---")

        # === LISTA DE USUARIOS CONFIGURADOS ===
        st.subheader("📋 Usuarios Configurados")

        if permisos:
            # Crear tabla de usuarios
            for email_user, datos in permisos.items():
                opciones_user = datos.get('opciones', [])

                with st.expander(f"👤 {email_user}", expanded=False):
                    st.write("**Permisos:**")

                    # Mostrar TODAS las opciones con su estado
                    for op in TODAS_LAS_OPCIONES:
                        if op in opciones_user:
                            st.write(f"  ✅ {op}")
                        else:
                            st.write(f"  ❌ {op}")

                    # Botón para editar (carga el email en el campo de arriba)
                    if st.button(f"✏️ Editar {email_user}", key=f"edit_{email_user}"):
                        st.session_state.edit_email_target = email_user
                        st.rerun()
        else:
            st.info("ℹ️ No hay usuarios configurados. Todos los usuarios tienen acceso completo por defecto.")

        st.markdown("---")

        # === INFORMACIÓN ===
        with st.expander("ℹ️ Información"):
            st.markdown("""
            ### Cómo funciona el sistema de permisos

            1. **Usuarios no configurados:** Tienen acceso a TODAS las opciones por defecto.
            2. **Usuarios configurados:** Solo ven las opciones que tengan marcadas.
            3. **Para restringir acceso:** Agrega el usuario y desmarca las opciones que NO debe ver.
            4. **Para dar acceso total:** Elimina el usuario de la lista (volverá al comportamiento por defecto).

            ### Opciones disponibles
            - 🔑 **FIFA OTP:** Consulta de códigos OTP de FIFA
            - 🔑 **UEFA OTP:** Consulta de códigos OTP de UEFA
            - 📋 **Mundial Comprobantes:** Verificación de comprobantes del Mundial
            - 📤 **Comprobantes Anytickets:** Subir comprobantes a Anytickets
            """)

# === CONTENIDO SEGÚN PÁGINA ===
elif pagina == "🔑 FIFA OTP":
    # Importar y ejecutar página OTP FIFA
    from modules import otp_page
    otp_page.render()

elif pagina == "🔑 UEFA OTP":
    # Importar y ejecutar página OTP UEFA
    from modules import uefa_otp_page
    uefa_otp_page.render()

elif pagina == "📋 Mundial Comprobantes":
    # Importar y ejecutar página Comprobantes
    from modules import comprobantes_page
    comprobantes_page.render()

elif pagina == "📤 Comprobantes Anytickets":
    # Importar y ejecutar página Anytickets
    from modules import anytickets_page
    anytickets_page.render()

elif pagina is None and not st.session_state.show_config:
    # Usuario sin permisos
    st.title("⚠️ Acceso Restringido")
    st.warning("No tienes acceso a ninguna herramienta. Contacta al administrador.")
