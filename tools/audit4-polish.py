#!/usr/bin/env python3
"""Audit IV P-5 + P-11 (2026-10-24, Shaka: "5 yes"). Idempotent, from the repo root:
    python3 tools/audit4-polish.py      (twice: the second run must print "0 edit(s)")
  P-5  index.html loads Chart.js (69 KB gz) only when a chart opens — the DAO Buys window, its share card and cadence strip,
       and the Affiliates buyer-distribution pie — via loadChartJs() (same file, same SRI as the old <script> tag) and the
       useChartJs() hook. Nothing on the first screen draws a chart. calculators.html keeps its `defer` tag: its six charts sit
       in effects with long shared dependency lists, and defer already keeps the file off the paint path.
  P-11 the Home BUY / SELL buttons and the dashboards' BUY button pulsed a BOX-SHADOW (repainted every frame, all day). The
       outer glow is now static at the pulse's middle and the pulse is an inset glow on a ::before whose OPACITY animates
       (composited, no repaint). Reduced motion stops it, as before.
"""
import hashlib
n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1
IX = 'index.html'

# ============================ P-5 ============================
TAG = '  <script defer src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.js" integrity="sha384-dug+JxfBvklEQdJ4AYuBBAIScUz0bVN73xpy273gcAwHjb3qI0fXmuYNaNfdyYJG" crossorigin="anonymous"></script>\n'
edit(IX, TAG, '  <!-- Audit IV P-5 (2026-10-24): Chart.js is loaded on demand by loadChartJs() (same file, same SRI) when a chart opens -->\n')
edit(IX, "    const HTML2CANVAS_SRC='https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';",
"""    /* Audit IV P-5 (2026-10-24): Chart.js on demand — no chart is on the first screen, so the 69 KB gz file waits for the first
       window that draws one. useChartJs() starts the load on mount and re-renders when it lands; each chart effect lists it. */
    const CHARTJS_SRC='https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.js';
    const CHARTJS_SRI='sha384-dug+JxfBvklEQdJ4AYuBBAIScUz0bVN73xpy273gcAwHjb3qI0fXmuYNaNfdyYJG';
    let _cjsP=null;
    const loadChartJs=()=>{
      if(window.Chart)return Promise.resolve(window.Chart);
      if(_cjsP)return _cjsP;
      _cjsP=new Promise((res,rej)=>{
        const el=document.createElement('script');
        el.src=CHARTJS_SRC;el.integrity=CHARTJS_SRI;el.crossOrigin='anonymous';el.async=true;
        el.onload=()=>window.Chart?res(window.Chart):rej(new Error('Chart.js did not initialise'));
        el.onerror=()=>{_cjsP=null;rej(new Error('could not load Chart.js'));};
        document.head.appendChild(el);
      });
      return _cjsP;
    };
    const useChartJs=()=>{const[ok,setOk]=useState(()=>!!window.Chart);
      useEffect(()=>{if(ok)return;let live=true;loadChartJs().then(()=>{if(live)setOk(true);}).catch(e=>console.warn(e.message));return()=>{live=false;};},[]);
      return ok;};
    const HTML2CANVAS_SRC='https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';""")
# the four chart sites
edit(IX, "      const cad=React.useMemo(()=>computeDaoBuysCadence(view),[view]);\n",
         "      const cad=React.useMemo(()=>computeDaoBuysCadence(view),[view]);\n      const cjsOk=useChartJs();   // P-5\n")
edit(IX, "      },[cad,phone,share]);", "      },[cad,phone,share,cjsOk]);")
edit(IX, """      const ref=useRef(null),inst=useRef(null);
      useEffect(()=>{
        if(!ref.current||!window.Chart)return;
        const ctx=ref.current.getContext('2d');
        try{inst.current=new window.Chart(ctx,buildDaoBuysChartConfig({view,unit,logY,phone:false,hex,logo:cfg.logo,share:true,ctx}));}""",
"""      const ref=useRef(null),inst=useRef(null);
      const cjsOk=useChartJs();   // P-5
      useEffect(()=>{
        if(!ref.current||!window.Chart)return;
        const ctx=ref.current.getContext('2d');
        try{inst.current=new window.Chart(ctx,buildDaoBuysChartConfig({view,unit,logY,phone:false,hex,logo:cfg.logo,share:true,ctx}));}""")
