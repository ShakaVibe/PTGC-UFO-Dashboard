#!/usr/bin/env python3
r"""Audit IV batch 3 (2026-10-23) — e17 + e24 + e25 (phone first screen), e12 (calculators' UFO reward share), e18 (defer the CDN
scripts), e20 + e21 + e23 (deploy safety net: compile check, boot-fail message, pipeline honesty). Idempotent, from the repo root:
    python3 tools/audit4-batch3.py      (twice: the second run must print "0 edit(s)")
then `cd tools/harness && npm run css` and commit tw.css (`?v=4` on the five pages). The three workflow files are written by tools/audit4-ci.py (run it on
the Mac: the file bridge refuses .github/workflows/*).
"""
import hashlib, re, subprocess, sys
n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    if s.count(old) != count:   # the files sometimes spell a character as a JS escape (\\uXXXX); match either spelling
        esc = ''.join(c if ord(c) < 128 else '\\u%04x' % ord(c) for c in old)
        if s.count(esc) == count: old = esc
    if s.count(old) != count and count == 1:
        pat = '\n'.join('[ \t]*' if not ln.strip() else re.escape(ln) for ln in old.split('\n'))
        m = list(re.finditer(pat, s))
        if len(m) == 1: old = m[0].group(0)
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:100]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1

IX, PF, CA, LE, CH = 'index.html', 'portfolio.html', 'calculators.html', 'ledger.html', 'charts.html'

# ======================================= e17 — the disclaimer: the button never scrolls away ====================================
edit(IX, r'''          <div className="bg-[#111] border border-yellow-500/30 rounded-2xl max-w-lg w-full p-6 shadow-2xl" style={{maxHeight:'90vh',overflowY:'auto'}}>
            <div className="text-center mb-6">''', r'''          {/* Audit IV e17 (2026-10-23): the text scrolls and the Accept button sits in a footer that never scrolls away — on a phone it
             used to be ~360 px below the fold of ONE scroll box, with no cue. Wording unchanged, so DISCLAIMER_VERSION stays. */}
          <div className="bg-[#111] border border-yellow-500/30 rounded-2xl max-w-lg w-full shadow-2xl flex flex-col overflow-hidden max-h-[90vh]" style={{maxHeight:'90dvh'}}>
            <div className="flex-1 min-h-0 overflow-y-auto p-6 pb-2">
            <div className="text-center mb-6">''')
edit(IX, r'''agree to use it entirely at your own discretion.
              </p>
            </div>

            <div className="flex flex-col gap-3">''', r'''agree to use it entirely at your own discretion.
              </p>
            </div>
            </div>
            <div className="flex flex-col gap-3 px-6 pt-4 pb-6 border-t border-white/10 shrink-0">''')

# ======================================= e25 — Leagues toggle + Socials column header ============================================
edit(IX, r'''    .lg-hd .tg{position:absolute;top:14px;left:50%;transform:translateX(-50%);z-index:2}''',
         r'''    .lg-hd .tg{position:absolute;top:14px;left:10px;right:10px;display:flex;justify-content:center;z-index:2;pointer-events:none}.lg-hd .tg>*{pointer-events:auto}   /* Audit IV e25: full width — `left:50%` capped the toggle at half the header and the two labels ran together at 390 */''')
edit(IX, r'''    .sh-hd .go svg{width:16px;height:16px}''', r'''    .sh-hd .go svg{width:16px;height:16px}
    /* Audit IV e25 (2026-10-23): at 901–1199 px (three columns on small laptops / iPad landscape) the Combined header — 120 px logo +
       27 px Orbitron name + the chevron — ran 15–81 px past its column ("Combine", the chevron clipped). Smaller there only. */
    .sh-hd>div{min-width:0}
    @media(min-width:901px) and (max-width:1199px){.sh-hd{gap:10px}.sh-hd .lg{width:70px;height:70px}.sh-hd .lg2{width:72px;height:66px;transform:scale(1.3)}.sh-hd .nm{font-size:clamp(16px,1.85vw,23px)}.sh-hd .ln{font-size:13px}}''')

# ======================================= e24 — calculators on a phone ===========================================================
edit(CA, r'''              <div className={`flex gap-5 ${isSingle?'justify-center':'items-stretch'}`}>''',
         r'''              <div className={`flex flex-col sm:flex-row gap-5 ${isSingle?'justify-center':'items-stretch'}`}>{/* Audit IV e24: the two token cards stack under 640 px (side by side the Fee badge was printed over the token name) */}''')
