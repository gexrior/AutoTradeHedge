"""
Trading Autoresearch — Strategy File (Cross-Asset Edition)
THIS IS THE ONLY FILE THE AGENT MODIFIES.
"""

import numpy as np
import pandas as pd

REBALANCE_FREQ = "weekly"
LOOKBACK = 252

def strategy(prices, current_date):
    """
    CA-1: Volatility-adjusted momentum, top 2, equal weight.

    Problem: Pure momentum picks crypto in bull runs (high raw return)
    but crypto's 50%+ annual vol makes it a poor risk-adjusted pick.

    Fix: Use risk-adjusted momentum = return / volatility (basically Sharpe).
    This naturally penalizes high-vol assets and levels the playing field
    between crypto (50%+ vol) and equities (15-20% vol).
    """
    if len(prices) < 252:
        return {}

    returns = prices.pct_change().dropna()
    if len(returns) < 200:
        return {}

    # 12-1 month momentum
    mom_12m = prices.iloc[-252:-21].pct_change(
        periods=len(prices.iloc[-252:-21]) - 1
    ).iloc[-1]

    # 60-day realized volatility (annualized)
    vol_60d = returns.iloc[-60:].std() * np.sqrt(252)

    # Risk-adjusted momentum = momentum / volatility
    risk_adj_mom = mom_12m / vol_60d.replace(0, np.nan)
    risk_adj_mom = risk_adj_mom.dropna()

    if len(risk_adj_mom) == 0:
        return {}

    def zscore(s):
        s = s.dropna()
        if s.std() == 0:
            return s * 0
        return (s - s.mean()) / s.std()

    signal = zscore(risk_adj_mom).dropna()
    if len(signal) == 0:
        return {}

    top_assets = signal.nlargest(2).index.tolist()
    return {sym: 0.475 for sym in top_assets}
