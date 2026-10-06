# Volume Split — people vs arbitrage bots (2026-10-06)

Shaka: "both ptgc and ufo heavily rely on the volume that it gets from the arb bots. I would like to add a little icon to the
volume box like we just did to the holders box. for now I want to hide it down with a very small faint dot in the bottom right…
Behind this button should be a nice window… volume broken down between Human Volume and ARB Bot volume." Both tokens, no known
bot addresses ("1 no, 2 both").

## Data — `scripts/build-swap-volume.mjs` → `data/swap-volume.json` (hourly, the rpc lane's last step)
- Every PTGC / UFO pool (DexScreener's list + the pinned RH cores), Swap events, 30 days kept, incremental (cursor; the cache file
  `data/swap-volume-cache.json` holds the compact trade rows and is not deployed).
- **Class = the Swap's `sender`**: a known router / aggregator → human (PulseX v1, v2, the current PulseXSwapRouter 0xda9a…, Piteas);
  anything else → bot; a sender PulseScan names as a verified Router / Aggregator / Swap contract is promoted to human automatically.
  Measured first (a day of the main pools): 160 of 172 swaps from six unverified contracts, ~28 each; 13 txs touching two pools.
- USD = token-side amount × the hourly close (`charts-intraday.json`; daily close beyond 14 d). Unpriced trades are counted, not valued.
- File: per token `hours` ([hourTs, humanN, humanUsd, botN, botUsd]) + `periods` 24h / 7d / 30d (totals, token amounts, per pool,
  top 25 senders) + `routers` (the human paths) + `pools`.

## Window — `VolumeSplitModal` (index.html, module scope above `NhDot`; CSS `vs-*`), `tools/volume-split.py`
- Hidden: `VOL_SPLIT_LIVE=false` → the faint dot bottom-right (`VsDot`, 16 %, token colour) on the dashboard. Live = the constant
  true (the dot goes); the Volume tile's icon entrance (right of the ⓘ, like Holders) is the next step then.
- Header: the Holders window's plate for now (his art for this window is owed — ask); title "Volume Split"; PTGC / UFO / BOTH;
  24H / 7D / 30D (opens on 7D); "as of" (amber past 3 h).
- Three tiles: Total · Human (token colour, "% · n trades through routers") · ARB bot (electric cyan `79,209,255` — never a token
  colour, so a bar reads at a glance; "% · n trades from n bot contracts").
- The split bar, then the stacked chart (bots at the foot, humans on top; 24H = hours, 7D = six-hour bins, 30D = days; hover
  titles), then the value-generated line (fee × each side; BOTH sums each token at its own fee).
- By pool (volume, humans, bots with counts, bot share mini-bar; phone: pool · volume · bot share), Top bot contracts (PulseScan
  links, trades, volume, share of bot volume), two folds: Human routes (which routers, how much) and How we tell.
- BOTH: sums of the two tokens' periods (the pTGC/UFO pool appears under both, as DexScreener counts it).
- Honesty: loading skeleton / failed card with Retry (gotcha 3, a18); the totals are on-chain over the pools we track and the note
  says they will not match DexScreener to the dollar.

## Harness (cloud clone; `design/volume-split/sample-swap-volume.json` = a 2-day backfill from the Mac VM, pinned pools only —
DexScreener is unreachable there, so pool names fall back to addresses; the pipeline's file has DexScreener's names)
`#/ptgc` → dot → window (1440): 7D PTGC $20,688 / 88 % human / 12 % bots, chart, pools, 8 bot contracts; `#/ufo` → BOTH; phone 390
no sideways scroll. Renders: `renders/vs-ptgc-1440.png`, `vs-ufo-both.png`, `vs-ufo-phone.png`.

## Owed / next
- His art for the header; the Volume tile's icon entrance + go-live word; a 📷 share card if he wants one.
- The UFO dashboard's **TXNS 24H** tile reads 10,761 / 46 while the chain shows ~100 UFO swaps a day — it counts something other
  than trades; fix alongside or the two surfaces contradict each other.
- A verified aggregator the heuristic misses shows up in "Top bot contracts" with a PulseScan name — add it to `ROUTERS`.