edit(CA, r'''                  <div className="flex items-center gap-4 mb-3 justify-center">
                    <div className="relative w-72">''', r'''                  <div className="flex flex-col sm:flex-row items-center gap-3 sm:gap-4 mb-3 justify-center">{/* Audit IV e24: amount box full width, the modes under it, on a phone ("Split" was clipped) */}
                    <div className="relative w-full sm:w-72">''')
edit(CA, r'''                  <div className="flex items-center gap-3">
                    <span className="text-white/30 text-sm font-semibold uppercase">My Bag:</span>''', r'''                  <div className="flex flex-wrap items-center gap-3">{/* Audit IV e24: "Load from Portfolio →" wraps instead of being cut at 390 */}
                    <span className="text-white/30 text-sm font-semibold uppercase">My Bag:</span>''')

# ======================================= e12 — calculators: the Portfolio's reward-eligible UFO supply ==========================
edit(CA, r'''    const BURN_ADDRESS='0x0000000000000000000000000000000000000369';''', r'''    const BURN_ADDRESS='0x0000000000000000000000000000000000000369';
    /* Audit IV e12 (2026-10-23): UFO's "share of every holder reward" divides by the SAME reward-eligible supply as the Portfolio
       (portfolio.html pfUfoEligible, measured on chain 2026-10-15): total supply − the burn − the token contract − the excluded
       wallet − the 13 PulseX pools, read in one batched call. It used to be circulating − DexScreener's tokens-in-LP, which kept the
       excluded wallet (~71.8B UFO) in the denominator, so every UFO reward projection was ~9 % low. Keep this list = PF_UFO_EXCL.
       A failed read uses the newest cached value from either page (≤ 24 h), then the old estimate — never a $0. */
    const CALC_UFO_EXCL={wallets:['0x92DD8E86fDb206fA41E451398A9f03fbd36d574D'],
      pools:['0x9aBD84EAE174c6cf7FBf67cBb550930845866e05','0x145BC3a8a5EC0C84061511a5DB6023360caDF654','0xE221e6fC30e5787F0d551f980B4da1055D832A03','0x1693b411Ca2dF63C15292ad1fCcF8Ff06a643b25','0xF7d75A0BbE1EF90CDA220DEa7450105a956Abf19','0x3fE128f60797E371aAF43c038955bb37356d1e8a','0xe61AA9A9B7a13cEEdEaa8D26BFf5222003A40634','0xc4434600F1f263Ee38c38dfe32c8DEf8c0047C0b','0x6e60E4fA05e1f2a4Ab5706B17b52ddd8EA92372D','0x1a813F71324C02a57e02a0b79460Bb2dD675ae02','0x50771B2B774541937D657144e034D7e2215542AD','0x865bEbb526a61d5aA75A379Ea84fa8d710eA25be','0x9Dc651b1435eAD1cC2dDf8745e9BaB7A3C94f1ca']};
    const CALC_UFO_ELIG_LS='grays_calc_ufo_elig_v1',PF_UFO_ELIG_LS_SHARED='grays_pf_ufo_elig';let calcUfoEligP=null,calcUfoEligMem=null;
    const calcUfoEligCached=()=>{let best=null;[CALC_UFO_ELIG_LS,PF_UFO_ELIG_LS_SHARED].forEach(k=>{try{const o=JSON.parse(localStorage.getItem(k)||'null');
      if(o&&o.elig>0&&o.at>0&&Date.now()-o.at<24*3600e3&&(!best||o.at>best.at))best={elig:o.elig,at:o.at};}catch(e){}});return best;};
    const calcUfoEligible=()=>{
      if(calcUfoEligMem&&Date.now()-calcUfoEligMem.at<10*60e3)return Promise.resolve(calcUfoEligMem);
      if(calcUfoEligP)return calcUfoEligP;
      const UFO=TOKENS.UFO.address,addrs=[BURN_ADDRESS,UFO,...CALC_UFO_EXCL.wallets,...CALC_UFO_EXCL.pools];
      const call=(id,data)=>({jsonrpc:'2.0',id,method:'eth_call',params:[{to:UFO,data},'latest']});
      const body=[call(0,'0x18160ddd'),...addrs.map((a,i)=>call(i+1,'0x70a08231'+a.slice(2).toLowerCase().padStart(64,'0')))];
      calcUfoEligP=rpcFetch(body,10000).then(res=>{if(!Array.isArray(res))throw new Error('batch failed');const by={};
          res.forEach(r=>{by[r.id]=r&&r.result&&r.result!=='0x'?Number(BigInt(r.result))/1e18:null;});
          const supply=by[0];if(!(supply>0))throw new Error('no supply');let excl=0;
          addrs.forEach((a,i)=>{const v=by[i+1];if(v==null)throw new Error('no balance');excl+=v;});
          const o={elig:supply-excl,at:Date.now()};calcUfoEligMem=o;try{localStorage.setItem(CALC_UFO_ELIG_LS,JSON.stringify(o));}catch(e){}return o;})
        .catch(()=>calcUfoEligCached())
        .finally(()=>{calcUfoEligP=null;});
      return calcUfoEligP;};
    const useCalcUfoElig=()=>{const[e,setE]=useState(()=>{const o=calcUfoEligCached();return o?o.elig:null;});
      useEffect(()=>{let live=true;calcUfoEligible().then(o=>{if(live&&o)setE(o.elig);});return()=>{live=false;};},[]);return e;};''')
