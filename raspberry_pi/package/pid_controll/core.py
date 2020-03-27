#!/usr/bin/python
# -*- coding:utf-8 -*-

__all__=['pid']

class pid(object):
    def __init__(self, Kp, Ki, Kd):
        """ 
        pid制御クラスのコンストラクタ。

        Parameters
        -------
        Kp, Ki, Kd : float, float, float
            p, i, dゲイン。
        """
        self.m, self.e, self.e_prev, self.integral= 0, 0, 0, 0
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd

    def update_pid(self, goal, val, dt):
        """ 
        pidをアップデートする。

        Parameters
        -------
        goal : float or int
            目標値。
        val : float or int
            測定値。
        dt : 前回アップデート時からの経過時間。

        Returns
        -------
        m : float
            操作量。
        """
        self.e = goal - val
        self.integral += self.e * dt
        self.m = self.Kp * self.e + self.Ki * self.integral + self.Kd * (self.e - self.e_prev) / dt
        self.e_prev = self.e
        
        return self.m

