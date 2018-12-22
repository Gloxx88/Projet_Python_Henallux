from socket import socket


class Machine:
    DEFAULT_PORT = 56842

    # initialize connection
    def __init__(self, address: str, port: int):
        self.address = address
        self.port = port
        self.socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((address, port))

    def stop(self):
        self.socket.close()
        print("End of connection")


class Client(Machine):
    def __init__(self, address, port):
        super().__init__(address, port)
        self.socket.connect("",port);
        print("connection")


class Target(Machine):
    def __init__(self, address, port):
        super().__init__(address, port)
        self.socket.listen(1)
        print("listening...")
        self.socket, infoCo = socket.accept()
        print("Co ok")

