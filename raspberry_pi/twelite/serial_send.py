import serial
import pigpio
import time

# buf = [0x00, 0x10, 0x11, 0x22, 0x33, 0xAA, 0xBB, 0xCC]
header = [0xA5, 0x5A] # ヘッダ

def make_checksum(buf):
    checksum = 0x00
    for i in range(len(buf)):
        checksum = checksum ^ buf[i]
    return checksum

def send_binary(buf):
    cmd_size = len(buf)
    data_size = 0x8000 + cmd_size # データ長
    buf = [0x00] + buf # 宛先(0x00:親機宛, 0x78:子機宛)
    buf = [0x01] + buf # コマンド種別(0x80未満で任意)
    checksum  = make_checksum(buf) # チェックサム
    pi.serial_write(h1, header + [data_size >> 8, data_size & 0b11111111] + buf + [checksum])
    # print(header + [0x80, 0x08] + buf + [checksum])


if __name__ == "__main__":
    pi = pigpio.pi()
    h1 = pi.serial_open("/dev/ttyS0", 115200)
    
    try:
        while True:
            buf = input()
            send_binary(buf)
            time.sleep(0.1)
    
    finally: