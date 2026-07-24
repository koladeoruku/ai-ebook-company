"""Pull real buyers from Paystack's own transaction history.

Usage: python scripts/fetch_customers.py

Fetches every successful transaction from the Paystack account (paginated,
requires PAYSTACK_SECRET_KEY), matches each one to a published book by
comparing (amount, currency) against that book's recorded charge_amount/
charge_currency in metadata.json, and rebuilds company/customers.json from
scratch (this is a rebuild, not an incremental merge -- sales volume for a
one-person company is low enough that re-deriving the whole list each time
is simpler and avoids stale-merge bugs).

Known limitation: Paystack's plain transaction-list endpoint doesn't expose
"which payment page this came from" as a documented, reliable field, so
attribution is done by matching the exact charged amount + currency. If two
books ever end up priced identically in the same currency at the same time,
a purchase could be misattributed between them. Good enough for informing
resell suggestions; not something to build fragile precision on top of.

This only reads Paystack's own record of real transactions on this
account -- no email is ever scraped, bought, or collected from anywhere
else. Emails in company/unsubscribed.md are always excluded from the
output so the Growth department never has a reason to email them.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS_DIR = ROOT / "company" / "books"
CUSTOMERS_PATH = ROOT / "company" / "customers.json"
UNSUBSCRIBED_PATH = ROOT / "company" / "unsubscribed.md"
PAYSTACK_API_BASE = "https://api.paystack.co"


def load_books():
    books = []
    if not BOOKS_DIR.exists():
        return books
    for book_dir in sorted(BOOKS_DIR.iterdir()):
        meta_path = book_dir / "metadata.json"
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        books.append(meta)
    return books


def load_unsubscribed() -> set:
    if not UNSUBSCRIBED_PATH.exists():
        return set()
    emails = set()
    for line in UNSUBSCRIBED_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip().lstrip("-").strip()
        if line and "@" in line:
            emails.add(line.lower())
    return emails


def fetch_all_successful_transactions(requests, api_key):
    transactions = []
    page = 1
    while True:
        response = requests.get(
            f"{PAYSTACK_API_BASE}/transaction",
            params={"status": "success", "perPage": 100, "page": page},
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30,
        )
        body = response.json()
        if not response.ok or not body.get("status"):
            raise RuntimeError(f"Paystack API error ({response.status_code}): {body.get('message', body)}")
        batch = body.get("data", [])
        transactions.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return transactions


def match_book(amount_subunit: int, currency: str, books: list):
    for b in books:
        book_currency = b.get("charge_currency", "USD")
        book_amount = b.get("charge_amount", b.get("price"))
        if book_amount is None:
            continue
        if book_currency == currency and round(book_amount * 100) == amount_subunit:
            return b
    return None


def main() -> None:
    api_key = os.environ.get("PAYSTACK_SECRET_KEY")
    if not api_key:
        print("PAYSTACK_SECRET_KEY is not set. Cannot fetch real transactions.")
        sys.exit(1)

    try:
        import requests
    except ImportError:
        print("The 'requests' package isn't installed. Run: pip install -r requirements.txt")
        sys.exit(1)

    books = load_books()
    unsubscribed = load_unsubscribed()

    try:
        transactions = fetch_all_successful_transactions(requests, api_key)
    except Exception as exc:
        print(f"Could not fetch transactions: {exc}")
        sys.exit(1)

    customers = {}
    unmatched = 0
    for txn in transactions:
        customer = txn.get("customer") or {}
        email = (customer.get("email") or "").strip().lower()
        if not email or email in unsubscribed:
            continue

        book = match_book(txn.get("amount", 0), txn.get("currency", ""), books)
        record = customers.setdefault(email, {"email": email, "purchases": []})
        record["purchases"].append({
            "slug": book["slug"] if book else None,
            "title": book["title"] if book else None,
            "amount": txn.get("amount", 0) / 100,
            "currency": txn.get("currency"),
            "reference": txn.get("reference"),
            "paid_at": txn.get("paid_at") or txn.get("transaction_date"),
        })
        if not book:
            unmatched += 1

    CUSTOMERS_PATH.write_text(
        json.dumps(sorted(customers.values(), key=lambda c: c["email"]), indent=2),
        encoding="utf-8",
    )

    print(f"Fetched {len(transactions)} successful transactions -> {len(customers)} unique customers.")
    if unmatched:
        print(f"Warning: {unmatched} purchase(s) couldn't be matched to a known book by amount/currency.")
    print(f"Wrote {CUSTOMERS_PATH}")


if __name__ == "__main__":
    main()
