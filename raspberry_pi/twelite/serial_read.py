import serial

ser = serial.Serial('/dev/ttyS0', 115200)
while True:
    line = ser.readline()
    print(line)
    print(line.decode('UTF-8'))
    print(int(line), 16)

ser.close()
