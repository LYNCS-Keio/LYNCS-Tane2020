# https://tokibito.hatenablog.com/entry/20150927/1443286053

from socket import socket, AF_UNIX, SOCK_STREAM
import sys

def sock_cli(path, msg):
    sys.stdout.write("send to server ({}): {}\n".format(1, msg))
    s = socket(AF_UNIX, SOCK_STREAM)
    s.connect(path)

    if type(msg) is str:
        msg = msg.encode()

    s.send(msg)
    data = s.recv(1024)

    sys.stdout.write("receive from server: {}\n".format(data.decode()))
    s.recv

    s.close()
    print (repr(data))

if __name__ == "__main__":
    sock_cli("test.sock", b"hello")
