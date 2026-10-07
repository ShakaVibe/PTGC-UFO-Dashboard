#!/usr/bin/env python3
"""Audit III, batch 4 (2026-10-07): the pipeline — c17, c18, c20, c19, c22. Idempotent — run from the repo root on both copies:
    python3 tools/audit3-p4.py
Each edit asserts its anchor exists exactly once (or is already applied) so a drifted file fails loudly instead of half-applying.
  c17 staleness thresholds sized for the HOURLY beat (the Worker's cron since 2026-10-06; a healthy hourly file is ≤ ~75 min old):
      amber at 2.5 h for the hourly files (burn-history, ledger, Holders Details, Humans vs Bots, DAO Buys — the latter a named
      constant now), VALUE_GEN_STALE 6 h → 3 h (past it the dashboard starts the live chain scan — two missed hours plus slack),
      the 6-h-gated allocation file 14 h / 36 h → 8 h / 24 h, cgFresh 24 h → 12 h. The "ignore" limits (36 h, 48 h, 7 d) stay.
      NOT done: dropping lv-snapshot's 6-h gate (hourly points would grow lv-snapshots.json 4× faster — 377 KB today, read every
      5 min by the dashboard; c16's kpi-history file is the right fix).
  c18 GitHub's fallback schedule moves off the Worker's minute (:07 → :37) and, on a schedule event, stands down when the last
      run is under 45 min old (data/pipeline-status.json's generatedAt, else burn-summary.json's lastUpdated).
  c20 scripts/pipeline-run.mjs writes data/pipeline-status.json (schema 1): generatedAt, trigger, runUrl, seconds, lanes, and per
      step outcome / seconds / why / lastSuccessAt / lastFailureAt / lastError / carried (a `::warning::` in the step's output —
      dao-buys' carry-forward exits 0 and showed green); the file joins the Commit list. The job summary marks carried steps ⚠️.
  c19 value-generated moves to the END of the rpc lane (it rescans 90 days every hour, ~6 min, and held eight quick files behind
      it). NOT done: the checkpoint cache (M).
  c22 fetch-coingecko-data.js: PTGC's `ath` is written (CoinGecko market_data.ath.usd, never lower than the previous file's; UFO
      stays unwritten on purpose — gotcha 0) and the readers take the max of the file and ATH_PRICES; `lastUpdated` is stamped
      right before the save (was the START of a ~3.5-min run); saveData writes tmp + rename.
"""
import sys, re, hashlib

def read(p): return open(p, encoding='utf-8').read()
def write(p, s): open(p, 'w', encoding='utf-8').write(s)
def md5(s): return hashlib.md5(s.encode('utf-8')).hexdigest()

class Edit:
    def __init__(self, path):
        self.path = path; self.s = read(path); self.n = 0
    def rep(self, old, new, count=1, done_marker=None):
        """Replace `old` → `new` exactly `count` times; skip silently when `done_marker` (default: new) is already present."""
        if done_marker is not None:
            if done_marker in self.s: return False
        elif new in self.s and old not in self.s:
            return False
        c = self.s.count(old)
        assert c == count, f'{self.path}: expected {count}× anchor, found {c}: {old[:90]!r}'
        self.s = self.s.replace(old, new); self.n += 1; return True
    def save(self):
        write(self.path, self.s); print(f'{self.path}: {self.n} edit(s), md5 {md5(self.s)}')

# ================================================================= index.html — c17 thresholds, c22 ath reader
ix = Edit('index.html')
ix.rep("""    const VALUE_GEN_STALE_MS=6*60*60*1000; // measured 2026-09-18: GitHub runs the hourly pipeline ~5x/day (gaps up to 5 h), so 6 h = one missed run -> fall back to live""",
       """    /* c17 (Audit III, 2026-10-07): the pipeline is HOURLY for real since the Worker's cron (2026-10-06) — a healthy hourly file
       is ≤ ~75 min old. Past this the dashboard starts the live chain scan, so it is two missed hours plus slack, not one.
       (Was 6 h, sized for "~5 runs a day, gaps up to 5 h" measured 2026-09-18.) */
    const VALUE_GEN_STALE_MS=3*60*60*1000;""")
