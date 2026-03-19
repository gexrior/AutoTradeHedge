# Trading Autoresearch

自主进化交易策略的实验框架。AI Agent 通过迭代修改策略代码、回测、评估、保留/丢弃的循环，自主搜索盈利策略。

## Setup

开始新实验前：

1. **确认 run tag**: 基于日期提议一个 tag（如 `mar15`）。分支 `autoresearch/<tag>` 必须不存在。
2. **创建分支**: `git checkout -b autoresearch/<tag>`
3. **读取关键文件**:
   - `README.md` — 项目说明
   - `backtest.py` — 固定的回测引擎（不要修改）
   - `strategy.py` — 你修改的唯一文件
4. **确认数据存在**: 检查 `.cache/data/` 是否有 parquet 文件。如果没有，先运行 `python backtest.py` 下载数据。
5. **初始化 results.tsv**: 创建只有 header 的 results.tsv。
6. **确认后开始实验**。

## Experimentation

每个实验运行回测引擎。你启动它：`python backtest.py --run`

**你可以做的：**
- 修改 `strategy.py` — 这是你唯一编辑的文件。所有内容都可以改：信号、权重、选股逻辑、指标、调仓频率。

**你不能做的：**
- 修改 `backtest.py`。它是只读的。包含固定的评估指标、回测引擎和数据加载。
- 安装新的包。只能用 pandas, numpy（已安装）。
- 修改评估函数。`evaluate()` 是 ground truth 指标。

**目标：在 test 期间（2024-2025）获得最高的 sharpe_ratio，同时保持低 overfit_score。**

复合评分公式：`score = test_sharpe - 0.5 * overfit_score`

## Output format

脚本运行结束后打印：

```
---
train_sharpe:     0.8500
train_cagr:       12.50%
train_max_dd:     -15.20%
test_sharpe:      0.6200
test_cagr:        8.30%
test_max_dd:      -12.10%
overfit_score:    0.2700
num_trades:       156
total_seconds:    5.2
```

提取关键指标：`grep "^test_sharpe:\|^overfit_score:" run.log`

## Logging results

每次实验结束后记录到 `results.tsv`（tab 分隔）。

Header 和 5 列：

```
commit	test_sharpe	overfit_score	status	description
```

1. git commit hash（7 字符）
2. test_sharpe（如 0.6200）— 崩溃时用 0.0000
3. overfit_score（如 0.2700）— 崩溃时用 1.0000
4. status: `keep`, `discard`, 或 `crash`
5. 简短描述

示例：

```
commit	test_sharpe	overfit_score	status	description
a1b2c3d	0.6200	0.2700	keep	baseline momentum + mean reversion
b2c3d4e	0.7100	0.1500	keep	add sector rotation with vol targeting
c3d4e5f	0.4500	0.6000	discard	overfit: too many parameters
d4e5f6g	0.0000	1.0000	crash	syntax error in signal calculation
```

## The experiment loop

LOOP FOREVER:

1. 查看当前 git 状态和 results.tsv 中的历史
2. 基于历史结果思考下一个策略改进方向
3. 修改 `strategy.py`
4. git commit
5. 运行实验: `python backtest.py --run > run.log 2>&1`
6. 读取结果: `grep "^test_sharpe:\|^overfit_score:\|^train_sharpe:" run.log`
7. 如果 grep 为空，说明崩溃了。运行 `tail -n 30 run.log` 看报错，尝试修复。
8. 记录到 results.tsv
9. 如果 `score = test_sharpe - 0.5 * overfit_score` 有改善，保留 commit
10. 如果更差，git reset 回上一个 keep 状态

## Hyperliquid Observation List

Use `HYPERLIQUID_WATCHLIST.md` as the venue-specific research watchlist.
Current contents: top 20 Hyperliquid assets ranked by reported open interest from the public API.

Rules:
- Treat it as an **idea funnel**, not a portfolio universe.
- Do not add names to strategy/backtest code until historical data and symbol mapping are confirmed.
- When doing discretionary opportunity discovery, prioritize names that combine high OI with rising volume, positive price response, and a clear catalyst.
- Refresh the list periodically; OI leadership can change fast.

## Strategy Ideas to Explore

按优先级排列的策略方向（从简单到复杂）：

### Phase 1: 基础因子
- [ ] 纯动量（3/6/12个月）
- [ ] 动量 + 均值回归混合
- [ ] 动量 + 波动率过滤
- [ ] 等权 vs 逆波动率加权 vs 风险平价

### Phase 2: 多因子
- [ ] 趋势跟踪（移动平均交叉）
- [ ] 相对强弱 + 绝对动量过滤
- [ ] 行业轮动（sector rotation）
- [ ] 跨资产动量（股票 + 债券 + 商品 + 黄金）

### Phase 3: 风险管理
- [ ] 动态仓位：波动率目标（如年化 10%）
- [ ] 最大回撤控制：回撤超阈值减仓
- [ ] 趋势过滤：200日均线以下减仓
- [ ] 相关性管理：避免过度集中

### Phase 4: 高级策略
- [ ] 动量崩溃保护（momentum crash protection）
- [ ] 制度切换（regime detection）：高/低波动率环境用不同策略
- [ ] 时间序列动量 vs 横截面动量组合
- [ ] 风险预算（risk budgeting）

### 关键约束
- **简洁优先**: 同等效果下，更简单的策略更好
- **抗过拟合**: overfit_score > 0.5 的策略应直接丢弃
- **现实约束**: 考虑交易成本（已内置 5bps 手续费 + 3bps 滑点）
- **可解释性**: 策略逻辑应该有经济学直觉支撑

## NEVER STOP

实验循环开始后，不要停下来问用户。用户可能在睡觉。你是自主研究员，持续实验直到被手动停止。如果用完了想法，重新审视历史结果，组合之前接近成功的策略，或尝试更激进的架构变化。
