# financial_factors.py
# 财务因子计算模块，计算每个个股的核心财务指标

import numpy as np
import pandas as pd

def calculate_financial_factors(df):
    """
    根据财务数据计算多种财务因子
    这些因子可以作为选股多因子体系的重要组成部分
    """

    # 成长性因子
    df['revenue_growth'] = df['revenue'].pct_change(4)  # 四季度同比增长
    df['profit_growth'] = df['net_profit'].pct_change(4)

    # 估值因子（假设市值已在外部计算加入）
    df['pe'] = df['market_cap'] / df['net_profit']
    df['pb'] = df['market_cap'] / df['net_asset']
    df['ev_ebitda'] = (df['market_cap'] + df['total_liability'] - df['cash']) / df['ebitda']

    # 财务健康因子
    df['debt_to_asset'] = df['total_liability'] / df['net_asset']
    df['cash_ratio'] = df['cash'] / df['total_liability']

    # 质量因子
    df['roe'] = df['net_profit'] / df['net_asset']

    # 特殊处理，防止极端值干扰
    for col in ['pe', 'pb', 'ev_ebitda']:
        df[col] = np.clip(df[col], 0, np.percentile(df[col].dropna(), 95))  # 剔除极端值

    return df

# factors/financial_factors.py
"""
财务因子计算模块
支持从财务数据中计算盈利能力、估值等因子
"""

def calculate_financial_factors(all_data):
    """
    计算财务因子
    :param all_data: 合并后的行情+财务数据（包含trade_date, ts_code, pe, roe等列）
    :return: all_data（增加财务因子列）
    """

    # 估值因子
    all_data['pe_ttm'] = all_data['pe_ttm'].replace([None, 0], pd.NA).fillna(method='ffill')
    all_data['pb'] = all_data['pb'].replace([None, 0], pd.NA).fillna(method='ffill')
    all_data['ps_ttm'] = all_data['ps_ttm'].replace([None, 0], pd.NA).fillna(method='ffill')

    # 盈利能力因子
    all_data['roe_ttm'] = all_data['roe'].replace([None], pd.NA).fillna(method='ffill')
    all_data['gross_profit_margin'] = all_data['grossprofit_margin'].replace([None], pd.NA).fillna(method='ffill')

    # 财务杠杆因子
    all_data['debt_asset_ratio'] = all_data['debt_to_assets'].replace([None], pd.NA).fillna(method='ffill')

    # 增长因子
    all_data['revenue_growth'] = all_data['revenue_yoy'].replace([None], pd.NA).fillna(method='ffill')
    all_data['net_profit_growth'] = all_data['netprofit_yoy'].replace([None], pd.NA).fillna(method='ffill')

    return all_data