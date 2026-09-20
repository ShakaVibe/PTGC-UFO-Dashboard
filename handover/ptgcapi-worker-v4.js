// Cloudflare Worker - Secure GitHub Proxy for ToolBox
// v3: Added scheduled cron sync for commission data
// v4 (2026-09-20): FIX — reads go through the GitHub RAW media type.
//   GitHub's contents API refuses to inline a file over 1 MB: it still answers
//   200 OK, but with "content": "" and "encoding": "none". The old code did
//   atob("") -> JSON.parse("") -> "Unexpected end of JSON input", which the outer
//   catch turned into a 500 on /public/commissions. data/affiliate-commissions.json
//   grows on every cron run, so it broke the moment it crossed 1 MB — both for the
//   public endpoint AND for the sync's own read (which failed silently, so no new
//   transactions were being recorded). Raw is served up to 100 MB.
//   Also: the sync now writes compact JSON instead of 2-space pretty-print, which
//   roughly halves the file it has to keep re-uploading.

const GITHUB_OWNER = 'ShakaVibe';
const GITHUB_REPO = 'ToolBox';
const ALLOWED_ORIGIN = '*';
const COMMISSION_FILE_PATH = 'data/affiliate-commissions.json';
const DATA_START_DATE = new Date('2026-01-12T00:00:00Z'); // Filter out test data before this

export default {
  // Handle HTTP requests
  async fetch(request, env) {
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': ALLOWED_ORIGIN,
          'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, X-ToolBox-Auth',
        },
      });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    try {
      if (request.method === 'GET' && path === '/public/commissions') {
        return await getPublicCommissions(env);
      }

      const authHeader = request.headers.get('X-ToolBox-Auth');
      if (authHeader !== env.TOOLBOX_SECRET) {
        return jsonResponse({ error: 'Unauthorized' }, 401);
      }

      if (request.method === 'GET' && path === '/read') {
        const filePath = url.searchParams.get('path');
        if (!filePath) {
          return jsonResponse({ error: 'Missing path parameter' }, 400);
        }
        return await readFile(filePath, env);
      }

      if (request.method === 'PUT' && path === '/write') {
        const filePath = url.searchParams.get('path');
        if (!filePath) {
          return jsonResponse({ error: 'Missing path parameter' }, 400);
        }
        const body = await request.json();
        return await writeFile(filePath, body.content, body.message, body.sha, env);
      }

      // Manual trigger for sync (authenticated)
      if (request.method === 'POST' && path === '/sync') {
        const result = await runCommissionSync(env);
        return jsonResponse(result);
      }

      return jsonResponse({ error: 'Not found' }, 404);

    } catch (e) {
      return jsonResponse({ error: e.message }, 500);
    }
  },

  // Handle scheduled cron triggers
  async scheduled(event, env, ctx) {
    console.log('Cron triggered at:', new Date().toISOString());
    ctx.waitUntil(runCommissionSync(env));
  },
};

