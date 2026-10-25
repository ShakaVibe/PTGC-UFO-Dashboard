// Audit V: the whole page's text (numbers to compare before / after)
document.body.innerText.replace(/[ \t]+/g,' ').replace(/\n\s*\n+/g,'\n').trim().slice(0,40000)
