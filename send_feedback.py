import socket

def send_feedback(server_ip, port, feedback):
    """サーバーにフィードバックを送信する"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, port))
        s.sendall(feedback.encode())

if __name__ == "__main__":
    server_ip = "127.0.0.1"  # サーバーのIPアドレス（必要に応じて変更）
    port = 12345  # フィードバックサーバーのポート番号（サーバー設定に合わせる）

    while True:
        command = input("Enter command (1 for 'good', 2 for 'bad'): ")
        if command == "1":
            send_feedback(server_ip, port, "good")
        elif command == "2":
            send_feedback(server_ip, port, "bad")
        else:
            print("Invalid command. Please enter 1 for 'good' or 2 for 'bad'.")
