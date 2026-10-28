# tools/

What is safe to run here, and what is history. Checked 2026-10-28 (Audit VI item 5) by running every `*.py` on a clean copy of
the repo and diffing: **no script changes a page any more.** 34 report "0 edit(s)" or "already applied", 43 refuse with an error,
none modify. Re-check the same way before trusting a script you have not run recently.

## Run these after editing their source (they are the sync, and idempotent)

| Script | Source of truth (edit this) | Writes into |
| --- | --- | --- |
| `pf-v2.py` | `tools/pf-v2/*.jsx`, `tools/pf-v2/pf2.css`; the Leagues `lg-*` CSS is copied from `index.html` | `portfolio.html` |
| `top100.py` | `tools/top100/t1.jsx`, `tools/top100/t1.css` | `index.html` (`T100:CSS` / `T100:JSX` blocks) |
| `league-history.py` | `tools/league-history/lh.jsx`, `lh.css` | `index.html` (`LH:CSS` / `LH:JSX` blocks) |

Run each twice; the second run must print `0 edit(s)`. Then `cd tools/harness && node compile.js`.

`tools/affiliate/af.css` matches the page's `AFFIL2:CSS` block again (it was 95 lines behind until 2026-10-28), but its sync
script `affiliate-v2.py` stops on a one-time edit whose anchor no longer exists. Until that script is reduced to its two
`splice()` steps (as `top100.py` was), edit the affiliate CSS in `index.html` and copy the block back into `af.css`.

## Everything else is history

Each of the other scripts applied one change on the date in its docstring. Keep them for the reasoning they record (Shaka's
quotes, before/after numbers); do not run them. They fall into three kinds:

- **Already applied, detects itself** — prints `0 edit(s)` / `already applied` and changes nothing (e.g. `hvb-count-off.py`,
  `lh-no-hilo.py`, `socials-hub.py`, `pf-cleanup.py`).
- **Anchor gone** — the text it looked for was edited later, so it stops with `AssertionError: anchor x0` before writing
  (e.g. `audit3-*.py`, `calc-v2.py`, `charts-v2.py`, `kpi-v2.py`, `*-pipeline.py`). `kpi-v2.jsx` / `kpi-v2.css` are the inputs of
  the finished `kpi-v2.py`, not a source: the page has moved on (e46, c23, Audit V v4).
- **Refuses on purpose** — first line is `sys.exit(…)` because re-running would undo a later decision or leave a broken page:
  `hvb-count-switch.py` (would restore the Humans vs Bots COUNT selector), `lh-cards-live.py` (would restore High/Low and the
  IN THE CHART tag), `audit4-batch6.py`, `audit4-batch7.py` (partial writes, then fail).

Data and measurement scripts (`audit5-measure-fees.py`, `ufo-reward-excluded.py`, `ufo-v1-earned.py`) read the chain; they change
no page and take minutes.

`harness/` is the test harness (its own README). New page code should go in a source file plus a sync step like the three above,
or (roadmap item 28) be loaded directly with `<script type="text/babel" src=…>` so nothing needs splicing at all.
