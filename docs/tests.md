## Comando necesario para que funcione
Desde /backend

set -a; source ../.env; set +a
export DATABASE_URL="postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/transcendence_test"
uv run python -m pytest -v

La base de datos de prueba se llama **transcendence_test**.

Para pasar un test en concreto:
uv run python -m pytest -v tests/test_follows.py::func_name

Para parar en el primer fallo:
uv run python -m pytest -v -x

Para pasar todos los tests cuyo nombre contiene un texto:
uv run python -m pytest -v -k "insert_text"
