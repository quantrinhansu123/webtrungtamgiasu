from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = ROOT / "giasubinhminh.com"


@dataclass(frozen=True)
class Copy:
    title: str
    body: str
    excerpt: str
    post_id: int | None = None


TOPICS: dict[str, Copy] = {
    "cam-ket-tien-bo-sau-10-buoi": Copy(
        title="Cam kết tiến bộ sau 10 buổi",
        body=(
            "Trung Tâm Gia Sư Trí Việt theo dõi tiến độ trong 10 buổi đầu theo "
            "mục tiêu đã thống nhất với phụ huynh và học sinh. Sau giai đoạn "
            "này, gia sư tổng hợp phần kiến thức đã củng cố, khó khăn còn lại "
            "và đề xuất điều chỉnh lộ trình. Mức tiến bộ thực tế phụ thuộc vào "
            "nền tảng, thời lượng học và sự phối hợp của học sinh; nội dung cam "
            "kết là quy trình theo dõi, trao đổi và điều chỉnh, không phải lời "
            "hứa về một mức điểm tuyệt đối."
        ),
        excerpt=(
            "Sau 10 buổi đầu, Trí Việt cùng phụ huynh và học sinh rà soát tiến "
            "độ để điều chỉnh lộ trình; kết quả phụ thuộc vào nền tảng và mức "
            "độ phối hợp thực tế."
        ),
        post_id=2631,
    ),
    "gia-su-luyen-hsg": Copy(
        title="Gia sư luyện HSG",
        body=(
            "Gia sư luyện học sinh giỏi của Trí Việt tập trung đánh giá nền "
            "tảng, hệ thống chuyên đề và rèn cách trình bày lời giải. Kế hoạch "
            "học được trao đổi theo môn, cấp lớp và kỳ thi mục tiêu; khối lượng "
            "bài tập được điều chỉnh theo tiến độ thực tế của học sinh."
        ),
        excerpt=(
            "Trí Việt hỗ trợ xây dựng lộ trình luyện học sinh giỏi theo môn, "
            "cấp lớp, kỳ thi mục tiêu và năng lực thực tế."
        ),
        post_id=3240,
    ),
    "gia-su-luyen-thi-dai-hoc": Copy(
        title="Gia sư luyện thi Đại Học",
        body=(
            "Gia sư luyện thi Đại học của Trí Việt hỗ trợ học sinh củng cố kiến "
            "thức, luyện dạng bài và xây kế hoạch ôn tập theo môn thi, mục tiêu "
            "và thời gian còn lại. Gia sư theo dõi lỗi sai để điều chỉnh nội "
            "dung từng buổi; kết quả phụ thuộc vào nền tảng và mức độ chủ động "
            "luyện tập của học sinh."
        ),
        excerpt=(
            "Trí Việt hỗ trợ ôn thi Đại học theo môn, mục tiêu và thời gian còn "
            "lại, chú trọng củng cố kiến thức và sửa lỗi sai."
        ),
        post_id=3242,
    ),
    "gia-su-lop-2": Copy(
        title="Gia sư lớp 2",
        body=(
            "Gia sư lớp 2 của Trí Việt hỗ trợ học sinh củng cố đọc hiểu, chính "
            "tả, phép tính và bài toán cơ bản theo chương trình đang học. Nội "
            "dung từng buổi được điều chỉnh theo khả năng tập trung, phần kiến "
            "thức còn vướng và mục tiêu của gia đình."
        ),
        excerpt=(
            "Gia sư lớp 2 Trí Việt hỗ trợ củng cố Toán, Tiếng Việt và thói quen "
            "học tập theo năng lực thực tế của học sinh."
        ),
        post_id=3217,
    ),
    "gia-su-lop-3": Copy(
        title="Gia sư lớp 3",
        body=(
            "Gia sư lớp 3 của Trí Việt đồng hành cùng học sinh ôn kiến thức "
            "trọng tâm, rèn tính toán, giải toán có lời văn, đọc hiểu và diễn "
            "đạt. Gia sư quan sát lỗi thường gặp để chọn bài tập vừa sức và "
            "hướng dẫn học sinh hình thành cách tự kiểm tra bài."
        ),
        excerpt=(
            "Gia sư lớp 3 Trí Việt hỗ trợ ôn kiến thức trọng tâm, rèn giải toán, "
            "đọc hiểu và kỹ năng tự kiểm tra bài."
        ),
        post_id=3219,
    ),
    "gia-su-lop-4": Copy(
        title="Gia sư lớp 4",
        body=(
            "Gia sư lớp 4 của Trí Việt giúp học sinh hệ thống kiến thức Toán và "
            "Tiếng Việt trọng tâm, luyện cách phân tích đề và trình bày bài rõ "
            "ràng. Lộ trình ưu tiên lấp phần kiến thức chưa chắc trước khi mở "
            "rộng bài tập theo mục tiêu của học sinh."
        ),
        excerpt=(
            "Gia sư lớp 4 Trí Việt giúp hệ thống kiến thức, rèn phân tích đề và "
            "trình bày bài theo tiến độ của học sinh."
        ),
        post_id=3221,
    ),
    "gia-su-lop-5": Copy(
        title="Gia sư lớp 5",
        body=(
            "Gia sư lớp 5 của Trí Việt hỗ trợ học sinh củng cố kiến thức cuối "
            "cấp tiểu học, rèn kỹ năng làm bài và chuẩn bị nền tảng lên lớp 6. "
            "Nội dung học bám phần còn yếu của từng môn, kết hợp hướng dẫn ghi "
            "chép và tự ôn tập."
        ),
        excerpt=(
            "Gia sư lớp 5 Trí Việt hỗ trợ củng cố kiến thức cuối cấp, rèn kỹ "
            "năng làm bài và chuẩn bị nền tảng lên lớp 6."
        ),
        post_id=3223,
    ),
    "gia-su-lop-6": Copy(
        title="Gia sư lớp 6",
        body=(
            "Gia sư lớp 6 của Trí Việt hỗ trợ học sinh thích nghi với cách học "
            "ở bậc trung học cơ sở, củng cố kiến thức từng môn và rèn phương "
            "pháp ghi chép, làm bài. Kế hoạch học được xây dựng từ những phần "
            "học sinh còn vướng và điều chỉnh theo tiến độ trên lớp."
        ),
        excerpt=(
            "Gia sư lớp 6 Trí Việt hỗ trợ chuyển tiếp lên THCS, củng cố từng "
            "môn và xây dựng phương pháp học phù hợp."
        ),
        post_id=3226,
    ),
    "gia-su-lop-7": Copy(
        title="Gia sư lớp 7",
        body=(
            "Gia sư lớp 7 của Trí Việt giúp học sinh rà soát kiến thức nền, "
            "hiểu bản chất bài học và luyện các dạng bài theo từng môn. Gia sư "
            "theo dõi lỗi sai, hướng dẫn cách tự học và điều chỉnh khối lượng "
            "bài tập theo khả năng tiếp thu."
        ),
        excerpt=(
            "Gia sư lớp 7 Trí Việt giúp rà soát kiến thức nền, luyện dạng bài "
            "và cải thiện phương pháp tự học."
        ),
        post_id=3228,
    ),
    "gia-su-lop-8": Copy(
        title="Gia sư lớp 8",
        body=(
            "Gia sư lớp 8 của Trí Việt hỗ trợ học sinh củng cố các chuyên đề "
            "trọng tâm, xử lý phần kiến thức hổng và rèn cách vận dụng vào bài "
            "tập. Lộ trình đồng thời chuẩn bị nền tảng cho lớp 9 nhưng vẫn bám "
            "sát nhu cầu và tiến độ hiện tại của học sinh."
        ),
        excerpt=(
            "Gia sư lớp 8 Trí Việt hỗ trợ củng cố chuyên đề, lấp kiến thức hổng "
            "và chuẩn bị nền tảng cho lớp 9."
        ),
        post_id=3230,
    ),
    "gia-su-lop-9": Copy(
        title="Gia sư lớp 9",
        body=(
            "Gia sư lớp 9 của Trí Việt hỗ trợ học sinh hệ thống kiến thức THCS, "
            "luyện kỹ năng làm bài và ôn thi vào lớp 10 khi có nhu cầu. Kế "
            "hoạch học được chia theo môn, phần kiến thức còn yếu và mốc thời "
            "gian thực tế, không áp dụng một lộ trình giống nhau cho mọi học "
            "sinh."
        ),
        excerpt=(
            "Gia sư lớp 9 Trí Việt hỗ trợ hệ thống kiến thức, luyện kỹ năng làm "
            "bài và ôn thi vào lớp 10 theo nhu cầu."
        ),
        post_id=3232,
    ),
    "gia-su-lop-10": Copy(
        title="Gia sư lớp 10",
        body=(
            "Gia sư lớp 10 của Trí Việt giúp học sinh thích nghi với chương "
            "trình THPT, củng cố kiến thức nền và rèn phương pháp học riêng cho "
            "từng môn. Nội dung học tập trung vào phần học sinh chưa nắm chắc, "
            "sau đó mới mở rộng bài tập theo mục tiêu."
        ),
        excerpt=(
            "Gia sư lớp 10 Trí Việt hỗ trợ thích nghi với chương trình THPT, "
            "củng cố nền tảng và rèn phương pháp học từng môn."
        ),
        post_id=3234,
    ),
    # Lớp 11 không phải một trong 14 bài chính cần viết lại. Bản sao tĩnh vẫn
    # chứa trích đoạn/feed sinh tự động của bài này nên cần nội dung dẫn xuất.
    "gia-su-lop-11": Copy(
        title="Gia sư lớp 11",
        body=(
            "Gia sư lớp 11 của Trí Việt hỗ trợ học sinh củng cố kiến thức theo "
            "từng môn, phát hiện phần còn hổng và rèn phương pháp tự học. Lộ "
            "trình được điều chỉnh theo mục tiêu, tiến độ thực tế và nhu cầu "
            "chuẩn bị nền tảng cho lớp 12."
        ),
        excerpt=(
            "Gia sư lớp 11 Trí Việt hỗ trợ củng cố từng môn, khắc phục kiến "
            "thức hổng và chuẩn bị nền tảng cho lớp 12."
        ),
        post_id=3236,
    ),
    "gia-su-lop-12": Copy(
        title="Gia sư lớp 12",
        body=(
            "Gia sư lớp 12 của Trí Việt hỗ trợ học sinh hệ thống kiến thức, "
            "luyện dạng bài và sắp xếp kế hoạch ôn tập theo môn thi cùng mục "
            "tiêu sau THPT. Gia sư theo dõi lỗi sai và mức độ hoàn thành để "
            "điều chỉnh trọng tâm; kết quả phụ thuộc vào nền tảng và quá trình "
            "luyện tập của học sinh."
        ),
        excerpt=(
            "Gia sư lớp 12 Trí Việt hỗ trợ hệ thống kiến thức, luyện dạng bài "
            "và xây kế hoạch ôn tập theo mục tiêu sau THPT."
        ),
        post_id=3238,
    ),
    "gia-su-quan-ba-dinh": Copy(
        title="Gia sư quận Ba Đình",
        body=(
            "Trí Việt tiếp nhận nhu cầu tìm gia sư tại quận Ba Đình theo môn "
            "học, cấp lớp, lịch học và khu vực cụ thể. Phụ huynh có thể trao "
            "đổi trực tiếp với gia sư được giới thiệu trước khi thống nhất; nội "
            "dung và tiến độ học được điều chỉnh theo nhu cầu thực tế của học "
            "sinh."
        ),
        excerpt=(
            "Trí Việt tiếp nhận nhu cầu tìm gia sư tại quận Ba Đình theo môn, "
            "cấp lớp, lịch học và mục tiêu thực tế."
        ),
        post_id=3260,
    ),
}


