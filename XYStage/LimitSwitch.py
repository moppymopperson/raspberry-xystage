#!/usr/bin/env python
# -*- coding: utf-8 -*-
from RPi import GPIO


class LimitSwitch:

    def __init__(self, pin):
        """ラズパイのピンを指定して作る"""
        self.pin = pin
        GPIO.setmode(GPIO.BOARD)    # ピン番号指定を物理番号でセット
        GPIO.setup(pin, GPIO.IN)    # 指定したピンをスイッチの電圧読み取りに設定

    def is_pressed(self):
        """リミットスイッチが押されている場合、Trueを返す"""
        # 0:スイッチオフ .1:スイッチオン
        return GPIO.input(self.pin) > 0.5


if __name__ == "__main__":
    switch1 = LimitSwitch(32)
    switch2 = LimitSwitch(36)
    switch3 = LimitSwitch(38)
    switch4 = LimitSwitch(40)

    import time 
    for i in range(100):
        print("1 : {}".format(switch1.is_pressed()))
        print("2 : {}".format(switch2.is_pressed()))
        print("3 : {}".format(switch3.is_pressed()))
        print("4 : {}".format(switch4.is_pressed()))
        time.sleep(0.1)
    
    GPIO.cleanup()
