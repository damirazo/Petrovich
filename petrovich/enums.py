# coding: utf-8
__author__ = 'damirazo <me@damirazo.ru>'


class Case(object):
    u"""
    Перечисление падежей
    """
    # Родительный
    CASE_GENITIVE = 0
    # Дательный
    CASE_DATIVE = 1
    # Винительный
    CASE_ACCUSATIVE = 2
    # Творительный
    CASE_INSTRUMENTAL = 3
    # Предложный
    CASE_PREPOSITIONAL = 4

    CASES = (
        CASE_DATIVE,
        CASE_GENITIVE,
        CASE_ACCUSATIVE,
        CASE_INSTRUMENTAL,
        CASE_PREPOSITIONAL,
    )