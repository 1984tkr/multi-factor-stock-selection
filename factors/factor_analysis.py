import pandas as pd
import os
import shutil
from collections import defaultdict


def calculate_ic(all_data, future_return_col='future_5d_return'):
    """
    计算每日IC（Information Coefficient），基于Spearman秩相关系数
    :param all_data: 包含因子列和未来收益率列的DataFrame
    :return: 每日IC DataFrame
    """
    factor_cols = [col for col in all_data.columns if
                   col.startswith(('momentum', 'volatility', 'bias', 'pe', 'roe', 'turnover', 'sentiment'))]

    ic_df = pd.DataFrame(index=all_data['trade_date'].unique(), columns=factor_cols)

    for date, group in all_data.groupby('trade_date'):
        for factor in factor_cols:
            if group[factor].isnull().all():
                continue
            ic = group[factor].corr(group[future_return_col], method='spearman')
            ic_df.at[date, factor] = ic

    return ic_df


def calculate_monthly_icir(ic_df):
    """
    计算月度IC均值和ICIR（IC均值/IC标准差）
    :param ic_df: 每日IC数据
    :return: 月度IC均值, 月度ICIR
    """
    ic_df['month'] = ic_df.index.strftime('%Y-%m')
    monthly_ic = ic_df.groupby('month').mean()
    monthly_ic_std = ic_df.groupby('month').std()
    icir_df = monthly_ic / monthly_ic_std
    return monthly_ic, icir_df


def filter_factors_by_icir(monthly_ic, icir_df):
    """
    根据最新月度IC和ICIR筛选有效因子
    筛选条件：IC > 0.02 且 ICIR > 0.3
    :return: 筛选后的因子列表
    """
    last_month = icir_df.index[-1]
    latest_ic = monthly_ic.loc[last_month]
    latest_icir = icir_df.loc[last_month]

    selected_factors = latest_ic[(latest_ic > 0.02) & (latest_icir > 0.3)].index.tolist()

    return selected_factors


def track_and_remove_underperforming_factors(icir_df, graveyard_path='factor_graveyard'):
    """
    因子退场机制：
    连续3个月ICIR低于0.3的因子触发退场，归档到factor_graveyard
    :param icir_df: 月度ICIR
    :param graveyard_path: 退场因子存放路径
    :return: 退场因子列表
    """
    if not os.path.exists(graveyard_path):
        os.makedirs(graveyard_path)

    factor_retreat_count = defaultdict(int)

    # 判断过去3个月连续低ICIR因子
    for factor in icir_df.columns:
        low_icir_streak = 0
        for month in icir_df.index[-3:]:
            if pd.isna(icir_df.at[month, factor]) or icir_df.at[month, factor] >= 0.3:
                low_icir_streak = 0
            else:
                low_icir_streak += 1

        if low_icir_streak >= 3:
            factor_retreat_count[factor] += 1

    retired_factors = []

    for factor in factor_retreat_count:
        factor_file = f'factors/{factor}.py'
        if os.path.exists(factor_file):
            shutil.move(factor_file, os.path.join(graveyard_path, f'{factor}.py'))
            log_factor_retreat(factor, graveyard_path)
            retired_factors.append(factor)

    return retired_factors


def log_factor_retreat(factor_name, graveyard_path):
    """
    记录退场因子到日志
    :param factor_name: 因子名
    :param graveyard_path: 退场因子存放路径
    """
    log_file = os.path.join(graveyard_path, 'retired_factors_log.txt')
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f'{pd.Timestamp.now()} - {factor_name} retired due to 3 consecutive months ICIR < 0.3\n')


def evaluate_and_filter_factors(all_data, future_return_col='future_5d_return'):
    """
    因子评估流程：
    1. 每日IC计算
    2. 月度IC和ICIR计算
    3. 因子筛选
    4. 因子退场机制（连续3个月ICIR<0.3的因子移入factor_graveyard）
    :return: 保留因子列表，每日IC，月度IC，月度ICIR
    """
    print("📊 计算每日IC...")
    ic_df = calculate_ic(all_data, future_return_col)

    print("📊 计算月度IC和ICIR...")
    monthly_ic, icir_df = calculate_monthly_icir(ic_df)

    print("📊 筛选有效因子...")
    selected_factors = filter_factors_by_icir(monthly_ic, icir_df)

    print("📊 检查并执行因子退场机制...")
    retired_factors = track_and_remove_underperforming_factors(icir_df)

    print(f"✅ 保留因子: {selected_factors}")
    print(f"❌ 退场因子: {retired_factors}")

    return selected_factors, ic_df, monthly_ic, icir_df