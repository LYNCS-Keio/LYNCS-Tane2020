from enum import Enum
import csv
import time

class logger_list_t(Enum):
    TIMESTAMP       = 0
    DPS_PRS         = 1
    DPS_HEIGHT      = 2
    DPS_TMP         = 3
    ICM_MAG         = 4
    ICM_GYRO_ACC    = 5
    INA_VOL         = 6
    INA_CUR         = 7

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

            elif i == logger_list_t.ICM_MAG or i == logger_list_t.ICM_GYRO_ACC and Icm20948 == False:
                import icm20948
                if icm_addr == None:
                    self.icm = icm20948.icm20948(self.handler_)
                else:
                    self.icm = icm20948.icm20948(self.handler_, icm_addr)
                Icm20948 = True

            elif i == logger_list_t.INA_CUR or i == logger_list_t.INA_VOL and Ina260 == False:
                # import ina260
                Ina260 = True

        if log_dir != None:
            self.fd = open(log_dir, mode='w')
            self.wri = csv.writer(fd, lineterminator='\n')


    def __del__(self):
        self.fd.close()

    def csv_logger(self):
        results = []
        for i in self.logging_list_:
            if i == logger_list_t.TIMESTAMP:
                results.append(time.time())
            elif i == logger_list_t.DPS_PRS:
                results.append(self.dps.read_Pressure())
            elif i == logger_list_t.DPS_TMP:
                results.append(self.dps.read_Temperature())
            elif i == logger_list_t.DPS_HEIGHT:
                pass
            elif i == logger_list_t.ICM_GYRO_ACC:
                results.append(self.icm.read_accelerometer_gyro_data())
            elif i == logger_list_t.ICM_MAG:
                results.append(self.icm.read_magnetometer_data())
            elif i == logger_list_t.INA_CUR:
                pass
            elif i == logger_list_t.INA_VOL:
                pass

        wri.writerow(results)

    def printer(self):
        results = []
        for i in self.logging_list_:
            if i == logger_list_t.TIMESTAMP:
                results.append(time.time())
            elif i == logger_list_t.DPS_PRS:
                results.append(self.dps.read_Pressure())
            elif i == logger_list_t.DPS_TMP:
                results.append(self.dps.read_Temperature())
            elif i == logger_list_t.DPS_HEIGHT:
                pass
            elif i == logger_list_t.ICM_GYRO_ACC:
                results.extend(self.icm.read_accelerometer_gyro_data())
            elif i == logger_list_t.ICM_MAG:
                results.extend(self.icm.read_magnetometer_data())
            elif i == logger_list_t.INA_CUR:
                pass
            elif i == logger_list_t.INA_VOL:
                pass

        print(results)


if __name__ == "__main__":
    import time
    log_list = [logger_list_t.TIMESTAMP, logger_list_t.DPS_PRS, logger_list_t.ICM_GYRO_ACC]
    logger = logger(log_list)
    
    try:
        while True:
            logger.printer()
            time.sleep(0.1)
    finally:
        del logger