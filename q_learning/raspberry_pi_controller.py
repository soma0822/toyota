# raspberry_pi_controller.py
import RPi.GPIO as GPIO
import time
from q_learning_agent import RESOLUTION, MIN_STEP, STEPS

# room temperature 
T = 22 # °C
# speed of sound at T 
VS = 33150 + 61 * T # cm / s

trig_arr = [15,13,32] #Trigピン番号(正面、左、右)
echo_arr = [26,24,31] #Echoピン番号(正面、左、右)
#上の配列でセンサーの位置を表すindex
FRONT_SENSOR = 0
LEFT_SENSOR  = 1
RIGHT_SENSOR = 2

MAX_DISTANCE = STEPS - 1

class RaspberryPiController:
    def __init__(self):
        # GPIOピン番号の指示方法
        GPIO.setmode(GPIO.BOARD)
        #超音波センサ初期設定
        for i in range(len(trig_arr)):
            GPIO.setup(trig_arr[i],GPIO.OUT,initial=GPIO.LOW)
            GPIO.setup(echo_arr[i],GPIO.IN)

    def measure_distance(self, trig, echo, timeout=0.02):
        sigon  = 0 #Echoピンの電圧が0V→3.3Vに変わった時間を記録する変数
        sigoff = 0 #Echoピンの電圧が3.3V→0Vに変わった時間を記録する変数
        GPIO.output(trig,GPIO.HIGH) #Trigピンの電圧をHIGH(3.3V)にする
        time.sleep(0.00001) #10μs待つ
        GPIO.output(trig,GPIO.LOW) #Trigピンの電圧をLOW(0V)にする
        
        start_time = time.time()
        while GPIO.input(echo) == GPIO.LOW:
            sigon = time.time()
            if sigon - start_time > timeout:
                return int(MAX_DISTANCE)  # タイムアウトの場合は-1を返す

        while GPIO.input(echo) == GPIO.HIGH:
            sigoff = time.time()
            if sigoff - start_time > timeout:
                return int(MAX_DISTANCE)  # タイムアウトの場合は-1を返す

        # 距離の計算
        duration = sigoff - sigon
        distance = duration * VS / 2  # 音速を340m/sとして、距離（cm）を計算

        if distance < MIN_STEP:
            distance = MIN_STEP
        if MAX_DISTANCE < distance:
            distance = MAX_DISTANCE  # 距離が200cm以上の場合は200cmを返す

        return int(distance)

    def get_state(self):
        # time.sleep(0.01)
        d_fr = self.measure_distance(trig_arr[FRONT_SENSOR],echo_arr[FRONT_SENSOR])
        d_lh = self.measure_distance(trig_arr[LEFT_SENSOR],echo_arr[LEFT_SENSOR])
        d_rh = self.measure_distance(trig_arr[RIGHT_SENSOR],echo_arr[RIGHT_SENSOR])

        d_fr_rounded = (d_fr // RESOLUTION) * RESOLUTION
        d_lh_rounded = (d_lh // RESOLUTION) * RESOLUTION
        d_rh_rounded = (d_rh // RESOLUTION) * RESOLUTION
        state = (d_fr_rounded, d_lh_rounded, d_rh_rounded)
        print("state is ", state)
        return state


    def set_servo(self, value):
        # サーボモーターの制御
        pass

    def set_speed(self, value):
        # スピードの制御
        pass
    
    def stop(self):
        GPIO.cleanup()
    # GPIOの解放

    # その他の必要なメソッド...