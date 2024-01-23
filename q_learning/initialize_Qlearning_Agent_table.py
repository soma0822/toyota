import numpy as np
from itertools import product
from q_learning_agent import STEPS, RESOLUTION, MIN_STEP_1, MIN_STEP_2, MIN_STEP_3

actions = ["Forward", "Left", "Right"]
action_index = {action: i for i, action in enumerate(actions)}
states = list(product(range(MIN_STEP_1, STEPS, RESOLUTION), range(MIN_STEP_2, STEPS, RESOLUTION), range(MIN_STEP_3, STEPS, RESOLUTION)))
state_index = {state: i for i, state in enumerate(states)}
q_table = np.zeros((len(states), len(actions)))

def Cntl(d_fr, d_lh, d_rh):
    if d_fr < 20:
        print('判断：止まる', d_fr, d_lh, d_rh)
        return "Stop"
    else:
        if d_lh > 140 or d_rh < 30:
            print('左に曲がる', d_fr, d_lh, d_rh)
            return "Left"
        elif d_lh < 80 or (d_fr < d_rh):
            print('右に曲がる', d_fr, d_lh, d_rh)
            return "Right"
        else:
            print('前に進む', d_fr, d_lh, d_rh)
            return "Forward"

for f in range(MIN_STEP_1, STEPS, RESOLUTION):
    for l in range(MIN_STEP_2, STEPS, RESOLUTION):
        for r in range(MIN_STEP_3, STEPS, RESOLUTION):
            state = (f, l, r)
            d_lr = l - r
            action = Cntl(f, l, r)
            if action == "Stop":
                for action in actions:
                    q_table[state_index[state], action_index[action]] = -1
            else:
                q_table[state_index[state], action_index[action]] = 0.2

np.savetxt("test3.csv", q_table, delimiter=",")
