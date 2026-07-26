import json
import os
import re
import uuid
import base64
import hashlib
import hmac
import ipaddress
import math
import secrets
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import warnings
from collections import deque
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from html import escape
from io import BytesIO
from pathlib import Path
from pathlib import PurePosixPath

from bs4 import BeautifulSoup
from flask import Flask, jsonify, request, send_from_directory, session
from PIL import Image, UnidentifiedImageError
from werkzeug.exceptions import RequestEntityTooLarge

BASE_DIR = Path(__file__).resolve().parent.parent
SITE_DIR = BASE_DIR / "giasubinhminh.com"
ADMIN_DIR = Path(__file__).resolve().parent
CONFIG_PATH = ADMIN_DIR / "config.json"
PAGE_TITLES_PATH = ADMIN_DIR / "page-titles.json"
CLASSES_PATH = ADMIN_DIR / "classes.json"
CLASS_TEMPLATE_PATH = ADMIN_DIR / "templates" / "lop-moi.html"
CLASS_PUBLIC_DIR = SITE_DIR / "lop-moi"
CLASS_PUBLIC_PATH = CLASS_PUBLIC_DIR / "index.html"
UPLOAD_DIR = SITE_DIR / "wp-content" / "uploads" / "cms"
PUBLIC_CONFIG_REL_PATH = "wp-content/uploads/cms/2026/07/site-config.json"
PUBLIC_CONFIG_PATH = SITE_DIR / PUBLIC_CONFIG_REL_PATH
PUBLIC_RUNTIME_REL_PATH = "wp-content/uploads/cms/2026/07/image-fallback.js"
PUBLIC_RUNTIME_PATH = SITE_DIR / PUBLIC_RUNTIME_REL_PATH
PUBLIC_RUNTIME_TEMPLATE_PATH = ADMIN_DIR / "templates" / "site-runtime.js"
ADMIN_CONFIG_REPO_PATH = "admin/config.json"
PUBLIC_CONFIG_REPO_PATH = f"giasubinhminh.com/{PUBLIC_CONFIG_REL_PATH}"
PUBLIC_RUNTIME_REPO_PATH = f"giasubinhminh.com/{PUBLIC_RUNTIME_REL_PATH}"
HOMEPAGE_REPO_PATH = "giasubinhminh.com/index.html"
SLIDE_RECOMMENDED = {"width": 1360, "height": 540}
LOGO_RECOMMENDED = {"width": 186, "height": 100}
FEEDBACK_PAGE_ID = (
    "gia-su-day-online-tai-nha-tu-lop-1-12-on-thi-tat-ca-cac-mon/index.html"
)
FEEDBACK_IMAGE_COUNT = 6
HOMEPAGE_FEEDBACK_NUMBERS = (*range(1, 7), *range(8, 22))
HOMEPAGE_FEEDBACK_IMAGE_COUNT = len(HOMEPAGE_FEEDBACK_NUMBERS)
PASSWORD_ITERATIONS = 390000
MAX_IMAGE_UPLOAD_BYTES = 8 * 1024 * 1024
MAX_IMAGE_PIXELS = 40_000_000
MAX_IMAGE_DIMENSION = 12_000
MAX_ANIMATION_FRAMES = 200
ALLOWED_IMAGE_FORMATS = {
    "JPEG": {".jpg", ".jpeg"},
    "PNG": {".png"},
    "GIF": {".gif"},
    "WEBP": {".webp"},
}
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS
RICH_TEXT_ALLOWED_TAGS = {
    "a",
    "abbr",
    "b",
    "blockquote",
    "br",
    "code",
    "div",
    "em",
    "figcaption",
    "figure",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "i",
    "img",
    "li",
    "mark",
    "ol",
    "p",
    "pre",
    "s",
    "small",
    "span",
    "strong",
    "sub",
    "sup",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "tr",
    "u",
    "ul",
}
RICH_TEXT_DROP_TAGS = {
    "base",
    "button",
    "embed",
    "form",
    "iframe",
    "input",
    "link",
    "math",
    "meta",
    "object",
    "option",
    "script",
    "select",
    "style",
    "svg",
    "template",
    "textarea",
}
RICH_TEXT_ALLOWED_STYLES = {
    "background-color",
    "color",
    "direction",
    "font-family",
    "font-size",
    "margin-left",
    "padding-left",
    "text-align",
    "white-space",
}
UNSAFE_URL_CHARACTERS = frozenset("<>\"'\\")
LOGIN_RATE_LIMIT = 5
LOGIN_RATE_WINDOW_SECONDS = 15 * 60
# Memory counters are a bounded application backstop. Serverless deployments
# must also enforce /api/login at the platform edge or in a shared TTL store.
_LOGIN_ATTEMPTS: dict[str, deque[float]] = {}
_LOGIN_ATTEMPTS_LOCK = threading.Lock()
_CONFIG_SAVE_LOCK = threading.Lock()
_UNSAFE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
_WINDOWS_RESERVED_NAMES = {
    "aux",
    "clock$",
    "com1",
    "com2",
    "com3",
    "com4",
    "com5",
    "com6",
    "com7",
    "com8",
    "com9",
    "con",
    "lpt1",
    "lpt2",
    "lpt3",
    "lpt4",
    "lpt5",
    "lpt6",
    "lpt7",
    "lpt8",
    "lpt9",
    "nul",
    "prn",
}
_SENSITIVE_PUBLIC_PARTS = {
    ".git",
    ".github",
    ".vercel",
    "__pycache__",
    "admin",
    "api",
    "node_modules",
    "tests",
    "wp-admin",
}
_SENSITIVE_PUBLIC_NAMES = {
    ".env",
    ".env.local",
    ".htaccess",
    "composer.json",
    "composer.lock",
    "package-lock.json",
    "package.json",
    "php.ini",
    "pyproject.toml",
    "requirements.txt",
    "server.py",
    "vercel.json",
    "wp-config.php",
}
DEFAULT_SITE_NAME = "Trung Tâm Gia Sư Trí Việt"
DEFAULT_LOGO = "wp-content/uploads/2018/07/logo-1.png"
DEFAULT_HOTLINE1 = "0962.005.996"
DEFAULT_HOTLINE2 = "0987.005.996"
DEFAULT_FEEDBACK_IMAGES = [
    {
        "url": f"/giasubinhminh.com/wp-content/uploads/cms/2026/07/feedback/fb{index}.jpg",
        "alt": f"Phản hồi của phụ huynh về gia sư Trí Việt {index}",
    }
    for index in range(1, FEEDBACK_IMAGE_COUNT + 1)
]
DEFAULT_HOMEPAGE_FEEDBACK_IMAGES = [
    {
        "url": (
            "/giasubinhminh.com/wp-content/uploads/cms/2026/07/"
            f"phu-huynh-phan-hoi/phan-hoi-{number:02d}.jpg"
        ),
        "alt": f"Phản hồi phụ huynh {number}",
    }
    for number in HOMEPAGE_FEEDBACK_NUMBERS
]


def running_on_vercel() -> bool:
    return bool(os.environ.get("VERCEL"))


def production_mode() -> bool:
    environment = (
        os.environ.get("CMS_ENV")
        or os.environ.get("FLASK_ENV")
        or os.environ.get("ENVIRONMENT")
        or ""
    )
    return running_on_vercel() or environment.strip().casefold() == "production"


def derive_session_secret() -> bytes:
    """Return a stable production key or an unpredictable local process key."""
    material = [
        os.environ[name].encode("utf-8")
        for name in ("CMS_SECRET", "CMS_PASSWORD", "GITHUB_TOKEN")
        if os.environ.get(name)
    ]
    if material:
        return hashlib.sha256(
            b"tri-viet-cms-session-v1\0" + b"\0".join(material)
        ).digest()
    if production_mode():
        raise RuntimeError(
            "Production CMS requires CMS_SECRET, CMS_PASSWORD, or GITHUB_TOKEN "
            "to sign administrator sessions."
        )
    return secrets.token_bytes(32)


def github_enabled() -> bool:
    return bool(os.environ.get("GITHUB_TOKEN")) and bool(
        os.environ.get("GITHUB_REPO", "quantrinhansu123/webtrungtamgiasu")
    )


def _github_request(method: str, url: str, payload: dict | None = None) -> dict:
    token = os.environ.get("GITHUB_TOKEN", "")
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "tri-viet-cms",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers=headers,
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"GitHub API {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Không kết nối được GitHub: {exc.reason}") from exc


def github_file_api(repo_path: str) -> str:
    repo = os.environ.get("GITHUB_REPO", "quantrinhansu123/webtrungtamgiasu")
    encoded_path = urllib.parse.quote(repo_path.lstrip("/"), safe="/")
    return f"https://api.github.com/repos/{repo}/contents/{encoded_path}"


def github_repository_api(path: str = "") -> str:
    repo = os.environ.get("GITHUB_REPO", "quantrinhansu123/webtrungtamgiasu")
    suffix = f"/{path.lstrip('/')}" if path else ""
    return f"https://api.github.com/repos/{repo}{suffix}"


def github_repository_tree() -> list[dict]:
    branch = os.environ.get("GITHUB_BRANCH", "main")
    payload = _github_request(
        "GET",
        (
            f"{github_repository_api('git/trees')}/"
            f"{urllib.parse.quote(branch, safe='')}?recursive=1"
        ),
    )
    if payload.get("truncated"):
        raise RuntimeError("Danh sách tệp GitHub quá lớn và đã bị cắt bớt")
    return payload.get("tree") or []


def github_read_file(repo_path: str) -> bytes:
    branch = os.environ.get("GITHUB_BRANCH", "main")
    return github_read_file_at_ref(repo_path, branch)


def github_read_file_at_ref(repo_path: str, ref: str) -> bytes:
    payload = _github_request(
        "GET",
        f"{github_file_api(repo_path)}?ref={urllib.parse.quote(ref, safe='')}",
    )
    encoded = (payload.get("content") or "").replace("\n", "")
    if not encoded:
        raise RuntimeError(f"GitHub không trả về nội dung của {repo_path}")
    return base64.b64decode(encoded)


def github_branch_snapshot() -> tuple[str, str]:
    branch = os.environ.get("GITHUB_BRANCH", "main")
    encoded_branch = urllib.parse.quote(branch, safe="")
    reference = _github_request(
        "GET",
        github_repository_api(f"git/ref/heads/{encoded_branch}"),
    )
    head_sha = str((reference.get("object") or {}).get("sha") or "")
    if not head_sha:
        raise RuntimeError("GitHub không trả về commit hiện tại của nhánh")
    commit = _github_request(
        "GET",
        github_repository_api(f"git/commits/{head_sha}"),
    )
    tree_sha = str((commit.get("tree") or {}).get("sha") or "")
    if not tree_sha:
        raise RuntimeError("GitHub không trả về cây tệp hiện tại của nhánh")
    return head_sha, tree_sha


def github_ref_update_conflict(exc: RuntimeError) -> bool:
    message = str(exc)
    return "GitHub API 409" in message or "GitHub API 422" in message


