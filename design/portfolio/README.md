# Portfolio page — redesign below the header (2026-10-13)

Shaka: "the portfolio page.. The top [banner] is already good, but the rest needs help. Here is a mock up that I want you to
start with. We need to mock up before you actually build. I want to see it."

His mock-up: `reference/shaka-portfolio-mockup.png`. Today's page for comparison: `renders/today-1440.jpg` (harness, two
stub wallets). Today's page also overflows sideways on a phone (the summary bar runs to ~1245 px wide at 390).

## Mock v1 — `mock-portfolio-v1.html` → `renders/pf-v1-1440.jpg`, `renders/pf-v1-390.jpg`
The header strip is a cut of the real v2 header + tab band (`mock-header.jpg`, `mock-header-m.jpg`), so the page reads in
context. Everything under it is the mock. Figures are his mock-up's sample numbers.

Built to his layout, top to bottom:
1. **YOUR PORTFOLIO** panel: title + line, HOW IT WORKS (gold hairline), the add row (address · label · group · lime
   ADD WALLET), MY WALLETS (n) + Select All, search + All Groups, wallet chips five across (checkbox, status dot — green
   loaded / amber loading / red failed — name or short address in mono, ×). Phone: chips two across, the first six then
   "Show all n wallets".
2. **Three summary tiles**: Total (his gold wallet, drawn in SVG), PTGC value (gold frame), UFO value (green frame), each
   with a sparkline.
3. **The two token cards**: coin, gradient name, subtitle, price + 24 h change; four tiles (PTGC: Total / Liquid / Staked /
   Reflections; UFO: Total / Principal / Reflections / Reflection yield); the donut + legend; the Total Lifetime Earned bar.
4. **Portfolio Value History**: 7D / 30D / 90D / 1Y / ALL, green area chart, side card (current value, 24 h change,
   all-time high / low).
5. **Recent Transactions (all wallets)**: Time / Wallet / Type / Token / Amount / Value / Tx, View All. Phone: two-line rows.

Added by Claude (not in his mock-up, kept from today's page — his call):
- a small **Leagues** pill (creature + "Leagues") beside each token's subtitle → today's Leagues window;
- PTGC: **Claimable rewards** + **Lock positions** as one quiet line under the lifetime bar; UFO: **Share of supply**.

Changed from his mock-up:
- the transaction type "Reflection" is **Claim** — reflections arrive with no transfer, so there is never a reflection row.

## Open for Shaka
- **Value history has no data today.** Options: (A) today's holdings × past prices (instant, every period, but it is "what
  your current bags were worth", not your real history); (B) a snapshot saved in the browser on every visit (true, but the
  chart starts on the day of the first visit, per device); (C) real balance history read from the chain per wallet (true
  from day one, slow with 20 wallets). The 24 h change and the tile sparklines use the same choice.
- **Recent transactions** are new: PulseScan's transfer list per wallet (one call each, cached). Types: Receive / Send /
  Swap / Stake / Unstake / Claim.
- **PLS** — his subtitle said "PTGC, UFO and PLS"; the page reads no PLS balances today (prices only). Add them, or drop
  PLS from the line (the mock drops it).
- **Moon Math** and **Per-Wallet Breakdown** are not in his mock-up — drop them, or keep them as folds under Transactions?
- Lock positions table / pending-rewards breakdown: the quiet line only, or a fold that opens the table?

## Mock v2 — `mock-portfolio-v2.html` → `renders/pf-v2-1440.jpg`, `renders/pf-v2-390.jpg`
Shaka on v1: "make all those changes, we definitely need the leagues back on there, and make sure we use the new emojis that
we have been using lately. Also use this for the total portfolio icon." Then: "mock it up with your changes first. I want to
approve the mock up before we do the work."
- **Total tile icon** = his black-and-gold wallet (`reference/shaka-wallet-icon.png`, real alpha → trimmed, squared, 320 px
  → `logos/portfolio/pf-wallet.webp`).
