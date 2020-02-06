"""Программа-клиент"""

import sys
import json
import socket
import time
import argparse
from logging import getLogger
import threading
import logs.config_client_log
from errors import ReqFieldMissingError, ServerError, IncorrectDataRecivedError
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, DEFAULT_PORT, ERROR, DEFAULT_IP_ADDRESS, SENDER, MESSAGE, \
    MESSAGE_TEXT, DESTINATION, EXIT
from common.utils import get_client_message, send_message
from decos import log

# Инициализация клиентского логера
CLIENT_LOGGER = getLogger('client')


@log
def create_message_for_exit(name_of_account):
    """
    Данный метод создаёт словарь с сообщением о выходе
    """
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: name_of_account
    }


@log
def server_message(sock, my_user_name):
    """
    Данный метод обрабатывает сообщения других пользователей, поступающих с сервера
    """
    while True:
        try:
            my_msg = get_client_message(sock)
            if ACTION in my_msg and my_msg[ACTION] == MESSAGE and \
                    SENDER in my_msg and DESTINATION in my_msg \
                    and MESSAGE_TEXT in my_msg and my_msg[DESTINATION] == my_user_name:
                print(f'\nОт пользователя {my_msg[SENDER]} получено сообщение:'
                      f'\n{my_msg[MESSAGE_TEXT]}')
                CLIENT_LOGGER.info(f'От пользователя {my_msg[SENDER]} Получено сообщение:'
                                   f'\n{my_msg[MESSAGE_TEXT]}')
            else:
                CLIENT_LOGGER.error(f'С сервера: {my_msg} получено некорректное сообщение')
        except IncorrectDataRecivedError:
            CLIENT_LOGGER.error(f'Полученное сообщение не удалось декодировать.')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            CLIENT_LOGGER.critical(f'Соединение с сервером потеряно.')
            break


@log
def create_client_message(sock, name_of_account='Guest'):
    """
    Данный метод запрашивает кому отправить сообщение, а также текст самого сообщения.
    Затем отправляет полученные данные на сервер.
    """
    to_user_name = input('Введите имя получателя сообщения: ')
    my_msg = input('Введите отправляемое сообщение: ')
    my_message_dict = {
        ACTION: MESSAGE,
        SENDER: name_of_account,
        DESTINATION: to_user_name,
        TIME: time.time(),
        MESSAGE_TEXT: my_msg
    }
    CLIENT_LOGGER.debug(f'Словарь сообщения сформирован: {my_message_dict}')
    try:
        send_message(sock, my_message_dict)
        CLIENT_LOGGER.info(f'Для пользователя {to_user_name} отправлено сообщение')
    except:
        CLIENT_LOGGER.critical('Соединение с сервером потеряно.')
        sys.exit(1)


@log
def user_interactivity(sock, my_user_name):
    """
    Данный метод предназначен для взаимодействия с пользователем.
    Функция запрашивает команды и отправляет сообщения.
    """
    print_help_info()
    while True:
        my_cmd = input('Введите команду: ')
        if my_cmd == 'message':
            create_client_message(sock, my_user_name)
        elif my_cmd == 'help':
            print_help_info()
        elif my_cmd == 'exit':
            send_message(sock, create_message_for_exit(my_user_name))
            print('Соединение завершено.')
            CLIENT_LOGGER.info('Работа завершена по команде пользователя.')
            # В данном случае задержка нужна, чтобы сообщение о выходе успело уйти
            time.sleep(0.5)
            break
        else:
            print('Команда не распознана. Попробуйте ввести команду снова. '
                  'help - вывести поддерживаемые команды.')


@log
def create_of_presence(name_of_account='Guest'):
    """
    Данный метод генерирует запрос о присутствии клиента.
    """
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: name_of_account
        }
    }
    CLIENT_LOGGER.debug(f'Для пользователя {name_of_account} сформировано {PRESENCE} сообщение')
    return out


def print_help_info():
    """
    Данный метод выводит справку по поддерживаемым командам
    """
    print('Поддерживаемые команды:')
    print('message - отправить сообщение. Кому и текст - будет запрошено отдельно.')
    print('help - вывести подсказки по командам')
    print('exit - выход из приложения')


@log
def process_response_answer(my_msg):
    """
    Данный метод разбирает ответ сервера на сообщение о присутствии.
    Функция возращает 200 если все ОК или генерирует исключение при ошибке
    """
    CLIENT_LOGGER.debug(f'Разбор приветственного сообщения от сервера: {my_msg}')
    if RESPONSE in my_msg:
        if my_msg[RESPONSE] == 200:
            return '200 : OK'
        elif my_msg[RESPONSE] == 400:
            raise ServerError(f'400 : {my_msg[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


@log
def create_parser_of_arg():
    """
    Данный метод создает парсер аргументов командной строки
    и читает параметры, а также возвращаем 3 параметра
    """
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    my_parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    my_parser.add_argument('-n', '--name', default=None, nargs='?')
    my_namespace = my_parser.parse_args(sys.argv[1:])
    my_server_address = my_namespace.addr
    my_server_port = my_namespace.port
    my_client_name = my_namespace.name

    # Произвести проверку, подходящий ли номер порта
    if not 1023 < my_server_port < 65536:
        CLIENT_LOGGER.critical(
            f'Зафиксирована попытка запуска клиента с неподходящим номером порта: {my_server_port}. '
            f'Допустимый диапазон адресов с 1024 до 65535 включительно. Клиент завершается.')
        sys.exit(1)

    return my_server_address, my_server_port, my_client_name


def main():
    """
    Это главный метод приложения-клиента.
    Метод загружает параметты командной строки.
    """
    print('Консольный месседжер. Клиентский модуль.')

    # Загружаем параметы коммандной строки
    server_address, server_port, client_name = create_parser_of_arg()

    # Если имя пользователя не было задано, необходимо запросить пользователя.
    if not client_name:
        client_name = input('Введите имя пользователя: ')

    CLIENT_LOGGER.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
        f'порт: {server_port}, имя пользователя: {client_name}')

    # Инициализируем сокет, а также сообщение серверу о нашем появлении
    try:
        my_transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_transport.connect((server_address, server_port))
        send_message(my_transport, create_of_presence(client_name))
        my_answer = process_response_answer(get_client_message(my_transport))
        CLIENT_LOGGER.info(f'Установлено соединение с сервером. От сервера принят ответ: {my_answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Ошибка: полученную Json строку декодировать не удалось.')
        sys.exit(1)
    except ServerError as error:
        CLIENT_LOGGER.error(f'Сервер вернул ошибку при установке соединения: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'Ошибка: в ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        CLIENT_LOGGER.critical(
            f'Ошибка: подключиться к серверу не удалось  {server_address}:{server_port}, '
            f'Причина: конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    else:
        # Если корректно установлено соединение с сервером,
        # то запускаем клиенский процесс приема сообщений
        my_receiver = threading.Thread(target=server_message, args=(my_transport, client_name))
        my_receiver.daemon = True
        my_receiver.start()

        # Теперь запускаем отправку сообщений и взаимодействие с пользователем.
        my_user_interface = threading.Thread(target=user_interactivity, args=(my_transport, client_name))
        my_user_interface.daemon = True
        my_user_interface.start()
        CLIENT_LOGGER.debug('Процессы запущены')

        # Сторожевой таймер - основной цикл, если один из потоков завершён,
        # то значит или потеряно соединение или пользователь
        # ввёл exit. Поскольку все события обработываются в потоках,
        # достаточно просто завершить цикл.
        while True:
            time.sleep(1)
            if my_receiver.is_alive() and my_user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
