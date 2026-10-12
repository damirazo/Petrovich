import os
import json
from typing import Optional, Tuple, Generator, Union


# Текущая директория
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
# Путь до файла с правилами округления
DEFAULT_RULES_PATH = os.path.join(CURRENT_PATH, 'rules', 'rules.json')


class Petrovich:
    """Сервисный класс для выполнения склонения ФИО"""
    # Разделители фрагментов ФИО
    separators: Tuple[str] = ('-', ' ')

    def __init__(self, rules_path: Optional[str] = None):
        """
        :param rules_path: Путь до файла с правилами.
            В случае отсутствия будет взят путь по умолчанию,
            указанный в `DEFAULT_RULES_PATH`
        """
        if rules_path is None:
            rules_path = DEFAULT_RULES_PATH

        if not os.path.exists(rules_path):
            raise IOError((
                'File with rules {} does not exists!'
            ).format(rules_path))

        with open(rules_path, 'r') as fp:
            self.data = json.load(fp)

    def firstname(
            self,
            value: str,
            case: int,
            gender: Optional[str] = None) -> str:
        """Склонение имени

        :param value: Значение для склонения
        :param case: Падеж для склонения (значение из класса Case)
        :param gender: Грамматический род
        """
        if not value:
            raise ValueError('Firstname cannot be empty.')

        return self.__inflect(value, case, 'firstname', gender)

    def lastname(
            self,
            value: str,
            case: int,
            gender: Optional[str] = str) -> str:
        """Склонение фамилии

        :param value: Значение для склонения
        :param case: Падеж для склонения (значение из класса Case)
        :param gender: Грамматический род
        """
        if not value:
            raise ValueError('Lastname cannot be empty.')

        return self.__inflect(value, case, 'lastname', gender)

    def middlename(
            self,
            value: str,
            case: int,
            gender: Optional[str] = None):
        """Склонение отчества

        :param value: Значение для склонения
        :param case: Падеж для склонения (значение из класса Case)
        :param gender: Грамматический род
        """
        if not value:
            raise ValueError('Middlename cannot be empty.')

        return self.__inflect(value, case, 'middlename', gender)

    def __split_name(self, name: str) -> Generator:
        """Разделяет имя на сегменты по разделителям в self.separators

        :param name: имя
        :return: разделённое имя вместе с разделителями
        """
        def gen(_name, separators):
            if len(separators) == 0:
                yield _name
            else:
                segments = _name.split(separators[0])
                for subsegment in gen(segments[0], separators[1:]):
                    yield subsegment
                for segment in segments[1:]:
                    for subsegment in gen(segment, separators[1:]):
                        yield separators[0]
                        yield subsegment

        return gen(name, self.separators)

    def __inflect(
            self,
            value: str,
            case: int,
            name_form: str,
            gender: Optional[str] = None) -> str:
        """Выполнение процесса склонения с заданными параметрами"""
        # Поиск возможных исключений для конкретного варианта склонения
        exceptions = self.__check_exceptions(value, case, name_form, gender)
        if exceptions is not None:
            return exceptions

        segments = list(self.__split_name(value))
        if len(segments) > 1:
            result = [
                (
                    self.__find_rules(segment, case, name_form, gender)
                    if (segment and segment not in self.separators)
                    else segment
                )
                for segment in segments
            ]

            result = ''.join(result)
        else:
            result = self.__find_rules(value, case, name_form, gender)

        return result

    def __find_rules(
            self,
            name: str,
            case: int,
            name_form: str,
            gender: Optional[str] = None) -> str:
        """Поиск подходящих правил склонения"""
        for rule in self.data[name_form]['suffixes']:
            # Если род указан и он не совпадает с текущим, то пропускаем
            # В противном случае проверяем соответствие
            if gender is not None and rule['gender'] != gender:
                continue

            for chars in rule['test']:
                last_chars = name[-len(chars):]
                if last_chars == chars:
                    if rule['mods'][case] == '.':
                        continue

                    return self.__apply_rule(rule['mods'], name, case)

        return name

    def __check_exceptions(
            self,
            name: str,
            case: int,
            name_form: str,
            gender: Optional[str] = None) -> Union[None, str]:
        """Проверка является ли указанная форма склонения исключением"""
        name_form_obj = self.data.get(name_form)
        if not name_form_obj or not name_form_obj.get('exceptions'):
            return

        lower = name.lower()
        for rule in name_form_obj['exceptions']:
            if gender is not None and rule['gender'] != gender:
                continue

            if lower in rule['test']:
                return self.__apply_rule(rule['mods'], name, case)

        return

    @staticmethod
    def __apply_rule(mods: list, name: str, case: int) -> str:
        """Применение правила с заменами к ФИО"""
        result = name[:len(name) - mods[case].count('-')]
        result += mods[case].replace('-', '')

        return result
