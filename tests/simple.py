# coding: utf-8
from unittest import TestCase
from petrovich.enums import Case
from petrovich.main import Petrovich

__author__ = 'damirazo <me@damirazo.ru>'


class PetrovichTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p = Petrovich()

    def test_1(self):
        self.assertEqual(
            self.p.firstname(u'Дамир', Case.CASE_GENITIVE), u'Дамира')

    def test_2(self):
        self.assertEqual(
            self.p.lastname(u'Абдуллин', Case.CASE_PREPOSITIONAL), u'Абдуллине')

    def test_3(self):
        self.assertEqual(
            self.p.lastname(u'Каримова', Case.CASE_DATIVE), u'Каримовой')

    def test_4(self):
        self.assertEqual(
            self.p.middlename(u'Васильевич', Case.CASE_DATIVE), u'Васильевичу')