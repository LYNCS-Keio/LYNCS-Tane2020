import serial
import pigpio
import time

pi = pigpio.pi()
h1 = pi.serial_open("/dev/ttyS0", 115200)

# ser = serial.Serial('/dev/ttyS0', 115200)

buf = [0x11, 0x22, 0x33, 0xAA, 0xBB, 0xCC]
header = [0xA5, 0x5A]

while True:
# binary
    buf = 0x112233AABBCC
    header = 0xA55A
    checksum = 0x00
    for i in range(len(header)):
        checksum = checksum ^ header[i]
    for i in range(len(buf)):
        checksum = checksum ^ buf[i]
    
    cmd_size = len(header) + len(buf)
    cmd = 0x8000 + cmd_size

    pi.serial_write(h1, header + [0x80, 0x08] + buf + [checksum])
    # pi.serial_write(h1, header)
    # pi.serial_write(h1, [0x80, 0x08])
    # pi.serial_write(h1, cmd >> 8 & 0b11111111)
    # pi.serial_write(h1, buf)
    # pi.serial_write(h1, [checksum])
    
    print(h1, header)
    print(h1, cmd >> 8)
    print(h1, cmd & 0b11111111)
    print(h1, buf)
    print(h1, [checksum])




# ascii
    # data = ':0001112233AABBCCXX\r\n'
    # pi.serial_write(h1, data)
    # # ser.write(data)
    # # print(data)


    time.sleep(0.1)

ser.close()
