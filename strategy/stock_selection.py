import pandas as pd
import numpy as np
import os

def standardize_and_score(group, factor_weights):
    """
    对单期因子数据进行标准化并计算综合评分
    """
    for factor in factor_weights:
        group[f'{factor}_z'] = (group[factor] - group[factor].mean()) / (group[factor].std() + 1e-8)
    group['composite_score'] = sum(group[f'{factor}_z'] * weight for factor, weight in factor_weights.items())
    return group

def select_stocks_by_score(group, top_n=50):
    """
    根据因子评分选出Top N股票，并计算等权权重（可替换为评分加权）
    """
    group = group.sort_values(by='composite_score', ascending=False).head(top_n)
    group['weight'] = 1 / len(group)  # 等权配置，你也可以改成按评分加权
    return group[['trade_date', 'ts_code', 'weight']]

def construct_positions(factor_data, factor_weights, top_n=50, output_dir='output'):
    """
    完整流程：因子标准化 -> 综合评分 -> 选股 -> 计算权重 -> 保存持仓文件
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 逐期标准化和评分
    factor_data = factor_data.groupby('trade_date').apply(lambda x: standardize_and_score(x, factor_weights))

    # 逐期选股并生成仓位
    positions = factor_data.groupby('trade_date').apply(lambda x: select_stocks_by_score(x, top_n))
    positions = positions.reset_index(drop=True)

    # 保存到positions.csv
    positions.to_csv(os.path.join(output_dir, 'positions.csv'), index=False)

    return positions

if __name__ == "__main__":
    # 示例因子数据（实盘请替换成真实数据）
    data = {
        'trade_date': ['2024-03-01'] * 5 + ['2024-03-02'] * 5,
        'ts_code': ['000001.SZ', '600519.SH', '002230.SZ', '000858.SZ', '300750.SZ'] * 2,
        'pe_ttm': [12, 25, 30, 15, 40, 12, 24, 29, 16, 38],
        'roe': [0.15, 0.22, 0.18, 0.21, 0.13, 0.14, 0.21, 0.17, 0.20, 0.12],
        'momentum_20': [0.05, 0.08, 0.12, 0.03, 0.10, 0.04, 0.07, 0.11, 0.02, 0.09],
        'volatility_60': [0.20, 0.18, 0.25, 0.22, 0.30, 0.21, 0.19, 0.24, 0.23, 0.28],
        'sentiment_score': [0.60, 0.72, 0.55, 0.70, 0.65, 0.61, 0.71, 0.57, 0.68, 0.66]
    }
    factor_data = pd.DataFrame(data)

    # 因子权重（正负代表因子对评分贡献方向）
    factor_weights = {
        'pe_ttm': -0.2,           # 估值越低越好
        'roe': 0.3,                # 盈利能力越高越好
        'momentum_20': 0.3,        # 趋势越强越好
        'volatility_60': -0.1,     # 波动越低越好
        'sentiment_score': 0.2     # 情绪越好越好
    }

    # 构建仓位并保存
    positions = construct_positions(factor_data, factor_weights, top_n=3)

    print("✅ 仓位构建完成，已保存到 output/positions.csv")
    print(positions)