# OTP Streamlit - FIFA Tools

Aplicación web Streamlit para consulta de códigos OTP y verificación de comprobantes del Mundial FIFA 2026.

**Repositorio:** https://github.com/juanantonio940-eng/fifa_tools

## Descripción

Esta aplicación proporciona siete herramientas principales:
1. **FIFA OTP** - Consulta de códigos OTP de FIFA desde correos de iCloud
2. **UEFA OTP** - Consulta de códigos OTP de UEFA desde correos de iCloud
3. **Mundial Comprobantes** - Verificación de comprobantes de tickets del Mundial FIFA 2026
4. **Comprobantes Anytickets** - Subir comprobantes de transferencia a Anytickets
5. **Lectura Correos** - Lectura avanzada de correos IMAP con carga de cuentas CSV, selección de cuentas, búsqueda robusta v4, extracción FIFA detallada y descarga de adjuntos
6. **Control BD** - Gestión de la tabla icloud_accounts en Supabase (buscar, editar, insertar, eliminar)
7. **Extracción Facturas** - Extracción de datos de facturas PDF con detección de moneda y anomalías

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
DATABASE_URL=postgresql://user:pass@db.xxx.supabase.co:5432/postgres?sslmode=require
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
├── permisos_usuarios.json      # (Legacy) Los permisos ahora se guardan en Supabase
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
│   ├── anytickets_client.py    # Cliente API Anytickets
│   ├── lectura_correos_page.py # Módulo Lectura Correos
│   ├── controlbd_page.py       # Módulo Control BD icloud_accounts
│   └── extraccion_factura_page.py # Módulo Extracción Facturas PDF
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
3. **Almacenamiento:** Tabla `app_permisos` en Supabase (persiste entre rebuilds de Docker)

### Tabla app_permisos (Supabase)
```sql
CREATE TABLE app_permisos (
    email TEXT PRIMARY KEY,
    opciones JSONB NOT NULL DEFAULT '[]'::jsonb
);
```

Ejemplo de datos:
```json
// email: "usuario@ejemplo.com"
// opciones: ["🔑 FIFA OTP", "🔑 UEFA OTP"]
```

### Opciones Disponibles
- `🔑 FIFA OTP` - Consulta OTP de FIFA
- `🔑 UEFA OTP` - Consulta OTP de UEFA
- `📋 Mundial Comprobantes` - Verificación de comprobantes
- `📤 Comprobantes Anytickets` - Subir comprobantes a Anytickets
- `📧 Lectura Correos` - Lectura de correos IMAP
- `🗄️ Control BD` - Gestión de icloud_accounts en Supabase
- `📄 Extracción Facturas` - Extracción de datos de facturas PDF

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

## Lectura Correos (v4)

### Descripción
Herramienta avanzada para lectura de correos IMAP desde múltiples cuentas con búsqueda robusta, extracción de datos FIFA World Cup 2026 y descarga de adjuntos.

### Funcionalidades
- **Carga de cuentas CSV:** Subir archivo CSV o pegar cuentas manualmente (email,password)
- **Selección de cuentas:** Multiselect para elegir qué cuentas conectar
- **Conexión con progreso:** Barra de progreso durante la conexión
- **Reconexión automática:** Si se pierde la conexión, reconecta automáticamente
- **Búsqueda robusta v4:** Envía solo 1 keyword al servidor IMAP por campo y filtra localmente (compatible con iCloud, Gmail, Outlook)
- **Filtros avanzados:** Asunto, remitente, destinatario, contenido (local), fecha, estado de lectura, carpeta IMAP, límite
- **Tabla de resultados:** DataFrame con cuenta, de, para, asunto, fecha, estado
- **Detalle de correos:** Expandir para ver contenido completo, adjuntos y botón de marcar como leído
- **Descarga de adjuntos:** Botón de descarga individual por adjunto
- **Marcar como leído:** Individual o masivo con progreso
- **Exportar CSV:** Todos los resultados a CSV
- **Extracción FIFA avanzada:** Partido (Match info), tipo (Conditional/Confirmed), categoría (Supporter Tier/Category), cantidad, precio USD, titular, equipo, solicitante
- **Exportar FIFA:** Excel y CSV con 11 columnas detalladas
- **Log de actividad:** Registro de todas las operaciones con descarga