def github_create_atomic_commit(
    changes: dict[str, str | bytes],
    *,
    message: str,
    expected_head: str,
    base_tree: str,
) -> str:
    """Commit all files together, then advance the branch with a CAS update."""
    if not changes:
        raise ValueError("Không có tệp nào để lưu")

    tree_entries = []
    for repo_path, content in changes.items():
        raw = content.encode("utf-8") if isinstance(content, str) else content
        blob = _github_request(
            "POST",
            github_repository_api("git/blobs"),
            {
                "content": base64.b64encode(raw).decode("ascii"),
                "encoding": "base64",
            },
        )
        blob_sha = str(blob.get("sha") or "")
        if not blob_sha:
            raise RuntimeError(f"GitHub không tạo được dữ liệu cho {repo_path}")
        tree_entries.append(
            {
                "path": repo_path.lstrip("/"),
                "mode": "100644",
                "type": "blob",
                "sha": blob_sha,
            }
        )

    tree = _github_request(
        "POST",
        github_repository_api("git/trees"),
        {
            "base_tree": base_tree,
            "tree": tree_entries,
        },
    )
    tree_sha = str(tree.get("sha") or "")
    if not tree_sha:
        raise RuntimeError("GitHub không tạo được cây tệp mới")

    commit = _github_request(
        "POST",
        github_repository_api("git/commits"),
        {
            "message": message,
            "tree": tree_sha,
            "parents": [expected_head],
        },
    )
    commit_sha = str(commit.get("sha") or "")
    if not commit_sha:
        raise RuntimeError("GitHub không tạo được commit mới")

    branch = os.environ.get("GITHUB_BRANCH", "main")
    encoded_branch = urllib.parse.quote(branch, safe="")
    try:
        _github_request(
            "PATCH",
            github_repository_api(f"git/refs/heads/{encoded_branch}"),
            {"sha": commit_sha, "force": False},
        )
    except RuntimeError as exc:
        if github_ref_update_conflict(exc):
            raise GitHubRefConflict(
                "Nhánh GitHub vừa được cập nhật bởi yêu cầu khác"
            ) from exc
        raise
    return commit_sha


class GitHubRefConflict(RuntimeError):
    """The branch head changed before an atomic transaction could publish."""


def github_upsert_file(
    repo_path: str,
    content: str | bytes,
    message: str,
    binary: bool = False,
):
    """Create or update a repository file so Vercel redeploys the new content."""
    branch = os.environ.get("GITHUB_BRANCH", "main")
    api_url = github_file_api(repo_path)
    sha = None
    try:
        existing = _github_request(
            "GET",
            f"{api_url}?ref={urllib.parse.quote(branch, safe='')}",
        )
        sha = existing.get("sha")
    except RuntimeError as exc:
        if "GitHub API 404" not in str(exc):
            raise

    if isinstance(content, str):
        raw = content.encode("utf-8")
    else:
        raw = content
    if not binary:
        raw = raw.decode("utf-8").encode("utf-8")

    payload = {
        "message": message,
        "content": base64.b64encode(raw).decode("ascii"),
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha
    return _github_request("PUT", api_url, payload)


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("ascii"),
        PASSWORD_ITERATIONS,
    )
    return (
        f"pbkdf2_sha256${PASSWORD_ITERATIONS}${salt}$"
        f"{base64.b64encode(digest).decode('ascii')}"
    )


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt, digest = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        computed = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("ascii"),
            int(iterations),
        )
        return hmac.compare_digest(
            base64.b64encode(computed).decode("ascii"),
            digest,
        )
    except (TypeError, ValueError):
        return False

BLOCKED_PREFIXES = {
    "wp-content",
    "wp-includes",
    "wp-json",
    "author",
    "tag",
    "feed",
    "comments",
    "category",
}

app = Flask(__name__, static_folder=str(ADMIN_DIR / "static"), static_url_path="/admin/static")
app.config.update(
    SECRET_KEY=derive_session_secret(),
    SESSION_COOKIE_NAME=(
        "__Host-triviet_cms_session"
        if production_mode()
        else "triviet_cms_session"
    ),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=production_mode(),
    SESSION_COOKIE_SAMESITE="Strict",
    SESSION_COOKIE_PATH="/",
    SESSION_REFRESH_EACH_REQUEST=False,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    MAX_CONTENT_LENGTH=MAX_IMAGE_UPLOAD_BYTES + (512 * 1024),
    MAX_IMAGE_UPLOAD_BYTES=MAX_IMAGE_UPLOAD_BYTES,
    LOGIN_RATE_LIMIT=LOGIN_RATE_LIMIT,
    LOGIN_RATE_WINDOW_SECONDS=LOGIN_RATE_WINDOW_SECONDS,
)


def canonical_site_path(
    rel_path: str,
    *,
    allow_empty: bool = False,
) -> tuple[str, Path]:
    """Resolve an untrusted relative path and prove it remains below SITE_DIR."""
    if not isinstance(rel_path, str):
        raise ValueError("Đường dẫn không hợp lệ")
    decoded = rel_path
    for _ in range(3):
        unquoted = urllib.parse.unquote(decoded)
        if unquoted == decoded:
            break
        decoded = unquoted
    decoded = decoded.replace("\\", "/")
    if "\x00" in decoded or decoded.startswith(("/", "//")):
        raise ValueError("Đường dẫn không hợp lệ")
    if decoded != decoded.strip() or "?" in decoded or "#" in decoded:
        raise ValueError("Đường dẫn không hợp lệ")
    if not decoded:
        if not allow_empty:
            raise ValueError("Đường dẫn không hợp lệ")
        return "", SITE_DIR.resolve()

    path = PurePosixPath(decoded)
    parts = path.parts
    if (
        not parts
        or any(part in {"", ".", ".."} for part in parts)
        or any(":" in part or part.endswith((" ", ".")) for part in parts)
        or any(
            part.split(".", 1)[0].casefold() in _WINDOWS_RESERVED_NAMES
            for part in parts
        )
    ):
        raise ValueError("Đường dẫn không hợp lệ")

    normalized = path.as_posix()
    site_root = SITE_DIR.resolve()
    candidate = (site_root / Path(*parts)).resolve()
    try:
        candidate.relative_to(site_root)
    except ValueError as exc:
        raise ValueError("Đường dẫn nằm ngoài thư mục website") from exc
    return normalized, candidate


def public_path_is_sensitive(rel_path: str) -> bool:
    try:
        normalized, _ = canonical_site_path(rel_path, allow_empty=True)
    except ValueError:
        return True
    parts = [part.casefold() for part in PurePosixPath(normalized).parts]
    if any(part.startswith(".") for part in parts):
        return True
    if parts and parts[0] in _SENSITIVE_PUBLIC_PARTS:
        return True
    if parts and (
        parts[0] == "wp-login" or parts[0].startswith("wp-login.")
    ):
        return True
    if parts and parts[-1] in _SENSITIVE_PUBLIC_NAMES:
        return True
    return bool(parts and parts[-1].endswith((".py", ".pyc")))


def valid_public_image_url(value: str) -> bool:
    value = str(value or "").strip()
    if (
        not value
        or len(value) > 2048
        or any(ord(char) < 32 for char in value)
        or any(char in value for char in UNSAFE_URL_CHARACTERS)
    ):
        return False
    if value.startswith("/giasubinhminh.com/"):
        rel_path = value[len("/giasubinhminh.com/") :]
    elif value.startswith("wp-content/"):
        rel_path = value
    else:
        try:
            parsed = urllib.parse.urlsplit(value)
        except ValueError:
            return False
        return (
            parsed.scheme == "https"
            and bool(parsed.netloc)
            and not parsed.username
            and not parsed.password
        )
    try:
        normalized, _ = canonical_site_path(rel_path)
    except ValueError:
        return False
    return normalized.startswith("wp-content/uploads/")


def valid_rich_text_link(value: str) -> bool:
    value = str(value or "").strip()
    if (
        not value
        or len(value) > 2048
        or any(ord(char) < 32 for char in value)
        or any(char in value for char in UNSAFE_URL_CHARACTERS)
    ):
        return False
    if value.startswith("#"):
        return bool(re.fullmatch(r"#[A-Za-z0-9_.:-]{1,160}", value))
    try:
        parsed = urllib.parse.urlsplit(value)
    except ValueError:
        return False
    if parsed.scheme:
        scheme = parsed.scheme.casefold()
        if scheme in {"http", "https"}:
            return (
                bool(parsed.netloc)
                and not parsed.username
                and not parsed.password
            )
        return scheme in {"mailto", "tel"} and bool(parsed.path)
    return value.startswith("/") and not value.startswith("//")


def sanitize_inline_style(value: str) -> str:
    safe_declarations = []
    for declaration in str(value or "").split(";"):
        name, separator, raw_value = declaration.partition(":")
        if not separator:
            continue
        name = name.strip().casefold()
        css_value = raw_value.strip()
        lowered = css_value.casefold()
        if (
            name not in RICH_TEXT_ALLOWED_STYLES
            or not css_value
            or len(css_value) > 160
            or any(char in css_value for char in "<>{}\\")
            or any(
                token in lowered
                for token in (
                    "@import",
                    "behavior",
                    "expression",
                    "javascript:",
                    "-moz-binding",
                    "url(",
                )
            )
        ):
            continue
        safe_declarations.append(f"{name}: {css_value}")
    return "; ".join(safe_declarations)


def sanitize_rich_html(value) -> str:
    """Allow Quill-style formatting while removing executable HTML/CSS."""
    fragment = BeautifulSoup(str(value or ""), "html.parser")
    for tag in list(fragment.find_all(True)):
        if tag.parent is None or not tag.name:
            continue
        name = tag.name.casefold()
        if name in RICH_TEXT_DROP_TAGS:
            tag.decompose()
            continue
        if name not in RICH_TEXT_ALLOWED_TAGS:
            tag.unwrap()
            continue

        allowed_attributes = {"class", "style"}
        if name == "a":
            allowed_attributes.update({"href", "rel", "target", "title"})
        elif name == "img":
            allowed_attributes.update(
                {
                    "alt",
                    "decoding",
                    "height",
                    "loading",
                    "src",
                    "title",
                    "width",
                }
            )
        elif name in {"li"}:
            allowed_attributes.add("data-list")
        elif name in {"td", "th"}:
            allowed_attributes.update({"colspan", "rowspan", "scope"})

        for attribute in list(tag.attrs):
            if attribute.casefold() not in allowed_attributes:
                tag.attrs.pop(attribute, None)

        if tag.has_attr("class"):
            class_values = tag.get("class") or []
            if isinstance(class_values, str):
                class_values = class_values.split()
            class_values = [
                item
                for item in class_values[:20]
                if re.fullmatch(r"[A-Za-z0-9_-]{1,64}", str(item))
            ]
            if class_values:
                tag["class"] = class_values
            else:
                tag.attrs.pop("class", None)

        if tag.has_attr("style"):
            safe_style = sanitize_inline_style(tag.get("style", ""))
            if safe_style:
                tag["style"] = safe_style
            else:
                tag.attrs.pop("style", None)

        if name == "a":
            if tag.has_attr("href") and not valid_rich_text_link(tag["href"]):
                tag.attrs.pop("href", None)
            target = str(tag.get("target") or "")
            if target not in {"_blank", "_self"}:
                tag.attrs.pop("target", None)
            if target == "_blank":
                tag["rel"] = "noopener noreferrer"
            elif tag.has_attr("rel"):
                tag["rel"] = "nofollow"
        elif name == "img":
            if not valid_public_image_url(tag.get("src", "")):
                tag.decompose()
                continue
            for dimension in ("width", "height"):
                if tag.has_attr(dimension):
                    try:
                        number = int(str(tag[dimension]))
                    except ValueError:
                        tag.attrs.pop(dimension, None)
                        continue
                    if not 1 <= number <= MAX_IMAGE_DIMENSION:
                        tag.attrs.pop(dimension, None)
            if tag.get("loading") not in {"eager", "lazy"}:
                tag.attrs.pop("loading", None)
            if tag.get("decoding") not in {"async", "auto", "sync"}:
                tag.attrs.pop("decoding", None)
        elif name == "li" and tag.has_attr("data-list"):
            if tag["data-list"] not in {
                "bullet",
                "checked",
                "ordered",
                "unchecked",
            }:
                tag.attrs.pop("data-list", None)
        elif name in {"td", "th"}:
            for span in ("colspan", "rowspan"):
                if tag.has_attr(span) and not re.fullmatch(
                    r"(?:[1-9]|[1-9][0-9])",
                    str(tag[span]),
                ):
                    tag.attrs.pop(span, None)
            if tag.has_attr("scope") and tag["scope"] not in {
                "col",
                "colgroup",
                "row",
                "rowgroup",
            }:
                tag.attrs.pop("scope", None)
    return fragment.decode_contents()


