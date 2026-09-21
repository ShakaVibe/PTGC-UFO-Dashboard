/* The harness serves this build in place of the Tailwind play CDN. The sibling pages load the
   same CDN and have been run through the harness since a12 / a36 (portfolio, ledger, charts,
   calculators), but only index.html was ever scanned — so a class that exists on one of those
   pages and nowhere in index.html had no CSS here and the screenshot lied about it (found
   2026-09-21 adding the Ledger's amber staleness banner, a60). All five pages are scanned now. */
const path = require('path');
const root = path.resolve(__dirname, '..', '..');
module.exports = {
  content: ['index.html', 'ledger.html', 'charts.html', 'calculators.html', 'portfolio.html']
    .map(f => path.join(root, f)),
  theme: { extend: {} }
};
