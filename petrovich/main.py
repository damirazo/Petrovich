# coding: utf-8
import os
import json

__author__ = 'damirazo <me@damirazo.ru>'


# Текущая директория
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
# Путь до файла с правилами округления
DEFAULT_RULES_PATH = os.path.join(CURRENT_PATH, 'rules', 'rules.json')


class Petrovich(object):
    u"""
    Основной класс для склонения кириллических ФИО
    """
    # Разделители
    separators = (u"-", u" ")

    def __init__(self, rules_path=None):
        u"""
        :param rules_path: Путь до файла с правилами.
            В случае отсутствия будет взят путь по умолчанию,
            указанный в `DEFAULT_RULES_PATH`
        :return:
        """
        if rules_path is None:
            rules_path = DEFAULT_RULES_PATH

        if not os.path.exists(rules_path):
            raise IOError((
                'File with rules {} does not exists!'
            ).format(rules_path))

        try:
            with open(rules_path, 'r', encoding='utf8') as fp:
                self.data = json.load(fp)
        except:
            with open(rules_path, 'r') as fp:
                self.data = json.load(fp)

    def firstname(self, value, case, gender=None):
        u"""
        Склонение имени

        :param value: Значение для склонения
        :param case: Падеж для склонения (значение из класса Case)
        :param gender: Грамматический род
        """
        if not value:
            raise ValueError('Firstname cannot be empty.')

        return self.__inflect(value, case, 'firstname', gender)

    def lastname(self, value, case, gender=None):
        u"""
        Склонение фамилии

        :param value: Значение для склонения
        :param case: Падеж для склонения (значение из класса Case)
        :param gender: Грамматический род
        """
        if not value:
            raise ValueError('Lastname cannot be empty.')

        return self.__inflect(value, case, 'lastname', gender)

    def middlename(self, value, case, gender=None):
        u"""
        Склонение отчества

        :param value: Значение для склонения
        :param case: Падеж для склонения (значение из класса Case)
        :param gender: Грамматический род
        """
        if not value:
            raise ValueError('Middlename cannot be empty.')

        return self.__inflect(value, case, 'middlename', gender)

    def __split_name(self, name):
        u"""
        Разделяет имя на сегменты по разделителям в self.separators
        :param name: имя
        :return: разделённое имя вместе с разделителями
        """
        def gen(name, separators):
            if len(separators) == 0:
                yield name
            else:
                segments = name.split(separators[0])
                for subsegment in gen(segments[0], separators[1:]):
                    yield subsegment
                for segment in segments[1:]:
                    for subsegment in gen(segment, separators[1:]):
                        yield separators[0]
                        yield subsegment

        return gen(name, self.separators)

    def __inflect(self, value, case, name_form, gender=None):
        excludes = self.__check_excludes(value, case, name_form, gender)
        if excludes:
            return excludes

        segments = list(self.__split_name(value))
        if len(segments) > 1:
            result = [(self.__find_rules(segment, case, name_form, gender)
                      if (segment and (segment not in self.separators)) else segment)
                      for segment in segments]
            return u"".join(result)

        else:
            return self.__find_rules(value, case, name_form, gender)

    def __find_rules(self, name, case, name_form, gender=None):
        for rule in self.data[name_form]['suffixes']:
            # Если род указан и он не совпадает с текущим, то пропускаем
            # В противном случае проверяем соответствие
            if gender is not None and rule['gender'] != gender:
                continue

            for char in rule['test']:
                last_char = name[len(name) - len(char): len(name)]

                if last_char == char:
                    if rule['mods'][case] == u'.':
                        continue

                    return self.__apply_rule(rule['mods'], name, case)

        return name

    def __check_excludes(self, name, case, name_form, gender=None):
        if not (name_form in self.data and
                self.data[name_form].get('exceptions', None)):
            return False

        lower = name.lower()

        for rule in self.data[name_form]['exceptions']:
            if gender is not None and rule['gender'] != gender:
                continue

            if lower in rule['test']:
                return self.__apply_rule(rule['mods'], name, case)

        return False

    @staticmethod
    def __apply_rule(mods, name, case):
        result = name[:len(name) - mods[case].count('-')]
        result += mods[case].replace(u'-', u'')

        return result