ix.rep("""    const ALLOC_STALE_MS=14*60*60*1000;
    const ALLOC_DEAD_MS=36*60*60*1000;""",
       """    const ALLOC_STALE_MS=8*60*60*1000;    // c17: the step is gated at 6 h and the pipeline is hourly, so a healthy file is ≤ ~7.3 h (was 14 h)
    const ALLOC_DEAD_MS=24*60*60*1000;    // c17: three missed rebuilds (was 36 h)""")
ix.rep("""    const BURN_HISTORY_STALE_MS=8*60*60*1000;     // the pipeline lands ~5x/day (gaps up to 5 h, measured 2026-09-18) — amber only past a missed run""",
       """    const BURN_HISTORY_STALE_MS=2.5*60*60*1000;   // c17: hourly file — amber past two missed runs (was 8 h for the old ~5-runs-a-day beat)
    const HOURLY_AMBER_MS=2.5*60*60*1000;         // c17: the one amber threshold for the hourly files (DAO Buys, Holders Details, Humans vs Bots)""")
ix.rep("""      const stale=ageMs!=null&&ageMs>6*3600000;
      const pill=(on)=>`tap-h px-2 rounded-md border text-[10px]""",
       """      const stale=ageMs!=null&&ageMs>HOURLY_AMBER_MS;   // c17: was a literal 6 h
      const pill=(on)=>`tap-h px-2 rounded-md border text-[10px]""")
ix.rep("""    const NH_MAX_AGE=36*3600*1000,NH_TTL=5*60*1000,NH_AMBER_MS=6*3600*1000;""",
       """    const NH_MAX_AGE=36*3600*1000,NH_TTL=5*60*1000,NH_AMBER_MS=HOURLY_AMBER_MS;   // c17: amber at 2.5 h (was 6 h)""")
ix.rep("""    const VS_MAX_AGE=36*3600*1000,VS_TTL=5*60*1000,VS_AMBER_MS=3*3600*1000;""",
       """    const VS_MAX_AGE=36*3600*1000,VS_TTL=5*60*1000,VS_AMBER_MS=HOURLY_AMBER_MS;   // c17: amber at 2.5 h (was 3 h)""")
ix.rep("""          const cgFresh = isFinite(cgAgeMs) && cgAgeMs < 24*3600*1000;""",
       """          const cgFresh = isFinite(cgAgeMs) && cgAgeMs < 12*3600*1000;   // c17: the file is hourly — 12 h is a long outage, not a normal gap (was 24 h)""")
ix.rep("""      const athPrice=coingeckoDataCache?.[token]?.ath||ATH_PRICES[token]||0;""",
       """      const athPrice=Math.max(coingeckoDataCache?.[token]?.ath||0,ATH_PRICES[token]||0);   // c22: the file's ATH (PTGC only, written since 2026-10-07) can only raise the hand constant""")
ix.rep("""    // These are fallbacks; coingeckoDataCache ATH will be used if available""",
       """    // These are floors: fetch-coingecko-data.js writes PTGC's CoinGecko ATH into the file (c22, 2026-10-07) and the readers take
    // the max; UFO's is NEVER written (gotcha 0: the pre-migration high is the one that counts)""")
ix.save()

# ================================================================= calculators.html — c22 ath readers
ca = Edit('calculators.html')
ca.rep("""      const athPrice=coingeckoDataCache?.[token]?.ath||ATH_PRICES[token]||0;""",
       """      const athPrice=Math.max(coingeckoDataCache?.[token]?.ath||0,ATH_PRICES[token]||0);   // c22: the file's ATH can only raise the floor""", count=2)
ca.rep("""            const mAthPrice=coingeckoDataCache?.[moonToken]?.ath||ATH_PRICES[moonToken]||0;""",
       """            const mAthPrice=Math.max(coingeckoDataCache?.[moonToken]?.ath||0,ATH_PRICES[moonToken]||0);   // c22""")
ca.save()

# ================================================================= ledger.html — c17
le = Edit('ledger.html')
le.rep("""    const LEDGER_STALE_MS = 8 * 60 * 60 * 1000;""",
       """    const LEDGER_STALE_MS = 2.5 * 60 * 60 * 1000;   // c17 (Audit III): the pipeline is hourly — amber past two missed runs (was 8 h)""")
le.save()

