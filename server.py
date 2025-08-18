import socket
import threading

# Server setup
HOST = "127.0.0.1"  # localhost
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []  # to store connected clients


def broadcast(message, conn):
    """Send message to all clients except the sender"""
    for client in clients:
        if client != conn:
            try:
                client.send(message)
            except:
                clients.remove(client)


def handle_client(conn, addr):
    """Handle communication with one client"""
    print(f"New connection: {addr}")
    while True:
        try:
            msg = conn.recv(1024)
            if not msg:
                break
            broadcast(msg, conn)
        except:
            break
    conn.close()
    clients.remove(conn)
    print(f"Connection closed: {addr}")


def start_server():
    print(f"Server started on {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        clients.append(conn)
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


start_server()
