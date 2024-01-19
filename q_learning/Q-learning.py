import Adafruit_PCA9685
import time  #timeというモジュールを使用する
import sys

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

feedback_server = FeedbackServer()
feedback_server.start_listening()
Q_TABLE_PATH = "test.csv"
agent = QLearningAgent(Q_TABLE_PATH)
rpi = RaspberryPiController()
pwm = Adafruit_PCA9685.PCA9685(address=0x40)
pwm.set_pwm_freq(60)

pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
pwm.set_pwm(SPEED, 0, PWM_STOP)

def get_reward(state, next_state, action):
    # 定数定義
    TIME_PENALTY = -0.01  # 時間経過に対する負の報酬
    COLLISION_PENALTY = -0.5  # 衝突に対する負の報酬
    GOOD_ACTION_REWARD = 0.5  # ゴールや素晴らしい行動に対する正の報酬
    BAD_ACTION_PENALTY = -1  # 悪い行動に対する負の報酬

    reward = 0

    reward += TIME_PENALTY

    feedback = feedback_server.get_feedback()
    if feedback == 1:
        print("good action!")
        reward += GOOD_ACTION_REWARD
    elif feedback == -1:
        print("bad action!")
        reward += BAD_ACTION_PENALTY

    if next_state[0] == 0:
        reward += COLLISION_PENALTY
    elif next_state[1] < 3 and next_state[1] < state[1]:
        reward += COLLISION_PENALTY / 2
    elif next_state[2] < 2 and next_state[2] < state[2]:
        reward += COLLISION_PENALTY / 2
    else:
        reward += 0.1
    return reward

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
    try:
        action = agent.get_action(state)
        reward, next_state = simulate_environment(state, action)
        # Q値の更新
        agent.learn(state, action, reward, next_state)
        state = next_state
    except KeyboardInterrupt:
        pwm.set_pwm(SERVO, 0, PWM_STRAIGHT)
        pwm.set_pwm(SPEED, 0, PWM_STOP)
        agent.save_q_table(Q_TABLE_PATH)
        rpi.stop()
        sys.exit(0)

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
