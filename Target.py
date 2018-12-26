from Objet_Us_Target import Target

while True:
    target = Target()
    target.socket_bind()
    target.socket_accept()
    try:
        target.recv_key_rsa()
        target.send_key_aes()
        target.what_to_do()
    except ConnectionResetError as msg:
        if target.print:
            print("The connection has been stopped")
            print("Error : " + str(msg))
        target.quit()
