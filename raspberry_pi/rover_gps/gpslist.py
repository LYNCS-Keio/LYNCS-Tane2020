# -*- coding: utf-8 -*-
import core as gps
import csv
import os
import time
import sys
import pigpio
import threading

# example
# python3 gpslist.py lat long

lock = threading.Lock()

def get_lat_long(pin):
    position = gps.lat_long_measurement(pi, pin)
    distance = ((position[0] - float(sys.argv[1]))**2 + (position[1] - float(sys.argv[2]))**2)**0.5
    lock.acquire()
    results.append(position[0])
    results.append(position[1])
    results.append(distance)
    lock.release()
    

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
        results = []
        thread_1 = threading.Thread(target=get_lat_long, args=([5]))
        thread_2 = threading.Thread(target=get_lat_long, args=([6]))
        thread_1.start()
        thread_2.start()
        thread_1.join()
        thread_2.join()
        wri.writerow(results)

pi.stop()
