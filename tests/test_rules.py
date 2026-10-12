import asyncio
import hashlib
import io
import json
from dataclasses import FrozenInstanceError
from importlib.resources import files
from unittest.mock import patch
from urllib.error import URLError

import pytest

from petrovich import Case, Petrovich
from petrovich.rules import (
    MAX_BYTES,
    RulesError,
    aload_rules,
    aupdate_rules,
    load_rules,
    parse_rules,
    rules_url,
    update_rules,
)


@pytest.fixture
def payload():
    return files("petrovich").joinpath("data/rules.json").read_bytes()


def response(payload):
    stream = io.BytesIO(payload)
    stream.url = "https://example.org/rules.json"
    return stream


def test_custom_rules(tmp_path, payload):
    data = json.loads(payload)
    data["firstname"]["exceptions"].insert(
        0,
        {
            "gender": "male",
            "test": ["иван"],
            "mods": ["."] * 5,
        },
    )
    path = tmp_path / "custom.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    assert Petrovich(path).firstname("Иван", Case.GENITIVE) == "Иван"
    rules = load_rules(path)
    with pytest.raises(FrozenInstanceError):
        rules.firstname = rules.lastname
    with pytest.raises(ValueError):
        Petrovich(path, rules=rules)


@pytest.mark.parametrize(
    "payload",
    [b"not json", b"\xff", b"[]", b"{}", b"x" * (MAX_BYTES + 1)],
    ids=["text", "encoding", "array", "missing", "oversized"],
)
def test_invalid_document(payload):
    with pytest.raises(RulesError):
        parse_rules(payload)


@pytest.mark.parametrize(
    "key,value",
    [
        ("gender", "other"),
        ("gender", None),
        ("test", []),
        ("test", "иван"),
        ("test", [None]),
        ("mods", ["а"]),
        ("mods", ["a"] * 5),
        ("mods", ["а-"] * 5),
        ("mods", ["-------а"] * 5),
        ("tags", ["unknown"]),
    ],
)
def test_invalid_rule(payload, key, value):
    data = json.loads(payload)
    data["firstname"]["exceptions"][0][key] = value
    with pytest.raises(RulesError):
        parse_rules(json.dumps(data).encode())


@pytest.mark.parametrize("value", [None, {}, [False]])
def test_invalid_collection(payload, value):
    data = json.loads(payload)
    data["firstname"]["suffixes"] = value
    with pytest.raises(RulesError):
        parse_rules(json.dumps(data).encode())


def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_rules(tmp_path / "absent.json")


def test_bundled_provenance(payload):
    from petrovich.rules import DEFAULT_REF

    provenance = json.loads(
        files("petrovich").joinpath("data/PROVENANCE.json").read_text(encoding="utf-8")
    )
    assert provenance["sha256"] == hashlib.sha256(payload).hexdigest()
    assert provenance["commit"] == DEFAULT_REF
    assert provenance["url"] == rules_url()


def test_non_utf8_document_rejected(payload):
    with pytest.raises(RulesError):
        parse_rules(payload.decode("utf-8").encode("utf-16"))


def test_update(tmp_path, payload):
    target = tmp_path / "nested" / "rules.json"
    digest = hashlib.sha256(payload).hexdigest()
    with patch("petrovich.rules.urlopen", return_value=response(payload)) as request:
        assert update_rules(target, sha256=digest) == digest
    request.assert_called_once_with(rules_url(), timeout=30)
    assert target.read_bytes() == payload
    assert list(target.parent.iterdir()) == [target]


@pytest.mark.parametrize("kind", ["invalid", "hash", "network", "replace", "downgrade"])
def test_failed_update_preserves_existing_file(tmp_path, payload, kind):
    target = tmp_path / "rules.json"
    target.write_bytes(b"original")
    stream = response(b"bad" if kind == "invalid" else payload)
    if kind == "downgrade":
        stream.url = "http://example.org/rules.json"
    with patch("petrovich.rules.urlopen", return_value=stream) as request:
        if kind == "network":
            request.side_effect = URLError("offline")
        with patch("petrovich.rules.os.replace", side_effect=OSError("busy")):
            with pytest.raises((ValueError, OSError)):
                update_rules(target, sha256="wrong" if kind == "hash" else None)
    assert target.read_bytes() == b"original"
    assert list(tmp_path.iterdir()) == [target]


def test_invalid_source(tmp_path):
    with pytest.raises(ValueError):
        update_rules(tmp_path / "rules.json", url="http://example.org")
    with pytest.raises(ValueError):
        update_rules(tmp_path / "rules.json", timeout=0)
    with pytest.raises(ValueError):
        rules_url("")
    assert "feature%2Ftest" in rules_url("feature/test")


async def test_async_io(tmp_path, payload):
    target = tmp_path / "rules.json"
    with patch("petrovich.rules.urlopen", return_value=response(payload)):
        await aupdate_rules(target)
    assert await aload_rules(target) == load_rules()


async def test_async_update_does_not_block_loop(tmp_path, payload):
    import threading

    started = threading.Event()
    release = threading.Event()

    def download(*args, **kwargs):
        started.set()
        assert release.wait(timeout=5)
        return response(payload)

    with patch("petrovich.rules.urlopen", side_effect=download):
        task = asyncio.create_task(aupdate_rules(tmp_path / "rules.json"))
        try:
            async with asyncio.timeout(5):
                assert await asyncio.to_thread(started.wait, 4)
                assert not task.done()
        finally:
            release.set()
        await task
