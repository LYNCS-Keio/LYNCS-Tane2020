import pigpio
import time
import pickle

class twelite():
    def __init__(self, handler):
        self.__handler = handler
        self.__ser = self.__handler.serial_open("/dev/ttyAMA0", 115200)

    def make_checksum(self, buf):
        checksum = 0x00
        for i in range(len(buf)):
            checksum = checksum ^ buf[i]
        return checksum

    def send_binary(self, buf):
        buf = [0x00, 0x01] + buf # 宛先(0x00:親機宛, 0x78:子機宛)
        checksum  = self.make_checksum(buf) # チェックサム
        cmd_size = len(buf)
        data_size = 0x8000 + cmd_size # データ長
        buf = [0xA5, 0x5A] + [data_size >> 8, data_size & 0b11111111] + buf + [checksum]
        self.__handler.serial_write(self.__ser, buf)

    def __del__(self):
        self.__handler.serial_close(self.__ser)


if __name__ == "__main__":
    pi = pigpio.pi()
    buf = 123.4
    buf = pickle.dumps(buf)
    pi.write(18,1)
    twe = twelite(pi)
    
    try:
        while True:
            twe.send_binary(list(buf))
            time.sleep(0.1)
    
    finally:
        pass
