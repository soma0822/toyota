import sys #sys.exit()を使用するためのモジュール
import atexit
import signal

# ファイルを書き込みモードで開く
file = open('example.txt', 'w')
ant = 'a'

if ant == 'a':
	def exit_handler():
		file.write('Hello, World!!!!!!!!\n')
		ant = 'b'
else:
	def exit_handler():
		return

sig = 0

def sigint_handler(signum, frame):
    global sig
    while True:
        time.sleep(1)
        if sig == 1:
            break
    sig = 0

def sigint_handler2(signum, frame):
    global sig
    sig = 1

signal.signal(signal.SIGINT, sigint_handler)
signal.signal(signal.SIGQUIT, sigint_handler2)

try:
    # ファイルに書き込むテキストを指定します
    file.write('Hello, World!\n')
    file.write('This is a sample file.\n')
    file.write('Python is awesome!\n')
except Exception as e:
    # 何らかのエラーが発生した場合の処理
    print(f'Error: {e}')

try:
	file.write('Hello, World!\n')
except Exception as e:
    # 何らかのエラーが発生した場合の処理
    print(f'Error: {e}') 

while True:
	print('Hello, World!\n')
