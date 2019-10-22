import pigpio

ADDR = 0x77
pi = pigpio.pi()

try:
    bus = pi.i2c_open(1, 0x77)
    ret = pi.i2c_read_byte_data(bus, 0x0D)
    print(bin(ret))

except:
    print("Error Opening File")

finally:
    pi.i2c_close(bus)