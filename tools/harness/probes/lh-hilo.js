// LEAGUE HISTORY: the big chart's High / Low pill texts
(()=>[...document.querySelectorAll('.lh-ch svg text')].map(t=>t.textContent).filter(s=>/^(High|Low) /.test(s)).join(' | '))()
