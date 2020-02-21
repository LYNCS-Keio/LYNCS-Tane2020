from package import rover_gps as gps
from package import dps310
from package import icm20948
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



#tv_homing from Noshiro-2019

Aov = 54 # angle of view
height = 240
width = 320
rotation = 0
cam_interval = 1.5
area = 400
lock = threading.Lock()
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
