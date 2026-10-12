"""Pure inflection engine with a backwards-compatible synchronous facade."""

import re
from typing import Self

from .enums import Case, Gender, NamePart
from .rules import Rule, RuleSet, RulesPath, aload_rules, load_rules


class Petrovich:
    def __init__(self, rules_path: RulesPath | None = None, *, rules: RuleSet | None = None):
        if rules_path is not None and rules is not None:
            raise ValueError("Specify either rules_path or rules")
        self._rules = rules if rules is not None else load_rules(rules_path)

    @classmethod
    async def create(cls, rules_path: RulesPath | None = None) -> Self:
        return cls(rules=await aload_rules(rules_path))

    def firstname(self, value: str, case: Case | int, gender: Gender | str | None = None) -> str:
        return self.inflect(value, case, NamePart.FIRSTNAME, gender)

    def lastname(self, value: str, case: Case | int, gender: Gender | str | None = None) -> str:
        return self.inflect(value, case, NamePart.LASTNAME, gender)

    def middlename(self, value: str, case: Case | int, gender: Gender | str | None = None) -> str:
        return self.inflect(value, case, NamePart.MIDDLENAME, gender)

    def inflect(
        self,
        value: str,
        case: Case | int,
        part: NamePart | str,
        gender: Gender | str | None = None,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError("Name must be a string")
        if not value.strip():
            raise ValueError("Name cannot be empty")
        case = Case(case)
        part = NamePart(part)
        gender = Gender(gender) if gender is not None else None
        if case == Case.NOMINATIVE:
            return value
        segments = re.split(r"([-\s]+)", value)
        words = [i for i, segment in enumerate(segments) if segment and i % 2 == 0]
        for position, index in enumerate(words):
            segments[index] = self._segment(
                segments[index], case, part, gender, position == 0 and len(words) > 1
            )
        return "".join(segments)

    def _segment(
        self,
        name: str,
        case: Case,
        part: NamePart,
        gender: Gender | None,
        first: bool,
    ) -> str:
        group = self._rules.group(part)
        for exact, rules in ((True, group.exceptions), (False, group.suffixes)):
            for rule in rules:
                if rule.tags and not first:
                    continue
                if gender is not None and rule.gender not in (gender, Gender.ANDROGYNOUS):
                    continue
                # Without a gender, prefer productive rules over ambiguous female no-ops.
                if gender is None and rule.gender == Gender.FEMALE and set(rule.mods) == {"."}:
                    continue
                lower = name.lower()
                if any(lower == test if exact else lower.endswith(test) for test in rule.tests):
                    return self._apply(name, rule, case)
        return name

    @staticmethod
    def _apply(name: str, rule: Rule, case: Case) -> str:
        mod = rule.mods[case]
        if mod == ".":
            return name
        remove = len(mod) - len(mod.lstrip("-"))
        ending = mod[remove:]
        if name.isupper():
            ending = ending.upper()
        return name[: len(name) - remove] + ending
