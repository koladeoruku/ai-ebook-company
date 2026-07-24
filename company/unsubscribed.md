# Unsubscribed

Emails that must never receive a campaign email again, one per line. `scripts/fetch_customers.py` and `scripts/send_campaign.py` both read this file and exclude every address listed here before doing anything else.

There's no automated backend to process unsubscribe requests (this is a static site with no server) — every campaign email includes a `List-Unsubscribe` header that most mail clients render as a one-click button, which arrives as a plain email to the founder's address. Whoever processes that inbox (founder, or a future automated step) needs to add the email here by hand.

<!-- one email per line, e.g.:
- someone@example.com
-->
