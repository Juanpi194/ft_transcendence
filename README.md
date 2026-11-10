<!--->TODO: La estructura del README<!--->
# FT_TRANSCENDENCE
Aquí encontrarás explicaciones de conceptos

## DOCKER-COMPOSE
Las palabras *db* y *backend* no son palabras clave, son los nombres que le estamos dando a los contenedores. Podemos poner lo que queramos.
### image
postgres:15-alpine
La más eficiente en la actualidad. 15 es la versión y alpine el sistema operativo que acompaña a Postgres por dentro. Si no ponemos nada se usa la latest
### environment
Las variables de entorno obligatorias que la imagen oficial de PostgreSQL necesita para encenderese por primera vez.
### ports
El de la izquierda es por el que escucha la máquina, el de la derecha es el del contenedor.
### build
En nuestro caso, el contenedor no se crea a través de una imagen, el backend va a ser nuestro propio código de Python. En esa ruta habrá un Dockerfile y se construirá la imagen con las instrucciones de ese Dockerfile.
### depends_on
El contenedor que dependa de otro no arrancará HASTA QUE el contenedor al que hace referencia no arranque. Si del que hace depende no arranca, este tampoco arrancará. En nuestro caso, *backend* no arrancará si *db* no arranca.
### environment
No lo entiendo la verdad.
- **Mi manera de entenderlo**:
Es como una especie de login en la página postgresql, concretamente al servidor db. Una vez nos hemos logeado, tendríamos que indicarle a qué base de datos concreta queremos conectarnos, que en este caso es transcendence_db.
- **Explicación de GEMINI**:
Es como abrir la puerta del "edificio" de PostgreSQL usando tus llaves (usuario y contraseña), entrar al servidor que está en db:5432, y sentarte directamente en la mesa de trabajo (la base de datos) llamada transcendence_db

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