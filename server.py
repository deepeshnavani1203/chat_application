import socket
import threading

HOST = "127.0.0.1"
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []  # list of connections
usernames = {}  # conn -> username


def broadcast(message, sender_conn=None):
    for client in clients:
        if client != sender_conn:
            try:
                client.send(message)
            except:
                client.close()
                clients.remove(client)


def handle_client(conn, addr):
    print(f"New connection: {addr}")

    try:
        # First receive username
        username = conn.recv(1024).decode("utf-8")
        usernames[conn] = username

        join_msg = f"{username} joined the chat!".encode("utf-8")
        broadcast(join_msg, conn)

        while True:
            msg = conn.recv(1024)
            if not msg:
                break

            formatted = f"{username}: {msg.decode('utf-8')}"
            broadcast(formatted.encode("utf-8"), conn)

    except:
        pass

    # Cleanup on disconnect
    print(f"Connection closed: {addr}")
    clients.remove(conn)

    if conn in usernames:
        left_msg = f"{usernames[conn]} left the chat.".encode("utf-8")
        broadcast(left_msg, conn)
        del usernames[conn]

    conn.close()


def start_server():
    print(f"Server started on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        clients.append(conn)

        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


start_server()
