"""Утилиты для поиска различных элементов в модуле или классе."""
import re

__all__ = [
    'IsDoc', 'get_first_spaces', 'get_classes', 'get_init_elements',
    'get_elements', 'get_functions', 'get_docs', 'get_comments',
    'get_module_docs_or_comments', 'get_block', 'get_indent', 'get_index'
]


class IsDoc:
    """Определение секций с документацией."""
    def __init__(self):
        self.doc = False
        """bool, открыты ли кавычки документации."""

    def is_doc(self, line):
        """Является ли строка документацией.

        :param line: строка
        :return: bool, True если истина
        """
        count = 0
        if line.strip()[:3] == '"""':
            count += 1
        if line.strip()[-3:] == '"""':
            count += 1
        if count == 1:  # одни кавычки - значит документация многострочна
            self.doc = not self.doc
            return True
        elif count == 2:  # документация однострочная
            self.doc = False
            return True
        return self.doc


def get_first_spaces(line):
    """Получить кол-во пробелов и табов в начале строки.

    :param line: строка
    :return: int
    """
    result = 0
    for ch in line:
        if ch != ' ' and ch != '	':
            break
        result += 1
    return result


def __for(func, lines, indent=-1):
    """Цикличная обработка списка строк для большинства алгоритмов.

    :param func: функция, в кторую передаётся строка, возвращает строку
    или None
    :param lines: список строк
    :param indent: отступ в начале строки (при -1 не анализируется),
    чтобы обрабатывать только нужные блоки
    :return: list, [(имя, индекс), ...]
    """
    result = []
    elements = []
    i = 0
    doc = IsDoc()
    for line in lines:
        i += 1
        if (not line or line.isspace()) or doc.is_doc(line) or (
                    line.strip()[0] == '#'):
            # пропуск не нужного
            continue
        if indent > -1:  # обработка только заданного блока
            fs = get_first_spaces(line)
            if fs < indent:
                break
            elif fs != indent:  # пропуск вложенных блоков
                continue
        element = func(line)
        if element and element not in elements:
            # вернулось значение - добавляем в список
            result.append((element, i-1))
            elements.append(element)
    return result


def get_classes(lines, start=0):
    """Получить классы.

    :param lines: список строк
    :param start: отступ в начале строки (при -1 не анализируется),
    чтобы обрабатывать только нужные блоки
    :return: list, [(имя(супер-классы), индекс), (имя, индекс), ...]
    """
    def func(line):  # поиск в строке определения класса
        line = line.strip()
        if line[:6] == 'class ' and ':' in line:
            return line[6:line.index(':')].strip()

    return __for(func, lines, start)


def __clean(line, ch):
    """Нахождение символа вне кавычек.

    :param line: строка
    :param ch: символ
    :return: часть строки, которая начинается с искомого символа вне кавычек
    """
    def get_ch():
        """Получить символ первой кавычки в строке.

        :return: ' или "
        """
        a = line.find('"')
        b = line.find('\'')
        if a == -1:
            c = '\''
        elif b == -1:
            c = '"'
        else:
            if a < b:
                c = '"'
            else:
                c = '\''
        return c

    q = line.find(get_ch())
    i = 0  # кол-во найденных кавычек
    while q != -1:
        i += 1
        line = line[q + 1:]  # отрезание кавычки
        q = line.find(get_ch())
    sh = line.find(ch)
    if sh != -1 and sh > q:
        # регирование на символ вне кавычек
        # поэтому целый алгоритм пришлось писать :(
        line = line[sh:]
    return line


def __trim_if(line):
    """Обрезка условий.

    :param line: строка
    :return: часть после двоеточия, очищенная от комментария (если есть)
    """
    # line = line.strip()
    if line[:3] == 'if ' or line[:5] == 'elif ':  # если PEP8 не соблюдается
        if '"' in line or '\'' in line:  # обрезка условий
            if ':' in line:
                line = __clean(line, ':')[1:].strip()
        else:
            if ':' in line:
                line = line[line.index(':') + 1:].strip()
        if '#' in line:  # обрезка коммента
            line = line[:line.index('#')].strip()
    return line


def get_init_elements(init):
    """Получить элементы класса, определённые в __init__.

    :param init: список строк (весь метод __init__)
    :return: list, [(имя, индекс), ...]
    """
    def func(line):  # поиск присвоения в строке
        line = line.strip()
        if line[:3] == 'if ' or line[:5] == 'elif ':
            # если PEP8 не соблюдается
            line = __trim_if(line)
        if line[:5] == 'self.' and '=' in line:
            first = line[5:line.index('=')].strip()
            if re.match('^[a-zAа-яЯ0-9-_]*$', first):
                return first

    return __for(func, init)


