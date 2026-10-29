"""Tests for high-level formatting behavior."""

from pathlib import Path

from nasm_pyfmt.formatter import format_source


def test_format_source_idempotent_on_hello_fixture() -> None:
    """Already formatted hello-world fixture must be unchanged by ``format_source``."""
    expected = (
        Path(__file__).parent / "fixtures" / "hello_syscall.expected.asm"
    ).read_text(encoding="utf-8")
    assert format_source(expected) == expected
