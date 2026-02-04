# Dockerfile para OTP Streamlit - FIFA Tools
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para easyocr, PIL y health check
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (para cache de Docker)
COPY docker/requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY app.py .
COPY clerk_auth.py .
COPY modules/ ./modules/

# Crear archivo de permisos vacío si no existe
RUN echo "{}" > permisos_usuarios.json

# Crear directorios necesarios
RUN mkdir -p datos_usuarios logs

# Configurar Streamlit
RUN mkdir -p ~/.streamlit
RUN echo "\
[server]\n\
headless = true\n\
port = 8501\n\
enableCORS = false\n\
enableXsrfProtection = false\n\
\n\
[browser]\n\
gatherUsageStats = false\n\
" > ~/.streamlit/config.toml

# Exponer puerto de Streamlit
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando para ejecutar la aplicación
ENTRYPOINT ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
