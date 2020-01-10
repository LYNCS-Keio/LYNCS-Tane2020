import core as dps
import csv
import os
import time
import sys
import pigpio

current_dir = os.path.dirname(os.path.abspath(__file__))

index = 0
filename = 'dps_log' + '%04d' % index
while os.path.isfile(current_dir + '/' + filename + '.csv') == True:
    index += 1
    filename = 'dps_log' + '%04d' % index

with open(current_dir + '/' + filename + '.csv', 'w') as c:
    wri = csv.writer(c, lineterminator = '\n')
    pi = pigpio.pi()
    while True:
        data = dps.dps310(pi, 0x77)
        data.set_OpMode(opMode.IDLE)
        data.get_coeffs()
        data.config_Pressure(measurement_conf.MEAS_RATE_16,measurement_conf.MEAS_RATE_16)
        data.config_Temperature(measurement_conf.MEAS_RATE_32, measurement_conf.MEAS_RATE_32)
        data.set_OpMode(opMode.CONT_BOTH)
        while True:
            results = []
            temp = data.read_Temperature()
            press = data.read_Pressure()
            results.append(temp)
            results.append(press)
            print(results)
            wri.writerow(results)
            time.sleep(0.01)
pi.stop()