<!--->TODO: La estructura del README<!--->
# FT_TRANSCENDENCE
Aquí encontrarás explicaciones de conceptos

## 🎯 MÓDULOS Y PUNTOS
> Para aprobar hacen falta **14 puntos**. Los módulos extra cuentan como bonus hasta un **máximo de 5 puntos** (14 + 5 = **19** puntos contables). Nuestra lista tiene **30 puntos** candidatos, así que tenemos margen por si algún módulo no se valida en la evaluación (módulo incompleto = 0 puntos).

**Major = 2 pts** · **Minor = 1 pt**

| #  | Categoría                          | Módulo                                                              | Tipo  | Pts   | Estado |
|----|------------------------------------|---------------------------------------------------------------------|:-----:|:-----:|:------:|
| 1  | 🌐 Web                             | 🧱 Use a framework for both the frontend and backend ¹              | Major | **2** | ⬜ |
| 2  | 🌐 Web                             | ⚡ Implement real-time features using WebSockets or similar technology | Major | **2** | ⬜ |
| 3  | 🌐 Web                             | 💬 Allow users to interact with other users (chat, profile, friends) | Major | **2** | ⬜ |
| 4  | 🌐 Web                             | 🔌 A public API to interact with the database                       | Major | **2** | ⬜ |
| 5  | 🌐 Web                             | 🗄️ Use an ORM for the database                                      | Minor | **1** | ⬜ |
| 6  | 🌐 Web                             | 🎨 Real-time collaborative features (r/place)                       | Minor | **1** | ⬜ |
| 7  | 🌐 Web                             | 🌈 Custom-made design system with reusable components               | Minor | **1** | ⬜ |
| 8  | 🌐 Web                             | 🔎 Advanced search functionality with filters, sorting and pagination | Minor | **1** | ⬜ |
| 9  | 🌐 Web                             | 📁 File upload and management system                                | Minor | **1** | ⬜ |
| 10 | ♿ Accessibility & Internationalization | 🌍 Support for multiple languages (at least 3)                  | Minor | **1** | ⬜ |
| 11 | ♿ Accessibility & Internationalization | 🧭 Support for additional browsers                              | Minor | **1** | ⬜ |
| 12 | 👤 User Management                 | 👥 Standard user management and authentication                      | Major | **2** | ⬜ |
| 13 | 👤 User Management                 | 🪪 Remote authentication with OAuth 2.0 (42)                        | Minor | **1** | ⬜ |
| 14 | 👤 User Management                 | 🔐 Advanced permissions system                                      | Major | **2** | ⬜ |
| 15 | 👤 User Management                 | 🏢 An organization system                                           | Major | **2** | ⬜ |
| 16 | 🤖 Artificial Intelligence         | 🛑 Content moderation AI                                            | Minor | **1** | ⬜ |
| 17 | 🛡️ Cybersecurity                   | 🔥 WAF/ModSecurity (hardened) + HashiCorp Vault for secrets         | Major | **2** | ⬜ |
| 18 | 🎮 Gaming & user experience        | 💭 Advanced chat features ²                                         | Minor | **1** | ⬜ |
| 19 | 🚀 DevOps                          | 📊 Monitoring system with Prometheus and Grafana                    | Major | **2** | ⬜ |
| 20 | 📈 Data & Analytics                | 📤 Data export and import functionality                             | Minor | **1** | ⬜ |
| 21 | 📈 Data & Analytics                | 📜 GDPR compliance features                                         | Minor | **1** | ⬜ |

¹ O bien los dos Minor: *Use a frontend framework* + *Use a backend framework* (también suman 2 pts).
² Requiere tener implementado antes el chat básico (módulo 3).

### Resumen
| Concepto                                   | Puntos |
|--------------------------------------------|:------:|
| Majors (9 × 2)                             | 18     |
| Minors (12 × 1)                            | 12     |
| **Total candidato**                        | **30** |
| Mínimo para aprobar                        | 14     |
| Máximo contable (14 + 5 de bonus)          | 19     |
| **Margen sobre el mínimo**                 | **16** |

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