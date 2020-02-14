# -*- coding: utf-8 -*-
#!usr/bin/python

import picamera
import time
import os
import io
import numpy as np
import cv2

__all__=['capture']

current_dir = os.path.dirname(os.path.abspath(__file__))
class capture:
    def __init__(self):
        self.camera = picamera.PiCamera()
        self.camera.resolution = (320, 240)
        self.camera.start_preview()
    
    def cap(self):
        stream = io.BytesIO()
        self.camera.capture(stream, 'jpeg')
        data = np.fromstring(stream.getvalue(), dtype=np.uint8)
        image = cv2.imdecode(data, 1)
        self.stream = image
        return image

    def flush(self):
        cv2.imwrite(current_dir + '/capture.png', self.stream)

    def __del__(self):
        self.camera.stop_preview()
        self.camera.close()

if __name__ == '__main__':
    ca = capture()
    time.sleep(2)
    stream = ca.cap()
    ca.flush()
    del ca
