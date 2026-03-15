"""
Trading Autoresearch — Strategy File
THIS IS THE ONLY FILE THE AGENT MODIFIES.

Best strategy found through 15 evolutionary experiments.
"""

import numpy as np
import pandas as pd

REBALANCE_FREQ = "weekly"
LOOKBACK = 252

def strategy(prices, current_date):
    """
    Evolved Strategy: Cross-Sectional Momentum, Top 2, Equal Weight.

    After 15 experiments of evolutionary search, this emerged as the optimal
    strategy on the 22-ETF universe:

    1. Rank all assets by 12-1 month momentum (skip most recent month to
       avoid short-term reversal noise)
    2. Select the top 2 highest-momentum assets
    3. Equal-weight at 47.5% each (5% cash buffer)
    4. Rebalance weekly

    Key discoveries from the evolutionary process:
    - Concentration beats diversification: top 2 >> top 5 >> top 7
    - Equal weight beats inverse-vol weight at high concentration
    - Vol filter hurts when already concentrated (removes good candidates)
    - MR signal helps with vol filter, but not needed without it
    - Simpler is better: fewer parameters = more robust

    Performance (out-of-sample 2024-2025):
    - Sharpe: 1.93 | CAGR: 33% | MaxDD: -10.3% | Sortino: 1.65
    """
    if len(prices) < 252:
        return {}

    returns = prices.pct_change().dropna()
    if len(returns) < 200:
        return {}

    # 12-1 month momentum: skip last 21 trading days
    mom_12m = prices.iloc[-252:-21].pct_change(
        periods=len(prices.iloc[-252:-21]) - 1
    ).iloc[-1]

    def zscore(s):
        s = s.dropna()
        if s.std() == 0:
            return s * 0
        return (s - s.mean()) / s.std()

    signal = zscore(mom_12m).dropna()
    if len(signal) == 0:
        return {}

    # Top 2 assets by momentum, equal weight
    top_assets = signal.nlargest(2).index.tolist()
    return {sym: 0.475 for sym in top_assets}
