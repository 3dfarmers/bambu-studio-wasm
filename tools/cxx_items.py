"""Split a C++ source file into top-level items (function definitions and the rest).

Good enough for Bambu Studio's GUI sources: it understands comments, string and
character literals (including raw strings) and brace nesting, and treats a
namespace block as transparent so the functions inside it become items.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Item:
    kind: str        # "func", "other"
    name: str        # qualified function name, e.g. "PartPlate::get_origin"
    text: str


def _skip_literal(src: str, i: int) -> int:
    """i points at a quote; return the index after the literal."""
    if src[i] == '"' and i > 0 and src[i - 1] == 'R':
        m = re.match(r'R"([^(\s]*)\(', src[i - 1:])
        if m:
            end = src.index(')' + m.group(1) + '"', i)
            return end + len(m.group(1)) + 2
    q = src[i]
    i += 1
    while i < len(src):
        c = src[i]
        if c == '\\':
            i += 2
            continue
        if c == q:
            return i + 1
        i += 1
    return i


def _scan(src: str, i: int, stop_at_top_semicolon: bool) -> int:
    """From i, scan until the braces opened after i are balanced again.
    Returns the index after the closing brace (or after a top-level ';' when
    no brace was opened and stop_at_top_semicolon is set)."""
    depth = 0
    opened = False
    paren = 0
    n = len(src)
    while i < n:
        c = src[i]
        if src.startswith('//', i):
            i = src.find('\n', i)
            if i < 0:
                return n
            continue
        if src.startswith('/*', i):
            i = src.find('*/', i) + 2
            continue
        if c in '"\'':
            # a digit separator like 1'000 is not a char literal
            if c == "'" and i > 0 and src[i - 1].isalnum() and i + 1 < n and src[i + 1].isalnum() and src[i + 2:i + 3] != "'":
                i += 1
                continue
            i = _skip_literal(src, i)
            continue
        if c == '(':
            paren += 1
        elif c == ')':
            paren -= 1
        elif c == '{':
            depth += 1
            opened = True
        elif c == '}':
            depth -= 1
            if opened and depth == 0:
                return i + 1
        elif c == ';' and depth == 0 and paren == 0 and stop_at_top_semicolon:
            return i + 1
        i += 1
    return n


_NS = re.compile(r'\s*(inline\s+)?namespace(\s+[A-Za-z_][\w:]*)?\s*\{')


def split(src: str) -> list[Item]:
    items: list[Item] = []
    i = 0
    n = len(src)
    buf_start = 0

    def flush(upto: int):
        nonlocal buf_start
        if upto > buf_start:
            items.append(Item("other", "", src[buf_start:upto]))
        buf_start = upto

    while i < n:
        # skip whitespace
        if src[i].isspace():
            i += 1
            continue
        if src.startswith('//', i):
            i = src.find('\n', i)
            i = n if i < 0 else i
            continue
        if src.startswith('/*', i):
            i = src.find('*/', i) + 2
            continue
        if src[i] == '#':
            # preprocessor line (with continuations)
            while True:
                j = src.find('\n', i)
                if j < 0:
                    i = n
                    break
                if src[j - 1] == '\\':
                    i = j + 1
                    continue
                i = j + 1
                break
            continue
        m = _NS.match(src, i)
        if m:
            i = m.end()
            continue
        if src[i] == '}':
            # closing a namespace
            i += 1
            continue
        # a declaration or definition starts here
        start = i
        end = _scan(src, i, stop_at_top_semicolon=True)
        chunk = src[start:end]
        head = chunk.split('{', 1)[0]
        is_func = '{' in chunk and '(' in head and not re.match(r'\s*(class|struct|enum|union|typedef|using)\b', head) \
            and not re.search(r'=\s*$', head.strip()) and not re.search(r'=\s*[^=(]*$', head.split('(')[0])
        if is_func:
            pre = head.split('(')[0]
            m2 = re.search(r'(~?[A-Za-z_][\w]*(?:\s*::\s*~?[A-Za-z_]\w*)*|operator\s*\S+)\s*$', pre)
            name = re.sub(r'\s+', '', m2.group(1)) if m2 else pre.strip()
            # include leading comments/whitespace that belong to the function
            flush(start)
            items.append(Item("func", name, src[start:end]))
            buf_start = end
        i = end
    flush(n)
    return items
