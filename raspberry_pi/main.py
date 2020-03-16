from package import rover_gps as gps
from package import dps310
from package import icm20948
from package import ina260
from package import pid_controll
#from package import twelite
#from package import camera
#from package import capture

import time
import pigpio
import math
import threading
import toml
import run

pi = pigpio.pi()
icm = icm20948.icm20948(pi)
toml_dic = toml.load(open('config.toml'))
p = pid_controll.pid(toml_dic['PID']['P'], toml_dic['PID']['I'], toml_dic['PID']['D'])

threshold_high = toml_dic['height']['high']
threshold_low = toml_dic['height']['low']
continuous_number = toml_dic['height']['continue_number']

camera_distance = toml_dic['camera']['start_distance']
pinL = toml_dic['pin']['Rmotor']
pinR = toml_dic['pin']['Lmotor']
goal = [toml_dic['gps']['goal_lat'], toml_dic['gps']['goal_long']]

lr = toml_dic['icm_calib']['learning_rate']
b = [30.0, 0.0, 15.0, 20]
drift = [0,0,0]
azimuth = 0

def pressure_while(height_threshold, continuous_number, mode)
    dps = dps310(pi, 0x77)
    dps.set_OpMode(opMpde.IDLE)
    dps.get_coeffs()
    dps.config_Pressure(mesurement_conf.MEAS_RATE_16, measurement_conf.MEAS_RATE_16)
    dps.config_Temperature(mesurement_conf.MEAS_RATE_32, measurement_conf.MEAS_RATE_32)
    dps.set_OpMode(opMode.CONT_BOTH)

    n = 0
    while n < continuous_number:
        height = dps.measurement_high()
        if (mode)*height >= (mode)*height_threshold:
            n += 1
        else:
            n = 0
        time.sleep(0.01)

try:
    pressure_while(threshold_high, continuous_number, 1)
    release_time = time.time() # 落下開始
    pressure_while(threshold_low, continuous_number, -1)

except KeyboardInterrupt:
    pass        

finally:
    pi.hardware_PWM(12, 0, 0)
    pi.hardware_PWM(13, 0, 0)


def update_target_gps():
    global to_goal
    while UPDATE_GPS:
        now = gps.lat_long_measurement()
        if now != [0, 0]:
            to_goal = gps.convert_lat_long_to_r_theta(*now, *goal)


try:
    pi.set_mode(pinL, pigpio.OUTPUT)
    pi.set_mode(pinR, pigpio.OUTPUT)
    pi.hardware_PWM(pinL, 50, 75000)
    pi.hardware_PWM(pinR, 50, 75000)

    run.calibrate_mag(pi, icm, 30, b, lr)
    azimuth = run.update_azimuth(icm, b)
    run.calc_drift(pi, icm, 30, drift)

    UPDATE_GPS = True
    GPS_THREAD = threading.Thread(target=update_target_gps)
    GPS_THREAD.start()
    
    speed = 0.7
    pt = time.time()
    while True:
        try:
            ax, ay, az, gx, gy, gz = icm.read_accelerometer_gyro_data()
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            gz = 0
        finally:
            pass
        
        nt = time.time()
        dt = nt - pt
        pt = nt
        azimuth += gz*dt
        m = p.update_pid(to_goal[1], azimuth, dt)

        m1 = min([max([m, -1]), 1])

        dL, dR = 75000 + 12500 * (speed - m1), 75000 - 12500 * (speed + m1)
        pi.hardware_PWM(13, 50, int(dL))
        pi.hardware_PWM(12, 50, int(dR))

except KeyboardInterrupt:
    pass        

finally:
    UPDATE_GPS = False
    pi.hardware_PWM(12, 0, 0)
    pi.hardware_PWM(13, 0, 0)
