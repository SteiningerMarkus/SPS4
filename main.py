#!/usr/bin/env python3

import os
import sys
import time

from ev3dev2.motor import LargeMotor, MoveTank, SpeedPercent, OUTPUT_A, OUTPUT_B
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import LightSensor, ColorSensor, InfraredSensor, UltrasonicSensor
from ev3dev2.led import Leds
from ev3dev2.port import LegoPort

LEFT = True
RIGHT = False

speed = 5
sback = 20 / speed
sturn = 20 / speed

forward = SpeedPercent(speed)
back = SpeedPercent(-speed)
engine = MoveTank(OUTPUT_B, OUTPUT_A)

sensorInfraredRight = InfraredSensor(INPUT_1)
sensorLightLeft = ColorSensor(INPUT_2)

sensorLightFront = LightSensor(INPUT_3)
sensorUltrasonicFront = UltrasonicSensor(INPUT_4)

def log(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

def test():
    p1 = InfraredSensor(INPUT_1)
    for i in range(1,1000):
        print(p1.proximity)
        time.sleep(.1)

def testInfraredSensor():
    return sensorInfraredRight.proximity > 20

def testLightSensor():
    return sensorLightLeft.reflected_light_intensity == 0

def testColorSensor():
    ''

def testUltrasonicSensor():
    return UltrasonicSensor.distance_centimeters_continuous < 10

def turn(dir):
    engine.off()
    engine.on_for_seconds(back, back, sback)
    if (dir == LEFT):
        engine.on_for_seconds(back, forward, sturn)
    else:
        engine.on_for_seconds(forward, back, sturn)
    engine.on(forward, forward)

def main():
    print('\x1Bc', end='') # reset console
    print('\x1B[?25l', end='') # disable cursor
    os.system('setfont Lat15-Terminus24x12')

    engine.on(forward, forward)
    while True:
        if testInfraredSensor():
            turn(LEFT)
        elif testLightSensor():
            turn(RIGHT)
        elif testUltrasonicSensor():
            engine.on(forward, forward)
            # TODO
        time.sleep(.5)

if __name__ == '__main__':
    main()
