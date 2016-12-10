import sys
from core import parser
from iface.enums import IfaceType
from iface.console.console import IfaceConsole


def _get_iface(type_):
    """Получить нужный интерфейс.

    :param type_: IfaceType
    :return: интерфейс, наследующий IfaceTemplate
    """
    if type_ == IfaceType.console:
        return IfaceConsole


if __name__ == '__main__':
    lang = parser.get_lang(sys.argv)  # локализация
    prop, help_ = parser.get_dict(sys.argv, lang)  # настройки
    iface_ = _get_iface(IfaceType.__getitem__(prop['iface']))
    iface_ = iface_(prop, lang, help_)
    if not parser.is_correct(prop):  # проверка корректности аргументов
        iface_.broken_args()
    else:
        if prop['help']:  # вывод справки
            iface_.print_help()
        elif prop['version']:  # вывод версии
            iface_.print_version()
        else:  # запуск интерфейса
            iface_.start()
