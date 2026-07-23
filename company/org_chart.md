# Org Chart

**Company**: Autonomous Press (working name — change freely in `scripts/generate_storefront.py` and `scripts/make_cover.py`)

**Founder**: kolad.oruku1@gmail.com — reviews `company/reports/`, owns the GitHub, Paystack, and Anthropic accounts this company runs on.

| Role | Subagent file | Responsibility |
|---|---|---|
| CEO | `.claude/commands/run-cycle.md` | Reads company state, picks the week's topic, delegates every step below, writes the weekly report. Not a subagent — this is the top-level orchestration run each cycle. |
| Researcher | `.claude/agents/researcher.md` | Finds trending topics/unmet demand via free web search, ranks candidates. |
| Ghostwriter | `.claude/agents/ghostwriter.md` | Writes the full manuscript for the chosen topic. |
| Editor | `.claude/agents/editor.md` | Revises the manuscript for quality, consistency, and safety; can veto a bad draft. |
| CMO | `.claude/agents/cmo.md` | Writes the blurb, suggests a price, drafts blog post + social captions. |
| Publisher | `.claude/agents/publisher.md` | Generates the cover, converts to EPUB/PDF, creates the Paystack listing, rebuilds the storefront, commits and pushes. |

No role has been given social-posting, ad-spend, or any paid-API access — the company operates at zero cash budget by design. See the plan/README for the tradeoffs that follow from that.
