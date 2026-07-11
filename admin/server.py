import json
import os
import re
import uuid
from datetime import datetime
from functools import wraps
from pathlib import Path

from bs4 import BeautifulSoup
from flask import Flask, jsonify, request, send_from_directory, session

BASE_DIR = Path(__file__).resolve().parent.parent
SITE_DIR = BASE_DIR / "giasubinhminh.com"
ADMIN_DIR = Path(__file__).resolve().parent
CONFIG_PATH = ADMIN_DIR / "config.json"
UPLOAD_DIR = SITE_DIR / "wp-content" / "uploads" / "cms"
SLIDE_RECOMMENDED = {"width": 1360, "height": 540}
LOGO_RECOMMENDED = {"width": 186, "height": 100}

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
app.secret_key = os.environ.get("CMS_SECRET", "tri-viet-cms-local-secret")


def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return jsonify({"error": "Unauthorized"}), 401
        return fn(*args, **kwargs)

    return wrapper


def is_editable_page(rel_path: str) -> bool:
    if not rel_path.endswith("index.html"):
        return False
    parts = Path(rel_path).parts[:-1]
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
    parts = Path(rel_path).parts[:-1]
    return "/" if not parts else "/".join(parts)


def page_public_url(rel_path: str) -> str:
    slug = page_slug(rel_path)
    if slug == "/":
        return "/giasubinhminh.com/index.html"
    return f"/giasubinhminh.com/{slug.strip('/')}/index.html"


