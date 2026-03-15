"""
Trading Autoresearch — Strategy File
THIS IS THE ONLY FILE THE AGENT MODIFIES.
"""

import numpy as np
import pandas as pd

REBALANCE_FREQ = "weekly"
LOOKBACK = 252

def strategy(prices, current_date):
    """
    Experiment 8: Extreme concentration — top 2 assets.

    Exp6: top 4 → sharpe 1.10
    Exp7: top 3 → sharpe 1.54
    Push further: top 2.
    """
    if len(prices) < 252:
        return {}

    returns = prices.pct_change().dropna()
    if len(returns) < 200:
        return {}

    mom_12m = prices.iloc[-252:-21].pct_change(periods=len(prices.iloc[-252:-21]) - 1).iloc[-1]
    ret_5d = prices.iloc[-5:].pct_change(periods=4).iloc[-1]
    mr_signal = -ret_5d

    def zscore(s):
        s = s.dropna()
        if s.std() == 0:
            return s * 0
        return (s - s.mean()) / s.std()

    combined = 0.8 * zscore(mom_12m) + 0.2 * zscore(mr_signal)

    vol_20d = returns.iloc[-20:].std() * np.sqrt(252)
    vol_threshold = vol_20d.quantile(0.85)
    eligible = combined[vol_20d < vol_threshold].dropna()

    if len(eligible) == 0:
        return {}

    top_n = min(2, len(eligible))
    top_assets = eligible.nlargest(top_n).index.tolist()

    inv_vol = 1.0 / vol_20d[top_assets].replace(0, np.nan).dropna()
    if len(inv_vol) == 0:
        return {}
    weights = inv_vol / inv_vol.sum()
    weights = weights * 0.95

    return {sym: float(w) for sym, w in weights.items() if w > 0.01}
