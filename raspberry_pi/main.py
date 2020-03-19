from package import rover_gps as gps
from package import dps310
from package import icm20948
from package import ina260
from package import pid_controll
from package import twelite
from package import camera
from package import capture

import time
import pigpio
import math
import threading
import toml
import run

pi = pigpio.pi()
icm = icm20948.icm20948(pi)
dps = dps310.dps310(pi)
toml_dic = toml.load(open('config.toml'))
p = pid_controll.pid(toml_dic['PID']['P'], toml_dic['PID']['I'], toml_dic['PID']['D'])
rotation_lock = threading.Lock()

dps.set_OpMode(dps310.opMode.IDLE)
dps.get_coeffs()
dps.config_Pressure(dps310.mesurement_conf.MEAS_RATE_16, dps310.measurement_conf.MEAS_RATE_16)
dps.config_Temperature(dps310.mesurement_conf.MEAS_RATE_32, dps310.measurement_conf.MEAS_RATE_32)
dps.set_OpMode(dps310.opMode.CONT_BOTH)

THRESHOLD_HIGH = toml_dic['height']['high']
THRESHOLD_LOW = toml_dic['height']['low']
CONTINUOUS_NUM = toml_dic['height']['continue_number']

LIMIT_DISTANCE = toml_dic['camera']['start_distance']
AoV = toml_dic['camera']['Angle_of_View']
pinL = toml_dic['pin']['Rmotor']
pinR = toml_dic['pin']['Lmotor']
goal = [toml_dic['gps']['goal_lat'], toml_dic['gps']['goal_long']]

lr = toml_dic['icm_calib']['learning_rate']
b = [30.0, 0.0, 15.0, 20]
drift = [0,0,0]
azimuth = 0
to_goal = [None, None]


def pressure_while(height_threshold, continuous_num, timeout, mode):
    n = 0
    pt = time.time()
    while n < continuous_num:
        height = dps.measurement_high()
        if (mode)*height >= (mode)*height_threshold:
            n += 1
        else:
            n = 0
        time.sleep(0.01)
        if (time.time() - pt) > timeout:
            break


def update_target_gps():
    global to_goal
    while UPDATE_GPS:
        now = gps.lat_long_measurement()
        if now != [None, None]:
            to_goal = gps.convert_lat_long_to_r_theta(*now, *goal)


def update_rotation_with_cam():
    global rotation
    cap = capture.capture()
    cam = camera.CamAnalysis()
    while UPDATE_CAMERA == True:
        stream = cap.cap()
        cam.morphology_extract(stream)
        cam.save_all_outputs()
        coord = cam.contour_find()

        conX = ((coord[0] - width / 2) / (width / 2)) / math.sqrt(3)
        rotation_lock.acquire()
        rotation = math.degrees(math.atan(-conX))
        rotation_lock.release()


try:
    pi.set_mode(pinL, pigpio.OUTPUT)
    pi.set_mode(pinR, pigpio.OUTPUT)
    pi.hardware_PWM(pinL, 50, 75000)
    pi.hardware_PWM(pinR, 50, 75000)

    run.calibrate_mag(pi, icm, 30, b, lr)
    azimuth = run.update_azimuth(icm, b)
    run.calc_drift(pi, icm, 30, drift)

    UPDATE_GPS = True
    update_target_gps()
    target_azimuth = to_goal[1]
    GPS_THREAD = threading.Thread(target=update_target_gps)
    GPS_THREAD.start()
    

    if STATE == 0:
        """ 気圧センサーによる頂点、落下判定 """        
        pressure_while(THRESHOLD_HIGH, CONTINUOUS_NUM, 300, 1)
        pressure_while(THRESHOLD_LOW, CONTINUOUS_NUM, 300, -1)
        # pi.write(26)
    

    elif STATE == 1:
        """ GPS誘導による走行コード """
        speed = 1
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
            m = p.update_pid(target_azimuth, azimuth, dt)

            m1 = min([max([m, -1]), 1])

            dL, dR = 75000 + 12500 * (speed - m1), 75000 - 12500 * (speed + m1)
            pi.hardware_PWM(13, 50, int(dL))
            pi.hardware_PWM(12, 50, int(dR))

            if to_goal[0] <= LIMIT_DISTANCE:
                break


    elif STATE == 2:
        """ 画像誘導による走行 """
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
            rotation += gz*dt
            m = p.update_pid(0, rotation, dt)

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
