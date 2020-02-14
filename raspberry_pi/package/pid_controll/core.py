#!/usr/bin/python
# -*- coding:utf-8 -*-

__all__=['pid']

class pid(object):
    def __init__(self, Kp, Ki, Kd):
        self.m, self.e, self.e_prev, self.integral= 0, 0, 0, 0
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd

    def update_pid(self, goal, val, dt):
        self.e = goal - val
        self.integral += self.e * dt
        self.m = self.Kp * self.e + self.Ki * self.integral + self.Kd * (self.e - self.e_prev) / dt
        self.e_prev = self.e
        
        return self.m

