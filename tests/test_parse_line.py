"""Unit tests ported from nasmfmt's parseLine tests."""

import pytest

from nasm_pyfmt.formatter import AsmLine, noquotes, parse_line


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("", AsmLine()),
        (":", AsmLine()),
        (";", AsmLine()),
        ("::;", AsmLine(text=":")),
        ("    label:    ", AsmLine(label="label")),
        (
            "   label:    ;    and a comment    ",
            AsmLine(label="label", comment="and a comment"),
        ),
        (
            "   mov rax, rbx    ;    and a comment    ",
            AsmLine(text="mov rax, rbx", comment="and a comment"),
        ),
        ("   mov rax, rbx    ;      ", AsmLine(text="mov rax, rbx")),
        ("   mov   rax,rbx    ;      ", AsmLine(text="mov rax, rbx")),
        ("   mov   rax,   rbx    ", AsmLine(text="mov rax, rbx")),
        ("   lbl  :mov   rax,   rbx    ", AsmLine(label="lbl", text="mov rax, rbx")),
        ("mov eax, fs:[eax + 0x30]", AsmLine(text="mov eax, fs:[eax + 0x30]")),
        ("lbl db data", AsmLine(label="lbl", text="db data")),
        (" dw   data", AsmLine(text="dw data")),
        ("lbl   dd   data;", AsmLine(label="lbl", text="dd data")),
        ("lbl dq data", AsmLine(label="lbl", text="dq data")),
        ("lbl ddq data", AsmLine(label="lbl", text="ddq data")),
        ("lbl do data", AsmLine(label="lbl", text="do data")),
        ("lbl dt data", AsmLine(label="lbl", text="dt data")),
        ("add data", AsmLine(text="add data")),
        ("lbl: ;:comment", AsmLine(label="lbl", comment=":comment")),
        ("data ;:comment", AsmLine(text="data", comment=":comment")),
        (";fake_lbl:comment", AsmLine(comment="fake_lbl:comment")),
        ('db "not: a label"', AsmLine(text='db "not: a label"')),
        (
            'db ";not a comment" ;real comment ',
            AsmLine(text='db ";not a comment"', comment="real comment"),
        ),
    ],
)
def test_parse_line(source: str, expected: AsmLine) -> None:
    """``parse_line`` must split and normalize lines like nasmfmt's parser."""
    assert parse_line(source) == expected


@pytest.mark.parametrize(
    ("text", "rep", "expected"),
    [
        ("", "x", ""),
        ("normal string", "x", "normal string"),
        ("something 'quoted'", "x", "something xxxxxxxx"),
        ('something "quoted"', "x", "something xxxxxxxx"),
        ('something "quoted" and \'again\'', "x", "something xxxxxxxx and xxxxxxx"),
        ('more "qu\'ot" marks', "x", "more xxxxxxx marks"),
    ],
)
def test_noquotes(text: str, rep: str, expected: str) -> None:
    """``noquotes`` must mask quoted spans for delimiter search tests."""
    assert noquotes(text, rep) == expected
