# coding: utf-8
import json
import os

__author__ = 'damirazo <me@damirazo.ru>'


# Текущая директория
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
# Путь до файла с правилами округления
RULES_PATH = os.path.join(CURRENT_PATH, 'data', 'rules.json')


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

    def firstname(self, value, case):
        u"""
        Склонение имени

        :param value: Значение для склонения
        :param case: Падеж для склонения (значение из класса Case)
        """
        if not value:
            raise ValueError('Firstname cannot be empty.')

        return self.__inflect(value, case, 'firstname')

    def lastname(self, value, case):
        u"""
        Склонение фамилии

        :param value: Значение для склонения
        :param case: Падеж для склонения (значение из класса Case)
        """
        if not value:
            raise ValueError('Lastname cannot be empty.')

        return self.__inflect(value, case, 'lastname')

    def middlename(self, value, case):
        u"""
        Склонение отчества

        :param value: Значение для склонения
        :param case: Падеж для склонения (значение из класса Case)
        """
        if not value:
            raise ValueError('Middlename cannot be empty.')

        return self.__inflect(value, case, 'middlename')

    def __inflect(self, value, case, name_form):
        excludes = self.__check_excludes(value, case, name_form)
        if excludes:
            return excludes

        if value.count('-') > 0:
            value_segments = value.split(u'-')
            result = u''

            for segment in value_segments:
                result += self.__find_rules(segment, case, name_form)

            return result[:len(result) - 1]

        else:
            return self.__find_rules(value, case, name_form)

    def __find_rules(self, name, case, name_form):
        for rule in self.data[name_form]['suffixes']:
            for char in rule['test']:
                last_char = name[len(name) - len(char): len(name)]

                if last_char == char:
                    if rule['mods'][case] == u'.':
                        continue

                    return self.__apply_rule(rule['mods'], name, case)

        return name

    def __check_excludes(self, name, case, name_form):
        if not (name_form in self.data
                and self.data[name_form].get('exceptions', None)):
            return False

        lower = name.lower()

        for rule in self.data[name_form]['exceptions']:
            if lower in rule['test']:
                return self.__apply_rule(rule['mods'], name, case)

        return False

    def __apply_rule(self, mods, name, case):
        result = name[:len(name) - mods[case].count('-')]
        result += mods[case].replace(u'-', u'')

        return result