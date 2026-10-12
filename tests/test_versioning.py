import pytest

from scripts.ci_version import version_for


@pytest.mark.parametrize(
    "base,branch,tag,pipeline,expected",
    [
        ("2.0.0.dev0", "petrovich_2", "", "42", "2.0.0.dev0"),
        ("2.0.0.dev0", "release/2.0", "", "42", "2.0.0.dev42"),
        ("2.0.1", "release/2.0", "", "43", "2.0.1.dev43"),
        ("2.0.0", "", "v2.0.0", "42", "2.0.0"),
        ("2.0.0rc1", "", "v2.0.0rc1", "42", "2.0.0rc1"),
        ("10.0.0", "release/10.0", "", "42", "10.0.0.dev42"),
    ],
)
def test_versions(base, branch, tag, pipeline, expected):
    assert version_for(base, branch, tag, pipeline) == expected


@pytest.mark.parametrize(
    "branch,tag,pipeline",
    [
        ("", "v1.0.0", "1"),
        ("", "v2.0.1", "1"),
        ("", "arbitrary", "1"),
        ("release/1.0", "", "1"),
        ("release/3.0", "", "1"),
        ("release/2.0", "", "bad"),
        ("release/2.0.0", "", "1"),
    ],
)
def test_reject_bad_release(branch, tag, pipeline):
    with pytest.raises(ValueError):
        version_for("2.0.0", branch, tag, pipeline)
