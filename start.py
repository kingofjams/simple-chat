# -*- coding: UTF-8 -*-
import argparse
import sys
import time
from multiprocessing import Pool, Manager, cpu_count
import os


class Start:
    def __init__(self):
        self.pid_path = 'pid'
        self.queue = Manager().Queue()
        self.max_fork = 10

    @staticmethod
    def init_command():
        parser = argparse.ArgumentParser()
        parser.add_argument('action', help='start 启动\n end 退出')  # 输入文件
        args = parser.parse_args()
        command = args.start
        if 'start' == command:
            print('启动中！')
            pass
        elif 'stop' == command:
            print('关闭中!')
            pass
        else:
            print('未找到相关命令!')
            pass

    @staticmethod
    def daemon():
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stdout.write('fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)
        os.setsid()
        os.umask(0)
        os.chdir('/tmp')
        try:
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stdout.write('fork #2 failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)

    def save_pid(self):
        my_pid = os.getpid()
        file_obj = open(self.pid_path, 'w')
        file_obj.write(my_pid)
        file_obj.close()

    def do_work(self, i):
        print(os.getpid())
        print('fsf', i)
        if not self.queue.empty():
            print(self.queue.get())
        time.sleep(5)

    def monitor_worker(self):
        pool = Pool()
        pool.map(self.do_work, range(cpu_count()))
        pool.close()
        pool.join()

if __name__ == '__main__':
    start = Start()
    start.monitor_worker()





