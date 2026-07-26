#!/usr/bin/env python3
"""Remove captured WordPress login/admin links from the static mirror."""

from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / "giasubinhminh.com"

COMMENT_LOGIN_RE = re.compile(
    r'<h3\b[^>]*class="comment-reply-title"[^>]*id="reply-title"[^>]*>'
    r".*?</h3>\s*"
    r'<p\b[^>]*class="must-log-in"[^>]*>.*?recaptcha\.cloud.*?</p>',
    re.IGNORECASE | re.DOTALL,
)
ANCHOR_RE = re.compile(
    r"<a\b(?P<before>[^>]*?)"
    r"href=(?P<quote>[\"'])(?P<href>.*?)(?P=quote)"
    r"(?P<after>[^>]*)>(?P<body>.*?)</a>",
    re.IGNORECASE | re.DOTALL,
)
TAG_RE = re.compile(r"<[^>]+>")

COMMENT_REPLACEMENT = (
    '<h3 class="comment-reply-title" id="reply-title">'
    "Liên hệ Trung Tâm Gia Sư Trí Việt để được tư vấn"
    "</h3>"
    '<p class="must-log-in">'
    "Vui lòng dùng nút yêu cầu tư vấn hoặc hotline trên trang."
    "</p>"
)
PUBLIC_LINKS = {
    "1005": "/giasubinhminh.com/gia-su-tieng-trung/",
    "937": (
        "/giasubinhminh.com/"
        "bang-gia-gia-su-luyen-chu-dep-tai-nha-tien-bo-chi-sau-1-thang/"
    ),
}


def visible_text(fragment: str) -> str:
    return " ".join(
        html.unescape(TAG_RE.sub(" ", fragment)).casefold().split()
    )


def public_target(href: str, body: str) -> str | None:
    decoded_href = html.unescape(href)
    text = visible_text(body)
    if "post=1005" in decoded_href or "gia sư tiếng trung" in text:
        return PUBLIC_LINKS["1005"]
    if "post=937" in decoded_href or "gia sư luyện chữ" in text:
        return PUBLIC_LINKS["937"]
    return None


def replace_unsafe_anchor(match: re.Match[str]) -> str:
    href = match.group("href")
    normalized = html.unescape(href).casefold()
    unsafe = (
        "recaptcha.cloud/" in normalized
        or "giasubinhminh.com/wp-admin/post.php" in normalized
    )
    if not unsafe:
        return match.group(0)
    target = public_target(href, match.group("body"))
    if not target:
        text = visible_text(match.group("body"))
        raise RuntimeError(
            f"Unsafe link has no public mapping: {href!r} ({text!r})"
        )
    return (
        f"<a{match.group('before')}href={match.group('quote')}"
        f"{target}{match.group('quote')}{match.group('after')}>"
        f"{match.group('body')}</a>"
    )


def clean_file(path: Path) -> tuple[int, int, bool]:
    original = path.read_bytes().decode("utf-8")
    updated, comment_count = COMMENT_LOGIN_RE.subn(
        COMMENT_REPLACEMENT,
        original,
    )
    anchor_count = 0

    def replace_and_count(match: re.Match[str]) -> str:
        nonlocal anchor_count
        replacement = replace_unsafe_anchor(match)
        if replacement != match.group(0):
            anchor_count += 1
        return replacement

    updated = ANCHOR_RE.sub(replace_and_count, updated)
    changed = updated != original
    if changed:
        path.write_bytes(updated.encode("utf-8"))
    return comment_count, anchor_count, changed


def main() -> None:
    changed_files = 0
    comments = 0
    links = 0
    for path in SITE_DIR.rglob("*.html"):
        comment_count, link_count, changed = clean_file(path)
        if changed:
            changed_files += 1
            comments += comment_count
            links += link_count

    remaining = []
    for path in SITE_DIR.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        lowered = html.unescape(text).casefold()
        if (
            "recaptcha.cloud/" in lowered
            or "giasubinhminh.com/wp-admin/post.php" in lowered
        ):
            remaining.append(path)
    if remaining:
        raise RuntimeError(
            "Unsafe links remain: "
            + ", ".join(str(path.relative_to(ROOT)) for path in remaining)
        )
    print(
        f"Cleaned {comments} comment prompts and {links} unsafe links "
        f"across {changed_files} files"
    )


if __name__ == "__main__":
    main()
