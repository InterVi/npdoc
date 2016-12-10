"""Модуль для записи проектов в файлы."""
import os

__all__ = ['write_rst_project']


def write_rst_project(modules, mods, index, path):
    """Запись rst проекта.

    :param modules: list, имена модулей
    :param mods: dict, словари с документацией модулей (list)
    :param index: list, index.rst
    :param path: путь к директории для записи
    """
    if index:  # запись главной страницы (если есть)
        path_file = os.path.join(path, 'index.rst')
        with open(path_file, 'w') as file:
            for line in index:
                file.write(line)
                file.write('\n')
    for module in modules:  # запись модулей
        path_file = os.path.join(path, module + '.rst')
        mod = mods[module]
        with open(path_file, 'w') as file:
            for line in mod:
                file.write(line)
                file.write('\n')
