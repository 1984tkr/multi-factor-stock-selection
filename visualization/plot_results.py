import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def plot_portfolio_performance(portfolio_value, timing_signals=None, benchmark_data=None, output_file='output/portfolio_performance.png'):
    """
    绘制策略净值曲线，并叠加择时信号（可选）和基准指数（可选），以及最大回撤区域。

    :param portfolio_value: DataFrame，包含 trade_date, portfolio_value
    :param timing_signals: DataFrame（可选），择时信号（trade_date, final_signal）
    :param benchmark_data: DataFrame（可选），基准指数净值（trade_date, benchmark_value）
    :param output_file: 图片保存路径
    """
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # 画策略净值曲线
    ax1.plot(portfolio_value['trade_date'], portfolio_value['portfolio_value'], label='策略净值', color='blue')

    # 画基准指数净值曲线（可选）
    if benchmark_data is not None:
        ax1.plot(benchmark_data['trade_date'], benchmark_data['benchmark_value'], label='基准指数', color='gray')

    ax1.set_ylabel('净值')
    ax1.set_title('策略净值 vs 参考指数 vs 择时信号')
    ax1.legend(loc='upper left')

    # === 标注最大回撤区域 ===
    max_drawdown_idx = (portfolio_value['portfolio_value'] / portfolio_value['portfolio_value'].cummax() - 1).idxmin()
    max_drawdown_date = portfolio_value.loc[max_drawdown_idx, 'trade_date']
    ax1.axvline(x=max_drawdown_date, color='black', linestyle='--', label='最大回撤')

    # === 画择时信号（可选）===
    if timing_signals is not None:
        ax2 = ax1.twinx()
        ax2.plot(timing_signals['trade_date'], timing_signals['final_signal'], label='择时信号', color='red', linestyle='--', alpha=0.6)
        ax2.set_ylabel('择时信号（1=多头，0=空仓）')
        ax2.set_ylim(-0.1, 1.1)
        ax2.legend(loc='upper right')

    plt.grid(True)
    plt.savefig(output_file)
    plt.close()

    print(f"✅ 策略净值 vs 择时信号 图已保存至 {output_file}")

def plot_annual_returns(portfolio_value, output_file='output/annual_returns.png'):
    """
    绘制年度收益柱状图

    :param portfolio_value: DataFrame，包含 trade_date, portfolio_value
    :param output_file: 图片保存路径
    """
    df = portfolio_value.copy()
    df['year'] = pd.to_datetime(df['trade_date']).dt.year
    df['annual_return'] = df['portfolio_value'].pct_change().fillna(0)

    annual_returns = df.groupby('year')['annual_return'].sum()

    plt.figure(figsize=(10, 5))
    annual_returns.plot(kind='bar', color='blue', alpha=0.7)
    plt.xlabel('年份')
    plt.ylabel('年度收益')
    plt.title('年度收益表现')
    plt.grid(True)

    plt.savefig(output_file)
    plt.close()
    print(f"✅ 年度收益柱状图已保存至 {output_file}")

def plot_excess_returns(portfolio_value, benchmark_data, output_file='output/excess_returns.png'):
    """
    绘制策略 vs 基准指数的累计超额收益曲线

    :param portfolio_value: DataFrame，包含 trade_date, portfolio_value
    :param benchmark_data: DataFrame，基准指数净值（trade_date, benchmark_value）
    :param output_file: 图片保存路径
    """
    merged = portfolio_value.merge(benchmark_data, on='trade_date', how='inner')
    merged['excess_return'] = merged['portfolio_value'] - merged['benchmark_value']

    plt.figure(figsize=(12, 6))
    plt.plot(merged['trade_date'], merged['excess_return'], label='累计超额收益', color='green')
    plt.axhline(0, color='gray', linestyle='--')
    plt.xlabel('日期')
    plt.ylabel('超额收益')
    plt.title('策略 vs 基准指数的累计超额收益')
    plt.legend()
    plt.grid(True)

    plt.savefig(output_file)
    plt.close()
    print(f"✅ 累计超额收益曲线已保存至 {output_file}")