#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PAGINA LECTURA CORREOS
======================
Lectura de correos IMAP con filtros y extraccion FIFA
"""

import streamlit as st
import imaplib
import email
from email.header import decode_header
import ssl
import re
from datetime import datetime, timedelta
from io import BytesIO
import csv

# === TRADUCCIONES ===
TRANSLATIONS = {
    "es": {
        "title": "Lectura de Correos",
        "subtitle": "Lee correos de multiples cuentas IMAP",
        "tab_accounts": "Cuentas",
        "tab_search": "Busqueda",
        "tab_results": "Resultados",
        # Tab Cuentas
        "accounts_label": "Cuentas IMAP (email,password por linea)",
        "accounts_placeholder": "usuario1@icloud.com,password1\nusuario2@gmail.com,password2",
        "accounts_help": "Pega las cuentas en formato email,password (una por linea)",
        "btn_connect_all": "Conectar Todas",
        "btn_disconnect": "Desconectar Todas",
        "connecting": "Conectando cuentas...",
        "connected": "Conectado",
        "failed": "Error",
        "no_accounts": "No hay cuentas configuradas",
        "connection_status": "Estado de Conexiones",
        "accounts_connected": "cuentas conectadas",
        # Tab Busqueda
        "filter_subject": "Asunto contiene",
        "filter_sender": "Remitente contiene",
        "filter_date_from": "Fecha desde",
        "filter_status": "Estado",
        "filter_limit": "Limite por cuenta",
        "status_all": "Todos",
        "status_unread": "No leidos",
        "status_read": "Leidos",
        "btn_search": "Buscar Correos",
        "searching": "Buscando correos...",
        "search_account": "Buscando en",
        "no_connections": "No hay cuentas conectadas. Ve a la pestana Cuentas primero.",
        # Tab Resultados
        "no_results": "No hay resultados. Realiza una busqueda primero.",
        "results_count": "correos encontrados",
        "col_account": "Cuenta",
        "col_from": "De",
        "col_subject": "Asunto",
        "col_date": "Fecha",
        "col_status": "Estado",
        "btn_mark_read": "Marcar como Leido",
        "btn_export_csv": "Exportar CSV",
        "marking": "Marcando como leido...",
        "marked_success": "Marcado como leido",
        "view_details": "Ver detalles",
        "email_body": "Contenido",
        # FIFA
        "fifa_section": "Extraccion FIFA World Cup",
        "btn_extract_fifa": "Extraer Datos FIFA",
        "extracting_fifa": "Extrayendo datos FIFA...",
        "fifa_no_data": "No se encontraron datos FIFA en los correos",
        "fifa_found": "entradas FIFA encontradas",
        "btn_export_excel": "Exportar Excel",
        "fifa_col_ticket": "Numero Ticket",
        "fifa_col_application": "Numero Solicitud",
        "fifa_col_applicant": "Nombre Solicitante",
        "fifa_col_email": "Email",
        # Errores
        "error_connect": "Error al conectar",
        "error_search": "Error al buscar",
        "error_generic": "Error",
    },
    "en": {
        "title": "Email Reader",
        "subtitle": "Read emails from multiple IMAP accounts",
        "tab_accounts": "Accounts",
        "tab_search": "Search",
        "tab_results": "Results",
        # Tab Accounts
        "accounts_label": "IMAP Accounts (email,password per line)",
        "accounts_placeholder": "user1@icloud.com,password1\nuser2@gmail.com,password2",
        "accounts_help": "Paste accounts in email,password format (one per line)",
        "btn_connect_all": "Connect All",
        "btn_disconnect": "Disconnect All",
        "connecting": "Connecting accounts...",
        "connected": "Connected",
        "failed": "Failed",
        "no_accounts": "No accounts configured",
        "connection_status": "Connection Status",
        "accounts_connected": "accounts connected",
        # Tab Search
        "filter_subject": "Subject contains",
        "filter_sender": "Sender contains",
        "filter_date_from": "Date from",
        "filter_status": "Status",
        "filter_limit": "Limit per account",
        "status_all": "All",
        "status_unread": "Unread",
        "status_read": "Read",
        "btn_search": "Search Emails",
        "searching": "Searching emails...",
        "search_account": "Searching in",
        "no_connections": "No accounts connected. Go to Accounts tab first.",
        # Tab Results
        "no_results": "No results. Perform a search first.",
        "results_count": "emails found",
        "col_account": "Account",
        "col_from": "From",
        "col_subject": "Subject",
        "col_date": "Date",
        "col_status": "Status",
        "btn_mark_read": "Mark as Read",
        "btn_export_csv": "Export CSV",
        "marking": "Marking as read...",
        "marked_success": "Marked as read",
        "view_details": "View details",
        "email_body": "Content",
        # FIFA
        "fifa_section": "FIFA World Cup Extraction",
        "btn_extract_fifa": "Extract FIFA Data",
        "extracting_fifa": "Extracting FIFA data...",
        "fifa_no_data": "No FIFA data found in emails",
        "fifa_found": "FIFA entries found",
        "btn_export_excel": "Export Excel",
        "fifa_col_ticket": "Ticket Number",
        "fifa_col_application": "Application Number",
        "fifa_col_applicant": "Applicant Name",
        "fifa_col_email": "Email",
        # Errors
        "error_connect": "Connection error",
        "error_search": "Search error",
        "error_generic": "Error",
    },
    "hi": {
        "title": "ईमेल रीडर",
        "subtitle": "कई IMAP खातों से ईमेल पढ़ें",
        "tab_accounts": "खाते",
        "tab_search": "खोज",
        "tab_results": "परिणाम",
        # Tab Accounts
        "accounts_label": "IMAP खाते (प्रति पंक्ति email,password)",
        "accounts_placeholder": "user1@icloud.com,password1\nuser2@gmail.com,password2",
        "accounts_help": "email,password प्रारूप में खाते पेस्ट करें",
        "btn_connect_all": "सभी कनेक्ट करें",
        "btn_disconnect": "सभी डिस्कनेक्ट करें",
        "connecting": "खाते कनेक्ट हो रहे हैं...",
        "connected": "कनेक्टेड",
        "failed": "विफल",
        "no_accounts": "कोई खाता कॉन्फ़िगर नहीं है",
        "connection_status": "कनेक्शन स्थिति",
        "accounts_connected": "खाते कनेक्ट हैं",
        # Tab Search
        "filter_subject": "विषय में शामिल है",
        "filter_sender": "प्रेषक में शामिल है",
        "filter_date_from": "तारीख से",
        "filter_status": "स्थिति",
        "filter_limit": "प्रति खाता सीमा",
        "status_all": "सभी",
        "status_unread": "अपठित",
        "status_read": "पठित",
        "btn_search": "ईमेल खोजें",
        "searching": "ईमेल खोज रहे हैं...",
        "search_account": "खोज रहे हैं",
        "no_connections": "कोई खाता कनेक्ट नहीं है। पहले खाते टैब पर जाएं।",
        # Tab Results
        "no_results": "कोई परिणाम नहीं। पहले खोज करें।",
        "results_count": "ईमेल मिले",
        "col_account": "खाता",
        "col_from": "से",
        "col_subject": "विषय",
        "col_date": "तारीख",
        "col_status": "स्थिति",
        "btn_mark_read": "पठित के रूप में चिह्नित करें",
        "btn_export_csv": "CSV निर्यात करें",
        "marking": "पठित के रूप में चिह्नित कर रहे हैं...",
        "marked_success": "पठित के रूप में चिह्नित",
        "view_details": "विवरण देखें",
        "email_body": "सामग्री",
        # FIFA
        "fifa_section": "FIFA विश्व कप निष्कर्षण",
        "btn_extract_fifa": "FIFA डेटा निकालें",
        "extracting_fifa": "FIFA डेटा निकाल रहे हैं...",
        "fifa_no_data": "ईमेल में कोई FIFA डेटा नहीं मिला",
        "fifa_found": "FIFA प्रविष्टियां मिलीं",
        "btn_export_excel": "Excel निर्यात करें",
        "fifa_col_ticket": "टिकट नंबर",
        "fifa_col_application": "आवेदन संख्या",
        "fifa_col_applicant": "आवेदक का नाम",
        "fifa_col_email": "ईमेल",
        # Errors
        "error_connect": "कनेक्शन त्रुटि",
        "error_search": "खोज त्रुटि",
        "error_generic": "त्रुटि",
    }
}

# === IMAP PRESETS ===
IMAP_PRESETS = {
    "icloud.com": ("imap.mail.me.com", 993),
    "me.com": ("imap.mail.me.com", 993),
    "mac.com": ("imap.mail.me.com", 993),
    "gmail.com": ("imap.gmail.com", 993),
    "outlook.com": ("outlook.office365.com", 993),
    "hotmail.com": ("outlook.office365.com", 993),
    "live.com": ("outlook.office365.com", 993),
    "yahoo.com": ("imap.mail.yahoo.com", 993),
}


def t(key):
    """Obtiene la traduccion para la clave dada"""
    lang = st.session_state.get("language", "es")
    return TRANSLATIONS.get(lang, TRANSLATIONS["es"]).get(key, key)


def infer_imap_server(email_addr):
    """Infiere el servidor IMAP basado en el dominio del email"""
    domain = email_addr.split("@")[-1].lower()
    return IMAP_PRESETS.get(domain, (f"imap.{domain}", 993))


def get_ssl_context():
    """Crea un contexto SSL para conexiones IMAP"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def decode_header_text(header_value):
    """Decodifica un header de email"""
    if not header_value:
        return ""

    decoded_parts = []
    try:
        parts = decode_header(header_value)
        for content, charset in parts:
            if isinstance(content, bytes):
                charset = charset or 'utf-8'
                try:
                    decoded_parts.append(content.decode(charset, errors='replace'))
                except:
                    decoded_parts.append(content.decode('utf-8', errors='replace'))
            else:
                decoded_parts.append(str(content))
    except:
        return str(header_value)

    return ''.join(decoded_parts)


