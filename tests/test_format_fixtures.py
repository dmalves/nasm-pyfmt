"""Compare formatter output against golden files (nasmfmt-style)."""

from pathlib import Path

import pytest

from nasm_pyfmt.formatter import format_source

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _fixture_cases() -> list[tuple[str, Path, Path]]:
    """Collect paired ``*.input.asm`` and ``*.expected.asm`` fixture paths.

    Returns:
        List of ``(case_name, input_path, expected_path)`` tuples sorted by name.

    Raises:
        pytest.Failed: If an input file has no matching expected file.
    """
    cases: list[tuple[str, Path, Path]] = []
    for input_path in sorted(FIXTURES_DIR.glob("*.input.asm")):
        stem = input_path.name.removesuffix(".input.asm")
        expected_path = FIXTURES_DIR / f"{stem}.expected.asm"
        if not expected_path.is_file():
            pytest.fail(f"Missing expected fixture for {input_path.name}")
        cases.append((stem, input_path, expected_path))
    return cases


_FORMAT_CASES = _fixture_cases()


@pytest.mark.parametrize(
    ("name", "input_path", "expected_path"),
    _FORMAT_CASES,
    ids=[case[0] for case in _FORMAT_CASES],
)
def test_format_matches_expected(
    name: str,
    input_path: Path,
    expected_path: Path,
) -> None:
    """Formatting a fixture input must exactly match its golden expected file."""
    source = input_path.read_text(encoding="utf-8")
    expected = expected_path.read_text(encoding="utf-8")
    assert format_source(source) == expected
