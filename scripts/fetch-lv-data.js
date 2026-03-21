/**
 * fetch-lv-data.js
 * ─────────────────────────────────────────────────────────────────────────────
 * Fetches live liquidity & volume data for PTGC and UFO from DexScreener,
 * appends a timestamped snapshot to data/lv-snapshots.json in the repo,
 * then commits the update via the GitHub API.
 *
 * Runs via GitHub Actions 4× daily (00:05, 06:05, 12:05, 18:05 UTC).
 *
 * Required environment variables (set as GitHub Actions secrets):
 *   GITHUB_TOKEN  – standard Actions token (automatically available)
 *   GITHUB_REPO   – e.g. "shakavibe/PTGC-UFO-Dashboard"
 *
 * Node 18+ (uses native fetch).
 * ─────────────────────────────────────────────────────────────────────────────
 */

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const GITHUB_REPO  = process.env.GITHUB_REPO || 'shakavibe/PTGC-UFO-Dashboard';
const DATA_PATH    = 'data/lv-snapshots.json';
const BRANCH       = 'main';

// ── Token config ──────────────────────────────────────────────────────────────
const TOKENS = {
  PTGC: { address: '0x94534EeEe131840b1c0F61847c572228bdfDDE93' },
  UFO:  { address: '0x456548A9B56eFBbD89Ca0309edd17a9E20b04018' }
};

// ── RH Core detection (mirrors the frontend logic) ────────────────────────────
const RH_CORE_ADDRESSES = new Set([
  '0xa1077a294dde1b09bb078844df40758a5d0f9a27', // WPLS
  '0x95b303987a60c71504d99aa1b13b4da07b0790ab', // PLSX
  '0x2fa878ab3f87cc1c9737fc071108f904c0b0c95d', // INC
  '0x2b591e99afe9f32eaa6214f7b7629768c40eeb39', // HEX
  '0x57fde0a71132198bbebc939b98976993d8d89d225'  // eHEX
]);
const RH_CORE_PAIRS = new Set([
  '0x975c7ab1dae5c97327ef7019587dffc66096f5d8', // PTGC/PRVX
  '0xbea0e55b82eb975280041f3b49c4d0bd937b72d5', // UFO/PRVC
]);
const RH_CORE_SYMBOLS = new Set(['PRVX', 'PRVC']);

function isPairCore(pair, tokenAddress) {
  const pairAddr = pair.pairAddress?.toLowerCase();
  if (pairAddr && RH_CORE_PAIRS.has(pairAddr)) return true;
  const baseAddr  = pair.baseToken?.address?.toLowerCase();
  const quoteAddr = pair.quoteToken?.address?.toLowerCase();
  const tokenAddr = tokenAddress.toLowerCase();
  const ptgcAddr  = TOKENS.PTGC.address.toLowerCase();
  const ufoAddr   = TOKENS.UFO.address.toLowerCase();
  const otherAddr = baseAddr === tokenAddr ? quoteAddr : baseAddr;
  const otherSym  = (baseAddr === tokenAddr ? pair.quoteToken?.symbol : pair.baseToken?.symbol)?.toUpperCase();
  if (otherSym && RH_CORE_SYMBOLS.has(otherSym)) return true;
  if ((otherAddr === ptgcAddr || otherAddr === ufoAddr) && otherAddr !== tokenAddr) return false;
  return RH_CORE_ADDRESSES.has(otherAddr);
}

// ── Fetch all pairs for a token from DexScreener ─────────────────────────────
async function fetchPairs(tokenAddress) {
  try {
    const [r1, r2] = await Promise.all([
      fetch(`https://api.dexscreener.com/latest/dex/tokens/${tokenAddress}`),
      fetch(`https://api.dexscreener.com/token-pairs/v1/pulsechain/${tokenAddress}`)
    ]);
    const d1 = await r1.json();
    let d2 = [];
    try { d2 = await r2.json(); } catch(e) {}
    const map = new Map();
    if (d1.pairs) d1.pairs.forEach(p => map.set(p.pairAddress?.toLowerCase(), p));
    if (Array.isArray(d2)) d2.forEach(p => { if (p.pairAddress && !map.has(p.pairAddress.toLowerCase())) map.set(p.pairAddress.toLowerCase(), p); });
    return Array.from(map.values());
  } catch(e) {
    console.error(`fetchPairs error for ${tokenAddress}:`, e.message);
    return [];
  }
}

