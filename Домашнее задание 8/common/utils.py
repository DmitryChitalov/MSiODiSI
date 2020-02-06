"""Утилиты"""

import sys
import json
from common.variables import MAX_PACKAGE_LENGTH, ENCODING
from errors import IncorrectDataRecivedError, NonDictInputError
from decos import log
sys.path.append('../')


@log
def get_client_message(client):
    """
    Данный метод является утилитой приёма и декодирования сообщения.
    Метод принимает байты, выдаёт словарь.
    А если принято что-то другое, то отдаёт ошибку значения
    """
    my_encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(my_encoded_response, bytes):
        json_response = my_encoded_response.decode(ENCODING)
        my_decoded_response = json.loads(json_response)
        if isinstance(my_decoded_response, dict):
            return my_decoded_response
        else:
            raise IncorrectDataRecivedError
    else:
        raise IncorrectDataRecivedError


@log
def send_message(sock, my_msg):
    """
    Данный метод является утилитой кодирования и отправки сообщения.
    Метод принимает словарь и отправляет его.
    """

    if not isinstance(my_msg, dict):
        raise NonDictInputError
    json_msg = json.dumps(my_msg)
    my_encoded_message = json_msg.encode(ENCODING)
    sock.send(my_encoded_message)