// ============================================
// COMMISSION SYNC LOGIC
// ============================================
async function runCommissionSync(env) {
  console.log('=== SCHEDULED SYNC STARTING ===');
  console.log('Time:', new Date().toISOString());

  try {
    // STEP 1: Load existing data from GitHub
    const existingResult = await readFileRaw(COMMISSION_FILE_PATH, env);
    const existingData = existingResult.data || {};
    const existingSha = existingResult.sha;

    const existingLogs = existingData.monthlyLogs || {};
    const existingReferrers = existingData.referrers || {};

    // Build lookup of ALL existing transactions by txHash
    const existingTxHashes = new Set();
    Object.values(existingLogs).forEach(monthLog => {
      (monthLog.entries || []).forEach(entry => {
        (entry.buys || []).forEach(tx => {
          if (tx.txHash) existingTxHashes.add(tx.txHash);
        });
      });
    });

    console.log('Existing txHashes:', existingTxHashes.size);

    // STEP 2: Fetch from referral API (both current and previous month)
    const [currentData, previousData] = await Promise.all([
      fetchReferralData('current'),
      fetchReferralData('previous')
    ]);

    // Combine and dedupe by username
    const combinedData = [...currentData];
    for (const prevItem of previousData) {
      const existing = combinedData.find(c => c.referred_username === prevItem.referred_username);
      if (existing) {
        const existingHashes = new Set((existing.transactions || []).map(t => t.tx_hash));
        for (const tx of (prevItem.transactions || [])) {
          if (!existingHashes.has(tx.tx_hash)) {
            existing.transactions = existing.transactions || [];
            existing.transactions.push(tx);
          }
        }
      } else {
        combinedData.push(prevItem);
      }
    }

    console.log('API referrers found:', combinedData.length);

    if (combinedData.length === 0) {
      console.log('No referrers from API');
      return { success: true, message: 'No data to sync', newTxCount: 0 };
    }

    // STEP 3: Process transactions and route to correct months
    const updatedReferrers = { ...existingReferrers };
    const updatedLogs = { ...existingLogs };

    let newTxCount = 0;
    let skippedTxCount = 0;
    let filteredOutCount = 0;
    const monthsUpdated = new Set();

    // Get default settings from most recent month, or use defaults
    const sortedMonths = Object.keys(existingLogs).sort().reverse();
    const defaultSettings = sortedMonths.length > 0
      ? existingLogs[sortedMonths[0]].settings
      : { commissionRate: 2, threshold: 0, thresholdType: 'usd', coverFee: true };

    for (const item of combinedData) {
      if (!item.referred_username || !item.referred_wallet) continue;

      const username = item.referred_username;
      const wallet = item.referred_wallet;

      for (const tx of (item.transactions || [])) {
        // Skip transactions without a date
        if (!tx.timestamp) {
          filteredOutCount++;
          continue;
        }

        // Skip transactions before start date
        const txDate = new Date(tx.timestamp);
        if (txDate < DATA_START_DATE) {
          filteredOutCount++;
          continue;
        }

        // Skip if we already have this transaction
        if (!tx.transaction_hash || existingTxHashes.has(tx.transaction_hash)) {
          skippedTxCount++;
          continue;
        }

        // Determine the correct month for this transaction
        const txMonth = tx.timestamp.slice(0, 7);
        monthsUpdated.add(txMonth);

        // Ensure month exists in logs
        if (!updatedLogs[txMonth]) {
          updatedLogs[txMonth] = {
            settings: { ...defaultSettings },
            entries: []
          };
        }

        // Find or create entry for this user in this month
        let entry = updatedLogs[txMonth].entries.find(e => e.username === username);
        if (!entry) {
          entry = {
            id: `${txMonth}-${username}`,
            username: username,
            wallet: wallet,
            buysCount: 0,
            usdAmount: 0,
            ptgcAmount: 0,
            commissionRate: updatedLogs[txMonth].settings.commissionRate || 2,
            commissionUsd: 0,
            commissionPtgc: 0,
            meetsThreshold: true,
            status: 'unpaid',
            paidTxHash: null,
            paidDate: null,
            buys: [],
            addedDate: new Date().toISOString(),
            lastSyncDate: new Date().toISOString()
          };
          updatedLogs[txMonth].entries.push(entry);
        }

        // Add the transaction
        const newTx = {
          date: tx.timestamp,
          buyerWallet: tx.user_address || null,
          usdAmount: parseFloat(tx.usd_amount) || 0,
          ptgcAmount: parseFloat(tx.ptgc_amount) || 0,
          txHash: tx.transaction_hash,
          paid: false,
          paidTxHash: null,
          paidDate: null,
          addedDate: new Date().toISOString()
        };

        entry.buys.push(newTx);
        existingTxHashes.add(tx.transaction_hash);
        newTxCount++;

        console.log(`Added tx ${tx.transaction_hash.slice(0, 10)}... to ${txMonth} for ${username}`);
      }

      // Update registry
      if (!updatedReferrers[username]) {
        updatedReferrers[username] = {
          wallet: wallet,
          addedDate: new Date().toISOString()
        };
      }
    }

    // STEP 4: Recalculate totals for all updated months
    for (const month of monthsUpdated) {
      const settings = updatedLogs[month].settings || {};
      const rate = settings.commissionRate || 2;
      const threshold = settings.threshold || 0;
      const thresholdType = settings.thresholdType || 'usd';

      updatedLogs[month].entries = updatedLogs[month].entries.map(entry => {
        entry.buysCount = entry.buys.length;
        entry.usdAmount = entry.buys.reduce((sum, b) => sum + (b.usdAmount || 0), 0);
        entry.ptgcAmount = entry.buys.reduce((sum, b) => sum + (b.ptgcAmount || 0), 0);

        // Check threshold
        let meetsThreshold;
        if (threshold === 0) {
          meetsThreshold = true;
        } else if (thresholdType === 'usd') {
          meetsThreshold = entry.usdAmount >= threshold;
        } else {
          meetsThreshold = entry.ptgcAmount >= threshold;
        }

        entry.commissionPtgc = meetsThreshold ? entry.ptgcAmount * (rate / 100) : 0;
        entry.meetsThreshold = meetsThreshold;
        entry.lastSyncDate = new Date().toISOString();

        return entry;
      });

      updatedLogs[month].lastSyncDate = new Date().toISOString();
    }

    // STEP 5: Save back to GitHub (only if there are changes)
    if (newTxCount > 0) {
      const updatedData = {
        ...existingData,
        referrers: updatedReferrers,
        monthlyLogs: updatedLogs,
        lastAutoSync: new Date().toISOString()
      };

      await writeFileRaw(
        COMMISSION_FILE_PATH,
        // v4: compact, not JSON.stringify(updatedData, null, 2). This file only ever
        // grows and is re-uploaded whole on every sync; the indentation was roughly
        // half its bytes and bought nothing — nothing reads it by hand.
        JSON.stringify(updatedData),
        `Auto-sync: Added ${newTxCount} new transactions`,
        existingSha,
        env
      );

      console.log('=== SYNC COMPLETE ===');
      console.log(`New transactions: ${newTxCount}`);
      console.log(`Skipped (existing): ${skippedTxCount}`);
      console.log(`Filtered out: ${filteredOutCount}`);
      console.log(`Months updated: ${Array.from(monthsUpdated).join(', ')}`);

      return {
        success: true,
        message: 'Sync complete',
        newTxCount,
        skippedTxCount,
        filteredOutCount,
        monthsUpdated: Array.from(monthsUpdated)
      };
    } else {
      console.log('=== SYNC COMPLETE (no new data) ===');
      return {
        success: true,
        message: 'No new transactions to sync',
        newTxCount: 0,
        skippedTxCount,
        filteredOutCount
      };
    }

  } catch (e) {
    console.error('Sync error:', e);
    return {
      success: false,
      error: e.message
    };
  }
}

