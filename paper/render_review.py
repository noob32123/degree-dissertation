"""Render every manuscript page and build contact sheets for visual QA."""

from __future__ import annotations

import argparse
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image, ImageDraw


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--output", type=Path, default=Path("tmp/pdfs/rendered"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    document = pdfium.PdfDocument(args.pdf)
    pages: list[Path] = []
    for index, page in enumerate(document):
        image = page.render(scale=1.5).to_pil().convert("RGB")
        path = args.output / f"page-{index + 1:02d}.png"
        image.save(path)
        pages.append(path)
    for start in range(0, len(pages), 4):
        images = [Image.open(path).convert("RGB") for path in pages[start:start + 4]]
        thumb_width = 500
        resized = [
            image.resize((thumb_width, round(image.height * thumb_width / image.width)))
            for image in images
        ]
        label_height = 34
        width = thumb_width * 2
        height = max(image.height for image in resized) * 2 + label_height * 2
        sheet = Image.new("RGB", (width, height), "#d7d7d7")
        draw = ImageDraw.Draw(sheet)
        for offset, image in enumerate(resized):
            row, column = divmod(offset, 2)
            x = column * thumb_width
            y = row * (image.height + label_height) + label_height
            sheet.paste(image, (x, y))
            draw.text((x + 8, y - 26), f"Page {start + offset + 1}", fill="black")
        sheet.save(args.output / f"contact-{start // 4 + 1:02d}.png")
    print(f"rendered {len(pages)} pages to {args.output}")


if __name__ == "__main__":
    main()
