// Audit VI item 2: after the Live Feed's own PTGC/UFO toggle the window must STILL be open on the other token.
// (popstate fires before hashchange on a hash navigation; e44's listener used to read it as Back and close the top window.)
(()=>JSON.stringify({hash:location.hash,dialogs:[...document.querySelectorAll('[role=dialog]')].map(d=>d.getAttribute('aria-label')),len:history.length,grayModal:history.state&&history.state.grayModal?1:0}))()
