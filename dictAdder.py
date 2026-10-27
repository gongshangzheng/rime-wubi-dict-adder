"""Append Wubi codes for words to a Rime dictionary.

Usage:
    dictAdder.py WORD [WORD ...] -d DICT
    dictAdder.py --check -d DICT

`--check` audits the whole dictionary instead of adding words: it reports
malformed lines, invalid codes, duplicate words and entries whose code differs
from what pywubi computes, as JSON:

    {"summary": {"lines": 5234, "entries": 5220, "errors": 4, "warnings": 1},
     "findings": [{"line": 29, "word": "怎么", "code": "thtc ",
                   "status": "invalid-code", "reason": "..."}]}

Prints one JSON array on stdout, with one object per word:

    [{"word": "中国", "code": "khlg", "status": "added"}]

`status` is `added`, `exists` or `error` (with a `reason`).  Exit status is 0
when every word was added or already present, 1 when any word failed.  Nothing
is written unless every word validates, so a bad word can never corrupt the
dictionary.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

CODE_RE = re.compile(r"^[a-z]{1,4}$")
WHITESPACE_RE = re.compile(r"\s")


def load_existing(dict_file: str) -> set[str]:
    """Return the set of words already present in DICT_FILE.

    Only `word<TAB>code` lines count; the YAML header, comments and blank lines
    are skipped.
    """
    existing: set[str] = set()
    if not os.path.exists(dict_file):
        return existing
    with open(dict_file, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.rstrip("\n")
            if "\t" not in line or line.startswith("#"):
                continue
            word, _, _code = line.partition("\t")
            existing.add(word)
    return existing


def wubi_code(word: str) -> tuple[str | None, str | None]:
    """Return `(code, None)` for WORD, or `(None, reason)` when it cannot be coded.

    pywubi returns a single code for a recognised word and a per-character list
    for anything it does not recognise as a word (mixed scripts, punctuation,
    whitespace).  Concatenating that list produces invalid Wubi codes, so it is
    rejected instead.
    """
    from pywubi import wubi

    if not word:
        return None, "empty word"
    if WHITESPACE_RE.search(word):
        return None, "contains whitespace"
    codes = wubi(word, single=False)
    if len(codes) != 1:
        return None, "not recognised as a single word (mixed scripts or punctuation?)"
    code = codes[0]
    if not CODE_RE.match(code):
        return None, f"generated code {code!r} is not a valid Wubi code"
    return code, None


def append_entries(dict_file: str, entries: list[tuple[str, str]]) -> None:
    """Append `(word, code)` ENTRIES to DICT_FILE, adding a final newline first."""
    needs_newline = False
    if os.path.exists(dict_file) and os.path.getsize(dict_file) > 0:
        with open(dict_file, "rb") as handle:
            handle.seek(-1, os.SEEK_END)
            needs_newline = handle.read(1) != b"\n"
    with open(dict_file, "a", encoding="utf-8") as handle:
        if needs_newline:
            handle.write("\n")
        for word, code in entries:
            handle.write(f"{word}\t{code}\n")


def process(words: list[str], dict_file: str) -> list[dict]:
    existing = load_existing(dict_file)
    results: list[dict] = []
    pending: list[tuple[str, str]] = []
    for word in words:
        if word in existing:
            results.append({"word": word, "status": "exists"})
            continue
        code, reason = wubi_code(word)
        if code is None:
            results.append({"word": word, "status": "error", "reason": reason})
            continue
        existing.add(word)
        pending.append((word, code))
        results.append({"word": word, "code": code, "status": "added"})

    if pending and not any(result["status"] == "error" for result in results):
        append_entries(dict_file, pending)
    elif pending:
        # Partial validation failure: report nothing as added, nothing written.
        for result in results:
            if result["status"] == "added":
                result["status"] = "error"
                result["reason"] = "not written because another word failed"
                result.pop("code", None)
    return results


ERROR_STATUSES = {"format", "invalid-code", "invalid-weight", "duplicate", "mismatch"}
# "shorter" and "unverifiable" are warnings: a stored code may be a deliberate
# abbreviation (Rime accepts prefixes) and rare glyphs cannot be coded by pywubi.


def check_dict(dict_file: str, report_shorter: bool = False) -> dict:
    """Audit DICT_FILE and return a summary plus findings.

    Codes that are a strict prefix of pywubi's result are legitimate shorthand
    for Rime (it matches by prefix), so they are only reported on request.
    """
    findings: list[dict] = []
    seen: dict[str, int] = {}
    lines_seen = 0
    entries = 0
    in_header = True

    def report(line: int, word: str, code: str, status: str, reason: str,
               suggested: str | None = None) -> None:
        item = {"line": line, "word": word, "code": code, "status": status, "reason": reason}
        if suggested:
            item["suggested"] = suggested
        findings.append(item)

    if not os.path.exists(dict_file):
        return {"summary": {"lines": 0, "entries": 0, "errors": 1, "warnings": 0},
                "findings": [{"line": 0, "word": "", "code": "", "status": "format",
                              "reason": f"dictionary not found: {dict_file}"}]}

    with open(dict_file, "r", encoding="utf-8") as handle:
        lines = handle.read().splitlines()

    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()
        if in_header:
            if stripped.startswith("..."):
                in_header = False
            continue
        if not stripped or stripped.startswith("#") or stripped.startswith("..."):
            continue
        lines_seen += 1
        fields = line.split("\t")
        if len(fields) < 2:
            report(lineno, line, "", "format", "missing TAB separator between word and code")
            continue
        entries += 1
        word, code = fields[0], fields[1]
        weight = fields[2] if len(fields) > 2 else None

        if not CODE_RE.match(code):
            report(lineno, word, code, "invalid-code",
                   "code is not 1-4 lowercase letters")
            continue
        if weight is not None and not weight.isdigit():
            report(lineno, word, code, "invalid-weight",
                   f"weight column is not a number: {weight!r}")

        if word in seen:
            report(lineno, word, code, "duplicate",
                   f"already defined on line {seen[word]}")
        else:
            seen[word] = lineno

        if code.startswith("z"):
            # Rime symbol namespace (e.g. `·` -> za): pywubi cannot verify these.
            continue
        try:
            computed, reason = wubi_code(word)
        except Exception as exc:  # noqa: BLE001
            report(lineno, word, code, "unverifiable", f"{type(exc).__name__}: {exc}")
            continue
        if computed is None:
            report(lineno, word, code, "unverifiable", reason or "pywubi cannot code it")
        elif computed != code and computed.startswith(code):
            if report_shorter:
                report(lineno, word, code, "shorter",
                       f"shorter than pywubi's {computed}", suggested=computed)
        elif computed != code:
            report(lineno, word, code, "mismatch",
                   f"stored {code} but pywubi says {computed}", suggested=computed)

    errors = sum(1 for item in findings if item["status"] in ERROR_STATUSES)
    return {"summary": {"lines": lines_seen, "entries": entries, "errors": errors,
                        "warnings": len(findings) - errors},
            "findings": findings}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Append Wubi codes for words to a Rime dictionary (JSON output)."
    )
    parser.add_argument("words", nargs="*", help="words to code and add")
    parser.add_argument("-d", "--dict", required=True, help="path to the RIME dictionary")
    parser.add_argument("--check", action="store_true",
                        help="audit the whole dictionary instead of adding words")
    parser.add_argument("--report-shorter", action="store_true",
                        help="also report codes that are a prefix of pywubi's code "
                             "(legitimate shorthand for Rime, off by default)")
    args = parser.parse_args(argv)

    dict_file = os.path.expanduser(args.dict)

    if args.check:
        try:
            result = check_dict(dict_file, report_shorter=args.report_shorter)
        except Exception as exc:  # noqa: BLE001
            print(json.dumps({"summary": {"lines": 0, "entries": 0, "errors": 1, "warnings": 0},
                              "findings": [{"line": 0, "word": "", "code": "",
                                            "status": "format",
                                            "reason": f"{type(exc).__name__}: {exc}"}]},
                             ensure_ascii=False))
            print(f"dictAdder.py: {type(exc).__name__}: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(result, ensure_ascii=False))
        return 1 if result["summary"]["errors"] else 0

    if not args.words:
        parser.error("at least one word is required (or use --check)")
    try:
        results = process(args.words, dict_file)
    except Exception as exc:  # noqa: BLE001 - report instead of a bare traceback
        results = [
            {"word": word, "status": "error", "reason": f"{type(exc).__name__}: {exc}"}
            for word in args.words
        ]
        print(json.dumps(results, ensure_ascii=False))
        print(f"dictAdder.py: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(results, ensure_ascii=False))
    return 1 if any(result["status"] == "error" for result in results) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
