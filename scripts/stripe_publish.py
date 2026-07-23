"""Create the Stripe Product, Price, and Payment Link for a finished book.

Usage: python scripts/stripe_publish.py <slug>

Reads company/books/<slug>/metadata.json for title/blurb/price, creates the
Stripe objects via the API (requires STRIPE_SECRET_KEY in the environment),
and writes stripe_product_id / stripe_price_id / stripe_payment_link back
into metadata.json. Does NOT mark status as "published" itself -- the
publisher subagent does that only after this AND the epub/pdf both exist.

The payment link's post-purchase redirect points at the book's unlisted
thank-you page (docs/book/<slug>/thank-you.html), which links the
actual epub/pdf downloads. STOREFRONT_BASE_URL must be set to the live
GitHub Pages URL for that redirect to work once deployed.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/stripe_publish.py <slug>")
        sys.exit(1)

    slug = sys.argv[1]
    book_dir = ROOT / "company" / "books" / slug
    meta_path = book_dir / "metadata.json"
    if not meta_path.exists():
        print(f"No metadata.json found at {meta_path}")
        sys.exit(1)

    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    api_key = os.environ.get("STRIPE_SECRET_KEY")
    if not api_key:
        print("STRIPE_SECRET_KEY is not set. Cannot create a real payment link — "
              "set it in your environment/.env before publishing.")
        sys.exit(1)

    try:
        import stripe
    except ImportError:
        print("The 'stripe' package isn't installed. Run: pip install -r requirements.txt")
        sys.exit(1)

    stripe.api_key = api_key

    storefront_base = os.environ.get("STOREFRONT_BASE_URL", "").rstrip("/")
    if not storefront_base:
        print("Warning: STOREFRONT_BASE_URL is not set — the post-purchase redirect "
              "will not point anywhere until you set it and re-run this step.")

    price_usd = float(meta["price"])
    product = stripe.Product.create(
        name=meta["title"],
        description=meta.get("blurb", "")[:500] or None,
    )
    price = stripe.Price.create(
        product=product.id,
        unit_amount=int(round(price_usd * 100)),
        currency="usd",
    )

    payment_link_kwargs = {
        "line_items": [{"price": price.id, "quantity": 1}],
    }
    if storefront_base:
        payment_link_kwargs["after_completion"] = {
            "type": "redirect",
            "redirect": {"url": f"{storefront_base}/book/{slug}/thank-you.html"},
        }
    payment_link = stripe.PaymentLink.create(**payment_link_kwargs)

    meta["stripe_product_id"] = product.id
    meta["stripe_price_id"] = price.id
    meta["stripe_payment_link"] = payment_link.url
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"Created Stripe product {product.id}, price {price.id}")
    print(f"Payment link: {payment_link.url}")


if __name__ == "__main__":
    main()
