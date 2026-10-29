# nasm-pyfmt

![A cute chip mascot lining up NASM assembly](docs/nasm-pyfmt-banner.jpg)

Opinionated formatter for [NASM](https://www.nasm.us/) assembly source code.

Instructions are indented 8 columns, and comments line up at column 40.

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

## Releases (standalone binaries)

Published [GitHub Releases](https://github.com/dmalves/nasm-pyfmt/releases) include executables built with PyInstaller:

| Asset | Platform |
|-------|----------|
| `nasm-pyfmt-linux-x86_64` | Linux x86_64 (glibc, built on `ubuntu-latest`) |
| `nasm-pyfmt-windows-x86_64.exe` | Windows x86_64 |

### Publish a new release

1. Bump `version` in [`pyproject.toml`](pyproject.toml) and [`src/nasm_pyfmt/__init__.py`](src/nasm_pyfmt/__init__.py) if needed.
2. Commit, tag, and push (tag must match version, e.g. `v0.1.0` for `0.1.0`):

   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

3. On GitHub: **Releases → Draft a new release** → select the tag → **Publish release**.
4. The [Release workflow](.github/workflows/release.yml) builds both binaries and attaches them to that release.

You can also run the release workflow manually (**Actions → Release → Run workflow**) to verify builds; assets are uploaded to GitHub only when a release is **published**.

### Run the binary

```bash
chmod +x nasm-pyfmt-linux-x86_64
./nasm-pyfmt-linux-x86_64 path/to/file.asm
```

```powershell
.\nasm-pyfmt-windows-x86_64.exe path\to\file.asm
```

## Development

```bash
uv run pytest
uv run ruff check src tests
```

### Local executable build

```bash
uv sync --group build
uv run pyinstaller nasm-pyfmt.spec --clean --noconfirm
./dist/nasm-pyfmt --version
```

## Project layout

```
src/nasm_pyfmt/   # package source
  cli.py          # CLI entry point
  formatter.py    # formatting implementation
tests/
  fixtures/       # *.input.asm (messy) vs *.expected.asm (golden)
.github/workflows/
  ci.yml          # lint and tests
  release.yml     # PyInstaller builds on release
```

Golden files in `tests/fixtures/` are the canonical formatted output (`*.input.asm` is the messy source, `*.expected.asm` is the formatted result).
