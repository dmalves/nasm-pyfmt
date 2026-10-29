"""Tests for the ``nasm-pyfmt`` command-line interface."""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

from nasm_pyfmt import __version__
from nasm_pyfmt.cli import _build_parser, main

FIXTURES = Path(__file__).parent / "fixtures"


def test_build_parser_exposes_documented_flags() -> None:
    """The CLI parser must define paths, ``--check``, and ``--version``."""
    parser = _build_parser()
    actions = {a.dest for a in parser._actions if a.dest != "help"}
    assert actions == {"paths", "check", "version"}


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    """``--version`` prints the package version and exits successfully."""
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == f"nasm-pyfmt {__version__}"
    assert captured.err == ""


def test_stdin_to_stdout(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With no file paths, ``main`` reads stdin and writes formatted text to stdout."""
    raw = (FIXTURES / "hello_syscall.input.asm").read_text(encoding="utf-8")
    expected = (FIXTURES / "hello_syscall.expected.asm").read_text(encoding="utf-8")
    monkeypatch.setattr(sys, "stdin", io.StringIO(raw))
    main([])
    captured = capsys.readouterr()
    assert captured.out == expected
    assert captured.err == ""


def test_format_file_in_place(tmp_path: Path) -> None:
    """Formatting a path rewrites the file when content would change."""
    source = (FIXTURES / "hello_syscall.input.asm").read_text(encoding="utf-8")
    expected = (FIXTURES / "hello_syscall.expected.asm").read_text(encoding="utf-8")
    asm_file = tmp_path / "prog.asm"
    asm_file.write_text(source, encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        main([str(asm_file)])

    assert exc.value.code == 0
    assert asm_file.read_text(encoding="utf-8") == expected


def test_check_exits_nonzero_and_does_not_write(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """``--check`` reports dirty files on stderr and leaves them unchanged."""
    source = (FIXTURES / "hello_syscall.input.asm").read_text(encoding="utf-8")
    asm_file = tmp_path / "prog.asm"
    asm_file.write_text(source, encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        main(["--check", str(asm_file)])

    assert exc.value.code == 1
    assert asm_file.read_text(encoding="utf-8") == source
    captured = capsys.readouterr()
    assert f"Would reformat: {asm_file}" in captured.err


def test_check_exits_zero_when_already_formatted(tmp_path: Path) -> None:
    """``--check`` succeeds when the file already matches formatter output."""
    expected = (FIXTURES / "hello_syscall.expected.asm").read_text(encoding="utf-8")
    asm_file = tmp_path / "prog.asm"
    asm_file.write_text(expected, encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        main(["--check", str(asm_file)])

    assert exc.value.code == 0
    assert asm_file.read_text(encoding="utf-8") == expected


def test_check_multiple_files_sets_exit_code_once(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """``--check`` over several paths fails if any file needs formatting."""
    dirty = (FIXTURES / "hello_syscall.input.asm").read_text(encoding="utf-8")
    clean = (FIXTURES / "hello_syscall.expected.asm").read_text(encoding="utf-8")
    dirty_file = tmp_path / "dirty.asm"
    clean_file = tmp_path / "clean.asm"
    dirty_file.write_text(dirty, encoding="utf-8")
    clean_file.write_text(clean, encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        main(["--check", str(clean_file), str(dirty_file)])

    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert f"Would reformat: {dirty_file}" in captured.err
    assert dirty_file.read_text(encoding="utf-8") == dirty
    assert clean_file.read_text(encoding="utf-8") == clean
