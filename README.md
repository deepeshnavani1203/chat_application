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
│── server.py # Server code
│── client.py # Client code

---

## Step-by-Step Tutorial

### Step 1: Create a Simple Server (`server.py`)

The server does the following:
1. Creates a socket and binds it to a host and port.
2. Listens for incoming client connections.
3. Accepts connections and starts a new thread for each client.
4. Receives messages from a client and broadcasts them to all other connected clients.

**Key parts of the code:**
- `socket.socket(socket.AF_INET, socket.SOCK_STREAM)` → Creates a TCP socket.
- `server.bind((host, port))` → Binds to a port.
- `server.listen()` → Listens for incoming clients.
- `threading.Thread(target=handle_client, ...)` → Handles multiple clients at once.
- `broadcast()` → Sends received messages to all clients.

---

### Step 2: Create a Simple Client (`client.py`)

The client does the following:
1. Connects to the server using its IP and port.
2. Starts a thread to listen for incoming messages from the server.
3. Continuously takes user input and sends it to the server.

**Key parts of the code:**
- `client.connect((host, port))` → Connects to the server.
- `threading.Thread(target=receive)` → Keeps receiving messages in the background.
- `send()` → Sends user input to the server.
- Prints all received messages in real time.

---

### Step 3: Run Messaging (Server ↔ Client)

- The server listens and broadcasts messages to all clients.
- Each client can send and receive messages simultaneously.

---

## Running the App

1. Start the server:

   ```bash
   python server.py
Start one or more clients:


Edit
python client.py
Type messages in any client, and they will be visible to all other connected clients.
