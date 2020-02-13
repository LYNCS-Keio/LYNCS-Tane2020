import serial
import pigpio
import time

pi = pigpio.pi()
h1 = pi.serial_open("/dev/ttyS0", 115200)

# data = ':DBF306X'
# pi.serial_write(h1, data)

buf = [0xA5, 0x5A, 0xF2, 0x06, 0x02]

checksum = 0x00
for i in range(len(buf)):
    checksum = checksum ^ buf[i]

pi.serial_write(h1, [0xA5, 0x5A, 0xF2, 0x06, 0x02] + [checksum])
print(buf + [checksum])

time.sleep(1)

line = pi.serial_read(h1)
print(line)
