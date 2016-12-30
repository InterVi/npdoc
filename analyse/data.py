"""Модуль с контейнерами данных."""
__all__ = ['Classes', 'Elements', 'SubElements', 'Sequence']


class Classes:
    """Контейнер с классами."""
    def __init__(self):
        self.cls = {}
        """Словарь с классами.

        Ключ - str, название класса
        Значение - tuple, ((супер-класс, модуль), ...), модуль)
        """
        self.names = {}
        """Словарь с именами классов.

        Ключ - имя модуля
        Значение - list, [класс, ...]
        """

    def add(self, name, module, sup_names=()):
        """Добавить класс в словари.

        :param name: имя класса
        :param module: имя модуля
        :param sup_names: tuple, наследуемые классы,
        ((класс, модуль), ...)
        """
        self.cls[name] = (sup_names, module)
        if module in self.names:
            self.names[module].append(name)
        else:
            self.names[module] = [name]

    def get_super_names(self, name, module=None):
        """Получить супер-классы.

        :param name: имя класса
        :param module: имя модуля (при None - поиск по всем модулям)
        :return: tuple, супер-классы - ((супер-класс, модуль), ...)
        """
        if module:
            result = []
            if name in self.cls:
                for cls in self.cls[name][0]:
                    if cls[0] in self.names[module]:
                        result.append(cls)
            return tuple(result)
        else:
            return self.cls[name][0]

    def get_sub_names(self, name, module=None):
        """Получить суб-классы.

        :param name: имя класса
        :param module: имя модуля (при None - поиск по всем модулям)
        :return: tuple, суб-классы - ((суб-класс, модуль), ...)
        """
        result = []
        for cls in self.cls:
            val = self.cls[cls]
            if val[0] and name in val[0][0]:
                if module:
                    if module == val[1]:
                        result.append(cls)
                else:
                    result.append(cls)
        result = tuple(result)
        return result

    def get_sub_or_sup_hie(self, name, sub=True, module=None):
        """Получить полную иерархию всех супер или суб классов.

        :param name: имя класса
        :param sub: bool, True - суб-классы, False - супер-классы
        :param module: имя модуля (при None - поиск по всем модулям)
        :return: dict,
        {класс: ({
            класс: ... / класс: ((имя, модуль), ...) / класс: None, ...
            }, модуль), ...},
        Пример:
        {Main: ({
            SubMain: ({SSMain: (One, Two), other), TwoSubMain: None}
            }, main), Enum: None}
        """
        def get_sub(tuple_arg):
            """Разворачивание иерархии.

            :param tuple_arg: tuple, имена классов
            :return: dict,
            {класс: (((класс, модуль), ...), модуль), ...}
            """
            result = {}
            for tup in tuple_arg:
                if sub:  # получение суб-классов
                    sts = self.get_sub_names(*tup)
                else:  # супер-классов
                    sts = self.get_super_names(*tup)
                if sts:  # раскрытый результат
                    result[tup[0]] = sts, tup[1]
                else:  # если наследников нет
                    result[tup[0]] = None
            return result

        def parse_dict(dict_arg):
            """Рекурсивное построение иерархии с помощью get_sub.

            :param dict_arg: dict,
            {класс: (((класс, модуль), ...), модуль), ...}
            :return: конечный результат (см. док. get_sub_or_sup_hie)
            """
            result = dict_arg  # присвоение для реализации рекурсии
            dicts = {}  # для рекурсии
            for d in dict_arg:  # цикл, вызываемый рекурсивно
                val = dict_arg[d]
                if type(val) == tuple:  # раскрытие tuple далее
                    nd = get_sub(val)  # получаем словарь
                    if nd:  # иерархия раскрыта на следуюший уровень
                        dicts[d] = nd  # сохраняем для рекурсии
                elif type(val) == dict:
                    # если уже раскрыто - опускаемся на уровень глубже
                    # вложенные словари будут разобраны
                    dicts[d] = val
            if dicts:
                for d in dicts:
                    # рекурсия метода для каждой итерации
                    # для глубокого раскрытия каждого словаря
                    val = parse_dict(dicts[d])
                    result[d] = val
                return result  # возвращаем раскрытиые словари
            else:  # выход на предельной глубине, когда разбирать нечего
                return result

        if sub:  # раскрытие иерархии суб-классов
            return parse_dict(self.get_sub_names(name, module))
        else:  # супер-классов
            return parse_dict(self.get_super_names(name))


