"""Derive a PEP 440 version from GitLab's release ref before building."""

import os
import re
from pathlib import Path


def version_for(base: str, branch: str, tag: str, pipeline: str) -> str:
    if tag:
        if not re.fullmatch(r"v(?:[2-9]|[1-9]\d+)\.\d+\.\d+(?:(?:a|b|rc)\d+)?", tag):
            raise ValueError("Expected a modern release tag, e.g. v2.0.0 or v2.0.0rc1")
        version = tag[1:]
        if base != version:
            raise ValueError(f"Tag {version} does not match pyproject.toml version {base}")
        return version
    if branch.startswith("release/"):
        match = re.fullmatch(r"release/((?:[2-9]|[1-9]\d+)\.\d+)", branch)
        if not match:
            raise ValueError("Expected release/MAJOR.MINOR (MAJOR >= 2)")
        if not base.startswith(match[1] + "."):
            raise ValueError("Release branch and package version do not match")
        if not pipeline.isdecimal():
            raise ValueError("A numeric pipeline ID is required for release snapshots")
        public = re.match(r"\d+\.\d+\.\d+", base)
        if public is None:
            raise ValueError("Invalid base version")
        return f"{public[0]}.dev{pipeline}"
    return base


def main() -> None:
    import tomllib

    path = Path("pyproject.toml")
    original = path.read_text(encoding="utf-8")
    base = tomllib.loads(original)["project"]["version"]
    version = version_for(
        base,
        os.getenv("CI_COMMIT_BRANCH", ""),
        os.getenv("CI_COMMIT_TAG", ""),
        os.getenv("CI_PIPELINE_IID", ""),
    )
    path.write_text(
        original.replace(f'version = "{base}"', f'version = "{version}"', 1), encoding="utf-8"
    )
    print(version)


if __name__ == "__main__":
    main()