# ================================================================= scripts/fetch-coingecko-data.js — c22
cg = Edit('scripts/fetch-coingecko-data.js')
cg.rep("""async function fetchPriceChanges(address, name) {
  console.log(`  Price changes: ${name} (${address.slice(0, 10)}...)`);
  try {
    const data = await fetchAPI(`/coins/pulsechain/contract/${address}`);
    if (!data?.market_data) return null;
    const md = data.market_data;""",
       """/* c22 (Audit III): CoinGecko's all-time high per token, from the same /coins call the price changes use. Published for PTGC
   only — UFO's ATH is the ORIGINAL contract's on purpose (index.html gotcha 0) and must not be overridden by the new listing. */
const ATH_SEEN = {};
async function fetchPriceChanges(address, name) {
  console.log(`  Price changes: ${name} (${address.slice(0, 10)}...)`);
  try {
    const data = await fetchAPI(`/coins/pulsechain/contract/${address}`);
    if (!data?.market_data) return null;
    const md = data.market_data;
    const ath = Number(md.ath && md.ath.usd);
    if (ath > 0) ATH_SEEN[name] = ath;""", done_marker='const ATH_SEEN = {};')
cg.rep("""function saveData(filename, data) {
  if (!fs.existsSync(CONFIG.outputDir)) fs.mkdirSync(CONFIG.outputDir, { recursive: true });
  const fp = path.join(CONFIG.outputDir, filename);
  fs.writeFileSync(fp, JSON.stringify(data, null, 2));
  console.log(`Saved: ${fp}`);
}""",
       """function saveData(filename, data) {
  if (!fs.existsSync(CONFIG.outputDir)) fs.mkdirSync(CONFIG.outputDir, { recursive: true });
  const fp = path.join(CONFIG.outputDir, filename);
  fs.writeFileSync(fp + '.tmp', JSON.stringify(data, null, 2));   // c22: tmp + rename — a job timeout never stages a half-written file
  fs.renameSync(fp + '.tmp', fp);
  console.log(`Saved: ${fp}`);
}""")
cg.rep("""      priceChanges: t.priceChanges,
      complete:     { ...t.complete }
    };""",
       """      priceChanges: t.priceChanges,
      complete:     { ...t.complete }
    };
    if (name === 'PTGC') {   // c22: the file's ATH never goes down (a CoinGecko hiccup must not lower "X's to ATH"); UFO is never written
      const ath = Math.max(ATH_SEEN.PTGC || 0, (p && p.ath) || 0);
      if (ath > 0) out.ath = ath;
    }""", done_marker="if (name === 'PTGC') {   // c22")
cg.rep("""  saveData('coingecko-data.json', {
    lastUpdated: timestamp,""",
       """  saveData('coingecko-data.json', {
    lastUpdated: new Date().toISOString(),   // c22: stamped at the SAVE, not the start of a ~3.5-min run (the histories keep `timestamp` for their hour bucket)""")
cg.save()

# ================================================================= scripts/pipeline-run.mjs — c19, c20
pr = Edit('scripts/pipeline-run.mjs')
pr.rep("""  { name: 'rpc',           steps: ['value-generated', 'burn-history', 'treasury', 'dao-buys', 'ufo-ptgc-burns', 'token-allocation', 'lv-snapshot', 'new-holders', 'swap-volume'] },""",
       """  // c19 (Audit III, 2026-10-07): value-generated LAST — it rescans the 90-day window every hour (~6 min) and held the eight quick
  // files behind it (burn-summary, treasury, dao-buys, new-holders, swap-volume all stamped 7–8 min after dispatch).
  { name: 'rpc',           steps: ['burn-history', 'treasury', 'dao-buys', 'ufo-ptgc-burns', 'token-allocation', 'lv-snapshot', 'new-holders', 'swap-volume', 'value-generated'] },""")
pr.rep("""const SUMMARY = path.join(process.env.RUNNER_TEMP || '/tmp', 'pipeline-summary.json');""",
       """const SUMMARY = path.join(process.env.RUNNER_TEMP || '/tmp', 'pipeline-summary.json');
const STATUS = 'data/pipeline-status.json';   // c20 (Audit III): the per-step record that outlives the runner (the freshness strip's file)""", done_marker="const STATUS = 'data/pipeline-status.json';")
pr.rep("""      for (const l of lines) { log(step, l); tail.push((isErr ? 'stderr: ' : '') + l); if (tail.length > 12) tail.shift(); }""",
       """      for (const l of lines) { log(step, l); tail.push((isErr ? 'stderr: ' : '') + l); if (tail.length > 12) tail.shift(); if (/::warning::/.test(l)) tail.carried = true; }   // c20: a carry-forward exits 0 — remember the warning""")
