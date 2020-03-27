import sys, pathlib
sys.path.append( str(pathlib.Path(__file__).resolve().parent) + '/../' )
import pigpio
from i2c_bus import *

import time
import struct

class register():
    CHIP_ID                         = 0xEA
    I2C_ADDR                        = 0x68
    I2C_ADDR_ALT                    = 0x69
    ICM20948_BANK_SEL               = 0x7f

    ICM20948_I2C_MST_ODR_CONFIG     = 0x00
    ICM20948_I2C_MST_CTRL           = 0x01
    ICM20948_I2C_MST_DELAY_CTRL     = 0x02
    ICM20948_I2C_SLV0_ADDR          = 0x03
    ICM20948_I2C_SLV0_REG           = 0x04
    ICM20948_I2C_SLV0_CTRL          = 0x05
    ICM20948_I2C_SLV0_DO            = 0x06
    ICM20948_EXT_SLV_SENS_DATA_00   = 0x3B

    ICM20948_GYRO_SMPLRT_DIV        = 0x00
    ICM20948_GYRO_CONFIG_1          = 0x01
    ICM20948_GYRO_CONFIG_2          = 0x02

    # Bank 0
    ICM20948_WHO_AM_I               = 0x00
    ICM20948_USER_CTRL              = 0x03
    ICM20948_PWR_MGMT_1             = 0x06
    ICM20948_PWR_MGMT_2             = 0x07
    ICM20948_INT_PIN_CFG            = 0x0F

    ICM20948_ACCEL_SMPLRT_DIV_1     = 0x10
    ICM20948_ACCEL_SMPLRT_DIV_2     = 0x11
    ICM20948_ACCEL_INTEL_CTRL       = 0x12
    ICM20948_ACCEL_WOM_THR          = 0x13
    ICM20948_ACCEL_CONFIG           = 0x14
    ICM20948_ACCEL_XOUT_H           = 0x2D
    ICM20948_GRYO_XOUT_H            = 0x33

    AK09916_I2C_ADDR                = 0x0c
    AK09916_CHIP_ID                 = 0x09
    AK09916_WIA                     = 0x01
    AK09916_ST1                     = 0x10
    AK09916_ST1_DOR                 = 0b00000010   # Data overflow bit
    AK09916_ST1_DRDY                = 0b00000001  # Data self.ready bit
    AK09916_HXL                     = 0x11
    AK09916_ST2                     = 0x18
    AK09916_ST2_HOFL                = 0b00001000  # Magnetic sensor overflow bit
    AK09916_CNTL2                   = 0x31
    AK09916_CNTL2_MODE              = 0b00001111
    AK09916_CNTL2_MODE_OFF          = 0
    AK09916_CNTL2_MODE_SINGLE       = 1
    AK09916_CNTL2_MODE_CONT1        = 2
    AK09916_CNTL2_MODE_CONT2        = 4
    AK09916_CNTL2_MODE_CONT3        = 6
    AK09916_CNTL2_MODE_CONT4        = 8
    AK09916_CNTL2_MODE_TEST         = 16
    AK09916_CNTL3                   = 0x32

class _ICM_ERROR(Exception):
    "icm20948 base error"

class ICM_FAILED(_ICM_ERROR):
    "Something went wrong on icm20948"

class ICM_FAILED_INIT(_ICM_ERROR):
    "Failed initializing  icm20948"

class ICM_FAILED_SETUP(_ICM_ERROR):
    "Failed setting up icm20948"

class ICM_FAILED_READING(_ICM_ERROR):
    "Failed reading data from the icm20948"

class ICM_FAILED_WRITING(_ICM_ERROR):
    "Failed writing data on the icm20948"

