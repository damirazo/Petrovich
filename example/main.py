# coding: utf-8
from petrovich.enums import Case, Gender
from petrovich.main import Petrovich

__author__ = 'damirazo <me@damirazo.ru>'


if __name__ == '__main__':
    rows = [
        (u'Алексеев', u'Алексей', u'Давыдович'),
        (u'Матвеев', u'Денис', u'Евгеньевич'),
        (u'Алимова', u'Алия', u'Маратовна'),
        (u'Ткач', u'Валентина', u'Петровна', Gender.FEMALE),
        (u'Ткач', u'Валентин', u'Петрович', Gender.MALE),
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
            print(u'{} {} {}'.format(
                petro.lastname(fname, case, gender),
                petro.firstname(iname, case, gender),
                petro.middlename(oname, case, gender),
            ))
