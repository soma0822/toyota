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

def sigint_handler(signum, frame):
    exit_handler()
def sigint_handler2(signum, frame):
    exit_handler()
    sys.exit(0)

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


