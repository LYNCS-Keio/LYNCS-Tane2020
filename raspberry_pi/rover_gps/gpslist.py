# -*- coding: utf-8 -*-
import core as gps
import csv
import os
import time
import sys
import pigpio

# example
# python3 gpslist.py lat long

current_dir = os.path.dirname(os.path.abspath(__file__))

index = 0
filename = 'gpslog' + '%04d' % index
while os.path.isfile(current_dir + '/' + filename + '.csv') == True:
    index += 1
    filename = 'gpslog' + '%04d' % index

with open(current_dir + '/' + filename + '.csv', 'w') as c:
    wri = csv.writer(c, lineterminator='\n')
    pi = pigpio.pi()
    while True:
        position = gps.lat_long_measurement(pi, 5)
        distance = ((position[0] - float(sys.argv[1]))**2 + (position[1] - float(sys.argv[2]))**2)**0.5
        pos = [position[0], position[1], distance]
        wri.writerow(pos)
        print(pos)

pi.stop()