CATEGORIES: dict[str, Copy] = {
    "gia-su-mon-anh-mb": Copy(
        title="Gia sư môn Anh",
        body=(
            "Chuyên mục Gia sư môn Anh của Trí Việt tổng hợp nội dung học theo "
            "trình độ và mục tiêu, từ củng cố nền tảng đến luyện kỹ năng và ôn "
            "thi. Phụ huynh, học viên có thể trao đổi môn học, lịch học và hình "
            "thức học để được tư vấn phù hợp."
        ),
        excerpt=(
            "Thông tin gia sư môn Anh theo trình độ, mục tiêu, lịch học và hình "
            "thức học phù hợp với từng học viên."
        ),
    ),
    "gia-su-mon-hoa-mb": Copy(
        title="Gia sư môn Hóa",
        body=(
            "Chuyên mục Gia sư môn Hóa của Trí Việt tổng hợp nội dung củng cố "
            "lý thuyết, bài tập và phương pháp học theo cấp lớp. Lộ trình cần "
            "dựa trên phần kiến thức còn hổng, mục tiêu và thời gian học thực "
            "tế của học sinh."
        ),
        excerpt=(
            "Thông tin gia sư môn Hóa theo cấp lớp, phần kiến thức cần củng cố "
            "và mục tiêu học tập thực tế."
        ),
    ),
    "gia-su-mon-dia-mb": Copy(
        title="Gia sư môn Địa",
        body=(
            "Chuyên mục Gia sư môn Địa của Trí Việt tổng hợp nội dung học theo "
            "cấp lớp, gồm hệ thống kiến thức, kỹ năng đọc dữ liệu và luyện cách "
            "trình bày bài. Kế hoạch học được điều chỉnh theo chương trình và "
            "mục tiêu của học sinh."
        ),
        excerpt=(
            "Thông tin gia sư môn Địa theo cấp lớp, chương trình và mục tiêu "
            "học tập của học sinh."
        ),
    ),
    "hanh-trang-lop-1-mb": Copy(
        title="Hành trang lớp 1",
        body=(
            "Chuyên mục Hành trang lớp 1 của Trí Việt chia sẻ nội dung giúp trẻ "
            "làm quen với nề nếp học tập, kỹ năng nghe hướng dẫn và kiến thức "
            "tiền tiểu học phù hợp độ tuổi. Hoạt động nên được điều chỉnh theo "
            "mức độ sẵn sàng của từng trẻ, tránh tạo áp lực học trước."
        ),
        excerpt=(
            "Nội dung giúp trẻ làm quen nề nếp và kỹ năng cần thiết trước lớp "
            "1, phù hợp với mức độ sẵn sàng của từng trẻ."
        ),
    ),
}


