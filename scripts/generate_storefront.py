"""Rebuild the static storefront from company/books/*/metadata.json.

Usage: python scripts/generate_storefront.py

Regenerates storefront/index.html (catalog) and storefront/book/<slug>/index.html
(per-book landing page with the Stripe payment link), and copies each book's
epub/pdf into storefront/downloads/. Only books with status == "published"
(i.e. they have a real stripe_payment_link) are listed for sale.
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS_DIR = ROOT / "company" / "books"
STOREFRONT_DIR = ROOT / "storefront"
COMPANY_NAME = "Autonomous Press"

BASE_CSS = """
body { font-family: -apple-system, Segoe UI, Roboto, sans-serif; margin: 0; padding: 0;
       background: #0f1117; color: #e8e8ec; }
.header { padding: 2rem 1.5rem; text-align: center; border-bottom: 1px solid #2a2d3a; }
.header h1 { margin: 0; font-size: 1.8rem; }
.header p { color: #9a9aa8; margin: .5rem 0 0; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 1.5rem; padding: 2rem; max-width: 1100px; margin: 0 auto; }
.card { background: #171a23; border: 1px solid #2a2d3a; border-radius: 10px; overflow: hidden;
        display: flex; flex-direction: column; }
.card img { width: 100%; display: block; }
.card .body { padding: 1rem; flex: 1; display: flex; flex-direction: column; }
.card h3 { margin: 0 0 .5rem; font-size: 1.05rem; }
.card p { color: #b0b0bc; font-size: .9rem; flex: 1; }
.price { font-weight: bold; color: #dcb45a; margin: .5rem 0; }
.buy { display: inline-block; text-align: center; background: #dcb45a; color: #14161d;
       padding: .6rem 1rem; border-radius: 6px; text-decoration: none; font-weight: 600; }
.buy:hover { opacity: .9; }
.book-page { max-width: 800px; margin: 0 auto; padding: 2rem 1.5rem; }
.book-page img { max-width: 320px; float: left; margin: 0 1.5rem 1rem 0; border-radius: 8px; }
.back { color: #9a9aa8; text-decoration: none; }
footer { text-align: center; color: #6a6a78; padding: 2rem; font-size: .85rem; }
"""


def load_books():
    books = []
    if not BOOKS_DIR.exists():
        return books
    for book_dir in sorted(BOOKS_DIR.iterdir()):
        meta_path = book_dir / "metadata.json"
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["_dir"] = book_dir
        books.append(meta)
    return books


def render_index(published_books):
    cards = ""
    for b in published_books:
        slug = b["slug"]
        cards += f"""
        <div class="card">
          <img src="book/{slug}/cover.png" alt="{b['title']} cover">
          <div class="body">
            <h3>{b['title']}</h3>
            <p>{b.get('blurb', '')}</p>
            <div class="price">${b['price']:.2f}</div>
            <a class="buy" href="book/{slug}/">View book</a>
          </div>
        </div>"""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{COMPANY_NAME}</title>
<style>{BASE_CSS}</style>
</head><body>
<div class="header">
  <h1>{COMPANY_NAME}</h1>
  <p>Short, practical ebooks — written, edited, and published by an autonomous AI company.</p>
</div>
<div class="grid">{cards if cards else '<p style="grid-column:1/-1;text-align:center;color:#777">No books published yet — check back soon.</p>'}</div>
<footer>{COMPANY_NAME} &middot; every book on this site was researched, written, and priced without human editing of the prose.</footer>
</body></html>"""


def render_book_page(b):
    slug = b["slug"]
    link = b.get("stripe_payment_link")
    buy_html = (
        f'<a class="buy" href="{link}">Buy for ${b["price"]:.2f}</a>'
        if link else '<p><em>Not yet available for purchase.</em></p>'
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{b['title']} — {COMPANY_NAME}</title>
<style>{BASE_CSS}</style>
</head><body>
<div class="book-page">
  <p><a class="back" href="../../">&larr; back to catalog</a></p>
  <img src="cover.png" alt="{b['title']} cover">
  <h1>{b['title']}</h1>
  <p>{b.get('blurb', '')}</p>
  <p class="price">${b['price']:.2f}</p>
  {buy_html}
  <div style="clear:both"></div>
</div>
</body></html>"""


def render_thank_you_page(b):
    slug = b["slug"]
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Thanks for buying {b['title']}</title>
<style>{BASE_CSS}</style>
</head><body>
<div class="book-page">
  <h1>Thank you!</h1>
  <p>Your copy of <strong>{b['title']}</strong> is ready. This link is unique to your
  purchase confirmation — save the files somewhere safe, they aren't linked from the
  public catalog.</p>
  <p>
    <a class="buy" href="../../downloads/{slug}.epub">Download EPUB</a>
    &nbsp;
    <a class="buy" href="../../downloads/{slug}.pdf">Download PDF</a>
  </p>
</div>
</body></html>"""


def main() -> None:
    books = load_books()
    published = [b for b in books if b.get("status") == "published" and b.get("stripe_payment_link")]

    (STOREFRONT_DIR / "downloads").mkdir(parents=True, exist_ok=True)
    (STOREFRONT_DIR / "book").mkdir(parents=True, exist_ok=True)

    for b in books:
        slug = b["slug"]
        src_dir = b["_dir"]
        page_dir = STOREFRONT_DIR / "book" / slug
        page_dir.mkdir(parents=True, exist_ok=True)

        cover_src = src_dir / "cover.png"
        if cover_src.exists():
            shutil.copyfile(cover_src, page_dir / "cover.png")

        (page_dir / "index.html").write_text(render_book_page(b), encoding="utf-8")
        (page_dir / "thank-you.html").write_text(render_thank_you_page(b), encoding="utf-8")

        for ext in ("epub", "pdf"):
            f = src_dir / f"{slug}.{ext}"
            if f.exists():
                shutil.copyfile(f, STOREFRONT_DIR / "downloads" / f"{slug}.{ext}")

    (STOREFRONT_DIR / "index.html").write_text(render_index(published), encoding="utf-8")
    print(f"Rebuilt storefront: {len(published)} published / {len(books)} total books.")


if __name__ == "__main__":
    main()
