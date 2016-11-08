"""Модуль для записи проектов в файлы."""
import os


def write_rst_project(modules, mods, index, path):
    """Запись rst проекта.

    :param modules: list, имена модулей
    :param mods: dict, словари с документацией модулей (list)
    :param index: list, index.rst
    :param path: путь к директории для записи
    """
    if index:
        path_file = os.path.join(path, 'index.rst')
        with open(path_file, 'w') as file:
            for line in index:
                file.write(line)
    for module in modules:
        path_file = os.path.join(path, module + '.rst')
        mod = mods[module]
        with open(path_file, 'w') as file:
            for line in mod:
                file.write(line)