- **A Leagues block in each token card** (between the donut and the lifetime bar), all in the sea art (`logos/panels/sea-*.webp`,
  the `SeaIcon` set, no emoji): LEAGUE + the current tier's creature and name, the creature ladder of the bag (PTGC sample:
  shark ×4, dolphin ×8, squid ×9; UFO: whale ×2, shark ×4, squid ×5 — today's `getHoldingCreatures` maths), "View tiers ›" →
  the Leagues window; a lit bar (gold / green, glowing tip) from the current creature to the next (grey-ish until reached),
  "43.2 % to Whale · need 1.70B ≈ $66,062" (today's `LeagueProgress` maths). The header pill names the real tier.
- v1's additions kept: Claimable rewards / Lock positions line, Share of supply, Claim instead of Reflection, the phone's
  six chips + "Show all".
- **Per-Wallet Breakdown and Moon Math kept** as two folds at the foot (not answered — nothing lost; strike if unwanted).
- PLS left out of the subtitle (not answered).
- Value history: still his drawing — the data source is the open question (A / B / C above).

## Mock v3 — `mock-portfolio-v3.html` → `renders/pf-v3-1440.jpg`, `renders/pf-v3-390.jpg`
Shaka on v2: "I like C too" (value history = real balances read from the chain) and "let's add all the sea creatures that
make up the wallet instead of it saying like 'Shark · Leagues' … lay it out how you think is best."
- The header pill is gone; **the bag as sea creatures** sits under the token name (PTGC: shark ×4 · dolphin ×8 · squid ×9;
  UFO: whale ×2 · shark ×4 · squid ×5), each a framed chip with the sea art 30 px + count, wraps if a bag has five tiers.
  Phone: the row runs the full card width under the logo / name / price.
- The Leagues block keeps the league name + creature, View tiers, and the lit bar to the next tier; its own ladder is
  dropped (it is the header row now — one ladder per card).
- Value history: a line under the title says what it is ("Your real balances, read from the chain day by day — sells
  show as drops, buys as rises"). **Decision: option C.**

## The wallets area — three options (`mock-wallets-v1.html` → `renders/wallets-v1-1440.jpg`)
Shaka on v3: "that all looks good now, but I don't like the look of this area [YOUR PORTFOLIO: add form + wallet chips].
What can you do?" All three: the page title becomes **Grays Portfolio** in the Grays Calculators / Grays Charts metallic
style; a "17 counted · $186,458.82" summary beside MY WALLETS; Select all + Clear; HOW IT WORKS moves onto the toolbar.
- **A — a deck of wallet cards** (5 across): on/off toggle, name, address · group, the wallet's value, a PTGC/UFO split bar
  with the two %; unticked cards dimmed + dashed; group filter as a segmented control. The add form is ONE lit capsule
  (his wallet icon · address · LABEL · GROUP · ADD WALLET).
- **B — grouped glass pills**: the same capsule; each group is a row (name, count, value) with its wallets as round pills —
  a split-coin avatar (gold PTGC / green UFO share), name, status dot, value; the pill's ring is gold or green by which
  token its value leans to; "+ add to <group>".
- **C — a wallet table**: the classic form row; one row per wallet (tick, name, address + copy, group, PTGC, UFO, value,
  split bar, edit / remove), sortable, first 12 then "Show all"; would replace the Per-Wallet Breakdown fold.

## Mock v4 — `mock-portfolio-v4.html` → `renders/pf-v4-1440.jpg`, `renders/pf-v4-390.jpg`
Shaka: "okay, mock up the new version using A." v3 with the YOUR PORTFOLIO panel replaced by option A of
`mock-wallets-v1.html`: the **Grays Portfolio** metallic title, the one lit add capsule (his wallet icon), the toolbar
(MY WALLETS (n) · counted + value · Select all · Clear · group filter · search · HOW IT WORKS), the deck of wallet cards five
across. Phone: the capsule stacks (address / label + group / ADD WALLET), cards two across, the first six + "Show all".

## Built — step 1, hidden (2026-10-13): `tools/pf-v2.py` → portfolio.html
Shaka: "Lets BUILD BUT… I do not want to make it live yet … hide it behind a small faint dot in the bottom right." v4 as
built from the page's own data, behind `PF_V2_LIVE=false` + the faint dot (localStorage `grays_pf_v2_preview`). Value
History + Recent Transactions are "Coming next" panels (step 2). Renders: `renders/build1-v2-1440.jpg`, `build1-v2-390.jpg`,
`build1-v2-rpcdown.jpg` (harness stub data — every wallet reads the same canned balance). Detail: `handover/sessions/2026-10-13.md`.

## Round 2 on the built page (2026-10-13, his first live look)
"1) the ptgc and ufo boxes do not align good enough, 2) there does not need to be boxes around each sea creature,
3) the view tiers should say leagues, and the leagues sheet should look like the leagues sheet we use … on the dashboards"
+ "we need to be able to edit a saved wallet so we can change the name".
1. The two token cards share one set of row tracks (CSS subgrid): header · tiles · donut · league · lifetime · extras line up
   and both cards end level (`probes/pf2-align.js`); the creature row spans the card under the name (one line for six tiers).
2. The creatures are bare sea art 34 px + "×n" — no chip boxes.
3. "Leagues" button → `PfTierInfoModal`, a port of index.html's TierInfoModal (sea header with whale + shark, lit coin,
   Starting / Burned / Circulating tiles, eight rows, Close); its lg-* CSS is copied from index.html by the build script on
   every run. Burned read live (balance of 0x…369 + totalSupply). Numbers via `pfAbbr` (= index fmtAbbr, never "1000.00M").
