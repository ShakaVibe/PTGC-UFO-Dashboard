## Round 12 — 2026-10-06 (Humans vs Bots: UFO banner, confidence note, Round-trips tip, darker header; Classic bot icon chosen)

Shaka (live UFO look): (1) banner's human side should go UFO green on UFO; (2) a disclaimer at the foot — vastly right, a few small ones may be mislabelled; (3) the go-live icon = option 1 "Classic" from `renders/bot-icons.png`; then (4) "what are Round trips in Top bot contracts? is How we tell up to speed?" and (5) "darken the header image more".

Done (edit script `_to_delete/hvb-round12-edit.py`, idempotent, applied to both copies → index.html md5 `cfd9509a2d95ea523f1c0021e3bf7d80`):
- `.vs-sky-tint` (mix-blend-mode:color, green 0→30 % solid, gone by 56 %) rendered only when `token==='UFO'` between `.vs-sky` and `.vs-sky-veil` — the gold man and his lines go UFO green, the robot keeps his blue. One image, so this is a colour blend not a re-export.
- `.vs-sky-veil` flat band 40 % → 56 % (and the fade 84 → 88 %) — the header reads darker, art still visible.
- `<p className="vs-conf">` after the How we tell fold: "How sure are we? Very. … read this as a very close picture rather than a to-the-cent ledger." (12.5 px, 42 % white, hairline above).
- "Round trips" column header carries an InfoTip (share of the contract's trades that were round trips; higher = surer it is a bot; low = bot only because it calls pools directly).
- How we tell gained the wallet rule: a wallet trading through a router ≥ 50×/day is a bot driving a router → "bot wallet via …".
- `logos/hvb/ic-bot.svg` — the Classic robot (24-px grid, grey #B9C2CC) saved for go-live; NOT wired yet (go-live = `VOL_SPLIT_LIVE=true`, `img.h2-hd`-style icon right of the Volume tile's ⓘ, dot removed). Pick sheet: `design/volume-split/renders/bot-icons.png`.

Verified in harness: UFO → `.vs-sky-tint` present, PTGC → absent; `.vs-conf` 387 chars; How we tell contains "bot wallet via"; renders vs12-ufo-top / vs12-ptgc-top / vs12-foot.