class Elements:
    """Контейнер с элементами."""
    def __init__(self):
        self.els = {}
        """Словарь с элементами. Каждый элемент - tuple, (ElementType, tuple):
        (тип, документация) - (ElementType, (DocType, ())).

        Ключи: модуль => класс => суб-элемент.

        Перменные класса:
        модуль: {класс: {имя: (ElementType, (DocType, ()))}}.

        Локальные переменные методов класса:
        модуль: {
            класс: {
                None: {
                    суб-элемент: {имя: {None: (ElementType, (DocType, ()))}}
                }
            }
        }.

        Глобальные переменные:
        модуль: {
            None: {
                None: {
                    имя: (ElementType, (DocType, ()))
                }
            }
        }.

        Локальные переменные функций модуля:
        модуль: {
            None: {
                суб-элемент: {имя: {None: (ElementType, (DocType, ()))}}
            }
        }.

        Чтобы добавить документацию по модулю, достаточно использовать
        None в качестве имени.
        """

    def add(
            self, name, module, el_type,
            cls=None, sub_el=None, doc=(None, ())
    ):
        """Добавить элемент в словарь.

        :param name: имя элемента
        :param module: имя модуля
        :param el_type: ElementType тип элемента
        :param cls: имя класса (None если элемент модуля)
        :param sub_el: имя суб-элемента (None если его нет)
        :param doc: tuple, (DocType тип, (строки...)), документация
        """
        if module in self.els:  # пополнение модуля
            mod = self.els[module]
            if cls:  # элемент класса
                if cls in mod:  # пополнение класса
                    if sub_el:  # элемент элемента класса
                        se = mod[cls]
                        if None in se:  # пополнение суб-элемента
                            se[None][sub_el][name] = {None: (el_type, doc)}
                        else:  # добавление суб-элемента
                            se[None] = {
                                sub_el: {name: {None: (el_type, doc)}}
                            }
                    else:  # элемент класса
                        mod[cls][name] = (el_type, doc)
                else:  # добавление класса
                    if sub_el:  # добавление суб-элемента
                        mod[cls] = {sub_el: {name: {None: (el_type, doc)}}}
                    else:  # добавление элемента
                        mod[cls] = {name: (el_type, doc)}
            else:  # элемент модуля
                if sub_el:  # элемент элемента модуля
                    if None in mod:  # пополнение элементов модуля
                        se = mod[None]
                        if sub_el in se:  # пополнение элемента
                            se[sub_el][name] = {None: (el_type, doc)}
                        else:  # добавление элемента
                            se[sub_el] = {name: {None: (el_type, doc)}}
                    else:  # добавление элемента модуля
                        mod[None] = {sub_el: {name: {None: (el_type, doc)}}}
                else:  # элемент модуля
                    if None in mod:  # пополнение элементов модуля
                        se = mod[None]
                        if None in se:  # пополнение элементов
                            se[None][name] = (el_type, doc)
                        else:  # добавление элемента
                            se[None] = {name: (el_type, doc)}
                    else:  # добавление элемента модуля
                        mod[None] = {None: {name: (el_type, doc)}}
        else:  # добавление модуля
            if cls:  # пополнение класса
                if sub_el:  # пополение элементов элемента класса
                    self.els[module] = {
                        cls: {None: {sub_el: {name: {None: (el_type, doc)}}}}
                    }
                else:  # пополнение элементов
                    self.els[module] = {cls: {name: (el_type, doc)}}
            else:  # пополнение модуля
                if sub_el:  # пополнение элементов элемента модуля
                    self.els[module] = {
                        None: {None: {sub_el: {name: {None: (el_type, doc)}}}}
                    }
                else:  # пополнение элементов модуля
                    self.els[module] = {
                        None: {None: {None: {name: (el_type, doc)}}}
                    }

    def get_module(self, module):
        """Получить документацию по модулю.

        :param module: имя модуля
        :return: tuple, (ElementType, (DocType, ()))
        """
        if module in self.els:
            mod = self.els[module]
            if None in mod and None in mod[None] and None in mod[None][None]\
                    and None in mod[None][None][None]:
                return mod[None][None][None][None]
        return ()

    def get_global(self, module):
        """Получить глобальные элементы модуля.

        :param module: имя модуля
        :return: dict, {имя: (ElementType, (DocType, ()))}
        """
        if module in self.els:
            mod = self.els[module]
            if None in mod and None in mod[None]:
                return mod[None][None]
        return {}

    def get_global_local(self, module, el):
        """Получить локальные перменные элемента модуля.

        :param module: имя модуля
        :param el: имя элемента
        :return: dict, {имя: (ElementType, (DocType, ()))}
        """
        if module in self.els:
            mod = self.els[module]
            if None in mod and el in mod[None]:
                return mod[None][el]
        return {}

    def get_self(self, module, cls):
        """Получить элементы класса.

        :param module: имя модуля
        :param cls: имя класса
        :return: dict, {имя: (ElementType, (DocType, ()))}
        """
        if module in self.els:
            mod = self.els[module]
            if cls in mod:
                return mod[cls]
        return {}

    def get_self_local(self, module, cls, el):
        """Получить элементы элемента класса.

        :param module: имя модуля
        :param cls: имя класса
        :param el: имя элемента
        :return: dict, {имя: (ElementType, (DocType, ()))}
        """
        if module in self.els:
            mod = self.els[module]
            if cls in mod and None in mod[cls] and el in mod[cls][None]:
                return mod[cls][None][el]
        return {}


