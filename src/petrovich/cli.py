"""Command-line rule management and inflection."""

import argparse
import sys
from urllib.error import URLError

from . import Case, Gender, NamePart, Petrovich
from .rules import DEFAULT_REF, load_rules, update_rules


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="petrovich")
    commands = parser.add_subparsers(dest="command", required=True)
    rules = commands.add_parser("rules").add_subparsers(dest="action", required=True)
    validate = rules.add_parser("validate")
    validate.add_argument("path", nargs="?")
    update = rules.add_parser("update")
    update.add_argument("--output", required=True)
    source = update.add_mutually_exclusive_group()
    source.add_argument("--ref", default=DEFAULT_REF)
    source.add_argument("--url")
    update.add_argument("--sha256")
    update.add_argument("--timeout", type=float, default=30)
    inflect = commands.add_parser("inflect")
    inflect.add_argument("part", choices=list(NamePart))
    inflect.add_argument("value")
    inflect.add_argument("--case", required=True, choices=[c.name.lower() for c in Case])
    inflect.add_argument("--gender", choices=list(Gender))
    inflect.add_argument("--rules")
    args = parser.parse_args(argv)
    try:
        if args.command == "inflect":
            print(
                Petrovich(args.rules).inflect(
                    args.value, Case[args.case.upper()], args.part, args.gender
                )
            )
        elif args.action == "validate":
            load_rules(args.path)
            print("Rules are valid")
        else:
            digest = update_rules(
                args.output, ref=args.ref, url=args.url, sha256=args.sha256, timeout=args.timeout
            )
            print(f"Updated {args.output}; sha256={digest}")
    except (OSError, ValueError, URLError) as exc:
        print(f"petrovich: {exc}", file=sys.stderr)
        return 1
    return 0
