import socket
import threading

HOST = '127.0.0.1'   # same as server
PORT = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))


def receive_messages():
    """Keep receiving messages from server"""
    while True:
        try:
            msg = client.recv(1024).decode("utf-8")
            print(msg)
        except:
            print("Disconnected from server")
            break


def send_messages():
    """Send user input messages to server"""
    while True:
        msg = input("")
        client.send(msg.encode("utf-8"))


# Run receiver in background
threading.Thread(target=receive_messages, daemon=True).start()

# Run sender in main thread
send_messages()
