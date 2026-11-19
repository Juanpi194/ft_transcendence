## DOCKER-COMPOSE
Las palabras *db* y *backend* no son palabras clave, son los nombres que le estamos dando a los contenedores. Podemos poner lo que queramos.
### image
postgres:15-alpine
La más eficiente en la actualidad. 15 es la versión y alpine el sistema operativo que acompaña a Postgres por dentro. Si no ponemos nada se usa la latest
### environment (db)
Las variables de entorno obligatorias que la imagen oficial de PostgreSQL necesita para encenderese por primera vez.
### ports
El de la izquierda es por el que escucha la máquina, el de la derecha es el del contenedor.
### build
En nuestro caso, el contenedor no se crea a través de una imagen, el backend va a ser nuestro propio código de Python. En esa ruta habrá un Dockerfile y se construirá la imagen con las instrucciones de ese Dockerfile.
### depends_on
El contenedor que dependa de otro no arrancará HASTA QUE el contenedor al que hace referencia no arranque. Si del que hace depende no arranca, este tampoco arrancará. En nuestro caso, *backend* no arrancará si *db* no arranca.
### environment (backend)
No lo entiendo la verdad.
- **Mi manera de entenderlo**:
Es como una especie de login en la página postgresql, concretamente al servidor db. Una vez nos hemos logeado, tendríamos que indicarle a qué base de datos concreta queremos conectarnos, que en este caso es transcendence_db.
- **Explicación de GEMINI**:
Es como abrir la puerta del "edificio" de PostgreSQL usando tus llaves (usuario y contraseña), entrar al servidor que está en db:5432, y sentarte directamente en la mesa de trabajo (la base de datos) llamada transcendence_db
### Enlace de carpetas
En lugar de copiar todos los archivos para la imagen, usamos un enlazado de carpetas.
Para desarrollo, mantener el enlace. Corresponde a esta linea:
- ./backend:/app
Significa que la carpeta backend de mi equipo es la misma carpeta app del contenedor, ignorando el COPY . . del Dockerfile (el enlaza lo tapa en el contenedor).
Para producción, borrar esa linea y hacer la copia.

Y esta linea:
- /app/.venv
indica que no se haga enlaze de esa ruta. Para que el contenedor no use el venv del equipo, sino del contenedor.

## DOCKERFILE
Lo que haya en el *.dockerignore* no se copiará. Necesario para no copiar un venv no deseado por ejemplo.

### FROM
Le decimos a Docker qué versión de Python queremos instalar en el contenedor (la 3.10 es super estable), y usamos la etiqueta *slim* para que sea una versión ligera de Linux optimizada para Python.
### WORKDIR
Le indica a Docker que cree una carpeta llamada /app dentro del contenedor y que a partir de ese momento cualquier comando que ejecutemos se hará dentro de esa ruta. Es como hacer un cd /app.
Esta carpeta /app no existe en nuestro ordenador, vive dentro del "universo paralelo" del contenedor. Nosotros no podemos verla.
### UV
**--locked**: Le dice a Docker que falle si el uv.lock no está actualizado con respecto al pyproject.toml, garantizando consistencia absoluta.

**--no-dev**: Omite la instalación de librerías de desarrollo o testing (como herramientas de linter) que no hacen falta dentro del contenedor de producción.
### CMD
Es el comando que se ejecuta automaticamente en cuanto el contenedor arranca. Vamos a ir 1 a 1.
#### uvicorn
Es el servidor web ultrarrápido (escrito en Python) que se encarga de recibir las peticiones HTTP que llegan de fuera (por ejemplo, cuando entras desde tu navegador) y pasárselas a tu código.
#### main:app
Es la instrucción clave para que Uvicorn sepa dónde está tu aplicación web:

- main hace referencia al archivo main.py de tu código.

- app hace referencia a la variable dentro de ese archivo donde has inicializado tu aplicación (por ejemplo, en FastAPI escribes app = FastAPI()). Le dice a Uvicorn: "Arranca el servidor usando la variable app que está dentro del archivo main.py".
#### --host 0.0.0.0
Esta parte es vital para Docker. Si pusieras 127.0.0.1 o localhost, el servidor solo escucharía peticiones que vengan de dentro del propio contenedor, y tu navegador (que está en tu ordenador/WSL) no podría comunicarse con él. Poner 0.0.0.0 le dice a Uvicorn: "Escucha peticiones que vengan de cualquier tarjeta de red externa", permitiendo que el tráfico de Docker llegue hasta tu app.
#### --port 8000
Le indica a Uvicorn que debe encenderse escuchando exactamente en el puerto 8000 (el mismo que luego enlazamos en el docker-compose.yml con 8000:8000).
#### --reload
Es el modo desarrollo definitivo. Hace que Uvicorn se quede "vigilando" tus archivos de Python. Si guardas un cambio en el código mientras programas, el servidor se reinicia solo al vuelo, sin necesidad de apagar y encender el contenedor a mano.

