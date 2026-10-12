import pytest

from petrovich import Case, Gender, Petrovich


@pytest.fixture(scope="module")
def petro():
    return Petrovich()


@pytest.mark.parametrize(
    "part,name,case,gender,expected",
    [
        ("firstname", "Дамир", Case.GENITIVE, None, "Дамира"),
        ("lastname", "Абдуллин", Case.PREPOSITIONAL, None, "Абдуллине"),
        ("lastname", "Каримова", Case.DATIVE, None, "Каримовой"),
        ("middlename", "Васильевич", Case.DATIVE, None, "Васильевичу"),
        ("lastname", "Ткач", Case.GENITIVE, Gender.FEMALE, "Ткач"),
        ("lastname", "Ткач", Case.GENITIVE, Gender.MALE, "Ткача"),
        ("lastname", "Дюма", Case.GENITIVE, Gender.MALE, "Дюма"),
        ("firstname", "Шота", Case.DATIVE, None, "Шота"),
        ("firstname", "НИНЕЛЬ", Case.ACCUSATIVE, Gender.FEMALE, "НИНЕЛЬ"),
        ("firstname", "ДАМИР", Case.GENITIVE, Gender.MALE, "ДАМИРА"),
        ("firstname", "Пётр", Case.GENITIVE, Gender.MALE, "Петра"),
        ("firstname", "ПЁТР", Case.GENITIVE, Gender.MALE, "ПЕТРА"),
        ("firstname", "Анна-Мария", Case.GENITIVE, Gender.FEMALE, "Анны-Марии"),
        ("firstname", "Лев-Павел", Case.GENITIVE, Gender.MALE, "Льва-Павла"),
        ("lastname", "Бонч-Бруевич", Case.GENITIVE, Gender.MALE, "Бонч-Бруевича"),
        ("lastname", "Бонч", Case.GENITIVE, Gender.MALE, "Бонча"),
        ("lastname", "Иванов-Бонч", Case.GENITIVE, Gender.MALE, "Иванова-Бонча"),
        ("lastname", "  Иванов--Петров \t", Case.GENITIVE, Gender.MALE, "  Иванова--Петрова \t"),
        ("firstname", "Никита", Case.GENITIVE, Gender.MALE, "Никиты"),
        ("firstname", "Ким", Case.GENITIVE, Gender.FEMALE, "Ким"),
        ("firstname", "Alex", Case.GENITIVE, None, "Alex"),
        ("firstname", "Анна", Case.NOMINATIVE, Gender.FEMALE, "Анна"),
    ],
)
def test_inflection(petro, part, name, case, gender, expected):
    assert getattr(petro, part)(name, case, gender) == expected


@pytest.mark.parametrize(
    "case,expected",
    [
        (Case.GENITIVE, "Ивана"),
        (Case.DATIVE, "Ивану"),
        (Case.ACCUSATIVE, "Ивана"),
        (Case.INSTRUMENTAL, "Иваном"),
        (Case.PREPOSITIONAL, "Иване"),
        (Case.NOMINATIVE, "Иван"),
    ],
)
def test_all_cases(petro, case, expected):
    assert petro.firstname("Иван", case, Gender.MALE) == expected


@pytest.mark.parametrize("value", ["", " ", "\t"])
def test_empty(petro, value):
    with pytest.raises(ValueError):
        petro.firstname(value, Case.GENITIVE)


def test_invalid_arguments(petro):
    with pytest.raises(TypeError):
        petro.firstname(None, Case.GENITIVE)
    with pytest.raises(ValueError):
        petro.firstname("Иван", -1)
    with pytest.raises(ValueError):
        petro.firstname("Иван", 12)
    with pytest.raises(ValueError):
        petro.firstname("Иван", 0, "unknown")
    with pytest.raises(ValueError):
        petro.inflect("Иван", 0, "unknown")


def test_legacy_api(petro):
    from petrovich.enums import Case as LegacyCase
    from petrovich.main import Petrovich as LegacyPetrovich

    assert LegacyPetrovich is Petrovich
    assert LegacyCase.GENITIVE == 0
    assert Gender.ANDRGN == "androgynous"
    assert len(Case.CASES) == 5
    assert petro.firstname("Иван", 0, "male") == "Ивана"


async def test_async_factory():
    petro = await Petrovich.create()
    assert petro.firstname("Иван", Case.GENITIVE) == "Ивана"
