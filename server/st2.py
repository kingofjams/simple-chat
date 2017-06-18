import socket

SOCKET_FAMILY = socket.AF_INET
SOCKET_TYPE = socket.SOCK_STREAM

sockServer = socket.socket()
sockServer.bind(('0.0.0.0', 8090))
sockServer.listen(5)

while True:
    cliobj, addr = sockServer.accept()
    while True:
        recvdata = cliobj.recv(1024)
        if recvdata:
            print cliobj.fileno()
            print(recvdata)
        else:
            cliobj.close()
            break