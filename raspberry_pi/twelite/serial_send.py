import serial

ser = serial.Serial('/dev/ttyS0', 115200)
while True:
    # data = bytes.fromhex(format(0xA55A8005000011223300, 'x'))
    data = 'hello\r\n'
    data2 = data.encode('utf-8')
    ser.write(data2)
ser.close()