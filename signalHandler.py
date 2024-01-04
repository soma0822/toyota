import signal
import sys
import time
import RPi.GPIO as GPIO

SPEED = 13
SERVO = 14

# 前進最高速、停止、後進最高速のPWM値
# pwm.set_pwm(SPEED_CNTL, 0, 380)
# MAX = 350
# MIN = 369
PWM_FORWARD_MAX = 363
PWM_FORWARD_MID = 365
PWM_FORWARD_MIN = 365
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

class SignalHandler:
	def __init__(self, pwm):
		self.sig = 0
		self.sig_flag = 0
		signal.signal(signal.SIGINT, self.sigint_handler)
		signal.signal(signal.SIGQUIT, self.sigquit_handler)
		signal.signal(signal.SIGILL, self.sigill_handler)
		self.pwm = pwm

	def sigint_handler(self, signum, frame):
		self.pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
		# タイヤを停止させる
		self.pwm.set_pwm(SPEED, 0, PWM_STOP)
		while True:
			time.sleep(1)
			if self.sig == 1:
				break
		self.sig = 0

	def sigquit_handler(self, signum, frame):
		self.sig = 1
		self.sig_flag = 1

	def sigill_handler(self, signum, frame):
		self.pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
		# タイヤを停止させる
		self.pwm.set_pwm(SPEED, 0, PWM_STOP)
		# Qテーブルを保存
		GPIO.cleanup()
		# GPIOの解放
		sys.exit(0)