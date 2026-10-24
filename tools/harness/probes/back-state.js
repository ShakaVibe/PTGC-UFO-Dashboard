// Audit IV e44: where the page is after a Back — the hash, how many windows are open, history length and state
(()=>JSON.stringify({hash:location.hash,dialogs:[...document.querySelectorAll('[role=dialog]')].map(d=>d.getAttribute('aria-label')),len:history.length,state:history.state}))()
