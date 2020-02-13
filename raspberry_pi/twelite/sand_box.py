import serial
import pigpio
import time

pi = pigpio.pi()
h1 = pi.serial_open("/dev/ttyS0", 115200)

data = ':DBF2062\r\n'
pi.serial_write(h1, data)