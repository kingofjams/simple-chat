# -*- coding: UTF-8 -*-
import sys
import os
from server.worker import Worker
pid_path = 'pid'
max_fork = 4
command = sys.argv[1]


def do_command():
    global command
    if 'start' == command:
        print '启动中！'
    elif 'stop' == command:
        print '关闭中!'
        exit(0)


def save_pid():
    global pid_path
    my_pid = os.getpid()
    my_pid = '%d' % my_pid
    file_obj = open(pid_path, 'w')
    file_obj.write(my_pid)
    file_obj.close()


def daemonize():
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        sys.stdout.write('fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))
        sys.exit(1)
    os.chdir('/')
    os.umask(0)
    os.setgid(pid)
    try:
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        sys.stdout.write('fork #2 failed: %d (%s)\n' % (e.errno, e.strerror))
        sys.exit(1)
    save_pid()


def fork_workers():
    global max_fork

    Worker.run_status

    while len(Worker.workers) > max_fork:
        Worker()




do_command()
daemonize()
fork_workers()


