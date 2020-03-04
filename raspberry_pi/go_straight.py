# -*-coding: utf-8 -*-

from package import pid_controll
from package import icm20948
# from package import madgwick_py
import pigpio
import time
from math import pi as PI
from math import atan2
from statistics import mean


def calibrate_mag(sec):
    Flag = True
    pi.hardware_PWM(12, 50, 75000)
    pi.hardware_PWM(13, 50, 75000)
    time.sleep(0.1)
    s_t = time.time()
    while Flag:
        pi.hardware_PWM(13, 50, 90000)
        pi.hardware_PWM(12, 50, 90000)
        try:
            x, y, z = icm.read_magnetometer_data()
        except　KeyboardInterrupt:
            raise KeyboardInterrupt
        finally:
            pass

        y,z = -y,-z
        
        dx = x - b[0]
        dy = y - b[1]
        dz = z - b[2]
        f = dx*dx + dy*dy + dz*dz - b[3]*b[3]
        
        b[0] = b[0] + 4 * lr * f * dx
        b[1] = b[1] + 4 * lr * f * dy
        b[2] = b[2] + 4 * lr * f * dz
        b[3] = b[3] + 4 * lr * f * b[3]
        if (time.time() - s_t) > sec:
            Flag = False
    pi.hardware_PWM(12, 50, 75000)
    pi.hardware_PWM(13, 50, 75000)


def calc_drift(sec):
    pi.hardware_PWM(13, 50, 75000)
    pi.hardware_PWM(12, 50, 75000)
    Flag = True
    gx_drift = []
    gy_drift = []
    gz_drift = []
    time.sleep(0.1)
    s_t = time.time()
    while Flag:
        try:
            ax, ay, az, gx, gy, gz = icm.read_accelerometer_gyro_data()
            gx_drift.append(gx)
            gy_drift.append(gy)
            gz_drift.append(gz)
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        finally:
            pass
        if (time.time() - s_t) > sec:
            Flag = False
    gx_drift = mean(gx_drift)
    gy_drift = mean(gy_drift)
    gz_drift = mean(gz_drift)


def update_azimuth():
    mx, my, mz = icm.read_magnetometer_data()
    azimuth = atan2(my-b[1], mx-b[0])*180/PI


pi = pigpio.pi()

pi.set_mode(13, pigpio.OUTPUT)
pi.set_mode(12, pigpio.OUTPUT)
pi.hardware_PWM(13, 50, 75000)
pi.hardware_PWM(12, 50, 75000)


icm = icm20948.icm20948(pi)
p = pid_controll.pid(0.002, 0.005, 0.003)
# mad = madgwick_py.MadgwickAHRS()

b = [30.0, 0.0, 15.0, 20]
lr = 0.0001

SPEED = 0.7

try:
    calibrate_mag(30)
    update_azimuth()
    calc_drift(30)
    
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

        # mad.update([gx,gy,gz], [ax,ay,az], [mx,-my,-mz])
        # x, y, z = mad.quaternion.to_euler_angles()
        # x, y, z = x*180/PI, y*180/PI, z*180/PI

        nt = time.time()
        dt = nt - pt
        pt = nt
        azimuth += gz*dt
        m = p.update_pid(0, azimuth, dt)

        m1 = min([max([m, -1]), 1])

        dL, dR = 75000 + 12500 * (SPEED - m1), 75000 - 12500 * (SPEED + m1)
        pi.hardware_PWM(13, 50, int(dL))
        pi.hardware_PWM(12, 50, int(dR))

except KeyboardInterrupt:
    pass        

finally:
    pi.hardware_PWM(12, 0, 0)
    pi.hardware_PWM(13, 0, 0)
    pi.stop()
