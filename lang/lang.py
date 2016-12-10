"""Модуль для работы с локализациями."""
import os
import sys
from configparser import ConfigParser

PATH = os.path.join(sys.path[0], 'lang', 'langs')
"""Путь к папке с конфигами."""
ENCODING = 'UTF-8'
"""Кодировка конфигов (UTF-8)."""
DEFAULT = 'ru'
"""Локализация по-умолчанию."""


def get_lang(lang):
    """Получить словарь локализации.

    :param lang: имя конфига
    :return: dict
    """
    path_lang = os.path.join(PATH, lang + '.conf')
    if os.path.isfile(path_lang):
        config = ConfigParser()
        config.read(path_lang, ENCODING)
        return dict(config)
    return {}


def get_langs():
    """Получить список доступных локализаций.

    :return: list
    """
    files = os.listdir(PATH)
    result = []
    for file in files:
        if len(file) >= 5 and file[-5:] == '.conf':
            result.append(file[:-5])
    return result