GENERIC_COPY = Copy(
    title="Trung Tâm Gia Sư Trí Việt",
    body=(
        "Trung Tâm Gia Sư Trí Việt cung cấp thông tin tham khảo về học tập, "
        "lựa chọn gia sư và xây dựng lộ trình theo nhu cầu thực tế của học "
        "sinh. Phụ huynh có thể trao đổi trực tiếp để làm rõ môn học, cấp lớp, "
        "lịch học và mục tiêu."
    ),
    excerpt=(
        "Thông tin tham khảo từ Trí Việt về học tập, lựa chọn gia sư và xây "
        "dựng lộ trình theo nhu cầu thực tế."
    ),
)


# The mirrored placeholder always ends at PageMaker (full copy) or at one of
# WordPress's plain/entity/Unicode truncation markers. This also matches JSON
# strings whose Vietnamese characters are encoded as \uXXXX, without
# reserializing the surrounding JSON.
PLACEHOLDER_RE = re.compile(
    r"(?:<strong>)?Lorem Ipsum(?:</strong>|<\\/strong>)?"
    r".*?(?:Aldus PageMaker\.|volutpat\.|\[(?:\.\.\.|&#8230;|…|\\u2026)\])",
    re.IGNORECASE | re.DOTALL,
)

POST_ID_TOPICS = {
    str(copy.post_id): slug
    for slug, copy in TOPICS.items()
    if copy.post_id is not None
}
CATEGORY_ID_SLUGS = {
    "463": "hanh-trang-lop-1-mb",
    "480": "gia-su-mon-hoa-mb",
    "481": "gia-su-mon-anh-mb",
    "485": "gia-su-mon-dia-mb",
}
SPECIAL_FILE_TOPICS = {
    "wp-json/oembed/1.0/embed3ea5": "cam-ket-tien-bo-sau-10-buoi",
    "wp-json/oembed/1.0/embed92cc.json": "cam-ket-tien-bo-sau-10-buoi",
}


