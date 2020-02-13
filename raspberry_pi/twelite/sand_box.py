buf = [0x11, 0x22, 0x33, 0xAA, 0xBB, 0xCC]
header = [0xA5, 0x5A]

checksum = 0x00
for i in range(len(header)):
    checksum = checksum ^ header[i]
for i in range(len(buf)):
    checksum = checksum ^ buf[i]

cmd_size = len(header) + len(buf)

print(cmd_size)
cmd = 0x8000 + cmd_size
print(cmd)
print([cmd >> 8, cmd & 0b111111111])
print(bin(cmd >> 8))








# print(header)
# print(0x8000 + cmd_size)
# print(format(0x8000 + cmd_size, 'x'))
# print(buf)
# print(checksum)

# print(size)
# print(buf)
# print(len(str(format(buf, 'x'))))
# print(format(buf, 'x'))
# print(format(18838593387468, 'x'))
# print(size_calculate(buf))