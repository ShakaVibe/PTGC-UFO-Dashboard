# Leagues (holder tiers) modal — redesign, 2026-10-04

Shaka's mock-up + assets: `reference/shaka-leagues-mockup.jpg`, `reference/shaka-leagues-assets.jpg` (one PNG: the
panorama on top, the two icons on a flattened checkerboard underneath). Cut from it: `lg-sky.jpg` (2172×384, the
panorama), `lg-ic-coins.png` (Starting supply), `lg-ic-circ.png` (Circulating supply) — both cut off the baked-in
checkerboard (saturation / darkness mask, closing, feathered), 320 px, provisional until he sends the icons on real alpha.

The target is `TierInfoModal` in index.html (the ⓘ on the Burn panel's creature row / Holder tiers) — the same numbers:
`BURN_C` × `tierFraction` on the chosen basis (starting / circulating), price × threshold.

## Mock v1 — `mock-tiers-v1.html` → `renders/tiers-v1.jpg`
His mock-up, with his asks: the dashboard's burn flame (`logos/panels/vg-flame.webp`) on the BURNED tile, our sea-creature
art on the rows, and NO percentage lines under the tier names or the token figures. Token column = the tier's range on the
site's model (Poseidon ≥ 10 %, Whale 1 % – 10 %, …, Shell under Shrimp's floor) — his mock's token column was one tier off its
own price column; the price column was right. Three columns rendered: PTGC gold; UFO green with the sky hue-rotated (the
Live Feed / Holders Details treatment — goes purple where the sky is blue); UFO green on the sky as painted. The chevrons
are drawn as in his mock (decorative — the rows do nothing); the two ⓘ are the existing explainers' places.

## Mock v2 — `mock-tiers-v2.html` → `renders/tiers-v2.jpg` (his three notes on v1)
His second sky (`reference/shaka-leagues-sky-v2.jpg` → `lg-sky-v2.jpg`) on BOTH tokens, no green shift for UFO (green UI only);
the logo is the dashboard's lit coin (`h2-coin`: halo + `logos/header/coin-corona*.webp` + flares + the logo, at u = 112/195);
the Tokens column is ONE figure per tier (the amount needed, as the modal prints today); then his mid-round ask: the chosen
supply tile GLOWS (`.t.sel`) and the other dims (`.t.dim`), the caption follows. PTGC rendered on Starting, UFO on Circulating.

## Combined card (Socials → PTGC & UFO Leagues) — `mock-combined-v1.html` (rejected: "use the ones we just built as
inspiration") → `mock-combined-v2.html` → `renders/combined-v2.jpg`: the MODAL's build with both tokens — the sky header with
the toggle on top, THE GRAYS LEAGUES in the gold→green gradient, the two lit coins with name + price, the modal's caption and
numbered rows (blue frames, Poseidon lit) with PTGC tokens / price and UFO tokens / price, the Socials footer. Tall 1080×1350
and Wide 1200×675; the frame = the combined cards' gold→green hairline. The toggle in the image mirrors the toolbar's.
v2 → Shaka: "The top part looks better, but the bottom sucks" — **v3** (`mock-combined-v3.html` → `renders/combined-v3.jpg`):
the creatures in the CENTRE of each row (small rank, art, name), PTGC tokens + price to the LEFT, UFO tokens + price to the
RIGHT; the Starting / Circulating toggle in SILVER metal (the old combined card's #f5f5f5 → #9a9a9a reading); **Tall only** —
"we dont need a horizontal version".
**v4** (`mock-combined-v4.html` → `renders/combined-v4.jpg`): his sea art — the whale and the shark (`reference/shaka-leagues-sea.jpg`
→ `lg-sea.jpg`, 2056×765) — as the top ("use this background for the top.. make it look good"): header 560 px, the art from
its top edge so both faces sit clear under the title, the coins dropped below their chins (top 330, a soft dark pool behind
each coin + name + price so they read over the bodies and the ruins), the bottom third sinking into the body. The same art,
faint, under the footer.
**v5** (`mock-combined-v5.html` → `renders/combined-v5.jpg`): his PORTRAIT sea art (`reference/shaka-leagues-sea-tall.jpg` →
`lg-sea-tall.jpg`, 1079×1457) as the WHOLE plate — the creatures at the top under the title, the coins below their chins,
the ruins and the glowing coral showing through a dark veil under the rows (the rows are translucent blue glass now).
**v6** (`mock-combined-v6.html` → `renders/combined-v6.jpg`): Shaka — "the whale has two tails… move the whale and the shark UP
so the UFO logo is not on the face of the shark". The lower-left fin (the second "tail") is painted out of the art
(`lg-sea-tall.jpg`: the ruins-and-water strip above it cloned down over a feathered mask, a soft
shadow over the corner — Telea inpainting smeared); the art sits at 108 % and 128 px higher, the coins 14 px lower, the header
626 px, rows 60 px.
**v7** (`mock-combined-v7.html` → `renders/combined-v7.jpg`): "use this whale and shark instead.. but use the rest of the
background" — the WIDE art's creatures (`reference/shaka-leagues-sea-wide.jpg`, one tail) composited over the portrait's ruins
and coral: the wide image at 85 % (1747×650) centred over the portrait's top, solid to y 560 then feathered out by y 650
(`lg-sea-tall.jpg`, 1079×1457). The art at 100 %, top 0 on the card.
**v8** (`mock-combined-v8.html` → `renders/combined-v8.jpg`): his cut-outs — `reference/shaka-whale.png`, `shaka-shark.png`
(real alpha) and the plain sea `shaka-sea-bg.png` (ruins + coral, no creatures). Assets: `lg-sea-bg.jpg` (flattened),
`lg-whale.webp` (1000 px, trimmed), `lg-shark.webp` (900 px, trimmed, MIRRORED so the two face each other). Layered on the
card (not baked): whale 620 px at (−40, 112), shark 440 px at (right −10, 96 — "move the shark up higher"), drop shadows; header 560, coins at 318 —
"make the whale and shark a little smaller so you can move them up… so the logos can also move up".
Then: "the rock formations on both sides… give them the shading of the token side they are on… also increase the token logos a
bit" — two gradient tint layers per side over the plate (`.tint.l` / `.tint.r` in `mix-blend-mode:color`, `.l2` / `.r2` in
`soft-light`, 26 % wide, strongest at the edge, gone by the creatures; the whale / shark sit ABOVE the tints, untinted); the
coins 0.66 → 0.8 u (156 px), header 584, coins at 306.
Then: "make sure the image does not go out past the border" — the creatures live in a `.clipin` box (inset 16, the frame's
radius) and are placed fully inside it (whale 590 px at 10 / 92, shark 430 px at right 12 / 78); "take the numbers away next
to the sea creatures" — the rank gone, creature + name left-aligned in the centre column.
