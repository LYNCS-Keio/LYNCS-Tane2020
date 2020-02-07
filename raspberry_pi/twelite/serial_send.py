import serial

ser = serial.Serial('/dev/ttyS0', 115200)
while True:
    data = binascii.a2b_hex('0xA55A8005000011223300')
    ser.write(data)
ser.close()