class SubElements(Elements):
    """Расширенный контейнер с элементами, полная глубина данных.

    Словарь els заполняется полными данными о локальных элементах.

    Локальные переменные методов класса:
    модуль: {
        класс: {
            None: {
                суб-элемент: {
                    имя: {
                        None: (ElementType, (DocType, ()))
                        суб-элемент1: {
                            имя: {
                                None: (ElementType, (DocType, ()))
                                cуб-элемент2: {
                                    имя: {None: (ElementType, (DocType, ()))}
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    Вложенная глубина может быть любой, по аналогии.

    Локальные переменные функций модуля:
    модуль: {
        None: {
            суб-элемент: {
                имя: {
                    None: (ElementType, (DocType, ()))
                    суб-элемент1: ...
                }
            }
        }
    }
    """
    def add(
            self, name, module, el_type,
            cls=None, sub_el=(), doc=(None, ())
    ):
        """Добавить элемент в словарь.

        :param name: имя элемента
        :param module: имя модуля
        :param el_type: ElementType тип элемента
        :param cls: имя класса (None если элемент модуля)
        :param sub_el: tuple, иерархия имён суб-элементов,
        в порядке от верхнего до нижнего
        :param doc: tuple, (DocType тип, (строки...)), документация
        """
        def add(pos, se_dict):
            """Добавить элемент в самый низ иерархии, разобрав словарь els.

            :param pos: позиция старта в sub_el
            :param se_dict: словарь (ссылающийся на self.els)
            """
            def add_in(pos_, se_dict_):
                if pos_ >= len(sub_el):
                    return
                se_dict_[sub_el[pos_]] = {}
                pos_ += 1
                if pos_ >= len(sub_el):
                    se_dict_[sub_el[pos_-1]] = {name: {None: (el_type, doc)}}
                else:
                    add_in(pos_, se_dict_[sub_el[pos_-1]])

            while pos < len(sub_el):
                if sub_el[pos] not in se_dict:
                    add_in(pos, se_dict)
                pos += 1

        def get_pos(se_dict):
            """Получить последнюю позицию в словаре,
            до которой ведёт иерархия sub_el.

            :param se_dict: словарь (ссылающийся на self.els)
            :return: tuple, индекс последней позиции и разложенный словарь
            """
            pos = 0
            for s in sub_el:
                if s in se_dict:
                    se_dict = se_dict[s]
                else:
                    break
                pos += 1
            return pos, se_dict

        if not sub_el:
            Elements.add(self, name, module, el_type, cls, None, doc)
        elif len(sub_el) == 1:
            Elements.add(self, name, module, el_type, cls, sub_el[0], doc)
        else:
            if module in self.els:
                mod = self.els[module]
                if cls:
                    if cls in mod:
                        se = mod[cls]
                        if None in se:
                            add(*get_pos(se))
                        else:
                            mod[cls] = {None: {}}
                            add(0, mod[cls][None])
                    else:
                        mod[cls] = {None: {}}
                        add(0, mod[cls][None])
                else:
                    if None in mod:
                        se = mod[None]
                        add(*get_pos(se))
                    else:
                        mod[None] = {}
                        add(0, mod[None])
            else:
                self.els[module] = {}
                mod = self.els[module]
                if cls:
                    mod[cls] = {}
                    add(0, mod[cls])
                else:
                    mod[None] = {}
                    add(0, mod[None])

    def __get_local(self, module, cls=None, el=()):
        """Получить словарь суб-элементов элемента.

        :param module: имя модуля
        :param cls: имя класса (None если элемент модуля)
        :param el: tuple, иерархия имён суб-элементов,
        в порядке от верхнего до нижнего (нужного)
        :return: dict, {имя: {None: (ElementType, (DocType, ())), ...}}
        """
        if module in self.els:
            mod = self.els[module]
            if cls and cls in mod:
                mod = mod[cls]
            i = 0
            while i < len(el):
                if el[i] in mod:
                    mod = mod[el[i]]
                    i += 1
                else:
                    break
            if i == len(el):
                return mod
            return {}

    def get_global_local(self, module, el=()):
        """Получить локальные перменные элемента модуля.

        :param module: имя модуля
        :param el: tuple / str, иерархия имён суб-элементов,
        в порядке от верхнего до нижнего (нужного)
        :return: dict, {имя: {None: (ElementType, (DocType, ())), ...}}
        """
        if type(el) == str or len(el) == 1:
            return Elements.get_global_local(self, module, el[0])
        else:
            return self.__get_local(module, el=el)

    def get_self_local(self, module, cls, el=()):
        """Получить элементы элемента класса.

        :param module: имя модуля
        :param cls: имя класса (None если элемент модуля)
        :param el: tuple / str, иерархия имён суб-элементов,
        в порядке от верхнего до нижнего (нужного)
        :return: dict, {имя: {None: (ElementType, (DocType, ())), ...}}
        """
        if type(el) == str or len(el) == 1:
            return Elements.get_global_local(self, module, el[0])
        else:
            return self.__get_local(module, cls, el)


