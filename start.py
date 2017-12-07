# -*- coding: UTF-8 -*-
import sys
import os
import signal
from server.worker import Worker
pid_path = 'pid'
max_fork = 1
to_close = False
command = sys.argv[1]
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))


def do_command():
    global command
    global pid_path
    global to_close
    if 'start' == command:
        print('启动中！')
    elif 'stop' == command:
        print('关闭中!')

        # 获取主进程
        complete = '/tmp/' + pid_path
        file_object = open(complete)
        try:
            main_pid = file_object.read()
        finally:
            file_object.close()
        os.kill(int(main_pid), signal.SIGTERM)
        sys.exit(0)


def save_pid():
    global pid_path
    my_pid = os.getpid()
    my_pid = '%d' % my_pid
    file_obj = open(pid_path, 'w')
    file_obj.write(my_pid)
    file_obj.close()


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


def set_signal():
    signal.signal(signal.SIGCHLD, chldHandler)
    signal.signal(signal.SIGTERM, termHandler)


def chldHandler():
    while 1:
        try:
            result = os.waitpid(-1, os.WNOHANG)
        except:
            break
        print('Reaped child process %d' % result[0])


def termHandler():
    global to_close
    to_close = True
    for workers in Worker.workers:
        os.kill(workers.pid, signal.SIGTERM)
    os.wait()
    sys.exit(0)


def fork_workers():
    global max_fork
    while len(Worker.workers) < max_fork:
        Worker()


def monitor_worker():
    global to_close
    while True:
        if to_close:
            # 杀死所有子进程
            # 退出当前进程
            for workers in Worker.workers:
                os.kill(workers.pid, signal.SIGTERM)
            os.wait()
            sys.exit(0)
        fork_workers()


do_command()
daemon()
save_pid()
set_signal()
fork_workers()
monitor_worker()



