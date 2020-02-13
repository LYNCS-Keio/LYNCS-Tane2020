import serial
import pigpio
import time

pi = pigpio.pi()
h1 = pi.serial_open("/dev/ttyS0", 115200)

data = ':DBF20602X'
pi.serial_write(h1, data)

line = pi.serial_read(h1, 100)
print(line)
