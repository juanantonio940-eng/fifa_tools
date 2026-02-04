# Despliegue en EasyPanel

## Requisitos Previos

1. Cuenta en EasyPanel
2. Repositorio privado en GitHub con el código
3. Tokens y API keys necesarios

## Estructura de Archivos

```
Otp_streamlit/
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .dockerignore
│   ├── requirements.txt
│   └── DEPLOY.md
├── app.py
├── clerk_auth.py
├── modules/
│   ├── __init__.py
│   ├── otp_page.py
│   ├── uefa_otp_page.py
│   ├── comprobantes_page.py
│   ├── anytickets_page.py
│   └── anytickets_client.py
└── requirements.txt
```

## Paso 1: Preparar el Repositorio GitHub

1. Crear repositorio privado en GitHub
2. Subir el contenido de la carpeta `Otp_streamlit`:

```bash
cd Otp_streamlit
git init
git add .
git commit -m "Initial commit - OTP Streamlit FIFA Tools"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

## Paso 2: Configurar EasyPanel

### Opción A: Usando GitHub App (Recomendado)

1. En EasyPanel, ir a **Projects** → **Create Project**
2. Seleccionar **App** → **GitHub**
3. Conectar con tu cuenta de GitHub
4. Seleccionar el repositorio privado
5. Configurar:
   - **Branch:** `main`
   - **Dockerfile Path:** `docker/Dockerfile`
   - **Build Context:** `.` (raíz del repositorio)

### Opción B: Usando Docker Image

1. En EasyPanel, crear un nuevo **App**
2. Seleccionar **Docker Image**
3. Configurar el build desde GitHub

## Paso 3: Variables de Entorno

En EasyPanel, ir a la pestaña **Environment** y agregar:

### Autenticación Clerk (Obligatorio)
```
CLERK_PUBLISHABLE_KEY=pk_live_xxxx
CLERK_SECRET_KEY=sk_live_xxxx
```

### Modo Debug (Opcional)
```
SKIP_AUTH=false
```
> Cambiar a `true` para desactivar autenticación durante pruebas

### Anytickets API (Para módulo Comprobantes Anytickets)
```
ANYTICKETS_BEARER_TOKEN=tu_bearer_token
ANYTICKETS_DEV_TOKEN=tu_dev_token
```

### Anthropic API (Para Claude Vision en Mundial Comprobantes)
```
ANTHROPIC_API_KEY=sk-ant-xxxx
```

## Paso 4: Configurar Puerto

En la pestaña **Domains**:
- **Container Port:** `8501`
- Configurar dominio o subdominio

## Paso 5: Persistencia de Datos (Opcional)

Para persistir datos entre reinicios, configurar volúmenes en **Mounts**:

| Host Path | Container Path | Descripción |
|-----------|----------------|-------------|
| `/data/otp/usuarios` | `/app/datos_usuarios` | Datos de usuarios |
| `/data/otp/logs` | `/app/logs` | Logs de seguridad |
| `/data/otp/permisos.json` | `/app/permisos_usuarios.json` | Permisos de usuarios |

## Paso 6: Deploy

1. Hacer clic en **Deploy**
2. Esperar a que el build complete
3. Verificar los logs para errores
4. Acceder a la URL configurada

## Verificación

1. Acceder a la URL de la aplicación
2. Verificar que aparece la pantalla de login de Clerk
3. Iniciar sesión y probar las funcionalidades

## Troubleshooting

### Error: ModuleNotFoundError
- Verificar que `requirements.txt` incluye todas las dependencias
- Reconstruir la imagen: **Rebuild**

### Error: Puerto no accesible
- Verificar que el puerto 8501 está configurado correctamente
- Revisar configuración de dominio/proxy

### Error: Variables de entorno no encontradas
- Verificar que las variables están configuradas en EasyPanel
- Reiniciar el servicio después de agregar variables

### Logs
- Ver logs en EasyPanel: **Logs** tab
- Los logs de la aplicación aparecen en tiempo real

## Actualizar la Aplicación

1. Hacer push de cambios a GitHub:
```bash
git add .
git commit -m "Update: descripción del cambio"
git push
```

2. En EasyPanel, hacer clic en **Rebuild** o configurar **Auto Deploy**

## Configuración de Auto Deploy

1. En EasyPanel, ir a **Settings**
2. Activar **Auto Deploy**
3. Seleccionar branch (`main`)
4. Cada push a `main` desplegará automáticamente

---

## Resumen de Variables de Entorno

| Variable | Obligatorio | Descripción |
|----------|-------------|-------------|
| `CLERK_PUBLISHABLE_KEY` | Sí | Clerk public key |
| `CLERK_SECRET_KEY` | Sí | Clerk secret key |
| `SKIP_AUTH` | No | `true` para desactivar auth |
| `ANYTICKETS_BEARER_TOKEN` | No* | Token Anytickets |
| `ANYTICKETS_DEV_TOKEN` | No* | Dev token Anytickets |
| `ANTHROPIC_API_KEY` | No* | API key de Anthropic |

*Obligatorio si se usa el módulo correspondiente

---

**Última actualización:** Febrero 2026
