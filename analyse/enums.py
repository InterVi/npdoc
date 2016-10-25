"""Модуль с IntEnum типами различных элементов."""
from enum import IntEnum
__all__ = ['ElementType', 'VisibleType', 'DocType']


class ElementType(IntEnum):
    """Тип элемента."""
    mo = 0  # модуль
    cl = 1  # класс
    fun = 2  # функция
    met = 3  # метод класса
    var = 4  # переменная


class VisibleType(IntEnum):
    """Видимость элемента."""
    gl = 0  # глобально
    gl_lo = 1  # локально в элементе модуля
    se = 2  # в классе
    se_lo = 3  # локально в элементе класса


class DocType(IntEnum):
    """Тип пояснительной информации."""
    doc = 0  # документация
    com = 1  # комментарий
