import Adafruit_PCA9685
import time  #timeというモジュールを使用する
import sys
import os
from datetime import datetime

from q_learning_agent import QLearningAgent
from raspberry_pi_controller import RaspberryPiController
from feedback_server import FeedbackServer

# pin number
SPEED = 13
SERVO = 14

# 前進最高速、停止、後進最高速のPWM値
# pwm.set_pwm(SPEED_CNTL, 0, 380)
# MAX = 350
# MIN = 369
PWM_FORWARD_MAX = 360
PWM_FORWARD_MID = 362
PWM_FORWARD_MIN = 364
PWM_STOP        = 380
PWM_BACK        = 395

# 左いっぱい、まっすぐ、右いっぱいのPWM値
# pwm.set_pwm(SERVO, 0, 380)
PWM_LEFT     = 290
PWM_STRAIGHT = 340
PWM_RIGHT    = 390

D_FR = 0
D_LH = 1
D_RH = 2

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

environment = 1 # 0:本番環境, 1:テスト環境（ログが出る）

if environment == 1:
    def Log(text, d_fr, d_lh, d_rh):
        global ftext
        if ftext != text:
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

feedback_server = FeedbackServer()
feedback_server.start_listening()
Q_TABLE_PATH = "test.csv"
agent = QLearningAgent(Q_TABLE_PATH)
rpi = RaspberryPiController()
pwm = Adafruit_PCA9685.PCA9685(address=0x40)
pwm.set_pwm_freq(60)

pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
pwm.set_pwm(SPEED, 0, PWM_STOP)

TIME_PENALTY = -0.01  # 時間経過に対する負の報酬
COLLISION_PENALTY = -2  # 衝突に対する負の報酬
GOOD_ACTION_REWARD = 1  # ゴールや素晴らしい行動に対する正の報酬
BAD_ACTION_PENALTY = -1  # 悪い行動に対する負の報酬

def get_reward(state, next_state, action):
    # 定数定義
    

    reward = 0

    reward += TIME_PENALTY

    feedback = feedback_server.get_feedback()
    if feedback == 1:
        print("good action!")
        reward += GOOD_ACTION_REWARD
    elif feedback == -1:
        print("bad action!")
        reward += BAD_ACTION_PENALTY

    if state[D_RH] <= 10:
        if action == "Left":
            reward += 0.5
        elif action == "Right":
            reward += -1
    if state[D_FR] <= 20:
        if action == "Forward":
            reward += -1
    if state[D_FR]  <= state[D_LH]:
        if action == "Left":
            reward += 0.5
    if state[D_FR] <= state[D_RH]:
        if action == "Right":
            reward += 0.5
    if state[D_FR] >= 100:
        if action == "Forward":
            reward += 0.5
    if state[D_FR] >= 40 and state[D_LH] >= 40 and state[D_RH] >= 40:
            reward += 0.2
    return reward

def act(action):

    if (action == "Forward"):
        pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
        pwm.set_pwm(SPEED, 0, PWM_FORWARD_MAX)
    elif (action == "Right"):
        pwm.set_pwm(SERVO, 0, PWM_RIGHT)
        pwm.set_pwm(SPEED, 0, PWM_FORWARD_MID)
    elif (action == "Left"):
        pwm.set_pwm(SERVO, 0, PWM_LEFT)
        pwm.set_pwm(SPEED, 0, PWM_FORWARD_MID)
    return

# Q学習の更新


# import threading
# trig_arr = [15,13,32] #Trigピン番号(正面、左、右)
# echo_arr = [26,24,31] #Echoピン番号(正面、左、右)

# def measure_distance(sensor_id, trig, echo, state):
#     while True:
#         state[sensor_id] = rpi.measure_distance(trig, echo)

# distance_arr = [0, 0, 0]

# for sensor_id in [0, 1, 2]:
#     threading.Thread(target=measure_distance, args=(sensor_id, trig_arr[sensor_id], echo_arr[sensor_id], distance_arr)).start()


state_action_stack = []

state = rpi.get_state()
while True:
    try:
        if state[D_FR] <= 20 or state[D_LH] <= 10 or state[D_RH] <= 10:
            pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
            pwm.set_pwm(SPEED, 0, PWM_STOP)
            Log('STOP', state[D_FR], state[D_LH], state[D_RH])
            while state_action_stack:  # stackが空になるまで
                s, a = state_action_stack.pop()
                agent.learn(s, a, COLLISION_PENALTY, (0, 0, 0))
            print("Collision, negative reward given.")
            while next_state[D_FR] <= 20 or next_state[D_LH] <= 10 or next_state[D_RH] <= 10:
                next_state = rpi.get_state()
                time.sleep(0.5)
        else:
            action = agent.get_action(state)
            act(action)
            Log(action, state[D_FR], state[D_LH], state[D_RH])
            next_state = rpi.get_state()
            Log(f"Next state: {next_state}", state[D_FR], state[D_LH], state[D_RH])
            reward = get_reward(state, next_state, action)
            Log(f"Reward: {reward}", state[D_FR], state[D_LH], state[D_RH])
            agent.learn(state, action, reward, next_state)

        if not state_action_stack or (state, action) != state_action_stack[-1]:
            state_action_stack.append((state, action))
        state = next_state
    except KeyboardInterrupt:
        pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
        pwm.set_pwm(SPEED, 0, PWM_STOP)
        rpi.stop()
        print("\nInterrupted by user")
        try:
            choice = input("Do you want to save the Q-table before exiting? (y/n): ").lower()
            if choice == 'y':
                agent.save_q_table("test.csv")
                print("Q-table saved.")
            elif choice == 'r':
                flag = True
                while state_action_stack:  # stackが空になるまで
                    next_s, next_a = state_action_stack.pop()
                    if flag:
                        s, a = next_s, next_a
                        flag = False
                    agent.learn(s, a, GOOD_ACTION_REWARD, next_s)
                    s, a = next_s, next_a
                    print("Course completed, positive reward given.")
                agent.save_q_table("test.csv")
                print("Q-table saved.")
            else:
                print("Q-table not saved.")
        except Exception as e:
            print(f"An error occurred while saving: {e}")
        finally:
            print("Exiting program.")
            sys.exit(0)
