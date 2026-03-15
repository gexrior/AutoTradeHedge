"""
Trading Autoresearch — Fixed backtesting engine.
DO NOT MODIFY this file. The agent only modifies strategy.py.

Provides:
  - Market data download & caching
  - Backtesting engine with realistic constraints
  - Fixed evaluation metrics (Sharpe, MaxDD, CAGR, etc.)

Usage:
  python backtest.py                # one-time data download
  python backtest.py --run          # run strategy.py and evaluate
"""

import os
import sys
import json
import math
import time
import importlib
import argparse
from datetime import datetime, timedelta

import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Constants (fixed, do not modify)
# ---------------------------------------------------------------------------

CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
DATA_DIR = os.path.join(CACHE_DIR, "data")
RESULTS_FILE = os.path.join(os.path.dirname(__file__), "results.tsv")

# Universe: US ETFs + Crypto + Commodities
# Mirrors trade.xyz cross-asset coverage: equities, crypto, precious metals, commodities
UNIVERSE = [
    # Broad market equities
    "SPY", "QQQ", "IWM", "DIA",
    # Sector ETFs
    "XLK", "XLF", "XLE", "XLV", "XLI",
    "XLP", "XLU", "XLB", "XLRE",
    # Precious metals & commodities (trade.xyz: Gold, Silver, Platinum, Palladium, Oil)
    "GLD", "SLV", "PPLT", "PALL",       # precious metals
    "USO", "UNG",                        # energy commodities (WTI oil, nat gas)
    "CPER",                              # copper
    # Bonds
    "TLT", "IEF",
    # International
    "EEM", "EFA", "VWO",
    # Credit
    "HYG", "LQD",
    # Crypto (trade.xyz: BTC, ETH, SOL perps)
    "BTC-USD", "ETH-USD", "SOL-USD",
]

# Backtest parameters
TRAIN_START = "2020-01-01"
TRAIN_END = "2023-12-31"
TEST_START = "2024-01-01"
TEST_END = "2025-12-31"

INITIAL_CAPITAL = 1_000_000
COMMISSION_BPS = 5          # 5 bps per trade (round trip = 10 bps)
SLIPPAGE_BPS = 3            # 3 bps slippage per trade
MIN_TRADE_SIZE = 100        # minimum dollar trade size
RISK_FREE_RATE = 0.04       # 4% annual risk-free rate

# ---------------------------------------------------------------------------
# Data download & caching
# ---------------------------------------------------------------------------

def download_data(symbols=None, force=False):
    """Download OHLCV data for all universe symbols via yfinance."""
    import yfinance as yf

    if symbols is None:
        symbols = UNIVERSE
    os.makedirs(DATA_DIR, exist_ok=True)

    for sym in symbols:
        filepath = os.path.join(DATA_DIR, f"{sym}.parquet")
        if os.path.exists(filepath) and not force:
            continue
        print(f"  Downloading {sym}...")
        try:
            df = yf.download(sym, start="2010-01-01", end="2026-03-15",
                             auto_adjust=True, progress=False)
            if df.empty:
                print(f"  WARNING: No data for {sym}, skipping")
                continue
            # Flatten MultiIndex columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df.index.name = "Date"
            df.to_parquet(filepath)
            print(f"  Saved {sym}: {len(df)} rows")
        except Exception as e:
            print(f"  ERROR downloading {sym}: {e}")

    print(f"Data cached at {DATA_DIR}")


def load_data(symbols=None, start=None, end=None):
    """Load cached market data. Returns dict of {symbol: DataFrame}."""
    if symbols is None:
        symbols = UNIVERSE
    data = {}
    for sym in symbols:
        filepath = os.path.join(DATA_DIR, f"{sym}.parquet")
        if not os.path.exists(filepath):
            continue
        df = pd.read_parquet(filepath)
        if start:
            df = df[df.index >= start]
        if end:
            df = df[df.index <= end]
        if not df.empty:
            data[sym] = df
    return data


