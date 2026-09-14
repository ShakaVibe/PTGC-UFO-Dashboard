# Buy/Sell (switch.win widget) — security & liability notes, 2026-09-14

Not legal advice. What the code does and where the exposure is.

## How the wallet connection works
- `SwapModal` = an `<iframe>` of `https://switch.win/widget?…` (URL built only in `switchWidgetUrl`).
- The user's wallet connects to the IFRAME's origin (switch.win), not ptgc-ufo.com. Wallet
  popups / approvals / signatures name switch.win; the swap is switch.win's router on PulseX.
- `index.html` has no wallet code at all (0 refs to `window.ethereum`, WalletConnect, signing)
  and no `message` listener. Cross-origin isolation: our JS cannot read the frame, theirs
  cannot touch our page. The `partnerAddress` fee share is the only thing of ours in the loop.
- Custody never changes: user wallet ↔ PulseX router. We host a window onto a third party.

## Where a compromise WOULD hurt
Whoever can change `index.html` can change what the window shows — swap the URL for a
look-alike domain with a drainer widget (wallet popups would show the fake origin), or
repoint the fee-share address. Who can change it:
1. GitHub account(s) with push to `main` (data bots commit with GITHUB_TOKEN, cannot deploy;
   forks cannot push).
2. The domain registrar / DNS account — a takeover replaces the whole site.
3. Executed third-party code: React / ReactDOM / Babel / Chart.js are SRI-pinned (tampering
   = the page goes blank, not compromised). Tailwind play CDN (`cdn.tailwindcss.com/3.4.16`)
   is version-pinned but CANNOT carry an SRI hash → the one unverifiable script on every load.
   Google Fonts CSS and DexScreener images execute nothing.

## Do (in order)
1. 2FA (authenticator / hardware key) on GitHub AND the registrar; review collaborators;
   branch protection on `main`; Pages "Enforce HTTPS".
2. Vite build (roadmap b1/b2): removes Babel-standalone and the Tailwind CDN.
3. Then CSP (b7): `frame-src https://switch.win`, `connect-src` the RPC/DexScreener/raw
   GitHub hosts, hashed/self scripts. Before the build a CSP needs `unsafe-inline` +
   `unsafe-eval`, which defeats it.
4. Pin `actions/*` to commit SHAs (minor).

## Done today
- Swap footer now says trades run on switch.win (third-party, non-custodial) and that this
  site never sees the wallet — link to switch.win.
- Iframe `allow` trimmed to `clipboard-write` (no clipboard READ for the third party) and
  `referrerPolicy="strict-origin"` so the frame only learns our origin, not the page path.
