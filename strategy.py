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
    Experiment 14: Pure 12-1m momentum, top 2, no vol filter.

    Exp11 showed pure mom was worse WITH vol filter.
    But exp12→13 showed removing vol filter + higher mom weight helps.
    Test: does 100% momentum beat 90/10?
    """
    if len(prices) < 252:
        return {}

    returns = prices.pct_change().dropna()
    if len(returns) < 200:
        return {}

    mom_12m = prices.iloc[-252:-21].pct_change(periods=len(prices.iloc[-252:-21]) - 1).iloc[-1]

    def zscore(s):
        s = s.dropna()
        if s.std() == 0:
            return s * 0
        return (s - s.mean()) / s.std()

    signal = zscore(mom_12m).dropna()
    if len(signal) == 0:
        return {}

    top_assets = signal.nlargest(2).index.tolist()

    vol_20d = returns.iloc[-20:].std() * np.sqrt(252)
    inv_vol = 1.0 / vol_20d[top_assets].replace(0, np.nan).dropna()
    if len(inv_vol) == 0:
        return {}
    weights = inv_vol / inv_vol.sum()
    weights = weights * 0.95

    return {sym: float(w) for sym, w in weights.items() if w > 0.01}