def get_elements(lines, indent=0):
    """Получить список элементов.

    :param lines: список строк
    :param indent: отступ в начале строки (при -1 не анализируется),
    чтобы обрабатывать только нужные блоки
    :return: list, [(имя, индекс), ...]
    """
    def func(line):
        line = line.strip()
        if line[:3] == 'if ' or line[:5] == 'elif ':  # обрезка условий
            line = __trim_if(line)
        elif line[:4] == 'def ' or line[:6] == 'while ':
            return
        if '=' in line:  # поиск присвоения в строке
            first = line.split('=')[0].strip()
            if re.match('^[a-zAа-яЯ0-9-_]*$', first):
                return first
    return __for(func, lines, indent)


def get_functions(lines, start=0):
    """Получить список функций.

    :param lines: список строк
    :param start: отступ в начале строки (при -1 не анализируется),
    чтобы обрабатывать только нужные блоки
    :return: list, [(имя(параметры), индекс), ...]
    """
    def func(line):  # поиск в строке определения функции
        line = line.strip()
        if line[:4] == 'def ' and ':' in line:
            return line[4:line.index(':')].strip()

    return __for(func, lines, start)


def get_docs(lines, elements, strip=False):
    """Получить документацию по элементам.

    :param lines: список строк
    :param elements: tuple / list, элементы, (имя, индекс)
    :param strip: bool, True - обрезать отступы
    :return: dict, {имя: [документация...], ...}
    """
    result = {}
    for el in elements:
        i = el[1]+1
        indent = -1
        doc = IsDoc()
        add = []
        while i < len(lines):
            no_strip = lines[i]  # для получения отступа
            line = no_strip.strip()  # для остальных алгоритмов
            spaces = ''
            if indent != -1:  # если первый отступ уже известен
                spaces = ' ' * (get_first_spaces(no_strip) - indent)
            if (not doc.doc and not line) or (line and line[0] == '#'):
                # пропуск комментов и пустых строк ДО
                i += 1
                continue
            if doc.is_doc(line):
                if indent == -1:  # получение первого отступа в документации
                    indent = get_first_spaces(no_strip)
                    spaces = ' ' * (get_first_spaces(no_strip) - indent)
                if not doc.doc:  # это однострочная документация
                    if line == '"""':  # строка состоит из закрывающих кавычек
                        break
                    line = line[line.index('"""')+3:]
                    line = line[:line.index('"""')]
                    add.append(line)
                    break
                # обработка контента многострочной документации
                if i == el[1]+1:  # чистка первой строки от кавычек
                    line = line[line.index('"""')+3:]
                    if not line:
                        continue
                if not strip:
                    line = spaces + line
                add.append(line)
            elif not line:  # сохранение пустых строк внутри документации
                if not strip:
                    line = spaces + line
                add.append(line)
            else:
                break
            i += 1
        if add:
            if len(add) > 1:  # чистка последнего элемента от кавычек
                last = len(add)-1
                end = add[last].find('"""')
                if end != -1:
                    add[last] = add[last][:end]
                if not add[last]:
                    del add[last]
            result[el[0]] = add  # сохранение результата
    return result


def get_comments(lines, elements):
    """Получить комментарии к элементу. Читает комментарии до, на строке
    и после. Если есть комментарий на строке, то только он + после.

    :param lines: список строк
    :param elements: список tuple, [(имя, индекс), ...]
    :return: dict, {имя: [комментарии], ...}
    """
    def get(pos, rev=False):
        """Получить комментарии до или после.

        :param pos: позиция старта
        :param rev: bool, при True читает вверх списка
        :return: list, комментарии
        """
        doc = IsDoc()
        com = []
        while (rev and pos >= 0) or (not rev and pos < len(lines)):
            line = lines[pos].strip()
            if not line or doc.is_doc(line):
                # пропуск не нужного
                if rev:
                    pos -= 1
                else:
                    pos += 1
                continue
            if line[0] == '#':  # строка - комментарий
                com.append(line[1:].strip())
            else:  # нет - прерывание цикла
                break
            if rev:
                pos -= 1
            else:
                pos += 1
        return com

    def get_one(line):
        """Получить однострочный комментарий на одной строке с элементом.

        :param line: строка
        :return: комментарий или None, если его нет
        """
        if '"' in line or '\'' in line:  # обрезание кавычек
            line = __clean(line, '#')
        else:  # если кавычек нет, просто поиск решётки
            if '#' in line:
                line = line[line.find('#'):]
        if line[0] == '#':  # коммент найден
            return line[1:].strip()

    result = {}
    for el in elements:
        add = []
        comment = get_one(lines[el[1]])  # однострочный коммент
        if comment:
            add.append(comment)
        comments = get(el[1]+1)  # многострочный коммент ПОСЛЕ
        if comments:
            add += comments
        elif not comment:  # если ПОСЛЕ и однострочного нет
            comments = get(el[1]-1, True)  # многострочный коммент ДО
            if comments:
                add += comments
        if add:
            result[el[0]] = add
    return result


