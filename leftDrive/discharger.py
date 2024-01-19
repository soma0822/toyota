import Adafruit_PCA9685
import time  #timeというモジュールを使用する
import sys
from datetime import datetime #日時を取得するためのモジュール

# pin number
SPEED = 13
SERVO = 14

# 前進最高速、停止、後進最高速のPWM値
# pwm.set_pwm(SPEED_CNTL, 0, 380)
# MAX = 350
# MIN = 369
PWM_STOP        = 380
PWM_BACK        = 395

# 左いっぱい、まっすぐ、右いっぱいのPWM値
# pwm.set_pwm(SERVO, 0, 380)
PWM_LEFT      = 290
PWM_STRAIGHT  = 340
PWM_MID_RIGHT = 365
PWM_RIGHT     = 390

pwm = Adafruit_PCA9685.PCA9685(address=0x40)
pwm.set_pwm_freq(60)

pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
pwm.set_pwm(SPEED, 0, PWM_STOP)

SLEEP_TIME = 7 * 60

try:
    pwm.set_pwm(SPEED, 0, 350)
    time.sleep(SLEEP_TIME)
except KeyboardInterrupt:
    pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
    pwm.set_pwm(SPEED, 0, PWM_STOP)
    sys.exit()

pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
pwm.set_pwm(SPEED, 0, PWM_STOP)
sys.exit()