pr.rep("""    results[step] = { outcome: code === 0 ? 'success' : 'failure', code, seconds, tail, lane: lane.name };""",
       """    results[step] = { outcome: code === 0 ? 'success' : 'failure', code, seconds, tail, lane: lane.name, carried: !!tail.carried };""")
pr.rep("""  const summary = { startedAt: new Date(t0).toISOString(), seconds: Math.round((Date.now() - t0) / 1000), steps: results };
  fs.writeFileSync(SUMMARY, JSON.stringify(summary, null, 2));""",
       """  const summary = { startedAt: new Date(t0).toISOString(), seconds: Math.round((Date.now() - t0) / 1000), steps: results };
  fs.writeFileSync(SUMMARY, JSON.stringify(summary, null, 2));
  writeStatus(summary);""", done_marker='writeStatus(summary);')
pr.rep("""function report() {""",
       """/* c20 (Audit III, 2026-10-07): data/pipeline-status.json — what the job summary says, kept across runs. Per step: this run's
   outcome / seconds / why, and the last time it succeeded or failed (carried over from the previous file when the step was
   skipped or did not run), the failing step's last lines, and `carried` when the step printed a ::warning:: (dao-buys keeping
   the previous file exits 0 and used to show as a plain ✅). Readers: the freshness strip (roadmap g4), anyone curious. */
function writeStatus(summary) {
  let prev = {}; try { prev = JSON.parse(fs.readFileSync(STATUS, 'utf8')).steps || {}; } catch (e) {}
  const now = new Date().toISOString();
  const steps = {};
  for (const name of Object.keys(STEPS)) {
    const r = summary.steps[name], p = prev[name] || {};
    const s = { outcome: r ? r.outcome : 'not-run', seconds: r ? r.seconds : 0, lane: r ? r.lane : (LANES.find(l => l.steps.includes(name)) || {}).name };
    if (r && r.outcome === 'skipped' && r.why) s.why = r.why;
    s.lastSuccessAt = r && r.outcome === 'success' ? now : (p.lastSuccessAt || null);
    s.lastFailureAt = r && r.outcome === 'failure' ? now : (p.lastFailureAt || null);
    const said = (r && r.tail || []).filter(l => !/^(stderr: )?\\s+at /.test(l));   // the message, not the stack frames
    s.lastError = r && r.outcome === 'failure' ? said.slice(-2).join(' ⏎ ').slice(0, 300) : (r && r.outcome === 'success' ? null : (p.lastError || null));
    s.carried = !!(r && r.carried);
    steps[name] = s;
  }
  const env = process.env;
  const status = {
    schema: 1, generatedAt: now, seconds: summary.seconds,
    trigger: env.GITHUB_EVENT_NAME || 'local', only: env.ONLY || null, force: env.FORCE === 'true',
    runUrl: env.GITHUB_RUN_ID ? `${env.GITHUB_SERVER_URL || 'https://github.com'}/${env.GITHUB_REPOSITORY}/actions/runs/${env.GITHUB_RUN_ID}` : null,
    lanes: LANES.map(l => ({ name: l.name, steps: l.steps })),
    counts: { ok: Object.values(steps).filter(s => s.outcome === 'success').length, skipped: Object.values(steps).filter(s => s.outcome === 'skipped').length, failed: Object.values(steps).filter(s => s.outcome === 'failure').length, carried: Object.values(steps).filter(s => s.carried).length },
    steps
  };
  fs.writeFileSync(STATUS + '.tmp', JSON.stringify(status, null, 2)); fs.renameSync(STATUS + '.tmp', STATUS);
  console.log(`pipeline-run: wrote ${STATUS}`);
}

function report() {""", done_marker='function writeStatus(summary) {')
pr.rep("""    const icon = r.outcome === 'success' ? '✅' : r.outcome === 'failure' ? '❌' : '⏭️';
    const note = r.outcome === 'skipped' ? (r.why || '') : r.outcome === 'failure' ? `exit ${r.code} — ${(r.tail || []).slice(-2).join(' ⏎ ').replace(/\\|/g, '\\\\|').slice(0, 200)}` : '';""",
       """    const icon = r.outcome === 'success' ? (r.carried ? '⚠️' : '✅') : r.outcome === 'failure' ? '❌' : '⏭️';   // c20: ⚠️ = exited 0 but printed a ::warning:: (kept the previous file)
    const note = r.outcome === 'skipped' ? (r.why || '') : r.outcome === 'failure' ? `exit ${r.code} — ${(r.tail || []).slice(-2).join(' ⏎ ').replace(/\\|/g, '\\\\|').slice(0, 200)}` : (r.carried ? 'carried forward (see ::warning:: in the log)' : '');""")
