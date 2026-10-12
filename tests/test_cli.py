from unittest.mock import patch

import pytest

from petrovich.cli import main


def test_inflect(capsys):
    assert main(["inflect", "firstname", "Иван", "--case", "genitive"]) == 0
    assert capsys.readouterr().out.strip() == "Ивана"


def test_validate(capsys):
    assert main(["rules", "validate"]) == 0
    assert "valid" in capsys.readouterr().out


def test_error(tmp_path, capsys):
    assert main(["rules", "validate", str(tmp_path / "missing")]) == 1
    assert "petrovich:" in capsys.readouterr().err


def test_update(capsys):
    with patch("petrovich.cli.update_rules", return_value="digest") as update:
        assert main(["rules", "update", "--output", "rules.json", "--ref", "master"]) == 0
    assert update.call_args.kwargs["ref"] == "master"
    assert "digest" in capsys.readouterr().out


def test_required_args():
    with pytest.raises(SystemExit) as exc:
        main(["rules", "update"])
    assert exc.value.code == 2