def normalized_topic_component(component: str) -> str:
    normalized = component.casefold()
    if normalized.endswith("-mb"):
        normalized = normalized[:-3]
    return normalized


def fixed_topic_for_path(relative_path: str) -> str | None:
    special_topic = SPECIAL_FILE_TOPICS.get(relative_path.casefold())
    if special_topic:
        return special_topic

    parts = relative_path.casefold().split("/")
    for part in parts:
        normalized = normalized_topic_component(part)
        if normalized in TOPICS:
            return normalized

    if "wp-json/wp/v2/posts" in relative_path.casefold():
        post_id = Path(relative_path).stem
        return POST_ID_TOPICS.get(post_id)
    return None


def nearest_topic(
    content: str,
    match_start: int,
    match_end: int,
) -> str | None:
    window_start = max(0, match_start - 1800)
    window_end = min(len(content), match_end + 1200)
    window = content[window_start:window_end].casefold()
    relative_start = match_start - window_start
    relative_end = match_end - window_start

    best_slug: str | None = None
    best_distance = 10**9
    for slug, copy in TOPICS.items():
        identifiers = [
            copy.title.casefold(),
            f"{slug}/",
            f"{slug}\\/",
        ]
        if copy.post_id is not None:
            identifiers.extend(
                (
                    f"?p={copy.post_id}",
                    f'"id":{copy.post_id}',
                    f'"id": {copy.post_id}',
                )
            )

        for identifier in identifiers:
            position = window.find(identifier)
            while position >= 0:
                identifier_end = position + len(identifier)
                if identifier_end < relative_start:
                    distance = relative_start - identifier_end
                elif position > relative_end:
                    distance = position - relative_end
                else:
                    distance = 0
                if distance < best_distance:
                    best_distance = distance
                    best_slug = slug
                position = window.find(identifier, position + 1)

    return best_slug if best_distance <= 1000 else None


