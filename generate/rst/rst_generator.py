"""Генератор документации в формате rst."""
from analyse.enums import *

__all__ = ['RSTGenerator']


class RSTGenerator:
    """Генератор документации по пакету."""
    def __init__(self, sequence, elements, classes, prop, lang):
        """

        :param sequence: Sequence из analyse.data
        :param elements: SubElements из analyse.data
        :param classes: Classes из analyse.data
        :param prop: Словарь с настройками.

        first -> vfc:
        v - переменные;
        f - функции / методы;
        c - классы.
        Определяет последовательность обработки и документирования.

        depth - глубина документирования (int);
        numbered - нумерация всех пунктов оглавления (bool);
        hidden - скрыть оглавление (bool).

        nohie - не выводить иерархию классов;
        notype - не выводить тип информации (документация или комментарий).
        :param lang: Языковой словарь.

        doc - документация;
        com - комментарий;
        sup - супер-классы;
        sub - суб-классы
        """
        self.sequence = sequence
        self.elements = elements
        self.classes = classes
        self.__prop = prop
        """Словарь с настройками, переданный в конструктор."""
        self.__lang = lang
        """Языковой словарь, переданный в конструктор."""
        self.__init = []
        """Описание пакета из модуля __init__."""

    def _gen_tree(self, content):
        """Генерация index.rst

        :param content: list
        :return: list
        """
        result = [
            '.. toctree::',
            '   :maxdepth: ' + str(self.__prop['depth']),
        ]
        if self.__prop['numbered']:
            result.append('   :numbered: ')
        if self.__prop['hidden']:
            result.append('   :hidden: ')
        result.append('')
        for c in content:
            result.append('   ' + c)
        result.append('')
        return result

    def gen_index(self, module=None, names=None):
        """Генерация index.rst, с добавлением имён модулей или классов.

        :param module: имя модуля (при None используются имена модулей)
        :param names: tuple или list с именами файлов rst без расширений,
        которые будут использоваться вместо имён модулей или классов
        :return: list
        """
        result = []
        if self.__init:
            result += self.__init
            result.append('')
        if names:
            result += self._gen_tree(names)
        elif module:
            result += self._gen_tree(self.sequence.get_classes(module))
        else:
            result += self._gen_tree(self.sequence.get_modules())
        return result

    def _gen_element(self, e_name, element, type_):
        """генерация документации по элементу.

        :param e_name: имя элемента
        :param element: tuple, (ElementType, (DocType, ()))
        :param type_: ElementType тип (при несовпадении вернёт None)
        :return: list
        """
        if element[0] != type_:  # если элемент не заданного типа
            return None
        result = [e_name, '+' * len(e_name), '']
        if element[1][1]:  # если содержимое не пустое (иначе метки не нужны)
            if not self.__prop['notype']:
                if element[1][0] == DocType.doc:  # документация
                    result += ['*' + self.__lang['RST_GENERATOR']['doc'] + '*',
                               '']
                else:  # комментарий
                    result += ['*' + self.__lang['RST_GENERATOR']['com'] + '*',
                               '']
            for doc_str in element[1][1]:
                result.append(doc_str)
            result.append('')
        return result

    def _gen_func(self, module, cls, name, els=(), doc=None):
        """Генерация документации по функции или методу.

        :param module: имя модуля
        :param cls: имя класса
        :param name: имя функции
        :param els: tuple, иерархия имён суб-элементов,
        в порядке от верхнего до нижнего
        :param doc: описание функции
        :return: list
        """
        gels = els + (name,)  # для вызова функций
        if els:  # составление иерархии в заголовке
            hie = ''
            for e in els:
                hie += e + ' -> '
            hie += '**' + name + '**'
            result = [hie, '']
        else:  # простой заголовок
            result = [name, '+' * len(name), '']
        if cls:  # если это метод класса
            if els:  # если это локальная функция
                content = self.elements.get_self_local(module, cls, gels)
                sequence =\
                    self.sequence.get_self_local_elements(module, cls, gels)
            else:
                content = self.elements.get_self(module, cls)
                sequence = self.sequence.get_self_elements(module, cls)
        else:  # если это функция модуля
            content = self.elements.get_global_local(module, gels)
            sequence = self.sequence.get_global_local_elements(module, gels)
        if doc:  # вставка описания функции
            result += doc
            result.append('')
        for e_name in sequence:  # обработка последовательности
            if e_name in content:  # если есть документация
                element = content[e_name]
                if element[0] == ElementType.var:  # переменные
                    gv = self._gen_element(e_name, element[1], ElementType.var)
                    if gv:
                        result += gv
                elif element[0] == ElementType.fun:  # функции
                    doc_func = self._gen_element(e_name, element,
                                                 ElementType.fun)
                    if doc_func:
                        doc_func = doc_func[3:]
                        f_els = els + (name,)
                        result += self._gen_func(module, cls, e_name, f_els,
                                                 doc_func)
                elif element[0] == ElementType.cl:  # классы
                    doc_cls = self._gen_element(e_name, element,
                                                ElementType.cl)
                    if doc_cls:
                        doc_cls = doc_cls[3:]
                        result += self._gen_class(module, e_name, els, doc_cls)
            # рекурсивное документирование функций
            # r_els = els + (name,)
            # result += self._gen_func(module, cls, e_name, r_els)
        return result

    def _gen_class(self, module, name, els=(), doc=None):
        """Генерация документации по классу.

        :param module: имя модуля
        :param name: имя класса
        :param els: tuple, иерархия имён суб-элементов,
        в порядке от верхнего до нижнего
        :param doc: описание класса
        :return: list
        """
        if els:  # если это вложенный класс
            # последовательность в заголовок
            hie = ''
            for e in els:
                hie += e + ' -> '
            hie += '**' + name + '**'
            result = [hie, '']
            content = self.elements.get_self_local(module, name, els)
            sequence = self.sequence.get_self_local_elements(module, name, els)
        else:  # если это нормальный класс
            result = [name, '-' * len(name), '']
            if not self.__prop['nohie']:
                sub = self.classes.get_sub_names(name)
                sup = self.classes.get_super_names(name)
                # перечисление супер и суб классов
                sb = ''  # строка с суб-классами
                for s in sub:
                    sb += s[0] + ', '
                sb = sb[:-2]
                sp = ''  # строка с супер-классами
                for s in sup:
                    sp += s[0] + ', '
                sp = sp[:-2]
                if sup:  # если есть супер-классы
                    result +=\
                        ['**' + self.__lang['RST_GENERATOR']['sup'] + '**:',
                         '', sp, '']
                if sub:  # если есть суб-классы
                    result +=\
                        ['**' + self.__lang['RST_GENERATOR']['sub'] + '**:',
                         '', sb, '']
            content = self.elements.get_self(module, name)
            sequence = self.sequence.get_self_elements(module, name)
        if doc:  # вставка описания класса
            result += doc
            result.append('')
        var = []
        classes = []
        func = []
        for e_name in sequence:  # заполнение списков по типам
            if e_name in content:
                element = content[e_name]
                if element[0] == ElementType.var:
                    var.append((e_name, element))
                elif element[0] == ElementType.cl:
                    classes.append((e_name, element))
                elif element[0] == ElementType.met:
                    func.append((e_name, element))
        for first in self.__prop['first']:  # обработка последовательности
            if first == 'v':  # переменные
                for v in var:
                    doc_vars = self._gen_element(v[0], v[1], ElementType.var)
                    if doc_vars:
                        result += doc_vars
            elif first == 'f':  # функции
                for f in func:
                    if els:
                        func_type = ElementType.fun
                    else:
                        func_type = ElementType.met
                    doc_func = self._gen_element(f[0], f[1], func_type)[3:]
                    if doc_func:
                        result +=\
                            self._gen_func(module, name, f[0], els, doc_func)
            elif first == 'c':  # классы
                for c in classes:  # рекурсивное документирование подклассов
                    doc_cls = self._gen_element(c[0], c[1], ElementType.cl)[3:]
                    if doc_cls:
                        result += self._gen_class(module, c[0], tuple(name),
                                                  doc_cls)
        return result

    def _gen_module(self, module):
        """Генерация документации по модулю.

        :param module: имя модуля
        :return: list
        """
        result = [module, '=' * len(module), '']
        elements = self.elements.get_global(module)
        sequence = self.sequence.get_global_elements(module)
        cls_sequence = self.sequence.get_classes(module)
        mod = self.elements.get_module(module)
        if mod:  # генерация документации по модулю
            m_doc = self._gen_element(module, mod, ElementType.mo)
            result += m_doc
            result.append('')
            if module == '__init__':  # сохранение описания пакета
                self.__init = m_doc
        for first in self.__prop['first']:  # обработка последовательности
            e_type = None  # определение текущего типа
            if first == 'v':
                e_type = ElementType.var
            elif first == 'f':
                e_type = ElementType.fun
            elif first == 'c':
                e_type = ElementType.cl
            # генерация
            if e_type == ElementType.cl:  # отдельная обработка классов
                for name in cls_sequence:
                    if name in elements:
                        element = elements[name]
                        doc_cls = \
                            self._gen_element(name, element, ElementType.cl)
                        if doc_cls:
                            doc_cls = doc_cls[3:]
                            result +=\
                                self._gen_class(module, name, doc=doc_cls)
                        else:
                            result += self._gen_class(module, name)
                continue
            for name in sequence:  # обработка остальных типов
                if name in elements:
                    element = elements[name]
                    if e_type == ElementType.var:  # переменные
                        doc_vars = self._gen_element(name, element, e_type)
                        if doc_vars:
                            result += doc_vars
                    if e_type == ElementType.fun:  # функции
                        doc_func =\
                            self._gen_element(name, element, ElementType.fun)
                        if doc_func:
                            doc_func = doc_func[3:]
                            result += self._gen_func(module, None, name,
                                                     doc=doc_func)
        return result

    def gen_project(self):
        """Генерация документации по пакету.

        :return: tuple, (list, dict, list),
        (список модулей, словарь с документацией модулей, документация пакета).

        Ключи для словаря - имена модулей, содержимое - list.
        """
        modules = self.sequence.get_modules()  # последовательность модулей
        mods = {}  # словарь с документацией по ним
        for module in modules:
            mods[module] = self._gen_module(module)
        index = self.gen_index()
        return modules, mods, index
