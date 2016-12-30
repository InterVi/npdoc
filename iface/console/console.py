"""Модуль с консольным интерфейсом."""
from iface.iface import IfaceTemplate
from core.core import Generator


class IfaceConsole(IfaceTemplate):
    """Консольный интерфейс."""
    def __init__(self, prop, lang, help_str):
        """

        :param prop: dict, словарь с параметрами
        :param lang: dict, словарь с локализацией
        :param help_str: str, справка
         """
        IfaceTemplate.__init__(self, prop, lang, help_str)
        self.generator = Generator(prop, lang)

    def start(self):
        print(self._lang['CONSOLE']['start'])
        if self.generator.start():
            print(self._lang['CONSOLE']['end'])
        else:
            print(self._lang['CONSOLE']['notfound'])

    def print_help(self):
        print(self._help)

    def print_version(self):
        print('pre alpha')

    def broken_args(self):
        self.print_help()
