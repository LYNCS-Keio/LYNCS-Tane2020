import serial

ser = serial.Serial('/dev/ttyS0', 115200)
while True:
    ser.write("HELLO!!!")
ser.close()