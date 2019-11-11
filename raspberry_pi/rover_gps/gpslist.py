# -*- coding: utf-8 -*-
import core as gps
import csv
import os
import time
import sys

# example
# python3 gpslist.py 緯度 経度

current_dir = os.path.dirname(os.path.abspath(__file__))

index = 0
filename = 'gpslog' + '%04d' % index
while os.path.isfile(current_dir + '/' + filename + '.csv') == True:
    index += 1
    filename = 'gpslog' + '%04d' % index

with open(current_dir + '/' + filename + '.csv', 'w') as c:
    wri = csv.writer(c, lineterminator='\n')
    while True:
        position = gps.lat_long_measurement()
        distance = ((poion[0] - sys.argv[1])**2 + (position[1] - sys.argv[2])**2)**0.5
        pos = [position, distance]
        wri.writerow(pos)
        time.sleep(1)
