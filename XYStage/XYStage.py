#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
import json
from threading import Thread

from Motor import Motor
from LimitSwitch import LimitSwitch
from Rail import Rail

class XYStage:

    def __init__(self, x_rail, y_rail):
        """XとY軸のレールを指定して作る"""
        self.x_rail = x_rail
        self.y_rail = y_rail
        self.calibrated = False

    def calibrate(self):
        """両方のリミットスイッチに当たるまで進み、位置を0,0とする"""
        x_thread = Thread(target=self.x_rail.calibrate)
        y_thread = Thread(target=self.y_rail.calibrate)
        x_thread.start()
        y_thread.start()
        x_thread.join()
        y_thread.join()
        self.calibrated = True

    def current_position(self):
        """現在位置を取得する"""
        return (self.x_rail.position, self.y_rail.position)

    def move_to_point(self, x, y):
        """現在値から指定した座標まで移動する"""
        assert self.calibrated, "校正を忘れたよ！"

        # かかる最短の時間を計算
        min_x_time = self.x_rail.min_time_to(x)
        min_y_time = self.y_rail.min_time_to(y)
        seconds = max(min_x_time, min_y_time)

        # レールごとにスレッドを作る
        x_thread = Thread(target=self.x_rail.move_to_position_in_seconds, args=(x, seconds))
        y_thread = Thread(target=self.y_rail.move_to_position_in_seconds, args=(y, seconds))

        x_thread.start()
        y_thread.start()

        x_thread.join()
        y_thread.join()

    def trace_points(self, points):
        """
        Moves the XY stage between a series of points. 

        This method is meant to be called from another process. Updates
        will be delivered to the parent progress via stdin.

        Parameters
        ----------
        points: list<list<float>>
            A 2D list of points of the form [[x0, y0], [x1, y1], [x2, y2]]
        """
        for idx, (x, y) in enumerate(points):
            self.move_to_point(x, y)
            progress = {'current': idx + 1, 'total': len(points)}
            sys.stdout.write(json.dumps(progress) + '\n')
            sys.stdout.flush()

if __name__ == "__main__":
    """
    Usage example:

    python XYStage.py [[0.5, 1], [0, 0], [1, 0]]
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('points', help="A 2D array of points as JSON")
    args = parser.parse_args()

    x_motor = Motor([13, 11, 15, 12])
    x_min_switch = LimitSwitch(40)
    x_max_switch = LimitSwitch(40)
    x_rail = Rail(x_motor, x_min_switch, x_max_switch, 0.008)

    y_motor = Motor([35,33,37,31])
    y_min_switch = LimitSwitch(38)
    y_max_switch = LimitSwitch(38)
    y_rail = Rail(y_motor, y_min_switch, y_max_switch, 0.008)

    points = json.loads(args.points)

    stage = XYStage(x_rail, y_rail)
    stage.calibrate()
    stage.trace_points(points)
