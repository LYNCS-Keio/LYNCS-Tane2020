import serial
import pigpio

# ser = serial.Serial('/dev/ttyS0', 115200)
pi = pigpio.pi()
h1 = pi.serial_open("/dev/ttyS0", 115200)

def make_data_size(data_size):
    minus_ = [0x80, 0x00]
    for i in range(2):
        data_size[i] -= minus_[i]
    res = (data_size[0] << 8) + data_size[1]
    return res

def read_binary():
    # ヘッダがくるまで
    head = pi.serial_read(h1, 1)
    if head[0] != 0xA5:
        return 0
    head = pi.serial_read(h1, 1)
    if head[1] != 0x5A:
        return 0

    # データ長をだす
    tmp = pi.serial_read(h1, 2)
    data_size = make_data_size(tmp)

    # データ部
    data = pi.serial_read(h1, data_size)
    checksum = pi.serial_read(h1, 1) # チェックサム
    footer = pi.serial_read(h1, 1) # フッタ

    print(hex(data))
    #print(bytes.hex(line))

ser.close()