import pigpio

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
        self.pi = handler
        self.addr = addr
        print("HELLO")
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
            (ret, val) = self.pi.i2c_read_i2c_block_data(self.bus, reg, length)
            if ret >= 0:
                int_val = [x for x in val]
            else:
                raise I2C_FAILED_READING
        except:
            raise I2C_FAILED_READING
        else:
            return int_val

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

    def __del__(self):
        self.pi.i2c_close(self.bus)
