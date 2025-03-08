import pandas as pd
from utils.data_loader import load_market_data, load_financial_data
from factors.financial_factors import calculate_financial_factors
from factors.technical_factors import calculate_technical_factors
from factors.factor_analysis import evaluate_and_filter_factors
from strategy.stock_selection import construct_positions
from strategy.backtest import run_backtest
from strategy.timing_signal import generate_combined_timing_signal
from utils.performance import calculate_performance_metrics
from visualization.plot_results import plot_portfolio_performance
from visualization.ic_plot import plot_ic_time_series
from visualization.backtest_vs_real import plot_backtest_vs_market
import os

def main():
    # 确保output目录存在
    os.makedirs('output', exist_ok=True)

    print("📊 正在加载市场和财务数据...")
    market_data = load_market_data()
    financial_data = load_financial_data()

    # 合并数据并计算因子
    print("📊 正在计算财务因子和技术因子...")
    all_data = market_data.merge(financial_data, on=['trade_date', 'ts_code'], how='left')
    all_data = calculate_financial_factors(all_data)
    all_data = calculate_technical_factors(all_data)

    # 计算未来5日收益率，作为IC评估基础
    all_data = all_data.sort_values(by=['ts_code', 'trade_date'])
    all_data['future_5d_return'] = all_data.groupby('ts_code')['close'].shift(-5) / all_data['close'] - 1

    # 评估因子表现并筛选有效因子
    print("📊 正在评估因子表现并筛选...")
    selected_factors, ic_df, monthly_ic, icir_df = evaluate_and_filter_factors(all_data, future_return_col='future_5d_return')

    print(f"✅ 选中的有效因子: {selected_factors}")

    # 绘制因子IC时间序列图
    plot_ic_time_series(ic_df, selected_factors, output_file='output/ic_time_series.png')

    # 构建仓位（选股+因子加权评分）
    print("📊 正在构建选股仓位...")
    factor_weights = {factor: 1 / len(selected_factors) for factor in selected_factors}
    positions = construct_positions(all_data, factor_weights, top_n=50)

    # 生成市场择时信号
    print("📊 正在生成市场择时信号...")
    timing_signals = generate_combined_timing_signal(market_data)
    timing_signals.to_csv('output/timing_signals.csv', index=False)

    # 执行回测（结合择时信号和仓位）
    print("📊 正在运行回测...")
    portfolio_value, daily_positions = run_backtest(positions, market_data, timing_signals)

    # 保存每日净值和持仓记录
    portfolio_value.to_csv('output/portfolio_value.csv', index=False)
    daily_positions.to_csv('output/positions.csv', index=False)

    # 计算并保存绩效统计
    print("📊 计算回测绩效...")
    performance_summary = calculate_performance_metrics(portfolio_value)
    performance_summary['Return Statistics'].to_csv('output/return_statistics.csv', index=False)

    # 保存因子IC表现
    ic_summary = monthly_ic.copy()
    for factor in monthly_ic.columns:
        ic_summary[f'ICIR_{factor}'] = icir_df[factor]
    ic_summary.to_csv('output/ic_summary.csv')

    # 绘制组合净值曲线+择时信号
    print("📊 生成净值及择时信号图表...")
    plot_portfolio_performance(portfolio_value, timing_signals)

    # 绘制回测 vs 上证指数 vs 择时信号对比图
    print("📊 生成回测与实盘信号对比图...")
    plot_backtest_vs_market(portfolio_value, market_data, timing_signals, output_file='output/backtest_vs_market.png')

    print("✅ 全流程运行完毕，结果保存至output文件夹！")

if __name__ == '__main__':
    main()