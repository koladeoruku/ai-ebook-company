# Org Chart

**Company**: Autonomous Press (working name — change freely in `scripts/generate_storefront.py` and `scripts/make_cover.py`)

**Founder**: kolad.oruku1@gmail.com — reviews `company/reports/`, owns the GitHub, Paystack, Brevo, and Anthropic accounts this company runs on.

| Role | Subagent file | Responsibility |
|---|---|---|
| CEO | `.claude/commands/run-cycle.md` | Reads company state, picks the week's topic, delegates every step below, writes the weekly report. Not a subagent — this is the top-level orchestration run each cycle. |
| R&D | `.claude/agents/rd.md` | Studies best-in-class nonfiction books and content/blog marketing; implements exactly one concrete craft improvement every cycle, before the book is written. Doesn't need permission to research or implement — standing autonomy. |
| Researcher | `.claude/agents/researcher.md` | Finds trending topics/unmet demand via free web search, ranks candidates. |
| Ghostwriter | `.claude/agents/ghostwriter.md` | Writes the full manuscript for the chosen topic. |
| Editor | `.claude/agents/editor.md` | Revises the manuscript for quality, consistency, and safety; can veto a bad draft. |
| CMO | `.claude/agents/cmo.md` | Writes the blurb, suggests a price, drafts the problem-first blog/sales post + social captions. |
| Publisher | `.claude/agents/publisher.md` | Generates the cover, converts to EPUB/PDF, creates the Paystack listing, rebuilds the storefront, commits and pushes. |
| Growth | `.claude/agents/growth.md` | Marketing/growth: applies SEO to the new book plus one previously-published book every cycle, and resells the catalog to real past buyers (pulled from Paystack's own transaction history) via email once Brevo is configured. Doesn't need permission to research, fetch data, or make its changes — standing autonomy. |

R&D and Growth are the two departments with standing autonomy to research and act without asking the founder first, every cycle — that's a deliberate choice, not an oversight. No role has been given ad-spend or any paid-API access beyond what's documented in the README — the company operates at zero cash budget by design (Brevo/free-tier email is the one addition beyond the original Stripe/Paystack + GitHub Pages stack, still free-tier). See the README for the tradeoffs that follow from that.

## Living playbooks

Two departments keep an append-only log of what they've researched and adopted, read by the roles their work affects:
- `company/craft_playbook.md` (R&D) — read by Ghostwriter, Editor, CMO
- `company/seo_playbook.md` (Growth) — read by CMO
- `company/growth_playbook.md` (Growth) — Growth's own log of resell-email practices

## Customer/compliance state

- `company/customers.json` — rebuilt every cycle from Paystack's real transaction history (never scraped/bought from anywhere else)
- `company/unsubscribed.md` — emails that must never receive another campaign; enforced by `scripts/fetch_customers.py` and `scripts/send_campaign.py`
- `company/campaigns/` — every drafted (and, once sent, logged) resell campaign