edit(IX, "      },[view,unit,logY]);", "      },[view,unit,logY,cjsOk]);")
edit(IX, """      useEffect(()=>{
        if(!view||!canvasRef.current||!window.Chart)return;""", """      const cjsOk=useChartJs();   // P-5
      useEffect(()=>{
        if(!view||!canvasRef.current||!window.Chart)return;""")
edit(IX, "      },[view,logY]);", "      },[view,logY,cjsOk]);")
edit(IX, """      // Chart
      useEffect(()=>{
        if(!chartRef.current||sortedWallets.length===0)return;""", """      // Chart
      const cjsOk=useChartJs();   // P-5
      useEffect(()=>{
        if(!chartRef.current||sortedWallets.length===0||!window.Chart)return;""")
edit(IX, "      },[sortedWallets,metric]);", "      },[sortedWallets,metric,cjsOk]);")

# ============================ P-11 ============================
edit(IX, "box-shadow:0 0 20px var(--g),inset 0 1px 0 rgba(255,255,255,0.15);animation:buyGlow 3s ease-in-out infinite}\n"
         "    @keyframes buyGlow{0%,100%{box-shadow:0 0 18px var(--g),inset 0 1px 0 rgba(255,255,255,0.15)}50%{box-shadow:0 0 34px var(--g),0 0 3px var(--g),inset 0 1px 0 rgba(255,255,255,0.22)}}",
         "box-shadow:0 0 26px var(--g),inset 0 1px 0 rgba(255,255,255,0.18)}\n"
         "    /* Audit IV P-11 (2026-10-24): the pulse was a box-shadow keyframe (a repaint every frame while the page is open); now the outer glow is\n"
         "       static at the pulse's middle and the pulse is an inset glow whose OPACITY animates on a ::before (composited) */\n"
         "    .buy-btn::before{content:'';position:absolute;inset:0;border-radius:inherit;pointer-events:none;box-shadow:inset 0 0 14px var(--g),0 0 0 1px var(--g);opacity:0;animation:buyGlowO 3s ease-in-out infinite}\n"
         "    @keyframes buyGlowO{0%,100%{opacity:0}50%{opacity:1}}")
edit(IX, ".buy-btn,.buy-btn::after{animation:none!important}", ".buy-btn,.buy-btn::before,.buy-btn::after{animation:none!important}")
edit(IX, "box-shadow:0 0 18px var(--hc-glow2),inset 0 0 18px var(--hc-glow2),inset 0 1px 0 rgba(255,255,255,.12);animation:hcGlow 3s ease-in-out infinite;transition:background .2s ease,transform .2s ease}",
         "box-shadow:0 0 23px var(--hc-glow2),inset 0 0 18px var(--hc-glow2),inset 0 1px 0 rgba(255,255,255,.14);transition:background .2s ease,transform .2s ease}   /* P-11: static — the pulse is the ::before's opacity */\n"
         "    .hc-buy::before{content:'';position:absolute;inset:0;border-radius:inherit;pointer-events:none;box-shadow:inset 0 0 22px var(--hc-glow);opacity:0;animation:hcGlowO 3s ease-in-out infinite}\n"
         "    @keyframes hcGlowO{0%,100%{opacity:0}50%{opacity:.9}}")
edit(IX, "    @keyframes hcGlow{0%,100%{box-shadow:0 0 16px var(--hc-glow2),inset 0 0 16px var(--hc-glow2),inset 0 1px 0 rgba(255,255,255,.12)}50%{box-shadow:0 0 30px var(--hc-glow),inset 0 0 22px var(--hc-glow2),inset 0 1px 0 rgba(255,255,255,.16)}}\n", "    /* (P-11: the hcGlow box-shadow keyframes went with the pulse — see .hc-buy::before) */\n")
edit(IX, ".hc-buy,.hc-buy::after{animation:none!important}", ".hc-buy,.hc-buy::before,.hc-buy::after{animation:none!important}")

sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'audit4-polish: {n} edit(s); index.html {sha(IX)}')
