# End-of-day handover update, 2026-10-06 (Shaka: "lets wrap it up and call it a day. update the handover"). Idempotent.
import re,sys,os
root=sys.argv[1] if len(sys.argv)>1 else '.'
H=os.path.join(root,'handover/HANDOVER.md'); S=os.path.join(root,'handover/sessions/2026-10-06.md')
h=open(H,encoding='utf-8').read()

# 1) the stray one-line bullets appended after the session log → gone (folded into the blocks below)
for line in ['- Round 12 (HvB): UFO greens the banner human side','- Round 13 (HvB): Round-trips column + Human routes fold removed','- Humans vs Bots LIVE 2026-10-06: VOL_SPLIT_LIVE=true','- 2026-10-06 tiles: clickable badges','- HvB share card + Socials rows LIVE 2026-10-06']:
    h=re.sub(r'\n'+re.escape(line)+r'[^\n]*','',h)

# 2) Current state → the end-of-day block
start=h.index('## Current state (2026-10-06, in progress)'); end=h.index('## Before that (end of 2026-10-05)')
cur='''## Current state (end of 2026-10-06)

**2026-10-06 (Tuesday), closed by Shaka ("lets wrap it up and call it a day"). Three pushes by him during the day (Charts 13:21,
Actions 13:40, Humans vs Bots round 11 `02323fe3f`); the evening's work is written on both copies, verified in the harness, and
NOT yet pushed — the commit line is at the end of the session file. Nothing is half-done.**

**HUMANS VS BOTS IS LIVE (in the code).** The Volume tile carries a bot icon (the "Classic" robot, `logos/hvb/ic-bot.svg`) right of
its ⓘ, the Holders pattern; `VOL_SPLIT_LIVE=true`, the preview dot is gone. The window (`VolumeSplitModal`, `.vs-*`) is the version
of rounds 1–14: his banner (green human side on UFO via `.vs-sky-tint`, 56 % veil), the lit coin over a centred title, the two cards
with his art, the split bar + daily chart, folds By pool · Top bot contracts · How we tell, then the confidence note (`.vs-conf`).
Removed on his word: the Round-trips column, the Human routes fold, every round-trip number (the concept stays in How we tell).
**The share card** (`tools/hvb-share.py`, `.hvs-*`, `HvbShareCard` / `HvbShareModal` / `HvbShareSocial`): 1200×675, screenshot-only,
from the 📷 beside the window's period pills (opens on the window's token + period; Card PTGC / UFO / BOTH + Period toolbar) and
from Socials — a "Humans vs Bots · Who moves the volume" row with his robot (`logos/hvb/sh-bot.webp`) in all three columns, opening
on 30 days. Mock-ups + decisions: `design/volume-split/mock-share-v1.html` (v3) and `renders/share-v3-*.png`, `hvb-share-live-ptgc.png`,
`hvb-socials-rows.png`. **Tile badges**: the clickable ones (bot, Holders people, RH) are drawn in the token colour — the two icons
are CSS masks (`.h2-hd` span, `--ic`) filled with `var(--a)`, RH is a `.h2-rh` badge the icons' size; the ⓘ circles and the LP %
(`.h2-pct`) stay grey. **Classification** (builder `scripts/build-swap-volume.mjs`, SCHEMA 3, 90 d): round trips are bots whoever sent
them, named/verified routers and many-recipient senders are human (switch.win recognised that way, its router + adapters now named),
a wallet trading ≥ 50×/day through a router is a bot; verified against DexScreener pool by pool; stated confidence: numbers ~98 %,
bot side ~90 %, human side ~85 %. The Telegram announcement is drafted (session file, "Announcement") — post it after the push +
a live look.

**Open / owed:** (1) Shaka's push (commit line in the session file), then a live look at the Volume tile icon, the window, the 📷
card (PTGC / UFO / BOTH), the Socials rows, Mac + phone — and the Telegram post. (2) **Worker v7's cron never reached GitHub**
(deployed 14:00; no `workflow_dispatch` runs at 14:07 / 15:07 UTC, no scheduled event in the Worker's Events) — check Cloudflare →
ptgcapi → Settings → Triggers (is the `7 * * * *` cron saved and enabled, is `DISPATCH_TOKEN` present) and the Logs at :07; GitHub's
own schedule still delivers ~4 runs a day. (3) The UFO TXNS 24H tile reads ~10,000 vs ~100 real swaps a day — explained to Shaka,
awaiting his yes to fix. (4) The banner robot cannot be shrunk alone (one image) — a re-export if he wants him smaller. (5) UFO day-90
real test 2026-10-07 after ~07:30 PDT. (6) Live looks still owed from 2026-10-04 / 10-05 (Calculators, KPI phone, KPI backgrounds).
(7) Decision -13(c), the orphan `data` branch.

'''
h=h[:start]+cur+h[end:]

