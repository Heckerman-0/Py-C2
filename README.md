# 🧠 Python C2 Framework (Educational)

> **⚠️ WARNING: This tool is for EDUCATIONAL and AUTHORIZED SECURITY TESTING purposes only.**
> Unauthorized access to computer systems is illegal. The authors and contributors are not responsible for any misuse. Use this only on networks and devices you own or have explicit written permission to test.

A lightweight, multi-threaded Command & Control (C2) server and client written in pure Python.  
This project demonstrates basic remote administration concepts, including command execution, file transfer, and interactive shell access.

---

## ✨ Features

- **Multi-client handling** – The server handles multiple connected clients concurrently using threads.
- **Remote Shell** – Execute system commands on the target machine.
- **File Transfer (Upload/Download)** – Reliable binary file transfer using **size-prefixed headers** (fixed the fragile `EOF` marker).
- **Dynamic Client Configuration** – The client accepts the server’s IP and port as command-line arguments (fixed hardcoded IP).
- **Heartbeat / Keep‑alive** – Built-in `ping`/`PONG` mechanism to check server responsiveness.
- **Timeouts & TCP Keep‑alive** – Prevents hanging connections due to network issues (fixed lack of timeouts).
- **Basic Security Hardening** – Path traversal protection (restricts file access to the server’s working directory) and proper error handling for all file operations.

---

## 📋 Requirements

- **Python 3.6+**
- No external dependencies (uses only the standard library).

---

## 📂 File Structure

```
.
├── server.py      # C2 Server (listens for connections)
└── client.py      # C2 Client (connects to the server)
```

---

## 🚀 Getting Started

### 1. Clone or save the files
Save the provided `server.py` and `client.py` to your machine.

### 2. Start the Server
The server listens on all interfaces (`0.0.0.0`) on port `4444` by default.

```bash
python server.py
```

You should see:
```
[*] C2 Server listening on 0.0.0.0:4444 😈
```

*(To change the port, modify the `C2Server()` call at the bottom of `server.py`.)*

### 3. Connect the Client
Run the client and point it to the server's IP address:

```bash
python client.py <SERVER_IP> <PORT>
```

**Examples:**
```bash
# Connect to localhost (default port)
python client.py 127.0.0.1

# Connect to a remote server on port 5555
python client.py 192.168.1.100 5555
```

If the connection succeeds, you will see:
```
[*] Connected to C2 Server. Enjoy your suffering! 😈
C2>
```

---

## 🎮 Command Reference

At the `C2>` prompt, you can type the following commands:

| Command | Syntax | Description |
| :------ | :----- | :---------- |
| `shell` | `shell` | Enters interactive shell mode. Execute any system command. Type `exit` to return to the main `C2>` prompt. |
| `upload` | `upload <local_file>` | Uploads a file from the **client** to the **server** (current working directory). |
| `download` | `download <remote_file>` | Downloads a file from the **server** to the **client** (current working directory). |
| `list` | `list` | Lists the files in the server's current working directory. |
| `ping` | `ping` | Sends a heartbeat to the server. The server replies with `PONG` (used to check connectivity). |
| `exit` | `exit` | Closes the connection and shuts down the client. |

### Shell Mode Example
```
C2> shell
[*] Shell mode activated. Type 'exit' to quit. 🐍
shell> whoami
desktop-abc\admin
shell> ipconfig
... (network info) ...
shell> exit
C2>
```

### File Transfer Example
```
C2> upload secret.pdf
[*] File 'secret.pdf' uploaded successfully. 😈

C2> download logs.txt
[*] File 'logs.txt' downloaded successfully. 😈
```

---

## 🔧 Key Fixes & Improvements

Compared to the original raw script, this version includes:

| Issue | Solution |
| :---- | :------- |
| **Hardcoded Client IP** | The client now accepts the server IP and port as `sys.argv` arguments. |
| **Fragile File Transfers (EOF marker)** | Implemented a **size-prefix header** (`struct.pack('!Q', file_size)`) to know exactly how many bytes to read, preventing data corruption. |
| **No Error Handling** | Wrapped all file operations, network recv/send, and subprocess calls in `try/except` blocks. Provides clear error messages for missing files, permission errors, and incomplete transfers. |
| **No Timeouts / Hanging connections** | Added `socket.settimeout()` and `SO_KEEPALIVE` on both client and server sockets. The server also catches `socket.timeout` to cleanly close dead clients. |
| **Path Traversal Vulnerability** | Added a check on the server side using `os.path.abspath()` to ensure file paths stay within the server's working directory. |

---

## 🛡️ Limitations & Security Notes

- **No Encryption** – All traffic (commands, output, files) is sent in **plaintext** over TCP. Do not use this over the internet or untrusted networks without adding TLS/SSL.
- **Shell Injection Risk** – The server uses `shell=True` in `subprocess`. While this allows complex commands (pipes, redirects), it is vulnerable if the client is compromised or malicious. In a real tool, commands should be sanitized or passed as argument lists.
- **Authentication** – There is no password or challenge-response mechanism. Anyone who can reach the server port can connect and issue commands.
- **Windows / Linux** – The shell commands are OS-dependent. For example, `ipconfig` works on Windows, while `ifconfig`/`ip a` works on Linux.

---

## ❓ Troubleshooting

If you run into issues, here are the most common fixes:

- **`ConnectionRefusedError`**  
  *Ensure the server is running and the IP/port are correct. Check your firewall settings.*

- **Timeout on long-running shell commands**  
  *The default socket timeout is 60 seconds for the server and 30 seconds for the client. For commands that take longer (e.g., heavy system scans), open `server.py` and `client.py` and increase the `settimeout()` values.*

- **`Permission denied` when uploading/downloading**  
  *Make sure the server process has write permissions in its current working directory, and the client process has read permissions for the files you are uploading.*

- **`Address already in use`**  
  *This means port `4444` (or the port you chose) is already occupied. Kill the existing process using that port, or change the port number inside `server.py` (and pass the new port to the client).*

- **Broken pipe / Connection reset**  
  *This usually happens when the client or server crashes unexpectedly. Check the error logs printed in the terminal and verify your Python version (3.6+).*

---

## 🤝 Contributing

This project is intended as a **proof-of-concept** for learning about socket programming, threading, and security fundamentals. Feel free to fork it and add:
- TLS/SSL encryption (`ssl.wrap_socket`)
- User authentication
- Command logging
- AES encryption for file transfers

---

## 📜 License

This project is provided under the **MIT License** for educational purposes.  
The author assumes no liability for any misuse or damage caused by this software.

---

## 📬 Final Note

This README is fully self-contained. If you need further help extending this tool (e.g., adding encryption or authentication), just open a new discussion or issue in your repository.
