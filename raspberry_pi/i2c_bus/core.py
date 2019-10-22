import pigpio

class I2C_ERROR(Exception):
    "I2C class error"

class I2C_FAILED(I2C_ERROR):
    "Something went wrong"

class I2C_FAILED_OPEN(I2C_ERROR):
    "Failed Opening bus error"

class I2C_FAILED_READING(I2C_ERROR):
    "Failed reading the device"

class I2C_FAILED_WRITING(I2C_ERROR):
    "Failed writing on the device"


class bus():
    def __init__(self, handler, addr):
        self.pi = handler
        self.addr = addr
        try:
            self.bus = self.pi.i2c_open(1, self.addr)
        except TypeError:
            raise TypeError
        except:
            raise I2C_FAILED_OPEN

    def readByte(self, reg):
        try:
            val = self.pi.i2c_read_byte_data(self.bus, reg)
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
            val = self.pi.i2c_read_i2c_block_data(self.bus, reg, length)
        except:
            raise I2C_FAILED_READING
        else:
            return val

    def writeByte(self, reg, data):
        try:
            self.pi.i2c_write_byte_data(self.bus, reg, data)
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

