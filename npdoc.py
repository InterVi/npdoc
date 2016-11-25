import sys
from core import parser
from iface import iface
from iface.enums import IfaceType


if __name__ == '__main__':
    lang = parser.get_lang(sys.argv)  # локализация
    prop = parser.get_dict(sys.argv, lang)  # настройки
    iface_ = iface.get_iface(IfaceType.__getitem__(prop['iface']))
    if not parser.is_correct(prop):  # проверка корректности аргументов
        iface_.broken_args()
    else:
        if prop['h'] or prop['help']:  # вывод справки
            iface_.print_help()
        else:  # запуск интерфейса
            iface_.start()
