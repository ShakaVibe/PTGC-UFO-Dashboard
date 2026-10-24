// LEAGUE HISTORY: a finger touch at 30 % across the big chart (pointerType touch) → the readout row's text, and whether LATEST shows
(()=>{const s=document.querySelector('.lh-ch svg');if(!s)return null;const r=s.getBoundingClientRect();const x=r.left+r.width*.3,y=r.top+r.height*.5;
  s.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,pointerType:'touch',clientX:x,clientY:y}));
  s.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,pointerType:'touch',clientX:x,clientY:y}));
  const rd=document.querySelector('.lh-rd');return{readout:rd.innerText.replace(/\n/g,' | '),latestBtn:!!rd.querySelector('.lh-rdx')};})()
