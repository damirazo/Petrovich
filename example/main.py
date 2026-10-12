from petrovich.enums import Case, Gender
from petrovich.main import Petrovich


if __name__ == '__main__':
    rows = [
        ('Алексеев', 'Алексей', 'Давыдович', Gender.MALE),
        ('Торсунов', 'Андрей', 'Владимирович', Gender.MALE),
        ('Матвеев', 'Денис', 'Евгеньевич', Gender.MALE),
        ('Исламов', 'Марат', 'Рафаэлевич', Gender.MALE),
        ('Алимова', 'Алия', 'Маратовна', Gender.FEMALE),
        ('Ткач', 'Валентина', 'Петровна', Gender.FEMALE),
        ('Ткач', 'Валентин', 'Петрович', Gender.MALE),
    ]

    petro = Petrovich()

    for segments in rows:
        fname, iname, oname, gender = segments

        for case in Case.CASES:
            print(u'{} {} {}'.format(
                petro.lastname(fname, case, gender),
                petro.firstname(iname, case, gender),
                petro.middlename(oname, case, gender),
            ))
