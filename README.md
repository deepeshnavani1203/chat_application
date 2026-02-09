# Python Chat Application

A console-based chat application built with Python using sockets and threading. Multiple clients can connect to one server and exchange messages in real time. This project is meant to demonstrate basic networking and concurrency in Python.

---

## Features

* Multi-client group chat
* Real-time messaging in terminal
* Built only with Python standard libraries
* Simple client–server model
* Easy to extend with more features

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
* Receives messages and broadcasts them to others

Core concepts used:

* TCP sockets
* Binding and listening
* Multithreading
* Broadcasting messages

---

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

## Possible Improvements

* Usernames
* Private messaging
* Chat rooms
* Message timestamps
* Chat history logging
* GUI or web interface
* Message encryption

---

## Purpose

This project is for learning and experimenting with:

* Socket programming
* Client–server communication
* Multithreading
* Real-time data exchange

A simple foundation for building larger real-time applications.
