# Alpaca Trading Claude Routines

Automated trading routines for an Alpaca **paper trading** account, executed by Claude Code Routines (scheduled cloud sessions).

## Active routine

**Alpaca daily paper trading** — trigger `trig_01AsNoAraxUSqfs2dYNNKsg4`

- **Schedule:** `0 14 * * 1-5` (weekdays at 14:00 UTC — 30 minutes after US market open during EDT)
- **Execution:** each firing spawns a fresh Claude Code session in an environment that has `ALPACA_API_KEY` / `ALPACA_SECRET` set (paper keys, account `PA3CA37T2KD3`)
- **Notifications:** push notification on completion
- **Prompt:** see [`routines/daily-paper-trading.md`](routines/daily-paper-trading.md)

## What the routine does

1. **Read the account** — live equity, cash, buying power, positions, open orders, and market clock via the Alpaca paper REST API (`https://paper-api.alpaca.markets`). Never trades on assumptions; skips trading entirely if reads fail or the market is closed.
2. **Research** — current market news via web search plus Alpaca market data (`https://data.alpaca.markets`) for prices and recent bars; reviews existing holdings against entry.
3. **Decide under guardrails** — cash only, liquid US large caps / broad ETFs (small crypto allowed), max ~$5,000 per new position, max 8 holdings, limit orders only, and "no trades today" is always a valid outcome.
4. **Execute** — places/cancels orders via the API and reads back order status to confirm.
5. **Report** — a concise markdown report: TL;DR, account snapshot, market overview, decisions with rationale, watchlist, and risk note.

## Safety

- Keys are **paper trading only** (`PK…` prefix) — no real money can move.
- Credentials live in the environment configuration, never in this repo.
- Guardrails in the prompt forbid margin abuse, options, penny stocks, and leveraged/inverse ETFs.

## History

- **2026-08-08** — First manual API test: $100 notional market buy of BTC/USD, filled at $64,977.12 (0.001509 BTC). Routine created and verification run fired.
