# https://tokibito.hatenablog.com/entry/20150927/1443286053

from socket import socket, AF_UNIX, SOCK_STREAM
import sys
import time
import struct

class pycli:
    def  __init__ (self, path):

        self.s = socket(AF_UNIX, SOCK_STREAM)
        self.s.connect(path)

    def sock_cli(self, msg):
        if type(msg) is str:
            msg = msg.encode()
        elif type(msg) is int:
            msg = msg.to_bytes(4, "little")
        elif type(msg) is float:
            msg = struct.pack('>d', msg)


        sys.stdout.write("send to server ({}): {}\n".format(1, msg))
        self.s.send(msg)
        data = self.s.recv(1024)
        sys.stdout.write("receive from server: {}\n".format(data.decode()))

    def __del__(self):
        self.s.close()

if __name__ == "__main__":
    so = pycli("test.sock")
    while 1:
        so.sock_cli(80.5)
