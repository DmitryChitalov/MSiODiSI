"""Программа-лаунчер"""

import subprocess

LAUNCH_PROCESS = []

while True:
    USER_ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, '
                   'x - закрыть все окна: ')

    if USER_ACTION == 'q':
        break
    elif USER_ACTION == 's':
        LAUNCH_PROCESS.append(subprocess.Popen('python server.py',
                                               creationflags=subprocess.CREATE_NEW_CONSOLE))
        LAUNCH_PROCESS.append(subprocess.Popen('python client.py -n test1',
                                               creationflags=subprocess.CREATE_NEW_CONSOLE))
        LAUNCH_PROCESS.append(subprocess.Popen('python client.py -n test2',
                                               creationflags=subprocess.CREATE_NEW_CONSOLE))
        LAUNCH_PROCESS.append(subprocess.Popen('python client.py -n test3',
                                               creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif USER_ACTION == 'x':
        while LAUNCH_PROCESS:
            VICTIM = LAUNCH_PROCESS.pop()
            VICTIM.kill()
