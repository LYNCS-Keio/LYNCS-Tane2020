# -*- coding: utf-8 -*-
#!usr/bin/python

import picamera
import time
import os
import numpy as np
import cv2

__all__=['capture']

class capture:
    def __init__(self):
        self.camera = picamera.PiCamera()
        self.camera.resolution = (320, 240)
        self.camera.start_preview()
    
    def cap(self):
        """
        PiCameraで撮影する。

        Returns
        -------
        stream : jpeg
        """
        self.stream = np.empty((240, 320, 3), dtype=np.uint8)
        self.camera.capture(self.stream, 'bgr', use_video_port=True)
        return self.stream

    def flush(self):
        """
        撮影した画像を保存する。
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cv2.imwrite(current_dir + '/capture.jpg', self.stream)

    def __del__(self):
        self.camera.stop_preview()
        self.camera.close()

if __name__ == '__main__':
    ca = capture()
    time.sleep(2)
    stream = ca.cap()
    ca.flush()
    del ca