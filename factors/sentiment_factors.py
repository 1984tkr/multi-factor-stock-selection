# factors/sentiment_factors.py
# 计算典型情绪因子（个股+市场整体情绪）

import pandas as pd

def calculate_sentiment_factors(stock_data, market_data):
    """
    计算情绪因子，包括换手率、连板、市场热度等
    :param stock_data: 个股行情数据（包含涨跌停信息等）
    :param market_data: 全市场行情数据（用于整体情绪因子计算）
    :return: 含情绪因子的DataFrame
    """
    df = stock_data.copy()

    # 1. 换手率因子
    if 'float_share' in df.columns and 'vol' in df.columns:
        df['turnover_rate'] = df['vol'] / df['float_share']
    else:
        df['turnover_rate'] = None  # 如果无流通股本数据，暂缺失

    # 2. 涨停/跌停标记
    df['is_limit_up'] = (df['pct_chg'] >= 9.9).astype(int)
    df['is_limit_down'] = (df['pct_chg'] <= -9.9).astype(int)

    # 3. 连板计数（按个股分组统计）
    df['consecutive_limit_up'] = 0
    for ts_code, stock_group in df.groupby('ts_code'):
        stock_group = stock_group.sort_values('trade_date')
        consecutive = 0
        for i, row in stock_group.iterrows():
            if row['is_limit_up'] == 1:
                consecutive += 1
            else:
                consecutive = 0
            df.at[i, 'consecutive_limit_up'] = consecutive

    # 4. 市场整体热度（涨停家数/跌停家数比值）
    if 'is_limit_up' in market_data.columns and 'is_limit_down' in market_data.columns:
        daily_stats = market_data.groupby('trade_date').agg(
            limit_up_count=('is_limit_up', 'sum'),
            limit_down_count=('is_limit_down', 'sum')
        )
        daily_stats['market_heat'] = daily_stats['limit_up_count'] / (daily_stats['limit_down_count'] + 1)
    else:
        daily_stats = pd.DataFrame(index=market_data['trade_date'].unique())
        daily_stats['market_heat'] = None

    # 合并市场情绪热度到个股数据
    df = df.merge(daily_stats[['market_heat']], on='trade_date', how='left')

    # 5. 预留扩展因子（例如龙虎榜净买、舆情得分等）
    df['net_buy_lhb'] = None  # 示例占位
    df['sentiment_score'] = None  # 示例占位，NLP舆情评分

    return df[['ts_code', 'trade_date', 'turnover_rate', 'consecutive_limit_up', 'market_heat', 'net_buy_lhb', 'sentiment_score']]