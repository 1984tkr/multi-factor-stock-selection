# factors/bias_60.py
"""
Bias_60 因子计算
计算规则：当前价格与60日均线的偏离度
"""

import pandas as pd

def calculate_bias_60(stock_data):
    """
    计算60日价格偏离度
    :param stock_data: 单只股票的历史行情数据，包含trade_date和close列
    :return: stock_data DataFrame，新增bias_60列
    """
    stock_data['ma_60'] = stock_data['close'].rolling(window=60).mean()
    stock_data['bias_60'] = (stock_data['close'] - stock_data['ma_60']) / stock_data['ma_60']
    return stock_data[['ts_code', 'trade_date', 'bias_60']]