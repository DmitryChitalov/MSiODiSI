"""Ошибки"""


class IncorrectDataRecivedError(Exception):
    """
    Исключение - от сокета получены некорректные данные
    """

    def __str__(self):
        return 'От удалённого компьютера принято некорректное сообщение.'


class ServerError(Exception):
    """
    Данное исключение - это ошибка сервера
    """
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class NonDictInputError(Exception):
    """
    Исключение - аргумент функции не является словарем
    """

    def __str__(self):
        return 'Аргумент функции должен являться словарем.'


class ReqFieldMissingError(Exception):
    """
    Ошибка - в принятом словаре отсутствует обязательное поле
    """

    def __init__(self, absenting_field):
        self.absenting_field = absenting_field

    def __str__(self):
        return f'Отсутствует обязательное поле в принятом словаре: {self.absenting_field}.'
