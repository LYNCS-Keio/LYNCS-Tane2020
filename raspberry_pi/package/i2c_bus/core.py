import pigpio

""" description
pigpioを用いたi2c library



"""

__all__ = ['I2C_FAILED', 'I2C_FAILED_OPEN', 'I2C_FAILED_READING', 'I2C_FAILED_WRITING', 'i2c_bus']

class _I2C_ERROR(Exception):
    "i2c_bus base error"

class I2C_FAILED(_I2C_ERROR):
    "Something went wrong on i2c_bus"

class I2C_FAILED_OPEN(_I2C_ERROR):
    "Failed Opening bus error"

class I2C_FAILED_READING(_I2C_ERROR):
    "Failed reading the device"

class I2C_FAILED_WRITING(_I2C_ERROR):
    "Failed writing on the device"


class i2c_bus():
    def __init__(self, handler, addr):
        self.__pi = handler
        self.__addr = addr
        try:
            self.__bus = self.__pi.i2c_open(1, self.__addr)
        except TypeError:
            raise TypeError
        except:
            raise I2C_FAILED_OPEN

    def readByte(self, reg):
        try:
            val = self.__pi.i2c_read_byte_data(self.__bus, reg)
        except:
            raise I2C_FAILED_READING
        else:
            return val

    def readByteBitfield(self, reg, mask, shift):
        try:
            val = self.readByte(reg)
            val = (val & mask) >> shift
        except I2C_FAILED_READING:
            raise I2C_FAILED_READING
        except:
            raise I2C_FAILED
        else:
            return val

    def readBytes(self, reg, length):
        try:
            (ret, val) = self.__pi.i2c_read_i2c_block_data(self.__bus, reg, length)
            if ret >= 0:
                int_val = [x for x in val]
            else:
                raise I2C_FAILED_READING
        except:
            raise I2C_FAILED_READING
        else:
            return int_val

    def readWord(self, reg):
        try:
            val = self.__pi.i2c_read_word_data(self.__bus, reg)
        except:
            raise I2C_FAILED_READING
        else:
            return val

    def readWordBitfield(self, reg, mask, shift):
        try:
            val = self.readWord(reg)
            val = (val & mask) >> shift
        except I2C_FAILED_READING:
            raise I2C_FAILED_READING
        except:
            raise I2C_FAILED
        else:
            return val

    def writeByte(self, reg, data):
        try:
            self.__pi.i2c_write_byte_data(self.__bus, reg, data)
        except:
            raise I2C_FAILED_WRITING

    def writeByteBitfield(self, reg, mask, shift, data):
        try:
            old = self.readByte(reg)
        except I2C_FAILED_READING:
            raise I2C_FAILED_READING
        else:
            try:
                self.writeByte(reg, (old & ~mask) | (data << shift) & mask)
            except I2C_FAILED_WRITING:
                raise I2C_FAILED_WRITING

    def writeBytes(self, reg, data):
        try:
            self.__pi.i2c_write_i2c_block_data(self.__bus, reg, data)
        except:
            raise I2C_FAILED_WRITING

    def writeWord(self, reg, data):
        try:
            self.__pi.i2c_write_word_data(self.__bus, reg, data)
        except:
            raise I2C_FAILED_WRITING

    def writeWordBitfield(self, reg, mask, shift, data):
        try:
            old = self.readWord(reg)
        except I2C_FAILED_READING:
            raise I2C_FAILED_READING
        else:
            try:
                self.writeWord(reg, (old & ~mask) | (data << shift) & mask)
            except I2C_FAILED_WRITING:
                raise I2C_FAILED_WRITING

