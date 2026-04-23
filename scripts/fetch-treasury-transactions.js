/**
 * Fetch DAO Treasury Transactions - MORALIS VERSION
 * 
 * Fetches all transactions (normal + token transfers) for DAO treasury wallets
 * and saves them to JSON files for the ledger to consume.
 * 
 * Files created:
 * - treasury-summary.json (totals, last updated, etc.)
 * - treasury-wallet1-txns.json (all txns for wallet 1)
 * - treasury-wallet2-txns.json (all txns for wallet 2)
 * - treasury-wallet1-tokens.json (all token transfers for wallet 1)
 * - treasury-wallet2-tokens.json (all token transfers for wallet 2)
 */

const fs = require('fs');
const path = require('path');

// Moralis API Key - set via environment variable
const MORALIS_API_KEY = process.env.MORALIS_API_KEY;
if (!MORALIS_API_KEY) {
  console.error('ERROR: MORALIS_API_KEY environment variable not set');
  process.exit(1);
}

// PulseChain chain identifier for Moralis
const CHAIN = '0x171'; // PulseChain mainnet (369 in hex)

// DAO Treasury Wallet Addresses
const WALLET1 = '0xeeac1da7f930078ab757ad8a64cf7c5e17b931e1';
const WALLET2 = '0x440773B5104a102c00EF26979a5c897155336A34';

// Known token addresses for labeling
const KNOWN_TOKENS = {
  '0xa1077a294dde1b09bb078844df40758a5d0f9a27': { symbol: 'WPLS', name: 'Wrapped PLS', decimals: 18 },
  '0x02dcdd04e3f455d838cd1249292c58f3b79e3c3c': { symbol: 'WETH', name: 'Wrapped ETH', decimals: 18 },
  '0x94534eeee131840b1c0f61847c572228bdfdde93': { symbol: 'PTGC', name: 'PTGC', decimals: 18 },
  '0x456548a9b56efbbd89ca0309edd17a9e20b04018': { symbol: 'UFO', name: 'UFO', decimals: 18 },
  '0x95b303987a60c71504d99aa1b13b4da07b0790ab': { symbol: 'PLSX', name: 'PulseX', decimals: 18 },
  '0x2fa878ab3f87cc1c9737fc071108f904c0b0c95d': { symbol: 'INC', name: 'Incentive', decimals: 18 },
  '0x2b591e99afe9f32eaa6214f7b7629768c40eeb39': { symbol: 'HEX', name: 'HEX', decimals: 8 },
  '0x57fde0a71132198bbec939b98976993d8d89d225': { symbol: 'EHEX', name: 'eHEX', decimals: 8 },
  '0x0d86eb9f43c57f6ff3bc9e23d8f9d82503f0e84b': { symbol: 'USDC', name: 'USD Coin', decimals: 6 },
  '0xefaeee334f0fd1712f9a8cc375f427d9cdd40d73': { symbol: 'USDT', name: 'Tether', decimals: 6 },
  '0x6b175474e89094c44da98b954eedeac495271d0f': { symbol: 'DAI', name: 'DAI', decimals: 18 },
};

// Known DEX routers
const KNOWN_ROUTERS = {
  '0x165c3410fc91b0e65d87e89d8bcadd85c9e6dbf1': 'PulseX V1 Router',
  '0x98bf93ebf5c380c0e6ae8e192a7e2ae08edacc3a': 'PulseX V2 Router',
  '0x636f6407b90661b73b1c0f7e24f4c79f624d0738': '9inch Router',
};

const MORALIS_BASE = 'https://deep-index.moralis.io/api/v2.2';
const PULSESCAN_BASE = 'https://api.scan.pulsechain.com/api';
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Make Moralis API request
 */
async function moralisRequest(endpoint, params = {}) {
  const url = new URL(`${MORALIS_BASE}${endpoint}`);
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null) url.searchParams.set(k, v);
  });
  
  try {
    const response = await fetch(url.toString(), {
      headers: {
        'X-API-Key': MORALIS_API_KEY,
        'Accept': 'application/json'
      }
    });
    
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`HTTP ${response.status}: ${text}`);
    }
    
    return await response.json();
  } catch (error) {
    console.log(`  API Error: ${error.message}`);
    return null;
  }
}

