(()=>{const p=[...document.querySelectorAll('section')].find(s=>/VALUE GENERATED/i.test(s.textContent)&&s.querySelector('h3'));return p?p.outerHTML:'none'})()
