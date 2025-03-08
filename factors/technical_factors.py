# technical_factors.py
# 技术因子计算模块，窗口参数全部外部配置

import numpy as np
import pandas as pd
from config import TECHNICAL_FACTOR_WINDOWS

def calculate_momentum_factors(df):
    """
    计算多周期动量因子（过去N日收益率），窗口N可配置
    """
    for window in TECHNICAL_FACTOR_WINDOWS:
        df[f'momentum_{window}'] = df['close'].pct_change(window)
    return df

def calculate_volatility_factors(df):
    """
    计算多周期波动率因子（过去N日收益率的标准差），窗口N可配置
    """
    for window in TECHNICAL_FACTOR_WINDOWS:
        df[f'volatility_{window}'] = df['close'].pct_change().rolling(window).std()
    return df

def calculate_bias_factors(df):
    """
    计算多周期均线乖离率因子，窗口N可配置
    """
    for window in TECHNICAL_FACTOR_WINDOWS:
        df[f'ma_{window}'] = df['close'].rolling(window).mean()
        df[f'bias_{window}'] = (df['close'] - df[f'ma_{window}']) / df[f'ma_{window}']
    return df

def calculate_turnover_factors(df):
    """
    换手率（成交量/流通股本），无周期窗口
    """
    if 'float_share' in df.columns:
        df['turnover_rate'] = df['vol'] / df['float_share']
    else:
        df['turnover_rate'] = np.nan
    return df

def calculate_macd(df, short_window=12, long_window=26, signal_window=9):
    """
    MACD指标（趋势信号），参数可根据风格调节
    """
    df['ema_short'] = df['close'].ewm(span=short_window, adjust=False).mean()
    df['ema_long'] = df['close'].ewm(span=long_window, adjust=False).mean()
    df['macd'] = df['ema_short'] - df['ema_long']
    df['macd_signal'] = df['macd'].ewm(span=signal_window, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']
    return df

def calculate_rsi(df, window=14):
    """
    RSI相对强弱指标（超买超卖），窗口默认14
    """
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window).mean()
    rs = gain / loss
    df['rsi'] = 100 - 100 / (1 + rs)
    return df

def calculate_technical_factors(df):
    """
    主调用函数，按配置计算所有技术因子
    """
    df = calculate_momentum_factors(df)
    df = calculate_volatility_factors(df)
    df = calculate_bias_factors(df)
    df = calculate_turnover_factors(df)
    df = calculate_macd(df)
    df = calculate_rsi(df)
    return df

# factors/technical_factors.py
"""
技术因子计算模块
包含动量类、波动率类、均线偏离类等因子
"""


def calculate_technical_factors(all_data):
    """
    计算技术因子
    :param all_data: 包含行情数据（trade_date, ts_code, close等列）
    :return: all_data（增加技术因子列）
    """

    # 计算各类技术指标
    def calc_rolling_features(group, windows):
        for window in windows:
            col_prefix = f'close_{window}'
            group[f'ma_{window}'] = group['close'].rolling(window).mean()
            group[f'bias_{window}'] = (group['close'] - group[f'ma_{window}']) / group[f'ma_{window}']
            group[f'momentum_{window}'] = group['close'].pct_change(window)

            # 波动率
            group[f'volatility_{window}'] = group['close'].pct_change().rolling(window).std()

        return group

    all_data = all_data.groupby('ts_code').apply(lambda x: calc_rolling_features(x, [5, 20, 60]))

    # 其他因子示例（ATR、量价相关等）
    all_data['turnover_rate'] = all_data['vol'] / all_data['float_share']
    all_data['avg_turnover_20'] = all_data.groupby('ts_code')['turnover_rate'].transform(lambda x: x.rolling(20).mean())

    return all_data