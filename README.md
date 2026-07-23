# Autonomous Press — an AI ebook company that runs itself

This repo *is* the company. A weekly cycle researches a trending topic, writes and
edits a full ebook, prices and markets it, creates a real Paystack payment page, and
publishes it to a free static storefront — then writes you a plain-English report.
See `.claude/commands/run-cycle.md` for the orchestration logic and
`.claude/agents/*.md` for each department's role.

Nothing here is a demo — when fully wired up, this creates real, sellable products
and real Paystack payment links. Do the one-time setup below carefully, and run the
first cycle manually before trusting the automated weekly schedule.

Payments run through **Paystack**, not Stripe — Stripe doesn't support Nigeria for
standard merchant accounts. Paystack is Stripe-owned, built for Nigerian businesses,
and its Payment Pages are the equivalent of Stripe Payment Links. Prices are in
whole Naira (NGN) throughout.

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

### 4. Create a Paystack account — still needed ⬜

Sign up free at https://paystack.com (Nigeria is fully supported). Get your
**test mode** secret key from Settings → API Keys & Webhooks (starts with `sk_test_`).
You'll switch to a live key only after you've verified a full test purchase works
end to end.

### 5. Configure your environment — partially done

`.env` already exists locally (gitignored) with:
```
PAYSTACK_SECRET_KEY=       <- fill this in from step 4
STOREFRONT_BASE_URL=https://koladeoruku.github.io/ai-ebook-company
```

## Running the first cycle manually

Before trusting the weekly schedule, run one cycle yourself inside Claude Code so
you can watch every step and read the actual output:

```
/run-cycle
```

Check afterward:
- `company/books/<slug>/manuscript.md` — is the writing actually good?
- `company/books/<slug>/cover.png` and the `.epub`/`.pdf` files — did they generate?
- `docs/index.html` (open locally in a browser, or the live Pages URL after a push)
  — does the catalog render?
- The Paystack payment link in `company/books/<slug>/metadata.json` — open it and
  complete a **test-mode** purchase (Paystack's test cards are listed in their docs,
  e.g. a test Visa card with any future expiry, CVV `408`, PIN `0000`, OTP `123456`
  — check Paystack's current test-cards page since these can change) to confirm the
  post-purchase redirect actually delivers the download.
- `company/reports/<date>.md` — is this something you'd trust unattended?

Only switch `PAYSTACK_SECRET_KEY` to a **live** key once you're satisfied.

## Turning on the weekly autonomous cycle

This project is designed to run its weekly cycle as a **cloud-hosted scheduled
routine** (Claude's `/schedule` mechanism), not a local Windows Task Scheduler job.
That means the actual weekly execution happens on Anthropic's infrastructure, not
your laptop — your laptop is where you build, review, and can still run `/run-cycle`
manually any time.

To set it up, use the `schedule` skill (`/schedule`) from within this project and
point it at `/run-cycle` on a weekly interval. You'll need to make sure the routine
has access to: this repo (so it can pull/push), and the same environment variables
(`PAYSTACK_SECRET_KEY`, `STOREFRONT_BASE_URL`) configured as secrets for the routine
rather than a local `.env` file, since the routine doesn't run on this machine.

Let the first scheduled run fire and read its report before considering this
"fire and forget."

## Project layout

```
.claude/agents/       role prompts (researcher, ghostwriter, editor, cmo, publisher)
.claude/commands/     run-cycle.md — the CEO's weekly orchestration prompt
.claude/settings.json permission allowlist so the cycle runs unattended
company/              persistent state: org chart, backlog, ledger, books, reports
scripts/               make_cover.py, generate_storefront.py, paystack_publish.py
docs/                  the static site GitHub Pages serves (regenerated each cycle)
```