def get_price_matrix(data, field="Close"):
    """Build aligned price matrix from data dict."""
    frames = {sym: df[field].rename(sym) for sym, df in data.items() if field in df.columns}
    if not frames:
        return pd.DataFrame()
    prices = pd.concat(frames.values(), axis=1).sort_index()
    prices = prices.ffill().dropna(how="all")
    return prices


# ---------------------------------------------------------------------------
# Backtesting engine
# ---------------------------------------------------------------------------

class BacktestEngine:
    """
    Event-driven backtester with realistic execution model.

    The strategy returns target weights (dict of {symbol: weight}).
    The engine handles:
      - Position sizing from weights
      - Commission and slippage
      - Daily portfolio tracking
      - No look-ahead bias (strategy only sees data up to current date)
    """

    def __init__(self, prices, initial_capital=INITIAL_CAPITAL,
                 commission_bps=COMMISSION_BPS, slippage_bps=SLIPPAGE_BPS):
        self.prices = prices
        self.initial_capital = initial_capital
        self.commission_rate = commission_bps / 10000
        self.slippage_rate = slippage_bps / 10000
        self.dates = prices.index.tolist()

    def run(self, strategy_func, rebalance_freq="weekly", lookback=252):
        """
        Run backtest.

        Args:
            strategy_func: callable(prices_history, current_date) -> dict of {symbol: weight}
                           weights should sum to <= 1.0 (remainder is cash)
            rebalance_freq: "daily", "weekly", or "monthly"
            lookback: number of trading days of history to pass to strategy

        Returns:
            dict with portfolio values, trades, and metadata
        """
        portfolio_values = []
        trade_log = []
        positions = {}  # {symbol: num_shares}
        cash = self.initial_capital

        rebalance_dates = self._get_rebalance_dates(rebalance_freq)

        for i, date in enumerate(self.dates):
            # Update portfolio value with current prices
            port_value = cash
            for sym, shares in positions.items():
                if sym in self.prices.columns and not pd.isna(self.prices.loc[date, sym]):
                    port_value += shares * self.prices.loc[date, sym]

            portfolio_values.append({"date": date, "value": port_value})

            # Rebalance if scheduled
            if date in rebalance_dates and i >= lookback:
                history = self.prices.iloc[max(0, i - lookback):i + 1]
                try:
                    target_weights = strategy_func(history, date)
                except Exception as e:
                    # Strategy error — hold current positions
                    continue

                if not isinstance(target_weights, dict):
                    continue

                # Normalize weights if they exceed 1.0
                total_weight = sum(abs(w) for w in target_weights.values())
                if total_weight > 1.0:
                    target_weights = {k: v / total_weight for k, v in target_weights.items()}

                # Execute trades
                cash, positions, trades = self._rebalance(
                    date, port_value, cash, positions, target_weights
                )
                trade_log.extend(trades)

        pv = pd.DataFrame(portfolio_values).set_index("date")
        return {
            "portfolio_values": pv,
            "trade_log": trade_log,
            "initial_capital": self.initial_capital,
        }

    def _get_rebalance_dates(self, freq):
        dates = self.prices.index
        if freq == "daily":
            return set(dates)
        elif freq == "weekly":
            # Rebalance on the first trading day of each week
            return set(dates.to_series().groupby(dates.to_period("W")).first())
        elif freq == "monthly":
            return set(dates.to_series().groupby(dates.to_period("M")).first())
        else:
            return set(dates)

    def _rebalance(self, date, port_value, cash, positions, target_weights):
        trades = []
        new_positions = dict(positions)

        for sym, target_weight in target_weights.items():
            if sym not in self.prices.columns:
                continue
            price = self.prices.loc[date, sym]
            if pd.isna(price) or price <= 0:
                continue

            target_value = port_value * target_weight
            current_shares = new_positions.get(sym, 0)
            current_value = current_shares * price
            trade_value = target_value - current_value

            if abs(trade_value) < MIN_TRADE_SIZE:
                continue

            # Apply slippage
            if trade_value > 0:  # buying
                exec_price = price * (1 + self.slippage_rate)
            else:  # selling
                exec_price = price * (1 - self.slippage_rate)

            shares_delta = trade_value / exec_price
            commission = abs(trade_value) * self.commission_rate

            new_positions[sym] = current_shares + shares_delta
            cash -= (shares_delta * exec_price + commission)

            trades.append({
                "date": date, "symbol": sym,
                "shares": shares_delta, "price": exec_price,
                "commission": commission, "value": trade_value,
            })

        # Close positions not in target
        for sym in list(new_positions.keys()):
            if sym not in target_weights or target_weights.get(sym, 0) == 0:
                shares = new_positions.pop(sym, 0)
                if shares == 0:
                    continue
                price = self.prices.loc[date, sym]
                if pd.isna(price):
                    continue
                exec_price = price * (1 - self.slippage_rate) if shares > 0 else price * (1 + self.slippage_rate)
                commission = abs(shares * exec_price) * self.commission_rate
                cash += shares * exec_price - commission
                trades.append({
                    "date": date, "symbol": sym,
                    "shares": -shares, "price": exec_price,
                    "commission": commission, "value": -shares * exec_price,
                })

        return cash, new_positions, trades