def extract_text_content(msg):
    """Extrae el contenido de texto de un mensaje"""
    text_content = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    payload = part.get_payload(decode=True)
                    if payload:
                        text_content += payload.decode(charset, errors='replace')
                except:
                    pass
    else:
        content_type = msg.get_content_type()
        if content_type == "text/plain":
            try:
                charset = msg.get_content_charset() or 'utf-8'
                payload = msg.get_payload(decode=True)
                if payload:
                    text_content = payload.decode(charset, errors='replace')
            except:
                pass

    return text_content


def extract_html_content(msg):
    """Extrae el contenido HTML de un mensaje"""
    html_content = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/html":
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    payload = part.get_payload(decode=True)
                    if payload:
                        html_content += payload.decode(charset, errors='replace')
                except:
                    pass
    else:
        content_type = msg.get_content_type()
        if content_type == "text/html":
            try:
                charset = msg.get_content_charset() or 'utf-8'
                payload = msg.get_payload(decode=True)
                if payload:
                    html_content = payload.decode(charset, errors='replace')
            except:
                pass

    return html_content


# === FIFA EXTRACTION FUNCTIONS ===
def extract_fifa_tickets(text):
    """Extrae numeros de ticket FIFA del texto"""
    # Patron para numeros de ticket FIFA (ej: 26-1234567-1234567)
    pattern = r'\b(26-\d{7}-\d{7})\b'
    matches = re.findall(pattern, text)
    return list(set(matches))


