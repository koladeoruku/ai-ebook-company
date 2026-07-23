"""Generate a simple, free, templated ebook cover (no paid image-gen API).

Usage: python scripts/make_cover.py <slug>

Reads the title (first '# ' heading) and author (line starting with
"Published by") from company/books/<slug>/manuscript.md and renders a
plain typographic cover to company/books/<slug>/cover.png.
"""
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
COMPANY_NAME = "Autonomous Press"
WIDTH, HEIGHT = 1600, 2400


def find_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "arialbd.ttf" if bold else "arial.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def extract_title_author(manuscript_path: Path) -> tuple[str, str]:
    title = "Untitled"
    author = COMPANY_NAME
    for line in manuscript_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("# ") and title == "Untitled":
            title = stripped[2:].strip()
        if stripped.lower().startswith("published by"):
            author = stripped.split("by", 1)[-1].strip()
        if title != "Untitled" and author != COMPANY_NAME:
            break
    return title, author


def draw_centered_wrapped(draw, text, y, font, max_width, fill, line_spacing=1.3):
    avg_char_w = font.getlength("x") or 10
    wrap_width = max(10, int(max_width / avg_char_w))
    lines = textwrap.wrap(text, width=wrap_width) or [text]
    for line in lines:
        w = draw.textlength(line, font=font)
        draw.text(((WIDTH - w) / 2, y), line, font=font, fill=fill)
        y += int(font.size * line_spacing)
    return y


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/make_cover.py <slug>")
        sys.exit(1)

    slug = sys.argv[1]
    book_dir = ROOT / "company" / "books" / slug
    manuscript_path = book_dir / "manuscript.md"
    if not manuscript_path.exists():
        print(f"No manuscript found at {manuscript_path}")
        sys.exit(1)

    title, author = extract_title_author(manuscript_path)

    img = Image.new("RGB", (WIDTH, HEIGHT), color=(24, 28, 38))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (WIDTH, 24)], fill=(220, 180, 90))
    draw.rectangle([(0, HEIGHT - 24), (WIDTH, HEIGHT)], fill=(220, 180, 90))

    title_font = find_font(120, bold=True)
    author_font = find_font(56)
    imprint_font = find_font(44)

    y = HEIGHT * 0.36
    y = draw_centered_wrapped(draw, title, y, title_font, WIDTH * 0.8, (245, 245, 245))

    y += 60
    author_text = f"by {author}"
    w = draw.textlength(author_text, font=author_font)
    draw.text(((WIDTH - w) / 2, y), author_text, font=author_font, fill=(200, 200, 210))

    imprint_text = COMPANY_NAME
    w = draw.textlength(imprint_text, font=imprint_font)
    draw.text(((WIDTH - w) / 2, HEIGHT - 140), imprint_text, font=imprint_font, fill=(220, 180, 90))

    out_path = book_dir / "cover.png"
    img.save(out_path)
    print(f"Wrote cover: {out_path}")


if __name__ == "__main__":
    main()
