import socket, struct, threading, uuid

HOST = "0.0.0.0"
CHAT_PORT = 12345
FILE_PORT = 12346

clients = {}
user_rooms = {}
admin = None
lock = threading.Lock()

pending_transfers = {}
pending_lock = threading.Lock()


def recv_exact(sock, n):
    buf = b""
    while len(buf) < n:
        c = sock.recv(n - len(buf))
        if not c:
            raise ConnectionError("closed")
        buf += c
    return buf


def recv_str(sock):
    n = struct.unpack("!H", recv_exact(sock, 2))[0]
    return recv_exact(sock, n).decode()


def send_str(sock, text):
    b = text.encode()
    sock.sendall(struct.pack("!H", len(b)) + b)


def safe_send(sock, data: bytes):
    try:
        sock.sendall(data)
    except Exception:
        pass


def send_msg(sock, text: str):
    safe_send(sock, text.encode())


def broadcast(text: str, room: str, exclude=None):
    data = text.encode()
    with lock:
        targets = [
            c for u, c in clients.items() if u != exclude and user_rooms.get(u) == room
        ]
    for c in targets:
        safe_send(c, data)


def send_dm(text: str, target_user: str):
    with lock:
        sock = clients.get(target_user)
    if sock:
        safe_send(sock, text.encode())
        return True
    return False


def kick_user(target: str):
    with lock:
        sock = clients.get(target)
    if sock:
        try:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        except Exception:
            pass
        return True
    return False


def handle_chat_client(conn, addr):
    global admin
    username = None
    try:
        username = recv_str(conn)

        with lock:
            if not clients:
                admin = username
            clients[username] = conn
            user_rooms[username] = "general"

        is_admin = username == admin
        print(f"[+] {username!r} connected from {addr} {'[ADMIN]' if is_admin else ''}")

        broadcast(
            f"\n[general] {username} joined the chat.\n", "general", exclude=username
        )

        welcome = f"Connected as {username}. Room: general\n"
        welcome += "You are admin.\n" if is_admin else ""
        welcome += (
            "Commands: /join <room>  /who  /rooms  /dm <user> <msg>  /sendfile  /quit\n"
        )
        welcome += "/kick <user>  (admin only)\n" if is_admin else ""
        send_msg(conn, welcome)

        while True:
            length = struct.unpack("!H", recv_exact(conn, 2))[0]
            msg = recv_exact(conn, length).decode().strip()
            if not msg:
                continue

            current_room = user_rooms.get(username, "general")

            if msg.startswith("/join "):
                new_room = msg[6:].strip()
                if not new_room:
                    send_msg(conn, "Usage: /join <roomname>\n")
                    continue
                broadcast(
                    f"\n[{current_room}] {username} has left.\n",
                    current_room,
                    exclude=username,
                )
                with lock:
                    user_rooms[username] = new_room
                broadcast(
                    f"\n[{new_room}] {username} joined.\n", new_room, exclude=username
                )
                send_msg(conn, f"Switched to room '{new_room}'.\n")

            elif msg == "/who":
                with lock:
                    members = [u for u, r in user_rooms.items() if r == current_room]
                send_msg(conn, f"Users in '{current_room}': {', '.join(members)}\n")

            elif msg == "/rooms":
                with lock:
                    rooms = sorted(set(user_rooms.values()))
                send_msg(conn, f"Active rooms: {', '.join(rooms)}\n")

            elif msg.startswith("/dm "):
                parts = msg[4:].split(" ", 1)
                if len(parts) < 2 or not parts[1].strip():
                    send_msg(conn, "Usage: /dm <username> <message>\n")
                    continue
                target, dm_text = parts[0].strip(), parts[1].strip()
                with lock:
                    exists = target in clients
                if not exists:
                    send_msg(conn, f"User '{target}' not found.\n")
                elif target == username:
                    send_msg(conn, "You can't DM yourself.\n")
                else:
                    send_dm(f"\n[DM from {username}]: {dm_text}\n", target)
                    send_msg(conn, f"[DM to {target}]: {dm_text}\n")

            elif msg.startswith("/kick "):
                if username != admin:
                    send_msg(conn, "Only the admin can kick users.\n")
                    continue
                target = msg[6:].strip()
                if target == username:
                    send_msg(conn, "You can't kick yourself.\n")
                    continue
                with lock:
                    exists = target in clients
                if not exists:
                    send_msg(conn, f"User '{target}' not found.\n")
                else:
                    send_dm("\nYou have been kicked by the admin.\n", target)
                    target_room = user_rooms.get(target, "general")
                    kick_user(target)
                    broadcast(
                        f"\n[{target_room}] {target} was kicked by admin.\n",
                        target_room,
                    )
                    send_msg(conn, f"{target} has been kicked.\n")
                    print(f"[KICK] {username!r} kicked {target!r}")

            else:
                broadcast(
                    f"[{current_room}] {username}: {msg}",
                    current_room,
                    exclude=username,
                )

    except Exception as e:
        print(f"[!] Chat error ({username}): {e}")
    finally:
        if username:
            gone_room = user_rooms.pop(username, "general")
            with lock:
                clients.pop(username, None)
                if username == admin and clients:
                    admin = next(iter(clients))
                    send_dm("You are now the admin.\n", admin)
                    print(f"[ADMIN] Promoted {admin!r}")
            broadcast(f"\n[{gone_room}] {username} disconnected.\n", gone_room)
            print(f"[-] {username!r} disconnected")
        try:
            conn.close()
        except Exception:
            pass