edit(CA, r'''      const supplyUnknown=circulatingSupply==null;''', r'''      const supplyUnknown=circulatingSupply==null;
      const ufoElig=useCalcUfoElig();   // Audit IV e12: the Portfolio's reward-eligible UFO supply (null until read)''')
edit(CA, r'''            const eligibleSupply=circSupply==null?null:(isPTGC?circSupply:Math.max(circSupply-totalUFOInLP,1));''',
         r'''            const eligibleSupply=circSupply==null?null:(isPTGC?circSupply:(ufoElig>0?ufoElig:Math.max(circSupply-totalUFOInLP,1)));   // e12: the old LP-only estimate only while the eligible supply has never been read''')
edit(CA, r'''            const ufoEligibleSupply=ufoCirc==null?null:Math.max(ufoCirc-ufoTokensInLP,1);''',
         r'''            const ufoEligibleSupply=ufoCirc==null?null:(ufoElig>0?ufoElig:Math.max(ufoCirc-ufoTokensInLP,1));   // e12''')

# ======================================= e18 — defer the CDN scripts (not charts.html: its plain scripts call Chart while parsing) ==
for page in (IX, PF, CA, LE):
    for lib in ('https://unpkg.com/react@18.3.1/', 'https://unpkg.com/react-dom@18.3.1/', 'https://unpkg.com/@babel/standalone@7.26.4/', 'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/'):
        s = open(page, encoding='utf-8').read()
        if f'<script src="{lib}' in s or f'<script defer src="{lib}' in s:
            edit(page, f'<script src="{lib}', f'<script defer src="{lib}')

# ======================================= e21 — a page that never renders says so ===============================================
BOOT_JS = r'''  <script>
    /* Audit IV e21 (2026-10-23): when the page never renders — a compile error after a bad edit, or the CDN blocked — the static
       shell said "LOADING…" for ever. A Babel / syntax error, or 20 s after the page has loaded with the shell still in place,
       swaps that line for a message. React's first render replaces the whole shell, so a working page never shows it. */
    (function(){var done=false;function stuck(){if(done)return;var m=document.getElementById('boot-msg');if(!m||!document.querySelector('#root [data-boot]'))return;done=true;
      m.textContent='This is taking longer than it should. Please reload the page — if it keeps happening, try again in a few minutes.';m.style.cssText='margin:0;max-width:30em;font-size:14px;line-height:1.5;color:#E8C044';}
      window.addEventListener('error',function(e){if(/SyntaxError|Unexpected token|Babel/i.test(String(e&&e.message||'')))setTimeout(stuck,300);});
      window.addEventListener('load',function(){setTimeout(stuck,20000);});})();
  </script>
'''
SHELL = r'''<div data-boot="1" style="min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;background:#000;color:#fff;font-family:system-ui,-apple-system,sans-serif;text-align:center;padding:24px;box-sizing:border-box"><div style="font-size:20px;font-weight:800;letter-spacing:.1em;color:#E8C044">THE GRAYS DASHBOARD</div><p id="boot-msg" style="margin:0;font-size:12px;letter-spacing:.14em;color:rgba(255,255,255,.35)">LOADING…</p></div>'''
edit(IX, r'''    <div style="min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;''',
         r'''    <div data-boot="1" style="min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;''')
edit(IX, r'''      <p style="margin:6px 0 0;font-size:12px;letter-spacing:.14em;color:rgba(255,255,255,.35)">LOADING…</p>''',
         r'''      <p id="boot-msg" style="margin:6px 0 0;font-size:12px;letter-spacing:.14em;color:rgba(255,255,255,.35)">LOADING…</p>''')
