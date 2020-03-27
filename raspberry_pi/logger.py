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
            self._handler = pigpio.pi()
            self.own_handler = True
        else:
            self._handler = handler
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
                    self.dps = dps310.dps310(self._handler)
                else:
                    self.dps = dps310.dps310(self._handler, dps_addr)
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
                    self.icm = icm20948.icm20948(self._handler)
                else:
                    self.icm = icm20948.icm20948(self._handler, icm_addr)
                Icm20948 = True
            
            elif i == logger_list_t.ICM_MADGWICK and Madgwick == False:
                from package import icm20948
                from package import madgwick_py
                if icm_addr == None:
                    self.icm = icm20948.icm20948(self._handler)
                else:
                    self.icm = icm20948.icm20948(self._handler, icm_addr)
                self.mad = madgwick_py.MadgwickAHRS()
                Icm20948 = True
                Madgwick = True

            elif i == logger_list_t.INA_CUR or i == logger_list_t.INA_VOL and Ina260 == False:
                from package import ina260
                if ina_addr == None:
                    self.ina = ina260.ina260(self._handler)
                else:
                    self.ina = ina260.ina260(self._handler, ina_addr)
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
        results = {}
    
        for i in self.logging_list_:
            if i == logger_list_t.TIMESTAMP:
                results['TIME'] = time.time() 
            elif i == logger_list_t.DPS_PRS:
                results['DPS_PRS'] =self.dps.read_Pressure()
            elif i == logger_list_t.DPS_TMP:
                results['DPS_TMP'] = self.dps.read_Temperature()
            elif i == logger_list_t.DPS_HEIGHT:
                data = self.dps.measure_high()
                results['DPS_HEIGHT'] = data[0]
                results['DPS_TMP'] = data[1]
                results['DPS_PRS'] = data[2]
            elif i == logger_list_t.ICM_GYRO_ACC:
                results['ICM_GYRO_ACC'] = self.icm.read_accelerometer_gyro_data()
            elif i == logger_list_t.ICM_MAG:
                results['ICM_MAG'] = self.icm.read_magnetometer_data()
            elif i == logger_list_t.ICM_MADGWICK:
                ax, ay, az, gx, gy, gz = self.icm.read_accelerometer_gyro_data()
                mx, my, mz = self.icm.read_magnetometer_data()
                gx,gy,gz=gx*pi/180,gy*pi/180,gz*pi/180
                self.mad.update([gx,gy,gz],[ax,ay,az],[mx,-my,-mz])
                x,y,z=self.mad.quaternion.to_euler_angles()
                results['ICM_MADGWICK'] = [x*180/pi,y*180/pi,z*180/pi]
            elif i == logger_list_t.INA_CUR:
                results['INA_CUR'] = self.ina.get_current()
            elif i == logger_list_t.INA_VOL:
                results['INA_VOL'] = self.ina.get_voltage()

        return results


    def csv_logger(self):
        
        self.wri.writerow((self.create_results()).values())

    def printer(self):
        
        print(self.create_results())


if __name__ == "__main__":
    import time
    import pigpio
    import pickle
    from twelite import serial_send
    pi_ = pigpio.pi()
    twe = serial_send.twelite(pi_)
    log_list = [logger_list_t.TIMESTAMP, logger_list_t.ICM_MAG, logger_list_t.INA_VOL, logger_list_t.DPS_HEIGHT]
    logger = logger(log_list)
    
    try:
        while True:
            # buf = pickle.dumps(logger.create_results())
            # twe.send_binary(list(buf))
            # time.sleep(0.01)
            logger.printer()
    finally:
        pi_.stop()
        del logger
