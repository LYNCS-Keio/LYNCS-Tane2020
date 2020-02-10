import serial
import time

ser = serial.Serial('/dev/ttyS0', 115200)
while True:
    #data = bytes.fromhex(format(0xA55A8005000011223300, 'x'))

    #data = bytes.fromhex(format(7880010101FFFFFFFFFFFFFFFFXX, 'x'))
    data = ':0001112233AABBCCXX\r\n'
    ser.write(data)
    print(data)
    time.sleep(0.1)

ser.close()