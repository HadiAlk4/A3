#!/usr/bin/env python3
"""Count words in the PEP from A3.tex and the section files it inputs.

Excludes the title page, appendix, bibliography, front-matter lists
(TOC / LOF / LOT), itemize/enumerate/description lists, and figures.
Prints one total that still includes table text, and one that does not.

Usage (from repo root):
    python3 scripts/word_count.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "A3.tex"

SECTION_INPUTS = [
    "sections/01_exec",
    "sections/02_overview",
    "sections/03_schedule",
    "sections/04_cost",
    "sections/05_resource",
    "sections/06_risk",
    "sections/07_delivery",
]

ALWAYS_DROP_ENVS = (
    "titlepage",
    "thebibliography",
    "itemize",
    "enumerate",
    "description",
    "figure",
    "tikzpicture",
    "equation",
    "align",
    "align*",
)

TABLE_ENVS = ("table", "table*", "longtable", "tabularx", "tabular", "tabular*")

DROP_COMMANDS = {
    "label",
    "ref",
    "pageref",
    "eqref",
    "cite",
    "citep",
    "citet",
    "citealp",
    "citeyear",
    "citeauthor",
    "includegraphics",
    "resizebox",
    "hspace",
    "vspace",
    "vspace*",
    "setlength",
    "addtolength",
    "setcounter",
    "hypersetup",
    "thispagestyle",
    "pagestyle",
    "addcontentsline",
    "phantomsection",
    "graphicspath",
    "renewcommand",
    "providecommand",
    "newcommand",
    "tableofcontents",
    "listoffigures",
    "listoftables",
    "centering",
    "raggedright",
    "raggedleft",
    "noindent",
    "newpage",
    "clearpage",
    "cleardoublepage",
    "vfill",
    "hfill",
    "emptysec",
    "xspace",
    "toprule",
    "midrule",
    "bottomrule",
    "endhead",
    "endfirsthead",
    "endfoot",
    "endlastfoot",
    "multicolumn",
    "numberwithin",
    "captionsetup",
    "onehalfspacing",
    "singlespacing",
    "arraystretch",
    "tabcolsep",
    "linewidth",
    "textwidth",
    "protect",
}

KEEP_ARG_COMMANDS = {
    "textbf",
    "textit",
    "emph",
    "textrm",
    "textsf",
    "texttt",
    "textsc",
    "textsl",
    "underline",
    "mbox",
    "text",
    "textrm",
    "caption",
    "section",
    "subsection",
    "subsubsection",
    "paragraph",
    "textbf",
    "textit",
    "textrm",
    "small",
    "footnotesize",
    "scriptsize",
    "tiny",
    "large",
    "Large",
    "LARGE",
    "huge",
    "Huge",
    "centering",
}


def strip_comments(text: str) -> str:
    out: list[str] = []
    for line in text.splitlines(True):
        buf: list[str] = []
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == "%" and (i == 0 or line[i - 1] != "\\"):
                buf.append("\n")
                break
            buf.append(ch)
            i += 1
        out.append("".join(buf))
    return "".join(out)


def skip_optional(text: str, i: int) -> int:
    while i < len(text) and text[i].isspace():
        i += 1
    while i < len(text) and text[i] == "[":
        depth = 1
        i += 1
        while i < len(text) and depth:
            if text[i] == "\\" and i + 1 < len(text):
                i += 2
                continue
            if text[i] == "[":
                depth += 1
            elif text[i] == "]":
                depth -= 1
            i += 1
        while i < len(text) and text[i].isspace():
            i += 1
    return i


def skip_star(text: str, i: int) -> int:
    if i < len(text) and text[i] == "*":
        return i + 1
    return i


def consume_group(text: str, i: int) -> tuple[str, int] | None:
    while i < len(text) and text[i].isspace():
        i += 1
    if i >= len(text) or text[i] != "{":
        return None
    depth = 0
    start = i + 1
    j = i
    while j < len(text):
        ch = text[j]
        if ch == "\\" and j + 1 < len(text):
            j += 2
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:j], j + 1
        j += 1
    return None


def resolve_tex(path_str: str) -> Path:
    p = Path(path_str)
    if not p.is_absolute():
        p = ROOT / p
    if p.suffix != ".tex":
        p = p.with_suffix(".tex")
    return p


def expand_inputs(text: str) -> str:
    pattern = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")

    def repl(m: re.Match[str]) -> str:
        path = resolve_tex(m.group(1).strip())
        if not path.exists():
            return ""
        return expand_inputs(strip_comments(path.read_text(encoding="utf-8")))

    return pattern.sub(repl, text)


def env_spans(text: str, name: str) -> list[tuple[int, int]]:
    begin_re = re.compile(r"\\begin\{" + re.escape(name) + r"\}")
    begin_lit = "\\begin{" + name + "}"
    end_lit = "\\end{" + name + "}"
    spans: list[tuple[int, int]] = []
    i = 0
    while True:
        m = begin_re.search(text, i)
        if not m:
            break
        start = m.start()
        pos = m.end()
        depth = 1
        while depth:
            b = text.find(begin_lit, pos)
            e = text.find(end_lit, pos)
            if e == -1:
                spans.append((start, len(text)))
                return spans
            if b != -1 and b < e:
                depth += 1
                pos = b + len(begin_lit)
            else:
                depth -= 1
                pos = e + len(end_lit)
        spans.append((start, pos))
        i = pos
    return spans


def remove_envs(text: str, names: tuple[str, ...]) -> str:
    for name in names:
        spans = env_spans(text, name)
        for a, b in reversed(spans):
            text = text[:a] + "\n" + text[b:]
    return text


def slice_document(text: str) -> str:
    m = re.search(r"\\begin\{document\}", text)
    if m:
        text = text[m.end() :]
    text = re.split(r"\\end\{document\}", text, maxsplit=1)[0]
    text = re.split(r"\\appendix\b", text, maxsplit=1)[0]
    return text


def parse_newcommands(text: str) -> tuple[str, dict[str, str]]:
    macros: dict[str, str] = {}
    out: list[str] = []
    i = 0
    while i < len(text):
        if text.startswith("\\newcommand", i) or text.startswith("\\renewcommand", i):
            j = i + (11 if text.startswith("\\newcommand", i) else 13)
            j = skip_star(text, j)
            grabbed = consume_group(text, j)
            if grabbed is None:
                out.append(text[i])
                i += 1
                continue
            name_raw, j = grabbed
            name = name_raw.strip().lstrip("\\")
            j = skip_optional(text, j)
            j = skip_optional(text, j)
            body = consume_group(text, j)
            if body is None:
                out.append(text[i])
                i += 1
                continue
            macros[name] = body[0]
            i = body[1]
            out.append(" ")
            continue
        out.append(text[i])
        i += 1
    return "".join(out), macros


def expand_macros(text: str, macros: dict[str, str]) -> str:
    if not macros:
        return text
    names = sorted(macros, key=len, reverse=True)
    pattern = re.compile(r"\\(" + "|".join(re.escape(n) for n in names) + r")\*?\s*(\{\})?")
    for _ in range(12):
        nxt = pattern.sub(lambda m: macros[m.group(1)], text)
        if nxt == text:
            break
        text = nxt
    return text


def drop_command_calls(text: str, names: set[str]) -> str:
    ordered = sorted(names, key=len, reverse=True)
    pattern = re.compile(r"\\(" + "|".join(re.escape(n) for n in ordered) + r")\*?")
    out: list[str] = []
    i = 0
    while i < len(text):
        m = pattern.match(text, i)
        if not m:
            out.append(text[i])
            i += 1
            continue
        i = m.end()
        i = skip_optional(text, i)
        while True:
            grabbed = consume_group(text, i)
            if grabbed is None:
                break
            i = grabbed[1]
        out.append(" ")
    return "".join(out)


def keep_command_args(text: str, names: set[str]) -> str:
    ordered = sorted(names, key=len, reverse=True)
    pattern = re.compile(r"\\(" + "|".join(re.escape(n) for n in ordered) + r")\*?")
    out: list[str] = []
    i = 0
    while i < len(text):
        m = pattern.match(text, i)
        if not m:
            out.append(text[i])
            i += 1
            continue
        i = m.end()
        i = skip_optional(text, i)
        args: list[str] = []
        while True:
            grabbed = consume_group(text, i)
            if grabbed is None:
                break
            args.append(grabbed[0])
            i = grabbed[1]
        if args:
            out.append(" " + args[-1] + " ")
        else:
            out.append(" ")
    return "".join(out)


def drop_remaining_commands(text: str) -> str:
    out: list[str] = []
    i = 0
    while i < len(text):
        if text[i] == "\\" and i + 1 < len(text):
            nxt = text[i + 1]
            if nxt.isalpha():
                j = i + 2
                while j < len(text) and text[j].isalpha():
                    j += 1
                if j < len(text) and text[j] == "*":
                    j += 1
                j = skip_optional(text, j)
                while True:
                    grabbed = consume_group(text, j)
                    if grabbed is None:
                        break
                    j = grabbed[1]
                out.append(" ")
                i = j
                continue
            out.append(" ")
            i += 2
            continue
        out.append(text[i])
        i += 1
    return "".join(out)


def to_plain(text: str, *, drop_tables: bool) -> str:
    text = strip_comments(text)
    text = expand_inputs(text)
    text = slice_document(text)
    text = remove_envs(text, ALWAYS_DROP_ENVS)
    if drop_tables:
        text = remove_envs(text, TABLE_ENVS)
    text, macros = parse_newcommands(text)
    text = expand_macros(text, macros)
    text = keep_command_args(text, KEEP_ARG_COMMANDS)
    text = drop_command_calls(text, DROP_COMMANDS)
    text = drop_remaining_commands(text)
    text = text.replace("~", " ")
    text = text.replace("&", " ")
    text = text.replace("$", " ")
    text = text.replace("{", " ")
    text = text.replace("}", " ")
    text = text.replace("\\", " ")
    text = text.replace("---", " ")
    text = text.replace("--", " ")
    text = text.replace("_", " ")
    text = text.replace("^", " ")
    text = re.sub(r"[#&%]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def count_words(plain: str) -> int:
    if not plain:
        return 0
    return sum(1 for tok in plain.split() if re.search(r"[A-Za-z0-9]", tok))


def section_source(rel: str) -> str:
    path = resolve_tex(rel)
    body = path.read_text(encoding="utf-8")
    return "\\begin{document}\n" + body + "\n\\end{document}\n"


def main() -> None:
    main_src = MAIN.read_text(encoding="utf-8")
    with_tables = count_words(to_plain(main_src, drop_tables=False))
    without_tables = count_words(to_plain(main_src, drop_tables=True))

    print("Word count from A3.tex + inputted section .tex files")
    print("Excluded: title page, appendix, references, TOC/LOF/LOT,")
    print("          itemize/enumerate lists, figures, display maths")
    print()
    print(f"  With tables:     {with_tables:,}")
    print(f"  Without tables:  {without_tables:,}")
    print()
    print("By section")
    print(f"  {'section':<24} {'with tables':>12} {'without tables':>16}")
    print("  " + "-" * 54)

    sum_with = sum_without = 0
    for rel in SECTION_INPUTS:
        src = section_source(rel)
        w = count_words(to_plain(src, drop_tables=False))
        wo = count_words(to_plain(src, drop_tables=True))
        sum_with += w
        sum_without += wo
        print(f"  {rel:<24} {w:>12,} {wo:>16,}")

    print("  " + "-" * 54)
    print(f"  {'section sum':<24} {sum_with:>12,} {sum_without:>16,}")
    print()
    print("Title-page target is 6,000 ± 10% (5,400–6,600), stated as 6,450")
    print("excluding references, appendices, tables and figures.")
    band = "inside" if 5400 <= without_tables <= 6600 else "outside"
    print(f"Without-tables count is {band} that band.")


if __name__ == "__main__":
    main()
