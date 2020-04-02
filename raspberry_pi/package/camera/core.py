# -*- coding: utf-8 -*-
#!usr/bin/python

import os
import cv2
import numpy as np

__all__ = ['CamAnalysis']

current_dir = os.path.dirname(os.path.abspath(__file__))


class CamAnalysis:
    def __init__(self):
        pass

    def morphology_extract(self, stream):
        """
        モルフォロジ変換をする。

        Parameters
        -------
        stream : numpy array
            入力する画像データ。

        Notes
        -----
        ノイズを除去します。
        """
        self.stream = stream
        self.stream_hsv = cv2.cvtColor(self.stream, cv2.COLOR_BGR2HSV)
        # Target Finder
        UPPER_THRESHOLD_1 = (15, 255, 255)
        LOWER_THRESHOLD_1 = (0, 40, 40)
        self.mask = cv2.inRange(self.stream_hsv, LOWER_THRESHOLD_1, UPPER_THRESHOLD_1)
        UPPER_THRESHOLD_2 = (179, 255, 255)
        LOWER_THRESHOLD_2 = (170, 40, 40)
        self.mask += cv2.inRange(self.stream_hsv, LOWER_THRESHOLD_2, UPPER_THRESHOLD_2)
        # Remove Noises
        kernel = np.ones((9, 9))
        self.mask = cv2.morphologyEx(self.mask, cv2.MORPH_OPEN, kernel)
        self.mask = cv2.morphologyEx(self.mask, cv2.MORPH_CLOSE, kernel)

    def contour_find(self):
        """
        輪郭を検出する。

        Retruns
        -------
        x, y : float, float
            面積最大輪郭の重心座標。
        area : int
            面積最大輪郭の面積。
        """
        contours = cv2.findContours(self.mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]
        '''
        index of return value is changed depend on the version of opencv
        '''
        if len(contours) == 0 :
            return None
        else:
            areas = list(map(lambda contour: cv2.contourArea(contour), contours))
            max_area_index = areas.index(max(areas))
            #    #max_area_contour = contours[max_area_index]
            #    # Find center of gravity
            m = cv2.moments(contours[max_area_index])
            x, y = (m['m10'] / m['m00']), (m['m01'] / m['m00'])
            cv2.drawContours(self.stream, contours, -1, (255, 255, 255), 5)
            cv2.circle(self.stream, (int(x), int(y)), 30, (0, 255, 0), 5)
            return [x, y, areas[max_area_index]] 

    def save_all_outputs(self):
        """
        画像を保存する。
        """
        index = 0
        filename1 = 'bgr2hsv' + '%04d' % index
        while os.path.isfile(current_dir + '/output/' + filename1 + '.png') == True:
            index += 1
            filename1 = 'bgr2hsv' + '%04d' % index

        index = 0
        filename2 = 'morpho' + '%04d' % index
        while os.path.isfile(current_dir + '/output/' + filename2 + '.png') == True:
            index += 1
            filename2 = 'morpho' + '%04d' % index

        index = 0
        filename3 = 'contour' + '%04d' % index
        while os.path.isfile(current_dir + '/output/' + filename3 + '.png') == True:
            index += 1
            filename3 = 'contour' + '%04d' % index
        
        #cv2.imwrite(current_dir + '/output/' + filename1 + '.png', self.stream_hsv)
        #cv2.imwrite(current_dir + '/output/' + filename2 + '.png', self.mask)
        cv2.imwrite(current_dir + '/output/' + filename3 + '.png', self.stream)


if __name__ == '__main__':
    stream = cv2.imread(current_dir + '/sample.png', 1)
    cam = CamAnalysis()
    cam.morphology_extract(stream)
    coord = cam.contour_find()
    cam.save_all_outputs()
    print(coord)
