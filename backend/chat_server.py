"""
Server to try the chat from several terminals. Development only.

    python3 chat_server.py

The terminals connect to it through a Unix socket: a special file that two
programs of the same computer use to talk. Everything is sent as JSON, one
object per line.
"""

import asyncio
import json
import os
import socket
import sys
from asyncio import StreamReader, StreamWriter
from pathlib import Path
from tempfile import gettempdir

from app.chat.constants import MESSAGE_MAX_LEN
from app.chat.memory import MemoryChatRepository
from app.core.constants import USERNAME_MAX_LEN, USERNAME_MIN_LEN


SOCKET_PATH = Path(gettempdir()) / f"transcendence_chat_{os.getuid()}.sock"


def send(writer: StreamWriter, data: dict) -> None:
    writer.write(json.dumps(data).encode() + b"\n")


async def receive(reader: StreamReader) -> dict | None:
    """The next object, or None if there are no more or it is not valid."""
    try:
        data = json.loads(await reader.readline())
    except (ConnectionError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def username_error(name: object) -> str | None:
    """Why the username is not valid, or None if it is."""
    if not isinstance(name, str) or not name.isidentifier():
        return "usa solo letras, números y _, sin empezar por un número"
    if not USERNAME_MIN_LEN <= len(name) <= USERNAME_MAX_LEN:
        return f"debe tener entre {USERNAME_MIN_LEN} y " \
               f"{USERNAME_MAX_LEN} caracteres"
    return None


class ChatServer:
    def __init__(self) -> None:
        self.repo = MemoryChatRepository()
        self.user_ids: dict[str, int] = {}
        """username -> id. TEMPORARY, until there are real users"""
        self.online: dict[int, tuple[int, StreamWriter]] = {}
        """user id -> the conversation it has open and its connection"""

    def user_id(self, name: str) -> int:
        """The id of the user, a new one the first time it appears."""
        return self.user_ids.setdefault(name, len(self.user_ids) + 1)

    def login_error(self, me: object, other: object) -> str | None:
        for name in (me, other):
            error = username_error(name)
            if error:
                return f"Usuario no válido: {error}"
        if me == other:
            return "No puedes hablar contigo"
        if self.user_ids.get(str(me)) in self.online:
            return f"{me} ya está conectado"
        return None

    async def handle(self, reader: StreamReader,
                     writer: StreamWriter) -> None:
        """Runs once for each terminal, until it disconnects."""
        try:
            login = await receive(reader)
            if login is None:
                return
            me, other = login.get("me"), login.get("other")
            error = self.login_error(me, other)
            if error:
                send(writer, {"error": error})
                return
            await self.talk(me, other, reader, writer)
        finally:
            writer.close()

    async def talk(self, me: str, other: str, reader: StreamReader,
                   writer: StreamWriter) -> None:
        my_id, other_id = self.user_id(me), self.user_id(other)
        chat = self.repo.get_or_create_direct(my_id, other_id)
        names = {my_id: me, other_id: other}

        self.online[my_id] = (chat.id, writer)
        print(f"{me} entra a hablar con {other}")
        try:
            history = self.repo.list_messages(chat.id, limit=100)
            send(writer, {"history": [{"from": names[m.sender_id],
                                       "text": m.content} for m in history]})

            while (data := await receive(reader)) is not None:
                self.new_message(chat.id, my_id, other_id, names,
                                 data.get("text"), writer)
        finally:
            del self.online[my_id]
            print(f"{me} sale")

    def new_message(self, chat_id: int, my_id: int, other_id: int,
                    names: dict[int, str], text: object,
                    writer: StreamWriter) -> None:
        text = text.strip() if isinstance(text, str) else ""
        if not text:
            return
        if len(text) > MESSAGE_MAX_LEN:
            send(writer, {"info": "No enviado: el máximo es de "
                                  f"{MESSAGE_MAX_LEN} caracteres"})
            return
        message = self.repo.add_message(chat_id, my_id, text)

        open_chat, other_writer = self.online.get(other_id, (None, None))
        if other_writer is not None and open_chat == chat_id:
            send(other_writer, {"from": names[my_id],
                                "text": message.content})
        else:
            send(writer, {"info": f"{names[other_id]} no está en el chat, "
                                  "lo verá cuando entre"})


def is_running() -> bool:
    with socket.socket(socket.AF_UNIX) as test:
        return test.connect_ex(str(SOCKET_PATH)) == 0


async def main() -> None:
    server = await asyncio.start_unix_server(ChatServer().handle,
                                             path=SOCKET_PATH)
    print("Servidor del chat en marcha. Ctrl+C para pararlo.")
    try:
        await asyncio.Event().wait()
    finally:
        server.close()
        SOCKET_PATH.unlink(missing_ok=True)


if __name__ == "__main__":
    if is_running():
        sys.exit("El servidor ya está en marcha en otra terminal.")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServidor parado.")
