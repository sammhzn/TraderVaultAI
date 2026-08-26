# Trader Vault AI
## MASTER STRATEGY DOCUMENT
Version: 1.0
Owner: Sam
Status: Active

---

# PURPOSE

Trader Vault AI is designed to execute ONLY this strategy.

The AI must NEVER invent new strategies.

The AI may only:

- Execute this strategy
- Record trades
- Learn from historical results
- Suggest improvements for user approval

The AI must NEVER change strategy rules automatically.

---

# MARKET

Instrument

XAUUSD

---

# TIMEFRAME

Execution Timeframe

1 Minute

---

# DAILY LEVELS

At the beginning of every trading day:

Store

Previous Day High

Previous Day Low

These are the ONLY liquidity levels used for that day.

Reset at the beginning of every new trading day.

---

# LIQUIDITY SWEEP

Valid SELL Setup

Entire candle body closes ABOVE Previous Day High.

Both OPEN and CLOSE must be above PDH.

Wicks never count.

---

Valid BUY Setup

Entire candle body closes BELOW Previous Day Low.

Both OPEN and CLOSE must be below PDL.

Wicks never count.

---

# SIGNAL CANDLE

SELL

First RED candle after valid breakout.

BUY

First GREEN candle after valid breakout.

---

# ENTRY

SELL

Next candle ONLY.

Must CLOSE below signal candle body.

If it fails

Cancel setup.

BUY

Next candle ONLY.

Must CLOSE above signal candle body.

If it fails

Cancel setup.

---

# INVALID SETUP

One liquidity sweep

=

One opportunity.

If confirmation fails

Ignore all future signals.

Wait for an entirely NEW liquidity sweep.

---

# STOP LOSS

Initial Stop Loss

20–30 pips from entry.

Future versions may optionally support strategy-based SL for testing, but the default implementation uses the fixed stop.

---

# LAYERING

Maximum Layers

5

Layer 1

Initial trade.

Additional layers

Only after valid pullback structure.

Never use fixed grid spacing.

Never use martingale.

Maximum adverse movement

1.00 from initial entry.

No additional layers beyond that.

---

# TP1

TP1 is the strongest previous reversal before entry.

At TP1

Close newest profitable layers first.

(LIFO)

Keep older layers open.

Move remaining layers to their own Break Even.

---

# BREAK EVEN

Every remaining open trade

Moves to its own entry price.

Not average price.

Every layer managed independently.

---

# TP2

TP2 is the next strongest previous reversal.

Continue managing remaining layers until

TP2

Break Even

Manual Close

Future exit rules

---

# TRADER VAULT

Store

Every trade

Entry

Exit

Layers

Screenshots

Profit

Loss

Reason

Market Session

Learning Notes

---

# AI

AI is NOT allowed to trade freely.

AI may

Review trades

Review statistics

Review screenshots

Find recurring patterns

Suggest improvements

User decides whether strategy changes are accepted.

---

END OF DOCUMENT