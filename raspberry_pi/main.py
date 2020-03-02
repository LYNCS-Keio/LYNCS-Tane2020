from package import rover_gps as GPS
from package import dps310
from package import icm20948 as icm
from package import ina260
from package import twelite
from package import pid_controll
from package import camera
from package import capture

import time
import pigpio
import math
import threading
import toml

pi = pigpio.pi()

def pressure_while(height_threshold, continuous_number, mode): #mode　1：data >= threshold   -1:data <= threshold
    dps = dps310(pi, 0x77)
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
         

pi = pigpio.pi()
toml_dic = toml.load(open('config.toml'))

pressure_while(toml_dic['height']['high'], toml_dic['height']['continue_number'], 1)
pressure_while(toml_dic['height']['low'], toml_dic['height']['continue_number'], -1)


#gps_homing
cam_dis = 0.003 # ????????????(km)
forward_dis = 0.01 # ???????(km)

pinL = 13
pinR = 12

goal_lat, goal_long = 0, 0 #?????

lock = threading.Lock()

calib = [0.0, 0.0, 0.0, 1.0] #[x, y, z, r]
lr = 0.0001

def update_magnetometer_data(x, y, z):
    dx = x - b[0]
    dy = y - b[1]
    dz = z - b[2]
    f = dx*dx + dy*dy + dz*dz - b[3]*b[3]
    
    b[0] = b[0] + 4 * lr * f * dx
    b[1] = b[1] + 4 * lr * f * dy
    b[2] = b[2] + 4 * lr * f * dz
    b[3] = b[3] + 4 * lr * f * b[3]

def magnetometer_get():
    global rotation
    mag_x, mag_y, mag_z = imu.read_magnetometer_data()
    update_magnetometer_data(mag_x, mag_y, mag_z)
    mag_x -= calib[0]
    mag_y -= calib[1]
    mag_z -= calib[2]
    lock.acquire()
    rotation = math.atan2(mag_y, mag_x)
    lock.release()

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

def gyro_get():
    global to_goal, rotation, dL, dR, m
    pt = time.time()
    while 1:
        #dutyL????
        gyro = mpu.get_gyro_data_lsb()[2] + drift
        nt = time.time()
        dt = nt - pt
        pt = nt
        lock.acquire()
        rotation += gyro * dt
        lock.release()
        m = p.update_pid(to_goal[1] , rotation, dt)
        m1 = min([max([m, -1]), 1])
        dL, dR = 75000 + 12500 * (1 - m1), 75000 - 12500 * (1 + m1)
        print([m, rotation, to_goal[1] - rotation])
        time.sleep(0.01)

        if to_goal[0] < cam_dis:
            break


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

#gps_homing
try:
    pi.set_mode(pinL, pigpio.OUTPUT)
    pi.set_mode(pinR, pigpio.OUTPUT)
    imu = icm20948.icm20948(pi)
    to_goal, rotation = [1, 0], 0
    t1 = threading.Thread(target=gps_get)
    t2 = threading.Thread(target=gyro_get)
    t3 = threading.Thread(target=magnetometer_get)
    t1.start()
    t2.start()
    t3.start()
    
    while True:
        pi.hardware_PWM(pinL, 50, int(dL))
        pi.hardware_PWM(pinR, 50, int(dR))
        if to_goal[0] < cam_dis:
            pi.hardware_PWM(pinL, 50, 75000)
            pi.hardware_PWM(pinR, 50, 75000)
            break
finally:
    pi.hardware_PWM(pinL, 0, 0)
    pi.hardware_PWM(pinR, 0, 0)

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
