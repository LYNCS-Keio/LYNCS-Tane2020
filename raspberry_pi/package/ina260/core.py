#thanks to https://github.com/charkster/INA260/blob/master/INA260_MINIMAL.py

import sys, pathlib
sys.path.append( str(pathlib.Path(__file__).resolve().parent) + '/../' )
from i2c_bus import *


class _INA_ERROR(Exception):
    "ina260 base error"

class INA_FAILED(_INA_ERROR):
    "Something went wrong on ina260"

class INA_FAILED_INIT(_INA_ERROR):
    "Failed initializing ina260"

class INA_FAILED_SETUP(_INA_ERROR):
    "Failed setting up ina260"

class INA_FAILED_READING(_INA_ERROR):
    "Failed reading data from the ina260"

class INA_FAILED_WRITING(_INA_ERROR):
    "Failed writing data on the ina260"


class register():
    CONFIG_REG      = 0x00
    CURRENT_REG     = 0x01
    BUS_VOL_REG     = 0x02
    POWER_REG       = 0x03
    MASK_ENABLE_REG = 0x06
    ALERT_LIMIT_REG = 0x07


class ina260():
    def __init__(self, handler, ina_addr=0x40):
        self.addr = ina_addr
        self.lsb = 1.25

        try:
            self.__bus = i2c_bus(handler, self.addr)
        except:
            raise INA_FAILED_INIT


    def get_voltage(self):
        """
        電圧を取得する。

        Returns
        -------
        vol : float or None
            　単位はV。つながっていなければNoneを返す。
        """
        try:
            raw = self.__bus.readBytes(register.BUS_VOL_REG, 2)
        except:
            raise INA_FAILED_READING
        word_data = raw[0] << 8 | raw[1]
        vol = float(word_data) / 1000 * self.lsb
        return vol 


    def get_current(self):
        """
        電圧を取得する。

        Returns
        -------
        current : float or None
                  単位はA。つながっていなければNoneを返す。
        """
        try:
            raw = self.__bus.readBytes(register.CURRENT_REG, 2)
        except:
            raise INA_FAILED_READING
        word_data = raw[0] << 8 | raw[1]
        current_sign_bit = word_data >> 15
        if (current_sign_bit == 1 and word_data & 1 << 15):
            word_data -= 1 << 16

        current = float(word_data) / 1000 * self.lsb
        return current

    def reset_chip(self):
        try:
            self.__bus.writeWordBitfield(register.CONFIG_REG, 0x8000, 15, 1)
        except:
            raise INA_FAILED_WRITING


if __name__ == '__main__':
    import pigpio
    import time
    pi = pigpio.pi()
    ina = ina260(pi)
    try:
        while True:
            print (ina.get_voltage(), ina.get_current())
            time.sleep(0.05)
    
    finally:
        pass
