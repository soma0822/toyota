import socket
import threading

class FeedbackServer:
    def __init__(self, port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', port))
        self.server_socket.listen(1)
        self.feedback = 0  # 初期フィードバック値

    def start_listening(self):
        """フィードバック受信のためのリスニングを開始"""
        threading.Thread(target=self.listen_for_feedback, daemon=True).start()

    def listen_for_feedback(self):
        """フィードバックを待つ"""
        while True:
            client_socket, _ = self.server_socket.accept()
            data = client_socket.recv(1024)
            if data:
                feedback_command = data.decode()
                if feedback_command == 'good':
                    self.feedback = 1  # 正の報酬
                elif feedback_command == 'bad':
                    self.feedback = -1  # 負の報酬
            client_socket.close()

    def get_feedback(self):
        """現在のフィードバック値を取得し、リセット"""
        current_feedback = self.feedback
        self.feedback = 0
        return current_feedback

# # フィードバックサーバーの初期化とリスニング開始
# feedback_server = FeedbackServer()
# feedback_server.start_listening()

# 以下のget_reward関数の中で、フィードバックの仕様例を示す

# def get_reward(current_state, action, next_state):
#     """
#     現在の状態、行動、次の状態に基づいて報酬を計算する。
    
#     :param current_state: 現在の状態（前方、左方、右方の距離）
#     :param action: 実行された行動
#     :param next_state: 次の状態
#     :return: 計算された報酬
#     """
#     # 定数定義
#     TIME_PENALTY = -0.1  # 時間経過に対する負の報酬
#     SAFE_DISTANCE_REWARD = 0.05  # 安全距離保持に対する正の報酬
#     COLLISION_PENALTY = -0.5  # 衝突に対する負の報酬
#     SAFE_DISTANCE = 30  # 安全と見なされる距離（cm）
#     COLLISION_DISTANCE = 15  # 衝突と見なされる距離（cm）
#     GOOD_ACTION_REWARD = 1  # ゴールや素晴らしい行動に対する正の報酬
#     BAD_ACTION_PENALTY = -1  # 悪い行動に対する負の報酬

#     reward = 0

#     # 時間経過に対する負の報酬
#     reward += TIME_PENALTY

#     # 行いに対するフィードバック
#     if feedback_server.get_feedback() == 1:
#         print("good action!")
#         return 1
#     elif feedback_server.get_feedback() == -1:
#         print("bad action!")
#         return -1

#     # 安全距離保持の報酬
#     if all(distance >= SAFE_DISTANCE for distance in next_state):
#         reward += SAFE_DISTANCE_REWARD

#     # 衝突のペナルティ
#     if any(distance <= COLLISION_DISTANCE for distance in next_state):
#         reward += COLLISION_PENALTY

#     return reward

