from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = ROOT / "giasubinhminh.com"
ASSET_ROOT = "/giasubinhminh.com/wp-content/uploads/cms/2026/07"

GENERAL_PRICE_IMAGE = (
    f'<img alt="Bảng giá gia sư tại nhà Trung Tâm Gia Sư Trí Việt" '
    f'class="aligncenter tri-viet-owned-image" decoding="async" loading="lazy" '
    f'src="{ASSET_ROOT}/bang-gia-gia-su-tai-nha-tri-viet.svg" '
    'style="height:auto;max-width:100%;width:100%;" width="1200" height="800"/>'
)
ONLINE_PRICE_IMAGE = (
    f'<img alt="Bảng giá gia sư online Trung Tâm Gia Sư Trí Việt" '
    f'class="aligncenter tri-viet-owned-image" decoding="async" loading="lazy" '
    f'src="{ASSET_ROOT}/bang-gia-gia-su-online-tri-viet.svg" '
    'style="height:auto;max-width:100%;width:100%;" width="1200" height="800"/>'
)
LANGUAGE_PRICE_IMAGE = (
    f'<img alt="Bảng giá gia sư ngoại ngữ Trung Tâm Gia Sư Trí Việt" '
    f'class="aligncenter tri-viet-owned-image" decoding="async" loading="lazy" '
    f'src="{ASSET_ROOT}/bang-gia-gia-su-ngoai-ngu-tri-viet.svg" '
    'style="height:auto;max-width:100%;width:100%;" width="1200" height="800"/>'
)
TEAM_IMAGE = (
    f'<img alt="Hoạt động chuyên môn của Trung Tâm Gia Sư Trí Việt" '
    f'class="aligncenter tri-viet-owned-image" decoding="async" loading="lazy" '
    f'src="{ASSET_ROOT}/anh-co-giao-dang-day.jpg" '
    'style="height:auto;max-width:100%;width:100%;" width="1200" height="630"/>'
)
BRAND_IMAGE = (
    f'<img alt="Trung Tâm Gia Sư Trí Việt" '
    f'class="aligncenter tri-viet-owned-image" decoding="async" loading="lazy" '
    f'src="{ASSET_ROOT}/banner-trung-tam-gia-su-tri-viet.png" '
    'style="height:auto;max-width:100%;width:100%;" width="1672" height="941"/>'
)

IMG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
HEADING_RE = re.compile(r"<h[1-4]\b[^>]*>.*?</h[1-4]>", re.IGNORECASE | re.DOTALL)

ONLINE_PRICE_RE = re.compile(r"2021/05/Gia-su-chung-ONLINE", re.IGNORECASE)
LANGUAGE_PRICE_RE = re.compile(
    r"(?:2018/09|2024/05)/Bang-Gia-Tieng-(?:Han|Nhat|Phap|Trung)",
    re.IGNORECASE,
)
GENERAL_PRICE_RE = re.compile(
    r"(?:"
    r"(?:2018/09|2024/05)/Bang-Gia-Toan-[0-9]+"
    r"|2018/11/Bang-Gia-Vat-LY"
    r"|2023/03/HOC-PHI-GIA-SU-TAI-NHA"
    r"|2018/10/hoc-phi-gia-su-tai-nha"
    r"|2018/09/hoc-phi-gia-su-lop-6"
    r")",
    re.IGNORECASE,
)
TEAM_RE = re.compile(
    r"(?:"
    r"2021/05/2-1-(?:150x150|300x300|768x768|1024x1024)"
    r"|2021/05/2-1\.png"
    r"|(?:2018/09|2024/05)/DOI-NGU-GIA-SU"
    r"|2023/03/Doi-ngu-Gia-su-HTCON"
    r"|2020/07/ADS-HTCON"
    r")",
    re.IGNORECASE,
)
BRAND_RE = re.compile(
    r"(?:"
    r"gia-su-binh-minh-cam-ket"
    r"|quyen-loi-khi-den-voi-trung-tam(?:-gia-su)?-binh-minh"
    r"|trung-tam-gia-su-binh-minh"
    r"|2025/01/3-1(?:-[0-9]+x[0-9]+)?\.png"
    r")",
    re.IGNORECASE,
)

OLD_FACEBOOK_RE = re.compile(
    r"https://www\.facebook\.com/[^\"'<\s]*722199304473155[^\"'<\s]*",
    re.IGNORECASE,
)
CURRENT_FACEBOOK = "https://www.facebook.com/profile.php?id=100063564159935"

