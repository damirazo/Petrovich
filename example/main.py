from petrovich.enums import Case, Gender
from petrovich.main import Petrovich

__author__ = "damirazo <me@damirazo.ru>"


if __name__ == "__main__":
    rows = [
        ("Алексеев", "Алексей", "Давыдович"),
        ("Матвеев", "Денис", "Евгеньевич"),
        ("Алимова", "Алия", "Маратовна"),
        ("Ткач", "Валентина", "Петровна", Gender.FEMALE),
        ("Ткач", "Валентин", "Петрович", Gender.MALE),
    ]

    petro = Petrovich()

    for segments in rows:
        gender = None

        if len(segments) == 4:
            fname, iname, oname, gender = segments
        elif len(segments) == 3:
            fname, iname, oname = segments
        else:
            raise ValueError

        for case in Case.CASES:
            print(
                f"{petro.lastname(fname, case, gender)} "
                f"{petro.firstname(iname, case, gender)} "
                f"{petro.middlename(oname, case, gender)}"
            )
