# nasm-pyfmt

Opinionated formatter for [NASM](https://www.nasm.us/) assembly source code.

Formatting rules follow [nasmfmt](https://github.com/yamnikov-oleg/nasmfmt) (default instruction indent 8, comment column 40).

## Requirements

- [uv](https://docs.astral.sh/uv/)
- Python 3.14 (pinned in `.python-version`; managed by uv)

## Setup

```bash
uv sync --dev
```

## Usage

```bash
uv run nasm-pyfmt --help
uv run nasm-pyfmt path/to/file.asm
echo 'section .text' | uv run nasm-pyfmt
```

## Development

```bash
uv run pytest
uv run ruff check src tests
```

## Project layout

```
src/nasm_pyfmt/   # package source
  cli.py          # CLI entry point
  formatter.py    # formatting implementation (stub)
tests/
  fixtures/       # *.input.asm (messy) vs *.expected.asm (golden)
```

Golden expected files match nasmfmt output; regenerate with Go installed:

```bash
go run github.com/yamnikov-oleg/nasmfmt@latest path/to/file.asm
```
