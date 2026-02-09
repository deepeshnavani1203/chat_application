# Python Chat Application

A console-based chat application built with Python using sockets and threading. Multiple clients can connect to one server and exchange messages in real time. This project demonstrates basic networking and concurrency in Python.

---

## Features

### Multi-client group chat

Multiple users can chat at the same time.
Example: If 3 clients are connected, a message from one is delivered to the other two.

### Real-time messaging

Messages are delivered instantly without refreshing.
Example: User A sends "Hello" and User B sees it immediately.

### Terminal-based communication

Runs entirely in the command line.
Example: Open multiple terminals and chat between them.

### No external libraries

Uses only Python’s built-in modules.
Example: Works on a fresh Python install without pip installs.

### Simple client–server model

One server handles multiple clients.
Example: Server runs once; many clients can join.

### Easy to extend

You can add features like usernames or private chat.
Example: Modify code to attach names to messages.

---

## Tech Stack

* Python 3
* socket (network communication)
* threading (handling multiple clients)

---

## Project Structure

chat-app/
server.py — server code
client.py — client code

---

## How It Works

### Server

* Creates a TCP socket
* Binds to a host and port
* Listens for connections
* Accepts clients and starts a new thread for each
* Receives messages and broadcasts them to other clients

### Client

* Connects to the server
* Runs a background thread to receive messages
* Takes user input and sends it to the server
* Displays incoming messages instantly

---

## Running the App

Start the server
python server.py

Start one or more clients
python client.py

Type messages in any client; all connected clients will see them.

---

## Example Usage

Server terminal:

Server started on 127.0.0.1:12345
New connection: ('127.0.0.1', 53021)
New connection: ('127.0.0.1', 53022)

Client 1:

Hello everyone

Client 2:

Hello everyone
Hi!

Client 3:

Hello everyone
Hi!
Nice to meet you

Each message from one client appears on all others.

---

## Possible Improvements

* Usernames
* Private messaging
* Chat rooms
* Message timestamps
* Chat history logging
* GUI or web interface
* Message encryption

Examples:

* Usernames → "Deepesh: Hello"
* Private chat → "/msg Rahul Hi"
* Chat rooms → "/join coding"
* Timestamps → "[12:45] Hello"

---

## Purpose

This project is for learning and experimenting with:

* Socket programming
* Client–server communication
* Multithreading
* Real-time data exchange

A simple foundation for building larger real-time applications.
