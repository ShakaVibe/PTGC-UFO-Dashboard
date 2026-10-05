    /* ===== KPI REPORT v2 (2026-10-05) =====
       The KPI Report tab's card, rebuilt to Shaka's mock-up (design/kpi/README.md): his art as the plate, the dashboard's
       lit coin, the panel icons on the tiles, 30-day sparklines from the SAME series the v2 KPI tiles draw (useH2Series,
       H2Spark — real data, never a seeded shape), the sea-creature row and the v2 fire bar on the burn block.
       SAME NUMBERS as the card it replaces: every figure below is the old renderKPICard's maths (a19 honest-null: a read that
       failed is "—" / no badge, never 0; u5/u6: Value Generated from the one model, an unknown burn window is "—").
       One component for the active token AND the compare card (the other token): the series hook keys on the token. */
    const KP_ICONS={price:'logos/panels/dao-coins.webp',mcap:{PTGC:'logos/panels/lp-bars-gold.webp',UFO:'logos/panels/lp-bars-green.webp'},liq:'logos/panels/vg-droplet.webp',ratio:'logos/panels/pbu-pie.webp',vol:'logos/holders/nh-ic-net.webp',hold:'logos/holders/nh-ic-new.webp',vg:'logos/panels/vg-moneybag.webp',flame:'logos/panels/vg-flame.webp'};
    const KpSpark=({pts,color,id,label})=>(<div className="kp-sk" aria-hidden="true"><H2Spark pts={pts} color={color} id={id} label={label}/></div>);
    const KpChg=({v,pct=true,dec=1,na=false})=>{   // a change badge: null → nothing (unknown is not "0.0%"); 0 → "— 0"
      if(v==null||!isFinite(v))return null;
      if(v===0)return<span className="kp-chg na">— 0</span>;
      const up=v>=0;
      return<span className={`kp-chg ${up?'up':'dn'}`}><i aria-hidden="true">{up?'▲':'▼'}</i>{pct?`${Math.abs(v).toFixed(dec)}%`:`${up?'+':''}${fmt(Math.abs(v))}`}</span>;
    };
    const KpInfo=({label,children})=>(<InfoTip label={label} className="kp-info" trigger={<span className="kp-i" aria-hidden="true">i</span>}>{children}</InfoTip>);
    const KpTile=({t,k,icon,label,badge,value,pts,spark})=>(   // module scope (gotcha 14): a tile declared inside the card would remount — and re-request its icon — on every render
      <div className="kp-bx kp-t">
        <div className="r1"><img className="kp-ic" src={icon} alt="" aria-hidden="true"/><span className="kp-chip">{label}</span><span className="sp"></span>{badge}</div>
        <div className="r2"><H2Val className="v">{value}</H2Val>{pts===false?null:<KpSpark pts={pts} color={spark} id={`kp-${t}-${k}`} label={`${label} ${H2_DAYS} day history`}/>}</div>
      </div>);
    const KpiCardV2=({t,c,d,b,bp,h,hChange,pls,token,volumeByPeriod,valueGen7d,burnHistoryCache,vgPrices,otherVg})=>{
      const isPTGC=t==='PTGC';
      const spark=isPTGC?'#FFD24D':'#8DFF3A';   // the tiles' line colour — one per token (2026-10-01)
      const ser=useH2Series(t,d,!d);              // the 30-day series: mcap (price candles), vol, liq, ratio (lv-snapshots), hold (holder history)
      const priceChange=(d?.change!=null&&isFinite(d.change))?d.change:null;
      const plsRatioVal=(d?.price>0&&pls>0)?d.price/pls:null;
      const volChange=(t===token)
        ?(()=>{const v24=d?.vol||0;const v7=volumeByPeriod?.vol7d||0;const avg=v7/7;return(v24>0&&avg>0)?((v24-avg)/avg)*100:null;})()
        :(burnHistoryCache?.[t]?.changes?.volume24h??null);
      /* the window box is 30 DAYS since 2026-10-05 round 3 (Shaka: "let's move the burn box to a 30 day burn not 7 day") — was d7 */
      const burn7dKnown=bp!=null&&bp.d30!=null;
      const burn7dAmt=burn7dKnown?bp.d30:0;
      const burn7dUSD=burn7dAmt*(d?.price||0);
      const burnKnown=!!(b&&b.supply>0);
      const burnPctNum=b?.pct||0;
      const burnUSD=(d?.price>0&&b)?b.total*d.price:null;
      const liqMcapPct=(d?.mcap>0&&d?.liq!=null)?(d.liq/d.mcap*100):null;
      const today=new Date().toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'});
      /* u5: the active token's figure is the panel's own object. The OTHER token: PTGC = volume × fee (its only basis);
         UFO = the UFO dashboard's DELIVERED figure from the hourly snapshot (value-generated.json, the same file its panel
         reads — fetched by loadOtherToken, with the PLSX / WETH prices its LP buckets need), so the compare card prints what
         the UFO page prints and the tag is "7D"; only when that file is missing or > 48 h old does it fall back to
         volume × fee, tagged "7D EST" (Shaka, 2026-10-05: "why are we putting 7D EST on UFO's"). */
      const vg7=(t===token&&valueGen7d)?valueGen7d
        :(t==='UFO'&&otherVg?.ufoSnap)?computeValueGen({token:'UFO',cfg:c,period:'7d',periodVol:vol7dFromCache('UFO'),delivered:otherVg.ufoSnap.delivered,realizedFees:otherVg.ufoSnap.realizedFees,
            prices:{...(vgPrices||{}),UFO:(vgPrices?.UFO)||(d?.price>0?d.price:null),PLSX:(vgPrices?.PLSX)||otherVg.plsxPx||null,WETH:(vgPrices?.WETH)||otherVg.wethPx||null}})
        :computeValueGen({token:t,cfg:c,period:'7d',periodVol:(t===token?volumeByPeriod?.vol7d:vol7dFromCache(t)),delivered:null,realizedFees:null,prices:{},estimate:t!==token});
      const valueGenPending=!!vg7.pending;
      const valueGenUsd=vg7.total;
      const valueGenTag=vg7.basis==='volume'&&t==='UFO'?'7D EST':'7D';
      const creatures=getBurnC(burnPctNum,'Squid').filter(cr=>['Poseidon','Whale','Shark','Dolphin','Squid'].includes(cr.n));
      const burn7dPct=b?.supply>0?(burn7dAmt/b.supply)*100:0;
      const singleCreature7d=getSingleC(burn7dPct);
      const whaleP=getWhaleProgress(burnPctNum);
      const chCls=priceChange==null?'':priceChange>=0?'up':'dn';
      const priceSpark=priceChange==null?spark:priceChange>=0?'#3DE38A':'#FF4D5E';   // the price box follows the move (his mock); every other line is the token's
      return(
        <div className={`kp ${isPTGC?'':'ufo'}`} data-kpi-card={t}>
          <div className="kp-art" aria-hidden="true"></div><div className="kp-veil" aria-hidden="true"></div>
          <div className="kp-in">
            <div className="kp-hd">
              <LgCoin token={t}/>
              <div className="kp-ttl"><div className="n">{t}</div><div className="s">KPI REPORT</div><div className="ad" title={c.address}>{c.address}</div></div>
              <div className="kp-rt"><div className="d">{today}</div><div className="p">24H</div></div>
            </div>
            <div className="kp-bx kp-pr">
              <div className="l"><div className="lab"><img className="kp-ic" src={KP_ICONS.price} alt="" aria-hidden="true"/><span className="kp-chip">PRICE</span></div><H2Val className="v">{formatSubPrice(d?.price)}</H2Val></div>
              <div className={`ch ${chCls}`} title={priceChange==null?'24h change unavailable':undefined}>
                {priceChange==null?<span className="kp-chg na" style={{fontSize:'21px'}}>{'—'}</span>:<KpChg v={priceChange} dec={2}/>}
                <KpSpark pts={ser.mcap} color={priceSpark} id={`kp-${t}-price`} label={`Price ${H2_DAYS} day history`}/>
              </div>
              <div className="pls"><div className="tt">PLS RATIO<KpInfo label="PLS ratio">{EXPLAINERS.plsRatio(t)}</KpInfo></div><div className="v2">{plsRatioVal==null?'—':plsRatioVal.toFixed(2)}</div></div>
            </div>
            <div className="kp-g">
              <KpTile t={t} spark={spark} k="mcap" icon={KP_ICONS.mcap[t]||KP_ICONS.mcap.PTGC} label="MARKET CAP" badge={<KpChg v={priceChange}/>} value={fmtUSD(d?.mcap)} pts={ser.mcap}/>
              <KpTile t={t} spark={spark} k="liq" icon={KP_ICONS.liq} label="LIQUIDITY" badge={<KpInfo label="Liquidity">{EXPLAINERS.liquidity(t)}</KpInfo>} value={fmtUSD(d?.liq)} pts={ser.liq}/>
              <KpTile t={t} spark={spark} k="ratio" icon={KP_ICONS.ratio} label="LIQ/MC RATIO" badge={<KpInfo label="Liquidity to market cap ratio">{EXPLAINERS.liqMcap(t)}</KpInfo>} value={liqMcapPct==null?'—':`${liqMcapPct.toFixed(1)}%`} pts={ser.ratio}/>
              <KpTile t={t} spark={spark} k="vol" icon={KP_ICONS.vol} label="VOLUME" badge={volChange!=null?<KpChg v={volChange}/>:<KpInfo label="Volume">{EXPLAINERS.volume24h(t)}</KpInfo>} value={fmtUSD(d?.vol)} pts={ser.vol}/>
              <KpTile t={t} spark={spark} k="hold" icon={KP_ICONS.hold} label="HOLDERS" badge={<KpChg v={hChange} pct={false}/>} value={fmt(h)} pts={ser.hold}/>
              {/* no change badge here — the old card's "change" on this tile was the VOLUME change relabelled (2026-10-05); the tag sits by the ⓘ */}
              <KpTile t={t} spark={spark} k="vg" icon={KP_ICONS.vg} label="VALUE GEN" badge={<><span className="kp-chip tag">{valueGenTag}</span><KpInfo label="Value Generated">{EXPLAINERS.valueGenerated(t,c)}</KpInfo></>}
                value={valueGenPending?<span className="animate-pulse text-white/40" title="reading fees from chain…">{'—'}</span>:fmtUSD(valueGenUsd)} pts={false}/>
            </div>
            <div className="kp-bn">
              <div className="L">
                <div className="lab"><img className="kp-ic" src={KP_ICONS.flame} alt="" aria-hidden="true"/><span className="kp-chip">TOTAL BURNED</span><span style={{flex:1}}></span><KpInfo label="Total burned">{EXPLAINERS.totalBurned(t)}</KpInfo></div>
                <H2Val className="big">{burnKnown?fmt(b.total):'—'}<span>{t}</span></H2Val>
                <div className="usd">{burnKnown?fmtUSD(burnUSD):'—'}{burnKnown&&<span>{burnPctNum.toFixed(2)}%</span>}</div>
                <div className="kp-cre"><NhsFit className="kp-crefit">{creatures.length>0?creatures.map((cr,i)=><span key={i}><SeaIcon e={cr.e} size={38}/>x{cr.cnt}</span>):<span style={{color:'rgba(255,255,255,.45)',fontSize:'14px',fontWeight:500}}>{burnKnown?'Building…':'—'}</span>}</NhsFit></div>
                <div className="kp-bar"><P2Bar pct={burnKnown?whaleP.progress:0}/><span className="pct">{burnKnown?`${whaleP.progress.toFixed(1)}%`:'—'}</span><SeaIcon e={'\u{1F40B}'} size={34}/></div>
              </div>
              <div className="R">
                <div className="lab"><img className="kp-ic" src={KP_ICONS.flame} alt="" aria-hidden="true"/><span className="kp-chip sm">30D BURN</span></div>
                <div className="a">{burn7dKnown?fmtAbbr(burn7dAmt):'—'}</div><div className="tk">{t}</div><div className="us">{burn7dKnown?fmtUSD(burn7dUSD):'—'}</div>
                <div className="cr"><SeaIcon e={burn7dKnown?singleCreature7d.e:'\u{1F41A}'} size={68} className={burn7dKnown?'':'na'}/></div>
              </div>
            </div>
          </div>
        </div>);
    };

