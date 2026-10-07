# RH Cores window — the Liquidity tile's "RH" button (2026-10-07)

Shaka (his screenshot of the old "LP with RH Core Coins" modal, right after the Volume window went live): "can you mock up a change
to the RH button in liquidity?"

The old window: `showRHModal` in index.html (~line 14416) — a `max-w-2xl` card, the total in a box top-right, six flat rows
(logo, pair, liquidity / volume / 24h, a 📈 link). Data: `rhCoresPairs` (the token's DexScreener pairs flagged `isRHCore`; WETH is
out since 2026-09-28) and `rhCoresLiq`.

## Mock v1 — `mock-rh-v1.html` → `renders/rh-v1-ufo.png`, `rh-v1-ptgc.png`, `rh-v1-phone.png` (390)
`?token=PTGC`. UFO's six rows are his screenshot's numbers; PTGC's per-pair figures are illustrative (the core total $650K and the
$1.207M total are the 11:15 UTC lv-snapshot's, the split is a guess) — the build reads the live pairs.

Decisions, top to bottom:
- **The Volume / Humans vs Bots shell** (same window family, same edge and halo).
- **Plate = Richard Heart on stage** (`logos/socials/rh-heart-stage.jpg`, the Socials RH Core Liquidity card's photo), him at the right,
  the dark two thirds at the left under a left-to-right veil; the lit coin (140 px) and the title "UFO **RH Cores**" sit LEFT, not
  centred, so the type never crosses his face. Phone: the stack centres and he stands behind it at the right.
- Subtitle names the six cores in one line; "DexScreener · live" where the other windows say "as of".
- **Hero**: RH CORE LIQUIDITY (the lit tile, the droplet icon, the figure at 44 px, "84.2 % of all UFO liquidity ($1,009,554)" with a
  share bar) · POOLS (6 of the six cores) · 24H VOLUME through the core pools.
- **Where it sits** — one stacked bar of the six pools in the cores' own colours (WPLS blue, PLSX green, INC lime, HEX magenta,
  eHEX orange, PRVX purple), the key under it with each share.
- **The six rows**, framed, in the LP Pairs table's language: the core's disc (the build uses `CORE_LOGOS`; the mock draws discs),
  pair in the token colour + "HEX pair", LIQUIDITY big, the share + a mini-bar in the core's colour, VOLUME 24H, the 24h price move as
  a red / green badge (DexScreener's PRICE change, as on the LP table), the DexScreener link as the LP table's dark glass square.
  Rows sort by liquidity (as today). A chain-read pool (DexScreener missing it) prints "—" for volume and the move.
- The honesty line: what the cores are, WETH is not one, where the numbers come from.
- Phone: hero stacks (RH tile full width, the two small ones side by side), rows become three lines — logo · pair · badge /
  liquidity · volume / share bar · link.

Not in v1 (ask): a PTGC / UFO switch inside the window; a 📷 share card (the Socials RH card exists for that); the pool's token
amounts (how much UFO / how much HEX sits in the pool) under the liquidity figure.

## Built (same day) — Shaka: "make it live."
`tools/rh-cores.py` on index.html AFTER `tools/volume-window.py` (it reuses the `vw-tile` / `vw-card` / `vw-hdr` / `vw-conf` classes;
md5 after both `e1f25b324708343a6d18e491b4379ba3`): the `rc-*` CSS after the `vw-*` block, `RC_CORE` (the six cores' colours and
names) + `RhCoresModal` at module scope just above `VolumeModal`, and the Dashboard's 68-line inline "LP with RH Core Coins" modal
replaced by `<RhCoresModal token cfg data pairs={rhCoresPairs} totalLiq={data?.liq} onClose/>` — the same `rhCoresPairs` /
`data.liq` the old window and the tile read. Rows sort by liquidity (as before). Honest: a chain-read pair (`_fromChain`) prints "—"
for volume and the move (the harness's UFO pairs are all chain-read, so the UFO render shows exactly that; PTGC with `DS_PAIRS=burn`
shows DexScreener's); the hero's 24H volume is "—" unless every pair's volume is known; the share of all liquidity is "—" without
`data.liq`. The partner logos are DexScreener's (`getLogo`), hidden on error — the harness stub fakes them (every disc is the UFO
coin there). Harness: `probes/rc-state.js`; renders `renders/build-v1-ptgc.png` (1440, DS_PAIRS=burn), `build-v1-ufo.png` (chain-read
pairs), `build-v1-phone.png` (390). Gotcha found: `.sh` is the Socials Hub's class — the row cells are `rc-sh` / `rc-liq` / `rc-vol` /
`rc-pp`, never bare names.
