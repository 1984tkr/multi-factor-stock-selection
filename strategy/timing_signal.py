# strategy/timing_signal.py
"""
市场择时信号模块
包含均线择时、市场宽度、成交量趋势等信号计算
"""

import pandas as pd
import numpy as np

def calculate_moving_average_signals(market_data):
    """
    基于指数均线判断多头/空头市场
    - MA20 > MA60：多头市场
    - MA20 < MA60：空头市场
    """
    index_data = market_data[market_data['ts_code'] == '000001.SH']  # 上证指数
    index_data['ma20'] = index_data['close'].rolling(20).mean()
    index_data['ma60'] = index_data['close'].rolling(60).mean()
    index_data['ma_signal'] = np.where(index_data['ma20'] > index_data['ma60'], 1, 0)
    return index_data[['trade_date', 'ma_signal']]

def calculate_market_breadth_signals(market_data):
    """
    市场宽度指标：
    - 上涨家数占比 > 60%：多头市场
    - 上涨家数占比 < 40%：空头市场
    """
    def daily_breadth(group):
        up_stocks = (group['pct_chg'] > 0).sum()
        total_stocks = len(group)
        return up_stocks / total_stocks

    breadth_df = market_data.groupby('trade_date').apply(daily_breadth).reset_index()
    breadth_df.columns = ['trade_date', 'up_ratio']
    breadth_df['breadth_signal'] = np.where(breadth_df['up_ratio'] > 0.6, 1,
                                             np.where(breadth_df['up_ratio'] < 0.4, 0, np.nan))

    return breadth_df[['trade_date', 'breadth_signal']]

def calculate_volume_trend_signals(market_data):
    """
    市场整体成交量趋势判断
    - 成交量5日均线 > 20日均线：放量
    - 否则：缩量
    """
    index_data = market_data[market_data['ts_code'] == '000001.SH']
    index_data['vol_ma5'] = index_data['vol'].rolling(5).mean()
    index_data['vol_ma20'] = index_data['vol'].rolling(20).mean()
    index_data['volume_signal'] = np.where(index_data['vol_ma5'] > index_data['vol_ma20'], 1, 0)
    return index_data[['trade_date', 'volume_signal']]

def generate_combined_timing_signal(market_data):
    """
    综合多个择时信号生成最终择时信号
    信号权重可以根据策略经验调整
    """
    ma_signals = calculate_moving_average_signals(market_data)
    breadth_signals = calculate_market_breadth_signals(market_data)
    volume_signals = calculate_volume_trend_signals(market_data)

    combined = ma_signals.merge(breadth_signals, on='trade_date', how='left')
    combined = combined.merge(volume_signals, on='trade_date', how='left')

    # 简单信号投票
    combined['timing_signal'] = combined[['ma_signal', 'breadth_signal', 'volume_signal']].mean(axis=1)

    # 当信号>=0.66（两项或以上看多），认为是多头信号
    # 当信号<=0.33（两项或以上看空），认为是空头信号
    combined['final_signal'] = np.where(combined['timing_signal'] >= 0.66, 1,
                                        np.where(combined['timing_signal'] <= 0.33, 0, np.nan))

    return combined[['trade_date', 'final_signal']]