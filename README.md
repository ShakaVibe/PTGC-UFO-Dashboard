# PTGC UFO Dashboard

A dedicated dashboard for tracking **PTGC** and **UFO** tokens on PulseChain.

## 🌐 Live Site
[https://shakavibe.github.io/PTGC-UFO-Dashboard/](https://shakavibe.github.io/PTGC-UFO-Dashboard/)

## ✨ Features

### Home Page
- Two token cards (PTGC & UFO) with live prices
- Market cap, liquidity, and volume at a glance
- Click to enter individual dashboards

### Token Dashboard
- **Stats Bar**: Price, 24h change, market cap, liquidity, volume, holders, Liq/MC ratio
- **Burn Section**: Total burned, 24h burn, sea creature visualization
- **LP Pairs Table**: All trading pairs with sortable columns (liquidity, volume, ratio, 24h change)
- **Holder Zoo**: Holders organized by sea creature tiers based on USD value
- **KPI Report**: Detailed stats modal with Twitter screenshot capability

## 🦑 Sea Creature Tiers

### Holder Tiers (by USD value)
| Creature | Range |
|----------|-------|
| 🦠 Plankton | $0 - $100 |
| 🦐 Shrimp | $100 - $1K |
| 🦀 Crab | $1K - $5K |
| 🐟 Fish | $5K - $10K |
| 🐙 Octopus | $10K - $25K |
| 🐬 Dolphin | $25K - $50K |
| 🦈 Shark | $50K - $100K |
| 🐋 Whale | $100K - $500K |
| 🦑 Kraken | $500K+ |

### Burn Tiers (by token amount)
| Creature | Range |
|----------|-------|
| 🦠 Plankton | 0 - 1M |
| 🦐 Shrimp | 1M - 10M |
| 🦀 Crab | 10M - 50M |
| 🐢 Turtle | 50M - 100M |
| 🐙 Octopus | 100M - 500M |
| 🐬 Dolphin | 500M - 1B |
| 🦈 Shark | 1B - 5B |
| 🐋 Whale | 5B - 25B |
| 🦑 Kraken | 25B+ |

## 📊 Data Sources

| Data | Source |
|------|--------|
| Price, MC, Liq, Volume | DexScreener API |
| Holder Count | PulseScan API |
| Burn Data | PulseChain RPC |
| LP Pairs | DexScreener API |

## 🛠️ Tech Stack

- **React 18** (via CDN)
- **Tailwind CSS** (via CDN)
- **No build step required** - pure HTML/JS

## 📁 File Structure

```
PTGC-UFO-Dashboard/
├── index.html              # Main app (everything in one file)
├── 06_PTGC_V1_transparent_bg (1).png   # PTGC logo
├── 07_Ufo_transparent.png              # UFO logo
└── README.md               # This file
```

## 🚀 Deployment

This site is deployed via GitHub Pages. Any push to `main` branch will auto-deploy.

## 📝 License

MIT License

---

Built for the PulseChain community 💚
