# coding: utf-8
from petrovich.enums import Case, Gender
from petrovich.main import Petrovich

__author__ = 'damirazo <me@damirazo.ru>'


if __name__ == '__main__':
    rows = [
        (u'Алексеев', u'Алексей', u'Давыдович', Gender.MALE),
        (u'Матвеев', u'Денис', u'Евгеньевич', Gender.MALE),
        (u'Алимова', u'Алия', u'Маратовна', Gender.FEMALE),
    ]

    petro = Petrovich()

    for (fname, iname, oname, gender) in rows:
        for case in Case.CASES:
            print(u'{} {} {}'.format(
                petro.lastname(fname, case, gender),
                petro.firstname(iname, case, gender),
                petro.middlename(oname, case, gender),
            ))
