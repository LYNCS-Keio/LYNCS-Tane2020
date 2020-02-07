import serial

ser = serial.Serial('/dev/ttyS0', 115200)
ser.write("HELLO!!!")
ser.close()