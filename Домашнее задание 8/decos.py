"""Декораторы"""

import sys
from logging import getLogger
import logs.config_server_log
import logs.config_client_log

# Данный метод определяет модуль - источник запуска.
# Метод работы со строкой find() возвращает индекс первого вхождения искомой подстроки,
# если он найден в данной строке, иначе - возвращает -1.
if sys.argv[0].find('client') == -1:
    # Логика такая - если не клиент то сервер!
    LOGGER = getLogger('server')
else:
    # а раз не сервер, то значит - клиент
    LOGGER = getLogger('client')


def log(my_func_to_log):
    """
    Этот метод - функция-декоратор
    """
    def my_log_saver(*args, **kwargs):
        return_result = my_func_to_log(*args, **kwargs)
        LOGGER.debug(f'Была вызвана функция {my_func_to_log.__name__} c параметрами {args}, {kwargs}. '
                     f'Вызов был произведен из модуля {my_func_to_log.__module__}')
        return return_result
    return my_log_saver
