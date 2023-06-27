import csv
import pytest

from petrovich.enums import Case, Gender
from petrovich.main import Petrovich


genders = {
    'M': Gender.MALE,
    'F': Gender.FEMALE,
}

test_dataset = list()

with open("./tests/first_names.csv", encoding='utf-8') as names_file:
    lines = csv.reader(names_file)
    for line in lines:
        test_dataset.append(line)


@pytest.mark.parametrize("first_name, first_name_dative, gender", test_dataset)
def test_first_name(first_name, first_name_dative, gender):
    p = Petrovich()
    hypothesis = p.lastname(first_name, Case.DATIVE, genders[gender])
    assert hypothesis == first_name_dative