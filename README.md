# 💬 TermiTalk — Python Terminal Chat App

A simple but powerful **terminal-based chat application** built with Python.  
Supports multiple rooms, private messages, file transfers, and admin controls — all over raw TCP sockets.

---

## 📋 Requirements

- Python **3.7+**
- No external libraries needed — only Python standard library
- `tkinter` (comes pre-installed with Python on Windows & macOS)
  - Linux users: `sudo apt install python3-tk`

---

## 🚀 Quick Start

### Step 1 — Start the Server

Run this on the machine that will **host** the chat:

```
python server.py
```

You will see:

```
[SERVER] Chat  → 0.0.0.0:12345
[SERVER] Files → 0.0.0.0:12346
[SERVER] First user to connect becomes ADMIN.
[SERVER] Ready. Ctrl+C to stop.
```

> Keep this terminal open. Don't close it.

---

### Step 2 — Connect as a Client

Everyone who wants to chat runs this **on their own machine**:

```
python client.py
```

You will be asked:

```
Username: Alice
```

That's it. You are now in the **general** room and can start chatting.

> ⚠️ Before running client.py, open the file and set the correct server IP:
>
> ```python
> HOST = "10.60.123.34"   ← change this to your server's IP address
> ```

---

## 🔧 Configuration

Open `client.py` and change these two lines at the top:

```python
HOST      = "10.60.123.34"   # ← Your server's IP address
CHAT_PORT = 12345             # ← Leave this as is
FILE_PORT = 12346             # ← Leave this as is
```

If you are running everything on the **same machine** (for testing):

```python
HOST = "127.0.0.1"
```

---

## 💬 How to Chat

After connecting, just **type anything and press Enter** to send a message to everyone in your current room.

```
Hello everyone!
[general] Alice: Hello everyone!       ← others see this
```

---

## 📖 All Commands

| Command                    | What it does                      |
| -------------------------- | --------------------------------- |
| `/join <room>`             | Switch to a different room        |
| `/who`                     | See who is in your current room   |
| `/rooms`                   | See all active rooms              |
| `/dm <username> <message>` | Send a private message to someone |
| `/sendfile`                | Open file picker and send a file  |
| `/kick <username>`         | Kick a user _(admin only)_        |
| `/quit`                    | Exit the chat                     |

---

## 🗂️ Rooms

- You start in **general** automatically
- Create any room instantly with `/join <name>`
- Example: `/join gaming` creates and joins the "gaming" room
- File transfers are **blocked in general** — switch to any other room first

```
/join study
✓ Switched to room 'study'.
```

---

## 📨 Private Messages (DM)

Send a message only one person can see:

```
/dm Bob Hey, are you free?
```

Bob sees:

```
[DM from Alice]: Hey, are you free?
```

You see:

```
[DM to Bob]: Hey, are you free?
```

---

## 📁 Sending Files

1. Make sure you are **NOT** in the general room (`/join anyroom`)
2. Type `/sendfile`
3. A file picker window opens — select your file
4. The receiver sees a notification and types `y` to accept or `n` to reject

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  📥  FILE OFFER  from Alice
      File : notes.pdf
      Size : 204,800 bytes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ▶  Type  y  to accept  or  n  to reject
```

Received files are saved in the **same folder** as `client.py` with the prefix `received_`.  
Example: `received_notes.pdf`

---

## 👑 Admin

- The **first user to connect** to the server automatically becomes admin
- Admin sees `👑 You are ADMIN.` in their welcome message
- If the admin disconnects, the **next connected user** is promoted automatically

### Admin Commands

**Kick a user:**

```
/kick Bob
✓ Bob has been kicked.
```

Bob sees:

```
⚠ You have been kicked by the admin.
```

---

## 🖥️ Running on the Same Machine (Testing)

Open **3 terminals**:

Terminal 1 — Server:

```
python server.py
```

Terminal 2 — Client 1:

```
python client.py
Username: Alice
```

Terminal 3 — Client 2:

```
python client.py
Username: Bob
```

Change `HOST = "127.0.0.1"` in `client.py` before testing locally.

---

## ❓ Common Issues

**"Cannot connect" error**

- Make sure `server.py` is running first
- Check the `HOST` IP in `client.py` is correct
- Make sure ports `12345` and `12346` are not blocked by a firewall

**File picker doesn't open**

- Linux: run `sudo apt install python3-tk`
- Make sure you're not in the general room when sending files

**Messages not appearing**

- Check that both users are in the same room (`/who` to verify)

---

## 📂 File Structure

```
project/
│
├── server.py       ← Run this on the host machine
└── client.py       ← Run this on every user's machine
```

---

_Made with Python standard library only. No pip installs needed._
