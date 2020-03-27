from math import ceil
from struct import pack, unpack

""" 
serial_writeはbytes listを引数とする、byte listを用いるならpackのちlist
serial_readのreturnはbyte arrayであり、適切にペイロードを抽出したのちunpackする
i = pack('>d', 1.119)
print(hex(unpack('>Q', i)[0]))
b = bytearray(i)
print(unpack('>d', b)[0]) 

一応関数化したけどあまり使いやすくはないため直書きしても良い気がする
"""

def to_buf(data, form=None):
    """ 
    input:
        data: int, float, str, bool, other list
        form: format character
    return: byte list

    https://docs.python.org/ja/3/library/struct.html
    """
    if form is None:
        if isinstance(data, int):
            return list(data.to_bytes(ceil((data.bit_length()+1)/8), 'big', signed=True))
        elif isinstance(data, float):
            return list(pack('>d', data))
        elif isinstance(data, str):
            return list(data.encode('utf-8'))
        elif isinstance(data, bool):
            return list(pack('>?', data))
        else:
            raise TypeError
    elif isinstance(data, list):
        return list(pack(form, *data))
    else:
        return list(pack(form, data))

def from_buf(buf, form):
    """ 
    input:
        data: bytearray, byte
        form: format character or 'str' or 'int'

    return: int, float, str, bool, other list
    """
    if form == 'str':
        return buf.decode('utf-8')
    elif form == 'int':
        return int.from_bytes(buf, 'big', signed=True)
    else:
        return unpack(form, buf)



if __name__ == '__main__':
    int_data = 1023             #0x3ff
    float_data = 41.115         #0x40448eb851eb851f
    str_data = "HELLO"          #72 69 76 76 79
    bool_data = True
    list_data = [1.23, 4.56, 7.89]
    
    print(to_buf(int_data))         #[3, 255]
    print(to_buf(float_data))       #[64, 68, 142, 184, 81, 235, 133, 31]
    print(to_buf(str_data))         #[72, 69, 76, 76, 79]
    print(to_buf(bool_data))
    print(to_buf(list_data, '>ddd'))

    print(from_buf(b'\x03\xff', 'int'))                             #1023
    print(from_buf(b'\x40\x44\x8e\xb8\x51\xeb\x85\x1f', '>d')[0])   #41.115
    print(from_buf(b'\x48\x45\x4c\x4c\x4f', 'str'))                 #HELLO
    print(from_buf(b'\x01', '>?'))
    print(from_buf(b'?\xf3\xae\x14z\xe1G\xae@\x12=p\xa3\xd7\n=@\x1f\x8f\\(\xf5\xc2\x8f', '>ddd'))
    