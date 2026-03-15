"""
Trading Autoresearch — Strategy File (Cross-Asset Edition)
THIS IS THE ONLY FILE THE AGENT MODIFIES.
"""

import numpy as np
import pandas as pd

REBALANCE_FREQ = "weekly"
LOOKBACK = 252

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
    CA-5: Cross-asset class rotation with signal-strength weighting.

    Instead of equal-weighting the top 2 classes, weight proportional
    to their risk-adjusted momentum score. Stronger signal gets more weight.
    """
    if len(prices) < 252:
        return {}

    returns = prices.pct_change().dropna()
    if len(returns) < 200:
        return {}

    mom_12m = prices.iloc[-252:-21].pct_change(
        periods=len(prices.iloc[-252:-21]) - 1
    ).iloc[-1]
    vol_60d = returns.iloc[-60:].std() * np.sqrt(252)
    risk_adj_mom = (mom_12m / vol_60d.replace(0, np.nan)).dropna()

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

    sorted_classes = sorted(class_picks.items(), key=lambda x: x[1][1], reverse=True)
    top_2 = sorted_classes[:2]

    # Signal-strength weighting (only use positive scores)
    scores = {sym: max(score, 0.01) for cls, (sym, score) in top_2}
    total_score = sum(scores.values())

    weights = {}
    for sym, score in scores.items():
        weights[sym] = (score / total_score) * 0.95

    return weights
