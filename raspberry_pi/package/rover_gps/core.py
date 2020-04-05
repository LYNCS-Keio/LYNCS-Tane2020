# -*- coding: utf-8 -*-

import pynmea2
import time
from math import radians, atan2, acos, sin, cos, tan

class gps():
    def __init__(self, handler, pin):
        """
        GPS取得ライブラリのコンストラクタ。
        Parameters
        -------
        handler : pigpio.pi()
            pigpioのハンドラー。
        pin : int
            RXピンの番号。

        Notes
        -----
        RXは任意である。
        """
        self.__handler = handler
        self.__pin = pin
        self.r = 6378.137  # km

        self.__uart = self.__handler.bb_serial_read_open(self.__pin, 9600, 8)


    def sentence_reader(self):
        """ 
        sentenceを取得する。
        
        Returns
        -------
        sentence : list of char
            分割された生のセンテンス。
        """
        count = 1
        se = ""
        while count: # read echoed serial data
            (count, data) = self.__handler.bb_serial_read(self.__pin)
            #print(data)
            if count:
                try:
                    se += data.decode("utf-8")
                except:
                    break
                time.sleep(0.1)
        return se.split()


    def lat_long_reader(self, sentence):
        """
        sentenceから緯度経度を取得する。

        Returns
        -------
        list : list of float or None
            緯度と経度のリスト。sentenceにこれらの情報が含まれていなかった場合はNoneとなる。
        """
        msg = pynmea2.parse(sentence)
        lat = None
        longi = None
        if msg.latitude != None:
            lat = float(msg.latitude)
        if msg.longitude != None:
            longi = float(msg.longitude)
        return [lat, longi]


    def velocity_reader(self, sentence):
        """
        sentenceから速度を取得する。

        Returns
        -------
        list : list of float or None
            speedとcourseのリスト。sentenceにこれらの情報が含まれていなかった場合はNoneとなる。

        Notes
        -----
        speedの単位はknot, courseの単位は度である。
        """
        msg = pynmea2.parse(sentence)
        speed = None
        course = None
        if msg.spd_over_grnd != None:
            speed = float(msg.spd_over_grnd)
        if msg.true_course != None:
            course = float(msg.true_course)
        return [speed, course]


    def lat_long_measurement(self):
        """
        GNSSを用いて緯度経度を取得する。

        Returns
        -------
        list : list of float or None
            緯度と経度のリスト。これらの情報が取得できなかった場合は取得できなかったものがNoneとなる。
        """
        flag = True
        while flag:
            sentence = self.sentence_reader()
            for i in range(len(sentence)):
                #print(sentence[i])
                if sentence[i][3:6] == 'GGA' or sentence[i][3:6] == 'RMC' or sentence[i][3:6] == 'GLL':
                    try:
                        lat_and_long = self.lat_long_reader(sentence[i])
                    except:
                        pass
                    else:
                        flag = False
        return [lat_and_long[0], lat_and_long[1]]
    

    def read_all_infomation(self):
        """
        GNSSセンテンスをパースする

        Returns
        -------
        pynmea2.types
            pynmea2のmessageインスタンス

        Notes
        -----
        参考 : https://github.com/Knio/pynmea2
        """
        flag = True
        while flag:
            sentence = self.sentence_reader()
            for i in range(len(sentence)):
                try:


    def velocity_measurement(self):
        """
        GNSSから速度を取得する。

        Returns
        -------
        list : list of float or None
            speedとcourseのリスト。これらの情報が取得できなかった場合は取得できなかったものがNoneとなる。

        Notes
        -----
        speedの単位はknot, courseの単位は度である。
        """
        flag = True
        while flag:
            sentence = self.sentence_reader()
            for i in range(len(sentence)):
                #print(sentence[i])
                if sentence[i][3:6] == 'RMC':
                    try:
                        gps_data = self.velocity_reader(sentence[i])
                    except:
                        pass
                    else:
                        flag = False
        return [gps_data[0], gps_data[1]]
        


    def convert_lat_long_to_r_theta(self, lat0, long0, lat1, long1):
        """
        点0から点1への距離と方位角を計算する。
        Parameters
        -------
        lat0 : float
            点0の緯度
        long0 : float
            点0の経度
        lat1 :
            点1の緯度
        long1 :
            点1の経度

        Returns
        -------
        list : list of float
            距離と方位角のリスト。

        Notes
        -----
        距離の単位はkm, 方位角の単位はradである。
        """
        y0 = radians(lat0)
        x0 = radians(long0)
        y1 = radians(lat1)
        x1 = radians(long1)
        deltax = x1 - x0

        theta = atan2(sin(deltax), (cos(y0) * tan(y1) - sin(y0) * cos(deltax)))
        distance = self.r * acos(sin(y0) * sin(y1) + cos(y0) * cos(y1) * cos(deltax))
        return [distance, theta]


    def r_theta_to_goal(self, goal_lat, goal_long):
        """
        GNSSから目的地までの距離と方位角を取得する。

        Parameters
        -------
        goal_lat : float
            ゴールの緯度
        goal_long :
            ゴールの経度

        Returns
        -------
        list : list of float
            距離と方位角のリスト。取得できなかった場合はNoneを返す。

        Notes
        -----
        距離の単位はkm, 方位角の単位はradである。
        """
        current_coordinate = lat_long_measurement()
        if current_coordinate[0] is None or current_coordinate[1] is None:
            return None
        else:
            return convert_lat_long_to_r_theta(
                current_coordinate[0], current_coordinate[1], goal_lat, goal_long)


if __name__ == "__main__":
    import pigpio
    import time
    pi = pigpio.pi()
    pi.set_mode(21, pigpio.OUTPUT)
    pi.write(21, 1)
    gp = gps(pi, 20)
    try:
        while True:
            print(gp.lat_long_measurement())
            time.sleep(0.1)
    finally:
        pi.bb_serial_read_close(20)
        pi.stop()
