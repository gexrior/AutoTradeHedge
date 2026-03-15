"""
Trading Autoresearch — Strategy File (Cross-Asset Edition)
THIS IS THE ONLY FILE THE AGENT MODIFIES.

Best strategy found through 24 evolutionary experiments across 2 phases:
  Phase 1 (ETF-only): 15 experiments → pure momentum, top 2, equal weight
  Phase 2 (Cross-Asset): 9 experiments → class rotation, signal-strength weight
"""

import numpy as np
import pandas as pd

REBALANCE_FREQ = "weekly"
LOOKBACK = 252

# Asset class definitions — mirrors trade.xyz coverage:
# equities, precious metals, energy commodities, bonds, crypto
ASSET_CLASSES = {
    "equity": ["SPY", "QQQ", "IWM", "DIA", "XLK", "XLF", "XLE", "XLV",
               "XLI", "XLP", "XLU", "XLB", "XLRE", "EEM", "EFA", "VWO"],
    "precious_metals": ["GLD", "SLV", "PPLT", "PALL"],
    "energy_commodities": ["USO", "UNG", "CPER"],
    "bonds": ["TLT", "IEF", "HYG", "LQD"],
    "crypto": ["BTC-USD", "ETH-USD", "SOL-USD"],
}

def strategy(prices, current_date):
    """
    Evolved Cross-Asset Momentum Rotation Strategy.

    Algorithm:
    1. Compute 12-1 month momentum for all assets (skip last month)
    2. Normalize by 60-day realized volatility → risk-adjusted momentum
       (this prevents crypto's high raw returns from dominating)
    3. From each of 5 asset classes, pick the single best asset
    4. Select top 2 asset classes by their champion's score
    5. Allocate proportional to signal strength (stronger signal = more weight)
    6. Rebalance weekly

    Key evolutionary discoveries:
    - Vol-adjusted momentum essential for cross-asset (crypto vol = 50%+ vs equity 15%)
    - Asset class rotation beats flat selection (forces structural diversification)
    - Signal-strength weighting beats equal weight (+4% sharpe improvement)
    - 12-month lookback dominates 6-month (6m caused severe overfitting)
    - Weekly rebalance critical (monthly lost 1.0+ sharpe)
    - Top 2 classes optimal (top 1 too fragile, top 3 too diluted)

    Out-of-sample performance (2024-2025):
    - Sharpe: 1.68 | CAGR: 20.9% | MaxDD: -6.7% | Overfit: 0.00
    """
    if len(prices) < 252:
        return {}

    returns = prices.pct_change().dropna()
    if len(returns) < 200:
        return {}

    # 12-1 month momentum (skip last 21 trading days)
    mom_12m = prices.iloc[-252:-21].pct_change(
        periods=len(prices.iloc[-252:-21]) - 1
    ).iloc[-1]

    # 60-day realized volatility (annualized)
    vol_60d = returns.iloc[-60:].std() * np.sqrt(252)

    # Risk-adjusted momentum
    risk_adj_mom = (mom_12m / vol_60d.replace(0, np.nan)).dropna()

    # Pick best asset from each class
    class_picks = {}
    for cls, symbols in ASSET_CLASSES.items():
        available = [s for s in symbols if s in risk_adj_mom.index]
        if not available:
            continue
        scores = risk_adj_mom[available]
        best = scores.idxmax()
        class_picks[cls] = (best, scores[best])

    if len(class_picks) == 0:
        return {}

    # Top 2 asset classes by signal strength
    sorted_classes = sorted(class_picks.items(), key=lambda x: x[1][1], reverse=True)
    top_2 = sorted_classes[:2]

    # Signal-strength proportional weighting
    scores = {sym: max(score, 0.01) for cls, (sym, score) in top_2}
    total_score = sum(scores.values())
    return {sym: (score / total_score) * 0.95 for sym, score in scores.items()}
