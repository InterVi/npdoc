"""Модуль для разбора параметров."""
from argparse import ArgumentParser
import lang.lang as locale

__all__ = ['get_dict', 'get_lang', 'is_correct']


def get_dict(args, lang):
    """Получить словарь с опциями.

    :param args: list
    :param lang: dict, локализация
    :return: tuple, (dict, str), словарь с опциями и справка
    """
    parser = ArgumentParser(
        lang['HELP']['prog'], lang['HELP']['usage'], lang['HELP']['desc'],
        lang['HELP']['epilog'], add_help=False)
    parser.add_argument('-first', default='vfc', type=str,
                        help=lang['HELP']['first'])
    parser.add_argument('-depth', default=-1, type=int,
                        help=lang['HELP']['depth'])
    parser.add_argument('-depth_vars', default=-1, type=int,
                        help=lang['HELP']['depth_vars'])
    parser.add_argument('-depth_func', default=-1, type=int,
                        help=lang['HELP']['depth_func'])
    parser.add_argument('-iface', default='console', type=str,
                        help=lang['HELP']['iface'], choices=['console'])
    parser.add_argument('-gen', default='rst', type=str,
                        help=lang['HELP']['gen'], choices=['rst'])
    parser.add_argument('-v', '--version', default=False, action='store_true',
                        dest='version', help=lang['HELP']['ver'])
    parser.add_argument('-h', '--help', default=False, action='store_true',
                        dest='help', help=lang['HELP']['help'])
    parser.add_argument('-path', type=str, help=lang['HELP']['path'])
    parser.add_argument('-out', type=str, help=lang['HELP']['out'])
    parser.add_argument('-step', type=int, default=-1,
                        help=lang['HELP']['step'])
    parser.add_argument('-proc', type=int, default=1,
                        help=lang['HELP']['proc'])
    parser.add_argument('-numbered', default=False, action='store_true',
                        help=lang['HELP']['numbered'])
    parser.add_argument('-hidden', default=False, action='store_true',
                        help=lang['HELP']['hidden'])
    parser.add_argument('-lang', type=str, help=lang['HELP']['lang'])
    parser.add_argument('-nohie', default=False, action='store_true',
                        help=lang['HELP']['nohie'])
    parser.add_argument('-notype', default=False, action='store_true',
                        help=lang['HELP']['notype'])
    parser.add_argument('-hide', default=False, action='store_true',
                        help=lang['HELP']['hide'])
    parser.add_argument('-private', default=False, action='store_true',
                        help=lang['HELP']['private'])
    parser.add_argument('-magic', default=False, action='store_true',
                        help=lang['HELP']['magic'])
    parser.add_argument('-strip', default=False, action='store_true',
                        help=lang['HELP']['strip'])
    parser.add_argument('-cleardir', default=False, action='store_true',
                        help=lang['HELP']['cleardir'])
    return vars(parser.parse_known_args(args)[0]), parser.format_help()


def get_lang(args):
    """Получить локализацию, согласно опции -lang.

    :param args: list
    :return: dict
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument('-lang', type=str)
    result, unknown = parser.parse_known_args(args)
    langs = locale.get_langs()
    if result.lang:
        if result.lang in langs:  # если такая локализация есть
            return locale.get_lang(result.lang)
        else:  # если нет - возвращаем по-умолчанию
            return locale.get_lang(locale.DEFAULT)
    else:  # если опция не задана, возвращаем по-умолчанию
        return locale.get_lang(locale.DEFAULT)


def is_correct(kwargs):
    """Проверка словаря с опциями на корректность.

    :param kwargs: dict
    :return: bool, True - словарь корректен, False - нет
    """
    if not kwargs:
        return False
    elif not kwargs['path']:
        return False
    elif not kwargs['out']:
        return False
    return True
