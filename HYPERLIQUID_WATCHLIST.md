# Hyperliquid OI Watchlist

Last refreshed: 2026-03-19 Asia/Shanghai
Source: Hyperliquid public `info` API (`type=metaAndAssetCtxs`)
Selection rule: sort listed assets by reported `openInterest` descending, keep top 20.
Purpose: add a single-venue derivatives attention list for future opportunity discovery and signal research.

## Top 20 by Open Interest

| Rank | Symbol | Open Interest | Mark Price | 24h Notional Volume |
|---|---:|---:|---:|---:|
| 1 | PUMP | 16,421,349,624 | 0.00197 | 11,169,287.90 |
| 2 | HMSTR | 7,335,286,856 | 0.00016 | 6,985.15 |
| 3 | kPEPE | 4,100,900,968 | 0.003518 | 12,077,760.18 |
| 4 | BLAST | 1,845,362,332 | 0.000501 | 113,192.16 |
| 5 | MON | 1,260,166,358 | 0.023187 | 2,208,328.02 |
| 6 | MEME | 1,144,345,276 | 0.000573 | 384,709.45 |
| 7 | PENGU | 902,297,606 | 0.00743 | 6,607,568.95 |
| 8 | kBONK | 866,299,042 | 0.006181 | 3,082,450.01 |
| 9 | LINEA | 845,313,074 | 0.003314 | 907,434.53 |
| 10 | NOT | 385,804,362 | 0.000392 | 15,131.08 |
| 11 | TURBO | 368,080,250 | 0.001008 | 300,585.22 |
| 12 | kSHIB | 315,101,060 | 0.005816 | 1,399,730.39 |
| 13 | XPL | 302,875,480 | 0.10821 | 8,597,873.12 |
| 14 | BOME | 287,998,490 | 0.000437 | 36,784.03 |
| 15 | ANIME | 243,998,362 | 0.00491 | 1,872,205.79 |
| 16 | FARTCOIN | 240,772,489.8 | 0.20485 | 67,905,231.48 |
| 17 | HEMI | 215,561,616 | 0.007868 | 355,900.41 |
| 18 | WLFI | 212,532,888 | 0.09687 | 1,322,095.04 |
| 19 | DOGE | 203,318,330 | 0.095375 | 10,575,892.35 |
| 20 | DOOD | 186,043,498 | 0.003272 | 83,294.25 |

## Research Notes

- This is a **watchlist**, not a trade list.
- OI alone is not enough. Future ranking should combine at least:
  - OI level
  - OI change
  - price change
  - volume / OI ratio
  - funding / basis
  - event or listing catalyst
- Several names are meme-heavy; high OI may represent crowding rather than quality.
- Before using this list in strategy code, normalize symbol mapping and confirm data history availability.
