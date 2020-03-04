def make_checksum(buf):
    checksum = 0x00
    for i in range(len(buf)):
        checksum = checksum ^ buf[i]
    return checksum

buf = [0x00, 0x10, 0x11, 0x22, 0x33, 0xAA, 0xBB, 0xCC]
header = [0xA5, 0x5A] # ヘッダ
data_size = [0x80, 0x08]
checksum = make_checksum(data_size+buf)
test = header + data_size + buf + [checksum]

def make_data_size(data_size):
    minus_ = [0x80, 0x00]
    for i in range(2):
        data_size[i] -= minus_[i]
    res = (data_size[0] << 8) + data_size[1]
    return res

def read_binary():
    # ヘッダがくるまで
    buf = test
    if buf[0] != 0xA5:
        return 0
    if buf[1] != 0x5A:
        return 0

    # データ長をだす
    data_size = make_data_size([buf[2], buf[3]])

    print(data_size)
    for i in range(len(buf)):
        print(hex(buf[i]))
    #print(bytes.hex(line))

read_binary()