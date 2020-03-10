from package import rover_gps as GPS
from package import dps310
from package import icm20948
from package import ina260
#from package import twelite
from package import pid_controll
#from package import camera
#from package import capture

import time
import pigpio
import math
import threading
import toml
import run

pi = pigpio.pi()
'''
def pressure_while(height_threshold, continuous_number, mode): #mode　1：data >= threshold   -1:data <= threshold
    dps = dps310.dps310(pi, 0x77)
    dps.set_OpMode(opMode.IDLE)
    dps.get_coeffs()
    dps.config_Pressure(measurement_conf.MEAS_RATE_16,measurement_conf.MEAS_RATE_16)
    dps.config_Temperature(measurement_conf.MEAS_RATE_32, measurement_conf.MEAS_RATE_32)
    dps.set_OpMode(opMode.CONT_BOTH)

    n = 0
    while n < continuous_number:
        height = dps.measure_high()
        if (mode)*height >= (mode)*height_threshold:
            n += 1
        else:
            n = 0
        time.sleep(0.01)
         
toml_dic = toml.load(open('config.toml'))

pressure_while(toml_dic['height']['high'], toml_dic['height']['continue_number'], 1)
pressure_while(toml_dic['height']['low'], toml_dic['height']['continue_number'], -1)
'''
cam_dis = 0.003 # ????????????(km)
forward_dis = 0.01 # ???????(km)

pinL = 13
pinR = 12

goal_lat, goal_long = 0, 0 #?????

lr = 0.0001

pi.set_mode(13, pigpio.OUTPUT)
pi.set_mode(12, pigpio.OUTPUT)
pi.hardware_PWM(13, 50, 75000)
pi.hardware_PWM(12, 50, 75000)

icm = icm20948.icm20948(pi)
p = pid_controll.pid(0.002, 0.005, 0.003)
# mad = madgwick_py.MadgwickAHRS()

b = [30.0, 0.0, 15.0, 20]
SPEED = 0.7


def gps_get():
    global to_goal, pre
    flag = 0
    while True:
        now = GPS.lat_long_measurement()
        if now[0] != None and now[1] != None:
            to_goal[0] = GPS.convert_lat_long_to_r_theta(now[0],now[1],goal_lat,goal_long)[0]
            print(to_goal[0])

            if flag == 0 and GPS.convert_lat_long_to_r_theta(pre[0], pre[1], now[0], now[1])[0] >= forward_dis:
                lock.acquire()
                to_goal[1] = -math.degrees(GPS.convert_lat_long_to_r_theta(now[0],now[1],goal_lat,goal_long)[1])
                lock.release()
                print("count!!!", now)
                pre = now
                flag = 1
            if to_goal[0] < cam_dis:
                break
'''
#tv_homing from Noshiro-2019
Aov = 54 # angle of view
height = 240
width = 320
rotation = 0
cam_interval = 1.5
area = 400
URwC_flag = 1

def update_rotation_with_cam():
    global rotation
    cap = capture.capture()
    cam = camera.CamAnalysis()
    while URwC_flag == 1:
        stream = cap.cap()
        cam.morphology_extract(stream)
        cam.save_all_outputs()
        coord = cam.contour_find()

        conX = ((coord[0] - width / 2) / (width / 2)) / math.sqrt(3)

        lock.acquire()
        rotation = math.degrees(math.atan(-conX))
        area = coord[2]
        lock.release()

        #print(coord[0], rotation)
'''
try:
    run.calibrate_mag(30, b, lr)
    run.update_azimuth()
    run.calc_drift(30)
    
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
'''
#tv_homing
try:
    URwC_thread = threading.Thread(target=update_rotation_with_cam)
    URwC_thread.start()
    #print('URwC start')
    pt = time.time()

    while True:
        #gyro = mpu.get_gyro_data_lsb()[2] + drift
        #nt = time.time()
        #dt = nt-pt
        #pt = nt
        rotation_lock.acquire()
        #rotation += gyro * dt
        rotation_lock.release()

        m = p.update_pid(0, rotation. dt)
        m1 = min(max(m, -1), 1)
        dL, dR = 75000 + 12500 + (1 - m1), 75000 - 12500 * (1 + m1)
        print([m1, rotation])

        pi.hardware_PWM(pinL, 50, int(dL))
        pi.hardware_PWM(pinR, 50, int(dR))

finally:
    URwC_flag = 0
    pi.hardware_PWM(pinL, 0, 0)
    pi.hardware_PWM(pinR, 0, 0)
    pi.stop()
'''
