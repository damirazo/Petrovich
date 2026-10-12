"""Validated, immutable rules and explicit, atomic HTTPS updates."""

import asyncio
import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from urllib.parse import quote, urlparse
from urllib.request import urlopen

from .enums import Gender, NamePart

DEFAULT_REF = "df207fbe61af6c58c191ee021c405c4a3759c3a7"
MAX_BYTES = 2 * 1024 * 1024
type RulesPath = str | os.PathLike[str]


class RulesError(ValueError):
    """The rule document is invalid or failed integrity validation."""


@dataclass(frozen=True, slots=True)
class Rule:
    gender: Gender
    tests: tuple[str, ...]
    mods: tuple[str, ...]
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RuleGroup:
    exceptions: tuple[Rule, ...]
    suffixes: tuple[Rule, ...]


@dataclass(frozen=True, slots=True)
class RuleSet:
    firstname: RuleGroup
    lastname: RuleGroup
    middlename: RuleGroup

    def group(self, part: NamePart) -> RuleGroup:
        return getattr(self, part.value)  # type: ignore[no-any-return]


def _strings(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(s, str) and s for s in value):
        raise RulesError(f"{label} must be a list of non-empty strings")
    return tuple(value)


def _rules(value: object) -> tuple[Rule, ...]:
    if not isinstance(value, list):
        raise RulesError("Rule collections must be arrays")
    result = []
    for item in value:
        if not isinstance(item, dict):
            raise RulesError("Each rule must be an object")
        try:
            gender_value = item.get("gender")
            if not isinstance(gender_value, str):
                raise ValueError("Gender must be a string")
            gender = Gender(gender_value)
        except (ValueError, TypeError) as exc:
            raise RulesError("Invalid rule gender") from exc
        tests = _strings(item.get("test"), "test")
        mods = _strings(item.get("mods"), "mods")
        tags = _strings(item.get("tags", []), "tags")
        if not tests or len(mods) != 5:
            raise RulesError("Rules need tests and exactly five modifiers")
        if any(tag != "first_word" for tag in tags):
            raise RulesError("Unsupported rule tag")
        if any(not re.fullmatch(r"\.|-*[а-яёА-ЯЁ]+", mod) for mod in mods):
            raise RulesError("Invalid modifier")
        if any(len(mod) - len(mod.lstrip("-")) > min(map(len, tests)) for mod in mods):
            raise RulesError("Modifier removes more characters than the matched test")
        result.append(Rule(gender, tuple(t.lower() for t in tests), mods, tags))
    return tuple(result)


def parse_rules(payload: bytes) -> RuleSet:
    if len(payload) > MAX_BYTES:
        raise RulesError("Rules exceed the 2 MiB limit")
    try:
        data = json.loads(payload.decode("utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise RulesError("Rules must be valid UTF-8 JSON") from exc
    if not isinstance(data, dict):
        raise RulesError("Rules must be an object")
    groups = {}
    for part in NamePart:
        group = data.get(part.value)
        if not isinstance(group, dict):
            raise RulesError(f"Missing rule group: {part}")
        groups[part.value] = RuleGroup(
            _rules(group.get("exceptions", [])), _rules(group.get("suffixes"))
        )
    return RuleSet(**groups)


def load_rules(path: RulesPath | None = None) -> RuleSet:
    resource = files("petrovich").joinpath("data/rules.json") if path is None else Path(path)
    with resource.open("rb") as stream:
        return parse_rules(stream.read(MAX_BYTES + 1))


async def aload_rules(path: RulesPath | None = None) -> RuleSet:
    return await asyncio.to_thread(load_rules, path)


def rules_url(ref: str = DEFAULT_REF) -> str:
    if not ref or ref in {".", ".."}:
        raise ValueError("An upstream commit, tag or branch is required")
    base = "https://raw.githubusercontent.com/petrovich/petrovich-rules"
    return f"{base}/{quote(ref, safe='')}/rules.json"


def update_rules(
    destination: RulesPath,
    *,
    ref: str = DEFAULT_REF,
    url: str | None = None,
    sha256: str | None = None,
    timeout: float = 30,
) -> str:
    """Validate before atomic replacement; return the downloaded SHA-256 digest."""
    source = url or rules_url(ref)
    if urlparse(source).scheme != "https":
        raise ValueError("Rules must be downloaded over HTTPS")
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    with urlopen(source, timeout=timeout) as response:
        if urlparse(response.url).scheme != "https":
            raise RulesError("HTTPS downgrade is not allowed")
        payload = response.read(MAX_BYTES + 1)
    digest = hashlib.sha256(payload).hexdigest()
    if sha256 is not None and digest != sha256.lower():
        raise RulesError("SHA-256 mismatch")
    parse_rules(payload)
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as stream:
            temporary = stream.name
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)
    return digest


async def aupdate_rules(
    destination: RulesPath,
    *,
    ref: str = DEFAULT_REF,
    url: str | None = None,
    sha256: str | None = None,
    timeout: float = 30,  # noqa: ASYNC109
) -> str:
    """Offload I/O; timeout limits the socket, cancellation cannot stop the thread."""
    return await asyncio.to_thread(
        update_rules, destination, ref=ref, url=url, sha256=sha256, timeout=timeout
    )
