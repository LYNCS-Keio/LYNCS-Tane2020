import serial
import pigpio
import time

pi = pigpio.pi()
h1 = pi.serial_open("/dev/ttyS0", 115200)

# ser = serial.Serial('/dev/ttyS0', 115200)

buf = [0x00, 0x10, 0x11, 0x22, 0x33, 0xAA, 0xBB, 0xCC]
header = [0xA5, 0x5A]

while True:
# binary
    checksum = 0x00
    for i in range(len(buf)):
        checksum = checksum ^ buf[i]
    
    cmd_size = len(buf)
    cmd = 0x8000 + cmd_size

    pi.serial_write(h1, [0xA5, 0x5A, 0x80, 0x08, 0x00, 0xA0, 0x13, 0x00, 0xFF, 0x12, 0x34, 0x56, 0x3D, 0x04])
    # i.serial_write(h1, header + [cmd >> 8, cmd & 0x11111111] + buf + [checksum])

    print([0xA5, 0x5A, 0x80, 0x08, 0x00, 0xA0, 0x13, 0x00, 0xFF, 0x12, 0x34, 0x56, 0x3D, 0x04])
    # print(header + [0x80, 0x08] + buf + [checksum])



# ascii
    # data = ':0001112233AABBCCXX\r\n'
    # pi.serial_write(h1, data)
    # # ser.write(data)
    # # print(data)


    time.sleep(0.1)

ser.close()
