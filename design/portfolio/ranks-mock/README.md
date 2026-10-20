# Holder rank — mock-up tools (2026-10-20)

Prototype scripts behind `design/portfolio/mock-ranks-v1/v2/v3.html`. Not part of the site.

- `holders.py <token> <out.json>` — pages PulseScan's `/api/v2/tokens/<token>/holders` (50 per page, sorted by balance) into
  `[[address, raw value, is_contract, name], …]`. Measured 2026-10-20: UFO 5,324 rows in ~95 s, PTGC 18,195 rows in ~7 min.
  This is the reading half of the planned pipeline step (`scripts/build-holder-ranks.mjs`, see handover).
- `mock_ranks.py` → v1 (options A / B / C), `mock_ranks2.py` → v2 (C as layouts D / E / F), `mock_ranks3.py` → v3 (C with the
  rank in its own column: G1 two-line badges, G2 one-line badges — HIS PICK OF LAYOUT). They import each other in that order.
- `excl_ufo.json` — `PF_UFO_EXCL` from `tools/pf-v2/PfLeagues.jsx` (the UFO OA wallet + 13 pools).
- Paths: the scripts point `S` at the session scratch dir that held `ptgc-holders.json` / `ufo-holders.json` and a clone of the repo;
  change `S` (and the output path at the bottom of each) to re-run. Ranking rule used: drop burn (0x0, 0x…369, 0x…dead), the
  token contract, EVERY contract (production: only pools — check `token0()`), the UFO OA wallet; keep balances ≥ 1 token;
  rank = 1 + number of listed balances strictly above the wallet's balance (binary search).
- Render: `node render.js <html> <png> 1380` with playwright-core from `tools/harness/node_modules` and
  `--headless=new` (the cloud Chromium refuses old headless).