# ---------------------------------------------------------------------------
# Evaluation metrics (DO NOT CHANGE — this is the fixed metric)
# ---------------------------------------------------------------------------

def evaluate(result, risk_free_rate=RISK_FREE_RATE):
    """
    Compute strategy performance metrics.

    Primary metric: sharpe_ratio (higher is better)
    The agent optimizes for this metric.
    """
    pv = result["portfolio_values"]["value"]
    daily_returns = pv.pct_change().dropna()

    if len(daily_returns) < 20:
        return {"sharpe_ratio": -999, "error": "insufficient data"}

    # Annualized metrics
    trading_days = 252
    total_days = (pv.index[-1] - pv.index[0]).days
    years = total_days / 365.25

    # CAGR
    total_return = pv.iloc[-1] / pv.iloc[0] - 1
    cagr = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

    # Volatility
    annual_vol = daily_returns.std() * np.sqrt(trading_days)

    # Sharpe Ratio
    excess_return = cagr - risk_free_rate
    sharpe = excess_return / annual_vol if annual_vol > 0 else 0

    # Max Drawdown
    cummax = pv.cummax()
    drawdown = (pv - cummax) / cummax
    max_dd = drawdown.min()

    # Sortino Ratio
    downside = daily_returns[daily_returns < 0]
    downside_vol = downside.std() * np.sqrt(trading_days) if len(downside) > 0 else 0.001
    sortino = excess_return / downside_vol

    # Calmar Ratio
    calmar = cagr / abs(max_dd) if max_dd != 0 else 0

    # Win rate
    n_trades = len(result.get("trade_log", []))
    winning_trades = sum(1 for t in result.get("trade_log", []) if t.get("value", 0) > 0)
    win_rate = winning_trades / n_trades if n_trades > 0 else 0

    # Total commission paid
    total_commission = sum(t.get("commission", 0) for t in result.get("trade_log", []))

    # Benchmark comparison (buy & hold SPY)
    benchmark_return = 0
    # Will be computed externally if needed

    return {
        "sharpe_ratio": round(sharpe, 4),
        "cagr_pct": round(cagr * 100, 2),
        "annual_vol_pct": round(annual_vol * 100, 2),
        "max_drawdown_pct": round(max_dd * 100, 2),
        "sortino_ratio": round(sortino, 4),
        "calmar_ratio": round(calmar, 4),
        "total_return_pct": round(total_return * 100, 2),
        "win_rate_pct": round(win_rate * 100, 2),
        "num_trades": n_trades,
        "total_commission": round(total_commission, 2),
        "final_value": round(pv.iloc[-1], 2),
        "years": round(years, 2),
    }


