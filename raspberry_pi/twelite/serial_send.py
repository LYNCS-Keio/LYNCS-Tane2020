import serial
from sys import

ser = serial.Serial('/dev/ttyS0', 115200)
ser.write("HELLO!!!")
ser.close()