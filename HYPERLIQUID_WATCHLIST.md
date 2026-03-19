# Hyperliquid / trade[XYZ] OI Watchlist

Last refreshed: 2026-03-19 Asia/Shanghai
Source: Hyperliquid public `info` API
Method:
- Enumerate builder perp dexes with `type=perpDexs`
- Query the `xyz` dex with `type=metaAndAssetCtxs`, `dex=xyz`
- Rank by estimated USD notional open interest: `openInterest × markPx`

Important:
- This watchlist is for the **trade[XYZ] / xyz dex** specifically.
- It is not the same as the default Hyperliquid perp universe.
- Earlier versions were wrong because they only looked at the default perp dex and/or ranked raw OI units instead of USD notional.

## Top 20 by USD Notional OI (`dex=xyz`)

| Rank | Symbol | OI (USD notional) | Raw OI | Mark Price | 24h Notional Volume | Funding |
|---|---:|---:|---:|---:|---:|---:|
| 1 | xyz:CL | 308,304,401.65 | 3,198,742.534 | 96.383 | 899,794,849.02 | -0.000010235 |
| 2 | xyz:XYZ100 | 212,461,354.65 | 8,710.2884 | 24,392.0 | 299,742,684.72 | -0.0000189426 |
| 3 | xyz:BRENTOIL | 178,374,167.85 | 1,669,232.34 | 106.86 | 313,701,419.52 | 0.0000792408 |
| 4 | xyz:GOLD | 139,881,693.99 | 28,838.0188 | 4,850.6 | 89,459,932.80 | 0.00000625 |
| 5 | xyz:SILVER | 105,142,050.72 | 1,388,728.86 | 75.711 | 310,024,042.89 | 0.00000625 |
| 6 | xyz:NVDA | 63,918,273.11 | 354,471.346 | 180.32 | 19,381,953.16 | 0.00000625 |
| 7 | xyz:SNDK | 49,843,237.69 | 67,568.476 | 737.67 | 12,308,262.71 | -0.0000272238 |
| 8 | xyz:MU | 33,053,577.47 | 73,742.448 | 448.23 | 23,641,098.77 | 0.0000274204 |
| 9 | xyz:CRCL | 27,527,640.15 | 205,506.832 | 133.95 | 24,975,616.72 | 0.00000625 |
| 10 | xyz:EWY | 21,926,068.13 | 163,969.998 | 133.72 | 18,031,092.91 | -0.0000307205 |
| 11 | xyz:COPPER | 21,269,503.27 | 3,855,685.46 | 5.5164 | 17,461,260.89 | 0.00000625 |
| 12 | xyz:SP500 | 20,764,824.73 | 3,138.15 | 6,616.9 | 33,918,544.11 | -0.000032096 |
| 13 | xyz:GOOGL | 20,521,896.68 | 66,796.526 | 307.23 | 5,049,512.91 | 0.00000625 |
| 14 | xyz:TSLA | 16,643,968.42 | 42,339.214 | 393.11 | 9,809,685.99 | -0.0000061998 |
| 15 | xyz:SKHX | 14,315,102.37 | 21,083.246 | 678.98 | 5,834,907.33 | 0.0002313706 |
| 16 | xyz:NATGAS | 13,686,262.92 | 4,347,053.4 | 3.1484 | 32,831,202.43 | 0.00000625 |
| 17 | xyz:MSTR | 6,981,971.29 | 49,839.184 | 140.09 | 8,591,090.80 | 0.0000314701 |
| 18 | xyz:EUR | 6,980,768.90 | 6,085,049.6 | 1.1472 | 9,455,829.01 | 0.0 |
| 19 | xyz:JPY | 6,906,227.73 | 43,242.3 | 159.71 | 8,403,399.28 | 0.0000020649 |
| 20 | xyz:HOOD | 6,405,600.51 | 85,340.872 | 75.059 | 19,631,880.26 | 0.00000625 |

## Notes

- The venue leaders are currently concentrated in:
  - energy (`CL`, `BRENTOIL`, `NATGAS`)
  - indices (`XYZ100`, `SP500`)
  - precious metals (`GOLD`, `SILVER`)
  - selected U.S. equities (`NVDA`, `TSLA`, `MSTR`, `HOOD`, etc.)
- For future research, this list should be paired with:
  - OI change
  - price change
  - volume / OI ratio
  - funding
  - catalyst / calendar context
