import Adafruit_PCA9685
import time  #timeというモジュールを使用する
import RPi.GPIO as GPIO #ラズパイのGPIOピンを操作するためのモジュール
import sys
import os #ファイル操作のためのモジュール
from datetime import datetime #日時を取得するためのモジュール

# room temperature 
T = 22 # °C
# speed of sound at T 
VS = 33150 + 61 * T # cm / s

# pin number
SPEED = 13
SERVO = 14

# 前進最高速、停止、後進最高速のPWM値
# pwm.set_pwm(SPEED_CNTL, 0, 380)
# MAX = 350
# MIN = 369
PWM_FORWARD_MAX = 364
PWM_FORWARD_MID = 363
PWM_FORWARD_MIN = 363
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

LR_DIFF = 20

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

# logディレクトリが存在しない場合は作成する
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)

logTime = time.time()

environment = 1# 0:本番環境, 1:テスト環境（ログが出る）

def Comp(d, prev_d):
    return prev_d < d - 0.5 or d + 0.5 < prev_d 

prev_time = time.time()
if environment == 1:
    def Log(text, d_fr, d_lh, d_rh, prev_d_fr, prev_d_lh, prev_d_rh):
        now_time = time.time()
        global prev_time
        if  Comp(d_fr, prev_d_fr) or Comp(d_lh, prev_d_lh) or Comp(d_rh, prev_d_rh) :
            print('{:.1f} 秒'.format(now_time - logTime))
            print('{:.3f} 秒\n'.format(now_time - prev_time))
            print('正面の壁との距離 {:>4.1f} cm'.format(d_fr)) #距離を表示する
            print('左の壁との距離   {:>4.1f} cm'.format(d_lh)) #距離を表示する
            print('右の壁との距離   {:>4.1f} cm'.format(d_rh)) #距離を表示する
            print(text)
            print("\033[A\033[A\033[A\033[A\033[A\033[A\033[A", end='\r')
            prev_time = now_time
else:
    def Log(text, d_fr, d_lh, d_rh, prev_d_fr, prev_d_lh, prev_d_rh):
        return

#超音波センサーで距離を測る関数
def Measure(trig, echo, timeout=0.02):
    sigon  = 0 #Echoピンの電圧が0V→3.3Vに変わった時間を記録する変数
    sigoff = 0 #Echoピンの電圧が3.3V→0Vに変わった時間を記録する変数
    GPIO.output(trig,GPIO.HIGH) #Trigピンの電圧をHIGH(3.3V)にする
    time.sleep(0.00001) #10μs待つ
    GPIO.output(trig,GPIO.LOW) #Trigピンの電圧をLOW(0V)にする
    
    start_time = time.time()
    while GPIO.input(echo) == GPIO.LOW:
        sigon = time.time()
        if sigon - start_time > timeout:
            return 300  # タイムアウトの場合は-1を返す

    # エコー信号の終了時間の測定
    while GPIO.input(echo) == GPIO.HIGH:
        sigoff = time.time()
        if sigoff - start_time > timeout:
            return 300  # タイムアウトの場合は-1を返す

    # 距離の計算
    duration = sigoff - sigon
    distance = duration * VS / 2  # 距離（cm）を計算

    if 200 < distance:
        distance = 200  # 距離が200cm以上の場合は200cmを返す

    return distance

b_fr = 100
b_lh = 100
b_rh = 100

while True:  #以下の部分をずっと繰り返す
    try:
        d_fr = Measure(trig_arr[FRONT_SENSOR],echo_arr[FRONT_SENSOR])
        d_lh = Measure(trig_arr[LEFT_SENSOR],echo_arr[LEFT_SENSOR])
        d_rh = Measure(trig_arr[RIGHT_SENSOR],echo_arr[RIGHT_SENSOR])
    
        Log("", d_fr, d_lh, d_rh, b_fr, b_lh, b_rh)
        b_fr = d_fr
        b_lh = d_lh
        b_rh = d_rh
    except KeyboardInterrupt:       #Ctrl+Cキーが押された
        pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
        pwm.set_pwm(SPEED, 0, PWM_STOP)
        GPIO.cleanup()              #GPIOをクリーンアップ
        print("\n\n\n\n\n\n")
        sys.exit()                  #プログラム終了
