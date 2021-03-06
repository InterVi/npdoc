"""Анализ и документирование кода."""
from analyse.data import *
import analyse.utils as utils
from analyse.enums import *

__all__ = ['Analyser']


class Analyser:
    """Анализтор и документатор кода."""
    def __init__(self, prop):
        """

        :param prop: Словарь с настройками.

        first -> vfc:
        v - переменные;
        f - функции / методы;
        c - классы.
        Определяет последовательность обработки и документирования.

        depth -> int:
        -1 - документировать на всю глубину;
        0-... - документировать на заданную глубину.
        Определяет общую глубину документирования.

        depth_vars, depth_func - аналогично depth, для глубины документирования
        переменных и функций / методов.
        """
        self.classes = Classes()
        """Контейнер с классами из модуля data."""
        self.sequence = Sequence()
        """Последовательность элементов из модуля data."""
        self.elements = SubElements()
        """Контейнер с документацией (SubElements) из модуля data."""
        self.__prop = prop
        """Словарь с настройками, переданный в конструктор."""

    def _module_doc(self, module, name):
        """Документирование модуля.

        :param module: список строк
        :param name: имя модуля
        """
        doc_type = DocType.doc
        doc = utils.get_module_docs_or_comments(module,
                                                strip=self.__prop['strip'])
        if not doc:  # если нет документации - читем комменты
            doc = utils.get_module_docs_or_comments(module, True,
                                                    self.__prop['strip'])
            doc_type = DocType.com
        if doc:
            self.elements.add(None, name, ElementType.mo, doc=(doc_type, doc))
        self.sequence.add(name)

    def _is_private(self, name):
        """Проверить, является ли имя приватным и разрешено ли это.

        :param name: str, имя элемента
        :return: bool, True - нельзя документировать, False - можно
        """
        if ((name[:1] == '_' and name[:2] != '__') and not
            self.__prop['hide']) or ((name[:2] == '__' and name[-2:] != '__')
                                     and not self.__prop['private']) or\
            ((name[:2] == '__' and name[-2:] == '__')
             and not self.__prop['magic']):
            return True
        return False

    def _elements_or_func_doc(self, module, block, indent, is_cls, cls=None,
                              els=(), func=False):
        """Документирование переменных или функций в блоке кода.

        :param module: имя модуля
        :param block: список строк
        :param indent: int, отступ
        :param is_cls: является ли блок кода классом (для обработки __init__)
        :param cls: имя класса (при None - элемент модуля)
        :param els: tuple, иерархия имён суб-элементов,
        в порядке от верхнего до нижнего
        :param func: bool, True - документирование функций,
        False - документирование переменных
        :return: list, [(имя, индекс), ...]
        """
        if func:  # поиск функций
            elements = utils.get_functions(block, indent)
            if cls:
                el_type = ElementType.met
            else:
                el_type = ElementType.fun
        else:  # поиск переменных
            elements = utils.get_elements(block, indent)
            el_type = ElementType.var
        docs = utils.get_docs(block, elements, self.__prop['strip'])
        # для элементов без документации будут использоватся комменты
        com = utils.get_comments(block, elements)
        if not func and is_cls:  # проверка __init__ в классе
            index = utils.get_index(  # поиск __init__
                utils.get_functions(block, indent), '__init__')
            if index:  # исследование __init__
                init = utils.get_init_elements(utils.get_block(block, index))
                if init:  # обновление данных
                    elements = elements + init
                    docs = docs.update(utils.get_docs(block, init,
                                                      self.__prop['strip']))
                    com = com.update(utils.get_comments(block, init))
        for element in elements:  # документирование элементов
            name = element[0]
            if self._is_private(name):
                continue
            self.sequence.add(module, cls, els + (name,))
            doc = ()
            doc_type = None
            if docs and element[0] in docs:  # поиск документации
                doc = tuple(docs[element[0]])
                doc_type = DocType.doc
            elif com and element[0] in com:  # или комментов
                doc = tuple(com[element[0]])
                doc_type = DocType.com
            self.elements.add(element[0], module, el_type, cls, els,
                              doc=(doc_type, doc))
        return elements

    def _classes_doc(self, module, block, indent, els=(), sup_cls=None):
        """Документирование классов в блоке кода.

        :param module: имя модуля
        :param block: список строк
        :param indent: int, отступ
        :param els: tuple, иерархия имён суб-элементов,
        в порядке от верхнего до нижнего
        :param sup_cls: имя класса, в котором в иерархии элементов
        определён класс
        :return: list, [(имя(супер-классы), индекс), (имя, индекс), ...]
        """
        classes = utils.get_classes(block, indent)
        docs = utils.get_docs(block, classes, self.__prop['strip'])
        com = utils.get_comments(block, classes)
        for cls in classes:
            name = cls[0]
            if self._is_private(name):
                continue
            sup = []
            if '(' in name:
                sup_names = name[name.index('(')+1:name.index(')')]
                if ',' in sup_names:
                    for sn in sup_names.split(','):
                        sup.append(sn.strip())
                else:
                    sup.append(sup_names.strip())
            self.classes.add(name, module, tuple(sup))  # добавление
            hie = ()
            if els:
                hie = els + (name,)
            self.sequence.add(module, cls[0], hie)
            doc = ()
            doc_type = None
            if cls[0] in docs:  # поиск документации
                doc = tuple(docs[cls[0]])
                doc_type = DocType.doc
            elif cls[0] in com:  # или комментов
                doc = tuple(com[cls[0]])
                doc_type = DocType.com
            if els:  # сохранение в иерархии элементов
                self.elements.add(cls[0], module, ElementType.cl, None,
                                  els + (cls[0],), doc=(doc_type, doc))
            else:  # сохранние в модуле
                self.elements.add(cls[0], module, ElementType.cl, sup_cls, els,
                                  doc=(doc_type, doc))
        return classes

    def _doc_elements(self, lines, module, is_cls, cls, els, elements, indent,
                      first, var, func):
        """Анализ и документирование элементов из блока кода.

        :param lines: список строк
        :param module: имя модуля
        :param is_cls: является ли блок кода классом (для обработки __init__)
        :param cls: имя класса (при None - элементы модуля)
        :param els: tuple, иерархия имён суб-элементов,
        в порядке от верхнего до нижнего
        :param elements: list, [(имя, индекс), (имя(), индекс), ...]
        :param indent: int, отступ
        :param first: оцпия first
        :param var: bool, True - документировать переменные
        :param func: bool, True - документировать функции
        :return: dict, {имя: (переменные, функции, классы), ...},
        {
            имя: (
                [(имя, индекс), ...],
                [(имя, индекс), (имя(), индекс), ...],
                [(имя, индекс), (имя(), индекс), ...]
            )
        }
        """
        result = {}
        for element in elements:
            # предполагается, что сами элементы уже задокументированы
            block = utils.get_block(lines, element[1], indent)
            name = element[0]
            if self._is_private(name):
                continue
            hie = els + (name,)
            variables = []
            functions = []
            classes = []
            for f in first:  # исследование содержимого каждого элемента
                if var and f == 'v':  # переменные
                    variables = self._elements_or_func_doc(
                        module, block, indent, is_cls, cls, hie)
                elif func and f == 'f':  # функции
                    functions = self._elements_or_func_doc(
                        module, block, indent, False, cls, hie, True)
                elif f == 'c':  # классы
                    classes = self._classes_doc(
                        module, block, indent, hie, cls)
            if variables or functions or classes:  # сохранение результата
                result[name] = variables, functions, classes
        return result

    def analyse(self, module, name):
        """Анализ и полное документирование всех элементов модуля.

        :param module: список строк
        :param name: имя модуля
        """
        # получение настроек
        first = self.__prop['first']  # последовательность обработки
        depth = self.__prop['depth']  # общая глубина докуметирования
        d_var = self.__prop['depth_vars']  # для переменных
        d_func = self.__prop['depth_func']  # для функций

        def parse_dict(lines, elements, cls, indent, hie=(), step=0):
            """Глубинный разбор всех элементов.

            :param lines: список строк
            :param elements: dict, {имя: (переменные, функции, классы), ...},
            {
                имя: (
                    [(имя, индекс), ...],
                    [(имя, индекс), (имя(), индекс), ...],
                    [(имя, индекс), (имя(), индекс), ...]
                )
            }
            :param cls: имя класса (при None - элементы модуля)
            :param indent: отступ
            :param hie: tuple, иерархия имён суб-элементов,
            в порядке от верхнего до нижнего
            :param step: глубина рекурсии
            :return: dict,
            {
                имя: {
                    имя: (
                        [(имя, индекс), ...],
                        [(имя, индекс), (имя(), индекс), ...],
                        [(имя, индекс), (имя(), индекс), ...]
                    ), ...
                }, ...
            },
            глубина словаря может быть любой.
            """
            if depth != -1 and depth >= step:  # проверка общей глубины
                return elements
            result = elements  # первичный словарь
            dicts = {}  # то, что передаётся в рекурсию
            for e_name in elements:
                if self._is_private(e_name):
                    continue
                element = elements[e_name]  # элемент словаря
                if type(element) == dict:  # для последующего раскрытия
                    dicts[e_name] = element
                elif type(element) == tuple:  # раскрытие дальше вглубь
                    # element - (переменные, функции, классы)
                    this_hie = hie + (e_name,)
                    # проверка глубин для типов элементов
                    var = False
                    func = False
                    if d_var >= step or d_var == -1:  # переменные
                        var = True
                    if d_func >= step or d_func == -1:  # функции
                        func = True
                    val = {}  # раскрытые вглубь элементы
                    for ft in first:  # обработка в заданной последовательности
                        if ft == 'f':  # раскрытие функций
                            if not element[1]:
                                continue
                            func_val = self._doc_elements(lines, name, False,
                                                          cls, this_hie,
                                                          element[1],
                                                          indent, first, var,
                                                          func)
                            if val:
                                val.update(func_val)
                            else:
                                val = func_val
                        elif ft == 'c':  # раскрытие классов
                            if not element[2]:
                                continue
                            cls_val = self._doc_elements(lines, module, True,
                                                         cls, this_hie,
                                                         element[2], indent,
                                                         first, var, func)
                            if val:
                                val.update(cls_val)
                            else:
                                val = cls_val
                    if val:  # если было раскрыто - добавление для рекурсии
                        dicts[e_name] = val
            if dicts:  # нужно раскрыть словарь дальше
                for d in dicts:
                    # каждый tuple будет раскрыт, когда раскрывать будет
                    # нечего - вызовы последовательно вернут значения вверх
                    this_hie = hie + (d,)
                    val = parse_dict(lines, dicts[d], cls, indent*2,
                                     this_hie, step+1)
                    result[d] = val
                return result  # финальный выход
            else:
                return result  # выход на глубине

        self._module_doc(module, name)  # документирование модуля
        ind = utils.get_indent(module)  # получение отступа
        var_doc = False
        func_doc = False
        if d_var >= 1 or d_var == -1:  # документировать ли переменные модуля
            var_doc = True
        if d_func >= 1 or d_func == -1:  # документировать ли функции модуля
            func_doc = True
        for f in first:  # документирование в заданной последовательности
            if f == 'v':  # переменные
                self._elements_or_func_doc(name, module, 0, False)
            elif f == 'f':  # функции
                functions = self._elements_or_func_doc(
                    name, module, 0, False, func=True)
                # документирование содержимого функций
                de = self._doc_elements(module, name, False, None, (),
                                        functions, ind, first, var_doc,
                                        func_doc)
                parse_dict(module, de, None, ind)
            elif f == 'c':  # классы
                classes = self._classes_doc(name, module, 0)
                for c in classes:  # каждый класс отдельно, т.к. нужны имена
                    code = utils.get_block(module, c[1], ind)
                    for fe in first:  # опять последовательность
                        # документирование содержимого классов
                        if fe == 'v':  # переменные
                            self._elements_or_func_doc(name, code, ind, True,
                                                       c[0])
                        elif fe == 'f':  # методы
                            functions = self._elements_or_func_doc(name, code,
                                                                   ind, True,
                                                                   c[0],
                                                                   func=True)
                            de = self._doc_elements(code, name, True, c[0],
                                                    (), functions, ind, first,
                                                    var_doc, func_doc)
                            parse_dict(module, de, c[0], ind)
                        elif fe == 'c':  # классы
                            c_classes = self._classes_doc(name, code, ind,
                                                          (c[0],), c[0])
                            de = self._doc_elements(code, name, True, c[0],
                                                    (c[0],), c_classes, ind,
                                                    first, var_doc, func_doc)
                            parse_dict(module, de, c[0], ind, (c[0],), 1)

    def analyse_all(self, modules, names):
        """Анализ и полное документирование модулей.

        :param modules: list, список списков со списками строк модулей,
        [[], ...]
        :param names: list, имена модулей, должны совпадать по индексам с
        modules
        """
        i = 0
        for module in modules:
            self.analyse(module, names[i])
            i += 1

    def get_result(self):
        """Получить результаты.

        :return: tuple, (Sequence, SubElements, Classes)
        """
        return self.sequence, self.elements, self.classes