def read_page_file(rel_path: str) -> str:
    path = SITE_DIR / rel_path.replace("/", os.sep)
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def write_page_file(rel_path: str, content: str):
    path = SITE_DIR / rel_path.replace("/", os.sep)
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

    return {
        "title": extract_text(title_tag),
        "description": meta_desc.get("content", "") if meta_desc else "",
        "og_title": og_title.get("content", "") if og_title else "",
        "heading": extract_text(heading),
        "thumbnail": thumbnail,
        "content": content,
        "page_type": page_type,
        "has_entry_content": bool(entry),
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


def apply_page_updates(html: str, data: dict) -> str:
    soup = BeautifulSoup(html, "html.parser")

    if data.get("title"):
        title_tag = soup.find("title")
        if title_tag:
            title_tag.string = data["title"]
        update_meta_content(soup, "og:title", data["title"], "property")
        update_meta_content(soup, "twitter:title", data["title"])

    if "description" in data:
        update_meta_content(soup, "description", data["description"] or "")
        update_meta_content(soup, "og:description", data["description"] or "", "property")
        update_meta_content(soup, "twitter:description", data["description"] or "")

    if data.get("heading"):
        heading = soup.select_one("h1.entry-title")
        if heading:
            heading.clear()
            heading.append(BeautifulSoup(data["heading"], "html.parser"))

    if data.get("thumbnail"):
        thumb_img = soup.select_one(".entry-image img")
        if thumb_img:
            thumb_img["src"] = data["thumbnail"]

    if "content" in data:
        entry = find_entry_content(soup)
        if entry is not None:
            entry.clear()
            fragment = BeautifulSoup(data["content"] or "", "html.parser")
            for child in list(fragment.children):
                entry.append(child)

    return str(soup)


def collect_pages():
    pages = []
    for root, _, files in os.walk(SITE_DIR):
        for name in files:
            if name != "index.html":
                continue
            full = Path(root) / name
            rel = full.relative_to(SITE_DIR).as_posix()
            if not is_editable_page(rel):
                continue
            try:
                html = read_page_file(rel)
                parsed = parse_page(html)
            except OSError:
                continue
            pages.append(
                {
                    "id": rel,
                    "slug": page_slug(rel),
                    "title": parsed["title"] or parsed["heading"] or page_slug(rel),
                    "page_type": parsed["page_type"],
                    "editable_content": parsed["has_entry_content"],
                    "public_url": page_public_url(rel),
                }
            )
    pages.sort(key=lambda p: p["title"].lower())
    return pages


def collect_media(limit=200, search=""):
    media = []
    uploads = SITE_DIR / "wp-content" / "uploads"
    if not uploads.exists():
        return media
    exts = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
    for root, _, files in os.walk(uploads):
        for name in files:
            ext = Path(name).suffix.lower()
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


@app.route("/admin")
@app.route("/admin/")
def admin_home():
    return send_from_directory(ADMIN_DIR / "static", "index.html")


@app.post("/api/login")
def api_login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    config = load_config()
    if username == config.get("username") and password == config.get("password", ""):
        session["logged_in"] = True
        session["username"] = username
        return jsonify({"ok": True, "username": username})
    return jsonify({"error": "Sai tên đăng nhập hoặc mật khẩu"}), 401


@app.post("/api/logout")
def api_logout():
    session.clear()
    return jsonify({"ok": True})


@app.get("/api/me")
def api_me():
    if session.get("logged_in"):
        return jsonify({"logged_in": True, "username": session.get("username")})
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
    html = read_page_file(page_id)
    parsed = parse_page(html)
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
    html = read_page_file(page_id)
    updated = apply_page_updates(html, data)
    write_page_file(page_id, updated)
    return jsonify({"ok": True, "message": "Đã lưu bài viết"})


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

    ext = Path(file.filename).suffix.lower()
    allowed = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
    if ext not in allowed:
        return jsonify({"error": "Định dạng ảnh không hỗ trợ"}), 400

    now = datetime.now()
    folder = UPLOAD_DIR / str(now.year) / f"{now.month:02d}"
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    save_path = folder / filename
    file.save(save_path)

    rel = save_path.relative_to(SITE_DIR).as_posix()
    size = get_image_size(rel)
    return jsonify(
        {
            "ok": True,
            "name": filename,
            "path": rel,
            "url": f"/giasubinhminh.com/{rel}",
            "width": size["width"],
            "height": size["height"],
            "size_label": size["size_label"],
        }
    )


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
    path = SITE_DIR / clean.replace("/", os.sep)
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
    pattern = rf"(#{re.escape(selector_id)}\s*\.bg\.bg-loaded\s*\{{[^}}]*background-image:\s*url\()(['\"]?)([^)'\"]+)\2(\))"

    def _repl(match):
        return f"{match.group(1)}{image_url}{match.group(4)}"

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
        title_tag = soup.find("title")
        if title_tag:
            title_tag.string = data["title"]
        update_meta_content(soup, "og:title", data["title"], "property")

    if "description" in data:
        update_meta_content(soup, "description", data["description"] or "")
        update_meta_content(soup, "og:description", data["description"] or "", "property")

    if data.get("logo"):
        for tag in soup.select("#logo .header_logo, #logo .header-logo, #logo .header-logo-dark"):
            tag["src"] = data["logo"]

    html = str(soup)
    slides = data.get("slides") or []
    for idx, banner_id in enumerate(SLIDER_BANNER_IDS):
        if idx >= len(slides):
            break
        image = (slides[idx] or {}).get("image") or ""
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
            img = commit.select_one("#image_1812503763 img")
            if img:
                img["src"] = data["commit_image"]

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
                    ul.append(BeautifulSoup(data.get("teacher_html") or "", "html.parser"))
        if len(cols) >= 2:
            if data.get("student_title"):
                set_deep_text(cols[1].select_one("h3"), data["student_title"])
            if "student_html" in data:
                ul = cols[1].select_one("ul")
                if ul is not None:
                    ul.clear()
                    ul.append(BeautifulSoup(data.get("student_html") or "", "html.parser"))
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
                img = box.select_one(".box-image img")
                if img:
                    img["src"] = item["image"]

    return str(soup)


@app.get("/api/homepage")
@login_required
def api_get_homepage():
    html = read_page_file("index.html")
    return jsonify(parse_homepage(html))


@app.put("/api/homepage")
@login_required
def api_update_homepage():
    data = request.get_json(silent=True) or {}
    html = read_page_file("index.html")
    updated = apply_homepage_updates(html, data)
    write_page_file("index.html", updated)
    return jsonify({"ok": True, "message": "Đã lưu trang chủ"})


@app.get("/api/settings")
@login_required
def api_get_settings():
    config = load_config()
    homepage = SITE_DIR / "index.html"
    logo = "wp-content/uploads/2018/07/logo-1.png"
    hotline1 = "096.31.38.511"
    hotline2 = "0987.115.131"
    if homepage.exists():
        soup = BeautifulSoup(read_page_file("index.html"), "html.parser")
        logo_img = soup.select_one(".header_logo, .header-logo")
        if logo_img and logo_img.get("src"):
            logo = logo_img["src"]
        phones = re.findall(r"Hotline\s*:\s*([^<]+)", read_page_file("index.html"))
        if len(phones) >= 1:
            hotline1 = phones[0].strip()
        if len(phones) >= 2:
            hotline2 = phones[1].strip()

    return jsonify(
        {
            "site_name": config.get("site_name", "Trung Tâm Gia Sư Trí Việt"),
            "logo": logo,
            "hotline1": hotline1,
            "hotline2": hotline2,
            "username": config.get("username", "admin"),
        }
    )


@app.put("/api/settings")
@login_required
def api_update_settings():
    data = request.get_json(silent=True) or {}
    config = load_config()

    if data.get("site_name"):
        config["site_name"] = data["site_name"]
    if data.get("new_password"):
        config["password"] = data["new_password"]
    save_config(config)

    site_name = config.get("site_name", "Trung Tâm Gia Sư Trí Việt")
    logo = data.get("logo")
    hotline1 = data.get("hotline1")
    hotline2 = data.get("hotline2")

    for root, _, files in os.walk(SITE_DIR):
        for name in files:
            if not name.endswith(".html"):
                continue
            rel = (Path(root) / name).relative_to(SITE_DIR).as_posix()
            if rel.startswith("wp-content/"):
                continue
            try:
                html = read_page_file(rel)
            except OSError:
                continue
            changed = False
            if site_name and site_name not in html:
                pass
            soup = BeautifulSoup(html, "html.parser")
            if site_name:
                for tag in soup.select(".header-top-heading h3"):
                    tag.string = site_name
                    changed = True
                for tag in soup.find_all("img", class_=lambda c: c and ("header-logo" in c or "header_logo" in c)):
                    tag["alt"] = site_name
                    changed = True
                for a in soup.select('#logo a[rel="home"]'):
                    a["title"] = site_name
                    changed = True
            if logo:
                for tag in soup.select(".header_logo, .header-logo, .header-logo-dark"):
                    tag["src"] = logo
                    changed = True
            if hotline1 or hotline2:
                buttons = soup.select(".header-button a.button")
                if hotline1 and len(buttons) >= 1:
                    span = buttons[0].find("span")
                    if span:
                        span.string = f"Hotline : {hotline1}"
                        changed = True
                if hotline2 and len(buttons) >= 2:
                    span = buttons[1].find("span")
                    if span:
                        span.string = f"Hotline : {hotline2}"
                        changed = True
            if changed:
                write_page_file(rel, str(soup))

    return jsonify({"ok": True, "message": "Đã cập nhật cài đặt website"})


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_site(path):
    if path.startswith("api/") or path.startswith("admin/"):
        return jsonify({"error": "Not found"}), 404
    target = BASE_DIR / path
    if target.is_dir():
        index = target / "index.html"
        if index.exists():
            return send_from_directory(target, "index.html")
    if target.is_file():
        return send_from_directory(target.parent, target.name)
    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    print("CMS Admin: http://localhost:5050/admin")
    print("Website:   http://localhost:5050/giasubinhminh.com/index.html")
    print("Login: admin / admin123")
    app.run(host="0.0.0.0", port=5050, debug=False)
