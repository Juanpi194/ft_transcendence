# Tests

## Requisitos previos

Los tests se ejecutan **en tu equipo**, no dentro del contenedor, y se conectan a la base de datos de Docker por `localhost:5432`. Solo hace falta el servicio `db`.

1. Levantar la base y esperar a que aparezca `healthy` en la columna de estado:

```bash
docker compose up -d db
docker compose ps
```

2. Crear la base de pruebas. Se hace **una única vez**, porque no se crea sola (hay que repetirlo si se recrea el volumen con `docker compose down -v`):

```bash
docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE DATABASE transcendence_test;"'
```

La base de pruebas se llama **transcendence_test** y es distinta de la de desarrollo. Los tests crean y borran sus tablas en cada ejecución. Para no tocar nunca la base de desarrollo, el fixture `db` (`tests/conftest.py`) se niega a ejecutarse si el nombre de la base no termina en `_test`.

## Comando necesario para que funcione

Desde `backend/`:

```bash
set -a; source ../.env; set +a
export DATABASE_URL="postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/transcendence_test"
uv run python -m pytest -v
```

## Variantes útiles

Un test en concreto:

```bash
uv run python -m pytest -v tests/test_follows.py::func_name
```

Parar en el primer fallo:

```bash
uv run python -m pytest -v -x
```

Todos los tests cuyo nombre contiene un texto:

```bash
uv run python -m pytest -v -k "insert_text"
```

Ver los `print` (pytest los oculta por defecto):

```bash
uv run python -m pytest -v -s
```

## Estructura

- `tests/conftest.py`: el fixture `db`, que prepara las tablas y las borra al terminar.
- `tests/helpers.py`: funciones para crear datos de prueba (`create_user`, `create_block`).
- Un archivo `test_*.py` por cada servicio de `app/services/`.
