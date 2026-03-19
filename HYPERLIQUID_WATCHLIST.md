# Hyperliquid OI Watchlist

Last refreshed: 2026-03-19 Asia/Shanghai
Source: Hyperliquid public `info` API (`type=metaAndAssetCtxs`)
Selection rule: sort listed assets by **USD notional open interest**, approximated as:

`oi_usd = openInterest × markPx`

Reason: raw `openInterest` from the API appears to be in contract/coin units, not USD notional. Ranking by raw OI can be misleading.

Purpose: add a single-venue derivatives attention list for future opportunity discovery and signal research.

## Top 20 by USD Notional OI

| Rank | Symbol | Raw OI | Mark Price | OI (USD notional, approx.) | 24h Notional Volume | Funding |
|---|---:|---:|---:|---:|---:|---:|
| 1 | BTC | 27,466.10206 | 71,231.0 | 1,956,437,915.84 | 2,917,665,517.30 | 0.0000022996 |
| 2 | ETH | 581,376.2774 | 2,212.6 | 1,286,353,151.38 | 1,765,235,031.55 | 0.0000060317 |
| 3 | HYPE | 20,268,276.98 | 41.526 | 841,660,469.87 | 606,123,057.57 | 0.0000125 |
| 4 | SOL | 3,454,828.14 | 90.843 | 313,846,952.72 | 298,098,434.92 | -0.0000059953 |
| 5 | XRP | 56,598,356.0 | 1.4736 | 83,403,337.40 | 59,220,505.42 | -0.0000021562 |
| 6 | ASTER | 99,814,158.0 | 0.69582 | 69,452,687.42 | 24,679,114.61 | 0.0000125 |
| 7 | ZEC | 269,687.38 | 252.58 | 68,117,638.44 | 94,601,532.98 | 0.0000125 |
| 8 | PAXG | 10,679.556 | 4,840.3 | 51,692,254.91 | 12,233,772.60 | 0.0000125 |
| 9 | FARTCOIN | 242,326,949.4 | 0.20441 | 49,534,051.73 | 68,191,833.01 | 0.0000089503 |
| 10 | ZRO | 20,277,821.0 | 2.093 | 42,441,479.35 | 11,960,632.92 | -0.0000125439 |
| 11 | AVAX | 4,095,361.62 | 9.6668 | 39,589,041.71 | 7,440,429.09 | 0.0000125 |
| 12 | LIT | 32,944,948.0 | 1.1953 | 39,379,096.34 | 11,122,049.79 | -0.0000338047 |
| 13 | TAO | 146,240.938 | 261.37 | 38,222,993.97 | 35,596,590.71 | -0.0000313662 |
| 14 | XPL | 302,874,436.0 | 0.10826 | 32,789,186.44 | 8,599,175.25 | 0.0000125 |
| 15 | PUMP | 16,430,316,096.0 | 0.00197 | 32,367,722.71 | 11,188,228.14 | 0.0000125 |
| 16 | XMR | 87,655.902 | 348.96 | 30,588,403.56 | 6,793,337.57 | 0.0000125 |
| 17 | MON | 1,260,167,854.0 | 0.023218 | 29,258,577.23 | 2,208,819.96 | -0.0000448251 |
| 18 | SUI | 25,987,236.8 | 0.98819 | 25,680,327.53 | 21,057,310.81 | 0.0000072794 |
| 19 | LINK | 2,693,907.0 | 9.2585 | 24,941,537.96 | 14,218,910.04 | 0.0000125 |
| 20 | BNB | 38,168.258 | 652.21 | 24,893,719.55 | 10,254,248.73 | 0.0000121991 |

## Quick Notes

- This corrected list now matches the structure of the Hyperliquid UI much better: large-cap majors rise to the top once OI is converted to USD notional.
- The most important names at the venue level right now are: **BTC, ETH, HYPE, SOL**.
- HYPE is notable because it ranks **#3 by estimated USD OI**, behind only BTC and ETH.
- OI alone is still not enough. Next ranking pass should combine:
  - OI level
  - OI change
  - price change
  - volume / OI ratio
  - funding / basis
  - event or listing catalyst

## Research Rule

Treat this as a **watchlist**, not a trade list.
Before using any symbol in strategy code, confirm:
- symbol mapping
- historical price data source
- historical OI / funding availability
- whether the asset is mature enough to avoid one-off noise