def extract_fifa_application_number(text):
    """Extrae numero de solicitud FIFA"""
    # Patron para Application Number
    patterns = [
        r'Application\s*(?:Number|No\.?|#)?\s*:?\s*(\d{8,12})',
        r'Solicitud\s*(?:Numero|No\.?|#)?\s*:?\s*(\d{8,12})',
        r'Reference\s*(?:Number|No\.?|#)?\s*:?\s*(\d{8,12})',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


def extract_fifa_applicant_name(text):
    """Extrae nombre del solicitante FIFA"""
    patterns = [
        r'(?:Dear|Estimado/a|Hi|Hello)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        r'Applicant\s*(?:Name)?\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        r'Name\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return ""


class ImapManager:
    """Gestor de conexiones IMAP"""

    def __init__(self):
        self.connections = {}  # email -> imaplib.IMAP4_SSL
        self.status = {}  # email -> bool (connected)
        self.errors = {}  # email -> str (error message)

    def connect(self, email_addr, password):
        """Conecta a una cuenta IMAP"""
        try:
            server, port = infer_imap_server(email_addr)
            ctx = get_ssl_context()

            imap = imaplib.IMAP4_SSL(server, port, ssl_context=ctx)
            imap.login(email_addr, password)
            imap.select("INBOX")

            self.connections[email_addr] = imap
            self.status[email_addr] = True
            self.errors[email_addr] = ""
            return True

        except Exception as e:
            self.status[email_addr] = False
            self.errors[email_addr] = str(e)
            return False

    def disconnect_all(self):
        """Desconecta todas las cuentas"""
        for email_addr, imap in self.connections.items():
            try:
                imap.logout()
            except:
                pass
        self.connections.clear()
        self.status.clear()
        self.errors.clear()

    def search(self, email_addr, subject_filter="", sender_filter="",
               date_from=None, status_filter="all", limit=50):
        """Busca correos en una cuenta"""
        results = []

        if email_addr not in self.connections:
            return results

        try:
            imap = self.connections[email_addr]
            imap.select("INBOX")

            # Construir criterios de busqueda
            criteria = []

            if status_filter == "unread":
                criteria.append("UNSEEN")
            elif status_filter == "read":
                criteria.append("SEEN")

            if date_from:
                date_str = date_from.strftime("%d-%b-%Y")
                criteria.append(f'SINCE {date_str}')

            if sender_filter:
                criteria.append(f'FROM "{sender_filter}"')

            if subject_filter:
                criteria.append(f'SUBJECT "{subject_filter}"')

            search_criteria = " ".join(criteria) if criteria else "ALL"

            # Buscar
            status, data = imap.search(None, search_criteria)

            if status != "OK":
                return results

            email_ids = data[0].split()

            # Limitar resultados
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids

            for eid in reversed(email_ids):  # Mas recientes primero
                try:
                    status, msg_data = imap.fetch(eid, "(RFC822 FLAGS)")

                    if status != "OK":
                        continue

                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    # Obtener flags para determinar si esta leido
                    flags_data = msg_data[0][0].decode() if msg_data[0][0] else ""
                    is_read = "\\Seen" in flags_data

                    # Extraer informacion
                    subject = decode_header_text(msg.get("Subject", ""))
                    from_addr = decode_header_text(msg.get("From", ""))
                    date_str = msg.get("Date", "")

                    # Parsear fecha
                    try:
                        date_parsed = email.utils.parsedate_to_datetime(date_str)
                        date_formatted = date_parsed.strftime("%Y-%m-%d %H:%M")
                    except:
                        date_formatted = date_str[:20] if date_str else ""

                    # Extraer contenido
                    text_content = extract_text_content(msg)
                    html_content = extract_html_content(msg)

                    results.append({
                        "account": email_addr,
                        "email_id": eid.decode() if isinstance(eid, bytes) else str(eid),
                        "from": from_addr,
                        "subject": subject,
                        "date": date_formatted,
                        "is_read": is_read,
                        "text_content": text_content,
                        "html_content": html_content,
                    })

                except Exception as e:
                    continue

        except Exception as e:
            st.error(f"{t('error_search')}: {email_addr} - {str(e)}")

        return results

    def mark_seen(self, email_addr, email_id):
        """Marca un correo como leido"""
        if email_addr not in self.connections:
            return False

        try:
            imap = self.connections[email_addr]
            imap.select("INBOX")
            imap.store(email_id.encode() if isinstance(email_id, str) else email_id,
                      '+FLAGS', '\\Seen')
            return True
        except:
            return False


def init_session_state():
    """Inicializa el session state"""
    if "lectura_imap" not in st.session_state:
        st.session_state.lectura_imap = ImapManager()

    if "lectura_accounts" not in st.session_state:
        st.session_state.lectura_accounts = []

    if "lectura_results" not in st.session_state:
        st.session_state.lectura_results = []

    if "lectura_fifa_data" not in st.session_state:
        st.session_state.lectura_fifa_data = []


def render():
    """Renderiza la pagina de lectura de correos"""

    init_session_state()

    # === HEADER ===
    st.title(f"📧 {t('title')}")
    st.markdown(f"{t('subtitle')}")
    st.markdown("---")

    # === TABS ===
    tab1, tab2, tab3 = st.tabs([
        f"👥 {t('tab_accounts')}",
        f"🔍 {t('tab_search')}",
        f"📋 {t('tab_results')}"
    ])

    # === TAB 1: CUENTAS ===
    with tab1:
        render_accounts_tab()

    # === TAB 2: BUSQUEDA ===
    with tab2:
        render_search_tab()

    # === TAB 3: RESULTADOS ===
    with tab3:
        render_results_tab()


def render_accounts_tab():
    """Renderiza la pestana de cuentas"""

    imap_manager = st.session_state.lectura_imap

    # Area de texto para cuentas
    accounts_text = st.text_area(
        t("accounts_label"),
        placeholder=t("accounts_placeholder"),
        help=t("accounts_help"),
        height=150,
        key="lectura_accounts_text"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(f"🔗 {t('btn_connect_all')}", type="primary", use_container_width=True):
            if accounts_text.strip():
                # Parsear cuentas
                accounts = []
                for line in accounts_text.strip().split("\n"):
                    line = line.strip()
                    if "," in line:
                        parts = line.split(",", 1)
                        if len(parts) == 2:
                            email_addr = parts[0].strip()
                            password = parts[1].strip()
                            if email_addr and password:
                                accounts.append((email_addr, password))

                if accounts:
                    st.session_state.lectura_accounts = accounts

                    # Conectar todas
                    progress = st.progress(0)
                    status_container = st.empty()

                    for i, (email_addr, password) in enumerate(accounts):
                        status_container.info(f"🔄 {t('connecting')} {email_addr}")
                        imap_manager.connect(email_addr, password)
                        progress.progress((i + 1) / len(accounts))

                    status_container.empty()
                    progress.empty()
                    st.rerun()

    with col2:
        if st.button(f"🔌 {t('btn_disconnect')}", use_container_width=True):
            imap_manager.disconnect_all()
            st.session_state.lectura_results = []
            st.session_state.lectura_fifa_data = []
            st.rerun()

    # Mostrar estado de conexiones
    st.markdown("---")
    st.subheader(f"📊 {t('connection_status')}")

    if imap_manager.status:
        connected_count = sum(1 for v in imap_manager.status.values() if v)
        st.info(f"✅ {connected_count} {t('accounts_connected')}")

        for email_addr, is_connected in imap_manager.status.items():
            if is_connected:
                st.success(f"✅ {email_addr} - {t('connected')}")
            else:
                error_msg = imap_manager.errors.get(email_addr, "")
                st.error(f"❌ {email_addr} - {t('failed')}: {error_msg}")
    else:
        st.info(f"ℹ️ {t('no_accounts')}")


def render_search_tab():
    """Renderiza la pestana de busqueda"""

    imap_manager = st.session_state.lectura_imap

    # Verificar conexiones
    connected_accounts = [e for e, s in imap_manager.status.items() if s]

    if not connected_accounts:
        st.warning(f"⚠️ {t('no_connections')}")
        return

    st.info(f"✅ {len(connected_accounts)} {t('accounts_connected')}")

    # Filtros
    col1, col2 = st.columns(2)

    with col1:
        subject_filter = st.text_input(
            f"📝 {t('filter_subject')}",
            key="lectura_filter_subject"
        )

        date_from = st.date_input(
            f"📅 {t('filter_date_from')}",
            value=datetime.now() - timedelta(days=7),
            key="lectura_filter_date"
        )

    with col2:
        sender_filter = st.text_input(
            f"👤 {t('filter_sender')}",
            key="lectura_filter_sender"
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

    limit = st.slider(
        f"🔢 {t('filter_limit')}",
        min_value=10,
        max_value=200,
        value=50,
        step=10,
        key="lectura_filter_limit"
    )

    # Boton buscar
    if st.button(f"🔍 {t('btn_search')}", type="primary", use_container_width=True):
        all_results = []

        progress = st.progress(0)
        status_container = st.empty()

        for i, email_addr in enumerate(connected_accounts):
            status_container.info(f"🔄 {t('search_account')} {email_addr}...")

            results = imap_manager.search(
                email_addr,
                subject_filter=subject_filter,
                sender_filter=sender_filter,
                date_from=date_from,
                status_filter=status_filter,
                limit=limit
            )

            all_results.extend(results)
            progress.progress((i + 1) / len(connected_accounts))

        status_container.empty()
        progress.empty()

        # Ordenar por fecha (mas recientes primero)
        all_results.sort(key=lambda x: x.get("date", ""), reverse=True)

        st.session_state.lectura_results = all_results
        st.success(f"✅ {len(all_results)} {t('results_count')}")


def render_results_tab():
    """Renderiza la pestana de resultados"""

    results = st.session_state.lectura_results
    imap_manager = st.session_state.lectura_imap

    if not results:
        st.info(f"ℹ️ {t('no_results')}")
        return

    st.success(f"📧 {len(results)} {t('results_count')}")

    # Botones de accion
    col1, col2 = st.columns(2)

    with col1:
        if st.button(f"📥 {t('btn_export_csv')}", use_container_width=True):
            # Crear CSV
            output = BytesIO()

            # Escribir con csv writer
            import io
            text_output = io.StringIO()
            writer = csv.writer(text_output)
            writer.writerow([t("col_account"), t("col_from"), t("col_subject"), t("col_date"), t("col_status")])

            for r in results:
                writer.writerow([
                    r.get("account", ""),
                    r.get("from", ""),
                    r.get("subject", ""),
                    r.get("date", ""),
                    "Read" if r.get("is_read") else "Unread"
                ])

            csv_content = text_output.getvalue()

            st.download_button(
                label="💾 Download CSV",
                data=csv_content,
                file_name=f"emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    with col2:
        pass  # Espacio reservado

    st.markdown("---")

    # Mostrar resultados
    for i, r in enumerate(results):
        status_icon = "📖" if r.get("is_read") else "📩"

        with st.expander(f"{status_icon} {r.get('subject', 'Sin asunto')[:60]} - {r.get('date', '')}"):
            st.markdown(f"**{t('col_account')}:** {r.get('account', '')}")
            st.markdown(f"**{t('col_from')}:** {r.get('from', '')}")
            st.markdown(f"**{t('col_date')}:** {r.get('date', '')}")
            st.markdown(f"**{t('col_status')}:** {'📖 Read' if r.get('is_read') else '📩 Unread'}")

            st.markdown("---")
            st.markdown(f"**{t('email_body')}:**")

            text_content = r.get("text_content", "")
            if text_content:
                st.text_area("", value=text_content, height=200, key=f"content_{i}", disabled=True)
            else:
                html_content = r.get("html_content", "")
                if html_content:
                    # Mostrar version simplificada del HTML
                    clean_text = re.sub(r'<[^>]+>', ' ', html_content)
                    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                    st.text_area("", value=clean_text[:2000], height=200, key=f"content_{i}", disabled=True)
                else:
                    st.info("No content available")

            # Boton marcar como leido
            if not r.get("is_read"):
                if st.button(f"✅ {t('btn_mark_read')}", key=f"mark_{i}"):
                    with st.spinner(t("marking")):
                        success = imap_manager.mark_seen(r.get("account"), r.get("email_id"))
                        if success:
                            st.session_state.lectura_results[i]["is_read"] = True
                            st.success(t("marked_success"))
                            st.rerun()

    # === SECCION FIFA ===
    st.markdown("---")
    st.subheader(f"⚽ {t('fifa_section')}")

    if st.button(f"🎫 {t('btn_extract_fifa')}", type="primary", use_container_width=True):
        fifa_data = []

        with st.spinner(t("extracting_fifa")):
            for r in results:
                text = r.get("text_content", "") + " " + r.get("html_content", "")

                # Extraer tickets
                tickets = extract_fifa_tickets(text)

                if tickets:
                    app_number = extract_fifa_application_number(text)
                    applicant = extract_fifa_applicant_name(text)

                    for ticket in tickets:
                        fifa_data.append({
                            t("fifa_col_ticket"): ticket,
                            t("fifa_col_application"): app_number,
                            t("fifa_col_applicant"): applicant,
                            t("fifa_col_email"): r.get("account", "")
                        })

        st.session_state.lectura_fifa_data = fifa_data

        if fifa_data:
            st.success(f"✅ {len(fifa_data)} {t('fifa_found')}")
        else:
            st.warning(t("fifa_no_data"))

    # Mostrar datos FIFA
    fifa_data = st.session_state.lectura_fifa_data

    if fifa_data:
        import pandas as pd
        df = pd.DataFrame(fifa_data)
        st.dataframe(df, use_container_width=True)

        # Boton exportar Excel
        try:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='FIFA Data')

            st.download_button(
                label=f"📊 {t('btn_export_excel')}",
                data=output.getvalue(),
                file_name=f"fifa_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except ImportError:
            st.warning("openpyxl not installed. Install it with: pip install openpyxl")
