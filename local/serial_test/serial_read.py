import io
import serial
import pickle
ser = serial.Serial('/dev/ttyUSB0',115200)
eol = bytearray([4])

try:
    err = 0
    suc = 0
    while True:
        line = []
        while True:
            c = ser.read()
            if c == eol:
                break
            else:
                line += c
        try:
            length = line[3]
            b = bytearray(line[6:6+length-1])
            data = pickle.loads(b)
            # l_n_hex = [hex(n) for n in line]
            # print(l_n_hex)
        except KeyboardInterrupt:
            break
        except:
            err += 1
        else:
            print(data)
            suc += 1

finally:
    ser.close()
    print(suc, err)