class icm20948():
    def write(self, reg, value):
        """
        センサーのレジスタにデータを書き込む。
        Parameters
        -------
        reg : 書き込むレジスタアドレス
        value : 書き込むデータ
        """
        self._bus.writeByte(reg, value)
        time.sleep(0.0001)

    def read(self, reg):
        """
        センサーから1バイトデータを取得する。
        Parameters
        -------
        reg : 読み込むレジスタアドレス
        """
        return self._bus.readByte(reg)

    def read_bytes(self, reg, length=1):
        """
        センサーから長さを指定してデータを取得する。  
        Parameters
        -------
        reg : 読み込むレジスタアドレス
        length : 読み込むデータの長さ
                 単位はバイト
        """
        return self._bus.readBytes(reg, length)

    def bank(self, value):
        """Switch register self.bank."""
        if not self._bank == value:
            self.write(register.ICM20948_BANK_SEL, value << 4)
            self._bank = value

    def mag_write(self, reg, value):
        """
        地磁気のスレーブにデータを書き込む
        Parameters
        -------
        reg : 書き込むレジスタのアドレス
        value : 書き込むデータ
        """
        self.bank(3)
        self.write(register.ICM20948_I2C_SLV0_ADDR, register.AK09916_I2C_ADDR)  # Write one byte
        self.write(register.ICM20948_I2C_SLV0_REG, reg)
        self.write(register.ICM20948_I2C_SLV0_DO, value)
        self.bank(0)

    def mag_read(self, reg):
        """
        地磁気のスレーブから1バイトデータを取得する。
        Parameters
        -------
        reg : 読み込むレジスタのアドレス

        Returns
        -------
        bytes : 読み込んだデータ
        """
        self.bank(3)
        self.write(register.ICM20948_I2C_SLV0_CTRL, 0x80 | 1)  # Read 1 byte
        self.write(register.ICM20948_I2C_SLV0_ADDR, register.AK09916_I2C_ADDR | 0x80)
        self.write(register.ICM20948_I2C_SLV0_REG, reg)
        self.write(register.ICM20948_I2C_SLV0_DO, 0xff)
        self.bank(0)
        return self.read(register.ICM20948_EXT_SLV_SENS_DATA_00)

    def mag_read_bytes(self, reg, length=1):
        """
        地磁気のスレーブから指定した長さのデータを取得する。
        Parameters
        -------
        reg : 読み込むレジスタのアドレス
        length : 読み込むデータの長さ
            　   単位はバイト

        Returns
        -------
        bytes : 読み込んだデータ
        """
        self.bank(3)
        self.write(register.ICM20948_I2C_SLV0_CTRL, 0x80 | 0x08 | length)
        self.write(register.ICM20948_I2C_SLV0_ADDR, register.AK09916_I2C_ADDR | 0x80)
        self.write(register.ICM20948_I2C_SLV0_REG, reg)
        self.write(register.ICM20948_I2C_SLV0_DO, 0xff)
        self.bank(0)
        return self.read_bytes(register.ICM20948_EXT_SLV_SENS_DATA_00, length)

    def magnetometer_ready(self):
        """
        Check the magnetometer status self.ready bit.

        Returns
        -------
        bool : 正常な状態であれば0を返す。
        """
        return self.mag_read(register.AK09916_ST1) & 0x01 > 0

    def read_magnetometer_data(self):
        """
        地磁気のデータを取得する。

        Returns
        -------
        x, y, z, : list of float
        x : x軸の地磁気
        y : y軸の地磁気
        z : z軸の地磁気
            単位はμﾃｽﾗ
        """
        self.mag_write(register.AK09916_CNTL2, 0x01)  # Trigger single measurement
        while not self.magnetometer_ready():
            time.sleep(0.00001)

        data = self.mag_read_bytes(register.AK09916_HXL, 6)

        # Read ST2 to confirm self.read finished,
        # needed for continuous modes
        # self.mag_read(AK09916_ST2)

        x, y, z = struct.unpack("<hhh", bytearray(data))

        # Scale for magnetic flux density "uT"
        # from section 3.3 of the datasheet
        # This value is constant
        x *= 0.15
        y *= 0.15
        z *= 0.15

        return x, y, z

    def read_accelerometer_gyro_data(self):
        """
        gyroデータの取得

        Returns
        -------
        list of float : 次の順に並んでいる。
        ax, ay, az : 各軸の加速度 
        xg, gy, gz : 各軸の重力加速度
        """
        self.bank(0)
        data = self.read_bytes(register.ICM20948_ACCEL_XOUT_H, 12)

        ax, ay, az, gx, gy, gz = struct.unpack(">hhhhhh", bytearray(data))

        self.bank(2)

        # Read accelerometer full scale range and
        # use it to compensate the self.reading to gs
        scale = (self.read(register.ICM20948_ACCEL_CONFIG) & 0x06) >> 1

        # scale ranges from section 3.2 of the datasheet
        gs = [16384.0, 8192.0, 4096.0, 2048.0][scale]

        ax /= gs
        ay /= gs
        az /= gs

        # Read back the degrees per second rate and
        # use it to compensate the self.reading to dps
        scale = (self.read(register.ICM20948_GYRO_CONFIG_1) & 0x06) >> 1

        # scale ranges from section 3.1 of the datasheet
        dps = [131, 65.5, 32.8, 16.4][scale]

        gx /= dps
        gy /= dps
        gz /= dps

        return ax, ay, az, gx, gy, gz

    def set_accelerometer_sample_rate(self, rate=125):
        """
        加速度データのsample rate を指定する。
        Parameters
        -------
        rate : sample rate
               単位はHz
        """
        self.bank(2)
        # 125Hz - 1.125 kHz / (1 + rate)
        rate = int((1125.0 / rate) - 1)
        # TODO maybe use struct to pack and then write_bytes
        self.write(register.ICM20948_ACCEL_SMPLRT_DIV_1, (rate >> 8) & 0xff)
        self.write(register.ICM20948_ACCEL_SMPLRT_DIV_2, rate & 0xff)

    def set_accelerometer_full_scale(self, scale=16):
        """
        加速度の上限を+-指定された値にする。
        set the accelerometer fulls cale range to +- the supplied value.
        """
        self.bank(2)
        value = self.read(register.ICM20948_ACCEL_CONFIG) & 0b11111001
        value |= {2: 0b00, 4: 0b01, 8: 0b10, 16: 0b11}[scale] << 1
        self.write(register.ICM20948_ACCEL_CONFIG, value)

    def set_accelerometer_low_pass(self, enabled=True, mode=5):
        """.
        加速度データのlow pass filter の設定をする。
        Parameters
        -------
        enable : low pass filter を使うかどうか。
        mode : モード指定。
               詳しくはデータシートを参照。
        """
        self.bank(2)
        value = self.read(register.ICM20948_ACCEL_CONFIG) & 0b10001110
        if enabled:
            value |= 0b1
        value |= (mode & 0x07) << 4
        self.write(register.ICM20948_ACCEL_CONFIG, value)

    def set_gyro_sample_rate(self, rate=100):
        """
        gyroデータのsample rate の指定。
        Parameters
        -------
        rate : sample rate
               
        """
        self.bank(2)
        # 100Hz sample rate - 1.1 kHz / (1 + rate)
        rate = int((1100.0 / rate) - 1)
        self.write(register.ICM20948_GYRO_SMPLRT_DIV, rate)

    def set_gyro_full_scale(self, scale=250):
        """
        gyroの上限を+-指定された値にする。
        Set the gyro full scale range to +- supplied value.
        """
        self.bank(2)
        value = self.read(register.ICM20948_GYRO_CONFIG_1) & 0b11111001
        value |= {250: 0b00, 500: 0b01, 1000: 0b10, 2000: 0b11}[scale] << 1
        self.write(register.ICM20948_GYRO_CONFIG_1, value)

    def set_gyro_low_pass(self, enabled=True, mode=5):
        """.
        gyroデータのlow pass filter の設定をする。
        Parameters
        -------
        enable : low pass filter を使うかどうか。
        mode : モード指定。
               詳しくはデータシートを参照。
        """
        self.bank(2)
        value = self.read(register.ICM20948_GYRO_CONFIG_1) & 0b10001110
        if enabled:
            value |= 0b1
        value |= (mode & 0x07) << 4
        self.write(register.ICM20948_GYRO_CONFIG_1, value)

    def __init__(self, handler, i2c_addr=register.I2C_ADDR):
        self._bank = -1
        self._addr = i2c_addr

        try:
            self._bus = i2c_bus(handler, self._addr)
        except:
            raise ICM_FAILED_INIT
        else:
            pass

        self.bank(0)
        if not self.read(register.ICM20948_WHO_AM_I) == register.CHIP_ID:
            raise ICM_FAILED_SETUP

        self.write(register.ICM20948_PWR_MGMT_1, 0x01)
        self.write(register.ICM20948_PWR_MGMT_2, 0x00)

        self.bank(2)

        self.set_gyro_sample_rate(100)
        self.set_gyro_low_pass(enabled=True, mode=5)
        self.set_gyro_full_scale(250)

        self.set_accelerometer_sample_rate(125)
        self.set_accelerometer_low_pass(enabled=True, mode=5)
        self.set_accelerometer_full_scale(16)

        self.bank(0)
        self.write(register.ICM20948_INT_PIN_CFG, 0x30)
        self.write(register.ICM20948_USER_CTRL, 0x20)

        self.bank(3)
        self.write(register.ICM20948_I2C_MST_CTRL, 0x4D)
        self.write(register.ICM20948_I2C_MST_DELAY_CTRL, 0x01)

        if not self.mag_read(register.AK09916_WIA) == register.AK09916_CHIP_ID:
            raise ICM_FAILED_SETUP

        # Reset the magnetometer
        self.mag_write(register.AK09916_CNTL3, 0x01)
        while self.mag_read(register.AK09916_CNTL3) == 0x01:
            time.sleep(0.0001)


if __name__ == "__main__":
    pi = pigpio.pi()
    imu = icm20948(pi)

    while True:
        x, y, z = imu.read_magnetometer_data()
        ax, ay, az, gx, gy, gz = imu.read_accelerometer_gyro_data()

        print("""
Accel: {:05.2f} {:05.2f} {:05.2f}
Gyro:  {:05.2f} {:05.2f} {:05.2f}
Mag:   {:05.2f} {:05.2f} {:05.2f}""".format(
            ax, ay, az, gx, gy, gz, x, y, z
        ))

        time.sleep(0.25)
