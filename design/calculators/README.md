# Calculators page — his art as the plate + a Hub-style title (2026-10-05)

Shaka: "let's use this on the calculator page. Let's also work on the text of the word calculator — make it more like the
titles we have done such as Socials Hub. Let's see a mock-up before building."

His art: `reference/shaka-calc-bg.png` (1024 × 1536, portrait — a frame of planets, rock and gold nebula around a black
centre; composed for content down the middle) → `logos/calculators/calc-bg.jpg` (same pixels, jpg 90).

## Mock v1 — `mock-calc-v1.html` → `renders/calc-v1a-1440.jpg` (title A), `calc-v1b-1440.jpg` (title B), `calc-v1-390.jpg`
The header strip in the mock is a cut of the real page's v2 header + tab band (`mock-header.jpg`, `mock-header-m.jpg`) so the
page reads in context; everything under it is the mock.

- **Plate**: his art `cover`, anchored top, **fixed to the viewport** on desktop (the frame of planets stays while the
  calculators scroll — the art's black centre is where the content sits, so the long page never runs off the bottom of a
  portrait image); a black-to-clear band under the tab bar (the Hub's rule — the art never runs up into the bar). Phones:
  the art over the top ~900 px, fading to black (no fixed attachment on iOS).
- **Title** in the Socials Hub's style (`.sh-t`: Orbitron 900 64 px, gold metallic gradient, drop shadow, the soft dark radial
  pool behind the block; 34 px on phones). Two options rendered: **A** "CALCULATORS" all gold; **B** "Grays" gold + "Calculators"
  silver (the Hub's two-tone split). The disclaimer lines take the Hub's sub / tag type (white, letter-spaced, text-shadowed)
  instead of the grey Tailwind lines.
- **Everything else as today** — the glass tabs, the COMING SOON strip, the panels and the two token cards — only their
  backgrounds darker (`rgba(8,8,10,.86)` + blur) so they read over the art.

Open for Shaka: A or B; whether the tabs / panels should get the gold frames of the newer surfaces (not in this round — he
asked for the art and the title).

## Mock v2 — `mock-calc-v2.html` → `renders/calc-v2-1440.jpg`, `calc-v2-390.jpg` (his three notes on v1)
"Dim down that background by 50 %" — a 50 % black veil over the art. "Instead of CALCULATORS at the top, use Grays Calculators"
— title B is the title (Grays gold, Calculators silver). "The disclaimer can be just normal font" — the two lines under the
title are today's plain type again (semibold white 72 % / white 58 %, 16 px), not the Hub's letter-spaced sub-line.

## Mock v3 — `mock-calc-v3.html` → `renders/calc-v3-1440.jpg`, `calc-v3-390.jpg`
His button mock-up (`reference/shaka-calc-buttons.png`) + his icon zip (`reference/calculator_button_icons.zip` → cleaned of
their stray alpha dust, squared, 320 px → `logos/calculators/ic-<calc>.webp`): a row of three gold buttons (X Multiplier, Moon
Math, Rewards) and a row of two blue (New Capital Simulator, 10 Yr Projection) — icon left, label, chevron right, a faint
scanline texture, the active one lit. His disclaimer screenshot (`reference/shaka-calc-disclaimer.png`): every calculator keeps
its own disclaimer block at the foot (all five have one today), framed like the panels, then Back to Dashboard. **"This needs to
stay on the bottom of all the calculator pages."**

## Built — `tools/calc-v2.py` (2026-10-05, Shaka: "make it live please … darken the background a little more first")
The veil is 62 % (50 % "was not enough"). `cp-*` CSS in calculators.html's `<style>`; the plate `.cp-art` (fixed; absolute over
the top 1000 px on phones) + `.cp-band` under the header; the title block; the buttons (`CALC_ICONS` by id, `CALC_BLUE` =
fresh + growth; a 6-column grid: 3 × span 2 then span 3 — a sixth live calculator takes a third row); the six disclaimer cards
(`cp-dc`, the LV analyser's too) framed; `bg-[#111]/80` panels a touch more solid; Back to Dashboard on a dark plate. The
script reproduces the file from the 10-03 calculators.html byte for byte. Renders: `renders/live-calc-1440.png`,
`live-calc-foot-1440.png`.