function processPairs(pairs, tokenAddress) {
  let coreLiquidity = 0, totalLiquidity = 0, coreVolume = 0, totalVolume = 0, price = 0;
  pairs.forEach(p => {
    const liq = p.liquidity?.usd || 0;
    const vol = p.volume?.h24   || 0;
    const isCore = isPairCore(p, tokenAddress);
    totalLiquidity += liq;
    totalVolume    += vol;
    if (isCore) { coreLiquidity += liq; coreVolume += vol; }
    if (!price && parseFloat(p.priceUsd) > 0) price = parseFloat(p.priceUsd);
  });
  return { price, coreLiquidity, totalLiquidity, coreVolume, totalVolume };
}

// ── GitHub API helpers ────────────────────────────────────────────────────────
async function ghGet(path) {
  const res = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/contents/${path}?ref=${BRANCH}`, {
    headers: { Authorization: `token ${GITHUB_TOKEN}`, Accept: 'application/vnd.github.v3+json' }
  });
  if (!res.ok) throw new Error(`GitHub GET failed: ${res.status} ${await res.text()}`);
  return res.json();
}

async function ghPut(path, content, sha, message) {
  const res = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/contents/${path}`, {
    method: 'PUT',
    headers: { Authorization: `token ${GITHUB_TOKEN}`, Accept: 'application/vnd.github.v3+json', 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, content: Buffer.from(content).toString('base64'), sha, branch: BRANCH })
  });
  if (!res.ok) throw new Error(`GitHub PUT failed: ${res.status} ${await res.text()}`);
  return res.json();
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  console.log('🔍 Fetching LV data from DexScreener...');

  const [ptgcPairs, ufoPairs] = await Promise.all([
    fetchPairs(TOKENS.PTGC.address),
    fetchPairs(TOKENS.UFO.address)
  ]);

  const ptgcData = processPairs(ptgcPairs, TOKENS.PTGC.address);
  const ufoData  = processPairs(ufoPairs,  TOKENS.UFO.address);

  const snapshot = {
    timestamp: new Date().toISOString(),
    date: new Date().toISOString().split('T')[0],
    PTGC: ptgcData,
    UFO:  ufoData
  };

  console.log(`✅ PTGC: liq=$${ptgcData.totalLiquidity.toFixed(0)} vol=$${ptgcData.totalVolume.toFixed(0)}`);
  console.log(`✅ UFO:  liq=$${ufoData.totalLiquidity.toFixed(0)} vol=$${ufoData.totalVolume.toFixed(0)}`);

  // Load existing snapshots from GitHub
  console.log('📂 Reading existing snapshot file from GitHub...');
  let existingSnapshots = [];
  let fileSha = null;

  try {
    const fileInfo = await ghGet(DATA_PATH);
    fileSha = fileInfo.sha;
    const decoded = Buffer.from(fileInfo.content, 'base64').toString('utf8');
    const parsed = JSON.parse(decoded);
    existingSnapshots = Array.isArray(parsed) ? parsed : (parsed?.snapshots || []);
    console.log(`📊 Found ${existingSnapshots.length} existing snapshots`);
  } catch(e) {
    console.log('📝 No existing file or empty — starting fresh');
  }

  // Append new snapshot
  existingSnapshots.push(snapshot);

  // Keep last 365 days of snapshots (4 per day = 1460 max)
  if (existingSnapshots.length > 1460) {
    existingSnapshots = existingSnapshots.slice(-1460);
  }

  // Commit back to GitHub
  const newContent = JSON.stringify(existingSnapshots, null, 2);
  const commitMsg  = `📊 Update LV data - ${snapshot.timestamp.slice(0, 16)} UTC`;

  console.log(`💾 Committing ${existingSnapshots.length} snapshots to GitHub...`);
  await ghPut(DATA_PATH, newContent, fileSha, commitMsg);
  console.log('🎉 Done!');
}

main().catch(err => { console.error('❌ Fatal error:', err.message); process.exit(1); });
