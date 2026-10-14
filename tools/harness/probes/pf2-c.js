(async()=>{const q=s=>[...document.querySelectorAll(s)];const S=ms=>new Promise(r=>setTimeout(r,ms));const out={};
out.chips=q('.pf2-chips button').map(b=>b.innerText.replace(/\n/g,' '));
const d=q('.pf2-chips button.dust')[0];if(d){d.click();await S(200);out.dustRows=q('.pf2-fr .t1').filter(e=>/\b10 PTGC/.test(e.innerText)).length;d.click();}
out.creatures=q('.pf2-crw span').map(e=>e.title);
out.counted=(document.querySelector('.pf2-tools .sum')||document.querySelector('.sum')||{}).innerText;
out.banner=(document.querySelector('.pf2-mm')||{}).innerText;
document.querySelector('.pf2-foldh').click();await S(300);out.sort=q('.pf2-bds button').map(b=>b.innerText);out.bdFirst=q('.pf2-bdt tbody tr').slice(0,3).map(t=>t.innerText.replace(/\n|\t/g,' | ').slice(0,80));
out.hiLo=q('.pf2-vhs .hl b').map(b=>b.innerText);
q('.pf2-edb')[0].click();for(let i=0;i<60&&!document.querySelector('.pf2-erw .sum');i++)await S(500);
out.edsel=q('.pf2-edsel button').map(b=>b.innerText+(b.className.includes('on')?'*':''));out.edsub=(document.querySelector('.pf2-erw .sub')||{}).innerText;
const b7=q('.pf2-edsel .pp button').find(b=>b.innerText==='7D');b7.click();for(let i=0;i<40&&!(document.querySelector('.pf2-erw .sum')&&q('.pf2-erw .dt tbody tr').length<=8);i++)await S(500);out.rows7=q('.pf2-erw .dt tbody tr').length;out.first7=q('.pf2-erw .dt tbody tr').slice(0,2).map(t=>t.innerText.replace(/\n|\t/g,' | ').slice(0,70));
const w2=q('.pf2-edsel .ws button')[2];if(w2){w2.click();for(let i=0;i<40&&!document.querySelector('.pf2-erw .sum');i++)await S(500);out.walletSub=(document.querySelector('.pf2-erw .sub')||{}).innerText;}
out.fn=(document.querySelector('.pf2-erw .fn')||{}).innerText.slice(-80);return out;})()
