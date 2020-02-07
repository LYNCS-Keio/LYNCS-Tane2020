import serial

ser = serial.Serial('/dev/ttyS0', 115200)
while True:
    data = bytes.fromhex(format(0xA5 5A 80 05 00 00 11 22 33 00, 'x'))
    ser.write(data)
ser.close()