pr.save()

# ================================================================= .github/workflows/data-pipeline.yml — c18, c20
wf = Edit('.github/workflows/data-pipeline.yml')
wf.rep("""    - cron: '7 * * * *'   # hourly at :07 — GitHub creates only ~4 of these a day (Oct 2026 run list); the
                          # real hourly beat is the ptgcapi Worker's cron, which dispatches this workflow
                          # (handover/ptgcapi-worker-v7.js). This schedule stays as the fallback.""",
       """    - cron: '37 * * * *'  # the FALLBACK, at :37 — the real hourly beat is the ptgcapi Worker's cron at :07, which dispatches
                          # this workflow (handover/ptgcapi-worker-v7.js). GitHub creates only ~4 of these a day, but when it
                          # does, the hour used to run twice (same minute as the Worker — three pairs on Oct 6–7, c18); now
                          # it is half an hour off AND the "Fresh enough?" step stands down when the last run is < 45 min old.""")
wf.rep("""      - name: Setup Node
        uses: actions/setup-node@v7
        with:
          node-version: '22'
""",
       """      - name: Setup Node
        uses: actions/setup-node@v7
        with:
          node-version: '22'

      # ---------- c18 (Audit III): on GitHub's own schedule, stand down when the Worker's dispatch already ran this hour ----------
      # The last run's stamp is data/pipeline-status.json (c20), else burn-summary.json's lastUpdated. Dispatches and manual
      # runs never stand down.
      - name: Fresh enough? (schedule events only)
        id: fresh
        if: github.event_name == 'schedule'
        run: |
          node -e '
            const fs = require("fs"); let at = null;
            try { at = Date.parse(JSON.parse(fs.readFileSync("data/pipeline-status.json", "utf8")).generatedAt); } catch (e) {}
            if (!at) { try { at = Date.parse(JSON.parse(fs.readFileSync("data/burn-summary.json", "utf8")).lastUpdated); } catch (e) {} }
            const min = at ? Math.round((Date.now() - at) / 60000) : null;
            const skip = min != null && min < 45;
            console.log(skip ? `last run ${min} min ago — the Worker is on the beat, standing down` : `last run ${min == null ? "unknown" : min + " min ago"} — running`);
            fs.appendFileSync(process.env.GITHUB_OUTPUT, `skip=${skip}\\n`);
          '
""", done_marker='Fresh enough? (schedule events only)')
wf.rep("""      - name: Run the pipeline (coingecko-key lane · rpc lane · pair-volume lane)
        id: run
        continue-on-error: true""",
       """      - name: Run the pipeline (coingecko-key lane · rpc lane · pair-volume lane)
        id: run
        if: steps.fresh.outputs.skip != 'true'
        continue-on-error: true""", done_marker="if: steps.fresh.outputs.skip != 'true'\n        continue-on-error: true")
wf.rep("""      - name: Commit if changed (rebase + retry)
        if: always()""",
       """      - name: Commit if changed (rebase + retry)
        if: always() && steps.fresh.outputs.skip != 'true'""", done_marker="Commit if changed (rebase + retry)\n        if: always() && steps.fresh")
wf.rep("""            data/swap-volume.json data/swap-volume-cache.json; do""",
       """            data/swap-volume.json data/swap-volume-cache.json \\
            data/pipeline-status.json; do""", done_marker='data/pipeline-status.json; do')
wf.rep("""      - name: Report step failures
        if: always()""",
       """      - name: Report step failures
        if: always() && steps.fresh.outputs.skip != 'true'""", done_marker="Report step failures\n        if: always() && steps.fresh")
wf.save()
print('audit3-p4: done')
