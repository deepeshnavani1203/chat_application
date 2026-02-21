import socket
import threading
import os
import struct

HOST = "10.60.123.34"  # CHANGE THIS TO SERVER IP
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
                filename = client.recv(1024).decode()
                filesize = struct.unpack("!I", client.recv(4))[0]

                data = b""
                while len(data) < filesize:
                    data += client.recv(4096)

                with open("received_" + filename, "wb") as f:
                    f.write(data)

                print("File received:", filename)
            else:
                print(msg.decode())

        except:
            break


def send_file(filename):
    if os.path.exists(filename):
        filesize = os.path.getsize(filename)

        client.send(f"/sendfile {filename}".encode())
        client.send(filename.encode())
        client.send(struct.pack("!I", filesize))

        with open(filename, "rb") as f:
            client.send(f.read())

        print("File sent!")
    else:
        print("File not found")


def send():
    while True:
        msg = input()

        if msg.startswith("/sendfile"):
            filename = msg.split(" ", 1)[1]
            send_file(filename)
        else:
            client.send(msg.encode())


threading.Thread(target=receive, daemon=True).start()
send()
