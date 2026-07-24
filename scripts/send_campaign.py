"""Send a drafted resell/upsell email campaign via Brevo's transactional API.

Usage: python scripts/send_campaign.py company/campaigns/<file>.json

The campaign file is a JSON list of already-personalized messages:
  [{"email": "...", "subject": "...", "html_body": "..."}, ...]
(the Growth department writes these -- this script only sends what's
already drafted, it doesn't compose anything itself).

Requires BREVO_API_KEY, BREVO_SENDER_EMAIL, BREVO_SENDER_NAME in the
environment. Without a real key, this fails cleanly and the draft stays on
disk unsent -- it never fakes a send.

Every send includes a List-Unsubscribe header pointing at a mailto address
(BREVO_SENDER_EMAIL) -- most mail clients (Gmail, Outlook, etc.) render this
as a one-click "Unsubscribe" button even without a custom backend. Since
this project has no server to process those requests automatically, the
founder (or a future cycle) must manually add any resulting unsubscribe
request to company/unsubscribed.md -- fetch_customers.py and this script
both already exclude every email listed there.

Never sends to the same email for the same campaign file twice: results
are recorded next to the campaign file as <file>.sent.json and checked
before sending.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UNSUBSCRIBED_PATH = ROOT / "company" / "unsubscribed.md"
BREVO_API_BASE = "https://api.brevo.com/v3"


def load_unsubscribed() -> set:
    if not UNSUBSCRIBED_PATH.exists():
        return set()
    emails = set()
    for line in UNSUBSCRIBED_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip().lstrip("-").strip()
        if line and "@" in line:
            emails.add(line.lower())
    return emails


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/send_campaign.py <campaign_file.json>")
        sys.exit(1)

    campaign_path = Path(sys.argv[1])
    if not campaign_path.exists():
        print(f"No campaign file found at {campaign_path}")
        sys.exit(1)

    api_key = os.environ.get("BREVO_API_KEY")
    sender_email = os.environ.get("BREVO_SENDER_EMAIL")
    sender_name = os.environ.get("BREVO_SENDER_NAME", "Autonomous Press")
    if not api_key or not sender_email:
        print("BREVO_API_KEY / BREVO_SENDER_EMAIL not set. Campaign stays drafted, not sent -- "
              "set these in .env once the Brevo account is ready.")
        sys.exit(1)

    try:
        import requests
    except ImportError:
        print("The 'requests' package isn't installed. Run: pip install -r requirements.txt")
        sys.exit(1)

    messages = json.loads(campaign_path.read_text(encoding="utf-8"))
    unsubscribed = load_unsubscribed()

    sent_log_path = campaign_path.with_suffix(".sent.json")
    already_sent = set()
    if sent_log_path.exists():
        already_sent = {r["email"] for r in json.loads(sent_log_path.read_text(encoding="utf-8"))}

    results = []
    if sent_log_path.exists():
        results = json.loads(sent_log_path.read_text(encoding="utf-8"))

    sent_count = 0
    skipped_count = 0
    for msg in messages:
        email = msg["email"].strip().lower()
        if email in unsubscribed or email in already_sent:
            skipped_count += 1
            continue

        response = requests.post(
            f"{BREVO_API_BASE}/smtp/email",
            json={
                "sender": {"name": sender_name, "email": sender_email},
                "to": [{"email": email}],
                "subject": msg["subject"],
                "htmlContent": msg["html_body"],
                "headers": {"List-Unsubscribe": f"<mailto:{sender_email}?subject=unsubscribe>"},
            },
            headers={"api-key": api_key, "Content-Type": "application/json"},
            timeout=30,
        )

        if response.ok:
            sent_count += 1
            results.append({"email": email, "status": "sent", "sent_at": response.json().get("messageId", "")})
        else:
            results.append({"email": email, "status": "failed", "error": response.text[:300]})
            print(f"Failed to send to {email}: {response.status_code} {response.text[:200]}")

    sent_log_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Sent {sent_count}, skipped {skipped_count} (already sent or unsubscribed), "
          f"out of {len(messages)} in {campaign_path.name}.")


if __name__ == "__main__":
    main()
