from lib import i2c_bus
import pigpio
import time
import datetime

address_dps310 = 0x77
pi = pigpio.pi()
bus = i2c_bus.i2c_bus(pi, address_dps310)

def read_dps310():
    # 気圧
    p1 = bus.readByte(0x00)
    p2 = bus.readByte(0x01)
    p3 = bus.readByte(0x02)
    p = p1
    p = p<<8
    p = p | p2
    p = p<<8
    p = p | p3
    if p & (1<<23):
        p = p - (1<<24)
    # 温度
    t1 = bus.readByte(0x03)
    t2 = bus.readByte(0x04)
    t3 = bus.readByte(0x05)
    t = t1
    t = t<<8
    t = t | t2
    t = t<<8
    t = t | t3
    if t & (1<<23):
        t = t - (1<<24)
    p_raw_sc = p / 1040384
    t_raw_sc = t / 1040384
    source13 = bus.readByte(0x13)
    source14 = bus.readByte(0x14)
    source15 = bus.readByte(0x15)
    source16 = bus.readByte(0x16)
    source17 = bus.readByte(0x17)
    source18 = bus.readByte(0x18)
    source19 = bus.readByte(0x19)
    source1A = bus.readByte(0x1A)
    source1B = bus.readByte(0x1B)
    source1C = bus.readByte(0x1C)
    source1D = bus.readByte(0x1D)
    source1E = bus.readByte(0x1E)
    source1F = bus.readByte(0x1F)
    source20 = bus.readByte(0x20)
    source21 = bus.readByte(0x21)
    c00 = source13
    c00 = c00<<8
    c00 = c00 | source14
    c00 = c00<<8
    c00 = c00 | source15
    c00 = c00>>4
    if c00 & (1<<19):
        c00 = c00 - (1<<20)
    c10 = source15 & 0x0F
    c10 = c10<<8
    c10 = c10 | source16
    c10 = c10<<8
    c10 = c10 | source17
    if c10 & (1<<19):
        c10 = c10 - (1<<20)
    c01 = source18
    c01 = c01<<8
    c01 = c01 | source19
    if c01 & (1<<15):
        c01 = c01 - (1<<16)
    c11 = source1A
    c11 = c11<<8
    c11 = c11 | source1B
    if c11 & (1<<15):
        c11 = c11 - (1<<16)
    c20 = source1C
    c20 = c20<<8
    c20 = c20 | source1D
    if c20 & (1<<15):
        c20 = c20 - (1<<16)
    c21 = source1E
    c21 = c21<<8
    c21 = c21 | source1F
    if c21 & (1<<15):
        c21 = c21 - (1<<16)
    c30 = source20
    c30 = c30<<8
    c30 = c30 | source21
    if c30 & (1<<15):
        c30 = c30 - (1<<16)
    #pcomp = c00 + p_raw_sc * (c10 + p_raw_sc * (c20 + p_raw_sc * c30)) + t_raw_sc * (c01 + p_raw_sc * (c11 + p_raw_sc * c21))
    pcomp = c00 + p_raw_sc * (c10 + p_raw_sc * (c20 + p_raw_sc * c30)) + t_raw_sc * c01 + t_raw_sc * p_raw_sc * (c11 + p_raw_sc * c21)
    return pcomp

def setup():
    # オーバーサンプリング 64time
    bus.writeByte(0x06, 0x26)
    time.sleep(1)
    bus.writeByte(0x07, 0xA6)
    time.sleep(1)
    bus.writeByte(0x08, 0x07)
    time.sleep(1)
    # コンフィグ(オーバーサンプリングを可能に)
    bus.writeByte(0x09, 0x0C)
    time.sleep(1)

setup()
bus.readByte(0x77)

if __name__ == "__main__":
    try:
        while True:
            print(bus.readByte(0x77))
            time.sleep(0.01)

    except KeyboardInterrupt:
        pass
