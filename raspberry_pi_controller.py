# raspberry_pi_controller.py
import RPi.GPIO as GPIO
import time

trig_arr = [15,13,32] #Trigピン番号(正面、左、右)
echo_arr = [26,24,31] #Echoピン番号(正面、左、右)
#上の配列でセンサーの位置を表すindex
FRONT_SENSOR = 0
LEFT_SENSOR  = 1
RIGHT_SENSOR = 2

class RaspberryPiController:
    def __init__(self):
        # GPIOピン番号の指示方法
        GPIO.setmode(GPIO.BOARD)
        #超音波センサ初期設定
        for i in range(len(trig_arr)):
            GPIO.setup(trig_arr[i],GPIO.OUT,initial=GPIO.LOW)
            GPIO.setup(echo_arr[i],GPIO.IN)

    def measure_distance(self, trig, echo):
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
        return int(distance / 20)
    
    def get_state(self):
        time.sleep(0.01)
        d_fr = self.measure_distance(trig_arr[FRONT_SENSOR],echo_arr[FRONT_SENSOR])
        d_lh = self.measure_distance(trig_arr[LEFT_SENSOR],echo_arr[LEFT_SENSOR])
        d_rh = self.measure_distance(trig_arr[RIGHT_SENSOR],echo_arr[RIGHT_SENSOR])
        state = (d_fr, d_lh, d_rh)
        return state


    def set_servo(self, value):
        # サーボモーターの制御
        pass

    def set_speed(self, value):
        # スピードの制御
        pass

    # その他の必要なメソッド...
