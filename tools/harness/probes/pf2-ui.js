/* Portfolio v2 (2026-10-13): drive the hidden page — the dot both ways, the add capsule's message, a wallet switched off,
   the group filter, search, How it works, the two folds. Run with the preview flag set and ≥ 8 wallets. */
(async()=>{const S=ms=>new Promise(r=>setTimeout(r,ms));const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const typeIn=(el,v)=>{const set=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;set.call(el,v);el.dispatchEvent(new Event('input',{bubbles:true}));};
const out={};
out.v2At0=!!$('.pf2');
$('.pf2-dotbtn').click();await S(400);out.afterDot_classic=!$('.pf2')&&!!$('input[placeholder^="Paste wallet address"]');out.flagCleared=localStorage.getItem('grays_pf_v2_preview');
$('.pf2-dotbtn').click();await S(400);out.backToV2=!!$('.pf2');out.flagSet=localStorage.getItem('grays_pf_v2_preview');
out.cards=$$('.pf2-wc').length;out.sum=$('.pf2-tools .sum').textContent;
typeIn($('.pf2-add input.ad'),'0x123');await S(100);$('.pf2-addb').click();await S(200);out.addMsg=($('.pf2-addmsg')||{}).textContent;
$$('.pf2-tg')[0].click();await S(300);out.sumAfterOff=$('.pf2-tools .sum').textContent;out.firstOff=$$('.pf2-wc')[0].className;out.total=$('.pf2-st.t .v').textContent;
$$('.pf2-tg')[0].click();await S(300);
const lp=$$('.pf2-seg button').find(b=>b.textContent==='LP');lp.click();await S(200);out.lpCards=$$('.pf2-wc').length;
$$('.pf2-seg button')[0].click();await S(200);
typeIn($('.pf2-srch input'),'mando');await S(200);out.searchCards=$$('.pf2-wc').map(c=>c.querySelector('.nm').textContent);
typeIn($('.pf2-srch input'),'zzz');await S(200);out.noMatch=($('.pf2-empty')||{}).textContent;typeIn($('.pf2-srch input'),'');await S(200);
$('.pf2-how').click();await S(200);out.how=!!$('.pf2-modal');$('.pf2-modal .x').click();await S(200);out.howClosed=!$('.pf2-modal');
const f=$$('.pf2-foldh');f[0].click();await S(200);out.bdRows=$$('.pf2-tbl tbody tr').length;
f[1].click();await S(200);out.mmInputs=$$('.pf2-mmg input').length;out.mmOn=f[1].getAttribute('aria-expanded');
$$('.pf2-mmb button')[0].click();await S(300);out.mmBanner=($('.pf2-mm')||{}).textContent;out.totalAth=$('.pf2-st.t .v').textContent;out.tileSub=$('.pf2-st.t .s').textContent;
$$('.pf2-mmb button')[1].click();f[1].click();await S(200);
$$('.pf2-ext button')[0].click();await S(200);out.det=!!$('.pf2-det');
$$('.pf2-lgbh .lnk')[0].click();await S(300);out.leaguesModal=document.body.innerText.includes('League')&&$$('.fixed.inset-0').length;
return JSON.stringify(out,null,1);})()
