"""Модуль с главной логикой для генерации документации."""
import os
from multiprocessing import Pool
from analyse.analyser import Analyser
from generate.rst.rst_generator import *
import core.reader as reader
import core.writer as writer
from core.enums import *

__all__ = ['Generator']


class Generator:
    """Генератор документации, согласно заданным параметрам."""
    def __init__(self, prop, lang):
        """

        :param prop: словарь с настройками
        :param lang: словарь с локализацией
        """
        self.__prop = prop
        self.__lang = lang

    def _get_doc(self, modules, names):
        """

        :param modules: list, список списков со списками строк модулей,
        [[], ...]
        :param names: list, имена модулей, должны совпадать по индексам с
        modules
        :return: tuple, (DocType тип, проект);
        - rst: tuple, (list, dict, list),
        (список модулей, словарь с документацией модулей, документация пакета).
        Ключи для словаря - имена модулей, содержимое - list.
        """
        analyser = Analyser(self.__prop)
        analyser.analyse_all(modules, names)
        sequence, elements, classes = analyser.get_result()
        if self.__prop['gen'] == 'rst':  # rst проект
            rst = RSTGenerator(sequence, elements, classes, self.__prop,
                               self.__lang)
            return DocType.rst, rst.gen_project()

    def _get_split(self, names, modules, path, out):
        """Создать список с группами модулей, для разделения по процессам.

        :param names: list, имена модулей
        :param modules: dict, словарь с путями к модулям
        :param path: str, путь к Python проекту
        :param out: str, путь для записи документации
        :return: list, [([list, ...], [dict, ...], str, str), ...],
        [
            (
                [имя, ...],
                {имя: путь, ...},
                path, out
            )
        ]
        """
        if self.__prop['proc'] == 1:  # 1 процесс
            if self.__prop['step'] == -1:  # шаг не задан
                return [names]
        split_names = []  # разделённые имена
        if self.__prop['step'] == -1:  # равномерное разделение на процессы
            part = round(len(names) / self.__prop['proc'])
            end = self.__prop['proc']
        else:
            part = self.__prop['step']
            end = part
        i = 1
        while i <= end:  # разделение имён
            m = i * part
            split_names.append(names[m:m+part+1])
            i += 1
        split_modules = []  # разделённый словарь с путями
        for block in split_names:  # используется словарь с именами
            # чтобы содержимое групп совпадало
            add = {}
            for name in block:
                add[name] = modules[name]
            split_modules.append(add)
        result = []  # список со сгруппированным результатом
        i = 0
        while i < len(split_names):
            result.append((split_names[i], split_modules[i], path, out))
        return result

    def _proc(self, names, modules, out):
        """Метод для запуска в процессе. Создание и запись документации.

        :param names: list, имена модулей
        :param modules: dict, словарь с путями к модулям
        :param out: str, путь к директории записи документации
        """
        cont = reader.get_names(modules)
        cont_list = []
        for name in names:  # выравнивание последовательности
            cont_list.append(cont[name])
        doc_type, project = self._get_doc(cont_list, names)
        if doc_type == DocType.rst:  # запись rst проекта
            writer.write_rst_project(project[0], project[1], None, out)

    def start(self):
        """Создание и запись документации."""
        def gen(names, modules, path, out):
            """Запуск создания и записи документации в процессах.

            :param names: list, имена модулей
            :param modules: dict, словарь с путями к модулям
            :param path: str, путь к Python проекту
            :param out: str, путь к директории записи документации
            """
            split = self._get_split(names, modules, path, out)
            with Pool(self.__prop['proc']) as pool:  # запуск процессов
                pool.map(self._proc, split)

        def gen_package(path, out, root=False):
            """Создание документации по пакетуи подпакетам (рекурсивно).

            :param path: str, путь к Python проекту
            :param out: str, путь к директории записи документации
            :param root: bool, True - сгенерировать index.rst
            """
            p_names, packages = reader.get_packages(path)
            m_names, modules = reader.get_modules(path, True)
            if root:  # если это корень, то сгенерировать index.rst
                if self.__prop['gen'] == 'rst':
                    index_names = m_names.copy()
                    for pack in p_names:
                        index_names.append(pack + '/*')
                    index = RSTGenerator(None, None, None, self.__prop,
                                         self.__lang
                                         ).gen_index(names=index_names)
                    writer.write_rst_project((), (), index, out)
            gen(m_names, modules, path, out)  # генерация модулей
            for pack in p_names:  # рекурсиваня генерация пакетов
                new_out = os.path.join(out, pack)
                if not os.path.isdir(new_out):
                    os.mkdir(new_out)
                gen_package(packages[pack], new_out)

        gen_package(self.__prop['path'], self.__prop['out'], True)
