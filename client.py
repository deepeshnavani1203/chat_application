import socket
import threading
import os

HOST = "127.0.0.1"
PORT = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

username = input("Enter username: ")
client.send(username.encode())


def receive():
    while True:
        try:
            msg = client.recv(1024)

            if msg == b"FILE":
                data = client.recv(999999)
                with open("received_file", "wb") as f:
                    f.write(data)
                print("File received!")
            else:
                print(msg.decode())

        except:
            break


def send():
    while True:
        msg = input()

        if msg:
            if msg != "/typing":
                client.send(msg.encode())
            else:
                client.send("/typing".encode())


threading.Thread(target=receive, daemon=True).start()
send()
