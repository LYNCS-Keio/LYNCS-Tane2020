from package.lib import i2c_bus
import pigpio

pi = pigpio.pi()

bus = i2c_bus.i2c_bus(pi, 0x77)
print(bin(bus.readByte(0x0D)))