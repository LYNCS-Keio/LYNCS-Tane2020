import serial

ser = serial.Serial('/dev/ttyS0', 115200)
while True:
    line = ser.readline()
    print(line)
    print(bytes.hex(line))

ser.close()
