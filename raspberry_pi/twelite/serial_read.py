import serial

ser = serial.Serial('/dev/ttyS0', 115200)
while True:
    line = ser.readline()
    print(line.decode('UTF-8'))

ser.close()
