import Adafruit_PCA9685
import time  #timeというモジュールを使用する
import RPi.GPIO as GPIO #ラズパイのGPIOピンを操作するためのモジュール
import sys
import os #ファイル操作のためのモジュール
from datetime import datetime #日時を取得するためのモジュール
import asyncio

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
PWM_FORWARD_MAX = 362
PWM_FORWARD_MID = 363
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

trig_arr = [15,13,32] #Trigピン番号(正面、左、右)
echo_arr = [26,24,31] #Echoピン番号(正面、左、右)

LR_DIFF = 20

pwm = Adafruit_PCA9685.PCA9685(address=0x40)
pwm.set_pwm_freq(60)

CORNERING_TIME   = 2.3  # s

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

# ファイルに走行ログを書き込む
current_time = datetime.now()
formatted_time = current_time.strftime("%Y-%m-%d_%H-%M-%S")
file_name = os.path.join(log_dir, f"output_{formatted_time}.txt")
try:
    f = open(file_name, 'w') # ファイルを開く
except Exception as e:
    print(f'Error opening file: {e}')
    exit()

ftext = 'a'
logTime = time.time()

environment = 0 # 0:本番環境, 1:テスト環境（ログが出る）

if environment == 1:
    def Log(text, d_fr, d_lh, d_rh):
        global ftext
        if True:
            ftext = text
            try:
                print('\n================')
                f.write('\n================\n')
                print('{:.1f} 秒\n'.format(time.time() - logTime))
                f.write('{:.1f} 秒\n'.format(time.time() - logTime))
                print('正面の壁との距離 {:.1f} cm'.format(d_fr)) #距離を表示する
                print('左の壁との距離 {:.1f} cm'.format(d_lh)) #距離を表示する
                print('右の壁との距離 {:.1f} cm'.format(d_rh)) #距離を表示する
                f.write('正面の壁との距離 {:.1f} cm\n'.format(d_fr)) #距離を表示する
                f.write('左の壁との距離 {:.1f} cm\n'.format(d_lh)) #距離を表示する
                f.write('右の壁との距離 {:.1f} cm\n'.format(d_rh)) #距離を表示する
                print(text)
                f.write(text + "\n")
                f.flush()  # バッファをフラッシュして即座に書き込む
            except Exception as e:
                print(f'Error writing to file: {e}')
else:
    def Log(text, d_fr, d_lh, d_rh):
        return

#超音波センサーで距離を測る関数
async def Measure(trig, echo):
    GPIO.output(trig, GPIO.HIGH)
    await asyncio.sleep(0.00001)
    GPIO.output(trig, GPIO.LOW)
    # タイムアウトの秒数を設定
    timeout = time.time() + 0.1  # 例: 0.1秒 (100ミリ秒) タイムアウト
    # EchoピンがHIGHになるまで待機
    while GPIO.input(echo) == GPIO.LOW:
        if time.time() > timeout:
            return 300  # タイムアウトした場合、200cm以上の距離として扱う
    sigon = time.time()
    # EchoピンがLOWになるまで待機
    while GPIO.input(echo) == GPIO.HIGH:
        if time.time() > timeout:
            return 300  # タイムアウトした場合、200cm以上の距離として扱う
    sigoff = time.time()
    distance = (sigoff - sigon) * VS / 2
    return min(distance, 200)  # 200cmを上限とする


time_of_starting_to_turn = 0

def Cntl(d_fr, d_lh, d_rh):
    global time_of_starting_to_turn
    if d_fr < 20:
        Log('判断：止まる', d_fr, d_lh, d_rh)
        # 前輪をまっすぐ向ける
        pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
        # タイヤを停止させる
        pwm.set_pwm(SPEED, 0, PWM_STOP)
        return False
    else:
        if d_lh > 140 or d_rh < 30:
            if 0 < time_of_starting_to_turn:
                time_of_starting_to_turn = 0
            Log('左に曲がる', d_fr, d_lh, d_rh)
            # 前輪を左に向ける
            pwm.set_pwm(SERVO, 0, PWM_LEFT)
            # タイヤを前進方向に回転させる
            pwm.set_pwm(SPEED, 0, PWM_FORWARD_MID)
        elif d_lh < 70 or (d_fr < d_rh and d_fr < 160):
            if time_of_starting_to_turn == 0.0:
                time_of_starting_to_turn = time.time()
            Log('右に曲がる', d_fr, d_lh, d_rh)
            # 前輪を右に向ける
            pwm.set_pwm(SERVO, 0, PWM_RIGHT)
            # タイヤを前進方向に回転させる
            if time.time() - time_of_starting_to_turn < CORNERING_TIME :
                pwm.set_pwm(SPEED, 0, PWM_FORWARD_MID)
            else :
                pwm.set_pwm(SPEED, 0, PWM_FORWARD_MIN)
        else:
            if 0 < time_of_starting_to_turn:
                time_of_starting_to_turn = 0
            Log('前に進む', d_fr, d_lh, d_rh)
            # 前輪をまっすぐ向ける
            pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
            if 170 < d_fr :
                pwm.set_pwm(SPEED, 0, PWM_FORWARD_MID)
            else :
                pwm.set_pwm(SPEED, 0, PWM_FORWARD_MID + 1)
        return True

async def main():
    while True:
        try:
            d_fr = await Measure(trig_arr[FRONT_SENSOR], echo_arr[FRONT_SENSOR])
            d_lh = await Measure(trig_arr[LEFT_SENSOR], echo_arr[LEFT_SENSOR])
            d_rh = await Measure(trig_arr[RIGHT_SENSOR], echo_arr[RIGHT_SENSOR])

            Cntl(d_fr, d_lh, d_rh)

        except KeyboardInterrupt:
            pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
            pwm.set_pwm(SPEED, 0, PWM_STOP)
            GPIO.cleanup()
            sys.exit()

asyncio.run(main())