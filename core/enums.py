"""Модуль с различными IntEnum."""
from enum import IntEnum

__all__ = ['DocType']


class DocType(IntEnum):
    """Тип документации."""
    rst = 0
