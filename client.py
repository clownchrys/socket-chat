import socket
import select
import sys
import json
import argparse

from models import Message
from utils import highlight


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', action='store', type=str, required=True)
    parser.add_argument('--port', action='store', type=int, required=True)
    parser.add_argument('--buffer_size', action='store', type=int, default=4096)
    args = parser.parse_args()
    return args


def connect_to_server(host, port) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    return sock


def read_from_socket(sock, buffer_size) -> Message:
    data = sock.recv(buffer_size)
    kwargs = json.loads(data.decode())
    msg = Message(**kwargs)
    return msg


def read_from_stdin(obj, user) -> Message:
    value = obj.readline()
    value = value.replace('\n', '')
    msg = Message(user=user, value=value)
    return msg


def main(args):
    user = 'undefined'
    fmt_display = '{user}: {content} ({datetime})'

    # Connect
    sock = connect_to_server(args.host, args.port)

    # Communicate
    wait_for_read = (sock, sys.stdin)
    wait_for_write = ()
    wait_for_except = ()

    while True:
        objs_read, objs_write, objs_except = select.select(wait_for_read, wait_for_write, wait_for_except)

        for obj in objs_read:

            # Read from message
            if isinstance(obj, socket.socket):
                msg_received = read_from_socket(sock, args.buffer_size)
            else:
                msg_received = read_from_stdin(obj, user)

            # Display in client
            if (msg_received.user == 'initializer') or (msg_received.user == user):
                color = 'green'
            elif msg_received.user == 'SYSTEM':
                color = 'red'
            else:
                color = 'yellow'

            if msg_received.user == 'initializer':
                user = msg_received.value
                display = f"Welcome! {highlight(user, color)}"
            else:
                display = fmt_display.format(
                    user = highlight('you', color) \
                        if (msg_received.user == user) else highlight(msg_received.user, color),
                    content=msg_received.value,
                    datetime=highlight(msg_received.datetime, 'cyan')
                )

            print(display)

            # Send to server
            if msg_received.user == 'initializer':
                msg_send = Message(
                    user='SYSTEM',
                    value=f"{user!r} have entered the room",
                )
            elif msg_received.user == user:
                msg_send = msg_received
            else:
                msg_send = None

            if msg_send:
                sock.send(msg_send.string().encode())


if __name__ == '__main__':
    args = parse_args()
    main(args)
