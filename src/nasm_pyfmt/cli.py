"""Command-line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from nasm_pyfmt import __version__
from nasm_pyfmt.formatter import format_source


def _build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser for the ``nasm-pyfmt`` CLI."""
    parser = argparse.ArgumentParser(
        prog="nasm-pyfmt",
        description="Format NASM assembly source files.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Files to format (stdin if omitted and piped)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit with a non-zero status if formatting would change a file",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    """Run the formatter from the command line.

    Reads from stdin when no file paths are given, otherwise formats each path
    in place (or checks formatting with ``--check``).

    Args:
        argv: Optional argument list; defaults to ``sys.argv[1:]``.

    Raises:
        SystemExit: Non-zero when ``--check`` finds files that need formatting.
    """
    args = _build_parser().parse_args(argv)

    if not args.paths:
        source = sys.stdin.read()
        sys.stdout.write(format_source(source))
        return

    exit_code = 0
    for path in args.paths:
        original = path.read_text(encoding="utf-8")
        formatted = format_source(original)
        if args.check and formatted != original:
            exit_code = 1
            print(f"Would reformat: {path}", file=sys.stderr)
        elif not args.check and formatted != original:
            path.write_text(formatted, encoding="utf-8")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
