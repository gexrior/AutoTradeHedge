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
    Experiment 13: Top 2 no vol filter, 90/10 momentum/MR.

    Exp12 (80/20) = 1.692. Try higher momentum weight.
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

    combined = 0.9 * zscore(mom_12m) + 0.1 * zscore(mr_signal)
    eligible = combined.dropna()

    if len(eligible) == 0:
        return {}

    top_assets = eligible.nlargest(2).index.tolist()

    vol_20d = returns.iloc[-20:].std() * np.sqrt(252)
    inv_vol = 1.0 / vol_20d[top_assets].replace(0, np.nan).dropna()
    if len(inv_vol) == 0:
        return {}
    weights = inv_vol / inv_vol.sum()
    weights = weights * 0.95

    return {sym: float(w) for sym, w in weights.items() if w > 0.01}
