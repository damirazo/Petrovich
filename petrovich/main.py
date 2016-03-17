# coding: utf-8
import os
import json
from petrovich.enums import Gender

__author__ = 'damirazo <me@damirazo.ru>'


# Текущая директория
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
# Путь до файла с правилами округления
RULES_PATH = os.path.join(CURRENT_PATH, 'rules', 'rules.json')


class Petrovich(object):
    u"""
    Основной класс для склонения кириллических ФИО
    """

    def __init__(self):
        if not os.path.exists(RULES_PATH):
            raise IOError(
                'File with rules {} does not exists!'.format(RULES_PATH))

        fp = open(RULES_PATH)
        self.data = json.load(fp)
        fp.close()

    def firstname(self, value, case, gender=Gender.ANDRGN):
        u"""
        Склонение имени

        :param value: Значение для склонения
        :param case: Падеж для склонения (значение из класса Case)
        :param gender: Грамматический род
        """
        if not value:
            raise ValueError('Firstname cannot be empty.')

        return self.__inflect(value, case, 'firstname', gender)

    def lastname(self, value, case, gender=Gender.ANDRGN):
        u"""
        Склонение фамилии

        :param value: Значение для склонения
        :param case: Падеж для склонения (значение из класса Case)
        :param gender: Грамматический род
        """
        if not value:
            raise ValueError('Lastname cannot be empty.')

        return self.__inflect(value, case, 'lastname', gender)

    def middlename(self, value, case, gender=Gender.ANDRGN):
        u"""
        Склонение отчества

        :param value: Значение для склонения
        :param case: Падеж для склонения (значение из класса Case)
        :param gender: Грамматический род
        """
        if not value:
            raise ValueError('Middlename cannot be empty.')

        return self.__inflect(value, case, 'middlename', gender)

    def __inflect(self, value, case, name_form, gender=Gender.ANDRGN):
        excludes = self.__check_excludes(value, case, name_form, gender)
        if excludes:
            return excludes

        if (value.count('-') > 0) and (name_form != 'middlename'):
            value_segments = value.split(u'-')
            result = u''

            for segment in value_segments:
                result += self.__find_rules(segment, case, name_form, gender)

            return result[:len(result) - 1]

        else:
            return self.__find_rules(value, case, name_form, gender)

    def __find_rules(self, name, case, name_form, gender=Gender.ANDRGN):
        for rule in self.data[name_form]['suffixes']:
            if (rule['gender'] == gender) or (rule['gender'] == 'androgynous'):
                for char in rule['test']:
                    last_char = name[len(name) - len(char): len(name)]

                    if last_char == char:
                        if rule['mods'][case] == u'.':
                            continue

                        return self.__apply_rule(rule['mods'], name, case)

        return name

    def __check_excludes(self, name, case, name_form, gender=Gender.ANDRGN):
        if not (name_form in self.data and
                self.data[name_form].get('exceptions', None)):
            return False

        lower = name.lower()

        for rule in self.data[name_form]['exceptions']:
            if (rule['gender'] == gender) or (rule['gender'] == 'androgynous'):
                if lower in rule['test']:
                    return self.__apply_rule(rule['mods'], name, case)

        return False

    def __apply_rule(self, mods, name, case):
        result = name[:len(name) - mods[case].count('-')]
        result += mods[case].replace(u'-', u'')

        return result
