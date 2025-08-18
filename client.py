import socket
import threading

HOST = "127.0.0.1"
PORT = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))


def receive_messages():
    while True:
        try:
            msg = client.recv(1024).decode("utf-8")
            print(msg)
        except:
            print("Disconnected from server")
            break


def send_messages():
    while True:
        msg = input("")
        client.send(msg.encode("utf-8"))


threading.Thread(target=receive_messages, daemon=True).start()

send_messages()
