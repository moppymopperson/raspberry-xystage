#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import sleep
import RPi.GPIO as GPIO


class Motor:

    def __init__(self, pins):
        """ラズパイのピン番号を指定して作る"""
        self.pins = pins

        # ステッピングモータの指令用
        self.states = [[GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.LOW],
                       [GPIO.HIGH, GPIO.HIGH, GPIO.LOW, GPIO.LOW],
                       [GPIO.LOW, GPIO.HIGH, GPIO.LOW, GPIO.LOW],
                       [GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW],
                       [GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.LOW],
                       [GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.HIGH],
                       [GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.HIGH],
                       [GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH]]


        self.rpm = 60.0
        self.max_rpm = 140.
        self.steps_per_rotation = 400.0     # ハーフステップ　０.9度/１ステップ
        self.calibrated = False             # 校正のチェック用


    @property
    def degrees_per_step(self):
        """ひとステップにつき回る角度"""
        # [degree]
        return 360./self.steps_per_rotation

    def calibrate(self):
        """初期化を行う"""
        # 物理番号の設定
        GPIO.setmode(GPIO.BOARD)
        # 各ピンに対して、出力設定を与える
        for p in self.pins:
            GPIO.setup(p, GPIO.OUT)

        # ピンの初期値設定
        self._set_state(self.states[0])

        # 校正終了
        self.calibrated = True

    def set_rpm(self, rpm):
        """モーターの回転速度(rpm)を設定する"""
        assert round(rpm) <= round(self.max_rpm), \
             "回転速度が高すぎる! ({}>{})".format(rpm, self.max_rpm)
        self.rpm = float(rpm)

    def current_state(self):
        """ 各ピンの今の状態(High or Low)を確認する """
        return [GPIO.input(p) for p in self.pins]

    def rotate_in_seconds(self, degrees, seconds, 
                          should_abort=None, step_callback=None):
        """
        seconds 秒で degrees だけ回転する。負の価もありえる。

        Parameters
        ----------
        degrees: float
            回転する角度
        
        seconds: float
            目標とする時間

        should_abort: function(degrees)
            この関数はステップごとに呼ばれる。Trueを返せば、｀rotate｀が
            直ちに終了する

        step_callback: function(degrees)
            この関数はステップごとに、 進んだ角度を引数に呼ばれる。
        """
        # [rotation] 指定した角度が何回転になるか計算 
        rotations_required = float(degrees)/360.0
        old_rpm = self.rpm
        self.set_rpm(abs(rotations_required / seconds * 60.0))
        self.rotate(degrees, should_abort, step_callback)
        self.set_rpm(old_rpm)

    def rotate(self, degrees, should_abort=None, step_callback=None):
        """
        degrees˚だけ回転する。 負の値もありえる。
        
        Parameters
        ----------
        degrees: float
            回転する角度

        should_abort: function(degrees)
            この関数はステップごとに呼ばれる。Trueを返せば、｀rotate｀が
            直ちに終了する

        step_callback: function(degrees)
            この関数はステップごとに、 進んだ角度を引数に呼ばれる。
        """
        assert self.calibrated, "校正するのを忘れた！"

        # [rotation] 指定した角度が何回転になるか計算 
        rotations_required = float(degrees)/360.0

        # [steps] 指定した回転回数が何ステップになるか計算
        # steps_required は float であるため、近い方の整数に丸め込んでからintに変換させる
        steps_required = int(round(abs(rotations_required * self.steps_per_rotation)))

        # [60 / [rotation/sec/60] / (step/rotation)]
        seconds_per_step = 60.0 / self.rpm / self.steps_per_rotation
        degrees_per_step = 360.0 / self.steps_per_rotation

        # 指定角度に対して、回転方向を設定する
        step = self.step_cw if degrees > 0 else self.step_ccw
        step_size = degrees_per_step if degrees > 0 else -degrees_per_step

        # 指定されたステップ数だけ回転させる
        for _ in range(0, steps_required):
            sleep(seconds_per_step)
            step()
            if step_callback is not None:
                step_callback(step_size)
            if should_abort is not None and should_abort():
                return

    def step_cw(self):
        """ CW方向に１ステップ動かす """
        # 現在のピン状態が、statesの何番目に当たるかチェック
        i = self.states.index(self.current_state())
        i = i + 1 if i < 7 else 0

        # 現在の状態を更新
        self._set_state(self.states[i])

    def step_ccw(self):
        """ CCW方向に１ステップ動かす """
        i = self.states.index(self.current_state())
        i = i - 1 if i > 0 else 7
        self._set_state(self.states[i])

    def _set_state(self, state):
        for i, p in enumerate(self.pins):
            GPIO.output(p, state[i])

if __name__ == "__main__":
    motor = Motor([13, 11, 15, 12])  # モータに配線しているピンの物理番号を設定
    motor.calibrate()                # 初期校正
    motor.rotate_in_seconds(720, 0.1)            # 指定角度分だけ回転させる

    motor2 = Motor([35,33,37,31])    # Motor2(Y-axis)
    motor2.calibrate()
    motor2.rotate_in_seconds(360, 4)

    # ピン設定を解除
    GPIO.cleanup()