edit(IX, r'''  <script>
    /* Silence internal diagnostics for regular users;''', BOOT_JS + r'''  <script>
    /* Silence internal diagnostics for regular users;''')
for page in (PF, CA, LE):
    edit(page, '  <div id="root"></div>\n', '  <div id="root">' + SHELL + '</div>   <!-- Audit IV e21: a static shell until React mounts (render replaces it) -->\n' + BOOT_JS)

# ======================================= harness: keep `defer`, wait for the real mount, print errors as JSON ===================
RJ = 'tools/harness/run.js'
for lib, local in (('react@18\\.3\\.1\\/umd\\/react\\.production\\.min\\.js', '__react.js'), ('react-dom@18\\.3\\.1\\/umd\\/react-dom\\.production\\.min\\.js', '__react-dom.js'), ('@babel\\/standalone@7\\.26\\.4\\/babel\\.min\\.js', '__babel.js')):
    edit(RJ, f'''.replace(/<script src="https:\\/\\/unpkg\\.com\\/{lib}"[^>]*><\\/script>/,'<script src="/{local}"></script>')''',
             f'''.replace(/<script (defer )?src="https:\\/\\/unpkg\\.com\\/{lib}"[^>]*><\\/script>/,'<script $1src="/{local}"></script>')''')
edit(RJ, r'''.replace(/<script src="https:\/\/cdn\.jsdelivr\.net\/npm\/chart\.js@4\.4\.1\/dist\/chart\.umd\.js"[^>]*><\/script>/,'<script src="/__chart.js"></script>')''',
         r'''.replace(/<script (defer )?src="https:\/\/cdn\.jsdelivr\.net\/npm\/chart\.js@4\.4\.1\/dist\/chart\.umd\.js"[^>]*><\/script>/,'<script $1src="/__chart.js"></script>')   // Audit IV e18: the pages defer the CDN scripts; keep it''')
edit(RJ, r'''const r=document.querySelector('#root');return r?r.children.length>0:true;''',
         r'''const r=document.querySelector('#root');return r?(r.children.length>0&&!r.querySelector('[data-boot]')):true;''', count=2)
edit(RJ, r'''  console.log('errors:',errors.length?errors.slice(0,8):'none');''', r'''  console.log('errors:',errors.length?errors.slice(0,8):'none');
  console.log('ERRORS_JSON',JSON.stringify(errors));   // Audit IV e20: one parseable line for ci-mount.js''')

# ======================================= e23 — pipeline honesty ===============================================================
edit('scripts/build-charts-data.js', r'''else if (prev[t.sym]) { tokens[t.sym] = { ...prev[t.sym], carriedForward: true }; console.warn(`  → kept previous ${t.sym} series`); }''',
     r'''else if (prev[t.sym]) { tokens[t.sym] = { ...prev[t.sym], carriedForward: true }; console.warn(`::warning::charts ${t.sym} carried forward — kept the previous series`); }''')
edit('scripts/build-charts-data.js', r'''else if (prev[m.sym]) { tokens[m.sym] = { ...prev[m.sym], carriedForward: true }; console.warn(`  → kept previous ${m.sym} series`); }''',
     r'''else if (prev[m.sym]) { tokens[m.sym] = { ...prev[m.sym], carriedForward: true }; console.warn(`::warning::charts ${m.sym} carried forward — kept the previous series`); }''')
edit('scripts/build-charts-data.js', r'''      if (prev[t.sym]) { tokens[t.sym] = { ...prev[t.sym], carriedForward: true }; }''',
     r'''      if (prev[t.sym]) { tokens[t.sym] = { ...prev[t.sym], carriedForward: true }; console.warn(`::warning::charts ${t.sym} carried forward after an error`); }''')
edit('scripts/build-charts-data.js', r'''      if (prev[m.sym]) { tokens[m.sym] = { ...prev[m.sym], carriedForward: true }; }''',
     r'''      if (prev[m.sym]) { tokens[m.sym] = { ...prev[m.sym], carriedForward: true }; console.warn(`::warning::charts ${m.sym} carried forward after an error`); }''')
edit('scripts/build-charts-intraday.js', r'''        console.warn(`  → kept previous ${job.sym} [${tier}] series`);''',
     r'''        console.warn(`::warning::charts-intraday ${job.sym} [${tier}] carried forward — kept the previous series`);''')
edit('scripts/build-pair-volume.mjs', r'''    out[p.addr] = { n: p.name, v, carried: prev.generatedAt }; carried++; return true;''',
     r'''    out[p.addr] = { n: p.name, v, carried: prev.generatedAt }; carried++; console.warn(`::warning::pair-volume ${p.name} carried forward from ${prev.generatedAt}`); return true;''')
