/* Socials → Combined KPI Report (2026-10-08): the window must hold the two KpiCardV2 cards and never the 1200×675
   TwitterCard share image (#twitter-capture). Before the fix: twitterCapture:true, kpCards:0 once UFO's data landed. */
(()=>{const d=document.querySelector('[role=dialog][aria-label="Combined KPI report"]');
return JSON.stringify({dialog:!!d,twitterCapture:!!document.getElementById('twitter-capture'),shareDialog:!!document.querySelector('[role=dialog][aria-label="PTGC + UFO KPI share card"]'),kpCards:document.querySelectorAll('.kp').length,loading:/Loading UFO/.test(document.body.innerText),removeBtn:!!document.querySelector('button[aria-label="Remove the UFO card"]')})})()
