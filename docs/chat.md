# Chat

## Idea general

Logica del chat en Python. Guarda chats privados, grupos, expulsiones y bloqueos. De momento **no depende de la base de datos ni del login**: todo se guarda en memoria y se borra al parar el programa.

Se puede probar un chat privado entre dos usuarios desde la terminal. Todavía faltan las reglas: por ejemplo, alguien bloqueado aún puede escribir.

## Qué hace cada archivo

### `backend/app/chat/`: la logica

Aqui está todo lo del chat. Por ahora, cuando lo probamos en la terminal solo se usan `constants.py`, `domain.py` y `memory.py`.

- `__init__.py` está vacío. Solo sirve para que Python pueda importar la carpeta.
- `constants.py` tiene los límites, como lo largo que puede ser un mensaje.
- `domain.py` explica qué es un chat, un miembro, un mensaje y un bloqueo.
- `repository.py` es la lista de lo que el chat necesita guardar y leer. No hace nada por sí solo.
- `memory.py` es el que guarda las cosas de verdad, en diccionarios. Más adelante se cambiará por la base de datos.
- `schemas.py` comprueba que lo que nos mandan está bien, por ejemplo que el mensaje no esté vacío.
- `dependencies.py` dice quién eres. Los usuarios son inventados hasta que tengamos el login.
- `router.py` tiene las rutas de la API: ver tus chats, abrir uno privado, crear grupos, añadir y expulsar gente, leer y enviar mensajes, y bloquear y desbloquear. Todavía no está conectado a `main.py`, y es mejor no hacerlo hasta que haya login de verdad, porque cualquiera podría hacerse pasar por otro.

### `backend/`: para probarlo

Hay dos archivos que son solo para eso:

- `chat_server.py` recibe los mensajes, los guarda y se los pasa al otro.
- `chat_terminal.py` es cada persona que chatea. Te pregunta quién eres y con quién quieres hablar.

## Cómo probarlo

No hace falta Docker ni instalar nada, solo Linux y Python 3.10 o más nuevo. Abre tres terminales y en todas entra en la carpeta:

```bash
cd backend
```

En la primera arranca el servidor y déjala abierta:

```bash
python3 chat_server.py
```

En las otras dos abre el chat:

```bash
python3 chat_terminal.py
```

En una di que eres `albondiga` y que quieres hablar con `pepe`, y en la otra al revés. Lo que escribas en una aparece en la otra.

También puedes probar a:

- Escribir cuando el otro no está. Al entrar verá el mensaje.
- Salir y volver a entrar. Los mensajes siguen ahí.
- Entrar dos veces con el mismo usuario. No te deja.

Para salir escribe `salir`, y para parar el servidor pulsa `Ctrl+C`.

Si te dice que el servidor no está en marcha, arranca antes `chat_server.py`. Los usuarios tienen que tener al menos 3 letras.

## Qué falta

- Las reglas de quién puede escribir, expulsar y bloquear.
- El chat en tiempo real en la web, con WebSockets.
- Guardarlo en la base de datos.
- El login de verdad.
- ...
