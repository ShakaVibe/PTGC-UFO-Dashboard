// TOP 100 header geometry: the switch, the coin (logo img), the title and subtitle must not overlap; reports their boxes
(()=>{const m=document.querySelector('.t1m');const R=e=>{if(!e)return null;const r=e.getBoundingClientRect();return[Math.round(r.top),Math.round(r.bottom),Math.round(r.left),Math.round(r.right)]};
const sw=R(m.querySelector('.t1sw')),coin=R(m.querySelector('.t1hd .lg-coin img.lg')),h2=R(m.querySelector('.t1ttl h2')),p=R(m.querySelector('.t1ttl p')),hd=R(m.querySelector('.t1hd')),x=R(m.querySelector('.t1x'));
const ov=(a,b)=>a&&b&&a[0]<b[1]&&b[0]<a[1]&&a[2]<b[3]&&b[2]<a[3];
return JSON.stringify({sw,coin,h2,p,hd,x,overlap:{swCoin:ov(sw,coin),coinTitle:ov(coin,h2),swX:ov(sw,x)},gaps:{swToCoin:sw&&coin?coin[0]-sw[1]:null,coinToTitle:coin&&h2?h2[0]-coin[1]:null,subToHdBottom:p&&hd?hd[1]-p[1]:null}});})()
