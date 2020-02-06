"""Unit-тесты клиента"""

import sys
import os
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from client import create_of_presence, process_answer


class TestClass(unittest.TestCase):
    """
    Данный класс - содержит тесты
    """

    def test_def_presense(self):
        """
        Это тест коректного запроса
        """
        my_test = create_of_presence()
        my_test[TIME] = 1.1  # в данном случае время необходимо приравнять
        # принудительно. В противном случае, тест никогда не будет пройден
        self.assertEqual(my_test, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_200_answer(self):
        """
        Это тест корректтного разбора ответа 200
        """
        self.assertEqual(process_answer({RESPONSE: 200}), '200 : OK')

    def test_400_answer(self):
        """
        Это тест корректного разбора ответа 400
        """
        self.assertEqual(process_answer({RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')

    def test_no_response(self):
        """
        Это тест исключения без поля RESPONSE
        """
        self.assertRaises(ValueError, process_answer, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
