#!/usr/bin/env python3
"""Advisory checker for a markdown cost ledger.

It reads every markdown table in a project file, sums columns whose header looks like a price,
and flags rows that are suspiciously far from the column median (a common symptom of Rial
entered as Toman, or a per-pack price entered as a per-unit price).

It never edits the file and never decides for the user. It only points at rows worth checking.

Usage:
    python ledger_check.py <project.md> [--json]

Exit code is 0 even when warnings are found; treat the output as advice.
"""

from __future__ import annotations

import json
import re
import statistics
import sys
from pathlib import Path
from typing import Any

PERSIAN = "۰۱۲۳۴۵۶۷۸۹"
ARABIC = "٠١٢٣٤٥٦٧٨٩"
TRANS = str.maketrans(PERSIAN + ARABIC, "0123456789" * 2)

PRICE_KEYS = ("قیمت", "price", "total", "cost", "مبلغ", "تومان", "جمع")
SUMMARY_KEYS = ("جمع", "total", "subtotal", "اصلاح", "سهم")
MISSING_MARKERS = {"", "-", "—", "⬜", "✅", "🛒", "?"}
NUMBER_RE = re.compile(r"^-?\d+(?:\.\d+)?$")
DATE_RE = re.compile(r"^\d{4}/\d{1,2}/\d{1,2}$")


def norm(text: str) -> str:
    return text.translate(TRANS)


def clean_cell(cell: str) -> str:
    s = cell.strip()
    s = s.replace("**", "").replace("`", "").strip()
    return s


def parse_number(cell: str) -> float | None:
    s = norm(cell).strip()
    s = s.replace(",", "").replace("٬", "").replace(" ", "")
    for token in ("~", "≈", "تومان", "تومن", "%"):
        s = s.replace(token, "")
    if s in MISSING_MARKERS or not s:
        return None
    if DATE_RE.fullmatch(s):
        return None
    if NUMBER_RE.fullmatch(s):
        try:
            return float(s)
        except ValueError:
            return None
    return None


