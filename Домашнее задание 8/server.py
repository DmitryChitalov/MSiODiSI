"""Программа-сервер"""


import socket
import sys
import argparse
import select
import time
import json
from logging import getLogger
import logs.config_server_log
from errors import IncorrectDataRecivedError
from common.variables import ACTION, USER, ACCOUNT_NAME, PRESENCE, \
    TIME, DEFAULT_PORT, MAX_CONNECTIONS, ERROR, SENDER, MESSAGE, \
    MESSAGE_TEXT, RESPONSE_400, DESTINATION, RESPONSE_200, EXIT
from common.utils import get_client_message, send_message
from decos import log

# Инициализация логирования сервера.
SERVER_LOGGER = getLogger('server')


@log
def process_message_of_client(my_msg, msgs_list, my_client, clients_list, names_list):
    """
    Данный метод является обработчиком сообщений от клиентов.
    На входе принимает словарь - сообщение от клинта, затем
    проверяет корректность и возвращает словарь-ответ для клиента
    """
    SERVER_LOGGER.debug(f'Выполняем разбор сообщения от клиента : {my_msg}')
    # Если это сообщение о присутствии, то принимаем и отвечаем
    if ACTION in my_msg and my_msg[ACTION] == PRESENCE and \
            TIME in my_msg and USER in my_msg:
        # Если такой пользователь ещё не зарегистрирован,
        # регистрируем, иначе отправляем ответ и завершаем соединение.
        if my_msg[USER][ACCOUNT_NAME] not in names_list.keys():
            names_list[my_msg[USER][ACCOUNT_NAME]] = my_client
            send_message(my_client, RESPONSE_200)
        else:
            my_response = RESPONSE_400
            my_response[ERROR] = 'Данное имя пользователя уже занято.'
            send_message(my_client, my_response)
            clients_list.remove(my_client)
            my_client.close()
        return
    # Если это сообщение - добавляем его в очередь сообщений. Ответ не требуется.
    elif ACTION in my_msg and my_msg[ACTION] == MESSAGE and \
            DESTINATION in my_msg and TIME in my_msg \
            and SENDER in my_msg and MESSAGE_TEXT in my_msg:
        msgs_list.append(my_msg)
        return
    # Если клиент выходит
    elif ACTION in my_msg and my_msg[ACTION] == EXIT and ACCOUNT_NAME in my_msg:
        clients_list.remove(names_list[my_msg[ACCOUNT_NAME]])
        names_list[my_msg[ACCOUNT_NAME]].close()
        del names_list[my_msg[ACCOUNT_NAME]]
        return
    # Иначе отдаём Bad request
    else:
        my_response = RESPONSE_400
        my_response[ERROR] = 'Запрос некорректен.'
        send_message(my_client, my_response)
        return


@log
def process_message(my_msg, names_list, listen_socks_list):
    """
    Это метод адресной отправки сообщения определённому клиенту.
    На входе:
     словарь сообщение,
     список зарегистрированых пользователейб
     слушающие сокеты.
    Ничего не возвращает.
    """
    if my_msg[DESTINATION] in names_list and names_list[my_msg[DESTINATION]] in listen_socks_list:
        send_message(names_list[my_msg[DESTINATION]], my_msg)
        SERVER_LOGGER.info(f'Пользователю {my_msg[DESTINATION]} отправлено сообщение '
                    f'от пользователя {my_msg[SENDER]}.')
    elif my_msg[DESTINATION] in names_list and names_list[my_msg[DESTINATION]] not in listen_socks_list:
        raise ConnectionError
    else:
        SERVER_LOGGER.error(
            f'Отправка сообщения невозможна. '
            f'Пользователь {my_msg[DESTINATION]} не зарегистрирован на сервере.')


@log
def create_parser_of_arg():
    """
    Этот метод выполняет парсинг аргументов командной строки
    """
    SERVER_LOGGER.info(f'Парсинг аргументов командной строки')
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    my_parser.add_argument('-a', default='', nargs='?')
    namespace = my_parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    # проверить, получен ли корретный номер порта для работы сервера.
    if not 1023 < listen_port < 65536:
        SERVER_LOGGER.critical(
            f'Попытка запуска сервера с указанием неподходящего порта '
            f'{listen_port}. Допустимы адреса с 1024 до 65535.')
        sys.exit(1)

    return listen_address, listen_port


def main():
    """
    Это главный метод приложения-сервера.
    Загружает параметры командной строки. А если нет параметров - то задаём значения по умоланию.
    """
    listen_address, listen_port = create_parser_of_arg()

    SERVER_LOGGER.info(
        f'Запущен сервер, порт для подключений: {listen_port}, '
        f'адрес с которого принимаются подключения: {listen_address}. '
        f'Если адрес не указан, принимаются соединения с любых адресов.')
    # Подготовить сокет
    my_transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_transport.bind((listen_address, listen_port))
    my_transport.settimeout(0.5)

    # объявить список клиентов и очередь сообщений
    clients_list = []
    messages_list = []

    # Словарь, содержащий имена пользователей и соответствующие им сокеты.
    names = dict()

    # Слушать порт
    my_transport.listen(MAX_CONNECTIONS)
    # Открыть основной цикл программы сервера
    while True:
        # Ждать подключения, если таймаут вышел, поймать исключение.
        try:
            my_client, my_client_address = my_transport.accept()
        except OSError:
            pass
        else:
            SERVER_LOGGER.info(f'Установлено соедение с ПК {my_client_address}')
            clients_list.append(my_client)

        recv_data_lst = []
        send_data_lst = []
        err_lst = []
        # Проверить на наличие ждущих клиентов
        try:
            if clients_list:
                recv_data_lst, send_data_lst, err_lst = select.select(clients_list, clients_list, [], 0)
        except OSError:
            pass

        # принять сообщения и если они есть - положить в словарь.
        # А если ошибка - исключить клиента.
        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    process_message_of_client(get_client_message(client_with_message),
                                              messages_list, client_with_message, clients_list, names)
                except Exception:
                    SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                f'отключился от сервера.')
                    clients_list.remove(client_with_message)

        # Проверить, есть ли сообщения. Если есть - обрабатываем каждое последовательно.
        for i in messages_list:
            try:
                process_message(i, names, send_data_lst)
            except Exception:
                SERVER_LOGGER.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                clients_list.remove(names[i[DESTINATION]])
                del names[i[DESTINATION]]
        messages_list.clear()


if __name__ == '__main__':
    main()
