#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Rail:

    def __init__(self, motor, min_switch, max_switch, m_per_rotation):
        """
        モーター、スイッチ、一回転ごとに進む距離を指定して作る
        
        Parameters
        ----------
        motor: instance of `Motor`
        min_switch: instance of `LimitSwitch`
        max_switch: instance of `Limit
        m_per_rotation:[m] １回転あたりの軸移動距離
        """        
        self.motor = motor
        self.min_switch = min_switch
        self.max_switch = max_switch

        # １回転あたりに、軸方向に移動する距離
        # [m]
        self.m_per_rotation = m_per_rotation

        # 軸端からの隙間を設定　設定した隙間分はステージが動かない様にする
        # [m] = [deg/step * step/rotation * m/rotation]
        self.margin = m_per_rotation * 3

        # 現在座標[-]
        self.position = None

        # レール長さ[m]
        self.length = None

    def calibrate(self):
        """リミットスイッチに当たるまでずらし、長さを測定し、位置を０に設定する"""
        # Motorクラスのキャリブレーションを実施
        self.motor.calibrate()
        self.position = 0.0

        # 奥のスイッチに当たるまで進む
        self._move_to_end()
        self._move_margin(reverse=True)
        self.position = 0.0

        # 距離を測りながら、手前のスイッチに当たるまで戻る
        self._move_to_start()
        self._move_margin(reverse=False)

        # 初期化。ここでの位置を原点
        self.length = -self.position
        self.position = 0.0

    @property
    def max_speed(self):
        """ネジとモータの組み合わせの最高速度(m/s)を計算する"""
        return float(self.motor.max_rpm) / 60.0 * self.m_per_rotation

    def min_time_to(self, position):
        """ある位置まで移動するのに必要な最短時間を計算"""
        return self.min_time_for_dist(self.position - position)

    def min_time_for_dist(self, dist):
        """dist[m]移動するにかかる最短の時間[s]を計算"""
        return abs(float(dist)) / self.max_speed

    def is_at_max(self):
        """進めなくなっているかチェック"""
        return self.max_switch.is_pressed()

    def is_at_min(self):
        """戻れなくなっているかチェック"""
        return self.min_switch.is_pressed()

    def move_to_position_in_seconds(self, position, seconds):
        """
        seconds 秒で position まで移動する

        Parameters
        ----------
        position: float
            メーターで指定する位置。０は原点。
        
        seconds: float
            移動にかかる時間。モーターが対応していない速さでの場合、例外をなげる
        """
        dist = float(position) - self.position
        rotations = dist * (1./self.m_per_rotation)
        degrees = rotations * 360.0
        check_switch = self.is_at_max if dist > 0 else self.is_at_min
        self.motor.rotate_in_seconds(degrees, seconds, check_switch, 
                                     self._accumulate_rotation)

    def _move_to_end(self):
        """遠い方のスイッチに当たるまで移動する"""
        self.motor.set_rpm(self.motor.max_rpm)
        self.motor.rotate(100000, self.is_at_max, self._accumulate_rotation)

    def _move_to_start(self):
        """近い方のスイッチに当たるまで移動する"""
        self.motor.set_rpm(self.motor.max_rpm)
        self.motor.rotate(-100000, self.is_at_min, self._accumulate_rotation)

    def _move_margin(self, reverse=False):
        """マージン分だけ動く"""
        # 設定したマージン[m]に対する、回転させる角度を計算
        # [degree] = [m / (m/rotation) / (degree / rotation)]
        angle = self.margin / self.m_per_rotation * 360.0
        angle = -angle if reverse else angle 
        
        # リミットスイッチから離れる方向に、設定角度分だけ移動 
        self.motor.rotate(angle, None, self._accumulate_rotation)

    def _accumulate_rotation(self, degrees):
        """回転した角度を位置に反映させる"""
        rotations = float(degrees) / 360.0
        meters = rotations * self.m_per_rotation
        self.position += meters


if __name__ == "__main__":
    from RPi import GPIO
    from Motor import Motor
    from LimitSwitch import LimitSwitch
    
    motor = Motor([35,33,37,31])    # モータに配線しているピンの物理番号を設定
    min_switch = LimitSwitch(40)    # リミットスイッチの状態を読み取るピン番号を指定
    max_switch = LimitSwitch(38)
    rail = Rail(motor, min_switch, max_switch, 0.008)
    rail.calibrate()                     # 初期校正
    
    rail.move_to_position_in_seconds(0.10, 10)
    print("Length: {}m".format(rail.length))   # 計測した1軸の長さを出力
    print("Position {}".format(rail.position))
    
    rail.move_to_position_in_seconds(0.05, 10)
    print("Length: {}m".format(rail.length))   # 計測した1軸の長さを出力
    print("Position {}".format(rail.position))

    # ピン設定を解除
    GPIO.cleanup()
