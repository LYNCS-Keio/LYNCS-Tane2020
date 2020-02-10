import serial
import pigpio
import time

pi = pigpio.pi()
h1 = pi.serial_open("/dev/ttyS0", 115200)

#ser = serial.Serial('/dev/ttyS0', 115200)
while True:
    #data = ':0001112233AABBCCXX\r\n'
    
    pi.serial_write(h1, b'hello!')
    ser.write(data)
    print(data)
    time.sleep(0.1)

ser.close()
