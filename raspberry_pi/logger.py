import pigpio 
import csv
import os
import time
import dps310
import icm20948

pi = pigpio.pi()
dps = dps310.dps310(pi)
icm = icm20948.icm20948(pi)

index = 0
current_dir = os.path.dirname(os.path.abspath(__file__))
filename = 'log' + '%04d' % index
while os.path.isfile(current_dir + '/' + filename + '.csv') == True:
    index += 1
    filename = 'log' + '%04d' % index

with open(current_dir + '/' + filename + '.csv', 'w') as c:
    wri = csv.writer(c, lineterminator = '\n')
    while True:
        dps.set_OpMode(opMode.IDLE)
        dps.get_coeffs()
        dps.config_Pressure(measurement_conf.MEAS_RATE_16,measurement_conf.MEAS_RATE_16)
        dps.config_Temperature(measurement_conf.MEAS_RATE_32, measurement_conf.MEAS_RATE_32)
        dps.set_OpMode(opMode.CONT_BOTH)
        while True:
            results = []
            results.append(dps.read_Temperature())
            results.append(dps.read_Pressure())
            results.extend(icm.read_magnetometer_data())
            results.extend(icm.read_accelerometer_gyro_data())
            print(results)
            wri.writerow(results)
            time.sleep(0.01)
pi.stop()
  