### Pestañas
1. **Cuentas** - Subir CSV, pegar cuentas, seleccionar y conectar
2. **Búsqueda** - Filtros avanzados y botones de búsqueda rápida
3. **Resultados** - Tabla resumen + detalles expandibles + adjuntos
4. **FIFA** - Extracción de datos FIFA con filtros y exportación
5. **Logs** - Log de actividad con limpiar y descargar

### Columnas FIFA Extraídas
| Campo | Descripción |
|-------|-------------|
| Email Madre | Cuenta de conexión IMAP |
| Cuenta FIFA | Email destinatario (To) |
| Solicitante | Nombre extraído del email |
| Equipo | Equipo solicitado (My Team) |
| Fecha Email | Fecha del correo |
| Partido | Ronda + equipos (Semi-final, Match XX, etc.) |
| Tipo Ticket | Conditional / Confirmed |
| Categoría | Supporter Tier / Category N |
| Titular | Nombre del titular del ticket |
| Cantidad | Número de tickets |
| Precio USD | Precio en dólares |

---

## Control BD (icloud_accounts)

### Descripción
Herramienta para gestionar la tabla `icloud_accounts` en Supabase PostgreSQL. Permite buscar, editar, insertar y eliminar registros directamente desde la interfaz web.

### Campos de la tabla
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | bigint (PK) | ID autoincremental |
| `MAIL_MADRE` | text | Email madre de iCloud |
| `ALIAS` | text | Alias de la cuenta |
| `PASSWORD` | text | Contraseña de aplicación |
| `PAQUETE` | text | Paquete al que pertenece |
| `created_at` | timestamptz | Fecha de creación |

### Funcionalidades
- **Buscar:** Por cualquier campo (ALIAS, MAIL_MADRE, PASSWORD, PAQUETE, id) con búsqueda parcial (ILIKE) o exacta
- **Editar fila:** Seleccionar fila y modificar campos editables (MAIL_MADRE, ALIAS, PASSWORD, PAQUETE)
- **Edición masiva:** Actualizar un campo en todas las filas que coincidan con un criterio (ej: cambiar PASSWORD de todas las filas con un mismo MAIL_MADRE)
- **Insertar:** Agregar nuevas filas con formulario
- **Eliminar:** Con confirmación antes de borrar
- **Limite configurable:** Por defecto 500 filas, ajustable hasta 10.000

### Configuración
| Variable | Descripción |
|----------|-------------|
| `DATABASE_URL` | URL de conexión PostgreSQL a Supabase |

Formato: `postgresql://user:password@db.xxx.supabase.co:5432/postgres?sslmode=require`

---

## Extracción Facturas PDF

### Descripción
Herramienta para extraer datos de facturas PDF del Mundial FIFA 2026. Combina detección de moneda ISO 4217 (3 niveles de fallback) con detección de anomalías y erratas.

### Funcionalidades
- **Subida múltiple:** Subir uno o varios PDFs desde la interfaz
- **Detección de moneda:** 14 monedas ISO 4217 con 3 niveles de fallback (texto explícito, encabezados GROSS, patrones de monto)
- **Detección de anomalías:** Variables sin expandir, erratas comunes, validación de MATCH, validación de montos (qty x price = net, net + tax = total)
- **Exportar CSV:** 15 columnas (fecha, email, factura, entidad, moneda en precio_unitario, items, etc.)
- **Reporte de anomalías:** Descargable en TXT con resumen por tipo
- **Soporte multiidioma:** ES, EN, HI

### Campos CSV Extraídos
| Campo | Descripción |
|-------|-------------|
| `fecha_archivo` | Fecha del nombre del archivo |
| `email_orden` | Email extraído del nombre |
| `numero_factura` | FU-XXXX-XX o FM-XXXX-XX |
| `entidad_vendedora` | FWC2026 Mexico/US/Canada |
| `fecha_factura` | Invoice Date |
| `referencia_cliente` | Our Customer Reference |
| `referencia_orden` | Our Order Reference |
| `descripcion` | Descripción del item (MATCH) |
| `tax_rate` | Tasa de impuesto normalizada |
| `categoria` | Categoría del ticket |
| `cantidad` | Cantidad |
| `precio_unitario` | Precio unitario + moneda (ej: "150.00 USD") |
| `neto` | Monto neto |
| `impuesto` | Impuesto |
| `total` | Total |

