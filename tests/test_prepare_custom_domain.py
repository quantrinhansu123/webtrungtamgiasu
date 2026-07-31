from scripts.prepare_custom_domain import CUSTOM_ORIGIN, normalize_content


def test_normalize_content_uses_custom_domain_and_clean_paths():
    original = "\n".join(
        (
            "https://giasutriviet.vercel.app/giasubinhminh.com/lop-moi/",
            r"https:\/\/giasutriviet.vercel.app\/giasubinhminh.com\/admin",
            "https%3A%2F%2Fgiasutriviet.vercel.app%2Fgiasubinhminh.com%2F",
            "/giasubinhminh.com/wp-content/uploads/logo.png",
        )
    )

    normalized = normalize_content(original)

    assert f"{CUSTOM_ORIGIN}/lop-moi/" in normalized
    assert CUSTOM_ORIGIN.replace("/", r"\/") + r"\/admin" in normalized
    assert (
        CUSTOM_ORIGIN.replace(":", "%3A").replace("/", "%2F") + "%2F"
        in normalized
    )
    assert "/wp-content/uploads/logo.png" in normalized
    assert "giasubinhminh.com" not in normalized
