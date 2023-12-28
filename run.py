import Adafruit_PCA9685
import time  #timeというモジュールを使用する
import RPi.GPIO as GPIO #ラズパイのGPIOピンを操作するためのモジュール


# pin number
SPEED = 13
SERVO = 14

# 前進最高速、停止、後進最高速のPWM値
# pwm.set_pwm(SPEED_CNTL, 0, 380)
PWM_FORWARD_MAX = 350
PWM_FORWARD_MID = 365
PWM_FORWARD_MIN = 369
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

#超音波センサーで距離を測る関数
def Measure(trig, echo):
    sigon  = 0 #Echoピンの電圧が0V→3.3Vに変わった時間を記録する変数
    sigoff = 0 #Echoピンの電圧が3.3V→0Vに変わった時間を記録する変数
    GPIO.output(trig,GPIO.HIGH) #Trigピンの電圧をHIGH(3.3V)にする
    time.sleep(0.00001) #10μs待つ
    GPIO.output(trig,GPIO.LOW) #Trigピンの電圧をLOW(0V)にする
    while(GPIO.input(echo) == GPIO.LOW):
        sigon = time.time() #Echoピンの電圧がHIGH(3.3V)になるまで、sigonを更新
    while(GPIO.input(echo) == GPIO.HIGH):
        sigoff = time.time() #Echoピンの電圧がLOW(0V)になるまで、sigoffを更新
    distance = (sigoff - sigon)*34000/2 #距離を計算(単位はcm)
    if 200 < distance:
        distance = 200 #距離が200cm以上の場合は200cmを返す
    return distance

def Cntl(d_fr, d_lh, d_rh):
    if d_fr < 20:
        print('判断：止まる')
        # 前輪をまっすぐ向ける
        pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
        # タイヤを停止させる
        pwm.set_pwm(SPEED, 0, PWM_STOP)
        return False
    elif 50 < d_fr:
        d_lr = d_lh - d_rh
        if -20 < d_lr and d_lr < 20:
            print('前に進む')
            # 前輪をまっすぐ向ける
            pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
            if 100 < d_fr :
                pwm.set_pwm(SPEED, 0, PWM_FORWARD_MAX)
            elif 70 < d_fr :
                pwm.set_pwm(SPEED, 0, PWM_FORWARD_MID)
            else :
                pwm.set_pwm(SPEED, 0, PWM_FORWARD_MIN)
        elif d_lr <= -20:
            print('右に曲がる')
            # 前輪を右に向ける
            pwm.set_pwm(SERVO, 0, PWM_RIGHT)
            # タイヤを前進方向に回転させる
            pwm.set_pwm(SPEED, 0, PWM_FORWARD_MIN)
        elif 20 <= d_lr:
            print('左に曲がる')
            # 前輪を左に向ける
            pwm.set_pwm(SERVO, 0, PWM_LEFT)
            # タイヤを前進方向に回転させる
            pwm.set_pwm(SPEED, 0, PWM_FORWARD_MIN)
        return True

while True:  #以下の部分をずっと繰り返す
    d_fr = Measure(trig_arr[FRONT_SENSOR],echo_arr[FRONT_SENSOR])
    print('正面の壁との距離 {:.1f} cm'.format(d_fr)) #距離を表示する

    d_lh = Measure(trig_arr[LEFT_SENSOR],echo_arr[LEFT_SENSOR])
    print('左の壁との距離 {:.1f} cm'.format(d_lh)) #距離を表示する
 
    d_rh = Measure(trig_arr[RIGHT_SENSOR],echo_arr[RIGHT_SENSOR])
    print('右の壁との距離 {:.1f} cm \n================'.format(d_rh)) #距離を表示する
    
    #if Cntl(d_fr, d_lh, d_rh) == False:
       # break
    Cntl(d_fr, d_lh, d_rh)

    time.sleep(0.01)

