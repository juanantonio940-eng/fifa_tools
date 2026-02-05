# OTP Streamlit - FIFA Tools

Aplicación web Streamlit para consulta de códigos OTP y verificación de comprobantes del Mundial FIFA 2026.

**Repositorio:** https://github.com/juanantonio940-eng/fifa_tools

## Descripción

Esta aplicación proporciona cuatro herramientas principales:
1. **FIFA OTP** - Consulta de códigos OTP de FIFA desde correos de iCloud
2. **UEFA OTP** - Consulta de códigos OTP de UEFA desde correos de iCloud
3. **Mundial Comprobantes** - Verificación de comprobantes de tickets del Mundial FIFA 2026
4. **Comprobantes Anytickets** - Subir comprobantes de transferencia a Anytickets

## Despliegue en Producción (EasyPanel)

### Repositorio GitHub
```
https://github.com/juanantonio940-eng/fifa_tools.git
```

### Configuración en EasyPanel

1. **Crear App desde GitHub:**
   - Projects → Create App → GitHub
   - Seleccionar repositorio `fifa_tools`
   - Branch: `main`
   - **Dockerfile Path:** `docker/Dockerfile`
   - **Build Context:** `.`

2. **Puerto:** `8501`

3. **Variables de Entorno:**
```env
CLERK_PUBLISHABLE_KEY=pk_test_xxx
CLERK_SECRET_KEY=sk_test_xxx
CLERK_DOMAIN=xxx.accounts.dev
USE_CLERK_AUTH=true
SKIP_AUTH=false
ANTHROPIC_API_KEY=sk-ant-xxx
ANYTICKETS_BEARER_TOKEN=xxx
ANYTICKETS_DEV_TOKEN=xxx
```
> **Nota:** Las claves reales están en el archivo `.env` local (no subido a GitHub)

4. **Deploy** y listo.

---

## Estructura del Proyecto

```
fifa_tools/
├── app.py                      # Aplicación principal con menú lateral
├── otp_consultor_web.py        # Versión standalone (FIFA + UEFA)
├── clerk_auth.py               # Autenticación con Clerk
├── permisos_usuarios.json      # Permisos de usuarios (se crea automáticamente)
├── .gitignore                  # Archivos ignorados por Git
├── .dockerignore               # Archivos ignorados por Docker
├── requirements.txt            # Dependencias
│
├── modules/
│   ├── __init__.py
│   ├── otp_page.py             # Módulo FIFA OTP
│   ├── uefa_otp_page.py        # Módulo UEFA OTP
│   ├── comprobantes_page.py    # Módulo Mundial Comprobantes
│   ├── anytickets_page.py      # Módulo Comprobantes Anytickets
│   └── anytickets_client.py    # Cliente API Anytickets
│
├── docker/
│   ├── Dockerfile              # Imagen Docker (python:3.11-slim)
│   ├── docker-compose.yml      # Compose para desarrollo local
│   ├── requirements.txt        # Dependencias con versiones
│   ├── .env.example            # Ejemplo de variables de entorno
│   └── DEPLOY.md               # Instrucciones detalladas
│
└── dist/                       # Carpeta de distribución local
    ├── app.py
    ├── clerk_auth.py
    └── modules/
```

---

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

---

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

---

## Autenticación

La aplicación usa **Clerk** para autenticación.

| Variable | Descripción |
|----------|-------------|
| `CLERK_PUBLISHABLE_KEY` | Clave pública de Clerk |
| `CLERK_SECRET_KEY` | Clave secreta de Clerk |
| `CLERK_DOMAIN` | Dominio de Clerk |
| `SKIP_AUTH` | `false` (cambiar a `true` para desactivar auth) |

> Obtener claves en: https://dashboard.clerk.com/

---

## Idiomas Soportados

- Español (es)
- English (en)
- हिन्दी - Hindi (hi)

---

## Comprobantes Anytickets

### Funcionalidades
- **Subida Individual:** Subir un comprobante especificando Invoice ID
- **Subida Masiva:** Subir múltiples comprobantes desde archivos con nombre numérico
- **Marketplaces:** Soporta `general` y `gotickets`

### Configuración API
| Variable | Descripción |
|----------|-------------|
| `ANYTICKETS_BEARER_TOKEN` | Token Bearer de autenticación |
| `ANYTICKETS_DEV_TOKEN` | Token de desarrollo |

### API Endpoints
- Base URL: `https://any-catchall.com/api/v1`
- Upload: `POST /fulfillment/upload/static`
- Confirm: `POST /fulfillment/confirm`

