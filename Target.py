from Objet_Us_Target import Target


target = Target()
target.socket_bind()
target.socket_accept()
try:
    target.what_to_do()
except ConnectionResetError as msg:
    if target.print:
        print("")
        #TODO try
