"""Модуль для чтения пакетов."""
import os

__all__ = ['get_file', 'get_names', 'get_modules', 'get_packages']


def get_file(path):
    """Прочитать файл.

    :param path: путь к файлу
    :return: list
    """
    if not os.path.isfile(path):
        return []
    result = []
    with open(path) as file:
        result.append(file.readline())
    return result


def get_names(names):
    """Прочитать выбранные модули.

    :param names: dict, ключи - имена модулей, содержимое - пути
    :return: dict, ключи - имена модулей, содержимое - list
    """
    result = {}
    for name in names:
        result[name] = get_file(names[name])
    return result


def get_modules(path, only_names=False):
    """Прочитать все модули из директории.

    :param path: путь к директории
    :param only_names: bool, True - вернуть словарь с адресами,
    False - содержимым
    :return: tuple, (list, dict), (имена, модули),
    ключи - названия файлов (без расширения), содержимое - str или list
    """
    if not os.path.isdir(path):
        return {}
    files = os.listdir(path)
    modules = {}  # словарь с адресами
    names = []  # список с именами (для сохранения последовательности)
    for file in files:
        if len(file) >= 4 and (file[-3:] == '.py' or file[-4:] == '.pyw'):
            # если подходящее расширение
            path_file = os.path.join(path, file)
            if os.path.isfile(path_file):  # если это файл
                name = file[:-3]
                modules[name] = path_file
                names.append(name)
    if only_names:  # если нужно вернуть только имена и адреса
        return names, modules
    result = {}  # словарь с содержимым модулей
    for name in names:
        result[name] = get_file(modules[name])
    return names, result


def get_packages(path):
    """Получить список пакетов в директории.

    :param path: путь к директории
    :return: tuple, (list, dict), (имена, пакеты)
    ключи - имена пакетов, значения - пути к ним
    """
    if not os.path.isdir(path):
        return {}
    files = os.listdir(path)
    packages = {}  # словарь с адресами
    names = []  # список с именами (для сохранения последовательности)
    for file in files:
        if file == '__pycache__':
            continue
        path_file = os.path.join(path, file)
        if os.path.isdir(path_file):
            check = os.listdir(path_file)
            for c in check:
                if len(c) >= 4 and (c[-3:] == '.py' or c[-4:] == '.pyw'):
                    packages[file] = path_file
                    names.append(file)
                    break
    return names, packages
