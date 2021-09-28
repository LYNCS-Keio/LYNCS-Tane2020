from package import icm20948
import csv
import os

b = [30.0, 0.0, 15.0, 20] #[x, y, z, r]
x = 0.0
y = 0.0
z = 0.0
lr = 0.0001

def update_magnetometer_data(x, y, z):
    dx = x - b[0]
    dy = y - b[1]
    dz = z - b[2]
    f = dx*dx + dy*dy + dz*dz - b[3]*b[3]
    
    b[0] = b[0] + 4 * lr * f * dx
    b[1] = b[1] + 4 * lr * f * dy
    b[2] = b[2] + 4 * lr * f * dz
    b[3] = b[3] + 4 * lr * f * b[3]

current_dir = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    import pigpio
    pi = pigpio.pi()
    imu = icm20948.icm20948(pi)

    with open(current_dir + '/' + 'log0001' + '.csv', 'w') as c:
        f = csv.writer(c, lineterminator = '\n')
        while True:
            x, y, z = imu.read_magnetometer_data()
            update_magnetometer_data(x, y, z)
            print(b+[x,y,z])
            f.writerow(b+[x, y, z])