def configured_drive_folder_url() -> str:
    value = os.environ.get("CMS_DRIVE_FOLDER_URL", "").strip()
    if not value or len(value) > 2048:
        return ""
    try:
        parsed = urllib.parse.urlsplit(value)
    except ValueError:
        return ""
    if (
        parsed.scheme != "https"
        or parsed.hostname not in {"drive.google.com", "docs.google.com"}
        or parsed.username
        or parsed.password
    ):
        return ""
    return value


def normalize_image_collection(
    value,
    *,
    defaults: list[dict[str, str]],
    label: str,
    strict: bool = False,
) -> list[dict[str, str]]:
    expected_count = len(defaults)
    if strict and (
        not isinstance(value, list) or len(value) != expected_count
    ):
        raise ValueError(f"Cần cung cấp đúng {expected_count} {label}")
    source = value if isinstance(value, list) else []
    normalized = []
    for index, fallback in enumerate(defaults):
        item = (
            source[index]
            if index < len(source) and isinstance(source[index], dict)
            else {}
        )
        supplied_url = str(item.get("url") or "").strip()
        if strict and not supplied_url:
            raise ValueError(f"{label.capitalize()} {index + 1} không được để trống")
        url = supplied_url or fallback["url"]
        alt = str(item.get("alt") or fallback["alt"]).strip()
        if not valid_public_image_url(url):
            if strict:
                raise ValueError(
                    f"Đường dẫn {label} {index + 1} không hợp lệ"
                )
            url = fallback["url"]
        if len(alt) > 240:
            if strict:
                raise ValueError(f"Mô tả {label} {index + 1} quá dài")
            alt = alt[:240]
        normalized.append({"url": url, "alt": alt})
    return normalized


def normalize_feedback_images(
    value,
    *,
    strict: bool = False,
) -> list[dict[str, str]]:
    return normalize_image_collection(
        value,
        defaults=DEFAULT_FEEDBACK_IMAGES,
        label="ảnh phản hồi",
        strict=strict,
    )


def normalize_homepage_feedback_images(
    value,
    *,
    strict: bool = False,
) -> list[dict[str, str]]:
    return normalize_image_collection(
        value,
        defaults=DEFAULT_HOMEPAGE_FEEDBACK_IMAGES,
        label="ảnh phản hồi trang chủ",
        strict=strict,
    )


def clean_public_text(value, fallback: str, maximum: int) -> str:
    cleaned = str(value or fallback).strip()
    if not cleaned or any(ord(char) < 32 and char not in "\t\n" for char in cleaned):
        cleaned = fallback
    return cleaned[:maximum]


def build_public_site_config(config: dict) -> dict:
    """Return the exact public whitelist; authentication data never crosses it."""
    logo = str(config.get("logo") or DEFAULT_LOGO).strip()
    if not valid_public_image_url(logo):
        logo = DEFAULT_LOGO
    hotline1 = clean_public_text(
        config.get("hotline1"),
        DEFAULT_HOTLINE1,
        50,
    )
    hotline2 = clean_public_text(
        config.get("hotline2"),
        DEFAULT_HOTLINE2,
        50,
    )
    if not re.fullmatch(r"[0-9+().\s-]{3,50}", hotline1):
        hotline1 = DEFAULT_HOTLINE1
    if not re.fullmatch(r"[0-9+().\s-]{3,50}", hotline2):
        hotline2 = DEFAULT_HOTLINE2
    return {
        "site_name": clean_public_text(
            config.get("site_name"),
            DEFAULT_SITE_NAME,
            160,
        ),
        "logo": logo,
        "hotline1": hotline1,
        "hotline2": hotline2,
        "feedback_images": normalize_feedback_images(config.get("feedback_images")),
        "homepage_feedback_images": normalize_homepage_feedback_images(
            config.get("homepage_feedback_images")
        ),
    }


