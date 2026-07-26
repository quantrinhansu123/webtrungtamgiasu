from __future__ import annotations

import html
import re
from pathlib import Path
from urllib.parse import unquote


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
LOGO_SRC = f"{ASSET_ROOT}/b60442c2c31d48ab8146e213a27ac28c.jpg"
FEEDBACK_GALLERY = (
    '<span aria-label="Phản hồi của phụ huynh về gia sư Trí Việt" '
    'class="tri-viet-feedback-gallery" role="group" '
    'style="display:grid;gap:14px;grid-template-columns:repeat('
    'auto-fit,minmax(240px,1fr));margin:20px auto;max-width:980px;">'
    + "".join(
        (
            f'<a href="{ASSET_ROOT}/feedback/fb{index}.jpg" '
            'rel="noopener" target="_blank">'
            f'<img alt="Phản hồi của phụ huynh về gia sư Trí Việt {index}" '
            'decoding="async" loading="lazy" '
            f'src="{ASSET_ROOT}/feedback/fb{index}.jpg" '
            'style="background:#f6f8fb;border-radius:10px;box-shadow:'
            '0 3px 12px rgba(15,52,96,.12);height:100%;max-height:560px;'
            'object-fit:contain;width:100%;"/></a>'
        )
        for index in range(1, 7)
    )
    + "</span>"
)

IMG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
HEADING_RE = re.compile(r"<h[1-4]\b[^>]*>.*?</h[1-4]>", re.IGNORECASE | re.DOTALL)
TEXT_NODE_RE = re.compile(r"(?<=>)([^<]+)(?=<)")
ASSET_REFERENCE_RE = re.compile(
    r"""[^"'=<>\s]*wp-content(?:\\/|/)[^"'<>\s]+""",
    re.IGNORECASE,
)

ONLINE_PRICE_RE = re.compile(r"2021/05/Gia-su-chung-ONLINE", re.IGNORECASE)
LOGO_RE = re.compile(
    r"(?:"
    r"2018/07/logo-1\.png"
    r"|(?:2018/(?:09|12)|2020/07)/(?:20139779_|22046752_)"
    r")",
    re.IGNORECASE,
)
LANGUAGE_PRICE_RE = re.compile(
    r"(?:"
    r"(?:2018/09)/Gia-SU-IELTS"
    r"|2018/11/Gia-su-Tieng-Anh"
    r"|2020/08/Gia-su-Tieng-(?:Han|Nhat|Trung)"
    r"|2024/05/Bang-Gia-Tieng-(?:Han|Nhat|Phap|Trung)"
    r")",
    re.IGNORECASE,
)
GENERAL_PRICE_RE = re.compile(
    r"(?:"
    r"(?:2018/09|2024/05)/Bang-Gia-Toan-[0-9]+"
    r"|2018/11/Bang-Gia-Vat-LY"
    r"|2018/11/Gia-su-Toan"
    r"|2020/08/Gia-su-HOA"
    r"|2020/08/GIA-SU-Van"
    r"|2023/03/HOC-PHI-GIA-SU-TAI-NHA"
    r"|2024/04/Gia-su-LOP-(?:9|12)"
    r"|2018/10/hoc-phi-gia-su-tai-nha"
    r"|2018/09/hoc-phi-gia-su-lop-6"
    r")",
    re.IGNORECASE,
)
TEAM_RE = re.compile(
    r"(?:"
    r"2018/09/1-1(?:-300x225)?\.jpg"
    r"|2018/10/1-300x225\.jpg"
    r"|2018/09/gia-su(?:%cc|̛|ư).*ha(?:%cc|̀|à).*no"
    r"|2021/05/2-1-(?:150x150|300x300|768x768|1024x1024)"
    r"|2021/05/2-1\.png"
    r"|(?:2018/09|2024/05)/DOI-NGU-GIA-SU"
    r"|2023/03/Doi-ngu-Gia-su-HTCON"
    r"|2020/07/ADS-HTCON"
    r")",
    re.IGNORECASE,
)
FEEDBACK_RE = re.compile(
    r"(?:2018/09|2024/05)/FEEDBACK-GIA-SU",
    re.IGNORECASE,
)

