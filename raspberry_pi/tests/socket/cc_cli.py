# https://tokibito.hatenablog.com/entry/20150927/1443286053

from socket import socket, AF_UNIX, SOCK_STREAM
import sys
import time

def sock_cli(path, msg):
    if type(msg) is str:
        msg = msg.encode()

    if type(msg) is int:
        msg = msg.to_bytes(4, "little")

    while True:
        sys.stdout.write("send to server ({}): {}\n".format(1, msg))
        s = socket(AF_UNIX, SOCK_STREAM)
        s.connect(path)


        s.send(msg)
        data = s.recv(1024)

        sys.stdout.write("receive from server: {}\n".format(data.decode()))
        s.recv

        s.close()
        time.sleep (1)

    print (repr(data))

if __name__ == "__main__":
    sock_cli("test.sock", 80)