def split_row(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [clean_cell(c) for c in body.split("|")]


def is_separator(line: str) -> bool:
    body = line.replace("|", "").strip()
    return bool(body) and all(c in "-: " for c in body)


def parse_tables(lines: list[str]) -> list[dict[str, Any]]:
    tables = []
    i = 0
    while i < len(lines):
        if not lines[i].lstrip().startswith("|"):
            i += 1
            continue
        start = i
        block = []
        while i < len(lines) and lines[i].lstrip().startswith("|"):
            block.append(lines[i])
            i += 1
        if len(block) < 3 or not is_separator(block[1]):
            continue
        header = split_row(block[0])
        rows = []
        for line in block[2:]:
            if is_separator(line):
                continue
            cells = split_row(line)
            if any(cells):
                rows.append(cells)
        tables.append({"start_line": start + 1, "header": header, "rows": rows})
    return tables


def is_price_header(header: str) -> bool:
    h = norm(header).lower()
    return any(k in h for k in PRICE_KEYS)


def is_summary_header(header: str) -> bool:
    h = norm(header).lower()
    return any(k in h for k in SUMMARY_KEYS)


def is_summary_row(row: list[str]) -> bool:
    joined = " ".join(row).lower()
    return any(k in joined for k in ("جمع", "مجموع", "total", "subtotal"))


def item_label(row: list[str], header: list[str]) -> str:
    """Pick the human-readable name, not the row-number column."""
    for i, title in enumerate(header):
        h = norm(title).lower()
        if any(k in h for k in ("قلم", "item", "name", "آیتم", "شرح", "دسته")):
            if i < len(row) and row[i]:
                return row[i]
    for cell in row:
        if cell and parse_number(cell) is None and not cell.isdigit():
            return cell
    return ""


def analyse_table(table: dict[str, Any]) -> dict[str, Any]:
    header = table["header"]
    all_rows = table["rows"]
    # A "جمع ..." row repeats a number that is already in the rows above it. Including it in a
    # column sum double-counts the whole table, which is exactly the kind of silent error this
    # checker exists to catch.
    data_rows = [(i, row) for i, row in enumerate(all_rows, start=1) if not is_summary_row(row)]
    if not data_rows:
        return {
            "start_line": table["start_line"],
            "header": header,
            "columns": [],
            "summary_only": True,
        }

    columns = []
    for idx, title in enumerate(header):
        if not title or not is_price_header(title):
            continue
        values = []
        for r, row in data_rows:
            if idx >= len(row):
                continue
            value = parse_number(row[idx])
            if value is not None:
                values.append((r, value, item_label(row, header)))
        if not values:
            continue

        numbers = [v for _, v, _ in values]
        median = statistics.median(numbers)
        total = sum(numbers)
        outliers = []
        if median > 0:
            for r, value, item in values:
                ratio = value / median if median else 0
                if value > 0 and (ratio >= 5 or ratio <= 0.1):
                    outliers.append(
                        {
                            "row": r,
                            "value": value,
                            "ratio": round(ratio, 2),
                            "item": item,
                        }
                    )

        missing_unit = None
        if "واحد" in norm(title) or "unit" in norm(title).lower():
            missing = []
            for r, row in data_rows:
                if idx >= len(row):
                    continue
                if parse_number(row[idx]) is None:
                    # Only flag when another price column on the same row has a value.
                    others = [
                        parse_number(row[j])
                        for j, t in enumerate(header)
                        if j != idx and is_price_header(t) and j < len(row)
                    ]
                    if any(v is not None and v > 0 for v in others):
                        missing.append((r, item_label(row, header)))
            if missing:
                missing_unit = missing

        columns.append(
            {
                "header": title,
                "count": len(values),
                "sum": total,
                "median": median,
                "outliers": outliers,
                "missing_unit_rows": missing_unit,
                "summary_like": is_summary_header(title),
            }
        )
    if columns and all(c["summary_like"] for c in columns):
        # A table whose every price column is already an aggregate (جمع / اصلاحشده) would
        # double-count itself; report it as a summary table and leave it out of the checks.
        return {
            "start_line": table["start_line"],
            "header": header,
            "columns": [],
            "summary_only": True,
        }
    return {
        "start_line": table["start_line"],
        "header": header,
        "columns": columns,
        "summary_only": False,
    }


def fmt(n: float) -> str:
    if abs(n - round(n)) < 1e-9:
        return f"{int(round(n)):,}"
    return f"{n:,.2f}"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    if not args:
        print("usage: python ledger_check.py <project.md> [--json]", file=sys.stderr)
        return 2

    path = Path(args[0])
    if not path.exists():
        print(f"file not found: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    tables = parse_tables(text.splitlines())
    analyses = [analyse_table(t) for t in tables]
    analyses = [a for a in analyses if a["columns"]]

    # The same row is checked once per price column (unit + total). Count it once.
    flagged = set()
    for a in analyses:
        for c in a["columns"]:
            for o in c["outliers"]:
                flagged.add((a["start_line"], o["row"], "outlier"))
            for r, _ in c["missing_unit_rows"] or []:
                flagged.add((a["start_line"], r, "missing_unit"))
    warnings = len(flagged)

    if as_json:
        payload = {
            "file": str(path),
            "tables": analyses,
            "warning_count": warnings,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(f"Ledger check — {path}")
    print(f"Tables with price columns: {len(analyses)}")
    print()

    for a in analyses:
        print(f"Table at line {a['start_line']}: {' | '.join(a['header'][:6])}")
        for c in a["columns"]:
            tag = " [summary-like]" if c["summary_like"] else ""
            print(
                f"  {c['header']}{tag}: {c['count']} values · "
                f"sum {fmt(c['sum'])} · median {fmt(c['median'])}"
            )
            for o in c["outliers"]:
                print(
                    f"    ⚠️ row {o['row']}: {fmt(o['value'])} is {o['ratio']}× median "
                    f"({o['item']}) — check Rial/Toman or pack vs unit"
                )
            if c["missing_unit_rows"]:
                rows = ", ".join(f"{r} ({item})" for r, item in c["missing_unit_rows"])
                print(f"    ⚠️ missing unit price on row(s): {rows}")
        print()

    if warnings:
        print(f"Warnings: {warnings}. Nothing was changed — confirm each row against its invoice.")
    else:
        print("No obvious outliers. Totals still need to match their rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
