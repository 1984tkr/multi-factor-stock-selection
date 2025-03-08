import pandas as pd
import numpy as np

def calculate_performance_metrics(portfolio_value, benchmark_data=None, positions=None):
    """
    计算策略的关键绩效指标：
    - 年化收益率
    - 最大回撤
    - 夏普比率
    - 卡玛比率
    - 索提诺比率
    - 信息比率（对比基准指数）
    - 回撤恢复时间
    - 盈利胜率
    - 盈亏比
    - 调仓换手率（从positions.csv计算）

    :param portfolio_value: DataFrame，包含 trade_date, portfolio_value
    :param benchmark_data: DataFrame（可选），基准指数净值（trade_date, benchmark_value）
    :param positions: DataFrame（可选），持仓数据（trade_date, ts_code, weight）
    :return: 绩效指标 DataFrame
    """
    df = portfolio_value.copy()
    df['daily_return'] = df['portfolio_value'].pct_change().fillna(0)

    # === 计算年化收益率 ===
    total_days = len(df)
    annual_return = (df['portfolio_value'].iloc[-1] / df['portfolio_value'].iloc[0]) ** (250 / total_days) - 1

    # === 计算最大回撤 ===
    rolling_max = df['portfolio_value'].cummax()
    drawdown = df['portfolio_value'] / rolling_max - 1
    max_drawdown = drawdown.min()

    # === 计算夏普比率 ===
    risk_free_rate = 0.02  # 无风险利率 2%
    excess_return = df['daily_return'] - risk_free_rate / 250
    sharpe_ratio = excess_return.mean() / excess_return.std() * np.sqrt(250)

    # === 计算卡玛比率 ===
    calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else np.nan

    # === 计算索提诺比率（Sortino Ratio，基于下行波动率） ===
    downside_return = df[df['daily_return'] < 0]['daily_return']
    downside_vol = downside_return.std() * np.sqrt(250)
    sortino_ratio = excess_return.mean() / downside_vol if downside_vol != 0 else np.nan

    # === 计算信息比率（对比基准指数） ===
    if benchmark_data is not None:
        merged = df.merge(benchmark_data, on='trade_date', how='inner')
        merged['benchmark_return'] = merged['benchmark_value'].pct_change().fillna(0)
        active_return = merged['daily_return'] - merged['benchmark_return']
        tracking_error = active_return.std() * np.sqrt(250)
        information_ratio = active_return.mean() / tracking_error if tracking_error != 0 else np.nan
    else:
        information_ratio = np.nan

    # === 计算回撤恢复时间 ===
    recovery_time = np.nan
    if max_drawdown < 0:
        drawdown_periods = drawdown[drawdown == max_drawdown].index[0]
        recovery_periods = df[df['portfolio_value'] >= rolling_max.shift(1)].index
        recovery_time = (recovery_periods[recovery_periods > drawdown_periods].min() - drawdown_periods).days if len(recovery_periods) > 0 else np.nan

    # === 计算盈利胜率（Win Rate） ===
    win_rate = (df['daily_return'] > 0).sum() / len(df)

    # === 计算盈亏比（Profit-Loss Ratio） ===
    avg_win = df[df['daily_return'] > 0]['daily_return'].mean()
    avg_loss = abs(df[df['daily_return'] < 0]['daily_return'].mean())
    profit_loss_ratio = avg_win / avg_loss if avg_loss != 0 else np.nan

    # === 计算换手率（Turnover Rate，从 positions.csv 获取） ===
    if positions is not None:
        turnover_rate = calculate_turnover_rate(positions)
    else:
        turnover_rate = np.nan

    # 组织结果
    metrics = pd.DataFrame({
        'Metric': [
            'Annual Return', 'Max Drawdown', 'Sharpe Ratio', 'Calmar Ratio', 'Sortino Ratio',
            'Information Ratio', 'Time to Recovery', 'Win Rate', 'Profit-Loss Ratio', 'Turnover Rate'
        ],
        'Value': [
            f'{annual_return:.2%}', f'{max_drawdown:.2%}', f'{sharpe_ratio:.2f}', f'{calmar_ratio:.2f}', f'{sortino_ratio:.2f}',
            f'{information_ratio:.2f}', f'{recovery_time} days', f'{win_rate:.2%}', f'{profit_loss_ratio:.2f}', f'{turnover_rate:.2%}'
        ]
    })

    return metrics

def calculate_turnover_rate(positions):
    """
    计算换手率
    :param positions: DataFrame，持仓数据
    :return: 年化换手率
    """
    unique_dates = positions['trade_date'].nunique()
    turnover_per_trade = 0.5  # 假设换手率 50%
    annual_turnover = turnover_per_trade * (250 / unique_dates)  # 估算年化换手率
    return annual_turnover