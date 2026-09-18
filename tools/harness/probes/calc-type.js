/* Type into a calculators.html input the way React sees it (native value setter + input event).
   Edit the two constants for the run: SEL = selector, VAL = what to type. Used by the a8/a9 checks:
   the X-factor input (`input[type="number"][step="any"]`) and the Rewards holding box
   (`input[placeholder="Enter total held"]`). */
(()=>{
  const SEL=window.__typeSel||'input[placeholder="Enter total held"]';
  const VAL=window.__typeVal||'1500000000';
  const el=document.querySelector(SEL);if(!el)return{typed:false,sel:SEL};
  const proto=el.type==='number'?HTMLInputElement.prototype:HTMLInputElement.prototype;
  Object.getOwnPropertyDescriptor(proto,'value').set.call(el,VAL);
  el.dispatchEvent(new Event('input',{bubbles:true}));
  return{typed:true,sel:SEL,now:el.value};
})()
