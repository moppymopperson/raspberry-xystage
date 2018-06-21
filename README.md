# Raspberrypi XY Stage
This was part of the SPAJAM2018 hackathon that I was lucky enough to get to participate in. It's a python module that controls an XY Stage composed of 2 motors and 4 limit switches.

```Python
from XYStage import Motor, LimitSwitch, Rail, XYStage

x_motor = Motor([13, 11, 15, 12])
x_min_switch = LimitSwitch(40)
x_max_switch = LimitSwitch(40)
x_rail = Rail(x_motor, x_min_switch, x_max_switch, 0.008)

y_motor = Motor([35,33,37,31])
y_min_switch = LimitSwitch(38)
y_max_switch = LimitSwitch(38)
y_rail = Rail(y_motor, y_min_switch, y_max_switch, 0.008)

stage = XYStage(x_rail, y_rail)
stage.calibrate()

points = [[0.0, 0.0], [0.2, 0.15], [0.3, 0.45]]
stage.trace_points(points)
```