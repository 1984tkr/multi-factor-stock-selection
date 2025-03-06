# Multi-Factor-Stock-Selection
P.S.此为初代模型,有待更新.

## 项目简介
本项目是一个完整的**多因子选股策略开发与回测框架**，兼顾**A股/港股/美股**市场，涵盖因子计算、因子筛选、评分模型、择时信号、回测分析、绩效评估等全流程。
适合：
- 量化投资研究员/策略开发岗自用
- 量化策略团队策略开发模板
- 多因子策略研究与实盘策略开发

---

## 功能概览
| 功能模块 | 主要功能 |
|---|---|
| 数据获取 | Tushare数据接口或本地CSV导入 |
| 因子计算 | 财务因子+技术因子（可配置N周期） |
| 因子筛选 | IC分析+连续3月ICIR低于0.3退场 |
| 因子评分 | LightGBM评分模型（超参调优+早停+特征重要性） |
| 择时信号 | MA+市场宽度+动量加权择时信号 |
| 回测框架 | 支持择时+评分加权+停牌处理+分红除权 |
| 绩效评估 | 收益率统计+因子IC分析+换手率统计 |
| 可视化 | 净值曲线+IC走势+择时信号可视化 |
| 一键运行 | `main.py`一键完成全流程 |

---

## 项目结构  


| Folder/File                | Description |
|------------------------|----------------|
| data/                   | Market & financial data (Tushare/CSV) |
| output/                 | Backtest results (net value, positions, IC stats) |
| factors/                 | Factors calculation & scoring |
| ├─ financial_factors.py | Financial factors calculation (PE, ROE, etc.) |
| ├─ technical_factors.py | Technical factors calculation (momentum, volatility, etc.) |
| ├─ factor_analysis.py   | Factor IC analysis, filtering, and retirement mechanism |
| ├─ factor_scoring.py    | Multi-factor scoring model (LGBM + hyperparameter tuning + early stopping) |
| ├─ timing_signal.py     | Market timing signals (MA, breadth, momentum combined weighting) |
| strategy/                | Backtest framework |
| ├─ backtest.py          | Backtest logic (position sizing, rebalancing, suspension handling, dividend adjustment) |
| utils/                    | Utility functions |
| ├─ data_loader.py       | Data loading (Tushare or CSV files) |
| ├─ performance.py       | Performance analysis (return stats, IC tracking, turnover rate) |
| visualization/            | Visualization of results |
| ├─ plot_results.py      | Net value curve, IC trend, timing signal chart |
| config.py                  | Configuration file (Tushare token, factor periods) |
| main.py                    | Main script (end-to-end process control) |
| README.md                  | Project documentation (current file) |
| log.md                     | Version update history |
| requirements.txt           | Python dependency list |
| Dockerfile                  | Docker container support (optional) |

---

## 策略流程
1. 加载数据（Tushare或本地）
2. 计算因子（财务+技术）
3. 因子IC分析、筛选、退场（ICIR低于0.3淘汰）
4. 训练评分模型（LGBM+超参调优+早停+特征重要性分析）
5. 计算最新因子评分（预测未来收益率）
6. 计算择时信号（均线+市场宽度+动量加权）
7. 回测策略表现（择时+评分加权+停牌+分红除权）
8. 绩效分析（收益率、IC表现、换手率）
9. 可视化（净值+IC+择时信号）
