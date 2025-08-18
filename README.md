
# Python Chat Application

This is a **console-based chat application** built using **pure Python** with `socket` and `threading`.  
It allows multiple clients to connect to a single server and exchange messages in real time.  

---

## Features
- Multi-client chat support (group chat)
- Real-time messaging
- Pure Python (no external libraries)
- Simple client-server architecture
- Easy to extend (usernames, private chat, logging, etc.)

---

## Tech Stack
- Python 3
- `socket` (for networking)
- `threading` (to handle multiple clients concurrently)

---

## Project Structure

chat-app/
│── server.py   # Server code
│── client.py   # Client code

# Step-by-Step Tutorial

### Step 1: Create a Simple Server
The server needs to:
- Bind to an IP and port
- Listen for client connections
- Accept connections

### Step 2: Create a Simple Client

The client needs to:

* Connect to the server
* Send and receive messages

### Step 3: Add Messaging (Server → Client)

Update the **server** to handle messages:

* Receive messages from clients
* Broadcast to all connected clients

### Step 4: Update Client to Send & Receive

Make client send messages and listen for new ones.

## Running the App

1. Start the server:

   ```
   python server.py
   ```
2. Start one or more clients:

   ```
   python client.py
   ```


## Possible Improvements

* Add usernames
* Private chat (direct messages)
* GUI with Tkinter/PyQt
* Chat history logging