VISIBLE_BRAND_REPLACEMENTS = (
    (
        re.compile(
            r"Gia\s*sư\s*Bình</(?:b|strong)>\s*<(?:b|strong)>Minh",
            re.IGNORECASE,
        ),
        "Gia sư Trí</b> <b>Việt",
    ),
    (re.compile(r"Trung\s*Tâm\s*Gia\s*Sư\s*Bình\s*Minh", re.IGNORECASE), "Trung Tâm Gia Sư Trí Việt"),
    (re.compile(r"Gia\s*Sư\s*Bình\s*Minh", re.IGNORECASE), "Gia Sư Trí Việt"),
    (re.compile(r"BÌNH\s*MÌNH"), "TRÍ VIỆT"),
    (re.compile(r"Bình\s*Mình"), "Trí Việt"),
    (re.compile(r"bình\s*mình"), "Trí Việt"),
    (re.compile(r"\bHT\s*Con\b", re.IGNORECASE), "Trí Việt"),
    (re.compile(r"TẬP CHUNG"), "TẬP TRUNG"),
    (re.compile(r"Tập chung"), "Tập trung"),
    (re.compile(r"tập chung"), "tập trung"),
    (re.compile(r"PHÀN HỒI"), "PHẢN HỒI"),
    (re.compile(r"Phàn hồi"), "Phản hồi"),
    (re.compile(r"phàn hồi"), "phản hồi"),
    (re.compile(r"Hà Nồi"), "Hà Nội"),
    (re.compile(r"đếb"), "đến"),
    (re.compile(r"hokc"), "học"),
)

PRICING_SECTIONS: dict[str, tuple[str, str]] = {
    "bang-gia-500-gia-su-mon-toan-gioi-tu-lop-1-12-o-ha-noi/index.html": (
        "IV – HỌC PHÍ GIA SƯ MÔN TOÁN",
        GENERAL_PRICE_IMAGE,
    ),
    "gia-su-day-kem-tai-nha-online-tu-lop-1-12-on-thi-tat-ca-cac-mon/index.html": (
        "IV – HỌC PHÍ GIA SƯ DẠY TẠI NHÀ",
        GENERAL_PRICE_IMAGE,
    ),
    "gia-su-luyen-day-thi-ielts-co-chung-chi-ielts-8-0-cam-ket-chat-luong/index.html": (
        "IV – HỌC PHÍ GIA SƯ LUYỆN IELTS",
        LANGUAGE_PRICE_IMAGE,
    ),
    "gia-su-mon-hoa/index.html": (
        "III – HỌC PHÍ GIA SƯ MÔN HÓA",
        GENERAL_PRICE_IMAGE,
    ),
    "gia-su-mon-van/index.html": (
        "III – HỌC PHÍ GIA SƯ MÔN VĂN",
        GENERAL_PRICE_IMAGE,
    ),
    "gia-su-tieng-han/index.html": (
        "III – BẢNG GIÁ, HỌC PHÍ GIA SƯ TIẾNG HÀN",
        LANGUAGE_PRICE_IMAGE,
    ),
    "gia-su-tieng-nhat/index.html": (
        "III – BẢNG GIÁ, HỌC PHÍ GIA SƯ TIẾNG NHẬT",
        LANGUAGE_PRICE_IMAGE,
    ),
    "gia-su-tieng-trung/index.html": (
        "III – BẢNG GIÁ, HỌC PHÍ GIA SƯ TIẾNG TRUNG",
        LANGUAGE_PRICE_IMAGE,
    ),
    "top-1-gia-su-tieu-hoc-su-pham-hoc-phi-chi-tu-100k/index.html": (
        "III – HỌC PHÍ GIA SƯ DẠY KÈM TIỂU HỌC",
        GENERAL_PRICE_IMAGE,
    ),
    "top-3000-gia-su-tieng-anh-tai-nha-tang-hieu-qua-gap-5-lan/index.html": (
        "II – HỌC PHÍ GIA SƯ TIẾNG ANH",
        LANGUAGE_PRICE_IMAGE,
    ),
    "top-500-gia-su-vat-ly-gia-su-su-pham-gioi/index.html": (
        "V – HỌC PHÍ GIA SƯ MÔN LÝ",
        GENERAL_PRICE_IMAGE,
    ),
}


