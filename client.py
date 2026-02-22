import os, queue, socket, struct, sys, threading
from tkinter import Tk, filedialog

HOST = "10.60.123.34"
CHAT_PORT = 12345
FILE_PORT = 12346

username = ""
room = "general"
chat_sock = None

offer_queue = queue.Queue()


def recv_exact(sock, n):
    buf = b""
    while len(buf) < n:
        c = sock.recv(n - len(buf))
        if not c:
            raise ConnectionError("Socket closed")
        buf += c
    return buf


def send_str(sock, text):
    b = text.encode()
    sock.sendall(struct.pack("!H", len(b)) + b)


def chat_send(msg: str):
    try:
        b = msg.encode()
        chat_sock.sendall(struct.pack("!H", len(b)) + b)
    except Exception as e:
        print(f"[!] Send error: {e}")


def open_file_picker():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    path = filedialog.askopenfilename()
    root.destroy()
    return path


def receive():
    global room
    while True:
        try:
            data = chat_sock.recv(4096)
            if not data:
                print("\n[!] Disconnected from server.")
                break

            if data.startswith(b"FILE_OFFER"):
                off = len(b"FILE_OFFER")

                tl = struct.unpack("!H", data[off : off + 2])[0]
                off += 2
                tid = data[off : off + tl].decode()
                off += tl

                sl = struct.unpack("!H", data[off : off + 2])[0]
                off += 2
                sender = data[off : off + sl].decode()
                off += sl

                fl = struct.unpack("!H", data[off : off + 2])[0]
                off += 2
                fname = data[off : off + fl].decode()
                off += fl

                fsize = struct.unpack("!I", data[off : off + 4])[0]

                offer_queue.put(
                    {"tid": tid, "sender": sender, "filename": fname, "filesize": fsize}
                )

                print(f"\nIncoming file from {sender}")
                print(f"  Name : {fname}")
                print(f"  Size : {fsize:,} bytes")
                print("Type y to accept or n to reject\n")

            elif data.startswith(b"FILEDATA"):
                off = len(b"FILEDATA")

                fl = struct.unpack("!H", data[off : off + 2])[0]
                off += 2
                fname = data[off : off + fl].decode()
                off += fl
                filesize = struct.unpack("!I", data[off : off + 4])[0]
                off += 4

                already = data[off:]
                remaining = filesize - len(already)
                buf = bytearray(already)

                while remaining > 0:
                    chunk = chat_sock.recv(min(4096, remaining))
                    if not chunk:
                        break
                    buf += chunk
                    remaining -= len(chunk)
                    print(
                        f"  Receiving... {int(len(buf)/filesize*100)}%",
                        end="\r",
                        flush=True,
                    )

                save = "received_" + fname
                with open(save, "wb") as f:
                    f.write(buf)
                print(f"\n  File saved as '{save}'\n")

            else:
                text = data.decode(errors="replace")
                print(text, end="" if text.endswith("\n") else "\n")

        except Exception as e:
            print(f"\n[!] Receive error: {e}")
            break


def send_file(filepath):
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    try:
        fsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fsock.connect((HOST, FILE_PORT))
        fsock.sendall(b"S")
        send_str(fsock, username)
        send_str(fsock, room)
        send_str(fsock, filename)
        fsock.sendall(struct.pack("!I", filesize))

        reply = fsock.recv(2)
        if reply == b"NO":
            print("File transfers are not allowed in the general room.\n")
            fsock.close()
            return

        sent = 0
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                fsock.sendall(chunk)
                sent += len(chunk)
                print(f"  Sending... {int(sent/filesize*100)}%", end="\r", flush=True)
        print(f"\n  '{filename}' sent.\n")
        fsock.close()
    except Exception as e:
        print(f"[!] File send error: {e}")


def respond_to_offer(offer, accept: bool):
    try:
        rsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        rsock.connect((HOST, FILE_PORT))
        rsock.sendall(b"R")
        send_str(rsock, offer["tid"])
        send_str(rsock, username)
        rsock.sendall(b"Y" if accept else b"N")
        rsock.close()
        if accept:
            print(f"  Accepted - waiting for '{offer['filename']}'\n")
        else:
            print(f"  Rejected '{offer['filename']}'\n")
    except Exception as e:
        print(f"[!] Response error: {e}")


def input_loop():
    global room

    pending_offer = None

    print("Commands: /join <room>  /dm <user> <msg>  /who  /rooms  /sendfile  /quit")
    print("Admin: /kick <user>")
    print("When a file arrives, type y or n\n")

    while True:
        if pending_offer is None:
            try:
                pending_offer = offer_queue.get_nowait()
                print(
                    f"\n  Pending offer: '{pending_offer['filename']}' from {pending_offer['sender']}"
                )
                print("  Type y or n then Enter\n")
            except queue.Empty:
                pass

        try:
            line = input()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        line = line.strip()

        if pending_offer:
            if line.lower() in ("y", "yes", "/accept"):
                threading.Thread(
                    target=respond_to_offer, args=(pending_offer, True), daemon=True
                ).start()
                pending_offer = None
                continue
            elif line.lower() in ("n", "no", "/reject"):
                threading.Thread(
                    target=respond_to_offer, args=(pending_offer, False), daemon=True
                ).start()
                pending_offer = None
                continue
            else:
                print(
                    f"  Offer from {pending_offer['sender']} still waiting - type y or n\n"
                )

        if not line:
            continue

        if line.startswith("/join "):
            new_room = line[6:].strip()
            if new_room:
                room = new_room
                chat_send(line)
            else:
                print("  Usage: /join <roomname>\n")

        elif line.startswith("/dm "):
            chat_send(line)

        elif line.startswith("/kick "):
            chat_send(line)

        elif line == "/sendfile":
            filepath = open_file_picker()
            if filepath:
                threading.Thread(
                    target=send_file, args=(filepath,), daemon=True
                ).start()
            else:
                print("  No file selected.\n")

        elif line in ("/who", "/rooms"):
            chat_send(line)

        elif line == "/quit":
            print("Goodbye.")
            break

        else:
            chat_send(line)

    try:
        chat_sock.close()
    except Exception:
        pass


def main():
    global username, room, chat_sock

    username = input("Username: ").strip()
    while not username:
        username = input("Username cannot be empty: ").strip()

    room = "general"

    chat_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        chat_sock.connect((HOST, CHAT_PORT))
    except Exception as e:
        print(f"[!] Cannot connect to {HOST}:{CHAT_PORT} - {e}")
        sys.exit(1)

    send_str(chat_sock, username)

    threading.Thread(target=receive, daemon=True).start()
    input_loop()


if __name__ == "__main__":
    main()