def public_site_config_payload(config: dict) -> str:
    return (
        json.dumps(
            build_public_site_config(config),
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )


def render_public_site_runtime(config: dict) -> str:
    template = PUBLIC_RUNTIME_TEMPLATE_PATH.read_text(encoding="utf-8")
    marker = "__SITE_CONFIG_JSON__"
    if template.count(marker) != 1:
        raise RuntimeError("Mẫu JavaScript cấu hình website không hợp lệ")
    config_json = json.dumps(
        build_public_site_config(config),
        ensure_ascii=False,
        separators=(",", ":"),
    )
    config_json = (
        config_json.replace("<", "\\u003c")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    return template.replace(marker, config_json)


def public_site_artifacts(config: dict) -> dict[str, str]:
    return {
        PUBLIC_CONFIG_REPO_PATH: public_site_config_payload(config),
        PUBLIC_RUNTIME_REPO_PATH: render_public_site_runtime(config),
    }


def write_text_atomically(path: Path, payload: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temp_path.write_text(payload, encoding="utf-8", newline="\n")
        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def repository_path_to_local(repo_path: str) -> Path:
    if repo_path == ADMIN_CONFIG_REPO_PATH:
        return CONFIG_PATH
    prefix = "giasubinhminh.com/"
    if not isinstance(repo_path, str) or not repo_path.startswith(prefix):
        raise ValueError("Đường dẫn tệp kho mã không được phép")
    rel_path = repo_path[len(prefix) :]
    normalized, target = canonical_site_path(rel_path)
    if repo_path != f"{prefix}{normalized}":
        raise ValueError("Đường dẫn tệp kho mã không chính tắc")
    return target


def write_repository_files_atomically(changes: dict[str, str | bytes]):
    """Stage every local file first and roll back if any replace fails."""
    if not changes:
        raise ValueError("Không có tệp nào để lưu")

    staged: list[tuple[Path, Path]] = []
    originals: dict[Path, bytes | None] = {}
    replaced: list[Path] = []
    targets: set[Path] = set()
    try:
        for repo_path, content in changes.items():
            target = repository_path_to_local(repo_path)
            if target in targets:
                raise ValueError("Một tệp bị cập nhật nhiều lần")
            targets.add(target)
            if target.exists() and not target.is_file():
                raise OSError(f"Đích lưu không phải là tệp: {target}")
            originals[target] = target.read_bytes() if target.exists() else None
            target.parent.mkdir(parents=True, exist_ok=True)
            temp_path = target.with_name(
                f".{target.name}.{uuid.uuid4().hex}.tmp"
            )
            raw = content.encode("utf-8") if isinstance(content, str) else content
            temp_path.write_bytes(raw)
            staged.append((temp_path, target))

        for temp_path, target in staged:
            temp_path.replace(target)
            replaced.append(target)
    except Exception as exc:
        rollback_error = None
        for target in reversed(replaced):
            try:
                original = originals[target]
                if original is None:
                    target.unlink(missing_ok=True)
                    continue
                rollback_path = target.with_name(
                    f".{target.name}.{uuid.uuid4().hex}.rollback"
                )
                try:
                    rollback_path.write_bytes(original)
                    rollback_path.replace(target)
                finally:
                    rollback_path.unlink(missing_ok=True)
            except Exception as current_error:
                rollback_error = rollback_error or current_error
        if rollback_error is not None:
            raise RuntimeError(
                "Lưu tệp thất bại và không thể khôi phục đầy đủ"
            ) from rollback_error
        raise exc
    finally:
        for temp_path, _target in staged:
            temp_path.unlink(missing_ok=True)


def atomic_repository_update(
    change_builder,
    *,
    message: str,
    max_attempts: int = 5,
):
    """Build against one snapshot and publish all changes as one transaction."""
    if max_attempts < 1:
        raise ValueError("Số lần thử lưu phải lớn hơn 0")

    if not running_on_vercel():
        with _CONFIG_SAVE_LOCK:

            def local_reader(repo_path: str) -> bytes:
                return repository_path_to_local(repo_path).read_bytes()

            changes, result = change_builder(local_reader)
            write_repository_files_atomically(changes)
            return result

    if not github_enabled():
        raise RuntimeError(
            "Chưa cấu hình GITHUB_TOKEN trên Vercel nên chưa thể lưu."
        )

    last_error = None
    for _attempt in range(max_attempts):
        head_sha, tree_sha = github_branch_snapshot()

        def github_reader(repo_path: str) -> bytes:
            return github_read_file_at_ref(repo_path, head_sha)

        changes, result = change_builder(github_reader)
        try:
            github_create_atomic_commit(
                changes,
                message=message,
                expected_head=head_sha,
                base_tree=tree_sha,
            )
        except GitHubRefConflict as exc:
            last_error = exc
            continue
        return result
    raise RuntimeError(
        "Dữ liệu bị cập nhật đồng thời; vui lòng thử lại."
    ) from last_error


def publish_public_site_config(config: dict):
    if running_on_vercel():
        return mutate_config_atomic(
            lambda latest: latest,
            publish_public=True,
            message="cms: publish public site configuration",
        )
    with _CONFIG_SAVE_LOCK:
        write_repository_files_atomically(public_site_artifacts(config))


def load_config(fresh: bool = False):
    if fresh and running_on_vercel() and github_enabled():
        raw = github_read_file(ADMIN_CONFIG_REPO_PATH)
        return json.loads(raw.decode("utf-8"))
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_config(config):
    """Legacy local helper; serverless writes must use mutate_config_atomic."""
    payload = json.dumps(config, ensure_ascii=False, indent=2) + "\n"
    if running_on_vercel():
        raise RuntimeError(
            "Cập nhật cấu hình trên Vercel phải dùng giao dịch nguyên tử."
        )
    write_text_atomically(CONFIG_PATH, payload)


def apply_config_mutator(config: dict, mutator) -> dict:
    updated = mutator(config)
    if updated is None:
        updated = config
    if not isinstance(updated, dict):
        raise TypeError("Config mutator must return a dictionary or None")
    return updated


def mutate_config_atomic(
    mutator,
    *,
    publish_public: bool,
    message: str = "cms: update admin settings",
    extra_changes_builder=None,
    max_attempts: int = 5,
) -> dict:
    """Mutate the latest config and publish every derived file together."""

    def build_changes(reader):
        raw = reader(ADMIN_CONFIG_REPO_PATH)
        config = json.loads(raw.decode("utf-8"))
        updated = apply_config_mutator(config, mutator)
        changes: dict[str, str | bytes] = {
            ADMIN_CONFIG_REPO_PATH: (
                json.dumps(updated, ensure_ascii=False, indent=2) + "\n"
            )
        }
        if publish_public:
            changes.update(public_site_artifacts(updated))
        if extra_changes_builder is not None:
            extra_changes = extra_changes_builder(updated, reader)
            if not isinstance(extra_changes, dict):
                raise TypeError("Extra changes builder must return a dictionary")
            if set(changes).intersection(extra_changes):
                raise ValueError("Một tệp bị cập nhật nhiều lần")
            changes.update(extra_changes)
        return changes, updated

    return atomic_repository_update(
        build_changes,
        message=message,
        max_attempts=max_attempts,
    )


def load_page_titles(fresh: bool = False) -> dict:
    if fresh and running_on_vercel() and github_enabled():
        raw = github_read_file("admin/page-titles.json")
        data = json.loads(raw.decode("utf-8"))
    else:
        if not PAGE_TITLES_PATH.exists():
            return {"titles": {}, "redirects": []}
        with open(PAGE_TITLES_PATH, encoding="utf-8") as source:
            data = json.load(source)
    if not isinstance(data, dict):
        return {"titles": {}, "redirects": []}
    titles = data.get("titles") if isinstance(data.get("titles"), dict) else {}
    redirects = data.get("redirects") if isinstance(data.get("redirects"), list) else []
    return {
        "titles": {str(key): str(value) for key, value in titles.items() if value},
        "redirects": [str(value) for value in redirects],
    }


def save_page_titles(data: dict):
    payload = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if running_on_vercel():
        if not github_enabled():
            raise RuntimeError(
                "Chưa cấu hình GITHUB_TOKEN trên Vercel nên chưa thể lưu tiêu đề trang."
            )
        github_upsert_file(
            "admin/page-titles.json",
            payload,
            "cms: update Vietnamese page title",
        )
        return
    with open(PAGE_TITLES_PATH, "w", encoding="utf-8", newline="\n") as source:
        source.write(payload)


def load_classes(fresh: bool | None = None):
    if fresh is None:
        fresh = running_on_vercel()
    if fresh and running_on_vercel() and github_enabled():
        raw = github_read_file("admin/classes.json")
        data = json.loads(raw.decode("utf-8"))
    else:
        if not CLASSES_PATH.exists():
            return []
        with open(CLASSES_PATH, encoding="utf-8") as f:
            data = json.load(f)
    classes = data if isinstance(data, list) else data.get("classes", [])
    return sorted(
        [item for item in classes if isinstance(item, dict)],
        key=lambda item: (item.get("date", ""), item.get("created_at", "")),
        reverse=True,
    )


def save_classes(classes):
    payload = json.dumps(classes, ensure_ascii=False, indent=2) + "\n"
    if running_on_vercel():
        if not github_enabled():
            raise RuntimeError(
                "Chưa cấu hình GITHUB_TOKEN trên Vercel nên chưa thể lưu lớp mới."
            )
        github_upsert_file(
            "admin/classes.json",
            payload,
            "cms: update class list",
        )
        return
    CLASSES_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path = CLASSES_PATH.with_suffix(".json.tmp")
    with open(temp_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(payload)
    temp_path.replace(CLASSES_PATH)


def format_class_date(value: str) -> str:
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return value or ""


def normalize_class_payload(data: dict) -> dict:
    title = str(data.get("title") or "").strip()
    class_date = str(data.get("date") or "").strip()
    content = str(data.get("content") or "").strip()
    if len(title) < 3:
        raise ValueError("Tiêu đề lớp mới phải có ít nhất 3 ký tự")
    if len(title) > 200:
        raise ValueError("Tiêu đề lớp mới không được quá 200 ký tự")
    try:
        datetime.strptime(class_date, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("Ngày đăng không hợp lệ") from exc
    if len(content) < 3:
        raise ValueError("Nội dung lớp mới không được để trống")
    if len(content) > 50000:
        raise ValueError("Nội dung lớp mới không được quá 50.000 ký tự")
    return {"title": title, "date": class_date, "content": content}


def render_classes_page(classes=None):
    classes = load_classes() if classes is None else classes
    template = CLASS_TEMPLATE_PATH.read_text(encoding="utf-8")
    cards = []
    for index, item in enumerate(classes):
        content = str(item.get("content") or "").strip()
        excerpt = " ".join(content.split())
        if len(excerpt) > 190:
            excerpt = f"{excerpt[:187].rstrip()}..."
        content_html = escape(content).replace("\n", "<br/>\n")
        cards.append(
            f'''<article class="class-card" id="lop-{escape(str(item.get("id") or ""))}">
  <div class="class-card-head">
    <div>
      <p class="class-date">{escape(format_class_date(item.get("date", "")))}</p>
      <h2>{escape(str(item.get("title") or ""))}</h2>
    </div>
    <span class="class-status">Đang tuyển gia sư</span>
  </div>
  <p class="class-excerpt">{escape(excerpt)}</p>
  <details{' open' if index == 0 else ''}>
    <summary>Xem đầy đủ danh sách lớp</summary>
    <div class="class-content">{content_html}</div>
  </details>
</article>'''
        )
    if not cards:
        cards.append(
            '<div class="empty-state"><h2>Chưa có lớp mới</h2>'
            '<p>Danh sách lớp cần gia sư sẽ được cập nhật tại đây.</p></div>'
        )
    latest = format_class_date(classes[0].get("date", "")) if classes else "—"
    rendered = template.replace("{{CLASS_ITEMS}}", "\n".join(cards))
    rendered = rendered.replace("{{UPDATED_AT}}", escape(latest))
    if running_on_vercel():
        if not github_enabled():
            raise RuntimeError(
                "Chưa cấu hình GITHUB_TOKEN trên Vercel nên chưa thể xuất trang lớp mới."
            )
        github_upsert_file(
            "giasubinhminh.com/lop-moi/index.html",
            rendered,
            "cms: publish class list",
        )
    else:
        CLASS_PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
        CLASS_PUBLIC_PATH.write_text(rendered, encoding="utf-8", newline="\n")
    return CLASS_PUBLIC_PATH

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not request_is_authenticated():
            return jsonify({"error": "Phiên đăng nhập đã hết hạn"}), 401
        if request.method in _UNSAFE_METHODS and not csrf_token_valid():
            return jsonify({"error": "Mã bảo vệ CSRF không hợp lệ"}), 403
        return fn(*args, **kwargs)

    return wrapper


def csrf_token_valid() -> bool:
    expected = session.get("csrf_token")
    supplied = request.headers.get("X-CSRF-Token", "")
    return (
        isinstance(expected, str)
        and len(expected) >= 32
        and isinstance(supplied, str)
        and hmac.compare_digest(expected, supplied)
    )


def credentials_valid(username: str, password: str) -> bool:
    username = str(username or "")
    password = str(password or "")
    env_password = os.environ.get("CMS_PASSWORD")
    if env_password:
        expected_username = os.environ.get("CMS_USERNAME", "admin")
        username_ok = hmac.compare_digest(username, expected_username)
        password_ok = hmac.compare_digest(password, env_password)
        return username_ok and password_ok

    config = load_config(fresh=running_on_vercel() and github_enabled())
    expected_username = str(config.get("username") or "admin")
    username_ok = hmac.compare_digest(username, expected_username)
    password_hash = str(config.get("password_hash") or "")
    if password_hash:
        password_ok = verify_password(password, password_hash)
        return username_ok and password_ok

    # Keep old plaintext config usable only on a local machine for migration.
    if not running_on_vercel():
        password_ok = hmac.compare_digest(password, str(config.get("password") or ""))
        return username_ok and password_ok
    return False


def credential_auth_material(config: dict) -> str:
    session_epoch = str(config.get("session_epoch") or "initial")
    env_password = os.environ.get("CMS_PASSWORD")
    if env_password:
        return "\0".join(
            (
                "environment",
                os.environ.get("CMS_USERNAME", "admin"),
                env_password,
                session_epoch,
            )
        )
    else:
        username = str(config.get("username") or "admin")
        password_hash = str(config.get("password_hash") or "")
        if password_hash:
            return "\0".join(
                ("password_hash", username, password_hash, session_epoch)
            )
        if not running_on_vercel() and config.get("password") is not None:
            return "\0".join(
                (
                    "legacy_plaintext",
                    username,
                    str(config.get("password") or ""),
                    session_epoch,
                )
            )
        return "\0".join(("disabled", username, session_epoch))


def credential_auth_version(config: dict | None = None) -> str:
    """Bind signed sessions to the active credential source and hash."""
    if config is None:
        config = load_config(
            fresh=running_on_vercel() and github_enabled()
        )
    material = credential_auth_material(config)
    signing_key = app.secret_key
    if isinstance(signing_key, str):
        signing_key = signing_key.encode("utf-8")
    return hmac.new(
        signing_key,
        material.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def request_is_authenticated() -> bool:
    if session.get("logged_in") is not True or not isinstance(
        session.get("username"),
        str,
    ):
        return False
    session_version = session.get("auth_version")
    if not isinstance(session_version, str):
        return False
    try:
        active_version = credential_auth_version()
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError):
        return False
    return hmac.compare_digest(session_version, active_version)


def client_ip_address() -> str:
    candidates = []
    if running_on_vercel():
        forwarded = request.headers.get("X-Forwarded-For", "")
        if forwarded:
            candidates.append(forwarded.split(",", 1)[0].strip())
    candidates.append(request.remote_addr or "unknown")
    for candidate in candidates:
        try:
            return ipaddress.ip_address(candidate).compressed
        except ValueError:
            continue
    return "unknown"


def login_rate_status(key: str) -> tuple[bool, int]:
    now = time.monotonic()
    window = int(app.config["LOGIN_RATE_WINDOW_SECONDS"])
    limit = int(app.config["LOGIN_RATE_LIMIT"])
    with _LOGIN_ATTEMPTS_LOCK:
        attempts = _LOGIN_ATTEMPTS.get(key)
        if attempts is None:
            return True, 0
        while attempts and attempts[0] <= now - window:
            attempts.popleft()
        if not attempts:
            _LOGIN_ATTEMPTS.pop(key, None)
            return True, 0
        if len(attempts) < limit:
            return True, 0
        return False, max(1, math.ceil(window - (now - attempts[0])))


def record_login_failure(key: str):
    now = time.monotonic()
    window = int(app.config["LOGIN_RATE_WINDOW_SECONDS"])
    with _LOGIN_ATTEMPTS_LOCK:
        attempts = _LOGIN_ATTEMPTS.setdefault(key, deque())
        while attempts and attempts[0] <= now - window:
            attempts.popleft()
        attempts.append(now)
        if len(_LOGIN_ATTEMPTS) > 4096:
            stale_keys = [
                item_key
                for item_key, timestamps in _LOGIN_ATTEMPTS.items()
                if not timestamps or timestamps[-1] <= now - window
            ]
            for item_key in stale_keys:
                _LOGIN_ATTEMPTS.pop(item_key, None)
            while len(_LOGIN_ATTEMPTS) > 4096:
                oldest_key = next(iter(_LOGIN_ATTEMPTS))
                _LOGIN_ATTEMPTS.pop(oldest_key, None)


def clear_login_failures(key: str):
    with _LOGIN_ATTEMPTS_LOCK:
        _LOGIN_ATTEMPTS.pop(key, None)


def is_editable_page(rel_path: str) -> bool:
    try:
        normalized, _ = canonical_site_path(rel_path)
    except ValueError:
        return False
    parts = PurePosixPath(normalized).parts
    if not parts or parts[-1] != "index.html":
        return False
    directories = tuple(part.casefold() for part in parts[:-1])
    if any(part.startswith(".") for part in directories):
        return False
    parts = directories
    if not parts:
        return True
    if parts[0] in BLOCKED_PREFIXES:
        return False
    if "page" in parts:
        idx = parts.index("page")
        if idx + 1 < len(parts) and parts[idx + 1].isdigit():
            return False
    if "feed" in parts:
        return False
    return True


def page_slug(rel_path: str) -> str:
    normalized, _ = canonical_site_path(rel_path)
    parts = PurePosixPath(normalized).parts[:-1]
    return "/" if not parts else "/".join(parts)


def page_public_url(rel_path: str) -> str:
    slug = page_slug(rel_path)
    if slug == "/":
        return "/giasubinhminh.com/index.html"
    return f"/giasubinhminh.com/{slug.strip('/')}/index.html"


def read_page_file(rel_path: str, fresh: bool = False) -> str:
    if not is_editable_page(rel_path):
        raise ValueError("Trang không được phép chỉnh sửa")
    normalized, path = canonical_site_path(rel_path)
    if fresh and running_on_vercel():
        repo_path = f"giasubinhminh.com/{normalized}"
        return github_read_file(repo_path).decode("utf-8", errors="ignore")
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def write_page_file(rel_path: str, content: str):
    if not is_editable_page(rel_path):
        raise ValueError("Trang không được phép chỉnh sửa")
    normalized, path = canonical_site_path(rel_path)
    if running_on_vercel():
        if not github_enabled():
            raise RuntimeError(
                "Chưa cấu hình GITHUB_TOKEN trên Vercel nên chưa thể lưu nội dung."
            )
        repo_path = f"giasubinhminh.com/{normalized}"
        github_upsert_file(
            repo_path,
            content,
            f"cms: update {repo_path}",
        )
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(content)


def find_entry_content(soup: BeautifulSoup):
    for div in soup.find_all("div"):
        classes = div.get("class") or []
        if "entry-content" in classes and "single-page" in classes:
            return div
    return soup.select_one(".entry-content")


def extract_text(tag):
    if not tag:
        return ""
    return tag.get_text(strip=True)


def parse_page_rating(soup: BeautifulSoup) -> tuple[float | None, int | None]:
    rating = soup.select_one(".kk-star-ratings[data-payload]")
    if not rating:
        return None, None
    try:
        payload = json.loads(rating.get("data-payload") or "{}")
        return float(payload.get("score")), int(payload.get("count"))
    except (TypeError, ValueError, json.JSONDecodeError):
        return None, None


def parse_page(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("title")
    meta_desc = soup.find("meta", attrs={"name": "description"})
    og_title = soup.find("meta", property="og:title")
    heading = soup.select_one("h1.entry-title")
    entry = find_entry_content(soup)
    thumbnail = ""
    thumb_img = soup.select_one(".entry-image img")
    if thumb_img and thumb_img.get("src"):
        thumbnail = thumb_img["src"]

    page_type = "post" if entry else "page"
    content = ""
    if entry:
        content = entry.decode_contents()
    rating_score, rating_count = parse_page_rating(soup)

    return {
        "title": extract_text(title_tag),
        "description": meta_desc.get("content", "") if meta_desc else "",
        "og_title": og_title.get("content", "") if og_title else "",
        "heading": extract_text(heading),
        "thumbnail": thumbnail,
        "content": content,
        "page_type": page_type,
        "has_entry_content": bool(entry),
        "rating_score": rating_score,
        "rating_count": rating_count,
    }


def update_meta_content(soup: BeautifulSoup, name: str, value: str, attr_name="name"):
    tag = soup.find("meta", attrs={attr_name: name})
    if tag:
        tag["content"] = value
    else:
        head = soup.find("head")
        if head:
            new_tag = soup.new_tag("meta")
            new_tag[attr_name] = name
            new_tag["content"] = value
            head.append(new_tag)


def update_jsonld_rating(value, score: float, count: int):
    if isinstance(value, dict):
        aggregate = value.get("aggregateRating")
        if isinstance(aggregate, dict):
            aggregate["ratingValue"] = score
            aggregate["ratingCount"] = count
            if "reviewCount" in aggregate:
                aggregate["reviewCount"] = count
        for child in value.values():
            update_jsonld_rating(child, score, count)
    elif isinstance(value, list):
        for child in value:
            update_jsonld_rating(child, score, count)


def apply_rating_updates(soup: BeautifulSoup, score_value, count_value):
    if score_value in (None, "") and count_value in (None, ""):
        return

    current_score, current_count = parse_page_rating(soup)
    if current_score is None:
        return

    try:
        score = current_score if score_value in (None, "") else float(score_value)
        count = current_count if count_value in (None, "") else int(count_value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Điểm sao hoặc số bình chọn không hợp lệ") from exc

    score = max(0.0, min(5.0, round(score, 1)))
    count = max(0, count or 0)
    score_text = f"{score:.1f}"
    legend_text = f"{score_text}/5 - ({count} bình chọn)"

    for rating in soup.select(".kk-star-ratings[data-payload]"):
        try:
            payload = json.loads(rating.get("data-payload") or "{}")
        except json.JSONDecodeError:
            payload = {}
        size = float(payload.get("size") or 24)
        gap = float(payload.get("gap") or 4)
        width = max(0.0, score * (size + gap) - (gap / 2))
        payload["score"] = score_text
        payload["count"] = str(count)
        payload["legend"] = legend_text
        payload["width"] = f"{width:.1f}"
        rating["data-payload"] = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        active = rating.select_one(".kksr-stars-active")
        if active:
            active["style"] = f"width: {width:.1f}px;"
        legend = rating.select_one(".kksr-legend")
        if legend:
            legend.string = legend_text

    for script in soup.select('script[type="application/ld+json"]'):
        try:
            structured = json.loads(script.string or script.get_text() or "")
        except (TypeError, json.JSONDecodeError):
            continue
        update_jsonld_rating(structured, score, count)
        script.string = json.dumps(structured, ensure_ascii=False, separators=(",", ":"))


def apply_page_updates(html: str, data: dict) -> str:
    soup = BeautifulSoup(html, "html.parser")

    if data.get("title"):
        title = str(data["title"]).strip()[:300]
        title_tag = soup.find("title")
        if title_tag:
            title_tag.string = title
        update_meta_content(soup, "og:title", title, "property")
        update_meta_content(soup, "twitter:title", title)

    if "description" in data:
        description = str(data.get("description") or "").strip()[:1000]
        update_meta_content(soup, "description", description)
        update_meta_content(soup, "og:description", description, "property")
        update_meta_content(soup, "twitter:description", description)

    if data.get("heading"):
        heading = soup.select_one("h1.entry-title")
        if heading:
            heading.clear()
            heading.append(str(data["heading"]).strip()[:300])

    if data.get("thumbnail"):
        thumbnail = str(data["thumbnail"]).strip()
        if not valid_public_image_url(thumbnail):
            raise ValueError("Đường dẫn ảnh đại diện không hợp lệ")
        thumb_img = soup.select_one(".entry-image img")
        if thumb_img:
            thumb_img["src"] = thumbnail

    if "content" in data:
        entry = find_entry_content(soup)
        if entry is not None:
            entry.clear()
            fragment = BeautifulSoup(
                sanitize_rich_html(data.get("content")),
                "html.parser",
            )
            for child in list(fragment.children):
                entry.append(child)

    apply_rating_updates(soup, data.get("rating_score"), data.get("rating_count"))

    return str(soup)


@lru_cache(maxsize=512)
def page_list_metadata(rel_path: str) -> tuple[str, bool]:
    """Read a concise Vietnamese title without parsing the full archived page."""
    try:
        if not is_editable_page(rel_path):
            return "", False
        _, path = canonical_site_path(rel_path)
    except ValueError:
        return "", False
    if not path.is_file():
        return "", False
    try:
        with open(path, encoding="utf-8", errors="ignore") as source:
            preview = source.read(600_000)
    except OSError:
        return "", False

    title_match = re.search(r"<title\b[^>]*>(.*?)</title>", preview, re.I | re.S)
    raw_title = title_match.group(1) if title_match else ""
    title_text = BeautifulSoup(raw_title, "html.parser").get_text(" ", strip=True)
    is_redirect = bool(
        re.search(
            r"<meta\b[^>]*http-equiv=[\"']?refresh[\"']?[^>]*>",
            preview,
            re.I,
        )
    ) or title_text.casefold() == "page has moved"
    if is_redirect:
        return "", True

    heading_match = re.search(
        r"<h1\b[^>]*class=[\"'][^\"']*\bentry-title\b[^\"']*[\"'][^>]*>(.*?)</h1>",
        preview,
        re.I | re.S,
    )
    if heading_match:
        heading_text = BeautifulSoup(
            heading_match.group(1), "html.parser"
        ).get_text(" ", strip=True)
        if heading_text:
            return heading_text, False
    return title_text, False


def collect_pages():
    if running_on_vercel():
        pages = []
        prefix = "giasubinhminh.com/"
        catalog = load_page_titles(fresh=github_enabled())
        saved_titles = catalog["titles"]
        redirects = set(catalog["redirects"])
        for item in github_repository_tree():
            repo_path = str(item.get("path") or "")
            if item.get("type") != "blob" or not repo_path.startswith(prefix):
                continue
            rel = repo_path[len(prefix) :]
            if not is_editable_page(rel):
                continue
            if rel in redirects:
                continue
            slug = page_slug(rel)
            title = saved_titles.get(rel, "")
            local_title, is_redirect = page_list_metadata(rel)
            if is_redirect:
                continue
            if not title:
                title = local_title
            if slug == "/":
                title = "Trang chủ"
            elif not title:
                title = slug.rsplit("/", 1)[-1].replace("-", " ").strip().title()
            pages.append(
                {
                    "id": rel,
                    "slug": slug,
                    "title": title or slug,
                    "page_type": "page",
                    "editable_content": True,
                    "public_url": page_public_url(rel),
                }
            )
        pages.sort(key=lambda page: page["title"].lower())
        return pages

    pages = []
    catalog = load_page_titles()
    saved_titles = catalog["titles"]
    redirects = set(catalog["redirects"])
    for root, _, files in os.walk(SITE_DIR):
        for name in files:
            if name != "index.html":
                continue
            full = Path(root) / name
            rel = full.relative_to(SITE_DIR).as_posix()
            if not is_editable_page(rel):
                continue
            if rel in redirects:
                continue
            list_title, is_redirect = page_list_metadata(rel)
            if is_redirect:
                continue
            title = saved_titles.get(rel) or list_title or page_slug(rel)
            pages.append(
                {
                    "id": rel,
                    "slug": page_slug(rel),
                    "title": title,
                    "page_type": "page",
                    "editable_content": True,
                    "public_url": page_public_url(rel),
                }
            )
    pages.sort(key=lambda p: p["title"].lower())
    return pages


def collect_media(limit=200, search=""):
    if running_on_vercel():
        media = []
        prefix = "giasubinhminh.com/wp-content/uploads/"
        extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
        for item in github_repository_tree():
            repo_path = str(item.get("path") or "")
            if item.get("type") != "blob" or not repo_path.startswith(prefix):
                continue
            name = repo_path.rsplit("/", 1)[-1]
            if legacy_media_filename(name):
                continue
            if Path(name).suffix.lower() not in extensions:
                continue
            if search and search.lower() not in name.lower():
                continue
            rel = repo_path[len("giasubinhminh.com/") :]
            media.append(
                {
                    "name": name,
                    "path": rel,
                    "url": f"/giasubinhminh.com/{rel}",
                    "size": item.get("size") or 0,
                }
            )
        media.sort(key=lambda image: image["name"].lower())
        return media[:limit]

    media = []
    uploads = SITE_DIR / "wp-content" / "uploads"
    if not uploads.exists():
        return media
    exts = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
    for root, _, files in os.walk(uploads):
        for name in files:
            ext = Path(name).suffix.lower()
            if legacy_media_filename(name):
                continue
            if ext not in exts:
                continue
            if search and search.lower() not in name.lower():
                continue
            full = Path(root) / name
            rel = full.relative_to(SITE_DIR).as_posix()
            media.append(
                {
                    "name": name,
                    "path": rel,
                    "url": f"/giasubinhminh.com/{rel}",
                    "size": full.stat().st_size,
                }
            )
    media.sort(key=lambda m: m["name"].lower())
    return media[:limit]


def legacy_media_filename(filename: str) -> bool:
    normalized = str(filename or "").casefold()
    return bool(re.search(r"(?:htcon|binh[-_.\s]*minh)", normalized))


def validate_image_upload(file_storage) -> tuple[bytes, str, int, int]:
    original_name = str(file_storage.filename or "")
    extension = Path(original_name).suffix.casefold()
    allowed_extensions = {
        suffix
        for suffixes in ALLOWED_IMAGE_FORMATS.values()
        for suffix in suffixes
    }
    if extension not in allowed_extensions:
        raise ValueError("Chỉ hỗ trợ ảnh raster JPEG, PNG, GIF hoặc WebP")

    maximum = int(app.config["MAX_IMAGE_UPLOAD_BYTES"])
    raw = file_storage.stream.read(maximum + 1)
    if not raw:
        raise ValueError("Tệp ảnh trống")
    if len(raw) > maximum:
        raise ValueError(
            f"Ảnh vượt quá giới hạn {maximum // (1024 * 1024)} MB"
        )

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(raw)) as image:
                detected_format = str(image.format or "").upper()
                width, height = image.size
                frame_count = int(getattr(image, "n_frames", 1) or 1)
                image.verify()
    except (
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        UnidentifiedImageError,
        OSError,
        SyntaxError,
        ValueError,
    ) as exc:
        raise ValueError("Nội dung tệp không phải ảnh hợp lệ") from exc

    if detected_format not in ALLOWED_IMAGE_FORMATS:
        raise ValueError("Định dạng ảnh không hỗ trợ")
    if extension not in ALLOWED_IMAGE_FORMATS[detected_format]:
        raise ValueError("Phần mở rộng tệp không khớp với nội dung ảnh")
    if (
        width < 1
        or height < 1
        or width > MAX_IMAGE_DIMENSION
        or height > MAX_IMAGE_DIMENSION
        or width * height > MAX_IMAGE_PIXELS
    ):
        raise ValueError("Kích thước ảnh vượt quá giới hạn cho phép")
    if frame_count > MAX_ANIMATION_FRAMES:
        raise ValueError("Ảnh động có quá nhiều khung hình")
    if frame_count > 1 and width * height * frame_count > MAX_IMAGE_PIXELS * 2:
        raise ValueError("Tổng kích thước ảnh động vượt quá giới hạn")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(raw)) as image:
                for frame_index in range(frame_count):
                    image.seek(frame_index)
                    frame_width, frame_height = image.size
                    if (
                        frame_width < 1
                        or frame_height < 1
                        or frame_width > MAX_IMAGE_DIMENSION
                        or frame_height > MAX_IMAGE_DIMENSION
                    ):
                        raise ValueError("Khung hình có kích thước không hợp lệ")
                    image.load()
    except (
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        UnidentifiedImageError,
        EOFError,
        OSError,
        SyntaxError,
        ValueError,
    ) as exc:
        raise ValueError("Không thể giải mã toàn bộ tệp ảnh") from exc
    return raw, extension, width, height


@app.after_request
def add_admin_security_headers(response):
    path = request.path
    if path in {"/admin", "/api"} or path.startswith(("/admin/", "/api/")):
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = (
            "camera=(), geolocation=(), microphone=(), payment=(), usb=()"
        )
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        if path.startswith("/api/"):
            response.headers["Content-Security-Policy"] = (
                "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
            )
        else:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; base-uri 'none'; object-src 'none'; "
                "frame-ancestors 'none'; form-action 'self'; "
                "script-src 'self' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; connect-src 'self'; "
                "font-src 'self' data:"
            )
        if production_mode():
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
    return response


@app.errorhandler(RequestEntityTooLarge)
def request_too_large(_error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Yêu cầu hoặc tệp tải lên quá lớn"}), 413
    return "Request too large", 413


@app.route("/admin")
@app.route("/admin/")
def admin_home():
    return send_from_directory(ADMIN_DIR / "static", "index.html")


@app.post("/api/login")
def api_login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username") or "").strip()
    password = str(data.get("password") or "")
    rate_key = client_ip_address()
    allowed, retry_after = login_rate_status(rate_key)
    if not allowed:
        response = jsonify(
            {"error": "Quá nhiều lần đăng nhập thất bại. Vui lòng thử lại sau."}
        )
        response.status_code = 429
        response.headers["Retry-After"] = str(retry_after)
        return response
    if credentials_valid(username, password):
        clear_login_failures(rate_key)
        session.clear()
        session["logged_in"] = True
        session["username"] = username
        session["csrf_token"] = secrets.token_urlsafe(32)
        try:
            session["auth_version"] = credential_auth_version()
        except (OSError, RuntimeError, ValueError, json.JSONDecodeError):
            session.clear()
            return jsonify({"error": "Không thể xác minh cấu hình đăng nhập"}), 503
        return jsonify(
            {
                "ok": True,
                "username": username,
                "csrf_token": session["csrf_token"],
            }
        )
    record_login_failure(rate_key)
    return jsonify({"error": "Sai tên đăng nhập hoặc mật khẩu"}), 401


@app.post("/api/logout")
@login_required
def api_logout():
    session.clear()
    return jsonify({"ok": True})


@app.get("/api/health")
def api_health():
    return jsonify(
        {
            "ok": True,
            "version": "1",
            "publishing_ready": not running_on_vercel() or github_enabled(),
        }
    )


@app.get("/api/me")
def api_me():
    if request_is_authenticated():
        return jsonify(
            {
                "logged_in": True,
                "username": session.get("username"),
                "csrf_token": session.get("csrf_token"),
                "publishing_ready": not running_on_vercel() or github_enabled(),
            }
        )
    return jsonify({"logged_in": False})


@app.get("/api/pages")
@login_required
def api_pages():
    search = (request.args.get("search") or "").strip().lower()
    pages = collect_pages()
    if search:
        pages = [p for p in pages if search in p["title"].lower() or search in p["slug"].lower()]
    return jsonify({"pages": pages, "total": len(pages)})


@app.get("/api/pages/<path:page_id>")
@login_required
def api_get_page(page_id):
    if not is_editable_page(page_id):
        return jsonify({"error": "Trang không được phép chỉnh sửa"}), 400
    try:
        html = read_page_file(page_id, fresh=running_on_vercel())
        parsed = parse_page(html)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    return jsonify(
        {
            "id": page_id,
            "slug": page_slug(page_id),
            "public_url": page_public_url(page_id),
            **parsed,
        }
    )


@app.put("/api/pages/<path:page_id>")
@login_required
def api_update_page(page_id):
    if not is_editable_page(page_id):
        return jsonify({"error": "Trang không được phép chỉnh sửa"}), 400
    data = request.get_json(silent=True) or {}
    try:
        html = read_page_file(page_id, fresh=running_on_vercel())
        updated = apply_page_updates(html, data)
        write_page_file(page_id, updated)
        display_title = str(data.get("heading") or data.get("title") or "").strip()
        if display_title:
            catalog = load_page_titles(fresh=running_on_vercel() and github_enabled())
            clean_title = BeautifulSoup(
                display_title, "html.parser"
            ).get_text(" ", strip=True)
            if catalog["titles"].get(page_id) != clean_title:
                catalog["titles"][page_id] = clean_title
                save_page_titles(catalog)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    message = "Đã lưu bài viết"
    if running_on_vercel():
        message += " — website đang cập nhật, vui lòng chờ khoảng 1 phút"
    return jsonify({"ok": True, "message": message})


@app.get("/api/media")
@login_required
def api_media():
    search = (request.args.get("search") or "").strip()
    return jsonify({"media": collect_media(search=search)})


@app.post("/api/media/upload")
@login_required
def api_upload_media():
    if "file" not in request.files:
        return jsonify({"error": "Không có file"}), 400
    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Tên file không hợp lệ"}), 400

    try:
        raw, ext, width, height = validate_image_upload(file)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    now = datetime.now()
    filename = f"{uuid.uuid4().hex}{ext}"
    rel = f"wp-content/uploads/cms/{now.year}/{now.month:02d}/{filename}"

    try:
        if running_on_vercel():
            if not github_enabled():
                return jsonify(
                    {
                        "error": (
                            "Chưa cấu hình GITHUB_TOKEN trên Vercel nên "
                            "chưa thể tải ảnh."
                        )
                    }
                ), 500
            github_upsert_file(
                f"giasubinhminh.com/{rel}",
                raw,
                f"cms: upload {rel}",
                binary=True,
            )
        else:
            _, save_path = canonical_site_path(rel)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.write_bytes(raw)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify(
        {
            "ok": True,
            "name": filename,
            "path": rel,
            "url": f"/giasubinhminh.com/{rel}",
            "width": width,
            "height": height,
            "size_label": f"{width} × {height} px",
        }
    )


def parse_feedback_gallery(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    section = soup.select_one("#parent-feedback-gallery")
    if not section:
        return {
            "images": [],
        }
    images = []
    for figure in section.select(".feedback-item")[:6]:
        image = figure.select_one("img")
        images.append(
            {
                "url": image.get("src", "") if image else "",
                "alt": image.get("alt", "") if image else "",
            }
        )
    return {
        "images": images,
        "public_url": page_public_url(FEEDBACK_PAGE_ID),
    }


def parse_homepage_feedback_gallery(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    images = []
    for image in soup.select(".testimonial-collage img")[
        :HOMEPAGE_FEEDBACK_IMAGE_COUNT
    ]:
        images.append(
            {
                "url": image.get("src", ""),
                "alt": image.get("alt", ""),
            }
        )
    return images


def valid_feedback_image_url(value: str) -> bool:
    return valid_public_image_url(value)


def apply_feedback_updates(html: str, data: dict) -> str:
    soup = BeautifulSoup(html, "html.parser")
    section = soup.select_one("#parent-feedback-gallery")
    if not section:
        raise ValueError("Không tìm thấy khối phản hồi phụ huynh trên trang")

    images = data.get("images") or []
    figures = section.select(".feedback-item")[:6]
    for index, figure in enumerate(figures):
        if index >= len(images):
            break
        item = images[index] or {}
        url = str(item.get("url") or "").strip()
        if url:
            if not valid_feedback_image_url(url):
                raise ValueError(f"Đường dẫn ảnh phản hồi {index + 1} không hợp lệ")
            image = figure.select_one("img")
            link = figure.select_one("a")
            if image:
                image["src"] = url
                image["alt"] = str(
                    item.get("alt")
                    or f"Phản hồi của phụ huynh về gia sư Trí Việt {index + 1}"
                ).strip()
            if link:
                link["href"] = url
    return str(soup)


@app.get("/api/feedback")
@login_required
def api_get_feedback():
    config = load_config(fresh=running_on_vercel() and github_enabled())
    configured = config.get("feedback_images")
    homepage_configured = config.get("homepage_feedback_images")
    feedback_images = None
    homepage_images = None
    if isinstance(configured, list) and len(configured) == FEEDBACK_IMAGE_COUNT:
        feedback_images = normalize_feedback_images(configured)
    if (
        isinstance(homepage_configured, list)
        and len(homepage_configured) == HOMEPAGE_FEEDBACK_IMAGE_COUNT
    ):
        homepage_images = normalize_homepage_feedback_images(homepage_configured)

    try:
        if feedback_images is None:
            html = read_page_file(FEEDBACK_PAGE_ID, fresh=running_on_vercel())
            feedback_images = normalize_feedback_images(
                parse_feedback_gallery(html).get("images")
            )
        if homepage_images is None:
            homepage_html = read_page_file(
                "index.html",
                fresh=running_on_vercel(),
            )
            homepage_images = normalize_homepage_feedback_images(
                parse_homepage_feedback_gallery(homepage_html)
            )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    return jsonify(
        {
            "images": feedback_images,
            "homepage_images": homepage_images,
            "public_url": page_public_url(FEEDBACK_PAGE_ID),
            "homepage_public_url": page_public_url("index.html"),
        }
    )


@app.put("/api/feedback")
@login_required
def api_update_feedback():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "Dữ liệu phản hồi không hợp lệ"}), 400
    try:
        images = normalize_feedback_images(
            data.get("images", data.get("feedback_images")),
            strict=True,
        )
        homepage_images = normalize_homepage_feedback_images(
            data.get(
                "homepage_images",
                data.get("homepage_feedback_images"),
            ),
            strict=True,
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    try:
        def update_feedback(config: dict):
            config["feedback_images"] = images
            config["homepage_feedback_images"] = homepage_images
            return config

        mutate_config_atomic(
            update_feedback,
            publish_public=True,
            message="cms: update parent feedback galleries",
        )
    except (RuntimeError, OSError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 500
    message = "Đã lưu phần phản hồi phụ huynh"
    if running_on_vercel():
        message += " — website đang cập nhật, vui lòng chờ khoảng 1 phút"
    return jsonify(
        {
            "ok": True,
            "message": message,
            "images": images,
            "homepage_images": homepage_images,
        }
    )


@app.get("/api/classes")
@login_required
def api_classes():
    try:
        classes = load_classes()
        if not running_on_vercel() and not CLASS_PUBLIC_PATH.exists():
            render_classes_page(classes)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    return jsonify(
        {
            "classes": classes,
            "total": len(classes),
            "public_url": "/giasubinhminh.com/lop-moi/index.html",
        }
    )


@app.post("/api/classes")
@login_required
def api_create_class():
    data = request.get_json(silent=True) or {}
    try:
        clean = normalize_class_payload(data)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    now = datetime.now().isoformat(timespec="seconds")
    item = {
        "id": uuid.uuid4().hex[:10],
        **clean,
        "created_at": now,
        "updated_at": now,
    }
    try:
        classes = load_classes()
        classes.append(item)
        classes.sort(
            key=lambda entry: (entry.get("date", ""), entry.get("created_at", "")),
            reverse=True,
        )
        save_classes(classes)
        render_classes_page(classes)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    message = "Đã đăng lớp mới"
    if running_on_vercel():
        message += " — website đang cập nhật"
    return jsonify({"ok": True, "message": message, "item": item}), 201


@app.put("/api/classes/<class_id>")
@login_required
def api_update_class(class_id):
    data = request.get_json(silent=True) or {}
    try:
        clean = normalize_class_payload(data)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    try:
        classes = load_classes()
        item = next((entry for entry in classes if entry.get("id") == class_id), None)
        if item is None:
            return jsonify({"error": "Không tìm thấy bài lớp mới"}), 404
        item.update(clean)
        item["updated_at"] = datetime.now().isoformat(timespec="seconds")
        classes.sort(
            key=lambda entry: (entry.get("date", ""), entry.get("created_at", "")),
            reverse=True,
        )
        save_classes(classes)
        render_classes_page(classes)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    message = "Đã cập nhật lớp mới"
    if running_on_vercel():
        message += " — website đang cập nhật"
    return jsonify({"ok": True, "message": message, "item": item})


@app.delete("/api/classes/<class_id>")
@login_required
def api_delete_class(class_id):
    try:
        classes = load_classes()
        kept = [entry for entry in classes if entry.get("id") != class_id]
        if len(kept) == len(classes):
            return jsonify({"error": "Không tìm thấy bài lớp mới"}), 404
        save_classes(kept)
        render_classes_page(kept)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    message = "Đã xóa bài lớp mới"
    if running_on_vercel():
        message += " — website đang cập nhật"
    return jsonify({"ok": True, "message": message})


def set_deep_text(tag, text: str) -> bool:
    if not tag:
        return False
    current = tag
    while True:
        children = [c for c in current.children if getattr(c, "name", None)]
        if len(children) == 1:
            current = children[0]
        else:
            break
    current.clear()
    current.append(text)
    return True


def resolve_site_image_path(src: str) -> Path | None:
    if not src:
        return None
    clean = src.strip().replace("\\", "/")
    if clean.startswith("http://") or clean.startswith("https://"):
        # local clone paths sometimes keep absolute originals; try last path segment under uploads
        marker = "/wp-content/"
        idx = clean.find(marker)
        if idx >= 0:
            clean = clean[idx + 1 :]
        else:
            return None
    if clean.startswith("/giasubinhminh.com/"):
        clean = clean[len("/giasubinhminh.com/") :]
    if clean.startswith("/"):
        clean = clean.lstrip("/")
    try:
        _, path = canonical_site_path(clean)
    except ValueError:
        return None
    return path if path.is_file() else None


def get_image_size(src: str) -> dict:
    path = resolve_site_image_path(src)
    if not path:
        return {"width": None, "height": None, "size_label": "Chưa có ảnh"}
    try:
        from PIL import Image

        with Image.open(path) as img:
            width, height = img.size
        return {
            "width": width,
            "height": height,
            "size_label": f"{width} × {height} px",
        }
    except Exception:
        return {"width": None, "height": None, "size_label": "Không đọc được khổ ảnh"}


SLIDER_BANNER_IDS = (
    "banner-75206964",
    "banner-443370161",
    "banner-1738321284",
)


def extract_css_bg(html: str, selector_id: str) -> str:
    pattern = rf"#{re.escape(selector_id)}\s*\.bg\.bg-loaded\s*\{{[^}}]*background-image:\s*url\((['\"]?)([^)'\"]+)\1\)"
    match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
    return match.group(2).strip() if match else ""


def replace_css_bg(html: str, selector_id: str, image_url: str) -> str:
    if not image_url:
        return html
    image_url = str(image_url).strip()
    if not valid_public_image_url(image_url):
        raise ValueError("Đường dẫn ảnh slide không hợp lệ")
    pattern = rf"(#{re.escape(selector_id)}\s*\.bg\.bg-loaded\s*\{{[^}}]*background-image:\s*url\()(['\"]?)([^)'\"]+)\2(\))"
    quoted_url = json.dumps(image_url, ensure_ascii=False)

    def _repl(match):
        return f"{match.group(1)}{quoted_url}{match.group(4)}"

    updated, count = re.subn(pattern, _repl, html, count=1, flags=re.IGNORECASE | re.DOTALL)
    return updated if count else html


def parse_homepage(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("title")
    meta_desc = soup.find("meta", attrs={"name": "description"})

    logo = ""
    logo_img = soup.select_one("#logo .header_logo, #logo .header-logo")
    if logo_img and logo_img.get("src"):
        logo = logo_img["src"]
    logo_size = get_image_size(logo)

    slides = []
    for banner_id in SLIDER_BANNER_IDS:
        image = extract_css_bg(html, banner_id)
        size = get_image_size(image)
        slides.append(
            {
                "id": banner_id,
                "image": image,
                "width": size["width"],
                "height": size["height"],
                "size_label": size["size_label"],
            }
        )

    why = soup.select_one("#section_1675344263")
    why_title = ""
    why_subtitle = ""
    why_features = []
    if why:
        why_title = extract_text(why.select_one(".why-choose > .col h2"))
        why_subtitle = extract_text(why.select_one(".why-choose > .col p.p1"))
        for col in why.select(".why-choose > .col")[1:5]:
            why_features.append(
                {
                    "title": extract_text(col.select_one("h3")),
                    "text": extract_text(col.select_one("p.p1")),
                }
            )

    subjects = soup.select_one("#section_12457")
    subjects_title = extract_text(subjects.select_one("h2")) if subjects else ""
    subjects_intro = extract_text(subjects.select_one("p.wp-title")) if subjects else ""

    commit = soup.select_one("#section_1521040097")
    commit_title = ""
    commit_items = []
    commit_image = ""
    if commit:
        commit_title = extract_text(commit.select_one("h2.wp-heading-header"))
        for p in commit.select(".icon-box-text p"):
            commit_items.append(extract_text(p))
        img = commit.select_one("#image_1812503763 img")
        if img and img.get("src"):
            commit_image = img["src"]

    banner = soup.select_one("#section_134981638")
    banner_title = extract_text(banner.select_one("h2")) if banner else ""
    banner_subtitle = extract_text(banner.select_one("h3")) if banner else ""
    banner_cta = ""
    banner_phone = ""
    if banner:
        strong = banner.select_one("p strong")
        banner_cta = extract_text(strong)
        phone = banner.select_one("a.button span")
        banner_phone = extract_text(phone)

    team = soup.select_one("#section_1404580446")
    team_title = extract_text(team.select_one("h2")) if team else ""
    teacher_title = ""
    teacher_html = ""
    student_title = ""
    student_html = ""
    register_label = ""
    if team:
        cols = team.select(".row > .col")
        if len(cols) >= 1:
            teacher_title = extract_text(cols[0].select_one("h3"))
            ul = cols[0].select_one("ul")
            teacher_html = ul.decode_contents() if ul else ""
        if len(cols) >= 2:
            student_title = extract_text(cols[1].select_one("h3"))
            ul = cols[1].select_one("ul")
            student_html = ul.decode_contents() if ul else ""
        btn = team.select_one("a.button span")
        register_label = extract_text(btn)

    tutors_section = soup.select_one("#section_203571188")
    tutors_title = ""
    tutors = []
    if tutors_section:
        tutors_title = extract_text(tutors_section.select_one("h2"))
        for box in tutors_section.select("#row-441710802 .box")[:4]:
            img = box.select_one(".box-image img")
            tutors.append(
                {
                    "title": extract_text(box.select_one("h4")),
                    "text": extract_text(box.select_one(".box-text-inner p")),
                    "image": img.get("src", "") if img else "",
                }
            )

    while len(why_features) < 4:
        why_features.append({"title": "", "text": ""})
    while len(commit_items) < 7:
        commit_items.append("")
    while len(tutors) < 4:
        tutors.append({"title": "", "text": "", "image": ""})

    return {
        "title": extract_text(title_tag),
        "description": meta_desc.get("content", "") if meta_desc else "",
        "public_url": "/giasubinhminh.com/index.html",
        "logo": logo,
        "logo_width": logo_size["width"],
        "logo_height": logo_size["height"],
        "logo_size_label": logo_size["size_label"],
        "logo_recommended": LOGO_RECOMMENDED,
        "slide_recommended": SLIDE_RECOMMENDED,
        "slides": slides,
        "why_title": why_title,
        "why_subtitle": why_subtitle,
        "why_features": why_features[:4],
        "subjects_title": subjects_title,
        "subjects_intro": subjects_intro,
        "commit_title": commit_title,
        "commit_items": commit_items[:7],
        "commit_image": commit_image,
        "banner_title": banner_title,
        "banner_subtitle": banner_subtitle,
        "banner_cta": banner_cta,
        "banner_phone": banner_phone,
        "team_title": team_title,
        "teacher_title": teacher_title,
        "teacher_html": teacher_html,
        "student_title": student_title,
        "student_html": student_html,
        "register_label": register_label,
        "tutors_title": tutors_title,
        "tutors": tutors[:4],
    }


def apply_homepage_updates(html: str, data: dict) -> str:
    soup = BeautifulSoup(html, "html.parser")

    if data.get("title"):
        title = str(data["title"]).strip()[:300]
        title_tag = soup.find("title")
        if title_tag:
            title_tag.string = title
        update_meta_content(soup, "og:title", title, "property")

    if "description" in data:
        description = str(data.get("description") or "").strip()[:1000]
        update_meta_content(soup, "description", description)
        update_meta_content(soup, "og:description", description, "property")

    if data.get("logo"):
        logo = str(data["logo"]).strip()
        if not valid_public_image_url(logo):
            raise ValueError("Đường dẫn logo không hợp lệ")
        for tag in soup.select("#logo .header_logo, #logo .header-logo, #logo .header-logo-dark"):
            tag["src"] = logo

    html = str(soup)
    slides = data.get("slides") or []
    for idx, banner_id in enumerate(SLIDER_BANNER_IDS):
        if idx >= len(slides):
            break
        image = str((slides[idx] or {}).get("image") or "").strip()
        if image:
            html = replace_css_bg(html, banner_id, image)
    soup = BeautifulSoup(html, "html.parser")

    why = soup.select_one("#section_1675344263")
    if why:
        if data.get("why_title"):
            set_deep_text(why.select_one(".why-choose > .col h2"), data["why_title"])
        if "why_subtitle" in data:
            set_deep_text(why.select_one(".why-choose > .col p.p1"), data.get("why_subtitle") or "")
        features = data.get("why_features") or []
        cols = why.select(".why-choose > .col")[1:5]
        for idx, col in enumerate(cols):
            if idx >= len(features):
                break
            item = features[idx] or {}
            if item.get("title"):
                set_deep_text(col.select_one("h3"), item["title"])
            if "text" in item:
                set_deep_text(col.select_one("p.p1"), item.get("text") or "")

    subjects = soup.select_one("#section_12457")
    if subjects:
        if data.get("subjects_title"):
            set_deep_text(subjects.select_one("h2"), data["subjects_title"])
        if "subjects_intro" in data:
            set_deep_text(subjects.select_one("p.wp-title"), data.get("subjects_intro") or "")

    commit = soup.select_one("#section_1521040097")
    if commit:
        if data.get("commit_title"):
            set_deep_text(commit.select_one("h2.wp-heading-header"), data["commit_title"])
        items = data.get("commit_items") or []
        for idx, p in enumerate(commit.select(".icon-box-text p")):
            if idx >= len(items):
                break
            set_deep_text(p, items[idx] or "")
        if data.get("commit_image"):
            commit_image = str(data["commit_image"]).strip()
            if not valid_public_image_url(commit_image):
                raise ValueError("Đường dẫn ảnh cam kết không hợp lệ")
            img = commit.select_one("#image_1812503763 img")
            if img:
                img["src"] = commit_image

    banner = soup.select_one("#section_134981638")
    if banner:
        if data.get("banner_title"):
            set_deep_text(banner.select_one("h2"), data["banner_title"])
        if "banner_subtitle" in data:
            set_deep_text(banner.select_one("h3"), data.get("banner_subtitle") or "")
        if "banner_cta" in data:
            strong = banner.select_one("p strong")
            if strong:
                strong.string = data.get("banner_cta") or ""
        if data.get("banner_phone"):
            phone = banner.select_one("a.button span")
            if phone:
                phone.string = data["banner_phone"]

    team = soup.select_one("#section_1404580446")
    if team:
        if data.get("team_title"):
            set_deep_text(team.select_one("h2"), data["team_title"])
        cols = team.select(".row > .col")
        if len(cols) >= 1:
            if data.get("teacher_title"):
                set_deep_text(cols[0].select_one("h3"), data["teacher_title"])
            if "teacher_html" in data:
                ul = cols[0].select_one("ul")
                if ul is not None:
                    ul.clear()
                    fragment = BeautifulSoup(
                        sanitize_rich_html(data.get("teacher_html")),
                        "html.parser",
                    )
                    for child in list(fragment.children):
                        ul.append(child)
        if len(cols) >= 2:
            if data.get("student_title"):
                set_deep_text(cols[1].select_one("h3"), data["student_title"])
            if "student_html" in data:
                ul = cols[1].select_one("ul")
                if ul is not None:
                    ul.clear()
                    fragment = BeautifulSoup(
                        sanitize_rich_html(data.get("student_html")),
                        "html.parser",
                    )
                    for child in list(fragment.children):
                        ul.append(child)
        if data.get("register_label"):
            btn = team.select_one("a.button span")
            if btn:
                btn.string = data["register_label"]

    tutors_section = soup.select_one("#section_203571188")
    if tutors_section:
        if data.get("tutors_title"):
            set_deep_text(tutors_section.select_one("h2"), data["tutors_title"])
        tutors = data.get("tutors") or []
        boxes = tutors_section.select("#row-441710802 .box")[:4]
        for idx, box in enumerate(boxes):
            if idx >= len(tutors):
                break
            item = tutors[idx] or {}
            if item.get("title"):
                set_deep_text(box.select_one("h4"), item["title"])
            if "text" in item:
                set_deep_text(box.select_one(".box-text-inner p"), item.get("text") or "")
            if item.get("image"):
                tutor_image = str(item["image"]).strip()
                if not valid_public_image_url(tutor_image):
                    raise ValueError(
                        f"Đường dẫn ảnh gia sư {idx + 1} không hợp lệ"
                    )
                img = box.select_one(".box-image img")
                if img:
                    img["src"] = tutor_image

    return str(soup)


@app.get("/api/homepage")
@login_required
def api_get_homepage():
    try:
        html = read_page_file("index.html", fresh=running_on_vercel())
        parsed = parse_homepage(html)
        config = load_config(
            fresh=running_on_vercel() and github_enabled()
        )
        canonical_logo = build_public_site_config(config)["logo"]
        logo_size = get_image_size(canonical_logo)
        parsed.update(
            {
                "logo": canonical_logo,
                "logo_width": logo_size["width"],
                "logo_height": logo_size["height"],
                "logo_size_label": logo_size["size_label"],
            }
        )
        return jsonify(parsed)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.put("/api/homepage")
@login_required
def api_update_homepage():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "Dữ liệu trang chủ không hợp lệ"}), 400
    requested_logo = str(data.get("logo") or "").strip()
    try:
        def homepage_changes(_config, reader):
            html = reader(HOMEPAGE_REPO_PATH).decode(
                "utf-8",
                errors="ignore",
            )
            return {
                HOMEPAGE_REPO_PATH: apply_homepage_updates(html, data)
            }

        if requested_logo:
            def update_logo(config: dict):
                config["logo"] = requested_logo
                config["feedback_images"] = normalize_feedback_images(
                    config.get("feedback_images")
                )
                config["homepage_feedback_images"] = (
                    normalize_homepage_feedback_images(
                        config.get("homepage_feedback_images")
                    )
                )
                return config

            mutate_config_atomic(
                update_logo,
                publish_public=True,
                extra_changes_builder=homepage_changes,
                message="cms: update homepage and shared logo",
            )
        else:
            def build_homepage_only(reader):
                changes = homepage_changes(None, reader)
                return changes, None

            atomic_repository_update(
                build_homepage_only,
                message="cms: update homepage",
            )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    message = "Đã lưu trang chủ"
    if running_on_vercel():
        message += " — website đang cập nhật, vui lòng chờ khoảng 1 phút"
    return jsonify(
        {
            "ok": True,
            "message": message,
            "logo": requested_logo or None,
        }
    )


@app.get("/api/settings")
@login_required
def api_get_settings():
    try:
        config = load_config(fresh=running_on_vercel() and github_enabled())
        public = build_public_site_config(config)
        if not all(key in config for key in ("logo", "hotline1", "hotline2")):
            try:
                homepage_html = read_page_file(
                    "index.html",
                    fresh=running_on_vercel(),
                )
            except (OSError, RuntimeError, ValueError):
                homepage_html = ""
            if homepage_html:
                soup = BeautifulSoup(homepage_html, "html.parser")
                logo_img = soup.select_one(".header_logo, .header-logo")
                if (
                    "logo" not in config
                    and logo_img
                    and valid_public_image_url(logo_img.get("src", ""))
                ):
                    public["logo"] = logo_img["src"]
                phones = re.findall(r"Hotline\s*:\s*([^<]+)", homepage_html)
                if "hotline1" not in config and len(phones) >= 1:
                    public["hotline1"] = phones[0].strip()[:50]
                if "hotline2" not in config and len(phones) >= 2:
                    public["hotline2"] = phones[1].strip()[:50]
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify(
        {
            "site_name": public["site_name"],
            "logo": public["logo"],
            "hotline1": public["hotline1"],
            "hotline2": public["hotline2"],
            "username": config.get("username", "admin"),
            "drive_folder_url": configured_drive_folder_url(),
            "publishing_ready": not running_on_vercel() or github_enabled(),
        }
    )


@app.put("/api/settings")
@login_required
def api_update_settings():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify({"error": "Dữ liệu cài đặt không hợp lệ"}), 400

    updates = {}
    password_changed = False
    new_password_hash = None
    new_session_epoch = None

    if "site_name" in data:
        site_name = str(data.get("site_name") or "").strip()
        if not site_name or len(site_name) > 160:
            return jsonify({"error": "Tên website phải có từ 1 đến 160 ký tự"}), 400
        updates["site_name"] = site_name

    if "logo" in data:
        logo = str(data.get("logo") or "").strip()
        if not valid_public_image_url(logo):
            return jsonify({"error": "Đường dẫn logo không hợp lệ"}), 400
        updates["logo"] = logo

    for key in ("hotline1", "hotline2"):
        if key not in data:
            continue
        hotline = str(data.get(key) or "").strip()
        if not re.fullmatch(r"[0-9+().\s-]{3,50}", hotline):
            return jsonify({"error": "Số hotline không hợp lệ"}), 400
        updates[key] = hotline

    if data.get("new_password"):
        if os.environ.get("CMS_PASSWORD"):
            return jsonify(
                {
                    "error": (
                        "Mật khẩu đang được quản lý bằng biến CMS_PASSWORD "
                        "trên Vercel."
                    )
                }
            ), 400
        new_password = str(data["new_password"])
        if len(new_password) < 12:
            return jsonify({"error": "Mật khẩu mới phải có ít nhất 12 ký tự"}), 400
        new_password_hash = hash_password(new_password)
        new_session_epoch = secrets.token_hex(16)
        password_changed = True

    try:
        def update_settings(config: dict):
            config.setdefault("site_name", DEFAULT_SITE_NAME)
            config.setdefault("logo", DEFAULT_LOGO)
            config.setdefault("hotline1", DEFAULT_HOTLINE1)
            config.setdefault("hotline2", DEFAULT_HOTLINE2)
            config.update(updates)
            config["feedback_images"] = normalize_feedback_images(
                config.get("feedback_images")
            )
            config["homepage_feedback_images"] = (
                normalize_homepage_feedback_images(
                    config.get("homepage_feedback_images")
                )
            )
            if password_changed:
                config["password_hash"] = new_password_hash
                config["session_epoch"] = new_session_epoch
                config.pop("password", None)
            return config

        config = mutate_config_atomic(
            update_settings,
            publish_public=True,
            message="cms: update website settings",
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    message = "Đã cập nhật cài đặt website"
    if running_on_vercel():
        message += " — website đang cập nhật"
    if password_changed:
        session.clear()
    return jsonify(
        {
            "ok": True,
            "message": message,
            "reauthenticate": password_changed,
            **build_public_site_config(config),
        }
    )


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_site(path):
    public_prefix = "giasubinhminh.com"
    if path != public_prefix and not path.startswith(f"{public_prefix}/"):
        return jsonify({"error": "Not found"}), 404
    rel_path = path[len(public_prefix) :].lstrip("/")
    if public_path_is_sensitive(rel_path):
        return jsonify({"error": "Not found"}), 404
    try:
        _, target = canonical_site_path(rel_path, allow_empty=True)
    except ValueError:
        return jsonify({"error": "Not found"}), 404
    if target.is_dir():
        index = target / "index.html"
        if index.is_file():
            resolved_index = index.resolve()
            try:
                resolved_index.relative_to(SITE_DIR.resolve())
            except ValueError:
                return jsonify({"error": "Not found"}), 404
            return send_from_directory(resolved_index.parent, resolved_index.name)
    if target.is_file():
        return send_from_directory(target.parent, target.name)
    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    print("CMS Admin: http://localhost:5050/admin")
    print("Website:   http://localhost:5050/giasubinhminh.com/index.html")
    print("Login: use the CMS credentials supplied by the site owner")
    app.run(host="0.0.0.0", port=5050, debug=False)
