import pigpio

ADDR = 0x77
pi = pigpio.pigpio()

try:
    bus = pi.i2c_open(1, 0x77)
except:
    print("Opening Error")
finally:
    

try:

finally:
    pi.i2c_close(bus)