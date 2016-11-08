"""Модуль для чтения пакетов."""
import os


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


def get_modules(path, only_names=False):
    """Прочитать все модули из директории.

    :param path: путь к директории
    :param only_names: bool, True - вернуть словарь с адресами,
    False - содержимым
    :return: dict, ключи - названия файлов (без расширения), содержимое -
    str или list
    """
    if not os.path.isdir(path):
        return {}
    files = os.listdir(path)
    names = {}
    for file in files:
        if len(file) >= 4 and (file[-3:] == '.py' or file[-4:] == '.pyw'):
            path_file = os.path.join(path, file)
            if os.path.isfile(path_file):
                names[file[:-3]] = path_file
    if only_names:
        return names
    result = {}
    for name in names:
        result[name] = get_file(names[name])
    return result


def get_packages(path):
    """Получить список пакетов в директории.

    :param path: путь к директории
    :return: dict, ключи - имена пакетов, значения - пути к ним
    """
    if not os.path.isdir(path):
        return {}
    files = os.listdir(path)
    result = {}
    for file in files:
        if file == '__pycache__':
            continue
        path_file = os.path.join(path, file)
        if os.path.isdir(path_file):
            check = os.listdir(path_file)
            for c in check:
                if len(c) >= 4 and (c[-3:] == '.py' or c[-4:] == '.pyw'):
                    result[file] = path_file
                    break
    return result
