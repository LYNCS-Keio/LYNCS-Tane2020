#thanks to https://github.com/charkster/INA260/blob/master/INA260_MINIMAL.py

import pigpio

class ina:
    def __init__(self):
        self.pi = pigpio.pi()
        ina_addr     = 0x40
        self.config_addr  = 0x00
        self.current_addr = 0x01
        self.vol_addr     = 0x02
        self.lsb          = 1.25

        try:
            self.bus = self.pi.i2c_open(1, ina_addr)
        except:
            print("Failed initializing ina260")

    def get_vol(self):
        try:
            raw = self.pi.i2c_read_i2c_block_data(self.bus, self.vol_addr, 2)[1]
        except:
            print("Failed getting vol_data ina260")
        word_data = raw[0] *256 + raw[1]
        vol = float(word_data) / 1000 * self.lsb
        return vol 

    def get_current(self):
        try:
            raw = self.pi.i2c_read_i2c_block_data(self.bus, self.current_addr, 2)[1]
        except:
            print("Failed getting current_data ina260")
        word_data = raw[0] *256 + raw[1]
        current_sign_bit = word_data >> 15
        if (current_sign_bit == 1 and word_data & 1 << 15):
            word_data -= 1 << 16

        current = float(word_data) / 1000 * self.lsb
        return current

    def reset_chip(self):
        byte_list = [0x80, 0x00]
        try:
            self.pi.i2c_write_i2c_block_data(self.bus, self.config_addr, byte_list)
        except:
            print("Failed reset_chip ina260")

if __name__ == '__main__':
    i = ina()
    print (i.get_vol(), i.get_current())
