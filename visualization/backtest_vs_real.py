import pandas as pd
import matplotlib.pyplot as plt

def plot_backtest_vs_market(portfolio_value, market_data, timing_signals, output_file='output/backtest_vs_market.png'):
    """
    绘制回测净值 vs 市场指数净值，以及择时信号叠加
    :param portfolio_value: 回测组合净值（trade_date, portfolio_value）
    :param market_data: 市场行情（trade_date, ts_code='000001.SH', close列）
    :param timing_signals: 择时信号（trade_date, final_signal）
    """

    # 获取市场基准指数（如上证指数）
    index_data = market_data[market_data['ts_code'] == '000001.SH'][['trade_date', 'close']].copy()
    index_data['index_return'] = index_data['close'].pct_change().fillna(0)
    index_data['index_nav'] = (1 + index_data['index_return']).cumprod()

    # 合并数据
    merged = portfolio_value.merge(index_data, on='trade_date', how='inner')
    merged = merged.merge(timing_signals, on='trade_date', how='left')

    # 绘图
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(merged['trade_date'], merged['portfolio_value'], label='策略净值', color='blue')
    ax1.plot(merged['trade_date'], merged['index_nav'], label='上证指数', color='gray')
    ax1.set_ylabel('净值')
    ax1.legend(loc='upper left')
    ax1.set_title('策略净值 vs 上证指数 vs 择时信号')

    # 添加择时信号
    ax2 = ax1.twinx()
    ax2.plot(merged['trade_date'], merged['final_signal'], label='择时信号', color='red', linestyle='--', alpha=0.6)
    ax2.set_ylabel('择时信号（1=多头，0=空头）')
    ax2.set_ylim(-0.1, 1.1)
    ax2.legend(loc='upper right')

    plt.grid(True)
    plt.savefig(output_file)
    plt.close()

    print(f"✅ 回测 vs 市场 vs 择时信号图已保存至 {output_file}")