edit('scripts/fetch-coingecko-data.js', r'''      console.warn(`⚠ ${name} ${figure}: kept the previous value (measured ${carriedFrom[figure] || 'unknown'}).`);''',
     r'''      console.warn(`::warning::coingecko ${name} ${figure}: kept the previous value (measured ${carriedFrom[figure] || 'unknown'}).`);''')
edit('scripts/fetch-coingecko-data.js', r'''    console.warn('\n⚠ WARNING: PTGC returned 0 pools / $0 liquidity — skipping PTGC data, keeping previous.');''',
     r'''    console.warn('\n::warning::coingecko PTGC returned 0 pools / $0 liquidity — skipping PTGC data, keeping previous.');''')
edit('scripts/fetch-coingecko-data.js', r'''    console.warn('\n⚠ WARNING: UFO returned 0 pools / $0 liquidity — skipping UFO data, keeping previous.');''',
     r'''    console.warn('\n::warning::coingecko UFO returned 0 pools / $0 liquidity — skipping UFO data, keeping previous.');''')
edit('scripts/build-value-generated.mjs', r'''  const burnPeriodsOut = burnPeriods || (prev && prev.burnPeriods && prev.burnPeriods.UFO ? { ...prev.burnPeriods.UFO, carriedForward: true } : null);''',
     r'''  const burnPeriodsOut = burnPeriods || (prev && prev.burnPeriods && prev.burnPeriods.UFO ? { ...prev.burnPeriods.UFO, carriedForward: true } : null);
  if (!burnPeriods && burnPeriodsOut) console.warn('::warning::value-generated UFO burn periods carried forward (the chain scan failed)');   // Audit IV e23''')
# an existing file that cannot be read is FATAL (it used to be treated as "first run" and replaced by a one-row file)
edit('scripts/lv-snapshot.js', r'''    catch (e) { console.warn('Could not parse existing snapshots, starting fresh'); snapshots = []; }''',
     r'''    catch (e) { console.error(`lv-snapshots.json exists but cannot be read (${e.message}) — refusing to replace the only copy with a one-row file`); process.exit(1); }   // Audit IV e23''')
edit('scripts/fetch-burn-history.js', r'''        console.log(`    ERROR loading ${filePath}: ${e.message}`);
        console.log(`    Stack: ${e.stack}`);''', r'''        console.log(`    ERROR loading ${filePath}: ${e.message}`);
        console.log(`    Stack: ${e.stack}`);
        throw new Error(`cannot read ${filePath} — refusing to build totals from a partial burn archive`);   // Audit IV e23 (it was skipped silently)''')
edit('scripts/fetch-burn-history.js', r'''  } catch (e) {
    console.log('Creating new holder history file...');
  }''', r'''  } catch (e) {
    console.error(`holder-history.json exists but cannot be read (${e.message}) — refusing to replace the only copy`);   // Audit IV e23
    process.exit(1);
  }''')
edit('scripts/fetch-burn-history.js', r'''    // Keep last 365 days of data (1 year)
    const maxSnapshots = 365;
    if (holderHistory.snapshots.length > maxSnapshots) {
      const removed = holderHistory.snapshots.length - maxSnapshots;
      holderHistory.snapshots = holderHistory.snapshots.slice(-maxSnapshots);
      console.log(`  Trimmed ${removed} old snapshots, keeping last ${maxSnapshots}`);
    }''', r'''    // Audit IV e23 (2026-10-23): NO trim — this daily holder count is the one record the chain cannot give back (~37 KB a year).''')
edit('scripts/fetch-ufo-ptgc-burns.js', r'''    console.log('Cache load failed, starting fresh:', e.message);''',
     r'''    console.error('Cache exists but cannot be read — refusing a full rescan from launch (it outlasts the job timeout):', e.message);   // Audit IV e23
    process.exit(1);''')

# tw.css gains the sm:flex-row / sm:w-72 / … utilities above → bump the cache key so a browser holding v3 fetches the new build
for p in ('index.html', 'portfolio.html', 'calculators.html', 'charts.html', 'ledger.html'):
    edit(p, 'href="tw.css?v=3"', 'href="tw.css?v=4"')
out = subprocess.run([sys.executable, 'tools/pf-v2.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'audit4-batch3: {n} edit(s), index {sha(IX)}, portfolio {sha(PF)}, calculators {sha(CA)}, ledger {sha(LE)}')