/**
 * Make PulseScan API request (no auth required — it's the public chain explorer)
 */
async function pulsescanRequest(params = {}) {
  const url = new URL(PULSESCAN_BASE);
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null) url.searchParams.set(k, v);
  });
  
  try {
    const response = await fetch(url.toString(), {
      headers: { 'Accept': 'application/json' }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.log(`  PulseScan Error: ${error.message}`);
    return null;
  }
}

/**
 * Load existing transactions from file
 */
function loadExistingData(filePath) {
  try {
    if (fs.existsSync(filePath)) {
      const stats = fs.statSync(filePath);
      console.log(`  Loading ${filePath} (${(stats.size / 1024 / 1024).toFixed(2)} MB)`);
      const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      return data;
    }
  } catch (e) {
    console.log(`  Could not load ${filePath}: ${e.message}`);
  }
  return null;
}

/**
 * Fetch all native transactions for a wallet using Moralis
 */
async function fetchWalletTransactions(walletAddress, walletName, existingTxns = []) {
  console.log(`\n${'='.repeat(50)}`);
  console.log(`Fetching ${walletName} transactions via Moralis...`);
  console.log(`Wallet: ${walletAddress}`);
  console.log(`${'='.repeat(50)}`);
  
  // Get the most recent block we have (for incremental updates)
  const lastBlock = existingTxns.length > 0 
    ? Math.max(...existingTxns.map(tx => Number(tx.block_number) || 0))
    : 0;
  
  if (lastBlock) {
    console.log(`Incremental mode: fetching after block ${lastBlock}`);
  } else {
    console.log('Full fetch mode: getting all historical transactions');
  }
  
  const newTxns = [];
  let cursor = null;
  let page = 0;
  
  while (true) {
    // Moralis endpoint for wallet transactions
    const params = {
      chain: CHAIN,
      cursor: cursor,
      limit: 100,
      include: 'internal_transactions'
    };
    
    // Only set from_block for incremental updates
    if (lastBlock > 0) {
      params.from_block = lastBlock + 1;
    }
    
    const data = await moralisRequest(`/${walletAddress}`, params);
    
    if (!data) {
      console.log(`  Page ${page + 1}: API error, retrying in 5s...`);
      await delay(5000);
      continue;
    }
    
    if (!data.result || data.result.length === 0) {
      console.log(`  No more data after page ${page + 1}`);
      break;
    }
    
    for (const tx of data.result) {
      // Convert Moralis format to PulseScan-compatible format
      const formattedTx = {
        hash: tx.hash,
        block_number: tx.block_number,
        timeStamp: Math.floor(new Date(tx.block_timestamp).getTime() / 1000).toString(),
        from: tx.from_address,
        to: tx.to_address || '',
        value: tx.value || '0',
        gas: tx.gas || '0',
        gasPrice: tx.gas_price || '0',
        gasUsed: tx.receipt_gas_used || '0',
        input: tx.input || '0x',
        txreceipt_status: tx.receipt_status === '1' ? '1' : '0',
        isError: tx.receipt_status === '1' ? '0' : '1',
        // Keep some Moralis-specific fields
        method_label: tx.method_label || '',
        // Store internal transactions if present
        internal_transactions: tx.internal_transactions || []
      };
      
      newTxns.push(formattedTx);
    }
    
    // Log progress
    if (page % 10 === 0 || page < 5) {
      console.log(`  Page ${page + 1}: ${newTxns.length} new transactions collected`);
    }
    
    // Check for next page
    cursor = data.cursor;
    if (!cursor) {
      break;
    }
    
    page++;
    await delay(200); // Gentle rate limiting
  }
  
  console.log(`Fetched ${newTxns.length} new transactions for ${walletName}`);
  console.log(`Existing transactions: ${existingTxns.length}`);
  
  // Merge with existing (new first, then existing)
  // Dedupe by hash
  const seenHashes = new Set();
  const allTxns = [];
  
  for (const tx of newTxns) {
    if (!seenHashes.has(tx.hash)) {
      seenHashes.add(tx.hash);
      allTxns.push(tx);
    }
  }
  
  for (const tx of existingTxns) {
    if (!seenHashes.has(tx.hash)) {
      seenHashes.add(tx.hash);
      allTxns.push(tx);
    }
  }
  
  // Sort by timestamp descending (newest first)
  allTxns.sort((a, b) => Number(b.timeStamp) - Number(a.timeStamp));
  
  console.log(`Total transactions after merge: ${allTxns.length}`);
  
  return allTxns;
}

/**
 * Fetch all token transfers for a wallet via PulseScan API.
 *
 * Why PulseScan instead of Moralis: as of April 2026, Moralis's /erc20/transfers
 * endpoint has stopped reliably indexing PulseChain Transfer events — the newest
 * data Moralis returns for our wallets is months old. PulseScan is PulseChain's
 * canonical block explorer and returns every Transfer event authoritatively.
 *
 * Normal transaction fetching (above) still uses Moralis since that endpoint
 * remains current.
 */
async function fetchWalletTokenTransfers(walletAddress, walletName, existingTransfers = []) {
  console.log(`\n${'='.repeat(50)}`);
  console.log(`Fetching ${walletName} token transfers via PulseScan...`);
  console.log(`Wallet: ${walletAddress}`);
  console.log(`${'='.repeat(50)}`);
  
  console.log(`Data source: PulseScan API (Moralis ERC20 indexing is behind by months)`);
  console.log(`Existing entries loaded from disk: ${existingTransfers.length}`);
  
  const newTransfers = [];
  let page = 1;
  const pageSize = 10000; // PulseScan allows up to 10k per page
  
  while (true) {
    const data = await pulsescanRequest({
      module: 'account',
      action: 'tokentx',
      address: walletAddress,
      startblock: 0,
      endblock: 99999999,
      sort: 'desc',
      page: page,
      offset: pageSize
    });
    
    if (!data) {
      console.log(`  Page ${page}: request failed, retrying in 5s...`);
      await delay(5000);
      continue;
    }
    
    // PulseScan returns { status, message, result } — result is array on success,
    // or a string message like "No transactions found" when empty.
    if (!Array.isArray(data.result) || data.result.length === 0) {
      console.log(`  Page ${page}: no more data (${data.message || 'empty'})`);
      break;
    }
    
    for (const tx of data.result) {
      const tokenAddr = (tx.contractAddress || '').toLowerCase();
      const knownToken = KNOWN_TOKENS[tokenAddr];
      
      const formattedTx = {
        hash: tx.hash,
        blockNumber: tx.blockNumber,
        timeStamp: tx.timeStamp,
        from: (tx.from || '').toLowerCase(),
        to: (tx.to || '').toLowerCase(),
        value: tx.value || '0',
        contractAddress: tx.contractAddress,
        tokenName: knownToken?.name || tx.tokenName || '',
        tokenSymbol: knownToken?.symbol || tx.tokenSymbol || '',
        tokenDecimal: (knownToken?.decimals || tx.tokenDecimal || 18).toString(),
        possible_spam: false,      // PulseScan doesn't flag spam
        verified_contract: false    // Not provided by PulseScan
      };
      
      newTransfers.push(formattedTx);
    }
    
    const newest = data.result[0];
    const newestBlock = newest?.blockNumber || '?';
    const newestDate = newest?.timeStamp 
      ? new Date(Number(newest.timeStamp) * 1000).toISOString().slice(0, 10) 
      : '?';
    console.log(`  Page ${page}: ${newTransfers.length} total fetched (newest on page: block ${newestBlock}, ${newestDate})`);
    
    // Got less than a full page → we've reached the end
    if (data.result.length < pageSize) break;
    
    page++;
    await delay(300); // Gentle rate limiting for PulseScan
  }
  
  console.log(`Fetched ${newTransfers.length} total token transfers from PulseScan`);
  console.log(`Existing local entries: ${existingTransfers.length}`);
  
  // Merge: new first (authoritative), then existing entries not in new fetch.
  // Preserves any data PulseScan might somehow drop; normally new covers everything.
  const getKey = (tx) => `${tx.hash}-${tx.contractAddress}-${tx.from}-${tx.to}-${tx.value}`;
  const seenKeys = new Set();
  const allTransfers = [];
  
  for (const tx of newTransfers) {
    const key = getKey(tx);
    if (!seenKeys.has(key)) {
      seenKeys.add(key);
      allTransfers.push(tx);
    }
  }
  
  let preservedCount = 0;
  for (const tx of existingTransfers) {
    const key = getKey(tx);
    if (!seenKeys.has(key)) {
      seenKeys.add(key);
      allTransfers.push(tx);
      preservedCount++;
    }
  }
  
  allTransfers.sort((a, b) => Number(b.timeStamp) - Number(a.timeStamp));
  
  // Sanity check: warn loudly if fetch missed recent activity
  const newestTs = allTransfers.length > 0 ? Number(allTransfers[0].timeStamp) : 0;
  const ageHours = (Date.now() / 1000 - newestTs) / 3600;
  if (ageHours > 48 && allTransfers.length > 0) {
    console.log(`  ⚠️  WARNING: newest token transfer is ${ageHours.toFixed(1)}h old — PulseScan may have an indexing issue`);
  }
  
  console.log(`Merge result: ${allTransfers.length} total (${preservedCount} preserved from existing, not in fresh fetch)`);
  
  return allTransfers;
}

/**
 * Fetch current token balances for a wallet
 */
async function fetchWalletBalances(walletAddress, walletName) {
  console.log(`\nFetching ${walletName} token balances...`);
  
  const data = await moralisRequest(`/${walletAddress}/erc20`, {
    chain: CHAIN
  });
  
  if (data && Array.isArray(data)) {
    console.log(`  Found ${data.length} tokens`);
    
    const balances = data.map(token => {
      const tokenAddr = token.token_address?.toLowerCase() || '';
      const knownToken = KNOWN_TOKENS[tokenAddr];
      const decimals = knownToken?.decimals || token.decimals || 18;
      const balance = Number(BigInt(token.balance || '0')) / Math.pow(10, decimals);
      
      return {
        address: token.token_address,
        symbol: knownToken?.symbol || token.symbol || 'Unknown',
        name: knownToken?.name || token.name || '',
        balance: balance,
        decimals: decimals,
        possible_spam: token.possible_spam || false,
        verified_contract: token.verified_contract || false
      };
    }).filter(t => t.balance > 0 && !t.possible_spam);
    
    // Sort by balance (descending)
    balances.sort((a, b) => b.balance - a.balance);
    
    return balances;
  }
  
  return [];
}

/**
 * Fetch native balance for a wallet
 */
async function fetchNativeBalance(walletAddress, walletName) {
  console.log(`\nFetching ${walletName} native (PLS) balance...`);
  
  const data = await moralisRequest(`/${walletAddress}/balance`, {
    chain: CHAIN
  });
  
  if (data && data.balance) {
    const balance = Number(BigInt(data.balance)) / 1e18;
    console.log(`  ${walletName} PLS balance: ${balance.toLocaleString()}`);
    return balance;
  }
  
  return 0;
}

/**
 * Main function
 */
async function main() {
  console.log('\n' + '='.repeat(60));
  console.log('TREASURY TRANSACTION FETCHER - MORALIS VERSION');
  console.log('Started:', new Date().toISOString());
  console.log('='.repeat(60));
  
  const dataDir = path.join(__dirname, '..', 'data');
  console.log(`\nData directory: ${dataDir}`);
  
  // Ensure data directory exists
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
    console.log('Created data directory');
  }
  
  // ============================================
  // LOAD EXISTING DATA
  // ============================================
  
  console.log('\nLoading existing data...');
  
  const existingW1Txns = loadExistingData(path.join(dataDir, 'treasury-wallet1-txns.json'));
  const existingW2Txns = loadExistingData(path.join(dataDir, 'treasury-wallet2-txns.json'));
  const existingW1Tokens = loadExistingData(path.join(dataDir, 'treasury-wallet1-tokens.json'));
  const existingW2Tokens = loadExistingData(path.join(dataDir, 'treasury-wallet2-tokens.json'));
  
  // ============================================
  // FETCH WALLET 1 DATA
  // ============================================
  
  const wallet1Txns = await fetchWalletTransactions(
    WALLET1, 
    'Wallet 1 (Main Treasury)', 
    existingW1Txns?.transactions || []
  );
  await delay(500);
  
  const wallet1Tokens = await fetchWalletTokenTransfers(
    WALLET1, 
    'Wallet 1 (Main Treasury)', 
    existingW1Tokens?.transfers || []
  );
  await delay(500);
  
  const wallet1Balances = await fetchWalletBalances(WALLET1, 'Wallet 1');
  await delay(300);
  
  const wallet1NativeBalance = await fetchNativeBalance(WALLET1, 'Wallet 1');
  await delay(500);
  
  // ============================================
  // FETCH WALLET 2 DATA
  // ============================================
  
  const wallet2Txns = await fetchWalletTransactions(
    WALLET2, 
    'Wallet 2 (Secondary)', 
    existingW2Txns?.transactions || []
  );
  await delay(500);
  
  const wallet2Tokens = await fetchWalletTokenTransfers(
    WALLET2, 
    'Wallet 2 (Secondary)', 
    existingW2Tokens?.transfers || []
  );
  await delay(500);
  
  const wallet2Balances = await fetchWalletBalances(WALLET2, 'Wallet 2');
  await delay(300);
  
  const wallet2NativeBalance = await fetchNativeBalance(WALLET2, 'Wallet 2');
  
  // ============================================
  // WRITE DATA FILES
  // ============================================
  
  console.log(`\n${'='.repeat(50)}`);
  console.log('Writing data files...');
  console.log(`${'='.repeat(50)}`);
  
  // Wallet 1 transactions
  const w1TxnPath = path.join(dataDir, 'treasury-wallet1-txns.json');
  fs.writeFileSync(w1TxnPath, JSON.stringify({
    wallet: WALLET1,
    lastUpdated: new Date().toISOString(),
    count: wallet1Txns.length,
    transactions: wallet1Txns
  }));
  console.log(`  Written: ${w1TxnPath} (${(fs.statSync(w1TxnPath).size / 1024 / 1024).toFixed(2)} MB)`);
  
  // Wallet 2 transactions
  const w2TxnPath = path.join(dataDir, 'treasury-wallet2-txns.json');
  fs.writeFileSync(w2TxnPath, JSON.stringify({
    wallet: WALLET2,
    lastUpdated: new Date().toISOString(),
    count: wallet2Txns.length,
    transactions: wallet2Txns
  }));
  console.log(`  Written: ${w2TxnPath} (${(fs.statSync(w2TxnPath).size / 1024 / 1024).toFixed(2)} MB)`);
  
  // Wallet 1 token transfers
  const w1TokenPath = path.join(dataDir, 'treasury-wallet1-tokens.json');
  fs.writeFileSync(w1TokenPath, JSON.stringify({
    wallet: WALLET1,
    lastUpdated: new Date().toISOString(),
    count: wallet1Tokens.length,
    transfers: wallet1Tokens
  }));
  console.log(`  Written: ${w1TokenPath} (${(fs.statSync(w1TokenPath).size / 1024 / 1024).toFixed(2)} MB)`);
  
  // Wallet 2 token transfers
  const w2TokenPath = path.join(dataDir, 'treasury-wallet2-tokens.json');
  fs.writeFileSync(w2TokenPath, JSON.stringify({
    wallet: WALLET2,
    lastUpdated: new Date().toISOString(),
    count: wallet2Tokens.length,
    transfers: wallet2Tokens
  }));
  console.log(`  Written: ${w2TokenPath} (${(fs.statSync(w2TokenPath).size / 1024 / 1024).toFixed(2)} MB)`);
  
  // ============================================
  // WRITE SUMMARY FILE
  // ============================================
  
  const summaryData = {
    lastUpdated: new Date().toISOString(),
    dataSource: 'Moralis',
    
    wallet1: {
      address: WALLET1,
      name: 'Main Treasury',
      transactionCount: wallet1Txns.length,
      tokenTransferCount: wallet1Tokens.length,
      nativeBalance: wallet1NativeBalance,
      tokenBalances: wallet1Balances.slice(0, 20), // Top 20 tokens
      oldestTx: wallet1Txns.length > 0 ? wallet1Txns[wallet1Txns.length - 1].timeStamp : null,
      newestTx: wallet1Txns.length > 0 ? wallet1Txns[0].timeStamp : null
    },
    
    wallet2: {
      address: WALLET2,
      name: 'Secondary',
      transactionCount: wallet2Txns.length,
      tokenTransferCount: wallet2Tokens.length,
      nativeBalance: wallet2NativeBalance,
      tokenBalances: wallet2Balances.slice(0, 20), // Top 20 tokens
      oldestTx: wallet2Txns.length > 0 ? wallet2Txns[wallet2Txns.length - 1].timeStamp : null,
      newestTx: wallet2Txns.length > 0 ? wallet2Txns[0].timeStamp : null
    },
    
    // Combined stats
    totals: {
      transactionCount: wallet1Txns.length + wallet2Txns.length,
      tokenTransferCount: wallet1Tokens.length + wallet2Tokens.length,
      totalPLSBalance: wallet1NativeBalance + wallet2NativeBalance
    },
    
    // References for file loading
    files: {
      wallet1Txns: 'treasury-wallet1-txns.json',
      wallet2Txns: 'treasury-wallet2-txns.json',
      wallet1Tokens: 'treasury-wallet1-tokens.json',
      wallet2Tokens: 'treasury-wallet2-tokens.json'
    }
  };
  
  const summaryPath = path.join(dataDir, 'treasury-summary.json');
  fs.writeFileSync(summaryPath, JSON.stringify(summaryData, null, 2));
  console.log(`  Written: ${summaryPath}`);
  
  // ============================================
  // PRINT SUMMARY
  // ============================================
  
  console.log('\n' + '='.repeat(60));
  console.log('SUMMARY');
  console.log('='.repeat(60));
  
  console.log(`\nWallet 1 (Main Treasury):`);
  console.log(`  Address: ${WALLET1}`);
  console.log(`  Transactions: ${wallet1Txns.length}`);
  console.log(`  Token Transfers: ${wallet1Tokens.length}`);
  console.log(`  PLS Balance: ${wallet1NativeBalance.toLocaleString()}`);
  console.log(`  Token Balances: ${wallet1Balances.length} tokens`);
  
  console.log(`\nWallet 2 (Secondary):`);
  console.log(`  Address: ${WALLET2}`);
  console.log(`  Transactions: ${wallet2Txns.length}`);
  console.log(`  Token Transfers: ${wallet2Tokens.length}`);
  console.log(`  PLS Balance: ${wallet2NativeBalance.toLocaleString()}`);
  console.log(`  Token Balances: ${wallet2Balances.length} tokens`);
  
  console.log(`\nCombined Totals:`);
  console.log(`  Total Transactions: ${wallet1Txns.length + wallet2Txns.length}`);
  console.log(`  Total Token Transfers: ${wallet1Tokens.length + wallet2Tokens.length}`);
  console.log(`  Total PLS Balance: ${(wallet1NativeBalance + wallet2NativeBalance).toLocaleString()}`);
  
  console.log('\n' + '='.repeat(60));
  console.log('FILES WRITTEN:');
  console.log('  - treasury-wallet1-txns.json');
  console.log('  - treasury-wallet2-txns.json');
  console.log('  - treasury-wallet1-tokens.json');
  console.log('  - treasury-wallet2-tokens.json');
  console.log('  - treasury-summary.json');
  console.log('Completed:', new Date().toISOString());
  console.log('='.repeat(60));
}

main().catch(err => {
  console.error('FATAL ERROR:', err);
  process.exit(1);
});