def category_for_path(relative_path: str) -> str | None:
    folded_parts = relative_path.casefold().split("/")
    for part in folded_parts:
        if part in CATEGORIES:
            return part

    if "wp-json/wp/v2/categories" in relative_path.casefold():
        category_id = Path(relative_path).stem
        return CATEGORY_ID_SLUGS.get(category_id)
    return None


def select_copy(
    relative_path: str,
    content: str,
    match_start: int,
    match_end: int,
) -> tuple[str, Copy]:
    fixed_topic = fixed_topic_for_path(relative_path)
    if fixed_topic:
        return fixed_topic, TOPICS[fixed_topic]

    contextual_topic = nearest_topic(content, match_start, match_end)
    if contextual_topic:
        return contextual_topic, TOPICS[contextual_topic]

    category_slug = category_for_path(relative_path)
    if category_slug:
        return category_slug, CATEGORIES[category_slug]

    return "generic", GENERIC_COPY


def replace_placeholders(
    relative_path: str,
    content: str,
) -> tuple[str, Counter[str]]:
    counts: Counter[str] = Counter()

    def replacement(match: re.Match[str]) -> str:
        key, copy = select_copy(
            relative_path,
            content,
            match.start(),
            match.end(),
        )
        is_full_copy = not re.search(
            r"\[(?:\.\.\.|&#8230;|…|\\u2026)\]",
            match.group(0),
            re.IGNORECASE,
        )
        counts["full" if is_full_copy else "excerpt"] += 1
        counts[f"copy:{key}"] += 1
        return copy.body if is_full_copy else copy.excerpt

    cleaned = PLACEHOLDER_RE.sub(replacement, content)
    if "lorem ipsum" in cleaned.casefold():
        raise ValueError(
            f"Unrecognized placeholder form remains in {relative_path}"
        )
    return cleaned, counts


def validate_document(path: Path, content: str) -> None:
    stripped = content.lstrip("\ufeff\r\n\t ")
    if path.suffix.casefold() == ".json" or stripped.startswith(("{", "[")):
        json.loads(content)
        return
    if stripped.startswith(("<?xml", "<oembed")):
        ET.fromstring(content)
        return
    if path.suffix.casefold() == ".html":
        parser = HTMLParser(convert_charrefs=False)
        parser.feed(content)
        parser.close()


def main() -> None:
    changed_files = 0
    totals: Counter[str] = Counter()

    for path in sorted(SITE_ROOT.rglob("*")):
        if not path.is_file():
            continue
        raw = path.read_bytes()
        relative_path = path.relative_to(SITE_ROOT).as_posix()
        prior_fallback = (
            relative_path.casefold() in SPECIAL_FILE_TOPICS
            and GENERIC_COPY.excerpt.encode("utf-8") in raw
        )
        if b"lorem ipsum" not in raw.lower() and not prior_fallback:
            continue

        original = raw.decode("utf-8")
        cleaned, counts = replace_placeholders(relative_path, original)
        if prior_fallback:
            topic = TOPICS[SPECIAL_FILE_TOPICS[relative_path.casefold()]]
            cleaned = cleaned.replace(GENERIC_COPY.excerpt, topic.excerpt)
            counts["derived_upgrade"] += 1
        if cleaned == original:
            continue

        validate_document(path, cleaned)
        path.write_bytes(cleaned.encode("utf-8"))
        changed_files += 1
        totals.update(counts)

    print(f"Changed files: {changed_files}")
    print(f"Replaced full placeholder blocks: {totals['full']}")
    print(f"Replaced placeholder excerpts: {totals['excerpt']}")
    print(
        "Fallback blocks: "
        f"{totals['copy:generic']} "
        "(only non-topic archive/template metadata)"
    )
    print(f"Upgraded derivative fallbacks: {totals['derived_upgrade']}")


if __name__ == "__main__":
    main()
