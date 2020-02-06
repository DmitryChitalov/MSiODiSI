"""Unit-тесты утилит"""

import sys
import os
import unittest
import json

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE, ENCODING
from common.utils import get_client_message, send_message


class TestSocket:
    """
    Данный класс - тестовый  для тестирования отправки и получения сообщений.
    При создании конструктор класса требует словарь, который будет прогоняться
    через тестовый метод.
    """

    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.receved_message = None

    def send(self, message_for_sending):
        """
        Данный метод - тестовая функция отправки. Метод корретно кодирует сообщение,
        так-же сохраняет то, что должно было отправлено в сокет.
        message_to_send - то, что отправляем в сокет.
        """
        json_message_for_test = json.dumps(self.test_dict)
        # кодирует сообщение
        self.encoded_message = json_message_for_test.encode(ENCODING)
        # сохраняем что должно было отправлено в сокет
        self.receved_message = message_for_sending

    def recv(self, max_len):
        """
        Данный метод нужен для получения данных из сокета
        """
        json_message_for_test = json.dumps(self.test_dict)
        return json_message_for_test.encode(ENCODING)


class Tests(unittest.TestCase):
    """
    Данный класс - тестовый класс. В нем выполняется, собственно, тестирование.
    """
    test_dict_send = {
        ACTION: PRESENCE,
        TIME: 111111.111111,
        USER: {
            ACCOUNT_NAME: 'test_test'
        }
    }
    test_dict_recv_ok = {RESPONSE: 200}
    test_dict_recv_err = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }

    def test_send_message(self):
        """
        Данный метод тестирует корректность работы метода отправки.
        Создает тестовый сокет и проверяет корректность отправки словаря.
        """
        # создадим экземпляр тестового словаря, который будет хранить собственно тестовый словарь
        socket_for_testing = TestSocket(self.test_dict_send)
        # сделаем вызов тестируемого метода. А результаты сохраним в тестовом сокете
        send_message(socket_for_testing, self.test_dict_send)
        # выполним проверку корретности кодирования словаря.
        # сделаем сравнение результата доверенного кодирования и результат от тестируемоого метода
        self.assertEqual(socket_for_testing.encoded_message, socket_for_testing.receved_message)
        # также, проверим генерацию исключения, если на вход подать не словарь.
        self.assertRaises(TypeError, send_message, socket_for_testing, 1111)

    def test_get_client_message(self):
        """
        Данный метод выполняет тестирование функции приема сообщения
        """
        test_sock_ok = TestSocket(self.test_dict_recv_ok)
        test_sock_err = TestSocket(self.test_dict_recv_err)
        # выполним тестирование корректной расшифровки корректного словаря
        self.assertEqual(get_client_message(test_sock_ok), self.test_dict_recv_ok)
        # проведем тестирование корректной расшифровки ошибочного словаря
        self.assertEqual(get_client_message(test_sock_err), self.test_dict_recv_err)


if __name__ == '__main__':
    unittest.main()