def replace_pricing_section_banners(relative_path: str, content: str) -> tuple[str, int]:
    config = PRICING_SECTIONS.get(relative_path)
    if not config:
        return content, 0

    heading_marker, replacement = config
    heading_start = content.find(heading_marker)
    if heading_start < 0:
        return content, 0

    next_h2 = re.search(r"<h2\b", content[heading_start + len(heading_marker) :], re.IGNORECASE)
    section_end = (
        heading_start + len(heading_marker) + next_h2.start()
        if next_h2
        else len(content)
    )
    section = content[heading_start:section_end]
    replaced = 0

    def replace_banner(match: re.Match[str]) -> str:
        nonlocal replaced
        tag = match.group(0)
        if "banner-trung-tam-gia-su-tri-viet.png" not in tag:
            return tag
        replaced += 1
        return replacement

    cleaned_section = IMG_RE.sub(replace_banner, section)
    return (
        content[:heading_start] + cleaned_section + content[section_end:],
        replaced,
    )


def replace_contextual_pricing_banners(content: str) -> tuple[str, int]:
    headings = list(HEADING_RE.finditer(content))
    heading_index = 0
    latest_heading = ""
    replaced = 0

    def contextual_replace(match: re.Match[str]) -> str:
        nonlocal heading_index, latest_heading, replaced
        tag = match.group(0)

        while heading_index < len(headings) and headings[heading_index].end() <= match.start():
            raw_heading = headings[heading_index].group(0)
            latest_heading = html.unescape(
                re.sub(r"<[^>]+>", " ", raw_heading, flags=re.DOTALL)
            )
            latest_heading = " ".join(latest_heading.split())
            heading_index += 1

        if "banner-trung-tam-gia-su-tri-viet.png" not in tag:
            return tag
        if not re.search(
            r"\b[IVX]+\s*[–-]\s*(?:BẢNG GIÁ[^–-]*?)?HỌC PHÍ",
            latest_heading,
            re.IGNORECASE,
        ):
            return tag

        replaced += 1
        if re.search(r"TIẾNG|IELTS|NGOẠI NGỮ", latest_heading, re.IGNORECASE):
            return LANGUAGE_PRICE_IMAGE
        return GENERAL_PRICE_IMAGE

    return IMG_RE.sub(contextual_replace, content), replaced


def replace_legacy_image(match: re.Match[str]) -> str:
    tag = match.group(0)
    if ONLINE_PRICE_RE.search(tag):
        return ONLINE_PRICE_IMAGE
    if LANGUAGE_PRICE_RE.search(tag):
        return LANGUAGE_PRICE_IMAGE
    if GENERAL_PRICE_RE.search(tag):
        return GENERAL_PRICE_IMAGE
    if TEAM_RE.search(tag):
        return TEAM_IMAGE
    if BRAND_RE.search(tag):
        return BRAND_IMAGE
    return tag


def clean_html(relative_path: str, content: str) -> tuple[str, int]:
    image_replacements = 0

    def counted_image_replace(match: re.Match[str]) -> str:
        nonlocal image_replacements
        replacement = replace_legacy_image(match)
        if replacement != match.group(0):
            image_replacements += 1
        return replacement

    cleaned = IMG_RE.sub(counted_image_replace, content)
    cleaned = OLD_FACEBOOK_RE.sub(CURRENT_FACEBOOK, cleaned)

    for pattern, replacement in VISIBLE_BRAND_REPLACEMENTS:
        cleaned = pattern.sub(replacement, cleaned)

    cleaned, pricing_count = replace_pricing_section_banners(relative_path, cleaned)
    image_replacements += pricing_count
    cleaned, contextual_count = replace_contextual_pricing_banners(cleaned)
    image_replacements += contextual_count

    return cleaned, image_replacements


def main() -> None:
    changed_files = 0
    replaced_images = 0

    for html_file in SITE_ROOT.rglob("*.html"):
        raw = html_file.read_bytes()
        original = raw.decode("utf-8")
        relative_path = html_file.relative_to(SITE_ROOT).as_posix()
        cleaned, image_count = clean_html(relative_path, original)
        if cleaned == original:
            continue
        html_file.write_bytes(cleaned.encode("utf-8"))
        changed_files += 1
        replaced_images += image_count

    print(f"Changed HTML files: {changed_files}")
    print(f"Replaced legacy image tags: {replaced_images}")


if __name__ == "__main__":
    main()