## DEPENDENCIES
Para añadir todos de una:
uv add fastapi uvicorn sqlalchemy "psycopg[binary]"

- fastapi: El framework web ultra rápido para construir APIs en Python con tipado estático y validación automática.

- uvicorn: El servidor ASGI que vimos antes en el Dockerfile, encargado de poner en marcha nuestra aplicación web.

- sqlalchemy: El ORM (Object-Relational Mapper). Es la herramienta que traduce las tablas de tu base de datos PostgreSQL en clases y objetos de Python para que no tengas que escribir consultas SQL crudas a mano.

- psycopg[binary]: El driver o conector oficial de PostgreSQL para Python. Es el puente físico que permite a SQLAlchemy hablar con la base de datos que tenemos corriendo en el otro contenedor de Docker.

## Resumen de lo que ocurre en main.py
Alguien abre el navegador y escribe http://localhost:8000/.

La petición llega al contenedor de Docker, entra por el puerto 8000 y Uvicorn la recoge.

Uvicorn busca en el archivo main.py la variable app.

app mira las rutas registradas con @app.get("/") y dice: "¡Oye, esta ruta encaja con la función read_root!".

Se ejecuta la función, devuelve el diccionario, FastAPI lo transforma en JSON, y el navegador recibe el mensaje "¡Hola desde el backend de ft-transcendence!"

## GUIA DE USO
docker compose up --build

### Comandos para ver el resultado
curl http://localhost:8000/

O puedes ir directamente al buscador y buscar http://localhost:8000/

FastAPI genera automaticamente una interfaz gráfica interactiva. Para verla: http://localhost:8000/docs

## ARCHIVOS
Pequeñas aclaraciones para la lógica de archivos importantes
### DATABASE.PY
Tenemos la constante con la ruta de la base de datos, que consiste basicamente en: postgresql indica que la base de datos la maneja postgre, transcende_user es el usuario que se va a conectar, transcendence_password es la contraseña de este usuario, se va a conectar a la base de datos que está en el contenedor db, a través del puerto 5432, a la base de datos llamada transcendence_db. Eso es lo que he entendido de esa variable, que es un poco la misma lógica que usamos en el Docker.

Después, engine es la conexión entre la aplicación y el contenedor, es decir, la conexión con la base de datos.

Después, SessionLocal es el concepto de una sesión, un usuario conectándose. Hemos especificado que los cambios no serán confirmados automaticamente, y lo hemos enlazado con la conexión entre la aplicación y el contendor (engine)

Y la variable Base es como la traducción de las clases que nosotros hagamos (deduzco que heredando de ella) a tablas para PostgreSQL.

Por último, la función get_db devuelve una sesión para conectarse a la base de datos, y ahí poder interactuar con ella.

**Corrección**: Sobre SessionLocal: No representa exactamente a "un usuario conectándose", sino más bien a una mesa de trabajo temporal (o un ticket de transacción) que se abre para una tarea concreta. Un mismo usuario que entre a la web puede abrir varias sesiones distintas a lo largo de su navegación (por ejemplo, una sesión para registrarse, otra para enviar un mensaje y otra para actualizar su avatar). Es simplemente el espacio de trabajo aislado donde hacemos operaciones antes de guardarlas definitivamente.

### MODELS.PY
Los distintos modelos de las tablas de la base de datos

### MAIN.PY
#### Depends
Función que automatiza la apertura de la conexión del usuario con la base de datos, garantizando que ocurra lo que ocurra, todo se gestione correctamente.

