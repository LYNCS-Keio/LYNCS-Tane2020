import serial

ser = serial.Serial('/dev/ttyS0', 115200)
line = ser.readline()
ser.close()