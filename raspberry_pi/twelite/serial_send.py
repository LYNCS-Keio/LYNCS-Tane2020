import serial

ser = serial.Serial('/dev/ttyS0', 115200)
while True:
    # data = bytes.fromhex(format(0xA55A8005000011223300, 'x'))
    data = "0xA50x5A0x800x050x000x000x110x220x330x00"
    ser.write(data)
ser.close()