### Tipos de Anomalías Detectadas
- `ERRATA_VARIABLE` - Variables sin expandir ($var, ${var}, %var%, {{var}})
- `ERRATA_PATRON` - Palabras duplicadas, valores null, errores Excel
- `MATCH_INVALIDO` - Variables sin expandir en descripción de MATCH
- `MATCH_INCOMPLETO` - MATCH sin número ordinal
- `CALCULO_INCORRECTO` - qty x price != net
- `TOTAL_INCORRECTO` - net + tax != total
- `MONTO_SOSPECHOSO` - Precio unitario > 10,000

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
| psycopg2-binary | Conexión PostgreSQL (Control BD) |
| pdfplumber | Extracción de tablas PDF (Extracción Facturas) |

---

## Historial de Cambios

### v4.1 (Última actualización - Febrero 2026)
- ✅ **Reescrito módulo Lectura Correos** (`modules/lectura_correos_page.py`) basado en Lectura_grafico_webhookv4.py
- ✅ Carga de cuentas via CSV (upload) o texto manual con selección de cuentas (multiselect)
- ✅ Búsqueda IMAP robusta v4: 1 keyword por campo al servidor + filtro local post-fetch
- ✅ `imap_search_safe()` con fallback UTF-8/None charset
- ✅ Reconexión automática ante pérdida de conexión (socket, EOF, broken)
- ✅ Filtros avanzados: asunto, remitente, destinatario, contenido (local), fecha, estado, carpeta, límite hasta 500
- ✅ Extracción FIFA avanzada: partido, tipo (Conditional/Confirmed), categoría (Supporter Tier), cantidad, precio USD, titular, equipo
- ✅ Descarga de adjuntos directa desde la interfaz
- ✅ Marcar como leído masivo con progreso
- ✅ Exportar resultados a CSV y FIFA a Excel/CSV
- ✅ 5 pestañas: Cuentas, Búsqueda, Resultados, FIFA, Logs
- ✅ Tab de logs con registro de actividad descargable

### v4.0
- ✅ Agregado módulo **Extracción Facturas** (`modules/extraccion_factura_page.py`)
- ✅ Extracción de datos de facturas PDF con detección de moneda ISO 4217 (14 monedas, 3 niveles de fallback)
- ✅ Detección de anomalías integrada (variables sin expandir, erratas, validación de montos)
- ✅ Subida múltiple de PDFs con barra de progreso
- ✅ Exportar CSV (15 columnas) y reporte de anomalías TXT
- ✅ Soporte multiidioma (ES, EN, HI)
- ✅ Integrado en sistema de permisos
- ✅ Añadida dependencia `pdfplumber`

### v3.6.1
- ✅ Corregido error en botón **Limpiar** de Control BD (`StreamlitAPIException: session_state cannot be modified after widget is instantiated`)

### v3.6
- ✅ **Permisos persistentes en Supabase:** Los permisos de usuarios se guardan en la tabla `app_permisos` en lugar de un archivo JSON local, sobreviven a cualquier rebuild de Docker
- ✅ Agregado **Edición masiva** en Control BD: actualizar un campo en todas las filas que coincidan con un criterio (ej: cambiar PASSWORD de un MAIL_MADRE)
- ✅ Vista previa de filas afectadas y confirmación antes de ejecutar cambios masivos

### v3.5
- ✅ Agregado módulo **Control BD** (`modules/controlbd_page.py`)
- ✅ Gestión completa de tabla `icloud_accounts` en Supabase
- ✅ Buscar, editar, insertar y eliminar registros desde la interfaz
- ✅ Soporte multiidioma (ES, EN, HI)
- ✅ Integrado en sistema de permisos
- ✅ Añadida dependencia `psycopg2-binary`
- ✅ Añadida variable `DATABASE_URL` para conexión PostgreSQL

### v3.4
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