## ALEMBIC
Gestiona modificaciones en las tablas de SQL. Genera migraciones (cambios en las tablas para no perder los datos ya existentes). El nombre de la carpeta y el .ini que lo gestiona es migrations/ y alembic.ini
### alembic.ini
Donde pone "*here*" es lo mismo que la ruta donde está el *.ini*.
Los archivos generados por alembic indican los cambios que se han realizado en las tablas.
### env.py
Todo ese archivo es generado por el comando alembic init *name*. Hay que modificar ciertas cosas para que se adapte a nuestra versión.
#### Librerías estandar
- fileConfig: lee la parte de logging del alembic.ini (qué mensajes se muestran por la terminal). Ya venía en la plantilla.
#### Librerías externas
- context: el objeto de Alembic a través del cual le das la configuración y le dices "ejecuta las migraciones". Ya venía en la plantilla.
- create_engine: Como en database.py para crear la conexión. Sustituye a engine_from_config de la plantilla, que leía la URL del .ini.
- pool: de aquí sacaremos NullPool
#### Librerías internas (código)
- settings: de aquí sale la URL de la base de datos.
- Base: de aquí sale "cómo deberían ser las tablas".
- models: parece que no se usa, pero es imprescindible. Una clase como User solo se registra en Base cuando se ejecuta su archivo, es decir, cuando se importa. Si nadie importa models.py, Alembic ve un Base vacío, cree que no quieres ninguna tabla y genera una migración que las borra todas. El *noqa: F401* le dice al linter "sé que este import parece sin usar, no lo marques". El resto del comentario explica a quien lo lea por qué está ahí.
### Comandos
```bash
alembic upgrade head --sql
```
Para ver los cambios que se aplicarían sin aplicarlos de verdad (gracias a la función **run_migrations_offline**, de *env.py*)
Ejecutarlo sin --sql es el modo online, y por lo tanto se aplicaría.

```bash
alembic revision --autogenerate -m "create users table"
```

(El mensaje descriptivo porfa :D)

Explicación por partes:
- alembic revision: Crea un archivo de migración nuevo.
- --autogenerate: Rellena el archivo comparando tus modelos con la base de datos.
- -m "message": El mensaje, que daemás forma parte del nombre del archivo.

## Comandos Docker generales
Cómo ejecutar los comandos en este proyecto. Los comandos de esta guía se ejecutan dentro del contenedor, anteponiendo docker compose exec backend. Por ejemplo, alembic current se escribe docker compose exec backend alembic current. Si el comando crea archivos en tu carpeta (como alembic revision), añade --user $(id -u):$(id -g) para que los archivos sean tuyos y no de root.

Tabla con mejores explicaciones que las mías :(:
| Comando | Qué hace |
|---|---|
| `docker compose exec --user $(id -u):$(id -g) backend alembic revision --autogenerate -m "mensaje"` | **Crea** el archivo de migración comparando los modelos con la base. No toca la base. El `--user` hace que el archivo sea tuyo y no de root. |
| `docker compose exec backend alembic history` | Lista las migraciones que Alembic ve, en orden. |
| `docker compose exec backend alembic current` | Dice en qué migración está la base de datos ahora. |
| `docker compose exec backend alembic upgrade head --sql` | Muestra el SQL que se ejecutaría, sin aplicarlo (modo offline). |
| `docker compose exec backend alembic upgrade head` | **Aplica** las migraciones pendientes a la base de datos (modo online). |
| `docker compose exec backend alembic downgrade -1` | Deshace la última migración. |

Comando para entrar en la base de datos:
```bash
docker compose exec db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```
Comandos útiles una vez estás dentro:
- \dt: Lista las tablas de la base de datos.
- \d *users*: Describe una tabla, en este caso, *users*
- SELECT * FROM users: Muestra las filas (los datos) de la tabla, en este caso, de *users*
- \q: Salir de psql

La diferencia entre el parámetro *default* y *server_default* en las tablas es que *default* **no acepta parámetro por defecto**
si la inserción es directamente desde SQL, y *server_default* **sí permite no dar esos valores** para rellenarlos con el valor
por defecto.

#### Retroceder y avanzar migraciones

Se ejecutan dentro del contenedor, desde cualquier carpeta del proyecto.

| Comando | Qué hace |
|---|---|
| `docker compose exec backend alembic current` | Dice en qué migración está la base de datos ahora. Sin salida = base vacía (sin migraciones aplicadas). |
| `docker compose exec backend alembic downgrade -1` | Deshace **una** migración (ejecuta su `downgrade()`). |
| `docker compose exec backend alembic upgrade +1` | Aplica **una** migración pendiente. |
| `docker compose exec backend alembic upgrade head` | Aplica **todas** las migraciones pendientes hasta la última. |

### Pendiente
1. **Automatizar** los comandos de Alembic (Makefile o script con subcomandos). Hacerlo ya sabiendo lo que hace cada comando.