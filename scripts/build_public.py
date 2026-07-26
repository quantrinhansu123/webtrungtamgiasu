#!/usr/bin/env python3
"""Build the allowlisted static output deployed by Vercel."""

from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "giasubinhminh.com").resolve()
OUTPUT_ROOT = (ROOT / "public").resolve()
OUTPUT_SITE = OUTPUT_ROOT / "giasubinhminh.com"

BLOCKED_PARTS = {"__pycache__", "wp-admin"}
BLOCKED_SUFFIXES = {
    ".bak",
    ".conf",
    ".ini",
    ".log",
    ".orig",
    ".php",
    ".py",
    ".pyc",
    ".pyo",
    ".sh",
    ".sql",
    ".swp",
}
BLOCKED_NAMES = {
    "license.txt",
    "readme.html",
    "wp-config.php",
}


def is_public_file(relative_path: Path) -> bool:
    parts = tuple(part.casefold() for part in relative_path.parts)
    name = relative_path.name.casefold()
    if not parts or any(part.startswith(".") for part in parts):
        return False
    if any(part in BLOCKED_PARTS for part in parts):
        return False
    if name.startswith("wp-login") or name in BLOCKED_NAMES:
        return False
    return relative_path.suffix.casefold() not in BLOCKED_SUFFIXES


def assert_safe_paths() -> None:
    if not SOURCE.is_dir():
        raise RuntimeError(f"Missing source site: {SOURCE}")
    if OUTPUT_ROOT.parent != ROOT or OUTPUT_ROOT.name != "public":
        raise RuntimeError(f"Unsafe output path: {OUTPUT_ROOT}")
    if OUTPUT_SITE.parent != OUTPUT_ROOT:
        raise RuntimeError(f"Unsafe site output path: {OUTPUT_SITE}")


def retry_locked_path(function, path, error):
    """Handle short-lived Windows scanner/server locks during local rebuilds."""
    last_error = error
    for attempt in range(20):
        time.sleep(0.1)
        try:
            function(path)
            return
        except PermissionError as exc:
            last_error = exc
    raise last_error


def remove_output_root():
    if sys.version_info >= (3, 12):
        shutil.rmtree(OUTPUT_ROOT, onexc=retry_locked_path)
        return

    def retry_legacy(function, path, error_info):
        retry_locked_path(function, path, error_info[1])

    shutil.rmtree(OUTPUT_ROOT, onerror=retry_legacy)


def build() -> tuple[int, int]:
    assert_safe_paths()
    if OUTPUT_ROOT.exists():
        remove_output_root()
    OUTPUT_SITE.mkdir(parents=True)

    copied_files = 0
    copied_bytes = 0
    for source_path in SOURCE.rglob("*"):
        if source_path.is_symlink() or not source_path.is_file():
            continue
        relative_path = source_path.relative_to(SOURCE)
        if not is_public_file(relative_path):
            continue
        destination = OUTPUT_SITE / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)
        copied_files += 1
        copied_bytes += source_path.stat().st_size

    required_files = (
        OUTPUT_SITE / "index.html",
        OUTPUT_SITE
        / "wp-content"
        / "uploads"
        / "cms"
        / "2026"
        / "07"
        / "site-config.json",
        OUTPUT_SITE
        / "wp-content"
        / "uploads"
        / "cms"
        / "2026"
        / "07"
        / "image-fallback.js",
    )
    missing = [path for path in required_files if not path.is_file()]
    if missing:
        raise RuntimeError(
            "Public build is incomplete: "
            + ", ".join(str(path.relative_to(OUTPUT_ROOT)) for path in missing)
        )
    return copied_files, copied_bytes


if __name__ == "__main__":
    files, total_bytes = build()
    print(f"Built {files} public files ({total_bytes} bytes) in {OUTPUT_ROOT}")
