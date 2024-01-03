import numpy as np
import random

STEPS = 11

class QLearningAgent:
    #lernen_rate:学習率 学習率が大きいと，Q値の更新量が大きくなる
    #discount_factor:割引率γ γが大きいと，長期的な報酬を重視する
    #epsilon:ε-greedy法のε εの確率でランダムに行動する
    def __init__(self, q_table_path, learning_rate=0.1, discount_factor=0.9, epsilon=0.5):
        self.actions = ["Forward", "Left", "Right"]
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon

        # stateとactionのインデックスを作成
        # 例えば，action = "Forward"のとき，action_index[action] = 0
        # 例えば，state = (2, 4, 1)のとき，state_index[state] = 241
        # このインデックスを使うことで，Q-tableを高速にアクセスできる
        self.action_index = {action: i for i, action in enumerate(self.actions)}
        self.state_index = {state: i for i, state in enumerate([(d1, d2, d3) for d1 in range(STEPS) for d2 in range(STEPS) for d3 in range(STEPS)])}

        # ファイルが存在する場合は，そのファイルを読み込む
        try:
            self.q_table = np.loadtxt(q_table_path, delimiter=",")
            # ファイルの中身の形が正しいかどうかチェック
            expected_shape = (STEPS * STEPS * STEPS, len(self.actions))
            if self.q_table.shape != expected_shape:
                print(f"Warning: Loaded q_table has shape {self.q_table.shape}, but expected {expected_shape}. Reinitializing q_table.")
                self.q_table = np.zeros(expected_shape)
        # Q-tableをstate数(前のあり得る長さ*左のあり得る長さ*右のあり得る長さ)×action数(前に進む+左に曲がる+右に曲がる)の大きさで初期化
        except:
            self.q_table = np.zeros((STEPS * STEPS * STEPS, len(self.actions)))

    # εの確率でランダムに行動する
    def get_action(self, state):
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        else:
            return self.get_best_action(state)

    # Q値が最大の行動を返す
    def get_best_action(self, state):
        state_idx = self.state_index[state]
        action_values = self.q_table[state_idx]
        max_action_idx = np.argmax(action_values)
        return self.actions[max_action_idx]

    def learn(self, state, action, reward, next_state):
        state_idx = self.state_index[state]
        next_state_idx = self.state_index[next_state]
        action_idx = self.action_index[action]

        # stateとactionもとにq_tableからQ値を取得
        q_predict = self.q_table[state_idx, action_idx]
        # 行動によって得られた報酬と，行動によって得られた次の状態のQ値の最大値=(次の状態でどの行動をとったとしてもQ値が低ければ，
        # 今回の行動は間違っているし，それなりに正しい行動が残されているのであれば，今回の行動は正しいということを表すための値)の和
        q_target = reward + self.discount_factor * np.max(self.q_table[next_state_idx])
        # 今回の行動がどれだけ正しいかを再計算した値q_targetと，元々のq_tableの値q_predictの差分をとって，q値を更新する
        # q_targetがより大きければ，少しだけq値は大きくなる
        self.q_table[state_idx, action_idx] += self.learning_rate * (q_target - q_predict)

    #q_tableを保存する
    def save_q_table(self, file_name):
        np.savetxt(file_name, self.q_table, delimiter=",")


# テスト用／使用例
# Q_TABLE_PATH = "test.csv"
# agent = QLearningAgent(Q_TABLE_PATH)

# state = (0,0,1)
# action = agent.get_action(state)
# reward = 1000
# next_state = (0,0,2)
# agent.learn(state, action, reward, next_state)

# agent.save_q_table(Q_TABLE_PATH)