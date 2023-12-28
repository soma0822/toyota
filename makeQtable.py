import numpy as np
import csv
# pin number
SPEED = 13
SERVO = 14

# 前進最高速、停止、後進最高速のPWM値
# pwm.set_pwm(SPEED_CNTL, 0, 380)
# MAX = 350
# MIN = 369
PWM_FORWARD_MAX = 363
PWM_FORWARD_MID = 365
PWM_FORWARD_MIN = 367
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

LR_DIFF = 0
actions = ["Forward", "Left", "Right"]
action_index = {action: i for i, action in enumerate(actions)}

states = [(d1, d2, d3) for d1 in range(11) for d2 in range(11) for d3 in range(11)]
state_index = {state: i for i, state in enumerate(states)}
q_table = np.zeros((len(states), len(actions)))


for f in range(0,11):
	for l in range(0,11):
		for r in range(0,11):
			state = (f, l, r)
			d_lr = l - r
			if -LR_DIFF < d_lr and d_lr < LR_DIFF:
				action = "Forward"
			elif l < 1 or (d_lr <= -LR_DIFF and f < 10):
				action = "Right"
			elif r < 1 or (LR_DIFF <= d_lr and f < 10):
				action = "Left"
			else:
				action = "Forward"
			q_table[state_index[state], action_index[action]] = 1

csv_file_path = "q_table2.csv"

with open(csv_file_path, 'w', newline='') as csv_file:
	writer = csv.writer(csv_file)
	
	# ヘッダーを書き込む（状態と行動の組み合わせを列に持つ）
	header = ["State"] + actions
	writer.writerow(header)
	
	# Qテーブルの内容を書き込む
	for i, state in enumerate(states):
		row = [str(state)] + [str(q) for q in q_table[i]]
		writer.writerow(row)