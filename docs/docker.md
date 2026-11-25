# Docker: separar desarrollo de producción

## Idea general

Un solo `docker-compose.yml` mezclaba lo que hace falta **siempre** con comodidades que solo sirven mientras programas. Ahora está repartido en dos archivos:

- `docker-compose.yml` (base): lo común. Es lo que se usaría en producción.
- `docker-compose.override.yml`: solo desarrollo. Compose lo carga automáticamente al ejecutar `docker compose up`.

Para ver producción (solo el base):

```bash
docker compose -f docker-compose.yml up
```

## Cómo se fusionan los dos archivos

- **Valor simple** (`restart`, `command`...): el override **sustituye** al base.
- **Lista** (`ports`, `volumes`): se **suman**.

Consecuencia: un override **no puede quitar** nada del base. Lo exclusivo de desarrollo hay que **mover** al override, no solo copiarlo. Y el override debe contener solo lo que cambia.

## Qué va en cada archivo

- **Base** (`docker-compose.yml`): `image`, `env_file`, `build`, `environment`, `depends_on`, puerto 8000, volumen `postgres_data`, `healthcheck` y `restart: unless-stopped`.
- **Override** (`docker-compose.override.yml`): enlace `./backend:/app` y `/app/.venv`, puerto de la base `127.0.0.1:5432:5432`, `command` con `--reload` y `restart: "no"`.

## Cómo comprobar el resultado

- `docker compose config`: muestra la fusión (desarrollo).
- `docker compose -f docker-compose.yml config`: muestra solo el base (producción).
- **Aviso:** esa salida incluye `POSTGRES_PASSWORD` en claro. No pegarla en ningún sitio.
- `docker compose config --quiet`: solo valida, sin imprimir nada.
- `docker build --check backend`: linter del Dockerfile (sintaxis, buenas prácticas y que las imágenes y etiquetas existan). No construye nada.

## Puertos

- **Puerto interno:** donde escucha el programa dentro del contenedor (Postgres siempre en 5432).
- **Puerto publicado** (`ports`): la "puerta" que se abre hacia fuera.
- Sin `ports`, la base sigue siendo accesible **desde otros contenedores** (el backend usa `db:5432` por la red interna de Compose), pero no desde fuera.
- `127.0.0.1:5432:5432`: solo tu máquina puede conectar, no tu red.

## El enlace de carpetas y los permisos

- `./backend:/app` comparte la carpeta de tu equipo con el contenedor (mismos archivos en los dos lados).
- `/app/.venv` "tapa" el `.venv` dentro del contenedor con un volumen propio, porque el de tu equipo y el del contenedor no son intercambiables.
- **Por qué puede aparecer un `.venv` vacío de root:** Docker necesita el hueco en tu disco para enchufar ese volumen y, si no existe, lo crea él (como root). Entonces `uv sync` falla con `Permission denied`.
- Arreglo puntual:

```bash
sudo chown $USER:$USER .venv
```

## Usuario no root

- **Problema:** el contenedor corría como root (UID 0) y todo lo que creaba en la carpeta enlazada (`__pycache__`) quedaba en tu disco con dueño root.
- **Idea clave:** Linux identifica a los usuarios por **número** (UID), no por nombre. El primer usuario de un sistema suele ser el 1000.
- **Solución:** en el `Dockerfile`, crear un usuario con UID 1000 y activarlo con `USER`, **después** de los pasos que necesitan root (`uv sync`, `COPY`) y **antes** del `CMD`.
- `ARG APP_USER` y `ARG APP_UID`: variables que solo existen al construir la imagen. Si tu UID no es 1000 (compruébalo con `id -u`), cambia `APP_UID` en el `Dockerfile` del backend. Más adelante se podría pasar desde el compose (`build: args:`).
- **Motivos:** comodidad (los archivos son tuyos) y **seguridad** (si explotan un fallo de la app, no tienen root).
- Efecto secundario: ya no hace falta `--user $(id -u):$(id -g)` en `docker compose exec`.
- Los `__pycache__` de root que ya existían hay que borrarlos una vez. Primero, sin borrar nada, para ver qué listaría:

```bash
sudo find backend/app backend/migrations -name __pycache__ -type d
```

Y si la lista es la esperada, añadiendo el borrado:

```bash
sudo find backend/app backend/migrations -name __pycache__ -type d -exec rm -rf {} +
```

## `--reload`
Es una opción de desarrollo. Se quitó del `CMD` del `Dockerfile` y se añadió en el `command` del override. Al cambiar el `Dockerfile` hay que reconstruir:

```bash
docker compose up -d --build
```

## Políticas de reinicio (`restart`)

- `"no"`: nunca reinicia.
- `on-failure`: solo si termina con error (admite límite: `on-failure:5`).
- `always`: siempre, incluso si lo paraste tú, al volver a arrancar Docker.
- `unless-stopped`: como `always`, pero respeta si lo paraste a mano.

Detalles:

- Docker solo mira si el **proceso principal termina**. Un error dentro de una petición (un 500) no reinicia nada.
- **Elección:** `unless-stopped` en el base (producción) y `"no"` en el override, para ver los errores en lugar de un bucle.
- **Cuidado:** en YAML, `no` sin comillas es el valor booleano falso. Hay que escribir `"no"`.

## Versión de `uv` fijada

`ghcr.io/astral-sh/uv:latest` cambiaba según el día en que se construyera la imagen. Ahora se usa `uv:0.13.9`, la versión que ya funcionaba. Se actualiza **a propósito**, cambiando el número.
actualiza **a propósito**, cambiando el número.

## Healthcheck de la base de datos

- `depends_on` en forma corta solo espera a que el contenedor **arranque**, no a que Postgres esté **listo**.
- `healthcheck` ejecuta `pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB` cada 5 segundos. Estados posibles: `starting`, `healthy` y `unhealthy`.
- `depends_on: db: condition: service_healthy` (con **guion bajo**) hace que el backend espere a que la base esté `healthy`.
- `$$` evita que Compose sustituya la variable con tu `.env`: así la lee el propio contenedor.
- `start_period`: periodo de gracia al arrancar durante el cual los fallos no cuentan para `retries`.

## Cambiar la contraseña de Postgres

`POSTGRES_PASSWORD` solo se lee cuando Postgres **inicializa una carpeta de datos vacía**, no al reconstruir ni al reiniciar. Cambiar solo el `.env` no cambia la contraseña real.

Dos opciones:

- Cambiarla dentro de la base con `ALTER USER` desde `psql`.
- Recrear la base: `docker compose down -v` (borra el volumen y los datos), `docker compose up -d` y después `alembic upgrade head`.

## Dibujo visual de la estructura

```
En el contenedor, /app:          En tu equipo, backend/:
.dockerignore                    .dockerignore
.venv                            .venv
Dockerfile                       Dockerfile
alembic.ini                      alembic.ini
app          ← el paquete        app          ← el paquete
migrations                       migrations
pyproject.toml                   pyproject.toml
tests                            tests
uv.lock                          uv.lock
```