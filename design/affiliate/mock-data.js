// REAL figures read off the live Affiliate Program page, 2026-10-22 (Shaka's screenshot) — the mock draws from these.
window.AF = {
  month: 'October 2026', monthShort: "October '26", rate: '2%', min: '$250', fee: 'Covered', updated: 'Updated 11h ago', next: 'next in 13h',
  all:   { referrers: 74, buys: '1,525', ptgc: '7.98B', sea: [['whale', 2], ['shark', 3], ['dolphin', 9]], usd: '$599,158', comm: '158.57M', paid: '146.71M' },
  month26: { referrers: 14, buys: 85, ptgc: '604.40M', sea: [['shark', 1], ['dolphin', 8], ['squid', 1]], usd: '$18,894', comm: '11.86M', paid: '0' },
  recent: [
    ['Oct 22', 'HEXican', '4.86M', '$128.81', '0x3c65…0b72'],
    ['Oct 22', 'HEXican', '1.10M', '$29.12', '0x324a…4afd'],
    ['Oct 21', 'PTGC', '10.95M', '$318.19', '0x9937…3868'],
  ],
  // user, wallet, buys, ptgc, creature, n, usd, commission, status
  log: [
    ['@ptgcofficialonboard', '0x6c0E…3805', 18, '223.74M', 'dolphin', 6, '$7,955.09', '4.47M', 'UNPAID'],
    ['88Xcuto4', '0x783c…2fB4', 1, '90.31M', 'dolphin', 2, '$1,916.57', '1.81M', 'UNPAID'],
    ['DeFiMission', '0xF132…8738', 15, '45.15M', 'dolphin', 1, '$1,739.10', '902.93K', 'UNPAID'],
    ['Baba', '0xfe23…fF94', 2, '42.77M', 'dolphin', 1, '$923.06', '855.42K', 'UNPAID'],
    ['PLTGC', '0xe272…7426', 6, '40.34M', 'dolphin', 1, '$1,079.66', '806.80K', 'UNPAID'],
    ['DomDoos', '0xA870…9729', 22, '38.19M', 'dolphin', 1, '$1,877.27', '763.90K', 'UNPAID'],
    ['tommyjane056@gmail', '0xd9e3…3F21', 2, '29.46M', 'squid', 8, '$1,275.86', '589.22K', 'UNPAID'],
    ['PrairieBanana', '0xE0Ed…DD9a', 5, '24.25M', 'squid', 7, '$390.32', '484.93K', 'UNPAID'],
    ['PTGC', '0x19D3…B290', 5, '20.68M', 'squid', 6, '$548.13', '413.50K', 'UNPAID'],
    ['lakers', '0x2812…C4E9', 1, '16.31M', 'squid', 4, '$280.13', '326.23K', 'UNPAID'],
    ['McCloud', '0x02ee…3960', 2, '11.47M', 'squid', 3, '$406.24', '229.32K', 'UNPAID'],
    ['HEXican', '0x462c…b3Ea', 4, '10.38M', 'squid', 3, '$223.59', '0', 'BELOW MIN'],
    ['porsiemprmiamorX0', '0x5426…763E', 1, '10.20M', 'squid', 3, '$254.52', '204.05K', 'UNPAID'],
    ['@Subtle_Craft', '0x9Aa9…9946', 1, '1.14M', 'turtle', 3, '$24.83', '0', 'BELOW MIN'],
  ],
  // the registry, first rows (all-time per referrer): name, wallet, buys, ptgc, creature, usd, comm paid, paid usd, pending
  reg: [
    ['@ptgcofficialonboard', '0x6c0E…3805', 212, '1.41B', 'whale', '$108,210', '28.12M', '$2,104', '4.47M'],
    ['DomDoos', '0xA870…9729', 188, '612.40M', 'shark', '$46,930', '12.25M', '$918', '763.90K'],
    ['DeFiMission', '0xF132…8738', 131, '402.11M', 'shark', '$30,158', '8.04M', '$603', '902.93K'],
    ['HEXican', '0x462c…b3Ea', 96, '255.90M', 'dolphin', '$19,192', '5.12M', '$384', '0'],
  ],
};
