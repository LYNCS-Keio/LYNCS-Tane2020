# https://tokibito.hatenablog.com/entry/20150927/1443286053

from socket  import socket, AF_UNIX, SOCK_STREAM
import sys
import os

path = './test.sock'

s=socket(AF_UNIX, SOCK_STREAM)
s.bind(path)
s.listen(1)

def accepted(conn, addr):
    data = conn.recv(1024)
    sys.stdout.write("from :{}\n".format(data.decode()))
    conn.send(data)
    sys.stdout.write("to :{}\n".format(data.decode()))

try:
    while True:
        conn, addr = s.accept()
        sys.stdout.write("connected\n")
        accepted(conn, addr)
        sys.stdout.write("disconnect\n")
finally:
    os.remove(path)
