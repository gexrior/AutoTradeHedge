"""
Trading Autoresearch — Strategy File
THIS IS THE ONLY FILE THE AGENT MODIFIES.

The agent iterates on this file to find profitable trading strategies.
Everything is fair game: signals, weights, allocation logic, indicators.

Requirements:
  - Must define a `strategy(prices, current_date)` function
  - `prices`: DataFrame with columns = symbols, index = dates (historical data up to current_date)
  - `current_date`: the current rebalancing date
  - Returns: dict of {symbol: weight}, weights should sum to <= 1.0
  - Optional: REBALANCE_FREQ ("daily", "weekly", "monthly"), LOOKBACK (int)
"""

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Strategy configuration
# ---------------------------------------------------------------------------

REBALANCE_FREQ = "weekly"   # how often to rebalance
LOOKBACK = 252              # trading days of history passed to strategy()

# ---------------------------------------------------------------------------
# Strategy implementation (BASELINE: simple momentum + mean reversion blend)
# ---------------------------------------------------------------------------

def strategy(prices, current_date):
    """
    Baseline strategy: 60/40 momentum-quality blend.

    - Ranks assets by 12-1 month momentum (skip most recent month)
    - Applies volatility-inverse weighting to top picks
    - Holds cash buffer for risk management
    """
    if len(prices) < 200:
        return {}

    symbols = prices.columns.tolist()
    returns = prices.pct_change().dropna()

    if len(returns) < 200:
        return {}

    # --- Signal 1: 12-1 Month Momentum (skip last 21 days) ---
    mom_12m = prices.iloc[-252:-21].pct_change(periods=len(prices.iloc[-252:-21]) - 1).iloc[-1]

    # --- Signal 2: Short-term mean reversion (5-day) ---
    ret_5d = prices.iloc[-5:].pct_change(periods=4).iloc[-1]
    mr_signal = -ret_5d  # buy recent losers

    # --- Combine signals ---
    # Normalize each signal to z-scores
    def zscore(s):
        s = s.dropna()
        if s.std() == 0:
            return s * 0
        return (s - s.mean()) / s.std()

    mom_z = zscore(mom_12m)
    mr_z = zscore(mr_signal)

    # Blend: 70% momentum, 30% mean reversion
    combined = 0.7 * mom_z + 0.3 * mr_z

    # --- Risk filter: skip high-volatility assets ---
    vol_20d = returns.iloc[-20:].std() * np.sqrt(252)
    vol_threshold = vol_20d.quantile(0.85)

    # --- Portfolio construction ---
    # Select top 5 assets by combined signal, excluding high-vol
    eligible = combined[vol_20d < vol_threshold].dropna()

    if len(eligible) == 0:
        return {}

    top_n = min(5, len(eligible))
    top_assets = eligible.nlargest(top_n).index.tolist()

    # Inverse volatility weighting
    inv_vol = 1.0 / vol_20d[top_assets]
    weights = inv_vol / inv_vol.sum()

    # Scale to 90% invested (10% cash buffer)
    weights = weights * 0.9

    return {sym: float(w) for sym, w in weights.items() if w > 0.01}
