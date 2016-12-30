"""Модуль с консольным интерфейсом."""
from iface.iface import IfaceTemplate


class IfaceConsole(IfaceTemplate):
    """Консольный интерфейс."""
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
