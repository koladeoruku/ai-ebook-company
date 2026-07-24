# Ledger

Every cost here should be $0 by design (zero-budget constraint) — this tracks listing price and, once you check Paystack, actual revenue. Claude/Anthropic usage cost is real but happens outside this ledger (it's your Claude subscription/API cost, not a company expense the loop tracks).

Prices are always in USD — this company's one canonical pricing currency — even on cycles where the actual Paystack charge was auto-converted to NGN (see `charge_currency`/`charge_amount` in a book's `metadata.json`) while international USD payments are pending approval.

**Running totals**
- Books published: 1
- Total listed catalog value: $7.99
- Revenue: check your Paystack dashboard directly — this file does not auto-reconcile actual sales, only what was listed.

## Books

<!-- Format for each entry:
### <title> (<slug>)
- published_date: YYYY-MM-DD
- price: $X.XX (USD, canonical)
- charge_currency / charge_amount: whatever was actually charged (may be NGN, converted)
- paystack_payment_link: <url>
-->

### Declutter When You're Overwhelmed (declutter-when-overwhelmed)
- published_date: 2026-07-24
- price: $7.99 (USD, canonical)
- charge_currency / charge_amount: NGN 10,932.38 (converted at rate 1,368.26 USD/NGN)
- paystack_payment_link: https://paystack.com/pay/z-xd9az5kl