// Fetch referral data from API
async function fetchReferralData(period) {
  const apiUrl = `https://stats.goptgc.com/api/referral/ranking?period=${period}&type=PTGC`;

  try {
    console.log(`Fetching ${period} from API...`);
    const response = await fetch(apiUrl, {
      headers: {
        'User-Agent': 'ToolBox-Worker'
      }
    });

    if (!response.ok) {
      if (response.status === 422) {
        console.log(`No data for ${period} period`);
        return [];
      }
      console.log(`API error for ${period}: ${response.status}`);
      return [];
    }

    const result = await response.json();
    return result.status === 200 && result.data ? result.data : [];
  } catch (e) {
    console.error(`Failed to fetch ${period}:`, e);
    return [];
  }
}

// ============================================
// GITHUB FILE OPERATIONS (internal use)
// ============================================

// v4: two requests instead of one.
//   1. the JSON metadata, for the sha the write path needs;
//   2. the file itself with Accept: application/vnd.github.raw.
// The old single request asked for the JSON form and read `result.content`, which
// GitHub leaves EMPTY for anything over 1 MB (encoding: "none") — the 500 that took
// the affiliates page down. Raw has no such ceiling.
async function readFileRaw(path, env) {
  const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${path}`;
  const headers = accept => ({
    'Authorization': `token ${env.GITHUB_TOKEN}`,
    'Accept': accept,
    'User-Agent': 'ToolBox-Worker',
  });

  const metaRes = await fetch(url, { headers: headers('application/vnd.github.v3+json') });
  if (!metaRes.ok) {
    if (metaRes.status === 404) {
      return { data: null, sha: null };
    }
    throw new Error(`GitHub read failed: ${metaRes.status}`);
  }
  const meta = await metaRes.json();

  const rawRes = await fetch(url, { headers: headers('application/vnd.github.raw') });
  if (!rawRes.ok) {
    throw new Error(`GitHub raw read failed: ${rawRes.status}`);
  }
  const content = await rawRes.text();

  // An empty body is never a valid JSON document. Say so plainly instead of letting
  // JSON.parse throw "Unexpected end of JSON input", which says nothing about where
  // it came from — that message cost an afternoon.
  if (!content.trim()) {
    throw new Error(`GitHub returned an empty body for ${path} (${meta.size} bytes on record)`);
  }

  return {
    data: JSON.parse(content),
    sha: meta.sha,
  };
}

async function writeFileRaw(path, content, message, sha, env) {
  let currentSha = sha;
  if (!currentSha) {
    try {
      const getRes = await fetch(
        `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${path}`,
        {
          headers: {
            'Authorization': `token ${env.GITHUB_TOKEN}`,
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'ToolBox-Worker',
          },
        }
      );
      if (getRes.ok) {
        const data = await getRes.json();
        currentSha = data.sha;
      }
    } catch (e) {
      // Ignore - file might not exist yet
    }
  }

  const body = {
    message: message || 'Update from ToolBox',
    content: btoa(content),
    branch: 'main',
  };

  if (currentSha) {
    body.sha = currentSha;
  }

  const response = await fetch(
    `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${path}`,
    {
      method: 'PUT',
      headers: {
        'Authorization': `token ${env.GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json',
        'User-Agent': 'ToolBox-Worker',
      },
      body: JSON.stringify(body),
    }
  );

  if (!response.ok) {
    throw new Error(`GitHub write failed: ${response.status}`);
  }

  return await response.json();
}

