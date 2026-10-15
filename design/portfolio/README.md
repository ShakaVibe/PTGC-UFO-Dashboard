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

## Round 5 (2026-10-13): Value History built (option C), lifetime icon + gold box, donut seam
Shaka: "Here is a logo for the total lifetime rewards. Make it small as I do not want to increase the height of that box. Also
let's try give that box a light gold shading. And go ahead and add in the portfolio value history now." + "fix the pie chart …
where the yellow meets the purple".
- **Value History** (`tools/pf-v2/PfHistory.jsx`): every counted wallet's PTGC + UFO `balanceOf` at past blocks (archive eth_call,
  batched 80 per request, two at a time; rpc.pulsechain.com + g4mm4 only — publicnode has no archive state, tested), × the
  price then (data/charts-data.json daily, charts-intraday.json hourly, raw GitHub). Points: 7D every 6 h, 30D / 90D daily,
  1Y every 4 days, + the live "now"; aligned to UTC so they repeat and are cached per wallet + token + time in localStorage
  (`grays_pf_hist_v1`); a point with any wallet unread or no price = a gap. Block for a time = interpolation between anchor
  blocks (head, 7 / 30 / 90 / 180 / 365 / 420 d). Side card: current value, change over the period, period high / low. Hover /
  touch crosshair + tooltip (date, total, PTGC $ / UFO $). **ALL dropped** — prices exist for 365 days only (1Y is the longest
  honest range). Default 30D.
- Tiles: sparklines from the 30D series; the total's **24 h change is real** now (every counted wallet's balances exactly 24 h
  ago × the price then vs now), falling back to the price move until it lands.
- Lifetime earned: his rising-coins icon (checkerboard removed) at 34 px inside the box, box height unchanged (59 px), light
  gold gradient + gold hairline; the token count prints whole numbers so it stays on one line.
- Donut: a 2-unit dark gap between arcs and one glow on the group — the last arc no longer paints over the first.
Harness: `PF_HIST=1` makes past balances grow toward today with a sell ~10 days back. Render `renders/r5-history.jpg`.

## Token cards — three layouts without the duplicates (`mock-cards-v1.html` → `renders/cards-v1-1440.jpg`)
Shaka: "some of it is duplicated — we have the boxes that say Staked, and then a purple dot next to the graph that says
Staked … same with Liquid … maybe the boxes need to be total holdings, reflections and reflection yield, and under that the pie
chart with the other detail lines that make up the chart". His real numbers. The donut / bar legend now carries tokens, $ and %
for each part (PTGC also a "Total staked" sub-line), so no figure appears twice. New figure: PTGC reflection yield =
reflections ÷ (holdings − reflections), the same rule as UFO's (13.55 % on his bag).
- **A** — three tiles (Total · Reflections · Reflection yield), then the donut + the full legend.
- **B** — a wide Total tile + Reflections + Yield, then a stacked bar instead of the donut, legend under it.
- **C** — the total INSIDE a bigger donut, the legend beside it, Reflections + Yield as two tiles below.
(The mock shows the cards un-aligned; the build keeps the shared row grid.)

## Round 6 (2026-10-13): option A built + a reflection yield that selling cannot inflate
Shaka: "I like A, let's do it. But make sure your math is right — what if they earned a lot of reflections early on, and they
sold most of that PTGC — that would make the yield look super high because it's against the current total" + "don't do the
total staked number at the bottom".
- Tiles (both tokens): Total holdings · Reflections · Reflection yield. PTGC donut legend: Liquid / Staked (not locked) /
  Locked & staked with tokens · $ · % (no Total-staked line). UFO legend: Principal / From reflections, tokens · $ · %.
- **The maths.** Reflections are LIFETIME (balance + sent − received). Old yield = R ÷ (balance − R) → infinite / huge after a
  sell. New: **yield = R ÷ everything ever received** (PTGC: the token's own totalReceived counter, now kept on the wallet data
  as `received`; UFO: the received sum the reflections scan already computes, stashed in `window.pfUfoRecv`). Bought 100,
  earned 10, sold 100 → 10 % (old: ∞). UFO split of today's bag = pro rata R ÷ (received + R) of the current holdings (never
  negative, never more than earned). Moves between your own wallets count as received at both ends → the yield reads a little
  LOW, never high. How it works explains it. Render `renders/r6-cards-A.jpg`.

## Rewards — three layouts (`mock-rewards-v1.html` → `renders/rewards-v1-1440.jpg`)
Shaka, before pushing round 6 (screenshot of the classic page's LIFETIME EARNED: Staking · Locking · Reflections boxes + the
total bar): "wait … rethink all this … before we even showed lifetime earned for each one". Plus his question: rename
"Reflections" to "Rewards"? (PTGC's reflections figure is reflections only — staking / lock claims arrive as transfers;
staking + locking + reflections = lifetime earned.) His real figures (staking 4.79B, locking 363.21M, reflections 4.44B,
total 9.59B / $372,596.53, claimable 34.78M); the reward yield is shown as xx.x % — computed at build.
- **A** — tiles Total · Lifetime earned · Reward yield; one "Earned by source" box (three source boxes with tokens, $, share)
  with Ready to claim (chest) as its last line; the old total bar and "Earned:" line go.
- **B** — the classic Lifetime Earned panel back under the tiles (three boxes + gold total bar with the coins icon); tiles Total ·
  Reward yield · Ready to claim. UFO repeats its one number (box + bar).
