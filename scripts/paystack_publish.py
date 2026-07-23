"""Create the Paystack Payment Page for a finished book.

Usage: python scripts/paystack_publish.py <slug>

Reads company/books/<slug>/metadata.json for title/blurb/price (price is in
whole Naira, e.g. 4999.00 == NGN 4,999), creates a Paystack Payment Page via
the API (requires PAYSTACK_SECRET_KEY in the environment), and writes the
resulting paystack_page_slug / paystack_payment_link back into metadata.json.
Does NOT mark status as "published" itself -- the publisher subagent does
that only after this AND the epub/pdf both exist.

Stripe doesn't support Nigeria for standard merchant accounts, so this
company uses Paystack instead -- it's Stripe-owned, built for Nigerian
businesses, and its Payment Pages are the equivalent of Stripe Payment Links.

The payment page's redirect_url points at the book's unlisted thank-you
page (docs/book/<slug>/thank-you.html), which links the actual epub/pdf
downloads. STOREFRONT_BASE_URL must be set to the live GitHub Pages URL
for that redirect to work once deployed.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAYSTACK_API_BASE = "https://api.paystack.co"


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/paystack_publish.py <slug>")
        sys.exit(1)

    slug = sys.argv[1]
    book_dir = ROOT / "company" / "books" / slug
    meta_path = book_dir / "metadata.json"
    if not meta_path.exists():
        print(f"No metadata.json found at {meta_path}")
        sys.exit(1)

    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    api_key = os.environ.get("PAYSTACK_SECRET_KEY")
    if not api_key:
        print("PAYSTACK_SECRET_KEY is not set. Cannot create a real payment page — "
              "set it in your environment/.env before publishing.")
        sys.exit(1)

    try:
        import requests
    except ImportError:
        print("The 'requests' package isn't installed. Run: pip install -r requirements.txt")
        sys.exit(1)

    storefront_base = os.environ.get("STOREFRONT_BASE_URL", "").rstrip("/")
    if not storefront_base:
        print("Warning: STOREFRONT_BASE_URL is not set — the post-purchase redirect "
              "will not point anywhere until you set it and re-run this step.")

    price_ngn = float(meta["price"])
    amount_kobo = int(round(price_ngn * 100))

    payload = {
        "name": meta["title"],
        "description": (meta.get("blurb", "") or "")[:500],
        "amount": amount_kobo,
        "currency": "NGN",
    }
    if storefront_base:
        payload["redirect_url"] = f"{storefront_base}/book/{slug}/thank-you.html"

    response = requests.post(
        f"{PAYSTACK_API_BASE}/page",
        json=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        timeout=30,
    )

    body = response.json()
    if not response.ok or not body.get("status"):
        print(f"Paystack API error ({response.status_code}): {body.get('message', body)}")
        sys.exit(1)

    data = body["data"]
    page_slug = data["slug"]
    payment_link = f"https://paystack.com/pay/{page_slug}"

    meta["paystack_page_id"] = data.get("id")
    meta["paystack_page_slug"] = page_slug
    meta["paystack_payment_link"] = payment_link
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"Created Paystack payment page {data.get('id')} (slug: {page_slug})")
    print(f"Payment link: {payment_link}")


if __name__ == "__main__":
    main()
