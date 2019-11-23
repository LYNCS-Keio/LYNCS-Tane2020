import sys, pathlib
sys.path.append( str(pathlib.Path(__file__).resolve().parent) + '/../' )
import pigpio
from i2c_bus import *
from consts import *


class dps310():
    def __init__(self, handler, addr):
        self.addr = addr
        self.p_osr = None; self.p_rate = None; self.t_osr = None; self.t_rate = None; self.Traw_sc_pre = None

        try:
            self.__bus = i2c_bus(handler, self.addr)
        except:
            self.state = opMode.ERR
            raise DPS_FAILED_INIT
        else:
            self.state = opMode.IDLE

    def setup(self, mode, p_rate, p_osr, t_rate, t_osr):
        try:
            self.set_OpMode(mode)
        except:
            raise DPS_FAILED_SETUP
        try:
            self.config_Pressure(p_rate, p_osr)
        except:
            raise DPS_FAILED_SETUP
        try:
            self.config_Temperature(t_rate, t_osr)
        except:
            raise DPS_FAILED_SETUP

    def convert_complement(self, data, bits):
        if (data & (1 << (bits -1))):
            data = -(~(data - 1) & (1 << bits) -1)
        return data

    def set_OpMode(self, mode):
        try:
            self.__bus.writeByteBitfield(config_register.MEAS_CTRL[0], config_register.MEAS_CTRL[1], config_register.MEAS_CTRL[2], mode)
        except:
            self.state = opMode.ERR
            raise DPS_FAILED_WRITING
        else:
            self.state = mode

    def get_coeffs(self):
        try:
            buf = self.__bus.readBytes(data_registers.COEFFS[0], data_registers.COEFFS[1])
        except:
            self.state = opMode.ERR
            raise DPS_FAILED_READING
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

    def config_Pressure(self, rate, osr):
        try:
            self.__bus.writeByteBitfield(config_registers.PRS_CONF[0], config_registers.PRS_CONF[1], config_registers.PRS_CONF[2], rate << 4 | osr)
        except:
            self.state = opMode.ERR
            raise DPS_FAILED_WRITING
        else:
            self.p_osr = osr
            self.p_rate = rate
            try:
                if osr > measurement_conf.MEAS_RATE_8:
                    self.__bus.writeByteBitfield(registers.PRS_SE[0], registers.PRS_SE[1], registers.PRS_SE[2], 1)
                else:
                    self.__bus.writeByteBitfield(registers.PRS_SE[0], registers.PRS_SE[1], registers.PRS_SE[2], 0)
            except:
                self.state = opMode.ERR
                raise DPS_FAILED_WRITING

    def config_Temperature(self, rate, osr):
        try:
            self.__bus.writeByteBitfield(config_registers.TMP_CONF[0], config_registers.TMP_CONF[1], config_registers.TMP_CONF[2], rate << 4 | osr)
        except:
            self.state = opMode.ERR
            raise DPS_FAILED_WRITING
        else:
            self.t_osr = osr
            self.t_rate = rate
            try:
                if osr > measurement_conf.MEAS_RATE_8:
                    self.__bus.writeByteBitfield(registers.TMP_SE[0], registers.TMP_SE[1], registers.TMP_SE[2], 1)
                else:
                    self.__bus.writeByteBitfield(registers.TMP_SE[0], registers.TMP_SE[1], registers.TMP_SE[2], 0)
            except:
                self.state = opMode.ERR
                raise DPS_FAILED_WRITING

    def read_Pressure(self):
        if ((self.state == opMode.CONT_PRS) or (self.state == opMode.CONT_BOTH)) and self.Traw_sc_pre != None:
            try:
                buf = self.__bus.readBytes(data_registers.PRS[0], data_registers.PRS[1])
            except:
                raise DPS_FAILED_READING
            else:
                calc_prs = lambda x: (x**3)*self.c30 + (x**2)*(self.c20 + self.Traw_sc_pre*self.c21) + \
                    x*(self.c10 + self.Traw_sc_pre*self.c11) + self.Traw_sc_pre*self.c01 + self.c00

                raw = self.convert_complement(buf[0] << 16 | buf[1] << 8 | buf[2], 24)
                return calc_prs(raw / scale_factor.scale_factors[self.p_osr])
        else:
            raise DPS_STATUS_ERROR

    def read_Temperature(self):
        if (self.state == opMode.CONT_TMP) or (self.state == opMode.CONT_BOTH):
            try:
                buf = self.__bus.readBytes(data_registers.TMP[0], data_registers.TMP[1])
            except:
                raise DPS_FAILED_READING
            else:
                calc_tmp = lambda x: self.c0*0.5 + self.c1*x
                raw = self.convert_complement(buf[0] << 16 | buf[1] << 8 | buf[2], 24)
                self.Traw_sc_pre = raw / scale_factor.scale_factors[self.t_osr]
                return calc_tmp(self.Traw_sc_pre)
        else:
            raise DPS_STATUS_ERROR


if __name__ == "__main__":
    pi = pigpio.pi()
    dps = dps310(pi, 0x77)
    dps.set_OpMode(opMode.CONT_BOTH)
    dps.config_Pressure(measurement_conf.MEAS_RATE_16,measurement_conf.MEAS_RATE_16)
    print(dps.read_Pressure())
