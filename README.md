# 🧠 Python C2 Framework (Educational)

> **⚠️ WARNING: This tool is for EDUCATIONAL and AUTHORIZED SECURITY TESTING purposes only.**  
> Unauthorized access to computer systems is illegal. The authors and contributors are not responsible for any misuse. Use this only on networks and devices you own or have explicit written permission to test.

A lightweight, multi‑threaded Command & Control (C2) server and client written in pure Python.  
This project demonstrates core concepts of remote administration: command execution, file transfer, interactive shell access, and basic networking with timeouts and error handling.

---

## ✨ Features

- **Multi‑client handling** – The server manages multiple connected clients concurrently using threads.
- **Remote Shell** – Execute system commands on the target machine.
- **Reliable File Transfers** – Upload/download binary files using **size‑prefixed headers** (fixes the fragile `EOF` marker).
- **Dynamic Client Configuration** – The client accepts the server’s IP and port as command‑line arguments (no hardcoded values).
- **Heartbeat / Keep‑alive** – Built‑in `ping`/`PONG` mechanism to check server responsiveness.
- **Timeouts & TCP Keep‑alive** – Prevents hanging connections due to network issues.
- **Path Traversal Protection** – Restricts file access to the server’s working directory.
- **Windows‑friendly Launchers** – Ready‑to‑use `.bat` files to start the client and server with a double‑click.
- **Standalone `.exe` potential** – Package the client as a single `.exe` that runs without Python installed (see Bonus section).

---

## 📋 Requirements

- **Python 3.6+** (for running the `.py` scripts)
- No external dependencies – uses only the standard library.

---

## 📂 File Structure

```
C:\my_c2_project\
│
├── server.py              # C2 Server
├── client.py              # C2 Client
├── server_launcher.bat    # Double‑click to start the server
├── client_launcher.bat    # Double‑click to connect to the server (asks for IP/port)
└── README.md              # This file
```

---

## 🚀 Getting Started

### 1. Save the scripts
Place `server.py` and `client.py` (the fixed versions provided earlier) in the same folder.

### 2. Start the Server
- **Option A – Command line:**
  ```bash
  python server.py
  ```
- **Option B – Double‑click `server_launcher.bat`** (see launcher section below).

The server binds to `0.0.0.0:4444` by default. You should see:
```
[*] C2 Server listening on 0.0.0.0:4444 😈
```

### 3. Connect a Client
- **Command line:**
  ```bash
  python client.py 192.168.1.100 4444
  ```
- **Double‑click `client_launcher.bat`** – it will ask you for the server IP and port, then launch the client automatically.

If successful, you’ll see:
```
[*] Connected to C2 Server. Enjoy your suffering! 😈
C2>
```

---

## 📦 Launcher Batch Files (`.bat`)

### `server_launcher.bat`
```batch
@echo off
title C2 Server Launcher
color 0C
echo ==============================
echo     🔥 C2 Server Launcher
echo ==============================
echo.
echo [*] Starting server on 0.0.0.0:4444 ...
echo.
python server.py
echo.
echo [*] Server has stopped. Press any key to close...
pause >nul
```

### `client_launcher.bat`
```batch
@echo off
title C2 Client Launcher
color 0A
echo ==============================
echo     🐍 C2 Client Launcher
echo ==============================
echo.
set /p SERVER_IP=Enter Server IP (e.g., 192.168.1.100): 
set /p PORT=Enter Server Port (default is 4444): 
if "%PORT%"=="" set PORT=4444
echo.
echo [*] Connecting to %SERVER_IP%:%PORT% ...
echo.
python client.py %SERVER_IP% %PORT%
echo.
echo [*] Client has exited. Press any key to close...
pause >nul
```

> 💡 *If your system uses `py` instead of `python`, replace `python` with `py` in both files.*

---

## 🎮 Command Reference

At the `C2>` prompt:

| Command | Syntax | Description |
| :------ | :----- | :---------- |
| `shell` | `shell` | Enter interactive shell. Type `exit` to return. |
| `upload` | `upload <file>` | Upload a file from **client** → **server**. |
| `download` | `download <file>` | Download a file from **server** → **client**. |
| `list` | `list` | List files in the server’s current directory. |
| `ping` | `ping` | Heartbeat – server replies with `PONG`. |
| `exit` | `exit` | Close the connection and quit. |

---

## 🔧 Key Fixes & Improvements

| Original Issue | Solution |
| :-------------- | :------- |
| **Hardcoded client IP** | Client accepts IP/port as `sys.argv` arguments. |
| **Fragile `EOF` file transfers** | Uses size‑prefixed headers (`struct.pack('!Q', size)`) for reliability. |
| **No error handling** | Full `try/except` blocks around file I/O, subprocess, and sockets. |
| **No timeouts / hanging** | Added `settimeout()` and `SO_KEEPALIVE` on both ends. |
| **Path traversal vulnerability** | Server sanitises paths with `os.path.abspath()` to stay inside its working directory. |

---

## 🛡️ Limitations & Security Notes

- **No encryption** – All traffic is plaintext. Do not use over the internet without TLS.
- **Shell injection risk** – Uses `shell=True`; commands are not sanitised. Only use in trusted lab environments.
- **No authentication** – Anyone who can reach the port can connect.
- **OS‑dependent** – Shell commands vary between Windows and Linux.

---

## ❓ Troubleshooting

| Problem | Solution |
| :------ | :------- |
| `ConnectionRefusedError` | Server not running, wrong IP/port, or firewall blocking. |
| Timeout on long commands | Increase `settimeout()` values in `server.py` and `client.py`. |
| `Permission denied` | Check write permissions on the server side and read permissions on the client side. |
| `Address already in use` | Port `4444` is busy – kill the existing process or change the port in `server.py`. |
| `python` not recognised | Replace `python` with `py` in the batch files or add Python to your PATH. |

---

## ⚡ BONUS: Create a Standalone `.exe` (No Python Required)

You can compile `client.py` (or `server.py`) into a single `.exe` file using **PyInstaller**. This lets you run the client on any Windows machine without installing Python.

### Step 1: Install PyInstaller
```bash
pip install pyinstaller
```

### Step 2: Build the `.exe`
For the **client** (most common):
```bash
pyinstaller --onefile --console client.py
```
For the **server**:
```bash
pyinstaller --onefile --console server.py
```

### Step 3: Find your `.exe`
After the build finishes, the standalone executable will be in the `dist` folder:
```
C:\my_c2_project\dist\client.exe
```

### Step 4: Use the `.exe` with your launcher
Update `client_launcher.bat` to call the `.exe` instead of the `.py` script:
```batch
client.exe %SERVER_IP% %PORT%
```
*(Make sure `client.exe` is in the same folder as the `.bat`, or use the full path.)*

Now you can:
- Distribute only `client.exe` and the `.bat` – no Python required.
- Run the client on machines that don’t have Python installed.
- Optionally, use tools like **UPX** to compress the `.exe` further.

> 📌 *The `.exe` will be larger (~5–10 MB) because it bundles the Python interpreter and standard library, but it’s completely self‑contained.*

---

## 🤝 Contributing

This project is a **proof‑of‑concept** for learning. Feel free to extend it with:
- TLS/SSL encryption (`ssl.wrap_socket`)
- Password‑based authentication
- Command logging and audit trails
- AES‑encrypted file transfers

---

## 📜 License

MIT License – for educational purposes only.  
The author assumes no liability for any misuse or damage caused by this software.

---

*Happy (ethical) hacking – and always stay on the right side of the law.* 🔐
