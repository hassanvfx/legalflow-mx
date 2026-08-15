"""Validate Lulu full-bleed geometry, title-art resolution, and PDF safety."""
from __future__ import annotations

import sys
from pathlib import Path

from pypdf import PdfReader

BLEED = (6.25 * 72, 9.25 * 72)
TITLE_IMAGE_MIN = (1875, 2775)  # 300 ppi at 6.25 x 9.25 inches


def _fonts_embedded(page) -> bool:  # type: ignore[no-untyped-def]
    fonts = page.get("/Resources", {}).get("/Font", {})
    if not fonts:
        return False
    for font in fonts.values():
        obj = font.get_object()
        descriptor = obj.get("/FontDescriptor")
        if descriptor:
            descriptor = descriptor.get_object()
            if any(key in descriptor for key in ("/FontFile", "/FontFile2", "/FontFile3")):
                return True
    return False


def _image_sizes(page) -> list[tuple[int, int]]:  # type: ignore[no-untyped-def]
    xobjects = page.get("/Resources", {}).get("/XObject", {})
    sizes: list[tuple[int, int]] = []
    for item in xobjects.values():
        obj = item.get_object()
        if obj.get("/Subtype") == "/Image":
            sizes.append((int(obj["/Width"]), int(obj["/Height"])))
    return sizes


def main(path: str) -> int:
    reader = PdfReader(path)
    if reader.is_encrypted or not reader.pages:
        print("FAIL: encrypted or empty PDF")
        return 1
    errors: list[str] = []
    for number, page in enumerate(reader.pages, 1):
        width, height = float(page.mediabox.width), float(page.mediabox.height)
        if abs(width - BLEED[0]) > 1 or abs(height - BLEED[1]) > 1:
            errors.append(f"page {number}: {width / 72:.2f} x {height / 72:.2f} in, expected 6.25 x 9.25 bleed")
        if number > 1 and not _fonts_embedded(page):
            errors.append(f"page {number}: no embedded font found")
    cover_images = _image_sizes(reader.pages[0])
    if not cover_images or max(cover_images) < TITLE_IMAGE_MIN:
        errors.append(f"title page: image below 300 ppi effective requirement {TITLE_IMAGE_MIN}")
    if errors:
        print("FAIL:", *errors, sep="\n")
        return 1
    print(f"PASS: {len(reader.pages)} portrait pages at 6.25 x 9.25 in full bleed; embedded fonts and 300 ppi title art verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
