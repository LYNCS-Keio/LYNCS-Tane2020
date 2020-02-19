from package import icm20948
from package import madgwick_py
import pigpio
import time
from math import pi

po = pigpio.pi()
icm = icm20948.icm20948(po)
mad = madgwick_py.MadgwickAHRS(0.05)
lt = time.time()
while True:
    ax, ay, az, gx, gy, gz = icm.read_accelerometer_gyro_data()
    mx, my, mz = icm.read_magnetometer_data()
    gx,gy,gz=gx*pi/180,gy*pi/180,gz*pi/180
    if (time.time()-lt) > 0.05:
        mad.update([gx,gy,gz],[ax,ay,az],[mx,-my,-mz])
        x,y,z=mad.quaternion.to_euler_angles()
        x,y,z=x*180/pi,y*180/pi,z*180/pi
        print('{:05.2f} {:05.2f} {:05.2f}'.format(x,y,z))
        lt = time.time()