- **C** — tiles as A; one Rewards row at the foot: an "Earned by source" split bar + rows, and the chest with Ready to claim.
Reward yield (all three) = everything earned ÷ the tokens the wallets brought in (received minus the reward claims that arrived as
transfers — to be checked on chain at build, so it is neither double-counted nor inflated by selling).

## Round 7 (2026-10-13): rewards option A built
Shaka: "let's go A then … and when I see it live I can make adjustments". Tiles Total holdings · **Lifetime earned** (PTGC staking +
locking + reflections; UFO reflections) · **Reward yield**. The lifetime bar, the "Earned:" line and the separate claimable box are
replaced by ONE gold **Earned by source** box (rising-coins icon): Staking / Locking / Reflections boxes (tokens, $, share of
earned) and a **Ready to claim** line with the chest (total + staking / locks split). UFO: one "Reflections — the only UFO reward"
box. Lock positions drop-down unchanged.
**Checked on chain** (block 27789531, wallet 0x559b…bf7c, a lock claim): the claim is a Transfer from the staking contract;
PTGC totalReceived rose by 539.104 and lockClaimed by 539.104 — claims sit in "received", not in reflections. So reward yield =
(claimed + lockClaimed + reflections) ÷ (received − claimed − lockClaimed). Render `renders/r7-rewards-A.jpg`.

