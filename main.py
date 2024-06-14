#!/usr/bin/env python3

import os
import sys

from ev3dev2.motor import LargeMotor, MediumMotor, MoveTank, SpeedPercent, OUTPUT_A, OUTPUT_B, OUTPUT_D
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import LightSensor, ColorSensor, InfraredSensor, UltrasonicSensor
from ev3dev2.button import Button

# constants

DO_BRICK_LOGGING = True
BALLOONS_TO_POP = 1

INFRARED_EDGE_BREAKPOINT = 20
ULTRASONIC_EDGE_BREAKPOINT = 10
LIGHT_WALL_BREAKPOINT = 15

DIR_RIGHT = 0
DIR_LEFT = 0

COLOR_NONE = 0
COLOR_WHITE = 1
COLOR_BLUE = 2
COLOR_RED = 3

SPEED = 15

T_BACK = 20 / SPEED
T_TURN = 19 / SPEED
T_TURNAROUND = 30 / SPEED
T_STEP = 10 / SPEED
T_POP = 10 / SPEED

FORWARD = SpeedPercent(SPEED)
BACK = SpeedPercent(-SPEED)
HOLD = SpeedPercent(0)

# sensors & motors

sensorInfraredRight = InfraredSensor(INPUT_1)
sensorUltrasonicLeft = UltrasonicSensor(INPUT_4)

sensorLightTop = LightSensor(INPUT_3)
sensorLightBottom = ColorSensor(INPUT_2)

engine = MoveTank(OUTPUT_B, OUTPUT_A)
needle = MediumMotor(OUTPUT_D)

# functions

def log(*args, **kwargs):
    if DO_BRICK_LOGGING:
        print(*args, **kwargs)

def logVS(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

def isOnEdgeRight():
    return sensorInfraredRight.proximity > INFRARED_EDGE_BREAKPOINT

def isOnWallLeft():
    return sensorUltrasonicLeft.distance_centimeters_continuous < ULTRASONIC_EDGE_BREAKPOINT

def isInFrontOfWall():
    return sensorLightBottom.reflected_light_intensity > LIGHT_WALL_BREAKPOINT

def getFacingColor():
    intensity = sensorLightTop.reflected_light_intensity
    if intensity > 45:
        return COLOR_WHITE
    if intensity > 35:
        return COLOR_RED
    if intensity < 23:
        return COLOR_BLUE
    return COLOR_NONE

def stop():
    engine.off()

def drive():
    engine.on(FORWARD, FORWARD)

def step(dir):
    stop()
    if dir == DIR_LEFT:
        engine.on_for_seconds(BACK, HOLD, T_STEP)
        engine.on_for_degrees(BACK, BACK, 120)
        engine.on_for_seconds(HOLD, BACK, T_STEP)
    elif dir == DIR_RIGHT:
        engine.on_for_seconds(HOLD, BACK, T_STEP)
        engine.on_for_degrees(BACK, BACK, 120)
        engine.on_for_seconds(BACK, HOLD, T_STEP)
    drive()
    while True:
        if isInFrontOfWall():
            stop()
            break

def popBalloon():
    stop()
    engine.on_for_seconds(BACK, BACK, T_POP)
    needle.on_for_degrees(SpeedPercent(10), 180)
    engine.on_for_seconds(FORWARD, FORWARD, T_POP)
    needle.on_for_degrees(SpeedPercent(-10), 180)

def colorToString(value):
    if value == COLOR_NONE:
        return 'none'
    if value == COLOR_WHITE:
        return 'white'
    if value == COLOR_BLUE:
        return 'blue'
    if value == COLOR_RED:
        return 'red'
    return 'invalid'

def run():
    log("ready")
    log("press any button to start ...")

    while not Button.any():
        ''

    log("start")

    ownColor = COLOR_NONE
    drive()
    while ownColor == COLOR_NONE:
        ownColor = getFacingColor()
    stop()
    log("set color to " + colorToString(ownColor))

    # turn right
    engine.on_for_seconds(BACK, BACK, T_BACK)
    engine.on_for_seconds(FORWARD, BACK, T_TURN)

    stepDir = DIR_RIGHT
    poppedBalloons = 0

    drive()
    while True:
        if isInFrontOfWall():
            stop()
            break
    log("wall reached")

    while True:
        log("step " + str(stepDir))
        step(stepDir)
        log("wall reached")
        color = getFacingColor()
        log("detecting " + colorToString(color) + " balloon")
        if color == COLOR_WHITE and poppedBalloons >= BALLOONS_TO_POP:
            log("pop white balloon")
            popBalloon()
            break
        if color == ownColor:
            poppedBalloons += 1
            log("pop balloon nr " + str(poppedBalloons))
            popBalloon()
        if isOnEdgeRight():
            log("change direction to left")
            stepDir = DIR_LEFT
        if isOnWallLeft:
            log("change direction to right")
            stepDir = DIR_RIGHT
    log("end")

def main():
    print('\x1Bc', end='') # reset console
    print('\x1B[?25l', end='') # disable cursor
    os.system('setfont Lat15-Terminus24x12')

    run()

if __name__ == '__main__':
    main()
