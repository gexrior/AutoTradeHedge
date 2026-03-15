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
    Experiment 15: Pure momentum, top 2, equal weight.

    Exp14 uses inv-vol weighting. With only 2 assets, equal weight
    might be simpler and equally effective.
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

    # Equal weight: 47.5% each
    return {sym: 0.475 for sym in top_assets}
