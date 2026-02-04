# OTP Streamlit - FIFA Tools

Aplicación web Streamlit para consulta de códigos OTP y verificación de comprobantes del Mundial FIFA 2026.

## Descripción

Esta aplicación proporciona cuatro herramientas principales:
1. **FIFA OTP** - Consulta de códigos OTP de FIFA desde correos de iCloud
2. **UEFA OTP** - Consulta de códigos OTP de UEFA desde correos de iCloud
3. **Mundial Comprobantes** - Verificación de comprobantes de tickets del Mundial FIFA 2026
4. **Comprobantes Anytickets** - Subir comprobantes de transferencia a Anytickets

## Estructura del Proyecto

```
Otp_streamlit/
├── app.py                      # Aplicación principal con menú lateral
├── otp_consultor_web.py        # Versión standalone (FIFA + UEFA)
├── clerk_auth.py               # Autenticación con Clerk
├── permisos_usuarios.json      # Permisos de usuarios (se crea automáticamente)
├── .env                        # Variables de entorno
├── .gitignore                  # Archivos ignorados por Git
├── .dockerignore               # Archivos ignorados por Docker
├── requirements.txt            # Dependencias
├── iniciar_otp_consultor.bat   # Script para iniciar la app
│
├── modules/
│   ├── __init__.py
│   ├── otp_page.py             # Módulo FIFA OTP
│   ├── uefa_otp_page.py        # Módulo UEFA OTP
│   ├── comprobantes_page.py    # Módulo Mundial Comprobantes
│   ├── anytickets_page.py      # Módulo Comprobantes Anytickets
│   └── anytickets_client.py    # Cliente API Anytickets
│
├── docker/                     # Configuración Docker para EasyPanel
│   ├── Dockerfile              # Imagen Docker
│   ├── docker-compose.yml      # Compose para desarrollo
│   ├── requirements.txt        # Dependencias con versiones
│   ├── .env.example            # Ejemplo de variables de entorno
│   └── DEPLOY.md               # Instrucciones de despliegue
│
├── dist/                       # Carpeta de distribución (copia de producción)
│   ├── app.py
│   ├── clerk_auth.py
│   └── modules/
│       ├── __init__.py
│       ├── otp_page.py
│       ├── uefa_otp_page.py
│       ├── comprobantes_page.py
│       ├── anytickets_page.py
│       └── anytickets_client.py
│
├── datos_usuarios/             # Datos por usuario (se crea automáticamente)
│   └── <email_usuario>/
│       ├── config.ini
│       ├── cache_resultados.json
│       ├── imagenes/
│       ├── tabla/
│       └── reportes/
│
└── logs/
    └── security.log
```

## Webhooks Utilizados

| Servicio | URL del Webhook |
|----------|-----------------|
| FIFA OTP | `https://fastapi-fastapi-webhook.6nzk5m.easypanel.host/webhook` |
| UEFA OTP | `https://fastapi-fastapi-uefa.6nzk5m.easypanel.host/webhook` |

### Estructura de Peticiones/Respuestas

**FIFA OTP:**
```json
// Request
POST /webhook
{"email": "usuario@icloud.com"}

// Response
{
  "messages": [
    {
      "otp_code": "123456",
      "from_": "remitente@fifa.com",
      "subject": "Your verification code",
      "date": "2024-01-01"
    }
  ]
}
```

**UEFA OTP:**
```json
// Request
POST /webhook
{"email": "usuario@icloud.com"}

// Response (SimpleResponse)
{
  "otp_code": "123456",
  "error": null
}
// o en caso de error:
{
  "otp_code": null,
  "error": "No se encontraron mensajes"
}
```

## Sistema de Permisos

### Acceso a Configuración
- **Botón:** "⚙️ Configuración" en el menú lateral
- **Contraseña de administrador:** `74674764Cc$`

### Funcionamiento
1. **Usuarios NO configurados:** Tienen acceso a TODAS las opciones por defecto
2. **Usuarios configurados:** Solo ven las opciones que tengan marcadas en su configuración
3. **Archivo de permisos:** `permisos_usuarios.json`

### Estructura del archivo de permisos
```json
{
  "usuario@ejemplo.com": {
    "opciones": ["🔑 FIFA OTP", "🔑 UEFA OTP"]
  },
  "otro@ejemplo.com": {
    "opciones": ["📋 Mundial Comprobantes"]
  }
}
```

### Opciones Disponibles
- `🔑 FIFA OTP` - Consulta OTP de FIFA
- `🔑 UEFA OTP` - Consulta OTP de UEFA
- `📋 Mundial Comprobantes` - Verificación de comprobantes
- `📤 Comprobantes Anytickets` - Subir comprobantes a Anytickets

## Autenticación

La aplicación usa **Clerk** para autenticación. Configurar en `.env`:

```env
CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
SKIP_AUTH=false  # true para desarrollo sin auth
```

## Idiomas Soportados

- Español (es)
- English (en)
- हिन्दी - Hindi (hi)

## Comprobantes Anytickets - Características

### Funcionalidades
- **Subida Individual:** Subir un comprobante especificando Invoice ID
- **Subida Masiva:** Subir múltiples comprobantes desde archivos con nombre numérico
- **Marketplaces:** Soporta `general` y `gotickets`

### Configuración API
Los tokens de Anytickets se pueden configurar de dos formas:

1. **Desde la interfaz (recomendado):** En la pestaña "Configuración" del módulo Anytickets
   - Los tokens se guardan en `.env` automáticamente
   - Botón "💾 Guardar Tokens" para persistir la configuración

2. **Variables de entorno:** Editar directamente el archivo `.env`
```env
ANYTICKETS_BEARER_TOKEN=tu_bearer_token
ANYTICKETS_DEV_TOKEN=tu_dev_token
```

### API Endpoints
- Base URL: `https://any-catchall.com/api/v1`
- Upload: `POST /fulfillment/upload/static`
- Confirm: `POST /fulfillment/confirm`

### Formato de archivos masivos
Los archivos deben tener nombre numérico que corresponde al Invoice ID:
- `12345.png` → Invoice ID: 12345
- `67890.jpg` → Invoice ID: 67890

---

## Mundial Comprobantes - Características

### Métodos de Extracción OCR
1. **Solo OCR (Gratuito)** - Usa EasyOCR
2. **Solo Claude Vision** - Usa API de Anthropic (de pago)
3. **OCR + Fallback** - Intenta OCR primero, si falla usa Claude Vision

### Configuración API Anthropic
Se requiere API key de Anthropic para usar Claude Vision:
- Obtener en: https://console.anthropic.com/
- Configurar en la pestaña "Configuración" de Mundial Comprobantes

### Campos Extraídos
- Email del destinatario
- Número de Match
- Cantidad de tickets
- Categoría

## Instalación

### Opción 1: Local

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno (Windows)
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
streamlit run app.py
```

### Opción 2: Docker

```bash
# Construir imagen
docker build -f docker/Dockerfile -t otp-streamlit .

# Ejecutar con variables de entorno
docker run -p 8501:8501 \
  -e CLERK_PUBLISHABLE_KEY=pk_xxx \
  -e CLERK_SECRET_KEY=sk_xxx \
  -e SKIP_AUTH=false \
  otp-streamlit
```

### Opción 3: Docker Compose

```bash
# Copiar variables de entorno
cp docker/.env.example docker/.env
# Editar docker/.env con tus valores

# Ejecutar
cd docker
docker-compose up -d
```

### Opción 4: EasyPanel (Producción)

Ver instrucciones detalladas en `docker/DEPLOY.md`

## Dependencias Principales

- streamlit
- requests
- pandas
- anthropic (para Claude Vision)
- easyocr (para OCR gratuito)
- python-dotenv
- openpyxl (para exportar Excel)

## Ejecución

### Aplicación Principal (con menú lateral)
```bash
streamlit run app.py
```

### Versión Standalone (solo OTP)
```bash
streamlit run otp_consultor_web.py
```

### Con script batch (Windows)
```bash
iniciar_otp_consultor.bat
```

## Historial de Cambios

### v3.3 (Última actualización)
- ✅ Agregada carpeta `docker/` con configuración completa para **EasyPanel**
- ✅ Creado `Dockerfile` optimizado para Streamlit
- ✅ Creado `docker-compose.yml` para desarrollo local
- ✅ Creado `DEPLOY.md` con instrucciones detalladas de despliegue
- ✅ Agregados `.gitignore` y `.dockerignore`
- ✅ Agregado `.env.example` como referencia

### v3.2
- ✅ Corregido: Botón **Editar** en usuarios ahora funciona correctamente (reset de widget keys)
- ✅ Corregido: Lista de usuarios ahora muestra **todas las opciones** con su estado (✅/❌)
- ✅ Actualizada carpeta `dist/` con todos los cambios

### v3.1
- ✅ Corregido: Checkbox de **Comprobantes Anytickets** ahora aparece en configuración de permisos
- ✅ Corregido: Error `StreamlitAPIException` al editar usuarios (session_state key conflict)
- ✅ Tokens de Anytickets configurables desde la interfaz con botón "Guardar Tokens"
- ✅ Actualizada carpeta `dist/` con todos los cambios

### v3.0
- ✅ Agregado módulo **Comprobantes Anytickets**
- ✅ Creado `modules/anytickets_page.py` - Interfaz Streamlit
- ✅ Creado `modules/anytickets_client.py` - Cliente API Anytickets
- ✅ Soporte para subida individual y masiva
- ✅ Actualizada carpeta `dist/` con todos los cambios

### v2.0
- ✅ Agregada opción **UEFA OTP** al menú lateral
- ✅ Creado módulo `modules/uefa_otp_page.py`
- ✅ Implementado **sistema de permisos por usuario**
- ✅ Agregada **página de configuración** protegida por contraseña
- ✅ Actualizada versión standalone `otp_consultor_web.py` con selector FIFA/UEFA
- ✅ Actualizada carpeta `dist/` con todos los cambios

### v1.0 (Versión inicial)
- FIFA OTP
- Mundial Comprobantes
- Autenticación Clerk
- Soporte multiidioma

## Notas para Desarrollo

### Agregar Nueva Opción al Menú
1. Crear módulo en `modules/nueva_opcion_page.py` con función `render()`
2. Agregar a `TODAS_LAS_OPCIONES` en `app.py`
3. Agregar el `elif` correspondiente en la sección de contenido
4. Copiar a `dist/modules/`

### Archivos a Sincronizar con dist/
- `app.py`
- `modules/*.py`
- `clerk_auth.py`

---

**Última actualización:** Febrero 2026