## Round 8 (2026-10-13)
Shaka's eight: (1) Ready to claim = his new chest (`reference/shaka-claim-icon-v2.png`, checkerboard removed → `logos/portfolio/
pf-claim2.webp`, new name so no cache); (2) "— the only UFO reward" removed; (3) "on brought in" → "on what you put in" + an ⓘ
that opens a plain-English note with his own numbers ("You put in X and have earned Y from … → Z %. Selling doesn't change it");
How it works reworded; (4) UFO "Share of supply" badge removed; (5) PTGC Total holdings gets the gold frame; (6) **buy / sell
markers** on the Value History — from the balances the chart already reads (no extra data): where a token count moved > 1 % between
two points, green (more tokens) / red (fewer); the tooltip names the move ("▼ −34.59B PTGC since the point before"); legend under
the chart. Net per step (a buy and a sell inside one step cancel); exact per-transaction dots need the transfer list (comes with
Recent Transactions). (7) Answered: the chart already prices REAL past balances at the price of that day — not today's tokens at
today's price. (8) UFO reflections source box in PTGC's gold. Render `renders/r8-history-markers.jpg`.

## Round 9 (2026-10-13)
Shaka: "remove the Reward yield, I don't think it's accurate, then the two other boxes can get larger including the font sizes;
add the coins logo to total holdings, and use the attached image for lifetime earned; make the UFO reflections box the same height
as PTGC's; add in the recent transactions".
- Tiles: two big ones (icon left, 31 px figure, 18 px $): Total holdings with his gold coin stack (`logos/leagues/lg-ic-coins.webp`),
  Lifetime earned with `logos/portfolio/pf-lifetime.webp` — **a copy of the rising-coins icon as a placeholder: his "attached image"
  did not come through** (only the screenshot did). Swap the file when it arrives (new name or a ?v bump — gotcha 38).
  Reward yield tile + How-it-works line removed (PfYield and the maths stay in the code, unused).
- UFO reflections source box gets "100% of earned" → same 120 px height as PTGC's boxes.
- **Recent Transactions** built (`tools/pf-v2/PfTx.jsx`): PulseScan `/api/v2/addresses/{w}/token-transfers?type=ERC-20&token=…`
  per counted wallet × PTGC/UFO (CORS open, tested live; latest 50 each), 3 in flight, cached 5 min in localStorage
  `grays_pf_tx_v1`; legs of one tx netted per wallet (a UFO sell's fee leg folds in). Types: Claim (paid by the staking contract —
  staked PTGC never leaves the wallet), Stake, Buy / Sell (the tx called a swap / multicall / execute / zap), Move (between two of
  his wallets, shown once as "A → B"), Receive / Send. Value = amount × that hour's / day's price, today's price when newer than the
  price files. 10 rows, Show more (40), Refresh, a "x of y reads failed — retry" line. Phone: two-line rows. Harness `PF_TX=1`.

## Round 9b: his Lifetime earned icon (infinity + coins) arrived → checkerboard removed → `logos/portfolio/pf-lifetime2.webp` (new name, no cache), shown 78 px wide (crops the square padding). The placeholder pf-lifetime.webp stays unused. Render `renders/r10-tiles.jpg`.

## Round 10 (2026-10-13): Moon Math moves into the tile row
"Shrink the three of these boxes a hair so we can move the moon math box to the end there instead of at the bottom." Row =
three value tiles (icons 52 px, figure 25 px, sparkline 66 px) + a 150 px Moon Math tile (moon, gradient title, ON/OFF, "try your
own prices ▾"); clicking it opens the price inputs as a full-width strip right under the row. Per-Wallet Breakdown is now the only
fold (full width). ≤ 1100 px: Moon Math drops to a slim full-width bar under the three; ≤ 980 px everything stacks. Also live-
checked round 9's Recent Transactions on ptgc-ufo.com with a real staking wallet: Claim / Buy rows, values and tx links correct.
Render `renders/r10-moonmath.jpg`.

## Round 11 (2026-10-13)
1. Lifetime earned icon → his rising-bars-in-a-gold-ring (`reference/shaka-lifetime-icon-v2.png` → `logos/portfolio/pf-lifetime3.webp`).
2. Moon Math: **Live / 🚀 All-time highs** is a lit toggle (the active one glows); a third "Your prices" chip appears when he types.
3. **PLS maths fixed.** On the old page (and v2 until now) a Moon Math PLS price changed nothing — no figure used it. Now PLS = X
   means PTGC and UFO keep their price IN PLS, so each $ price moves by X ÷ today's PLS (PLS ×2 → PTGC and UFO ×2; probe
   `pf2-moon.js` ratio 2.0000). A PTGC / UFO price typed in still wins for that token; a line under the strip says what PLS did
   ("PLS at … is 4.00× today's price → PTGC …, UFO …"). The classic page is left as it was.
4. "Earned by source" heading without the icon. 5. UFO legend's "split of today's bag, pro rata" line removed.
6. Moon Math strip redesigned: ONE row — token logo + PRICE + a short 150 px box for PTGC, UFO, PLS (PLS logo = DexScreener's
   WPLS image), then the toggle at the right; phones stack. Render `renders/r11-moonmath.jpg`.

## Round 12 (2026-10-13): Moon Math all inside its tile
"Remove the PLS … add Live, Custom, All-time highs … make the border of the long box the same purple as the Moon Math tile …
even better, eliminate that extra bar and get it all into the moon math tile — maybe Custom opens a little window."
The strip under the row is gone (and PLS with it). The tile (`PfMoonTile`, 168 px, bright purple border always) holds the title and
a three-way toggle **Live · Custom ✎ · 🚀 All-time highs** (the active one lit). Custom opens a small window anchored under the tile,
same purple border: "Your own prices — type the price you want to imagine for PTGC and / or UFO. Every dollar figure on the page —
totals, cards, wallets — switches to it. Leave one empty to keep its live price.", PTGC and UFO boxes (logo, name, live price under
each), Clear / Done; closes on Done, Esc or a click outside; "edit your prices" link stays in the tile. The banner above the tiles
names the mode ("… uses your custom prices" / "… the all-time-high prices") with a Back to live button. Probe `pf2-moon.js`
(PTGC ×2 → value ×2.000, every toggle state). Render `renders/r12-moontile.jpg`.

## Round 13 (2026-10-13)
1. The purple Moon Math banner shows for Custom too (any mode but Live Prices); with Custom and nothing typed yet it says so
   ("type a PTGC and / or UFO price … live prices until you do"); its button reads "Back to Live Prices".
2–3. Toggle labels: **Live Prices · Custom ✎ · 🚀 All-Time Highs**.
4. Lifetime earned icon → his clock + coins (`logos/portfolio/pf-lifetime4.webp`; real alpha, trimmed).
5. Moon Math tile + banner use his gold crescent (`logos/portfolio/pf-moon.webp`).
6. **Transaction types fixed.** Checked live on PulseScan: every PTGC transfer (sell, buy, plain send) splits off fee legs to the
   token contract, the STAKING contract and the burn address — so the old "a leg went to staking = Stake" rule turned every
   PTGC sell into "Stake" (his 0xAC0E…0bd0 rows). Routers also often show a bare selector (0xe25d4a18), so the method name can't
   decide a swap. New rule (PfTx.jsx `pftClassify`): fee legs (token contract, staking contract, 0x0 / 0x…369 / 0x…dEaD) are
   ignored when finding the counterparty but still count in the amount; the biggest remaining leg is the counterparty. From the
   staking contract → Claim; one of your wallets → Move; add/removeLiquidity → Add LP / Remove LP; a contract (pair, router,
   aggregator) → Buy / Sell; a person → Receive / Send. Verified on a real wallet's 8 PTGC txs (multicall sells split over two
   pairs → Sell, selector-only buys from up to 9 pairs → Buy). Cache key → `grays_pf_tx_v2` (rows now carry is_contract).
   Harness PF_TX stub gained a fee-split sell.

## Round 14 (2026-10-13)
1. **Chart dots come from the real trades** (Shaka: "a bunch of sells… yet no red dots"). The round-8 dots compared token
   counts between chart points and hid anything under 1 % of the bag — every normal-sized sell (his ~$350 sells of 8.9M PTGC
   on a multi-billion bag). Now Recent Transactions hands its rows to the chart (`onRows` → `txs`): every Sell / Send / Add LP
   is a red dot and every Buy / Receive / Remove LP a green one, on the first chart point at or after the trade; a step with
   both gets both dots side by side; the tooltip lists the trades (type, amount, token, $). Claims and moves between your own
   wallets get no dot. Older than PulseScan's latest-50-per-wallet window (or if a read failed), the old balance-change dots
   still fill in, and the legend says so.
2. **Lessons from his `pulsechain_monitor.py`** (the trade monitor built earlier) folded into `pftClassify`:
   claims labelled by function (withdrawReward → staking, withdrawRewardLock → lock); **Unstake** (withdraw(uint256) on the staking contract — principal never moves, so the
   principal is decoded from the call and shown); the hidden 1 % reflection slice of a send added back (PTGC = the staking
   leg, UFO = contract fee ÷ 5) so Sell / Send amounts are the real gross; helper-made LP adds that look like sells are caught
   by an LP-token mint to the wallet in the same tx (per-tx detail fetched only for the rows on screen, cached in
   `grays_pf_txd_v1`). Harness: PF_TX stub gained an unstake and a zapper LP add, plus `/transactions/{hash}`
   stubs; PF_TX_SHIFT=h ages the stub; probe `pf2-txdots.js`.

### Round 14b
- DAO rules dropped (Shaka: the DAO has nothing to do with a personal wallet) — no DAO claim / DAO lock types.
- The hidden 1 % was questioned, so it was re-checked on chain: PTGC sell tx 0x91968a23… (block 27,789,557) logged
  14,850 PTGC out (95 % + 2.5 % + 1 % + 0.5 % of 15,000) while the wallet's balanceOf fell 15,000.0 — the missing 1 % is the
  holders' share of his 5 % fee, which reflection tokens pay without a Transfer event. Three UFO sells: balance fell by the
  emitted legs + exactly (5 % fee leg ÷ 5) = the holders' 1 % of his 6 % fee. The gross-up stays.

## Round 15 (2026-10-13)
1. **More chart dots** (Shaka): claims are a BLUE dot, liquidity adds / removes a YELLOW one (the table's colours); buys /
   receives green, sells / sends red. Several kinds in one step sit side by side; the tooltip lists each transaction.
2. **UFO rewards now include the OLD UFO contract.** The new-contract scan counted the Jul 9 migration airdrop as tokens
   received — but that airdrop was each wallet's old balance at the Jul 6 snapshot, old reflections included, so they showed
   as principal. `tools/ufo-v1-earned.py` (method + every on-chain check in its header) built `data/ufo-v1-earned/{0-f}.json`
   once: 7,457 wallets, 50.08B UFO earned there. The UFO card's Earned by source shows **New UFO contract** + **Old UFO
   contract**; Lifetime earned, the principal / reflections ring and the per-wallet table include it. If the file can't be
   read, the old box says "unavailable" and the totals are the new contract alone. Harness: PF_V1=1 / PF_V1=down; probe
   `pf2-v1.js`.

## Round 17 (2026-10-14) — Recent Transactions as an activity feed
Mock-up `mock-tx-v1.html` (render `renders/tx-v1-1340.jpg`): A refined table · B activity feed · C day boxes. Shaka picked **B**,
plus a copy button next to the wallet. Built in PfTx.jsx: one plain-words line per transaction ("Sold 8.91M PTGC"), a round
type icon with the token logo on its corner, wallet + copy button + time underneath (Claim says "from staking / lock", Unstake
"released from staking"), dollar value on the right with received / paid / earned / value, PulseScan link button. Grouped by
day (Today / Yesterday / weekday / date). Filter chips with counts — All · Buys · Sells · Claims (+ Unstake) · LP · Transfers
(Move, Receive, Send); empty ones hide. "Show 30 more" instead of the 10 / 40 toggle. Same layout on a phone. Probe `pf2-feed.js`.

## Round 18 (2026-10-14)
1. Bigger type: Earned by source (labels / amounts / $), Ready to claim, the whole Value History (axes, legend, tooltip, the
   side panel) and the transaction feed.
2. **Chart dots fixed for real.** Only the newest 50 transfers per wallet + token were read, which on a busy wallet reach back
   hours — and the coverage cut-off was the most active wallet's, applied to every wallet. Now each wallet + token pages back up
   to a year (or 20 pages): page 1 for everyone first, the older pages in the background, refreshes only read the newest pages
   and merge (cache `grays_pf_tx_v3`). Coverage is per wallet + token. The round-8 "token count moved > 1 %" fallback dots are
   gone — dots come only from real transactions; if a wallet's history is cut short inside the period, the legend says "dots
   complete from <date>". Harness PF_TX_PAGES=1 serves a second page.
3. Mock-up `mock-r18-v1.html` (render `renders/r18-v1-1340.jpg`) for his two layout questions: the empty space under UFO's
   Earned by source (A one tall box · B a "paid automatically · nothing to claim" strip mirroring PTGC's Ready to claim — my
   pick) and the Per-Wallet Breakdown (A rich table · B wallet cards).

## Round 19 (2026-10-14) — his "go with your suggestions" on mock-r18-v1
1. UFO gap → **B**: under UFO's Reflections box, a strip mirroring PTGC's Ready to claim — UFO logo, "Paid to your wallet
   automatically · nothing to claim", "You get ≈ X% of every holder reward" (counted UFO ÷ 999,999,999,051 supply) and
   "1% of every UFO buy, sell & transfer".
2. Per-Wallet Breakdown → **A** (rich table) on desktop / tablet, **B's cards** on a phone (≤ 700 px): copy button on every
   address, PTGC + Pending to claim (PTGC yellow) + UFO (one total, no reflections column), $ under every amount, Total with each
   wallet's share and a PTGC/UFO split bar, an All-wallets row. Total = PTGC + UFO held (pending not included, same as the
   page's Total portfolio value).

## Round 20 (2026-10-14) — Earned by source · 30-day Details (mock-earned-details-v1, approved "awesome, let's build it")
"Details · 30D" pill in both Earned by source headers → a window (PfEarnedModal, PfHistory.jsx) with PTGC / UFO tabs:
30-day total + per-source tiles (UFO: total / daily average / best day), stacked daily columns (staking / locking /
reflections; UFO green) with hover + legend toggles + an average line, a by-day table newest first with the best day marked
(cards on a phone). Maths — running totals per wallet at each UTC midnight (archive eth_call, batched 80, cached for good in
`grays_pf_ed_v1`; the head read fresh): staking = claimed + pendingToClaimed + pendingReward; locking = lockClaimed +
Σ pendingRewardLock; PTGC reflections = balance + totalSend − totalReceived; UFO = Δbalance − that day's net transfers
(Recent Transactions now also hands up per-tx `flows`, both sides of a move), split at the boundary blocks' real timestamps.
Verified on chain on a real staker (all three only rise; a 4.2M-PTGC staking day showed up as one). Gaps, never guesses.
Prices: that day's from the price files, today's live. Harness PF_ED=1 + probes pf2-ed.js / pf2-ed-ufo.js.
- Round 20b hotfix: the window's class `.pf2-ed` clashed with the wallet card's ✎ edit button (also `.pf2-ed`, round 2) — the
  pencil picked up the window's box styling and, while the mouse was over the window, the pencil's `:hover` background made
  the window see-through. Window renamed `.pf2-erw`. Found live-checking round 20 on ptgc-ufo.com.

## Round 21 (2026-10-14) — Details window: BOTH tab (default) + scrolling day list
- Tabs **Both · PTGC · UFO**, Both the default (whichever card's button opened it). Both is in **dollars** (the two tokens can't
  share a token scale): tiles Earned 30 days / PTGC $ (+ tokens) / UFO $ (+ tokens) / Best day; stacked daily $ columns —
  PTGC staking, PTGC locking, PTGC reflections, UFO reflections (legend chips toggle); by-day rows with PTGC and UFO tokens + $
  and the day's total value. PTGC and UFO days complete independently (UFO needs its transfers in reach).
- No "show all": every day is in the list, which scrolls inside its own box (sticky header, a wide gold / green / gold-green
  scroll bar on the right); on a phone the day cards scroll the same way.
- Round 21b (his ask, mid-round): the average per day moved out of the plot to a chip right of "DAILY" ("- - Avg 8.59M PTGC / day";
  in Both, dollars); the line in the chart stays, now dashed to match the chip's key.

## Round 22 (2026-10-14) — Details window: loader, tiles, scroll bar
1. Big loader ("Crunching your last 30 days…": spinning gold/green rings round the logos, two steps — daily totals from the
   chain (with %) and, for Both / UFO, the UFO transfers from PulseScan (pages read) — and a progress bar) until EVERYTHING the
   tab needs is in. His screenshot showed Both at $0 with every day "Waiting for your transactions…": Both needs the UFO
   transfers back 30 days, which arrive in the background paging after the window opened. Recent Transactions now reports
   `busy` / `pages` and pages UFO first; the window waits until each wallet's UFO history reaches 30 days back (or paging ends).
2. Tiles dressed up: tinted by source, bigger type (values 31 px, total 36 px, $ 17.5 px), a 🏆 on Best day.
3. Scroll bar always shown: Chrome ignores ::-webkit-scrollbar styling (and macOS then hides the bar until you scroll) when
   `scrollbar-color` is set, so the standard properties are now Firefox-only (@supports); overflow-y:scroll; a fade at the
   bottom of the list hints there's more.

## Round 23 (2026-10-14) — Phase A of the roadmap (handover/PORTFOLIO-ROADMAP.md)
A1 **Activity strip** (Shaka picked B of `mock-dots-v1.html`, render `renders/dots-v1-1340.jpg`): no dots on the line any more;
   under the chart one stacked bar per chart point (buys / sells / claims / liquidity), taller with more, a count on 4+, dust
   under $1 left out; hover lights the bar and lists the transactions. Harness PF_TX_BUSY=1 (a 3-trades-a-day wallet), probe
   `pf2-strip.js`.
A2 Clear all → "No wallets are counted. Switch one on…" (was "Reading your wallets…" forever).
A3 A failed price-file load is no longer cached for 30 min; old rows / days never fall back to today's price unless the price
   series exists and the row is newer than it.
A4 Coverage: a wallet+token is "complete" only when PulseScan ran out of pages; capped / aged lists are complete back to their
   oldest item (fixes UFO day maths + the strip's "complete from" note for busy wallets).
A5 Transactions cache: debounced saves; on quota the least-recently-read entries are evicted one at a time (was: wipe all);
   old `grays_pf_tx_v1` / `v2` keys removed.
A6 The feed hands `busy:false` to the Details window when its run is cut short (wallet set changed / unmounted).
A7 Loader: "N pages read".  A8 Remove asks first (card ✕ → Remove? Yes/No, auto-dismiss 5 s; Edit window → Yes, remove / Keep);
   ✕ hit area 26 px.  A9 Empty feed with failed reads says so + Retry.  A10 ADD WALLET with "+ New group" not created → message.
A11 Old-UFO-contract file failure shows "old contract not included · retry" (Lifetime earned + Reflections box); shard fetch 20 s timeout.
A12 **Unstake**: PulseScan doesn't decode the staking contract's withdraw — real unstakes are method null + selector 0x2e1a7d4d
   (checked on two live txs) → the selector is matched too. (deposit 0xb6b55f25 mints a receipt token, nothing in our feed.)
A13 Buy / Sell only when ANOTHER token moved in the same tx (checked lazily with the per-tx detail we already fetch); a plain
   transfer to a contract (Safe, bridge, vesting) is Send / Receive. Detail cache → `grays_pf_txd_v2`.
Also: a stray backspace character in the LP-name regex (`/\bLP\b/` had been written through a non-raw string) fixed.

## Round 24 (2026-10-14) — Phase B (performance), B8 held (it would go live)
B1 One `build()` per landed history page; the parent is told at most ~2× a second (always at the end); `PfHistChart` memoised,
   its points stable between renders. B2 In-flight dedupe for the price files and the block anchors (were fetched up to 5× / 3×
   at first paint); 24 h balances remembered per wallet per 10-min slot (a toggle no longer re-reads every wallet); Refresh forces
   a page-1 re-read ONCE (nonce>0 used to force it on every later toggle). B3 Transactions cache is one localStorage key per
   wallet+token (`grays_pf_tx_v4:<addr|TOK>`) — a page writes only its own entry; v3 blob removed. B4 Details: UFO flows bucketed
   per wallet and sorted once, two-pointer per day. B5 1Y points on 4-day boundaries (repeat day to day); history cache pruned
   on load (> 400 days; 6-h points > 15 days). B6 PulseScan 429 → one 2.5 s retry. B7 Deep paging waits for the Recent
   Transactions section to come within 600 px of the screen (or 5 s). Strip legend / tooltip say per 6 hours / day / 4 days.

## Round 25 (2026-10-14) — Phase C (polish), "do it all"
C1 Dust: feed rows under $1 hidden behind a "Show dust (N)" chip (moves / claims / unstakes never count as dust). C2 Local
time everywhere: chart points on local midnights (local 6-h slots on 7D; 1Y keeps 4-day boundaries), Details days are local
midnights, footnote says so. C3 Feed names resolved at render (a rename shows at once). C4 The old chart (and the sparklines)
stay while a toggle / period change reloads, with an "updating… N%" tag. C5 Chart tooltip centred on phones, never clipped.
C6 Side panel high / low in full dollars (stacked). C7 Moon Math banner: "your holdings, rewards and totals are valued at…
(The value history and the transactions stay at real prices.)". C8 "· N unreadable" after the counted total. C9 Unstakes have
their own chip. C10 No UFO → Details opens on PTGC, Both / UFO greyed. C11 Creature row uses the League's 8 tiers (Shrimp,
Shell). C12 Contrast lifted (footer, source line, chip counts, strip note). C13 One address style (0x1234…abcd); an unnamed
wallet in the breakdown shows its group instead of the address twice. C14 Moon Math: a custom price counts only once it's a
number above 0 (typing "0." no longer zeroes the page); decimal text inputs. C15 Details: wallet picker (All wallets · each).
C16 Details: 7D / 30D / 90D (remembered). C17 Breakdown: sort by Value / Name / Added; group subtotal rows where a group has
2+ wallets. Fixed on the way: a cleanup-scope bug from round 24 (tellT) that threw on every wallet toggle.

## Round 26 (2026-10-14) — Phase D (accessibility)
D1 PfModal traps Tab inside the window; How it works now goes through PfModal (Esc, focus, scroll lock). D2 Focus goes back to the
button that opened a window; an autoFocus'd field (Edit → Name) is left alone. D3 Charts are keyboard-readable: Tab to the value
chart or the daily bars, ← → Home End step the points, a hidden live region announces the tooltip text. D4 Every tap target
≥ 24 px (switch 40×26 with the track drawn inside, ✎ 26 px, copy buttons 26 px, card ✕ 26 px, Retry 24 px). D5 Wallet status
dot has an aria-label. D6 Search field gets a visible focus ring; one gold focus ring for every button / switch / chart.
D7 Moon Math, Details tabs and the supply toggle are aria-pressed buttons (no fake tab / radio semantics). D8 No meaningful text
under 12 px (harness sweep: 0 small texts, 0 small targets at 390 px). D9 iOS: windows lock the page behind (position:fixed);
clipboard ✓ only on a successful copy, with an execCommand fallback.

## Round 27 (2026-10-14) — Phase E (code health), hidden as before
E1 Dead code out: PfYield (+ its CSS), the yield maths (ptYield / ufoYield / fmtY / ptgcEarned / ptRecv / ptIn), the PLS
multiplier maths, the retired rounds' CSS (table feed, old Moon Math strip, `.pf2-src3.two`, `.pf2-tbl`, `.pf2-le`, …) — an
audit script found every class never referenced from the JSX (comments excluded); pf2.css −10 % (the "a third" estimate in the
roadmap was high). E2 One PF_ADDR / PF_SUPPLY block in PfLeagues.jsx; PFH_TOK, PFT_STAKING, PFE_ST, PF_TOKEN_ADDR, PF_BURN_ADDR
and the UFO supply literal all read from it. E3 One quota strategy: `pfLsSet(key,obj,shrink)` — the history cache drops its
oldest 10 % of points, the Details cache its oldest days, the tx cache its least-recently-read wallets (never a wipe).
E4 A header in each file listing what it expects from the others and the concatenation order. E6 `pftCovered(txs,addr,tok,t)`
is the one reading of the coverage map (strip, Details days, Details loader). E7 Comments fixed (swapped / duplicated / stale
ones, the PfTx header). E8 Named: PFH_BLOCK_MS, PFH_RPC_TIMEOUT, PFH_BATCH. Left for later: E5 (window.pfUfoRecv → needs a
classic-code change), E8's remaining literals, E9 (precompiling the JSX is a site-wide decision), the pool() helper.
Also: Moon Math tile buttons 24 px tall (last sub-24 px target on desktop).

## Round 28 — mock-ups (2026-10-14, after Phase E; v2 still hidden)

Shaka (screenshots of the strip and the 24-wallet deck): "can you make it where you can mouse over or click on the little
daily bars and it pops a window showing the day's moves? 2) I feel like each of these [wallet cards] are way too big…
what can we do to drastically make these smaller."

mock-daybar-v1.html (renders/daybar-v1-1340.jpg): each strip bar becomes a button with a 19 px hit area. Hover / tap →
a tooltip above the bar (day, value, day move, first 5 trades, "click for all N"). Click / Enter → a DAY WINDOW in the
Details frame: day + move, four tiles (buys / sells / claims / liquidity with counts and $), tokens in / out, every
transaction of the day in Recent-Transactions rows (scrolling), ◀ ▶ previous / next day with trades, Esc, a "show this
day in Recent Transactions" link.

mock-wallets-v2.html (renders/wallets-v2-1340.jpg): A mini tiles 7 across (~330 px for 24 wallets, everything kept,
✕ on hover) · B two-column 32 px list sorted by value (~400 px) · C chips: switch · name · value with the split as a
line under the pill (~170 px; percentages / dot only in the edit window). Waiting for his pick.

Shaka: "A". Built (round 28, pf-r28.tgz, still hidden):
- Strip bars are buttons (19 px hit area): hover / tap lights the bar and shows the chart tooltip (5 trades, "N transactions
  on Oct 4", "+9 more — click the bar for the full list"); click, or Enter on the focused chart, opens PfDayModal (PfHistory.jsx)
  — title + portfolio move, four tiles, tokens in / out, every trade in PfTxRow rows (now shared with Recent Transactions,
  PfTx.jsx), ◀ ▶ previous / next bar with trades, Esc, "Go to Recent Transactions". Labels come from the bucket (previous
  point, this point]: the daily points sit at local midnight, so the bar at Oct 5 00:00 is labelled Oct 4 (the old tooltip
  said "Oct 5 … this day" — one day off). 7D bars: "Oct 4 12 PM – 6 PM"; 1Y: "Oct 1 – Oct 4"; the live point: "Today".
- Deck: 7 across (5 under 1100 px, 2 on the phone), 24 wallets ≈ 330 px; group line dropped from the tile (it is in the ✎
  window and the name's title); ✕ on hover (always faint on touch); Show-all cuts at 28 / 20 / 6; a Value · Name · Added sort
  in the toolbar (saved in grays_pf_deck_sort, default Value); 24 px switch / ✎ targets, 12 px smallest text.
Harness: `tools/harness/README.md` r28 line; renders `renders/r28-1440-*.jpg`. Classic hash still 215506704.

## Round 29 — separation between the wallets and the data (2026-10-15)

Shaka (screenshot): "I dont like how all the wallets go right into the total port value etc boxes.. we need some more
seperation there?" → mock-sep-v1.html (renders/sep-v1-1380.jpg): A a YOUR HOLDINGS section heading with a fading rule ·
B a glowing gold-to-green divider with the two coins · C the wallets (toolbar + deck + Moon Math banner) in their own bordered
panel, then the heading from A. He said A, then "actually C please". Built: `.pf2-wpan` (a `.pf2-pn` with a gold-tinted
border, 12/14 px padding; the toolbar inside loses 2 px of gap and the search box 24 px so HOW IT WORKS stays on the line),
`.pf2-hsec` heading "YOUR HOLDINGS · N wallets counted" 34 px below it, the tiles row `.hd` with no top margin. Tile name gap
3 px / mono letter-spacing −.04em so the short address still fits 7-across inside the panel. Phone: panel 10 px, heading 26 px.
Still hidden. Classic hash 215506704.

## Round 30 — the trades loader + the ledger (2026-10-15)

Shaka: "1) while the transactions are loading… put a cool loading graphic over the chart… 2) The per wallet break down needs
a major cosmetic upgrade… Text is too small." Mock-up mock-r30-v1.html (renders/r30-v1-1380.jpg): loader L-A (a UFO saucer
scanning the strip) / L-B (radar veil); breakdown B-A (the ledger, bigger + dressed) / B-B (wallet row-cards). He: "I dont
like the loading one at all. Can we use the one you created that shows up when you hit the details 30 days button" + B-A.
Built: `.pf2-txload` — the Details loader (`.pf2-edload.ov`, two-coin orb, rings, steps PTGC · UFO "n / N wallets", bar)
over the chart column while the first PulseScan read runs (PfRecentTx → `onProgress`, PortfolioV2 `txP` → PfValueHistory
`txp`; shown while `!txs`, i.e. until every wallet's first page is in — the side stats stay visible; compact on the phone).
Ledger: 17 px base, names / amounts 19 px, dollars 15 px, 12 px rows with a soft zebra, wallet colour as a 3 px left accent
(dot hidden in the table), logos in the column headers, 120 px share bar, ALL WALLETS a gold band (26 px total, its own
share bar), group subtotal bands kept; the fold header gold 15 px. Sprite `logos/portfolio/pf-saucer.webp` cut from the UFO
badge (unused now, kept for later). Harness `SLOW_SCAN=ms` delays only the PulseScan reads. Still hidden; classic 215506704.

## Round 31 — the UFO share audited, Ready to claim mock-up, chart padding (2026-10-15)

Shaka: "audit this number [You get ≈ 23.22% of every holder reward]… tokens that have been burned are not getting rewards…
a percentage of circulating supply not starting supply." Audit (tools/ufo-reward-excluded.py, on chain 2026-10-15):
the holder reward is split by balance among holders NOT excluded from rewards. Excluded (balance never moves by
reflections): the burn address 0x…369 (95.76 B), the token contract, the EOA 0x92DD…574D (71.76 B — "UFO OA" in his deck,
excluded by the owner) and 13 PulseX pools (6.0 → 19.7 B each). Four untouched holders' reflections ÷ balance × the window's
total reflected fee all imply 735.87 B eligible; supply − the excluded balances = 734.1 B. So the old figure (÷ the 1,000 B
supply) understated everyone's share by ~26 % (his 23.22 % is really ≈ 31.6 %). Built: `PF_UFO_EXCL` + `pfUfoEligible()` /
`usePfUfoEligible()` in PfLeagues.jsx (one batched RPC read of supply + 16 balances, 10-min memory cache, localStorage
fallback `grays_pf_ufo_elig`), share = balance ÷ eligible, and a third line under the strip: "Your 232B of the 734B UFO that
earns rewards · the 95.8B burned, 170B in liquidity pools and 71.8B in excluded wallets earn nothing". If the RPC is down and
nothing is cached it falls back to the supply and says so.
3) `.pf2-sec.pf2-vh{margin-top:34px}` — more air between the token cards and the chart.
2) Ready to claim: mock-claim-v1.html (renders/claim-v1-1380.jpg): A gold vault banner in place (+ CLAIM ↗ button if there is
a dapp URL) · B a fourth green tile in the Earned row · C a spotlight under the holdings tiles. Waiting for his pick.

## Round 32 — Ready to claim spotlight (2026-10-15)

Shaka: "I like C, but I want to put that ready to claim box under the Earned by source boxes." Built `.pf2-spot` in the
old strip's place: green-gold panel, pulsing READY TO CLAIM, the amount 38 px + PTGC, "$… waiting in the staking contract",
a Staking / Locks bar with the legend; "Nothing to claim yet — rewards build up while you stake" when staked but 0 pending;
phone 28 px. The UFO strip (`.pf2-rtc.u`) is unchanged. Render renders/r32-1440-spot.jpg. Still hidden; classic 215506704.

## Round 33 — claim wording, the UFO spotlight, the history loader (2026-10-15)

Shaka: 1) "waiting in the staking contract" → "waiting to be claimed". 2) "The UFO side needs to match the look of the ptgc
side" → `.pf2-spot.u`: the same spotlight (green border, 84 px logo), PAID TO YOUR WALLET AUTOMATICALLY, the share at 34 px
"of every holder reward", one line of plain words, a bar of your slice of the reward-eligible supply, legend "Your X of the
734B UFO that earns rewards" / "Not earning: burned · pools · excluded". The old `.pf2-rtc.u` strip is gone. 3) "you still
get the old little updating badge" → the Details loader for the history too: `.pf2-hload` in-flow on the first look
("Reading your 30D history… Chain reads N %"), `.pf2-txload` over the stale chart on a period / wallet change; `.pf2-upd`
and the old `.pf2-hwait` bar removed. The trades loader waits for the history (only one overlay at a time).
4) He asked for more suggestions — see the chat / sessions/2026-10-15.md. Still hidden; classic 215506704.

## Round 34 — six small ones he picked from the review (2026-10-15)

1 Day headers in Recent Transactions carry the day's net ("−$1,468 net", in/out on hover; dust / filter respected).
2 Lock positions header: "9 · 3 unlockable · next unlock in 13 h" (`pfIn`). 3 The two token cards align always: the
Earned-by-source block is a flex column so the shorter spotlight stretches to the other's bottom, the folds sit at the row's
end (`align-self:end`), and the UFO card got its sixth row — a "🛸 Not earning rewards" fold opposite Lock positions listing
the burn address, the contract, the excluded wallet and the 13 pools with balances and % of supply (from the round-31
`pfUfoEligible()` list, PulseScan links; two-column rows on the phone). 4 "read 2 min ago" stamps on the Value History title
and the feed header (`usePfTick` 30 s, `pfAgo`; `s.at` / `st.at`). 5 The coverage note left the legend for the chart
tooltip ("trades before Oct 9 still loading / not available" only when hovering before the coverage). 6 The Total tile shows
the period change under the 24 h one ("▲ +392.31% (30D)", `onChg` from PfValueHistory). Still hidden; classic 215506704.

## Round 35 — the feed as a ledger, rolled up (2026-10-15)

Shaka (screenshot): "so much dead space between the text on the left and the dollar value on the right. Rethink how this
lays out… clean, easy to read, and sexy." mock-feed-v2.html (renders/feed-v2-1380.jpg): A ledger columns · B two-up cards ·
C slim timeline with dotted leaders. He: "lets go with mock up A", plus "have recent transactions roll up into a bar that you
click to expand, like the per wallet breakdown", and "take the bullet point away that says not earning" (UFO spotlight).
Built: `PfTxRow` is a ledger row (icon · action + note · wallet + copy · price per token (value ÷ amount, Buy / Sell only,
`fmtPriceNode`) · time · value · link), `PfTxColh` headers, zebra via `z`, no card borders, day headers with the net; the
section is a `.pf2-fold` with `.pf2-foldh` ("RECENT TRANSACTIONS · 997 transactions · all wallets · read 2 min ago"), closed
by default, opened by the day window's "Go to Recent Transactions" (window event `pf2-open-feed`); reads still run while
closed (the chart's strip needs them). Phone: card rows again (price / time columns hidden, time inline); the day window
hides the price column. UFO spotlight legend is one line now. Still hidden; classic 215506704.

## Round 36 — spotlight alignment, fold bars (2026-10-15)

Shaka (screenshots): 1) the UFO Reflections tile was shorter while "scanning…" → it keeps its three lines (scanning… / — /
"reading the UFO transfers…"). 2) the spotlights touched the tiles → the stretch rule lost its `margin-top:auto`, 12 px again.
3) the two spotlights line up graphically: the same 84 px icon column, the same 38 px amount line (UFO's small 20 px), one-line
`.u` for both ("1% of every UFO buy, sell and transfer — nothing to claim"), one-line legends; the harness measures both at the
same top and height. 4) the two fold bars "blend in too much" → gold border, hover glow, a "Show ▾ / Hide ▴" pill on the
right (`.pf2-foldh .chev` draws it), and 18 px between the chart and Recent Transactions. Still hidden; classic 215506704.
