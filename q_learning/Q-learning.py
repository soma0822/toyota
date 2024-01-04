import Adafruit_PCA9685
import time  #timeというモジュールを使用する
import signal
import sys

from q_learning.q_learning_agent import QLearningAgent
from raspberry_pi_controller import RaspberryPiController

# pin number
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

Q_TABLE_PATH = "test.csv"
agent = QLearningAgent(Q_TABLE_PATH)
rpi = RaspberryPiController()
pwm = Adafruit_PCA9685.PCA9685(address=0x40)
pwm.set_pwm_freq(60)

pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
pwm.set_pwm(SPEED, 0, PWM_STOP)

sig = 0
sig_flag = 0

def sigint_handler(signum, frame):
    global sig
    pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
    # タイヤを停止させる
    pwm.set_pwm(SPEED, 0, PWM_STOP)
    while True:
        time.sleep(1)
        if sig == 1:
            break
    sig = 0

def sigquit_handler(signum, frame):
    global sig
    global sig_flag
    sig = 1
    sig_flag = 1

def sigill_handler(signum, frame):
    pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
    # タイヤを停止させる
    pwm.set_pwm(SPEED, 0, PWM_STOP)
    # Qテーブルを保存
    agent.save_q_table(Q_TABLE_PATH)
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)
signal.signal(signal.SIGQUIT, sigquit_handler)
signal.signal(signal.SIGILL, sigill_handler)

def get_reward(state, next_state, action):
    if next_state[0] == 0:
        return -10
    elif next_state[1] < 3 and next_state[1] < state[1]:
        return -5
    elif next_state[2] < 2 and next_state[2] < state[2]:
        return -5
    elif action == "Forward":
        return 3
    elif action == "Right":
        return 2
    elif action == "Left":
        return 1
    

# シミュレーション上での報酬と次の状態の仮定
def simulate_environment(state, action):

    if (action == "Forward"):
        pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
        pwm.set_pwm(SPEED, 0, PWM_FORWARD_MID)
    elif (action == "Right"):
        pwm.set_pwm(SERVO, 0, PWM_RIGHT)
        pwm.set_pwm(SPEED, 0, PWM_FORWARD_MIN)
    elif (action == "Left"):
        pwm.set_pwm(SERVO, 0, PWM_LEFT)
        pwm.set_pwm(SPEED, 0, PWM_FORWARD_MIN)
    next_state = rpi.get_state()
    reward = get_reward(state, next_state, action)
    return reward, next_state

# Q学習の更新


state = rpi.get_state()
while True:
    action = agent.get_action(state)
    reward, next_state = simulate_environment(state, action)
    # Q値の更新
    if (sig_flag == 1):
        sig_flag = 0
        state = rpi.get_state()
        continue
    agent.learn(state, action, reward, next_state)
    state = next_state

#超音波センサーで距離を測る関数

# while True:  #以下の部分をずっと繰り返す
#     d_fr = Measure(trig_arr[FRONT_SENSOR],echo_arr[FRONT_SENSOR])

#     d_lh = Measure(trig_arr[LEFT_SENSOR],echo_arr[LEFT_SENSOR])
 
#     d_rh = Measure(trig_arr[RIGHT_SENSOR],echo_arr[RIGHT_SENSOR])
    
#     Cntl(d_fr, d_lh, d_rh)
#     time.sleep(0.01)

# 学習後、Qテーブルを使用して運転
# current_state = (2, 4, 1)  # 仮の初期状態
# while True:
#     action = actions[np.argmax(q_table[state_index[current_state]])]
#     print(f"Taking action: {action}")
    
#     # センサーデータを取得して次の状態を決定する
#     # この例ではランダムな次の状態を仮定
#     next_state = np.random.choice(states)
    
#     if is_terminal_state(next_state):
#         break

#     current_state = next_state
