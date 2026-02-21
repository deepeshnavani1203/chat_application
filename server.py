import socket
import threading
import random
from datetime import datetime
import os
import struct

HOST = "0.0.0.0"
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
admin_conn = None

COLORS = ["\033[91m", "\033[92m", "\033[93m", "\033[94m", "\033[95m", "\033[96m"]
RESET = "\033[0m"

server_ip = socket.gethostbyname(socket.gethostname())
admin_assigned = False


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


def receive_file(conn, sender):
    filename = conn.recv(1024).decode()
    filesize = struct.unpack("!I", conn.recv(4))[0]

    data = b""
    while len(data) < filesize:
        data += conn.recv(4096)

    with open("received_" + filename, "wb") as f:
        f.write(data)

    for c in clients:
        if c != conn and user_room.get(c) == user_room.get(conn):
            try:
                c.send(b"FILE")
                c.send(filename.encode())
                c.send(struct.pack("!I", filesize))
                c.send(data)
            except:
                pass

    broadcast(f"{sender} sent file {filename}\n", user_room[conn], conn)


def handle_client(conn, addr):

    global admin_conn
    global admin_assigned

    print("Connected:", addr)

    username = conn.recv(1024).decode()
    color = random.choice(COLORS)
    usernames[conn] = f"{color}{username}{RESET}"
    user_room[conn] = "general"

    # 👑 ADMIN LOGIC
    if addr[0] == server_ip and not admin_assigned:
        admin_conn = conn
        admin_assigned = True
        conn.send("You are ADMIN\n".encode())

    if "general" not in rooms:
        rooms["general"] = []
    rooms["general"].append(conn)

    send_history(conn)
    broadcast(f"{username} joined chat\n", "general")

    while True:
        try:
            msg = conn.recv(1024).decode()

            if not msg:
                break

            if msg.startswith("/"):
                parts = msg.split(" ", 2)
                cmd = parts[0]

                if cmd == "/users":
                    u = ", ".join([n[5:-4] for n in usernames.values()])
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
                    broadcast(f"{username} is typing...\n", user_room[conn], conn)

                elif cmd == "/kick":
                    if conn != admin_conn:
                        conn.send("Only Server Admin can kick\n".encode())
                        continue
                    target = parts[1]
                    for c, u in usernames.items():
                        if target in u:
                            c.send("You were kicked!\n".encode())
                            c.close()

                elif cmd == "/mute":
                    if conn != admin_conn:
                        conn.send("Only Server Admin can mute\n".encode())
                        continue
                    target = parts[1]
                    for c, u in usernames.items():
                        if target in u:
                            muted.add(c)

                elif cmd == "/sendfile":
                    room = user_room.get(conn)
                    if room is None or room == "general":
                        conn.send("Error: Join a custom room to send file!\n".encode())
                        continue
                    receive_file(conn, username)

                continue

            if conn in muted:
                continue

            formatted = f"[{timestamp()}] {usernames[conn]}: {msg}"
            history.append(formatted)
            broadcast(formatted + "\n", user_room[conn], conn)

        except:
            break

    clients.remove(conn)
    rooms[user_room[conn]].remove(conn)
    broadcast(f"{username} left chat\n")
    conn.close()


def start():
    print("Server running...")
    while True:
        conn, addr = server.accept()
        clients.append(conn)
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


start()
