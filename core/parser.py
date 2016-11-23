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
        lang['prog'], lang['usage'], lang['desc'], lang['epilog'],
        add_help=False
    )
    parser.add_argument('-first', default='vfc', type=str, help=lang['first'])
    parser.add_argument('-depth', default=-1, type=int, help=lang['depth'])
    parser.add_argument('-depth_vars', default=-1, type=int,
                        help=lang['depth_vars'])
    parser.add_argument('-depth_func', default=-1, type=int,
                        help=lang['depth_func'])
    parser.add_argument('-iface', default='console', type=str,
                        help=lang['iface'])
    parser.add_argument('-gen', default='rst', type=str, help=lang['gen'])
    parser.add_argument('-v', '--version', default=False, action='store_true',
                        help=lang['ver'])
    parser.add_argument('-h', '--help', default=False, action='store_true',
                        help=lang['help'])
    parser.add_argument('-path', type=str, help=lang['path'])
    parser.add_argument('-out', type=str, help=lang['out'])
    parser.add_argument('-step', type=int, default=-1, help=lang['step'])
    parser.add_argument('-proc', type=int, default=1, help=lang['proc'])
    parser.add_argument('-numbered', type=bool, default=False,
                        action='store_true', help=lang['numbered'])
    parser.add_argument('-hidden', type=bool, default=False,
                        action='store_true', help=lang['hidden'])
    return vars(parser.parse_args(args)), parser.format_help()


def get_lang(args):
    """Получить локализацию, согласно опции -lang.

    :param args: list
    :return: dict
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument('-lang', type=str)
    result = parser.parse_args(args)
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
    elif 'path' not in kwargs:
        return False
    elif 'out' not in kwargs:
        return False
    return True
