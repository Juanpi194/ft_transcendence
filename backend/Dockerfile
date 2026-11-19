# TODO: Clear the comments

# 1. La imagen base de Python
FROM python:3.10-slim

# 1.2. Creamos variables que usaremos en el Dockerfile
ARG APP_USER=appuser
ARG APP_UID=1000

# 2. Copiamos el binario de 'uv' desde su imagen oficial (basicamente instalamos uv en el contenedor)
COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /bin/uv

# 3. Creamos y nos situamos en una carpeta de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiamos los archivos de dependencias primero
COPY pyproject.toml uv.lock ./

# 5. Instalamos las dependencias globalmente en el sistema del contenedor con uv
RUN uv sync --locked --no-dev

# 6. Copiamos el resto del código fuente de nuestro proyecto al contenedor
COPY . .

# 7. Añadimos el entorno virtual de uv al PATH del contenedor
ENV PATH="/app/.venv/bin:$PATH"

# 8. Creación del usuario para que el usuario que ejecute este contenedor no tenga permisos de root.
RUN useradd --uid ${APP_UID} ${APP_USER}

USER ${APP_USER}

# 9. Comando para arrancar el servidor web
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]