### Formato de archivos masivos
Los archivos deben tener nombre numérico que corresponde al Invoice ID:
- `12345.png` → Invoice ID: 12345
- `67890.jpg` → Invoice ID: 67890

---

## Mundial Comprobantes

### Métodos de Extracción OCR
1. **Solo OCR (Gratuito)** - Usa EasyOCR
2. **Solo Claude Vision** - Usa API de Anthropic (de pago)
3. **OCR + Fallback** - Intenta OCR primero, si falla usa Claude Vision

### Configuración API Anthropic
| Variable | Descripción |
|----------|-------------|
| `ANTHROPIC_API_KEY` | API key de Anthropic para Claude Vision |

Obtener en: https://console.anthropic.com/

### Campos Extraídos
- Email del destinatario
- Número de Match
- Cantidad de tickets
- Categoría

---

## Instalación Local

### Opción 1: Python directo

```bash
# Clonar repositorio
git clone https://github.com/juanantonio940-eng/fifa_tools.git
cd fifa_tools

# Crear entorno virtual
python -m venv .venv

# Activar entorno (Windows)
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env con las variables
# Ejecutar
streamlit run app.py
```

### Opción 2: Docker local

```bash
# Construir imagen
docker build -f docker/Dockerfile -t fifa-tools .

# Ejecutar
docker run -p 8501:8501 \
  -e CLERK_PUBLISHABLE_KEY=pk_xxx \
  -e CLERK_SECRET_KEY=sk_xxx \
  -e SKIP_AUTH=false \
  fifa-tools
```

### Opción 3: Docker Compose

```bash
cp docker/.env.example docker/.env
# Editar docker/.env con tus valores

cd docker
docker-compose up -d
```

---

## Dependencias Principales

| Paquete | Uso |
|---------|-----|
| streamlit | Framework web |
| requests | HTTP requests |
| pandas | Procesamiento de datos |
| anthropic | Claude Vision API |
| easyocr | OCR gratuito |
| python-dotenv | Variables de entorno |
| openpyxl | Exportar Excel |
| Pillow | Procesamiento de imágenes |

---

## Historial de Cambios

### v3.4 (Última actualización - Febrero 2026)
- ✅ **Desplegado en producción** en EasyPanel
- ✅ Repositorio GitHub: `juanantonio940-eng/fifa_tools`
- ✅ Corregido Dockerfile: `libgl1` en lugar de `libgl1-mesa-glx`
- ✅ Añadido `curl` para health check en Docker
- ✅ Documentación completa actualizada

### v3.3
- ✅ Agregada carpeta `docker/` con configuración completa para EasyPanel
- ✅ Creado `Dockerfile` optimizado para Streamlit
- ✅ Creado `docker-compose.yml` para desarrollo local
- ✅ Creado `DEPLOY.md` con instrucciones detalladas de despliegue
- ✅ Agregados `.gitignore` y `.dockerignore`

### v3.2
- ✅ Corregido: Botón **Editar** en usuarios ahora funciona correctamente
- ✅ Corregido: Lista de usuarios muestra **todas las opciones** con su estado (✅/❌)

### v3.1
- ✅ Corregido: Checkbox de **Comprobantes Anytickets** en permisos
- ✅ Corregido: Error `StreamlitAPIException` al editar usuarios
- ✅ Tokens de Anytickets configurables desde la interfaz

### v3.0
- ✅ Agregado módulo **Comprobantes Anytickets**
- ✅ Creado `modules/anytickets_page.py` y `anytickets_client.py`
- ✅ Soporte para subida individual y masiva

### v2.0
- ✅ Agregada opción **UEFA OTP**
- ✅ Implementado **sistema de permisos por usuario**
- ✅ Página de configuración protegida por contraseña

### v1.0 (Versión inicial)
- FIFA OTP
- Mundial Comprobantes
- Autenticación Clerk
- Soporte multiidioma

---

## Notas para Desarrollo

### Agregar Nueva Opción al Menú
1. Crear módulo en `modules/nueva_opcion_page.py` con función `render()`
2. Agregar a `TODAS_LAS_OPCIONES` en `app.py`
3. Agregar el `elif` correspondiente en la sección de contenido
4. Commit y push a GitHub → EasyPanel rebuilds automáticamente

### Actualizar Producción
```bash
git add .
git commit -m "Descripción del cambio"
git push
# EasyPanel detecta el cambio y hace rebuild automático
```

---

**Última actualización:** Febrero 2026
