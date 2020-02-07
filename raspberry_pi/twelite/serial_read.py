import serial

ser = serial.Serial('/dev/ttyS0', 115200)
while True:
    line = ser.readline()
    line.encode('utf-8')
    print(line)

ser.close()
