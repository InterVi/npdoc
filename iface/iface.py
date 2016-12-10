"""Модуль для работы с интерфейсами."""
from core.core import Generator

__all__ = ['IfaceTemplate']


class IfaceTemplate:
    """Шаблон каркаса интерфейса, который наследуют все интерфейсы."""
    def __init__(self, prop, lang, help_str):
        """

        :param prop: dict, словарь с параметрами
        :param lang: dict, словарь с локализацией
        :param help_str: str, справка
        """
        self._prop = prop
        self._lang = lang
        self._help = help_str
        self.generator = Generator(prop, lang)

    def start(self):
        """Запуск интерфейса."""
        pass

    def print_help(self):
        """Вывод справки."""
        pass

    def print_version(self):
        """Вывод версии."""
        pass

    def broken_args(self):
        """Вывод сообщения о неверных аргументах запуска."""
        pass
