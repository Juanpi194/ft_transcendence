# Base de datos

## Visión general

- La base de datos es **PostgreSQL**, y se accede desde el backend con **SQLAlchemy**.
- Los modelos (las clases que representan las tablas) están en `backend/app/models/`, un archivo por modelo, y se exportan en `models/__init__.py`.
- El esquema solo se cambia mediante **migraciones de Alembic**, nunca a mano.
- Para mirar la base desde la terminal (con los contenedores arrancados):

```bash
docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Dentro de `psql`, `\dt` lista las tablas y `\d nombre_tabla` describe una. Más detalles de Docker en `docs/docker.md`.

## Tablas

### `users`

Guarda las cuentas de usuario.

- `id`: clave primaria.
- `username` y `email`: únicos y obligatorios.
- `hashed_password`: la contraseña ya cifrada. Nunca se guarda en claro.
- `avatar_url`: opcional. El valor por defecto (`DEFAULT_AVATAR`) lo pone el código Python.
- `is_active`: booleano, obligatorio, verdadero por defecto.
- `is_private`: booleano, obligatorio, **falso por defecto**. Indica si la cuenta es privada, es decir, si para seguirla hay que enviar una solicitud y esperar aprobación.
- `created_at`: fecha de creación, que rellena la base con `now()`.

### `follows`

Guarda **quién sigue a quién**. Una fila significa "A sigue a B", o bien "A ha solicitado seguir a B" si todavía no está aceptado.

Refleja el **estado actual**, no un historial: dejar de seguir o rechazar una solicitud **borra la fila**.

- `follower_id`: quién sigue (clave foránea a `users.id`).
- `followed_id`: a quién se sigue (clave foránea a `users.id`).
- `status`: `accepted` o `pending`. **No tiene valor por defecto a propósito**: quien escribe el código está obligado a decidirlo, para evitar que una cuenta privada quede aceptada por un olvido. Los textos están en `core/constants.py` (`FOLLOW_ACCEPTED_TXT` y `FOLLOW_PENDING_TXT`).
- `created_at`: cuándo se creó, con `now()`.

Reglas que garantiza la propia base de datos:

- No se puede seguir dos veces al mismo usuario (clave primaria compuesta `follower_id` + `followed_id`).
- Nadie puede seguirse a sí mismo (`disallow_autofollow`).
- `status` solo admite los valores permitidos (`status_accepted_values`).
- Los dos usuarios tienen que existir (claves foráneas).
- Si se borra un usuario, se borran sus filas de `follows` (`ON DELETE CASCADE`).
- Hay un índice sobre `followed_id`, para consultar rápido "quién sigue a X".

### `blocks`

Guarda **quién bloquea a quién**. Una fila significa "A bloquea a B", en una sola dirección. Desbloquear es **borrar la fila**.

- `blocker_id`: quién bloquea (clave foránea a `users.id`).
- `blocked_id`: a quién se bloquea (clave foránea a `users.id`).
- `created_at`: cuándo se bloqueó, con `now()`.

Reglas que garantiza la base de datos:

- No se puede bloquear dos veces al mismo usuario (clave primaria compuesta).
- Nadie puede bloquearse a sí mismo (`disallow_autoblock`).
- Si se borra un usuario, se borran sus bloqueos (`ON DELETE CASCADE`).
- Hay un índice sobre `blocked_id`.

Esta tabla la usará también el chat.

## Convenciones comunes

- Las columnas que apuntan a otra tabla acaban en `_id`.
- `created_at` lo rellena la base de datos (`server_default`), no el código.
- Los valores por defecto que importan para la integridad de los datos están **en la base de datos** (`server_default`), no solo en Python, para que se cumplan aunque el `INSERT` no venga del backend.
- Las tablas que conectan dos usuarios usan una clave primaria compuesta, sin columna `id` propia.

## Reglas que debe cumplir el código

Estas reglas **no las impone el esquema**: tiene que cumplirlas el código del backend (los endpoints y las funciones que llaman). La base de datos solo guarda los datos y rechaza los inválidos, pero no ejecuta acciones por su cuenta.

1. **Estado al seguir.** Seguir a una cuenta pública crea la fila con `status = accepted`. Seguir a una cuenta privada (`is_private` verdadero) la crea con `status = pending`. Como `status` no tiene valor por defecto, siempre hay que indicarlo.
2. **Cuenta que pasa de privada a pública.** Todas las solicitudes pendientes hacia esa cuenta se aceptan automáticamente (`pending` pasa a `accepted`).
3. **Bloquear.** Al bloquear a alguien se eliminan los seguimientos entre ambos, **en las dos direcciones**, y todo debe hacerse en **una sola transacción** (o se hace todo o no se hace nada).
4. **Seguir a alguien bloqueado.** Antes de crear un seguimiento hay que comprobar que no existe un bloqueo entre los dos usuarios, en cualquiera de las dos direcciones.
5. **Dejar de seguir y rechazar.** Dejar de seguir a alguien, y rechazar una solicitud pendiente, **borran la fila** de `follows`. Si el usuario rechazado quiere impedir que lo intente de nuevo, la herramienta es bloquear.
6. **Amigos.** Dos usuarios son amigos cuando existen **las dos filas** de `follows` (A sigue a B y B sigue a A) con `status = accepted`. La amistad **no se guarda** en ninguna tabla: se calcula con una consulta.

## Cómo cambiar el esquema

1. Modificar el modelo en `backend/app/models/`.
2. Generar la migración:

```bash
docker compose exec backend alembic revision --autogenerate -m "mensaje en imperativo"
```

3. **Leer el archivo generado** antes de aplicarlo. Alembic no detecta todo, y hay que comprobar que contiene lo que se espera (restricciones, índices, `server_default`...).
4. Aplicarla y comprobar el resultado:

```bash
docker compose exec backend alembic upgrade head
```

Normas:

- **No editar migraciones que ya estén integradas en `main`.** Los cambios se hacen con una migración nueva.
- **Los cambios del esquema pasan por quien lleva la base de datos.** Si dos personas generan una migración a la vez a partir del mismo punto, la cadena se bifurca (dos "cabezas") y hay que arreglarlo a mano.

## Pendiente y futuro

- **Mejores amigos:** una lista aparte (tabla propia), solo entre usuarios que se siguen mutuamente. La comprobación de esa condición la haría el código.
- **Chat:** conversaciones privadas y grupos, mensajes con estado de lectura, edición y borrado. El diseño de las tablas (conversaciones, participantes y mensajes) está pendiente.