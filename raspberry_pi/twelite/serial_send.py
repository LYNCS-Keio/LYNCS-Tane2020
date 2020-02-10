import serial
import time

ser = serial.Serial('/dev/ttyS0', 115200)
while True:
    # data = bytes.fromhex(format(0xA55A8005000011223300, 'x'))
    data = 'abcd'
    data2 = data.encode('utf-8')
    ser.write(data2)
    print(data2)
    time.sleep(0.1)

ser.close()
