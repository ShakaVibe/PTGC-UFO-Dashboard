// Affiliates Report card (2026-09-29): pick the second month in the picker (React-safe value set) and report it.
(()=>{const s=document.querySelector('select[aria-label="Month shown on card"]');if(!s)return 'no picker';
const set=Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set;set.call(s,s.options[1].value);
s.dispatchEvent(new Event('change',{bubbles:true}));return s.value;})()
