# timing_signal.py
# 多因子选股策略择时信号模块（含加权择时功能）

import pandas as pd
import numpy as np

def calculate_ma_timing_signal(index_df, short_window=20, long_window=60):
    """
    简单均线择时信号：短期均线上穿长期均线看多，反之看空
    """
    index_df['ma_short'] = index_df['close'].rolling(short_window).mean()
    index_df['ma_long'] = index_df['close'].rolling(long_window).mean()
    index_df['ma_signal'] = np.where(index_df['ma_short'] > index_df['ma_long'], 1, 0)
    return index_df[['ma_signal']]

def calculate_breadth_timing_signal(stock_universe_df, date_col='trade_date'):
    """
    市场宽度择时信号：每日上涨股票占比
    """
    stock_universe_df['up'] = stock_universe_df['pct_chg'] > 0
    breadth_df = stock_universe_df.groupby(date_col)['up'].mean()
    breadth_signal = np.where(breadth_df > 0.6, 1, np.where(breadth_df < 0.4, 0, np.nan))
    return pd.DataFrame(breadth_signal, index=breadth_df.index, columns=['breadth_signal'])

def calculate_momentum_timing_signal(index_df, window=20):
    """
    指数动量择时信号：最近N日涨幅大于0，看多；反之看空
    """
    index_df['momentum'] = index_df['close'].pct_change(window).rolling(window).sum()
    index_df['momentum_signal'] = np.where(index_df['momentum'] > 0, 1, 0)
    return index_df[['momentum_signal']]

def calculate_weighted_timing_signal(index_df, stock_universe_df, weights=None, long_threshold=0.6, short_threshold=0.4):
    """
    加权择时信号：
    - 按权重综合三种择时信号
    - 加权得分高于long_threshold时做多，低于short_threshold时空仓
    """
    if weights is None:
        # 默认权重（可以根据历史回测效果微调）
        weights = {
            'ma': 0.4,
            'breadth': 0.3,
            'momentum': 0.3
        }

    # 计算各单项信号
    ma_signal = calculate_ma_timing_signal(index_df)['ma_signal']
    breadth_signal = calculate_breadth_timing_signal(stock_universe_df)['breadth_signal']
    momentum_signal = calculate_momentum_timing_signal(index_df)['momentum_signal']

    # 合并信号
    combined_signal = pd.concat([ma_signal, breadth_signal, momentum_signal], axis=1)
    combined_signal.columns = ['ma_signal', 'breadth_signal', 'momentum_signal']

    # 计算加权得分
    combined_signal['weighted_score'] = (
        combined_signal['ma_signal'] * weights['ma'] +
        combined_signal['breadth_signal'] * weights['breadth'] +
        combined_signal['momentum_signal'] * weights['momentum']
    )

    # 根据加权得分判断最终信号
    combined_signal['final_signal'] = np.where(
        combined_signal['weighted_score'] >= long_threshold, 1,
        np.where(combined_signal['weighted_score'] <= short_threshold, 0, np.nan)
    )

    return combined_signal[['weighted_score', 'final_signal']]