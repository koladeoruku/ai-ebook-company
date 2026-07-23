# Autonomous Press — an AI ebook company that runs itself

This repo *is* the company. A weekly cycle researches a trending topic, writes and
edits a full ebook, prices and markets it, creates a real Stripe payment link, and
publishes it to a free static storefront — then writes you a plain-English report.
See `.claude/commands/run-cycle.md` for the orchestration logic and
`.claude/agents/*.md` for each department's role.

Nothing here is a demo — when fully wired up, this creates real, sellable products
and real Stripe payment links. Do the one-time setup below carefully, and run the
first cycle manually before trusting the automated weekly schedule.

## What you're accepting by running this

- Once scheduled, the cycle runs **with no human approval step** — it will write
  files, run `git push`, and call the Stripe API on its own every week.
- Delivery is an unlisted download link (not DRM) — good enough at zero budget,
  not bulletproof against someone reposting the link.
- Covers are simple typographic templates, not AI-illustrated art (no image-gen
  budget).
- Marketing output (blog post, social captions) is drafted text only — nothing
  auto-posts to social platforms.

## One-time setup

### 1. Install pandoc (needed to convert manuscripts to EPUB/PDF)

Download and install from https://pandoc.org/installing.html (Windows installer).
Verify with:

```
pandoc --version
```

### 2. Install Python dependencies

```
pip install -r requirements.txt
```

### 3. Create a Stripe account

Sign up free at https://stripe.com. Get your **test mode** secret key from
Developers → API keys (starts with `sk_test_`). You'll switch to a live key only
after you've verified a full test purchase works end to end.

### 4. Create a GitHub repo and enable Pages

1. Create a new repo on GitHub (public or private — Pages works with either on
   paid GitHub plans; use **public** if you're on a free personal account, since
   free-tier Pages requires a public repo).
2. Push this project to it (see `git init` step below).
3. In the repo's Settings → Pages, set the source to deploy from the `main`
   branch, folder `/docs` (GitHub Pages can only serve the repo root or a
   folder literally named `docs` when deploying from a branch — that's why
   the storefront lives at `docs/` in this repo, not `storefront/`).
4. Note the resulting URL (e.g. `https://yourusername.github.io/your-repo-name`).

### 5. Configure your environment

```
cp .env.example .env
```

Fill in `STRIPE_SECRET_KEY` (the test key from step 3) and `STOREFRONT_BASE_URL`
(the Pages URL from step 4).

### 6. Initialize git and push

```
git init
git add -A
git commit -m "Initial scaffold"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
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
- `docs/index.html` (open locally in a browser) — does the catalog render?
- The Stripe payment link in `company/books/<slug>/metadata.json` — open it and
  complete a **test-mode** purchase (use Stripe's test card `4242 4242 4242 4242`)
  to confirm the post-purchase redirect actually delivers the download.
- `company/reports/<date>.md` — is this something you'd trust unattended?

Only switch `STRIPE_SECRET_KEY` to a **live** key once you're satisfied.

## Turning on the weekly autonomous cycle

This project is designed to run its weekly cycle as a **cloud-hosted scheduled
routine** (Claude's `/schedule` mechanism), not a local Windows Task Scheduler job.
That means the actual weekly execution happens on Anthropic's infrastructure, not
your laptop — your laptop is where you build, review, and can still run `/run-cycle`
manually any time.

To set it up, use the `schedule` skill (`/schedule`) from within this project and
point it at `/run-cycle` on a weekly interval. You'll need to make sure the routine
has access to: this repo (so it can pull/push), and the same environment variables
(`STRIPE_SECRET_KEY`, `STOREFRONT_BASE_URL`) configured as secrets for the routine
rather than a local `.env` file, since the routine doesn't run on this machine.

Let the first scheduled run fire and read its report before considering this
"fire and forget."

## Project layout

```
.claude/agents/       role prompts (researcher, ghostwriter, editor, cmo, publisher)
.claude/commands/     run-cycle.md — the CEO's weekly orchestration prompt
.claude/settings.json permission allowlist so the cycle runs unattended
company/              persistent state: org chart, backlog, ledger, books, reports
scripts/               make_cover.py, generate_storefront.py, stripe_publish.py
docs/                  the static site GitHub Pages serves (regenerated each cycle)
```
