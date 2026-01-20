// collect-holders.js
// Run this script to add a new snapshot to holder-history.json
// Usage: node collect-holders.js

const fs = require('fs');
const path = require('path');

const TOKENS = {
  PTGC: '0x94534EeEe131840b1c0F61847c572228bdfDDE93',
  UFO: '0x456548A9B56eFBbD89Ca0309edd17a9E20b04018'
};

const HISTORY_FILE = path.join(__dirname, 'data', 'holder-history.json');

async function fetchHolderCount(address) {
  const url = `https://api.scan.pulsechain.com/api/v2/tokens/${address}/counters`;
  const response = await fetch(url);
  const data = await response.json();
  return parseInt(data.token_holders_count) || 0;
}

async function main() {
  console.log('Fetching holder counts from PulseScan...');
  
  // Fetch current counts
  const ptgcHolders = await fetchHolderCount(TOKENS.PTGC);
  const ufoHolders = await fetchHolderCount(TOKENS.UFO);
  
  console.log(`PTGC: ${ptgcHolders} holders`);
  console.log(`UFO: ${ufoHolders} holders`);
  
  // Load existing history
  let history = { source: 'PulseScan', lastUpdated: '', snapshots: [] };
  try {
    if (fs.existsSync(HISTORY_FILE)) {
      history = JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf8'));
    }
  } catch (e) {
    console.log('Creating new history file...');
  }
  
  // Create new snapshot
  const now = new Date().toISOString();
  const newSnapshot = {
    timestamp: now,
    PTGC: ptgcHolders,
    UFO: ufoHolders
  };
  
  // Add to history
  history.snapshots.push(newSnapshot);
  history.lastUpdated = now;
  history.source = 'PulseScan';
  
  // Keep last 90 days of data (assuming ~1 snapshot per day = 90 snapshots)
  if (history.snapshots.length > 90) {
    history.snapshots = history.snapshots.slice(-90);
  }
  
  // Save
  fs.writeFileSync(HISTORY_FILE, JSON.stringify(history, null, 2));
  console.log(`Snapshot saved. Total snapshots: ${history.snapshots.length}`);
}

main().catch(console.error);
