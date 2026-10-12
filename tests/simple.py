from unittest import TestCase
from petrovich.enums import Case, Gender
from petrovich.main import Petrovich


class PetrovichTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p = Petrovich()

    def test_1(self):
        self.assertEqual(
            self.p.firstname('Дамир', Case.GENITIVE, gender=Gender.MALE),
            'Дамира'
        )

    def test_2(self):
        self.assertEqual(
            self.p.lastname('Абдуллин', Case.PREPOSITIONAL, Gender.MALE),
            'Абдуллине'
        )

    def test_3(self):
        self.assertEqual(
            self.p.lastname('Каримова', Case.DATIVE, Gender.FEMALE),
            'Каримовой'
        )

    def test_4(self):
        self.assertEqual(
            self.p.middlename('Васильевич', Case.DATIVE, gender=Gender.MALE),
            'Васильевичу'
        )

    def test_5(self):
        self.assertEqual(
            self.p.lastname('Ткач', Case.GENITIVE, gender=Gender.FEMALE),
            'Ткач'
        )

    def test_6(self):
        self.assertEqual(
            self.p.lastname('Ткач', Case.GENITIVE, gender=Gender.MALE),
            'Ткача'
        )
