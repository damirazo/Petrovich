# coding: utf-8
from petrovich.enums import Case
from petrovich.main import Petrovich

__author__ = 'damirazo <me@damirazo.ru>'


if __name__ == '__main__':
    strings = [
        (u'Алексеев', u'Алексей', u'Давыдович'),
        (u'Матвеев', u'Денис', u'Евгеньевич'),
        (u'Алимова', u'Алия', u'Маратовна'),
    ]

    petro = Petrovich()

    for (fname, iname, oname) in strings:
        for case in Case.CASES:
            print(u'{} {} {}'.format(
                petro.lastname(fname, case),
                petro.firstname(iname, case),
                petro.middlename(oname, case),
            ))