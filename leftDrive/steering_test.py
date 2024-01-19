import Adafruit_PCA9685
import time  #timeというモジュールを使用する
import RPi.GPIO as GPIO #ラズパイのGPIOピンを操作するためのモジュール
import sys
import os #ファイル操作のためのモジュール
from datetime import datetime #日時を取得するためのモジュール
import asyncio

# pin number
SPEED = 13
SERVO = 14

# 前進最高速、停止、後進最高速のPWM値
# pwm.set_pwm(SPEED_CNTL, 0, 380)
# MAX = 350
# MIN = 369
PWM_FORWARD_MAX = 355
PWM_FORWARD_MID = 356
PWM_FORWARD_MIN = 364
PWM_STOP        = 380
PWM_BACK        = 395

# 左いっぱい、まっすぐ、右いっぱいのPWM値
# pwm.set_pwm(SERVO, 0, 380)
PWM_LEFT     = 290
PWM_STRAIGHT = 340
PWM_RIGHT    = 390

# array index
FRONT_SENSOR = 0
LEFT_SENSOR  = 1
RIGHT_SENSOR = 2

trig_arr = [15,13,32] #Trigピン番号(正面、左、右)
echo_arr = [26,24,31] #Echoピン番号(正面、左、右)

pwm = Adafruit_PCA9685.PCA9685(address=0x40)
pwm.set_pwm_freq(60)


# GPIOピン番号の指示方法
GPIO.setmode(GPIO.BOARD)
#超音波センサ初期設定
for i in range(len(trig_arr)):
    GPIO.setup(trig_arr[i],GPIO.OUT,initial=GPIO.LOW)
    GPIO.setup(echo_arr[i],GPIO.IN)

pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
pwm.set_pwm(SPEED, 0, PWM_STOP)

pwm_value = PWM_STRAIGHT

print("input l or r or number from 290 to 390")

while True:
    try:
        ope = input()
        if ope == "l":
            if pwm_value <= PWM_LEFT:
                pwm_value = PWM_LEFT
            else :
                pwm_value -= 1
        elif ope == "r":
            if PWM_RIGHT <= pwm_value:
                pwm_value = PWM_RIGHT
            else :
                pwm_value += 1
        elif PWM_LEFT <= int(ope) and int(ope) <= PWM_RIGHT:
            pwm_value = int(ope)
        else :
            continue
        print("\033[A", end='\r')
        print("PWM is", pwm_value)
        pwm.set_pwm(SERVO, 0, pwm_value)
    except KeyboardInterrupt:
        pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
        pwm.set_pwm(SPEED, 0, PWM_STOP)
        GPIO.cleanup()
        sys.exit()
