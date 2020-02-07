import serial

ser = serial.Serial('/dev/ttyS0', 115200)
while True:
    data = bytes.fromhex(format(0xA55A8005000011223300, 'x'))
    ser.write(data)
ser.close()