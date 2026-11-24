"""
One user of the chat. Open one terminal for each user, with the server
(chat_server.py) already running. Development only.

    python3 chat_terminal.py
"""

import json
import readline
import signal
import socket
import sys
from threading import Thread, main_thread
from typing import TextIO

from chat_server import SOCKET_PATH


def clean(text: str) -> str:
    """Without the characters that could control the terminal."""
    return "".join(c if c.isprintable() else " " for c in text)


def send(connection: socket.socket, data: dict) -> None:
    connection.sendall(json.dumps(data).encode() + b"\n")


def login() -> tuple[str, socket.socket, TextIO]:
    """Ask for the users until the server accepts them."""
    while True:
        me = input("Tu usuario: ").strip().lower()
        other = input("¿Con quién quieres hablar?: ").strip().lower()

        connection = socket.socket(socket.AF_UNIX)
        try:
            connection.connect(str(SOCKET_PATH))
        except OSError:
            sys.exit("El servidor no está en marcha: python3 chat_server.py")
        send(connection, {"me": me, "other": other})
        lines = connection.makefile(encoding="utf-8")
        answer = json.loads(lines.readline())

        if "error" not in answer:
            print(f'\nChat con {other}. Escribe "salir" para terminar.')
            for message in answer["history"]:
                print(f"{message['from']}: {clean(message['text'])}")
            return me, connection, lines
        print(f"{answer['error']}\n")
        connection.close()


def show_messages(lines: TextIO, prompt: str) -> None:
    """Runs in another thread, because input() stops the main one."""
    try:
        for line in lines:
            data = json.loads(line)
            if "info" in data:
                text = f"({data['info']})"
            else:
                text = f"{data['from']}: {clean(data['text'])}"
            # Borra la línea, imprime el mensaje y vuelve a escribir lo que
            # el usuario estaba escribiendo
            print(f"\r\033[K{text}\n{prompt}{readline.get_line_buffer()}",
                  end="", flush=True)
    except OSError:
        pass
    print("\r\033[KSe ha cortado la conexión.", flush=True)
    # Es como pulsar Ctrl+C: activa el input() del hilo principal
    signal.pthread_kill(main_thread().ident, signal.SIGINT)


def main() -> None:
    me, connection, lines = login()
    prompt = f"{me}: "
    Thread(target=show_messages, args=(lines, prompt), daemon=True).start()

    while (text := input(prompt).strip()) != "salir":
        if text:
            send(connection, {"text": text})


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError, OSError):
        print()