def get_module_docs_or_comments(lines, com=False, strip=False):
    """Получить документацию или комментарии модуля.

    :param lines: список строк
    :param com: bool, True - получить комментарии, False - документацию
    :param strip: bool, True - обрезать отступы
    :return: list
    """
    result = []
    doc = IsDoc()
    indent = -1
    for line in lines:
        no_strip = line  # для получения отступа
        line = line.strip()  # для остальных алгоритмов
        spaces = ''
        if indent != -1:  # если отступ уже известен
            spaces = ' ' * (get_first_spaces(no_strip) - indent)
        if not doc.doc and (not line or (line[:6] == 'import'
                                         or line[:4] == 'from')):
            # пропуск импортов и пустых строк ДО
            continue
        elif line and line[0] == '#':  # сохранение комментариев
            if com:
                result.append(line[1:].strip())
                continue
        elif com:  # выход из цикла при завершении комментариев
            break
        if not com and doc.is_doc(line):  # сохранение документации
            if not strip:
                if indent == -1:  # получение первого отступа в документации
                    indent = get_first_spaces(no_strip)
                    spaces = ' ' * (get_first_spaces(no_strip) - indent)
                line = spaces + line
            result.append(line)
            if not doc.doc:  # документация однострочная - прерывание цикла
                break
        else:  # выход из цикла при завершении документации
            # документация должна быть до мешанины кода
            # или после обычных импортов, иначе не выявится
            break
    if result and not com:  # обрезание кавычек
        if len(result) == 1:  # у однострочной документации
            if result[0] == '"""':
                del result[0]
            else:
                result[0] = result[0][result[0].index('"""') + 3:]
                result[0] = result[0][:result[0].index('"""')]
        else:  # у многострочной
            result[0] = result[0][result[0].index('"""') + 3:]
            if not result[0]:
                del result[0]
            last = len(result) - 1
            result[last] = result[last][:result[last].index('"""')]
            if not result[last]:
                del result[last]
    return result


def get_block(lines, index, indent=4):
    """Получить блок кода.

    :param lines: список строк
    :param index: индекс элемента
    :param indent: отступ в начале строки
    :return: list, блок кода с данным отступом
    """
    i = index+1
    while i < len(lines):  # анализ с заданной позиции
        line = lines[i]
        if not line or line.isspace():  # пропуск пустых строк
            i += 1
            continue
        if get_first_spaces(line) < indent:  # проверка отступа
            break
        i += 1
    if i == index+1:  # иначе в блоке будет первая строка
        return []
    return lines[index+1:i]


def get_indent(lines):
    """Получить кол-во символов отступа в начале строки.

    :param lines: список строк
    :return: int (-1 если отступ не найден)
    """
    block = False
    doc = IsDoc()
    for line in lines:
        if not doc.is_doc(line) and not block and\
                ((line[:6] == 'class ' or line[:4] == 'def ') and ':' in line)\
                or line[:5] == 'pass ':
            # поиск блока
            block = True
            continue
        if block and line and not line.isspace() and not (
                    line.strip()[0] == '#'):
            # определение отступа в блоке
            return get_first_spaces(line)
    return -1


def get_index(elements, name):
    """Получить индекс нужного элемента.

    :param elements: list, [(имя, индекс), (имя(), индекс), ...]
    :param name: имя искомого элемента
    :return: int индекс или None
    """
    for element in elements:
        el_name = element[0]
        if '(' in el_name:
            el_name = el_name[:el_name.index('(')].strip()
        if el_name == name:
            return element[1]
