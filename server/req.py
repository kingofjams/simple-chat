import socket

client = socket.socket()
client.connect(("127.0.0.1", 8090))

while True:
    inp = input("Please(q\退出):\n>>>")
    client.sendall(bytes(inp, encoding="utf-8"))
    if inp == "q":
        break
    ret = str(client.recv(1024), encoding="utf-8")
    print(ret)