# Markers below were verified visually against every raster asset under
# wp-content/uploads. They cover images whose pixels still contain the old
# Bình Minh/HTcon names or logos even when the filename itself looks generic.
LEGACY_BRAND_MARKERS = tuple(
    marker.casefold()
    for marker in (
        "2018/07/logo-1.png",
        "2018/09/20139779_",
        "2018/09/22046752_",
        "2018/12/22046752_",
        "2020/07/22046752_",
        "2018/09/gia-su-binh-minh-cam-ket",
        "2018/09/gia-su-luyen-thi-ielts-tai-nha",
        "2018/09/gia-su-lop-8-300x127",
        "2018/09/gia-su-lop-8-bao-nhieu-tien",
        "2018/09/gia-su-mon-toan-lop-10",
        "2018/09/gia-su-tieng-anh-cho-nguoi-da-di-lam",
        "2018/09/gia-su-tieng-anh-cho-nguoi-di-lam",
        "2018/09/gia-su-toan-lop-9-luyen-thi-vao-lop-10",
        "2018/09/GSBM-QUY-DINH-HOC-THU",
        "2018/09/hinh-thuc-hoc-gia-su-tai-nha",
        "2018/09/hoc-sinh-lop-5-can-hoc-gia-su",
        "2018/09/ly-do-nen-thue-gia-su-toan-lop-3",
        "2018/09/nen-thue-sinh-vien-hay-giao-vien",
        "2018/09/quyen-loi-khi-den-voi-trung-tam",
        "2018/09/Toan-6.png",
        "2018/09/Toan-7.png",
        "2018/09/Toan-8.png",
        "2018-10-26-lu",
        "2018/10/gia-su-van-lop-8-copy",
        "2018/10/hoc-gia-su-la-gi",
        "2018/10/kho-khan-khi-hoc-mon-van",
        "2018/10/kinh-nghiem-lua-chon-gia-su-phu-hop-cho-con",
        "2018/10/quyen-loi-khi-den-voi-trung-tam-gia-su-binh-minh",
        "2018/11/Gia-su-hoa-300x169",
        "2018/11/Gia-su-la-ai-300x212",
        "2018/11/GIA-SU-TIEU-HOC",
        "2018/11/GIA-SU-TOAN-CAP-2",
        "2018/11/GIA-SU-VAT-LY",
        "2018/11/gia-su-van",
        "2018/11/hoc-gia-su-la-gi",
        "2018/11/hoc-thu-750x340",
        "2018/11/hoc-thu-gia-su-tai-nha",
        "2018/11/nen-lua-chon-gia-su-la-sinh-vien-hay-giao-vien",
        "2018/11/trung-tam-gia-su-binh-minh",
        "2018/11/Xanh-la-nhat-Mau-kem-Hien-dai-Toi-gian",
        "2020/07/1.png",
        "2020/07/1-300x300.png",
        "2020/07/QUY-DINH-HOC-THU",
        "2020/08/GIA-SU-HOA-1",
        "2020/08/gia-su-mon-dia",
        "2020/08/gia-su-mon-ly",
        "2020/08/gia-su-mon-su",
        "2020/08/gia-su-tieng-han",
        "2020/08/gia-su-tieng-nhat",
        "2020/08/Gia-su-Tieng-Trung",
        "2020/08/GIA-SU-Van-1",
        "2021/03/gia-su-mon-lich-su",
        "2021/06/hoc-thu-gsbm",
        "2021/06/trung-tam-gia-su-binh-minh",
        "2023/03/CHINH-SACH-HOC-THU",
        "2024/05/GIA-SU-NGOAI-NGU",
        "2024/05/QUY-DINH-HOC-THU",
        "2024/05/Toan-12",
        "2024/05/Toan-9",
    )
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


def normalized_image_tag(tag: str) -> str:
    return unquote(html.unescape(tag)).replace("\\", "/").casefold()


def replace_legacy_image(match: re.Match[str]) -> str:
    tag = match.group(0)
    normalized_tag = normalized_image_tag(tag)
    if FEEDBACK_RE.search(normalized_tag):
        return FEEDBACK_GALLERY
    if LOGO_RE.search(normalized_tag):
        cleaned_tag = re.sub(
            r"""\s+(?:sizes|srcset)=(["']).*?\1""",
            "",
            tag,
            flags=re.IGNORECASE,
        )
        cleaned_tag = re.sub(
            r"""\bsrc=(["']).*?\1""",
            f'src="{LOGO_SRC}"',
            cleaned_tag,
            count=1,
            flags=re.IGNORECASE,
        )
        return cleaned_tag
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
    if any(marker in normalized_tag for marker in LEGACY_BRAND_MARKERS):
        return BRAND_IMAGE
    return tag


def replacement_asset_path(normalized_reference: str) -> str | None:
    if FEEDBACK_RE.search(normalized_reference):
        return f"{ASSET_ROOT}/feedback/fb1.jpg"
    if LOGO_RE.search(normalized_reference):
        return LOGO_SRC
    if ONLINE_PRICE_RE.search(normalized_reference):
        return f"{ASSET_ROOT}/bang-gia-gia-su-online-tri-viet.svg"
    if LANGUAGE_PRICE_RE.search(normalized_reference):
        return f"{ASSET_ROOT}/bang-gia-gia-su-ngoai-ngu-tri-viet.svg"
    if GENERAL_PRICE_RE.search(normalized_reference):
        return f"{ASSET_ROOT}/bang-gia-gia-su-tai-nha-tri-viet.svg"
    if TEAM_RE.search(normalized_reference):
        return f"{ASSET_ROOT}/anh-co-giao-dang-day.jpg"
    if BRAND_RE.search(normalized_reference):
        return f"{ASSET_ROOT}/banner-trung-tam-gia-su-tri-viet.png"
    if any(marker in normalized_reference for marker in LEGACY_BRAND_MARKERS):
        return f"{ASSET_ROOT}/banner-trung-tam-gia-su-tri-viet.png"
    return None


def replace_legacy_asset_references(content: str) -> str:
    def replace_reference(match: re.Match[str]) -> str:
        raw_reference = match.group(0)
        normalized_reference = unquote(
            html.unescape(raw_reference.replace("\\/", "/"))
        ).casefold()
        replacement = replacement_asset_path(normalized_reference)
        if replacement is None:
            return raw_reference

        if normalized_reference.startswith(("http://", "https://", "//")):
            replacement = f"https://giasutriviet.vercel.app{replacement}"
        if "\\/" in raw_reference:
            replacement = replacement.replace("/", "\\/")
        return replacement

    return ASSET_REFERENCE_RE.sub(replace_reference, content)


def replace_corrupted_bullet_markers(content: str) -> str:
    # The original blue-diamond emoji (U+1F539) was captured as one or four
    # literal question marks in the static mirror. Only repair a marker at the
    # beginning of a text node; real Vietnamese questions end with "?" and are
    # therefore left untouched.
    content = re.sub(
        r">\?{4}</span>(\s*Cơ sở)",
        r">📍</span>\1",
        content,
        flags=re.IGNORECASE,
    )
    content = content.replace('alt="????"', 'alt="🔹"')
    content = content.replace("alt='????'", "alt='🔹'")

    def repair_text_node(match: re.Match[str]) -> str:
        text_node = match.group(1)
        repaired = re.sub(
            r"^(\s*)\?+(?=(?:\s|\u00a0|&nbsp;|[A-Za-zÀ-ỹ]|$))",
            r"\1🔹",
            text_node,
            count=1,
        )
        return repaired

    return TEXT_NODE_RE.sub(repair_text_node, content)


def clean_html(relative_path: str, content: str) -> tuple[str, int]:
    image_replacements = 0

    def counted_image_replace(match: re.Match[str]) -> str:
        nonlocal image_replacements
        replacement = replace_legacy_image(match)
        if replacement != match.group(0):
            image_replacements += 1
        return replacement

    cleaned = IMG_RE.sub(counted_image_replace, content)
    cleaned = replace_legacy_asset_references(cleaned)
    cleaned = OLD_FACEBOOK_RE.sub(CURRENT_FACEBOOK, cleaned)

    for pattern, replacement in VISIBLE_BRAND_REPLACEMENTS:
        cleaned = pattern.sub(replacement, cleaned)

    cleaned = replace_corrupted_bullet_markers(cleaned)
    cleaned = cleaned.replace("Array<div", "<div")
    cleaned = cleaned.replace(
        "auto-fit,minmax(180px,1fr)",
        "auto-fit,minmax(240px,1fr)",
    )

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
