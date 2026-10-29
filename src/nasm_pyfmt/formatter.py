"""NASM source formatter (behavior aligned with nasmfmt)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from io import StringIO

DEFAULT_INSTRUCTION_INDENT = 8
DEFAULT_COMMENT_INDENT = 40

_MUL_SPACES = re.compile(r"\s+")
_COMMA_SPACES = re.compile(r",\s*")
_DATA_PSEUDO_RES = [
    re.compile(rf"(?:\s|^){pseudo}(?:\s|\")")
    for pseudo in ("db", "dw", "dd", "dq", "ddq", "do", "dt")
]
_LABEL_HAS_SPACE = re.compile(r"\S*\s+\S*")


@dataclass
class AsmLine:
    """One logical line of assembly after parsing.

    Attributes:
        label: Symbol before ``:`` or before a data pseudo-instruction.
        text: Instruction, directive, or data remainder on the line.
        comment: Text after ``;``, without the semicolon.
    """

    label: str = ""
    text: str = ""
    comment: str = ""

    def empty(self) -> bool:
        """Return whether the line has no label, text, or comment."""
        return not self.label and not self.text and not self.comment


def _index_rune_any(s: str, chars: str) -> int:
    """Return the index of the first character from ``chars`` in ``s``, or -1."""
    for i, ch in enumerate(s):
        if ch in chars:
            return i
    return -1


def noquotes(s: str, rep: str) -> str:
    """Replace quoted regions so substring searches ignore string contents.

    Each single- or double-quoted span (including delimiters) is replaced by
    repeating ``rep`` once per rune in that span. Unpaired quotes are copied
    literally. Useful to find ``:`` or ``;`` outside strings.

    Args:
        s: Input text, typically one assembly source line.
        rep: Replacement rune(s) repeated over each quoted region.

    Returns:
        A copy of ``s`` with quoted sections substituted.
    """
    sr = list(s)
    repr_chars = list(rep)
    out: list[str] = []

    while sr:
        ind = _index_rune_any("".join(sr), "\"'")
        if ind >= 0:
            quote = sr[ind]
            rest = sr[ind + 1 :]
            ind2 = ind + 1
            for j, ch in enumerate(rest):
                if ch == quote:
                    ind2 = ind + 1 + j
                    break
            else:
                out.extend(sr[: ind + 1])
                sr = sr[ind + 1 :]
                continue
            out.extend(sr[:ind])
            out.extend(repr_chars * (ind2 - ind + 1))
            sr = sr[ind2 + 1 :]
        else:
            out.extend(sr)
            break

    return "".join(out)


def _parse_label(line: str) -> tuple[str, str]:
    """Split ``line`` into a label prefix and the remaining text.

    Detects labels at ``:`` (outside quotes) and before NASM data pseudos
    (``db``, ``dw``, etc.). Rejects labels that contain internal whitespace.

    Args:
        line: Source fragment with comment already removed.

    Returns:
        ``(label, rest)`` where ``label`` may be empty.
    """
    lbl = ""
    rest = line
    noq = noquotes(line, "x")

    ind = noq.find(":")
    if ind >= 0:
        lbl = line[:ind].strip()
        rest = line[ind + 1 :]

    for pseudo in _DATA_PSEUDO_RES:
        match = pseudo.search(noq)
        if match:
            ind = match.start()
            lbl = line[:ind].strip()
            rest = line[ind:]

    if _LABEL_HAS_SPACE.match(lbl):
        lbl, rest = "", line

    return lbl, rest


def _parse_comment(line: str) -> tuple[str, str]:
    """Split ``line`` at the first ``;`` outside quoted strings.

    Args:
        line: Raw source line.

    Returns:
        ``(comment, rest)`` with comment text stripped of surrounding space.
    """
    noq = noquotes(line, "x")
    ind = noq.find(";")
    if ind >= 0:
        return line[ind + 1 :].strip(), line[:ind]
    return "", line


def parse_line(line: str) -> AsmLine:
    """Parse one assembly source line into structured fields.

    Normalizes horizontal whitespace in the instruction text and spacing
    after commas.

    Args:
        line: Raw line without trailing newline.

    Returns:
        Parsed ``AsmLine`` with label, text, and comment components.
    """
    comment, line = _parse_comment(line)
    label, line = _parse_label(line)
    text = line.strip()
    text = _MUL_SPACES.sub(" ", text)
    text = _COMMA_SPACES.sub(", ", text)
    return AsmLine(label=label, text=text, comment=comment)


def _print_line(
    out: StringIO,
    asm_line: AsmLine,
    *,
    instruction_indent: int,
    comment_indent: int,
) -> None:
    """Write one formatted assembly line to ``out``.

    Labels are emitted with a trailing colon; instructions start on the next
    line when both label and text are present. Comments align near
    ``comment_indent`` when they share a line with code.

    Args:
        out: Buffer receiving formatted output.
        asm_line: Parsed line to render.
        instruction_indent: Leading spaces before instruction text.
        comment_indent: Target column for inline comments.
    """
    column = 0

    if asm_line.label:
        out.write(asm_line.label)
        out.write(":")
        column += len(asm_line.label) + 1
        if asm_line.text:
            out.write("\n")
            column = 0

    if asm_line.text:
        out.write(" " * instruction_indent)
        out.write(asm_line.text)
        column += instruction_indent + len(asm_line.text)

    if asm_line.comment:
        if column != 0:
            if column < comment_indent - 1:
                out.write(" " * (comment_indent - column - 1))
            else:
                out.write(" ")
        out.write("; ")
        out.write(asm_line.comment)

    out.write("\n")


def format_source(
    source: str,
    *,
    instruction_indent: int = DEFAULT_INSTRUCTION_INDENT,
    comment_indent: int = DEFAULT_COMMENT_INDENT,
) -> str:
    """Format NASM assembly source text.

    Behavior matches `nasmfmt` defaults: instruction indent, comment column,
    and at most one consecutive blank line.

    Args:
        source: Full assembly file contents.
        instruction_indent: Spaces before each instruction line.
        comment_indent: Target column for trailing comments.

    Returns:
        Formatted source, including a trailing newline on each output line.
    """
    out = StringIO()
    last_empty = False

    for raw_line in source.splitlines():
        asm_line = parse_line(raw_line)
        if last_empty and asm_line.empty():
            continue
        _print_line(
            out,
            asm_line,
            instruction_indent=instruction_indent,
            comment_indent=comment_indent,
        )
        last_empty = asm_line.empty()

    return out.getvalue()
