import sys, pathlib
sys.path.append( str(pathlib.Path(__file__).resolve().parent) + '/../' )
import i2c_bus
import pigpio
import time
import datetime

address_dps310 = 0x77
pi = pigpio.pi()
bus = i2c_bus.i2c_bus(pi, address_dps310)

coe = []

def read_Data():
    # pressure
    p1 = bus.readByte(0x00)
    p2 = bus.readByte(0x01)
    p3 = bus.readByte(0x02)
    p = ((p1 << 16) | (p2 << 8) | p3)
    if p & (1<<23):
        p = p - (1<<24)
    # temperature
    t1 = bus.readByte(0x03)
    t2 = bus.readByte(0x04)
    t3 = bus.readByte(0x05)
    t = ((t1 << 16) | (t2 << 8) | t3)    
    if t & (1<<23):
        t = t - (1<<24)

    p_raw_sc = p / 1040384
    t_raw_sc = t / 1040384    
    pcomp = coe[0] + p_raw_sc * (coe[1] + p_raw_sc * (coe[4] + p_raw_sc * coe[6])) + t_raw_sc * coe[2] + t_raw_sc * p_raw_sc * (coe[3] + p_raw_sc * coe[5])
    return pcomp


def get_calib_coefficient():
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

    coe.append(((source13 << 16) | (source14 << 8) | source15) >> 4)
    coe.append(((source15 & 0x0F) << 16) | (source16 << 8) | source17)
    coe.append((source18 << 8) | source19)
    coe.append((source1A << 8) | source1B)
    coe.append((source1C << 8) | source1D)
    coe.append((source1E << 8) | source1F)
    coe.append((source20 << 8) | source21)
    for i in range(7):
        if i <= 1:
            if (coe[i] & (1<<19)):
                coe[i] = coe[i] - (1<<20)
        else:
            if (coe[i] & (1<<15)):
                coe[i] = coe[i] - (1<<16)

def setup():
    # oversampling
    bus.writeByte(0x06, 0x26)
    time.sleep(1)
    bus.writeByte(0x07, 0xA6)
    time.sleep(1)
    bus.writeByte(0x08, 0x07)
    time.sleep(1)
    bus.writeByte(0x09, 0x0C)
    time.sleep(1)

setup()
get_calib_coefficient()

if __name__ == "__main__":
    try:
        while True:
            print(read_Data())
            time.sleep(0.01)

    except KeyboardInterrupt:
        pass