4. Edit: a pencil beside every wallet's name (always visible) → the Edit window — address + Copy, Name, Group (+ new
   group), Save / Cancel / Remove wallet; Esc closes (`probes/pf2-edit.js`). The card's corner × stays.
Renders: `renders/r2-cards.jpg`, `r2-leagues.jpg`, `r2-edit.jpg`.

## Round 3 (2026-10-13): rewards + locks open on the page
Shaka (with a screenshot of the classic page): "we lost the Claimable Rewards Breakdown … that needs to be there … also
missing the locked and staked … and then the details for locks". They were behind the two dashed chips — he never found them.
- PTGC tiles are five: Total · Liquid · Staked · **Locked & staked** (pink) · Reflections (phones: Total full width, then 2×2).
- A full-width **PTGC REWARDS & LOCKS** panel under the two cards (only when the counted wallets stake / lock / have rewards):
  Claimable rewards (staking, lock, total — tokens + $), Staking (not locked, locked & staked, total), and **every lock**:
  amount + $ + which wallet, time left + unlock date + a progress bar from lock start to unlock, pending reward; soonest first,
  unlockable ones green; six shown then "Show all n locks"; goptgc.com verify link in the header.
- Lock times under a day read in hours ("13h"), not "0d". Harness: `PF_STAKE=1` stubs a staked + locked position with three
  locks. Render `renders/r3-rewards-locks.jpg`.

## Round 4 (2026-10-13): rewards + locks inside the PTGC card
Shaka: "I don't like how the ptgc stuff is under the UFO side too … just under the PTGC side. The claimable should be above,
and then the lock positions should be in a drop down. Let's add this icon to the claimable part … and we don't need to
repeat this [the Staking split]" + "increase the font size of the dollar figures a bit".
- The full-width panel is gone. In the PTGC card, under the "Earned" line: **Claimable rewards** with his gold chest
  (`reference/shaka-claim-icon.png` had a baked-in checkerboard → removed by flood fill from the edges + alpha unmixing
  against the local checker grey, specks dropped, squared 320 px → `logos/portfolio/pf-claim.webp`), staking / lock / total;
  then **Lock positions** as a drop-down (closed by default; "24 · 8 unlockable"), the same lock rows inside + goptgc link.
- The Staking split block is dropped (the tiles + donut already show it).
- Dollar figures bigger: tile $ 13.5 → 15.5 px (five-tile row 12.5 → 14.5), claimable $ 14 → 15.5, lock $ 13 → 14.
- Fix on the way: the token-name gradient rule (`.pf2-tk.p .t`) leaked onto the lock rows' `.t` cells → scoped to `.pf2-tkh`.
- The UFO card keeps the shared row grid, so it carries empty space at the foot level with PTGC's claimable box.
Render `renders/r4-ptgc-claim.jpg`.
