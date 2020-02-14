from package import rover_gps as gps
from package import dps310
from package import icm20948
from package import ina260
from package import twelite
from package import pid_controll

import time
import pigpio
import math
import threading
import toml


def pressure_while(height_threshold, continuous_number, mode): #mode　1：data >= threshold   -1:data <= threshold
    dps = dps310(pi, 0x77)
    dps.set_OpMode(opMode.IDLE)
    dps.get_coeffs()
    dps.config_Pressure(measurement_conf.MEAS_RATE_16,measurement_conf.MEAS_RATE_16)
    dps.config_Temperature(measurement_conf.MEAS_RATE_32, measurement_conf.MEAS_RATE_32)
    dps.set_OpMode(opMode.CONT_BOTH)

    n = 0
    while n < continuous_number:
        height = dps.mesure_high()
        if (mode)*height >= (mode)*height_threshold:
            n += 1
        else:
            n = 0
        time.sleep(0.01)
         

pi = pigpio.pi()
toml_dic = toml.load(open('config.toml'))

pressure_while(toml_dic['height']['high'], toml_dic['height']['continue_number'], 1)
pressure_while(toml_dic['height']['low'], toml_dic['height']['continue_number'], -1)