class Sequence:
    """Контейнер с последовательностью элементов."""
    def __init__(self):
        self.mods = {}
        """Словарь с последовательностями модулей, классов и элементов.

        {
            None: [модуль1, модуль2, модуль3, ...]
            модуль: {
                None: {
                    None: [
                        [класс1, класс2, класс3, ...],
                        [элемент1, элемент2, элемент3, ...]
                    ]
                    элемент: {
                        None: [суб-элемент1, суб-элемент2, суб-элемент3, ...]
                        суб-элемент: ...
                    }
                }
                класс: {
                    None: [
                        элемент1, элемент2, элемент3, ...
                        None: [
                            [], [имя_элемента1, имя_элемента2, ...]
                        ]
                    ]
                    элемент: {
                        None: [суб-элемент1, суб-элемент2, суб-элемент3, ...]
                        суб-элемент: ...
                    }
                }
            }
        }
        """

    def add(self, module, cls=None, el=()):
        """Добавить элемент в словарь.

        :param module: имя модуля
        :param cls: имя класса (None если элемент модуля)
        :param el: tuple, иерархия имён элементов,
        в порядке от верхнего до нижнего
        """
        def add(se_dict, one=True):
            """Добавить информацию в самый низ иерархии.

            :param se_dict: словарь (ссылающийся на self.mods)
            :param one: bool, true - обновлять первый список под None[0],
            false - обновлять под None[1]
            """
            for e in el:
                if one:  # добавить имя в список классов
                    if None in se_dict:
                        if e not in se_dict[None][0]:
                            se_dict[None][0].append(e)
                    else:
                        se_dict[None] = [[e], []]
                else:
                    # в список элементов, все последующие - в список классов
                    if None in se_dict:
                        if e not in se_dict[None][1]:
                            se_dict[None][1].append(e)
                    else:
                        se_dict[None] = [[], [e]]
                    one = True
                if e in se_dict:  # раскрытие словаря в глубину
                    se_dict = se_dict[e]
                else:
                    # добавление словаря в глубь иерархии
                    # для последующего заполнения
                    se_dict[e] = {}
                    se_dict = se_dict[e]

        if module in self.mods:  # дополнение модуля
            mod = self.mods[module]
            if cls:  # элемент класса
                if None in mod:  # добавление имени в список элементов класса
                    se = mod[None]
                    if None in se:
                        if cls not in se[None][0]:
                            se[None][0].append(cls)
                    else:
                        se[None] = [[cls], []]
                else:
                    mod[None] = {None: [cls]}
                if el:  # добавление элемента в класс
                    if cls in mod:  # обновление информации
                        add(mod[cls])  # add делает всё за нас :)
                    else:  # создание словаря с элементами класса
                        mod[cls] = {}
                        add(mod[cls])
            else:  # элемент модуля
                if None in mod:
                    add(mod[None], False)
                else:
                    mod[None] = {}
                    add(mod[None], False)
        else:  # добавление модуля
            if None in self.mods:  # добавление в список модулей
                self.mods[None].append(module)
            else:
                self.mods[None] = [module]
            self.mods[module] = {}  # создание словаря с элементами модуля
            mod = self.mods[module]
            if cls:  # элемент класса
                mod[cls] = {}
                add(mod[cls])
            else:  # элемент модуля
                mod[None] = {}
                add(mod[None], False)

    def get_modules(self):
        """Получить последовательность модулей.

        :return: list
        """
        if None in self.mods:
            return self.mods[None]
        return []

    def get_classes(self, module):
        """Получить последовательность классов.

        :param module: имя модуля
        :return: list
        """
        if module in self.mods:
            mod = self.mods[module]
            if None in mod and None in mod[None]:
                return mod[None][None][0]
        return []

    def get_global_elements(self, module):
        """Получить последовательность элементов модуля.

        :param module: имя модуля
        :return: list
        """
        if module in self.mods:
            mod = self.mods[module]
            if None in mod and None in mod[None]:
                return mod[None][None][1]
        return []

    @staticmethod
    def __get_local(se_dict, el=()):
        """Получить последовательность элемента внутри иерархии.

        :param se_dict: словарь (ссылающийся на self.mods)
        :param el: tuple, иерархия имён элементов,
        в порядке от верхнего до нижнего
        :return: list
        """
        for e in el:
            if e in se_dict:
                se_dict = se_dict[e]
            else:  # искомого элемента в иерархии нет
                return []
        if None in se_dict:
            return se_dict[None][1]
        return []

    def get_global_local_elements(self, module, el=()):
        """Получить последовательность элементов
        внутри иерархии элемента модуля.

        :param module: имя модуля
        :param el: tuple, иерархия имён элементов,
        в порядке от верхнего до нижнего
        :return: list
        """
        if module in self.mods:
            mod = self.mods[module]
            if None in mod:
                return self.__get_local(mod[None], el)
        return []

    def get_self_elements(self, module, cls):
        """Получить последовательность элементов класса.

        :param module: имя модуля
        :param cls: имя класса
        :return: list
        """
        if module in self.mods:
            mod = self.mods[module]
            if cls in mod:
                se = mod[cls]
                if None in se:
                    return se[None][1]
        return []

    def get_self_local_elements(self, module, cls, el=()):
        """Получить последовательность элементов
        внутри иерархии элемента класса.

        :param module: имя модуля
        :param cls: имя класса
        :param el: tuple, иерархия имён элементов,
        в порядке от верхнего до нижнего
        :return: list
        """
        if module in self.mods:
            mod = self.mods[module]
            if cls in mod:
                return self.__get_local(mod[None], el)
        return []