// ============================================
// EXISTING ENDPOINTS
// ============================================

// v4: reads through readFileRaw (raw media type) instead of repeating the
// contents-API inline read that broke past 1 MB. A read that fails now answers 503
// with the reason instead of a bare 500 — the page can say the service is down
// rather than showing a mystery.
async function getPublicCommissions(env) {
  let data;
  try {
    const result = await readFileRaw(COMMISSION_FILE_PATH, env);
    data = result.data;
  } catch (e) {
    console.error('getPublicCommissions failed:', e);
    return jsonResponse({ error: 'Commission data unavailable: ' + e.message }, 503);
  }

  if (!data) {
    return jsonResponse({ error: 'Data not found' }, 404);
  }

  const publicData = {
    referrers: data.referrers || {},
    monthlyLogs: data.monthlyLogs || {},
    receipts: (data.receipts || []).map(r => ({
      id: r.id,
      date: r.date,
      username: r.username,
      wallet: r.wallet,
      amount: r.amount,
      rate: r.rate,
      txCount: r.txCount,
      txHash: r.txHash,
      month: r.month,
      ptgcPrice: r.ptgcPrice,
      usdValue: r.usdValue,
      feeCovered: r.feeCovered
    })),
  };

  return jsonResponse(publicData);
}

async function readFile(path, env) {
  const result = await readFileRaw(path, env);
  return jsonResponse(result);
}

async function writeFile(path, content, message, sha, env) {
  const result = await writeFileRaw(path, content, message, sha, env);
  return jsonResponse({ success: true, sha: result.content.sha });
}

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': ALLOWED_ORIGIN,
    },
  });
}
