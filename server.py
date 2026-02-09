import socket
import threading
import random
from datetime import datetime
import os

HOST = "127.0.0.1"
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
usernames = {}
rooms = {}
user_room = {}
muted = set()
history = []

ADMIN = "admin"  # first user can login as admin

COLORS = ["\033[91m", "\033[92m", "\033[93m", "\033[94m", "\033[95m", "\033[96m"]
RESET = "\033[0m"


def timestamp():
    return datetime.now().strftime("%H:%M")


def broadcast(msg, room=None, exclude=None):
    for c in clients:
        if c != exclude:
            if room is None or user_room.get(c) == room:
                try:
                    c.send(msg.encode())
                except:
                    pass


def send_history(conn):
    conn.send("\n--- Chat History ---\n".encode())
    for m in history[-20:]:
        conn.send((m + "\n").encode())


def handle_client(conn, addr):
    print("Connected:", addr)

    # USERNAME
    username = conn.recv(1024).decode()
    color = random.choice(COLORS)
    usernames[conn] = f"{color}{username}{RESET}"
    user_room[conn] = "general"

    if "general" not in rooms:
        rooms["general"] = []
    rooms["general"].append(conn)

    send_history(conn)

    broadcast(f"{username} joined chat", "general")

    while True:
        try:
            msg = conn.recv(1024).decode()

            if not msg:
                break

            # COMMANDS
            if msg.startswith("/"):
                parts = msg.split(" ", 2)
                cmd = parts[0]

                if cmd == "/users":
                    u = ", ".join(
                        [name for name in [n[5:-4] for n in usernames.values()]]
                    )
                    conn.send(f"Online: {u}\n".encode())

                elif cmd == "/msg":
                    target = parts[1]
                    text = parts[2]

                    for c, u in usernames.items():
                        if target in u:
                            c.send(f"[DM]{username}: {text}\n".encode())

                elif cmd == "/join":
                    room = parts[1]

                    old = user_room[conn]
                    rooms[old].remove(conn)

                    if room not in rooms:
                        rooms[room] = []
                    rooms[room].append(conn)

                    user_room[conn] = room
                    conn.send(f"Joined room {room}\n".encode())

                elif cmd == "/typing":
                    broadcast(
                        f"{username} is typing...",
                        user_room[conn],
                        conn,
                    )

                elif cmd == "/kick" and username == ADMIN:
                    target = parts[1]
                    for c, u in usernames.items():
                        if target in u:
                            c.send("You were kicked!\n".encode())
                            c.close()

                elif cmd == "/mute" and username == ADMIN:
                    target = parts[1]
                    for c, u in usernames.items():
                        if target in u:
                            muted.add(c)

                elif cmd == "/sendfile":
                    filename = parts[1]
                    if os.path.exists(filename):
                        conn.send("FILE".encode())
                        with open(filename, "rb") as f:
                            conn.send(f.read())

                continue

            # MUTED CHECK
            if conn in muted:
                continue

            # NORMAL MESSAGE
            formatted = f"[{timestamp()}] {usernames[conn]}: {msg}"
            history.append(formatted)

            broadcast(formatted, user_room[conn], conn)

        except:
            break

    # DISCONNECT
    clients.remove(conn)
    rooms[user_room[conn]].remove(conn)
    broadcast(f"{username} left chat")
    conn.close()


def start():
    print("Server running...")

    while True:
        conn, addr = server.accept()
        clients.append(conn)

        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


start()