def evaluate_train_test(strategy_module):
    """
    Run strategy on both train and test periods.
    Returns train metrics, test metrics, and overfitting score.
    """
    # Load data
    train_data = load_data(start=TRAIN_START, end=TRAIN_END)
    test_data = load_data(start=TEST_START, end=TEST_END)

    if not train_data or not test_data:
        print("ERROR: No data. Run `python backtest.py` first to download.")
        sys.exit(1)

    train_prices = get_price_matrix(train_data)
    test_prices = get_price_matrix(test_data)

    # Get strategy config
    strategy_func = strategy_module.strategy
    rebalance_freq = getattr(strategy_module, "REBALANCE_FREQ", "weekly")
    lookback = getattr(strategy_module, "LOOKBACK", 252)

    # Run backtests
    print("Running train period backtest...")
    train_engine = BacktestEngine(train_prices)
    train_result = train_engine.run(strategy_func, rebalance_freq, lookback)
    train_metrics = evaluate(train_result)

    print("Running test period backtest...")
    test_engine = BacktestEngine(test_prices)
    test_result = test_engine.run(strategy_func, rebalance_freq, lookback)
    test_metrics = evaluate(test_result)

    # Overfitting score: how much does test degrade vs train
    train_sharpe = train_metrics["sharpe_ratio"]
    test_sharpe = test_metrics["sharpe_ratio"]
    if train_sharpe > 0:
        overfit_score = 1 - (test_sharpe / train_sharpe)
    else:
        overfit_score = 0
    overfit_score = round(max(0, overfit_score), 4)

    return train_metrics, test_metrics, overfit_score


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_strategy():
    """Import and run strategy.py, print results."""
    t0 = time.time()

    # Import strategy module
    strategy_path = os.path.join(os.path.dirname(__file__), "strategy.py")
    if not os.path.exists(strategy_path):
        print("ERROR: strategy.py not found")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location("strategy", strategy_path)
    strategy_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(strategy_module)

    train_metrics, test_metrics, overfit_score = evaluate_train_test(strategy_module)

    t1 = time.time()

    # Print summary (parseable by agent)
    print("\n---")
    print(f"train_sharpe:     {train_metrics['sharpe_ratio']:.4f}")
    print(f"train_cagr:       {train_metrics['cagr_pct']:.2f}%")
    print(f"train_max_dd:     {train_metrics['max_drawdown_pct']:.2f}%")
    print(f"train_vol:        {train_metrics['annual_vol_pct']:.2f}%")
    print(f"train_sortino:    {train_metrics['sortino_ratio']:.4f}")
    print(f"test_sharpe:      {test_metrics['sharpe_ratio']:.4f}")
    print(f"test_cagr:        {test_metrics['cagr_pct']:.2f}%")
    print(f"test_max_dd:      {test_metrics['max_drawdown_pct']:.2f}%")
    print(f"test_vol:         {test_metrics['annual_vol_pct']:.2f}%")
    print(f"test_sortino:     {test_metrics['sortino_ratio']:.4f}")
    print(f"overfit_score:    {overfit_score:.4f}")
    print(f"num_trades:       {test_metrics['num_trades']}")
    print(f"total_seconds:    {t1 - t0:.1f}")

    return train_metrics, test_metrics, overfit_score


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trading Autoresearch — Backtesting Engine")
    parser.add_argument("--run", action="store_true", help="Run strategy.py and evaluate")
    parser.add_argument("--force-download", action="store_true", help="Force re-download data")
    args = parser.parse_args()

    if args.run:
        run_strategy()
    else:
        print("Downloading market data...")
        download_data(force=args.force_download)
        print("\nDone! Ready to run strategies.")
        print("Next: python backtest.py --run")
