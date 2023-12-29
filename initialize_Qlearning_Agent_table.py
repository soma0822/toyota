import numpy as np

LR_DIFF = 20

actions = ["Forward", "Left", "Right"]
action_index = {action: i for i, action in enumerate(actions)}
states = [(d1, d2, d3) for d1 in range(11) for d2 in range(11) for d3 in range(11)]
state_index = {state: i for i, state in enumerate(states)}
q_table = np.zeros((len(states), len(actions)))

def Cntl(d_fr, d_lh, d_rh):
    if d_fr < 1:
        print('判断：止まる', d_fr, d_lh, d_rh)
        return "Stop"
    else:
        if d_lh > 7 or d_rh < 1:
            print('左に曲がる', d_fr, d_lh, d_rh)
            return "Left"
        elif d_lh < 4 or (d_fr < d_rh and d_fr < 5):
            print('右に曲がる', d_fr, d_lh, d_rh)
            return "Right"
        else:
            print('前に進む', d_fr, d_lh, d_rh)
            return "Forward"

for f in range(0,11):
    for l in range(0,11):
        for r in range(0,11):
            state = (f, l, r)
            d_lr = l - r
            action = Cntl(f, l, r)
            if action != "Stop":
                q_table[state_index[state], action_index[action]] = 0.01

np.savetxt("test.csv", q_table, delimiter=",")
