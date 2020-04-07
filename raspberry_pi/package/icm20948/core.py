import sys, pathlib
sys.path.append( str(pathlib.Path(__file__).resolve().parent) + '/../' )
import pigpio
from i2c_bus import *

import time
import struct

class constant():
    CHIP_ID                         = 0xEA
    I2C_ADDR_ALT                    = 0x69
    I2C_ADDR                        = 0x68

class register():
    ICM20948_BANK_SEL               = 0x7f
    # bank 0
    ICM20948_WHO_AM_I               = [0x00, 0]
    ICM20948_USER_CTRL              = [0x03, 0]
    ICM20948_LP_CONFIG              = [0x05, 0]
    ICM20948_PWR_MGMT_1             = [0x06, 0]
    ICM20948_PWR_MGMT_2             = [0x07, 0]
    ICM20948_INT_PIN_CFG            = [0x0F, 0]
    ICM20948_ACCEL_XOUT_H           = [0x2D, 0]
    ICM20948_GYRO_XOUT_H            = [0x33, 0]
    ICM20948_EXT_SLV_SENS_DATA_00   = [0x3B, 0]
    
    # bank 1
    
    # bank 2
    ICM20948_GYRO_SMPLRT_DIV        = [0x00, 2]
    ICM20948_GYRO_CONFIG_1          = [0x01, 2]
    ICM20948_GYRO_CONFIG_2          = [0x02, 2]
    ICM20948_ACCEL_SMPLRT_DIV_1     = [0x10, 2]
    ICM20948_ACCEL_SMPLRT_DIV_2     = [0x11, 2]
    ICM20948_ACCEL_INTEL_CTRL       = [0x12, 2]
    ICM20948_ACCEL_WOM_THR          = [0x13, 2]
    ICM20948_ACCEL_CONFIG           = [0x14, 2]

    # bank 3
    ICM20948_I2C_MST_ODR_CONFIG     = [0x00, 3]
    ICM20948_I2C_MST_CTRL           = [0x01, 3]
    ICM20948_I2C_MST_DELAY_CTRL     = [0x02, 3]
    ICM20948_I2C_SLV0_ADDR          = [0x03, 3]
    ICM20948_I2C_SLV0_REG           = [0x04, 3]
    ICM20948_I2C_SLV0_CTRL          = [0x05, 3]
    ICM20948_I2C_SLV0_DO            = [0x06, 3]

    # AK09916
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
    def write(self, reg, value, no_check=False):
        """
        センサーのレジスタにデータを書き込む。
        Parameters
        -------
        reg : list or int
            書き込むレジスタアドレス, listの場合bank番号を含む
        value : int
            書き込むデータ
        no_check : bool
            Trueの場合書き込み後の確認を行わない。
        """
        if isinstance(reg, int):
            self._bus.writeByte(reg, value, no_check)
        elif isinstance(reg, list):
            self.bank(reg[1])
            self._bus.writeByte(reg[0], value, no_check)
        else:
            raise ICM_FAILED_WRITING
        time.sleep(0.0001)

    def _writeByteBitfield(self, reg, mask, shift, data, no_check=False):
        """
        レジスタの一部だけに書き込む。

        Parameters
        -------
        reg : int
            書き込むレジスタアドレス, listの場合bank番号を含む
        mask : int
            レジスタ内での目的データのマスク。
        shift : int
            マスクしたデータのビットシフト数。
        data : int
            書き込むデータ。
        no_check : bool
            Trueの場合書き込み後の確認を行わない。
        """
        if isinstance(reg, int):
            self._bus.writeByteBitfield(reg, mask, shift, data, no_check)
        elif isinstance(reg, list):
            self.bank(reg[1])
            self._bus.writeByteBitfield(reg[0], mask, shift, data, no_check)
        else:
            raise ICM_FAILED_WRITING
        time.sleep(0.0001)


    def read(self, reg):
        """
        センサーから1バイトデータを取得する。
        Parameters
        -------
        reg : int or list
            読み込むレジスタアドレス, listの場合はbank番号を含む
        """
        if isinstance(reg, int):
            return self._bus.readByte(reg)
        elif isinstance(reg, list):
            self.bank(reg[1])
            return self._bus.readByte(reg[0])
        else:
            raise ICM_FAILED_READING

    def read_bytes(self, reg, length=1):
        """
        センサーから長さを指定してデータを取得する。  
        Parameters
        -------
        reg : int or list
            読み込むレジスタアドレス, listの場合はbank番号を含む
        length : int
            読み込むデータの長さ (bytes)
        """
        if isinstance(reg, int):
            return self._bus.readBytes(reg, length)
        elif isinstance(reg, list):
            self.bank(reg[1])
            return self._bus.readBytes(reg[0], length)

    def bank(self, value):
        """Switch register user bank"""
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

    def read_accelerometer_data(self):
        """
        加速度データの取得

        Returns
        -------
        list of float : 次の順に並んでいる。
        ax, ay, az : 各軸の加速度 
        """
        if self.accelerometer == False:
            return 0, 0, 0
        else:
            data = self.read_bytes(register.ICM20948_ACCEL_XOUT_H, 6)

            ax, ay, az = struct.unpack(">hhh", bytearray(data))

            # Read accelerometer full scale range and
            # use it to compensate the self.reading to gs
            scale = (self.read(register.ICM20948_ACCEL_CONFIG) & 0x06) >> 1

            # scale ranges from section 3.2 of the datasheet
            gs = [16384.0, 8192.0, 4096.0, 2048.0][scale]

            ax /= gs
            ay /= gs
            az /= gs

            return ax, ay, az

    def read_gyro_data(self):
        """
        gyroデータの取得

        Returns
        -------
        list of float : 次の順に並んでいる。
        gx, gy, gz : 各軸の重力加速度
        """
        if self.gyro == False:
            return 0, 0, 0
        else:
            data = self.read_bytes(register.ICM20948_GYRO_XOUT_H, 6)

            gx, gy, gz = struct.unpack(">hhh", bytearray(data))


            # Read back the degrees per second rate and
            # use it to compensate the self.reading to dps
            scale = (self.read(register.ICM20948_GYRO_CONFIG_1) & 0x06) >> 1

            # scale ranges from section 3.1 of the datasheet
            dps = [131, 65.5, 32.8, 16.4][scale]

            gx /= dps
            gy /= dps
            gz /= dps

            return gx, gy, gz

    def set_accelerometer_sample_rate(self, rate=125):
        """
        加速度データのsample rate を指定する。
        Parameters
        -------
        rate : sample rate
               単位はHz
        """
        # 125Hz - 1.125 kHz / (1 + rate)
        rate = int((1125.0 / rate) - 1)
        # TODO maybe use struct to pack and then write_bytes
        self.write(register.ICM20948_ACCEL_SMPLRT_DIV_1, (rate >> 8) & 0xff)
        self.write(register.ICM20948_ACCEL_SMPLRT_DIV_2, rate & 0xff)

    def set_accelerometer_full_scale(self, scale=16):
        """
        加速度の上限を+-指定された値にする。
        set the accelerometer fulls cale range to +- the supplied value.
        Parameters
        -------
        scale : 2, 4, 8, 16 g
                上記以外の値を指定した場合16 gとなる。
        """
        value = self.read(register.ICM20948_ACCEL_CONFIG) & 0b11111001
        dic = {2: 0b00, 4: 0b01, 8: 0b10, 16: 0b11}
        if scale in dic:
            value |= dic[scale] << 1
        else:            
            value |= dic[16] << 1
        self.write(register.ICM20948_ACCEL_CONFIG, value)

    def set_accelerometer_low_pass(self, enabled=True, mode=5):
        """.
        加速度データのlow pass filter の設定をする。
        Parameters
        -------
        enable : low pass filter を使うかどうか。
        mode : モード指定。
               詳しくはデータシートTable 18.を参照。
        """
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
        # 100Hz sample rate - 1.1 kHz / (1 + rate)
        rate = int((1100.0 / rate) - 1)
        self.write(register.ICM20948_GYRO_SMPLRT_DIV, rate)

    def set_gyro_full_scale(self, scale=250):
        """
        gyroの上限を+-指定された値にする。
        Set the gyro full scale range to +- supplied value.
        Parameters
        -------
        scale : 250, 500, 1000, 2000 degree/sec
        """
        value = self.read(register.ICM20948_GYRO_CONFIG_1) & 0b11111001
        dic = {250: 00, 500: 0b01, 1000: 0b10, 2000: 0b11}
        if scale in dic:
            value |= dic[scale] << 1
        else:            
            value |= dic[250] << 1
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
        value = self.read(register.ICM20948_GYRO_CONFIG_1) & 0b10001110
        if enabled:
            value |= 0b1
        value |= (mode & 0x07) << 4
        self.write(register.ICM20948_GYRO_CONFIG_1, value)

    def set_accelerometer_enabled(self, enabled=True, lowpower=False):
        """
        加速度計の有効/無効を切り替える
        Parameters
        -------
        enabled : bool
            有効/無効
        lowpower : bool
            低電力モードの有効/無効
        """
        try:
            if enabled:
                self._writeByteBitfield(register.ICM20948_PWR_MGMT_2, 0b00111000, 3, 0b0)
                self.accelerometer = True
            else:
                self._writeByteBitfield(register.ICM20948_PWR_MGMT_2, 0b00111000, 3, 0b111)
                self.accelerometer = False

            if lowpower:
                self._writeByteBitfield(register.ICM20948_LP_CONFIG, 0b00100000, 5, 0b1)
                self.accelerometer_lowpower = True
            else:
                self._writeByteBitfield(register.ICM20948_LP_CONFIG, 0b00100000, 5, 0b0)
                self.accelerometer_lowpower = False
            self.set_lowpower()
        except:
            raise ICM_FAILED_SETUP


    def set_gyro_enabled(self, enabled=True, lowpower=False):
        """
        ジャイロの有効/無効を切り替える
        Parameters
        -------
        enabled : bool
            有効/無効
        lowpower : bool
            低電力モードの有効/無効
        """
        try:
            if enabled:
                self._writeByteBitfield(register.ICM20948_PWR_MGMT_2, 0b00000111, 0, 0b0)
                self.gyro = True
            else:
                self._writeByteBitfield(register.ICM20948_PWR_MGMT_2, 0b00000111, 0, 0b111)
                self.gyro = False

            if lowpower:
                self._writeByteBitfield(register.ICM20948_LP_CONFIG, 0b00010000, 4, 0b1)
                self.gyro_lowpower = True
            else:
                self._writeByteBitfield(register.ICM20948_LP_CONFIG, 0b00010000, 4, 0b0)
                self.gyro_lowpower = False
            self.set_lowpower()
        except:
            raise ICM_FAILED_SETUP

    def set_device_awake(self, awake=True):
        """
        スリープモードを切り替える。
        Parameters
        -------
        awake : bool
        """
        try:
            if awake:
                self._writeByteBitfield(register.ICM20948_PWR_MGMT_1, 0b01000000, 6, 0b0)
                self.sleep = False
            else:
                self._writeByteBitfield(register.ICM20948_PWR_MGMT_1, 0b01000000, 6, 0b1)
                self.sleep = True
        except:
            raise ICM_FAILED_SETUP

    def set_lowpower(self):
        """
        加速度計、ジャイロ、地磁気のいずれかが低電力モードのとき、回路部を低電力モードにする。
        """
        try:
            if self.accelerometer_lowpower or self.gyro_lowpower:
                if self.circuit_lowpower == False:
                    self._writeByteBitfield(register.ICM20948_PWR_MGMT_1, 0b00100000, 5, 0b1)
                    self.circuit_lowpower = True
            else:
                if self.circuit_lowpower == True:
                    self._writeByteBitfield(register.ICM20948_PWR_MGMT_1, 0b00100000, 5, 0b0)
                    self.circuit_lowpower = False
        except:
            raise ICM_FAILED_SETUP

    def reset_device(self):
        try:
            self.write(register.ICM20948_PWR_MGMT_1, 0x80, no_check=True)
        except:
            raise ICM_FAILED_SETUP

    def __init__(self, handler, i2c_addr=constant.I2C_ADDR):
        self._bank = -1
        self._addr = i2c_addr

        self.sleep = False
        self.accelerometer = True
        self.gyro = True 
        self.accelerometer_lowpower = False
        self.gyro_lowpower = False
        self.circuit_lowpower = False

        try:
            self._bus = i2c_bus(handler, self._addr)
        except:
            raise ICM_FAILED_INIT

        if not self.read(register.ICM20948_WHO_AM_I) == constant.CHIP_ID:
            raise ICM_FAILED_SETUP

        try:
            self.reset_device()
            time.sleep(0.05)
            self.write(register.ICM20948_PWR_MGMT_1, 0x01) # clock select

            self.set_device_awake()
            self.set_accelerometer_enabled()
            self.set_gyro_enabled()

            self.set_gyro_sample_rate(100)
            self.set_gyro_low_pass(enabled=True, mode=5)
            self.set_gyro_full_scale(250)

            self.set_accelerometer_sample_rate(125)
            self.set_accelerometer_low_pass(enabled=True, mode=5)
            self.set_accelerometer_full_scale(8)

            self.write(register.ICM20948_INT_PIN_CFG, 0x30)
            self.write(register.ICM20948_USER_CTRL, 0x20)

            self.write(register.ICM20948_I2C_MST_CTRL, 0x4D)
            self.write(register.ICM20948_I2C_MST_DELAY_CTRL, 0x01)
        except:
            raise ICM_FAILED_SETUP    

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
        ax, ay, az = imu.read_accelerometer_data()
        gx, gy, gz = imu.read_gyro_data() 

        print("""
Accel: {:05.2f} {:05.2f} {:05.2f}
Gyro:  {:05.2f} {:05.2f} {:05.2f}
Mag:   {:05.2f} {:05.2f} {:05.2f}""".format(
            ax, ay, az, gx, gy, gz, x, y, z
        ))

        time.sleep(0.25)
