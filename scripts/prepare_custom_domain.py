#!/usr/bin/env python3
"""Normalize the generated public mirror for the production custom domain."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_SITE = ROOT / "public" / "giasubinhminh.com"
CUSTOM_ORIGIN = "https://www.giasusuphamtriviet.vn"
TEXT_SUFFIXES = {".css", ".html", ".js", ".json", ".txt", ".xml"}

PLAIN_ORIGINS = (
    "https://giasutriviet.vercel.app/giasubinhminh.com",
    "http://giasutriviet.vercel.app/giasubinhminh.com",
    "https://www.giasubinhminh.com",
    "http://www.giasubinhminh.com",
    "https://giasubinhminh.com",
    "http://giasubinhminh.com",
)


def normalize_content(content: str) -> str:
    for origin in PLAIN_ORIGINS:
        content = content.replace(origin, CUSTOM_ORIGIN)
        content = content.replace(
            origin.replace("/", r"\/"),
            CUSTOM_ORIGIN.replace("/", r"\/"),
        )
        content = content.replace(
            origin.replace(":", "%3A").replace("/", "%2F"),
            CUSTOM_ORIGIN.replace(":", "%3A").replace("/", "%2F"),
        )

    return (
        content.replace("/giasubinhminh.com/", "/")
        .replace(r"\/giasubinhminh.com\/", r"\/")
        .replace("%2Fgiasubinhminh.com%2F", "%2F")
    )


def main() -> None:
    if not PUBLIC_SITE.is_dir():
        raise RuntimeError(f"Missing generated public site: {PUBLIC_SITE}")

    changed_files = 0
    for path in PUBLIC_SITE.rglob("*"):
        if not path.is_file() or path.suffix.casefold() not in TEXT_SUFFIXES:
            continue
        original = path.read_text(encoding="utf-8", errors="strict")
        normalized = normalize_content(original)
        if normalized == original:
            continue
        path.write_text(normalized, encoding="utf-8", newline="\n")
        changed_files += 1

    print(f"Prepared {changed_files} files for {CUSTOM_ORIGIN}")


if __name__ == "__main__":
    main()
