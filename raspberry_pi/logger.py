from enum import Enum
import csv
import time
from math import pi

class logger_list_t(Enum):
    TIMESTAMP       = 0
    DPS_PRS         = 1
    DPS_HEIGHT      = 2
    DPS_TMP         = 3
    ICM_MAG         = 4
    ICM_GYRO_ACC    = 5
    ICM_MADGWICK    = 6
    INA_VOL         = 7
    INA_CUR         = 8

class logger():
    def __init__(self, logging_list, log_dir=None, handler=None, dps_addr=None, icm_addr=None, ina_addr=None):
        if handler == None:
            import pigpio
            self.handler_ = pigpio.pi()
            self.own_handler = True
        else:
            self.handler_ = handler
            self.own_handler = False


        Time = False
        Dps310 = False
        Icm20948 = False
        Madgwick = False
        Ina260 = False


        self.logging_list_ = logging_list
        for i in self.logging_list_:
            if i == logger_list_t.DPS_PRS or i == logger_list_t.DPS_TMP or i == logger_list_t.DPS_HEIGHT and Dps310 == False:
                from package import dps310
                if dps_addr == None:
                    self.dps = dps310.dps310(self.handler_)
                else:
                    self.dps = dps310.dps310(self.handler_, dps_addr)
                self.dps.set_OpMode(dps310.opMode.IDLE)

                time.sleep(0.01)
                self.dps.get_coeffs()
                self.dps.config_Pressure(dps310.measurement_conf.MEAS_RATE_16, dps310.measurement_conf.MEAS_RATE_16)
                self.dps.config_Temperature(dps310.measurement_conf.MEAS_RATE_32, dps310.measurement_conf.MEAS_RATE_32)
                self.dps.set_OpMode(dps310.opMode.CONT_BOTH)
                self.dps.read_Temperature()
                Dps310 = True

            elif i == logger_list_t.ICM_MAG or i == logger_list_t.ICM_GYRO_ACC and Icm20948 == False and Madgwick == False:
                from package import icm20948
                if icm_addr == None:
                    self.icm = icm20948.icm20948(self.handler_)
                else:
                    self.icm = icm20948.icm20948(self.handler_, icm_addr)
                Icm20948 = True
            
            elif i == logger_list_t.ICM_MADGWICK and Madgwick == False:
                from package import icm20948
                from package import madgwick_py
                if icm_addr == None:
                    self.icm = icm20948.icm20948(self.handler_)
                else:
                    self.icm = icm20948.icm20948(self.handler_, icm_addr)
                self.mad = madgwick_py.MadgwickAHRS()
                Icm20948 = True
                Madgwick = True

            elif i == logger_list_t.INA_CUR or i == logger_list_t.INA_VOL and Ina260 == False:
                # import ina260
                Ina260 = True

        if log_dir != None:
            self.fd = open(log_dir, mode='w')
            self.wri = csv.writer(self.fd, lineterminator='\n')
        else:
            self.fd = None


    def __del__(self):
        if self.fd != None:
            self.fd.close()

    def create_results(self):
        results = []
        for i in self.logging_list_:
            if i == logger_list_t.TIMESTAMP:
                results.append(time.time())
            elif i == logger_list_t.DPS_PRS:
                results.append(self.dps.read_Pressure())
            elif i == logger_list_t.DPS_TMP:
                results.append(self.dps.read_Temperature())
            elif i == logger_list_t.DPS_HEIGHT:
                results.extend(self.dps.measure_high())
            elif i == logger_list_t.ICM_GYRO_ACC:
                results.extend(self.icm.read_accelerometer_gyro_data())
            elif i == logger_list_t.ICM_MAG:
                results.extend(self.icm.read_magnetometer_data())
            elif i == logger_list_t.ICM_MADGWICK:
                ax, ay, az, gx, gy, gz = self.icm.read_accelerometer_gyro_data()
                mx, my, mz = self.icm.read_magnetometer_data()
                gx,gy,gz=gx*pi/180,gy*pi/180,gz*pi/180

                self.mad.update([gx,gy,gz],[ax,ay,az],[mx,-my,-mz])
                x,y,z=self.mad.quaternion.to_euler_angles()
                
                results.extend([x*180/pi,y*180/pi,z*180/pi])
            elif i == logger_list_t.INA_CUR:
                pass
            elif i == logger_list_t.INA_VOL:
                pass

        return results


    def csv_logger(self):
        
        self.wri.writerow(self.create_results())

    def printer(self):
        
        print(self.create_results())


if __name__ == "__main__":
    import time
    import pigpio
    pi = pigpio.pi()
    log_list = [logger_list_t.ICM_MAG]
    logger = logger(log_list, '/home/pi/LYNCS-Tane2020/raspberry_pi/'+ 'log_0' +'.csv')
    pi.set_mode(13, pigpio.OUTPUT)
    pi.set_mode(12, pigpio.OUTPUT)
    pi.hardware_PWM(13, 50, 90000)
    pi.hardware_PWM(12, 50, 90000)
    
    try:
        while True:
            logger.csv_logger()
            time.sleep(0.01)
    finally:
        pi.hardware_PWM(12, 0, 0)
        pi.hardware_PWM(13, 0, 0)
        pi.stop()
        del logger
