# -*- coding: utf-8 -*-
import core as gps
import csv
import os
import time

current_dir = os.path.dirname(os.path.abspath(__file__))

index = 0
filename = 'gpslog' + '%04d' % index
while os.path.isfile(current_dir + '/' + filename + '.csv') == True:
    index += 1
    filename = 'gpslog' + '%04d' % index

with open(current_dir + '/' + filename + '.csv', 'w') as c:
    wri = csv.writer(c, lineterminator='\n')
    while True:
        pos = gps.lat_long_measurement()
        wri.writerow(pos)
        time.sleep(1)