def handle_file_connection(conn, addr):
    try:
        tag = recv_exact(conn, 1)

        if tag == b"S":
            sender = recv_str(conn)
            room = recv_str(conn)
            filename = recv_str(conn)
            filesize = struct.unpack("!I", recv_exact(conn, 4))[0]

            print(f"[FILE] {sender!r} -> '{filename}' ({filesize}B) room={room!r}")

            if room.lower() == "general":
                conn.sendall(b"NO")
                return

            conn.sendall(b"OK")
            file_data = recv_exact(conn, filesize)
            print(f"[FILE] Buffered '{filename}' from {sender!r}")

            with lock:
                targets = {
                    u: c
                    for u, c in clients.items()
                    if user_rooms.get(u) == room and u != sender
                }

            if not targets:
                print(f"[FILE] No targets in '{room}' for '{filename}'")
                return

            tid = str(uuid.uuid4())
            events = {u: threading.Event() for u in targets}
            with pending_lock:
                pending_transfers[tid] = {
                    "data": file_data,
                    "filename": filename,
                    "sender": sender,
                    "filesize": filesize,
                    "events": events,
                    "responses": {},
                }

            tid_b = tid.encode()
            sender_b = sender.encode()
            fname_b = filename.encode()
            offer = (
                b"FILE_OFFER"
                + struct.pack("!H", len(tid_b))
                + tid_b
                + struct.pack("!H", len(sender_b))
                + sender_b
                + struct.pack("!H", len(fname_b))
                + fname_b
                + struct.pack("!I", filesize)
            )
            for uname, chat_conn in targets.items():
                safe_send(chat_conn, offer)

            for uname, evt in events.items():
                evt.wait(timeout=120)

            with pending_lock:
                record = pending_transfers.pop(tid, {})

            for uname, accepted in record.get("responses", {}).items():
                chat_conn = targets.get(uname)
                if not chat_conn:
                    continue
                if accepted:
                    fname_b = filename.encode()
                    fhdr = (
                        b"FILEDATA"
                        + struct.pack("!H", len(fname_b))
                        + fname_b
                        + struct.pack("!I", len(file_data))
                    )
                    safe_send(chat_conn, fhdr)
                    safe_send(chat_conn, file_data)
                    print(f"[FILE] Delivered '{filename}' -> {uname!r}")
                else:
                    print(f"[FILE] {uname!r} rejected '{filename}'")

        elif tag == b"R":
            tid = recv_str(conn)
            username = recv_str(conn)
            decision = recv_exact(conn, 1)
            with pending_lock:
                record = pending_transfers.get(tid)
            if record:
                record["responses"][username] = decision == b"Y"
                evt = record["events"].get(username)
                if evt:
                    evt.set()
                print(
                    f"[FILE] {username!r} {'ACCEPTED' if decision == b'Y' else 'REJECTED'} {tid[:8]}"
                )
            else:
                print(f"[FILE] Unknown tid from {username!r}")

    except Exception as e:
        print(f"[FILE] Error from {addr}: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass


def accept_chat():
    while True:
        conn, addr = chat_server.accept()
        threading.Thread(
            target=handle_chat_client, args=(conn, addr), daemon=True
        ).start()


def accept_files():
    while True:
        conn, addr = file_server.accept()
        threading.Thread(
            target=handle_file_connection, args=(conn, addr), daemon=True
        ).start()


chat_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
chat_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
chat_server.bind((HOST, CHAT_PORT))
chat_server.listen(10)

file_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
file_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
file_server.bind((HOST, FILE_PORT))
file_server.listen(10)

print(f"[SERVER] Chat  -> {HOST}:{CHAT_PORT}")
print(f"[SERVER] Files -> {HOST}:{FILE_PORT}")
print("[SERVER] Ready.\n")

threading.Thread(target=accept_chat, daemon=True).start()
threading.Thread(target=accept_files, daemon=True).start()

try:
    threading.Event().wait()
except KeyboardInterrupt:
    print("\n[SERVER] Shutting down.")
