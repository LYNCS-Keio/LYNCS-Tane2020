# https://tokibito.hatenablog.com/entry/20150927/1443286053

from socket import socket, AF_UNIX, SOCK_STREAM
import sys

path = 'test.sock'


msg = "hello"

for idx in range(1):
    sys.stdout.write("send to server ({}): {}\n".format(idx, msg))
    s = socket(AF_UNIX, SOCK_STREAM)
    s.connect(path)
    s.send(msg.encode())
    data = s.recv(1024)
    sys.stdout.write("receive from server: {}\n".format(data.decode()))
    s.recv
    s.close()

print (repr(data))