# 3) Next up -14 → the live state
i=h.index('-14. **THE VOLUME SPLIT WINDOW'); j=h.index('-13. **The Actions review')
h=h[:i]+'''-14. **HUMANS VS BOTS (2026-10-06) — LIVE in the code, NOT pushed (evening batch; commit line in the session file).** Volume tile bot
   icon → `VolumeSplitModal`; the 📷 share card + the Socials rows; tile badges in the token colour. After the push: Actions → Data
   Pipeline → Run workflow → `only=swap-volume` if the live file is still schema < 3 (the window accepts any schema ≥ 1, the
   builder's first schema-3 run rebuilds 90 d in ~100 s), then his live look + the Telegram post. Owed: the TXNS 24H tile fix (his
   yes), the banner robot re-export (optional), a phone look at the card. Design + method: `design/volume-split/README.md`,
   `mock-share-v1.html`; build scripts `tools/volume-split.py` (+ the round edit scripts in `_to_delete/hvb-round*.py`, applied),
   `tools/hvb-share.py`.
'''+h[j:]

# 4) session log entry
old='  pair-volume on CoinGecko Pro, dao-buys carrying forward.\n- `sessions/2026-10-05.md`'
new='''  pair-volume on CoinGecko Pro, dao-buys carrying forward. Evening: HUMANS VS BOTS — the window through 14 design rounds (his
  art, his mock-ups), the classification self-check (round trips, switch.win, the wallet rule; confidence stated), the DAO Buys
  creature-clipping fix, the RH cores pinned, go-live (Volume tile bot icon), tile badges in the token colour, the share card
  (3 mock rounds → built) + Socials rows, the Telegram announcement; everything after round 11 NOT pushed at close.
- `sessions/2026-10-05.md`'''
if 'Evening: HUMANS VS BOTS' not in h:
    assert old in h; h=h.replace(old,new,1)
open(H,'w',encoding='utf-8').write(h)

# 5) the session file: close-of-day block + the announcement + the commit line
s=open(S,encoding='utf-8').read()
if '## Close of day' not in s:
    s+='''
## Close of day (Shaka: "lets wrap it up and call it a day")

**State:** both copies identical — index.html md5 `f452e7ac4dec0414da21438d0e0d8e07`, h2.css `07c3f76e061fd226abfe6029f4d3f5be`.
Last push by Shaka: `02323fe3f` (round 11). Uncommitted on the Mac (17 paths): index.html, h2.css, handover (2), `tools/hvb-share.py`,
`logos/hvb/ic-bot.svg`, `logos/hvb/sh-bot.webp`, `design/volume-split/` (mock-share-v1.html, renders), `_to_delete/hvb-round12/13/14-edit.py`,
`_to_delete/hvb-golive-edit.py`, `_to_delete/tile-badges-accent-edit.py`, `_to_delete/tile-badges-accent-css.py`, `_to_delete/hvb-round12.md`,
`_to_delete/handover-eod-2026-10-06.py`. (`_to_delete/` = Claude cannot delete from the bridge; Shaka may `rm -rf _to_delete` before
committing or leave it — nothing there is referenced.)

**Commit line (his):**
```
cd ~/Desktop/PTGC-UFO && git add -A && git commit -m "Humans vs Bots: share card (1200x675, screenshot) from the window's camera and a Socials row in all three columns with the robot icon; goes LIVE with the Volume tile bot icon; tile badges in the token colour; rounds 12-14; handover" && git pull --rebase && git push
```

**Then:** hard-refresh ptgc-ufo.com (Pages ~1–2 min) → Volume tile bot icon → the window → 📷 → PTGC / UFO / BOTH cards → Socials
rows (three columns) → phone. If the window says "Couldn't load" or shows no 90D data: Actions → Data Pipeline → Run workflow →
`only=swap-volume`. Then the Telegram post below.

### Announcement (Telegram, final wording — no "our pools", emoji version)

🤖 **Humans vs Bots is live on the dashboard** 👤

One of the strongest things about the PTGC and UFO contracts has always been hard to *see*. Every pool PTGC and UFO trade in has a
slightly different price at any given second, and arbitrage bots exist to close that gap. Every time one does, it trades through
those pools, and every trade pays the fee: 5% on PTGC, 6% on UFO. 💰

The bots aren't thinking about holders. They're chasing a few cents of spread, and in the process they generate volume and value
for holders around the clock, whether anyone in this chat is awake or not. 🌙

Until now that was a thing people said. Now it's a thing you can watch. 👀

📊 Open the Volume tile on the dashboard and tap the new bot icon in the corner. The window splits every trade on every pool into
two piles: people, and bots. You get the human volume, the bot volume, how much value each side generated for the contract, the
split by pool, the biggest bot contracts, and a daily chart of who moved the money. Switch between PTGC, UFO, or both together,
over 24 hours, 7, 30, or 90 days. 🛸

🔄 Updated every hour. Go look at what the bots have been paying you.

🔗 ptgc-ufo.com
'''
    open(S,'w',encoding='utf-8').write(s)
print('handover ok')
