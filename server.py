import threading
import socket
import os
import json


def getType(path):
    if path.endswith(".html"):
        return "text/html"
    elif path.endswith(".css"):
        return "text/css"
    elif path.endswith(".js"):
        return "text/javascript"
    elif path.endswith(".json"):
        return "application/json"
    elif path.split(".")[len(path.split(".")) - 1 :] in [
        "jpg",
        "jpeg",
        "png",
        "gif",
        "bmp",
        "ico",
    ]:
        return "CANNOT HANDLE"
    elif path.endswith(".txt"):
        return "text/plain"
    elif path.endswith(".svg"):  # svg is just text
        return "image/svg+xml"
    else:
        return "text/plain"


class Server:
    thread: threading.Thread

    def __init__(self, port=8080, doOutput=True):
        self.port = port
        self.paths = {}
        self.doOutput = doOutput
        self.running = False
        self.server_socket = None

    def saveConfig(self):
        path = input("path(default: config.json) >").strip() or "config.json"
        conf = {
            "port": self.port,
            "paths": self.paths,
            "doOutput": self.doOutput,
        }

        with open(path, "w") as f:
            json.dump(conf, f)

    def loadConfig(self):
        path = input("path(default: config.json) >").strip() or "config.json"
        with open(path, "r") as f:
            conf = json.load(f)
            self.port = conf["port"]
            self.paths = conf["paths"]
            self.doOutput = conf["doOutput"]

    def readFile(self, path):
        if not os.path.exists(path):
            if self.doOutput:
                print(f"File not found: {path}")
            return "File not found"
        with open(path, "r") as f:
            return f.read()

    def getStatus(self):
        if self.running:
            return "running"
        else:
            return "stopped"

    def config(self):
        t: str = ""
        while t != "done":
            t = input("config> ")

            if t == "port":
                self.port = int(input("port> "))
                if self.doOutput:
                    print(f"Set port to {self.port}")
            elif t == "path":
                p = input("path> ")
                self.paths[p] = input("value> ")
                if self.doOutput:
                    print(f"Set path {p} to {self.paths[p]}")
            elif t == "output":
                self.doOutput = not self.doOutput
                if self.doOutput:
                    print("Set doOutput to true")
                else:
                    print("Set doOutput to false")
            elif t == "save":
                self.saveConfig()
                if self.doOutput:
                    print("Saved config")
            elif t == "load":
                self.loadConfig()
                if self.doOutput:
                    print("Loaded config")
            elif t == "help":
                print("port")
                print("path")
                print("output")
                print("done")
                print("save")
                print("load")
            elif t == "done":
                return
            else:
                print("Invalid command")

    def start(self):
        if not self.running:
            self.running = True
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(("", self.port))
            self.server_socket.listen(5)
            if self.doOutput:
                print(f"Server started on port {self.port}")

            self.thread = threading.Thread(target=self.handleClients)
            self.thread.start()

    def stop(self):
        if self.running:
            self.running = False
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None
                self.thread = None
            if self.doOutput:
                print("Server stopped")

    def handleClients(self):
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                if self.doOutput:
                    print(f"Connection from {client_address}")
                threading.Thread(
                    target=self.handleClient, args=(client_socket,)
                ).start()
            except OSError:
                break  # Occurs when server_socket is closed

    def handleClient(self, client_socket):
        try:
            request = client_socket.recv(1024).decode()
            if self.doOutput:
                print(f"Received request: {request}")

            response = self.processRequest(request)
            client_socket.sendall(response.encode())
        except Exception as e:
            if self.doOutput:
                print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def processRequest(self, request: str) -> str:
        # Simple processing: look up the path in self.paths
        lines = request.splitlines()
        if lines:
            first_line = lines[0]
            parts = first_line.split()
            if len(parts) >= 2:
                path = parts[1]
                if path in self.paths:
                    type = getType(path)
                    if type == "CANNOT HANDLE":
                        return "HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nCANNOT HANDLE, zcore will never handle binary files >:]"
                    return f"HTTP/1.1 200 OK\r\nContent-Type: {type}\r\n\r\n{self.readFile(self.paths[path])}"
        return "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nNot Found"
