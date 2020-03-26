import pigpio
import time

buf = [0xAB, 0xCD, 0xEF, 0x12, 0x34, 0x56, 0x78, 0x90]
header = [0xA5, 0x5A] # ヘッダ

def make_checksum(buf):
    checksum = 0x00
    for i in range(len(buf)):
        checksum = checksum ^ buf[i]
    return checksum

def send_binary(buf):
    buf = [0x00, 0x01] + buf # 宛先(0x00:親機宛, 0x78:子機宛)
    checksum  = make_checksum(buf) # チェックサム
    cmd_size = len(buf)
    data_size = 0x8000 + cmd_size # データ長
    buf = header + [data_size >> 8, data_size & 0b11111111] + buf + [checksum]
    pi.serial_write(h1,buf)
    buf_hex=[hex(i) for i in buf]
    print(buf_hex)


if __name__ == "__main__":
    pi = pigpio.pi()
    h1 = pi.serial_open("/dev/ttyAMA0", 115200)
    pi.write(18,1)
    
    try:
        while True:
            send_binary(buf)
            time.sleep(0.1)
    
    finally:
        pi.serial_close(h1)
