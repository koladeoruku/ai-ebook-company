# Autonomous Press — an AI ebook company that runs itself

This repo *is* the company. A weekly cycle improves its own writing/marketing
craft, researches a trending topic, writes and edits a full ebook, prices and
markets it, creates a real Paystack payment page, publishes it to a free static
storefront, then grows visibility via SEO and resells the catalog to real past
buyers by email — and writes you a plain-English report throughout.
See `.claude/commands/run-cycle.md` for the orchestration logic and
`.claude/agents/*.md` for each department's role.

Two departments — **R&D** (craft research) and **Growth** (SEO + resell email) —
have standing autonomy: they research and implement changes every cycle without
asking the founder first. That's a deliberate choice the founder made, not an
oversight; see `company/org_chart.md`.

Nothing here is a demo — when fully wired up, this creates real, sellable products
and real Paystack payment links. Do the one-time setup below carefully, and run the
first cycle manually before trusting the automated weekly schedule.

**⚠️ This is running on LIVE Paystack keys as of 2026-07-23**, switched on at the
founder's request before a full test-mode purchase walkthrough was completed and
before any book existed. The next `/run-cycle` that reaches the Publisher step
creates a genuinely live, real-money payment page — there is no test/staging
buffer anymore. See `.env` for the (commented-out) test keys if you want to
switch back to test mode for any reason.

Payments run through **Paystack**, not Stripe — Stripe doesn't officially support
Nigeria as a business's home country. Paystack is Stripe-owned, built for Nigerian
businesses, and its Payment Pages are the equivalent of Stripe Payment Links.

**Pricing is in USD everywhere** (this is a global company) — but the *actual
charge* depends on your Paystack account's status:
- Once "Accept international payments" is approved on your account, checkout
  charges USD directly.
- Until then, `scripts/paystack_publish.py` automatically converts the USD price
  to NGN at a live exchange rate (no hardcoded/stale rate) and charges that —
  confirmed working against this account's test keys, since USD isn't approved
  yet (`PAYSTACK_CURRENCY=NGN` in `.env` reflects that today).

## What you're accepting by running this

- Once scheduled, the cycle runs **with no human approval step** — it will write
  files, run `git push`, and call the Paystack API on its own every week.
- Delivery is an unlisted download link (not DRM) — good enough at zero budget,
  not bulletproof against someone reposting the link.
- Covers are simple typographic templates, not AI-illustrated art (no image-gen
  budget).
- Marketing output (blog post, social captions) is drafted text only — nothing
  auto-posts to social platforms.

## One-time setup

### 1. Pandoc — done ✅

Installed via `winget install --id JohnMacFarlane.Pandoc` (v3.10). Needed to convert
manuscripts to EPUB/PDF. Verify any time with `pandoc --version`.

### 2. Python dependencies — done ✅

Installed via `pip install -r requirements.txt` (`requests`, `Pillow`).

### 3. GitHub repo + Pages — done ✅

- Repo: https://github.com/koladeoruku/ai-ebook-company (public — free-tier Pages
  requires a public repo)
- Pages is enabled, deploying from `main` branch, `/docs` folder (GitHub Pages can
  only serve the repo root or a folder literally named `docs` when deploying from
  a branch — that's why the storefront lives at `docs/`, not `storefront/`)
- Live storefront URL: **https://koladeoruku.github.io/ai-ebook-company/**

### 4. Paystack account — LIVE ✅ (USD approval still pending) ⬜

- Live secret/public keys are in `.env` (gitignored). Test keys are also kept
  there, commented out, in case you want to switch back to test mode.
- **USD is not confirmed enabled** on this account — it returned "Currency not
  supported" under test mode; not yet re-verified under live. To enable it:
  finish business KYC activation on Paystack, then request "Accept
  international payments" in the Preferences tab (Paystack says ~48hr
  review). Until confirmed, `PAYSTACK_CURRENCY=NGN` keeps the company running
  via the auto-conversion fallback described above.
- Once approved, flip `PAYSTACK_CURRENCY` from `NGN` to `USD` in `.env` (and in
  the secrets of any scheduled cloud routine) — no code changes needed.

### 5. Configure your environment — done ✅

`.env` exists locally (gitignored) with real **live** keys, `PAYSTACK_CURRENCY=NGN`
(current working fallback), and `STOREFRONT_BASE_URL` set to the live Pages URL.

### 6. Brevo account — still needed ⬜ (for Growth's resell emails)

Sign up free at https://www.brevo.com (free tier: ~300 emails/day), verify one
sender email address (no domain/DNS ownership needed for this), and get an API
key from the SMTP & API settings. Fill in `BREVO_API_KEY`, `BREVO_SENDER_EMAIL`,
and `BREVO_SENDER_NAME` in `.env`. Until this is done, the Growth department
still drafts and commits resell campaigns every cycle (once there are real
customers and a second book to recommend) — it just can't send them yet;
`scripts/send_campaign.py` fails cleanly rather than faking a send.

## Running the first cycle manually

Before trusting the weekly schedule, run one cycle yourself inside Claude Code so
you can watch every step and read the actual output. Because keys are live, the
Publisher step will create a real, purchasable payment page the moment it runs —
there's no test-mode buffer:

```
/run-cycle
```

Check afterward:
- `company/books/<slug>/manuscript.md` — is the writing actually good?
- `company/books/<slug>/cover.png` and the `.epub`/`.pdf` files — did they generate?
- `docs/index.html` (open locally in a browser, or the live Pages URL after a push)
  — does the catalog render, and does the USD price look right?
- The Paystack payment link in `company/books/<slug>/metadata.json` — this is now
  a **real** link. Either complete an actual small real purchase yourself to
  confirm the post-purchase redirect delivers the download, or temporarily set
  `PAYSTACK_SECRET_KEY`/`PAYSTACK_PUBLIC_KEY` back to the commented-out test keys
  in `.env` for a risk-free test-mode purchase first, then switch back to live.
- `company/reports/<date>.md` — is this something you'd trust unattended?

## Turning on the weekly autonomous cycle

This project is designed to run its weekly cycle as a **cloud-hosted scheduled
routine** (Claude's `/schedule` mechanism), not a local Windows Task Scheduler job.
That means the actual weekly execution happens on Anthropic's infrastructure, not
your laptop — your laptop is where you build, review, and can still run `/run-cycle`
manually any time.

To set it up, use the `schedule` skill (`/schedule`) from within this project and
point it at `/run-cycle` on a weekly interval. You'll need to make sure the routine
has access to: this repo (so it can pull/push), and the same environment variables
(`PAYSTACK_SECRET_KEY`, `PAYSTACK_CURRENCY`, `STOREFRONT_BASE_URL`, and once set up,
`BREVO_API_KEY`/`BREVO_SENDER_EMAIL`/`BREVO_SENDER_NAME`) configured as secrets for
the routine rather than a local `.env` file, since the routine doesn't run on this
machine.

Let the first scheduled run fire and read its report before considering this
"fire and forget."

## Project layout

```
.claude/agents/       role prompts (rd, researcher, ghostwriter, editor, cmo, publisher, growth)
.claude/commands/     run-cycle.md — the CEO's weekly orchestration prompt
.claude/settings.json permission allowlist so the cycle runs unattended
company/              persistent state: org chart, backlog, ledger, books, reports,
                       craft_playbook.md / seo_playbook.md / growth_playbook.md,
                       customers.json, unsubscribed.md, campaigns/
scripts/               make_cover.py, generate_storefront.py, paystack_publish.py,
                       fetch_customers.py, send_campaign.py
docs/                  the static site GitHub Pages serves (regenerated each cycle)
```
