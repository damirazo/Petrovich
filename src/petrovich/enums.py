"""Public grammatical categories; legacy numeric values are preserved."""

from enum import IntEnum, StrEnum
from typing import ClassVar


class Case(IntEnum):
    GENITIVE = 0
    DATIVE = 1
    ACCUSATIVE = 2
    INSTRUMENTAL = 3
    PREPOSITIONAL = 4
    NOMINATIVE = 5

    CASES: ClassVar[tuple["Case", ...]]


Case.CASES = (Case.DATIVE, Case.GENITIVE, Case.ACCUSATIVE, Case.INSTRUMENTAL, Case.PREPOSITIONAL)


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    ANDROGYNOUS = "androgynous"
    ANDRGN = "androgynous"


class NamePart(StrEnum):
    FIRSTNAME = "firstname"
    LASTNAME = "lastname"
    MIDDLENAME = "middlename"
