"""Create the Paystack Payment Page for a finished book.

Usage: python scripts/paystack_publish.py <slug>

Reads company/books/<slug>/metadata.json for title/blurb/price. price is
ALWAYS a USD decimal amount (e.g. 9.99) -- USD is this company's one
canonical pricing currency, set by the CMO regardless of which currency
Paystack actually charges in.

Stripe doesn't officially support Nigeria as a business's home country, so
this company uses Paystack instead -- it's Stripe-owned, built for Nigerian
businesses, and its Payment Pages are the equivalent of Stripe Payment Links.
Paystack can accept and settle in USD for Nigerian businesses once "Accept
international payments" is enabled on the account (Preferences tab, after
business KYC activation).

Until that approval lands, set PAYSTACK_CURRENCY=NGN in .env as an interim
fallback. In that mode this script converts the USD price to NGN using a
live, free, no-key exchange rate (open.er-api.com) at publish time -- never
a hardcoded rate -- and records the rate used in metadata.json so the
ledger stays honest about what was actually charged. Once USD is approved,
switch PAYSTACK_CURRENCY back to USD and no conversion happens at all.

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
FX_API_URL = "https://open.er-api.com/v6/latest/USD"


def get_usd_to_ngn_rate(requests) -> float:
    resp = requests.get(FX_API_URL, timeout=15)
    resp.raise_for_status()
    body = resp.json()
    if body.get("result") != "success":
        raise RuntimeError(f"FX API did not return success: {body}")
    return float(body["rates"]["NGN"])


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

    currency = os.environ.get("PAYSTACK_CURRENCY", "USD").upper()
    price_usd = float(meta["price"])

    if currency == "USD":
        charge_amount = price_usd
        fx_rate = None
    elif currency == "NGN":
        try:
            fx_rate = get_usd_to_ngn_rate(requests)
        except Exception as exc:
            print(f"Could not fetch a live USD->NGN rate ({exc}). Not publishing with a "
                  "guessed rate — fix connectivity/FX API access and retry.")
            sys.exit(1)
        charge_amount = price_usd * fx_rate
    else:
        print(f"Unsupported PAYSTACK_CURRENCY={currency!r}. Use USD or NGN.")
        sys.exit(1)

    amount_subunit = int(round(charge_amount * 100))  # cents (USD) / kobo (NGN)

    payload = {
        "name": meta["title"],
        "description": (meta.get("blurb", "") or "")[:500],
        "amount": amount_subunit,
        "currency": currency,
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
        if currency == "USD":
            print("If this mentions currency/channel support, USD likely isn't enabled yet "
                  "on this account -- request 'Accept international payments' in Paystack's "
                  "Preferences tab, or set PAYSTACK_CURRENCY=NGN in .env to publish in the "
                  "meantime.")
        sys.exit(1)

    data = body["data"]
    page_slug = data["slug"]
    payment_link = f"https://paystack.com/pay/{page_slug}"

    meta["paystack_page_id"] = data.get("id")
    meta["paystack_page_slug"] = page_slug
    meta["paystack_payment_link"] = payment_link
    meta["charge_currency"] = currency
    meta["charge_amount"] = round(charge_amount, 2)
    if fx_rate is not None:
        meta["fx_rate_usd_ngn"] = fx_rate
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"Created Paystack payment page {data.get('id')} (slug: {page_slug})")
    print(f"Payment link: {payment_link}")
    if fx_rate is not None:
        print(f"Charged {currency} {charge_amount:,.2f} (converted from USD {price_usd:.2f} "
              f"at rate {fx_rate:,.2f})")


if __name__ == "__main__":
    main()
