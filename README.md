# Trading Autoresearch

受 [karpathy/autoresearch](https://github.com/karpathy/autoresearch) 启发的自主交易策略进化框架。

AI Agent 通过进化搜索自主迭代交易策略：修改策略 → 回测 → 评估 → 保留/丢弃 → 循环。

## 核心思想

1. **Evolutionary Search** — 每次修改策略代码后回测，效果好就保留，差就丢弃回滚
2. **Trajectory Improvement** — results.tsv 记录所有历史尝试，Agent 从中学习哪些方向有效
3. **Context Engineering** — program.md 引导 Agent 的搜索方向和约束

## 文件结构

```
backtest.py     — 固定的回测引擎 + 数据加载 + 评估指标（不要修改）
strategy.py     — Agent 修改的唯一文件，包含交易策略逻辑
program.md      — Agent 的指令手册（人编辑）
results.tsv     — 实验轨迹记录（自动生成）
.cache/data/    — 缓存的市场数据（parquet 格式）
HYPERLIQUID_WATCHLIST.md — Hyperliquid 高 OI 观察清单（机会发现入口）
```

## Quick Start

```bash
# 1. 安装依赖
pip install pandas numpy yfinance pyarrow

# 2. 下载市场数据（一次性）
python backtest.py

# 3. 手动运行一次回测（验证 baseline）
python backtest.py --run

# 4. 启动 Agent 自主研究
# 在此目录打开 Claude Code，然后：
# > 读一下 program.md，开始自主实验
```

## 评估体系

- **Train period**: 2015-2023（策略开发期）
- **Test period**: 2024-2025（样本外验证期）
- **Primary metric**: test_sharpe（样本外 Sharpe 比率）
- **Overfit guard**: overfit_score = 1 - test_sharpe/train_sharpe
- **Composite score**: test_sharpe - 0.5 * overfit_score

## 投资标的

22 只高流动性美股 ETF：SPY, QQQ, IWM, DIA, XLK, XLF, XLE, XLV, XLI, XLP, XLU, XLB, XLRE, GLD, SLV, TLT, IEF, EEM, EFA, VWO, HYG, LQD

## 卸载

不需要时直接删除整个文件夹即可：
```bash
rm -rf ~/.claude/trading-autoresearch
```
