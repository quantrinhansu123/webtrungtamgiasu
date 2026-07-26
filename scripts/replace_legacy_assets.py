from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps

from cleanup_legacy_branding import ROOT, SITE_ROOT, replacement_asset_path


UPLOAD_ROOT = SITE_ROOT / "wp-content" / "uploads"


def source_path(replacement_url: str) -> Path:
    path = ROOT / replacement_url.lstrip("/")
    if path.suffix.lower() == ".svg":
        raster_path = path.with_suffix(".png")
        if raster_path.is_file():
            return raster_path
    return path


def replacement_bytes(source: Path, target: Path) -> bytes:
    with Image.open(target) as existing:
        target_size = existing.size
        target_format = existing.format

    if target_format not in {"JPEG", "PNG"}:
        raise ValueError(f"Unsupported target format {target_format}: {target}")

    with Image.open(source) as raw_source:
        normalized = ImageOps.exif_transpose(raw_source).convert("RGBA")
        white = Image.new("RGBA", normalized.size, "white")
        white.alpha_composite(normalized)
        fitted = ImageOps.contain(
            white.convert("RGB"),
            target_size,
            Image.Resampling.LANCZOS,
        )

    canvas = Image.new("RGB", target_size, "white")
    canvas.paste(
        fitted,
        (
            (target_size[0] - fitted.width) // 2,
            (target_size[1] - fitted.height) // 2,
        ),
    )

    output = BytesIO()
    if target_format == "JPEG":
        canvas.save(
            output,
            format="JPEG",
            quality=92,
            optimize=True,
            progressive=True,
        )
    else:
        canvas.save(output, format="PNG", optimize=True)
    return output.getvalue()


def main() -> None:
    matched = 0
    changed = 0

    for target in sorted(path for path in UPLOAD_ROOT.rglob("*") if path.is_file()):
        relative_path = target.relative_to(SITE_ROOT).as_posix().casefold()
        replacement_url = replacement_asset_path(relative_path)
        if replacement_url is None:
            continue

        matched += 1
        source = source_path(replacement_url)
        if not source.is_file():
            raise FileNotFoundError(
                f"Missing replacement source for {target}: {source}"
            )
        if source.resolve() == target.resolve():
            continue

        rendered = replacement_bytes(source, target)
        if rendered == target.read_bytes():
            continue
        target.write_bytes(rendered)
        changed += 1

    print(f"Matched legacy image files: {matched}")
    print(f"Rewritten legacy image files: {changed}")


if __name__ == "__main__":
    main()
