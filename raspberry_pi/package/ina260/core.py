#thanks to https://github.com/charkster/INA260/blob/master/INA260_MINIMAL.py

import pigpio

pi = pi.pigpio()
ina_addr     = 0x44
config_addr  = 0x00
current_addr = 0x01
vol_addr     = 0x02
lsb          = 1.25

ina = pi.i2c_open(1, ina_addr)

def get_vol():
    raw = pi.i2c_read_i2c_block_data(ina, vol_addr, 2)
    word_data = raw[0] *256 + raw[1]
    vol = float(word_data) / 1000 * lsb
    return vol 

def get_current():
    raw = pi.i2c_read_i2c_block_data(ina, current_addr, 2)
    word_data = raw[0] *256 + raw[1]
    current_sign_bit = word_data >> 15
    if (current_sign_bit == 1 and word_data & 1 << 15):
        word_data -= 1 << 16

    current = float(word_data) / 1000 * lsb
    return current

def reset_chip():
    byte_list = [0x80, 0x00]
    pi.i2c_write_i2c_block_data(ina_addr, config_addr, byte_list)

