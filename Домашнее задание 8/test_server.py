"""Unit-тесты сервера"""

import sys
import os
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from server import process_message_of_client


class TestServer(unittest.TestCase):
    """
    В сервере имеется только 1 функция для тестирования
    """
    bad_dict = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }
    good_dict = {RESPONSE: 200}

    def test_of_no_action(self):
        """
        Выдать сообщение об ошибке, если нет действия
        """
        self.assertEqual(process_message_of_client(
            {TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.bad_dict)

    def test_of_wrong_action(self):
        """
        Выдать сообщение об ошибке, если неизвестное действие
        """
        self.assertEqual(process_message_of_client(
            {ACTION: 'Wrong', TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.bad_dict)

    def test_of_no_time(self):
        """
        Выдать сообщение об ошибке, если запрос не содержит штампа времени
        """
        self.assertEqual(process_message_of_client(
            {ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}}), self.bad_dict)

    def test_of_no_user(self):
        """
        Выдать сообщение об ошибке, если нет пользователя
        """
        self.assertEqual(process_message_of_client(
            {ACTION: PRESENCE, TIME: '1.1'}), self.bad_dict)

    def test_of_unknown_user(self):
        """
        Выдать сообщение об ошибке, если имя пользователя не Guest
        """
        self.assertEqual(process_message_of_client(
            {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest1'}}), self.bad_dict)

    def test_ok_check(self):
        """
        Проверить выполнение корректного запроса
        """
        self.assertEqual(process_message_of_client(
            {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}), self.good_dict)


if __name__ == '__main__':
    unittest.main()
