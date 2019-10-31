import sys, pathlib
sys.path.append( str(pathlib.Path(__file__).resolve().parent) + '/../' )
import i2c_bus
import pigpio
from consts import opMode, config_registers, registers, measurement_rate


class dps310(opMode):
    def __init__(self, handler, addr):
        self.addr = addr
        self.p_prc = None; self.p_rate = None; self.t_prc = None; self.t_rate = None
        
        try:
            self.bus = i2c_bus.i2c_bus(handler, self.addr)
        except:
            self.state = opMode.ERR
            raise TypeError
        else:
            self.state = opMode.IDLE

    def convert_complement(self, data, bits):
        if (data & (1 << (bits -1))):
            data = -(~(data - 1) & (1 << bits) -1)
        return data
        
    def set_OpMode(self, mode):
        try:
            self.bus.writeByteBitfield(config_register.MSR_CTRL[0], config_register.MSR_CTRL[1], config_register[2], mode)
        except:
            self.state = opMode.ERR
            raise i2c_bus.I2C_FAILED_WRITING
        else:
            self.state = mode

    def get_coeffs(self):
        try:
            buf = self.bus.readBytes(0x10, 18)
        except:
            self.state = opMode.ERR
            raise i2c_bus.I2C_FAILED_READING
        else:
            self.c0  = self.convert_complement(buf[0] << 4 | buf[1] >> 4, 12)
            self.c1  = self.convert_complement((buf[1] & 0x0F) << 8 | buf[2], 12)
            self.c00 = self.convert_complement(buf[3] << 12 | buf[4] << 4 | buf[5] >> 4, 20)
            self.c10 = self.convert_complement((buf[5] & 0x0F) << 16 | buf[6] << 8 | buf[7], 20)
            self.c01 = self.convert_complement(buf[8] << 8 | buf[9], 16)
            self.c11 = self.convert_complement(buf[10] << 8 | buf[11], 16)
            self.c20 = self.convert_complement(buf[12] << 8 | buf[13], 16)
            self.c21 = self.convert_complement(buf[14] << 8 | buf[15], 16)
            self.c30 = self.convert_complement(buf[16] << 8 | buf[17], 16)

    def config_Pressure(self, rate, prc):
        try:
            self.bus.writeByteBitfield(config_registers.PM_RATE[0], config_registers.PM_RATE[1], config_registers.PM_RATE[2], rate << 4 | prc)
        except:
            self.state = opMode.ERR
            raise i2c_bus.I2C_FAILED_WRITING
        else:
            self.p_prc = prc
            self.p_rate = rate
            try:
                if prc > measurement_rate.MEAS_RATE_8:
                    pass
                else:
                    pass
            except:
                self.state = opMode.ERR
                raise i2c_bus.I2C_FAILED_WRITING

    def config_Temperature(self):
        pass

    def read_Pressure(self):
        pass

    def read_Temperature(self):
        pass