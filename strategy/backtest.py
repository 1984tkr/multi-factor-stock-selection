import pandas as pd
import numpy as np

def run_backtest(positions, market_data, timing_signals, initial_capital=1e7):
    """
    完整回测逻辑：
    - 支持持仓动态跟踪
    - 支持择时信号（多头/空仓切换）
    - 支持停牌补全
    - 支持分红除权价格（默认行情数据已为复权价）

    :param positions: 每期选股仓位（trade_date, ts_code, weight）
    :param market_data: 市场行情数据（包含trade_date, ts_code, close等列）
    :param timing_signals: 择时信号（trade_date, final_signal=0/1）
    :param initial_capital: 初始资金
    :return: 每日净值DataFrame, 每日持仓快照
    """

    all_dates = market_data['trade_date'].sort_values().unique()

    portfolio_value = []
    daily_positions = []

    capital = initial_capital
    current_positions = {}  # 股票 -> 股数
    last_prices = {}        # 股票 -> 上个有效收盘价（用于停牌补全）

    for trade_date in all_dates:
        daily_market = market_data[market_data['trade_date'] == trade_date]
        timing_signal = timing_signals.loc[timing_signals['trade_date'] == trade_date, 'final_signal'].values

        if len(timing_signal) > 0:
            timing_signal = timing_signal[0]
        else:
            timing_signal = 1  # 无信号默认多头持仓

        # === 调仓日处理 ===
        if trade_date in positions['trade_date'].values:
            daily_positions_data = positions[positions['trade_date'] == trade_date]

            if timing_signal == 1:  # 正常持仓
                current_positions = adjust_positions(daily_positions_data, daily_market, capital)
            else:  # 空仓信号，清仓
                current_positions = {}

        # === 计算每日市值 ===
        daily_value = 0
        for stock, shares in current_positions.items():
            price_row = daily_market[daily_market['ts_code'] == stock]
            if not price_row.empty:
                close_price = price_row['close'].values[0]
                last_prices[stock] = close_price  # 更新有效价格
            else:
                close_price = last_prices.get(stock, np.nan)  # 如果停牌，使用最近价格

            if not np.isnan(close_price):
                daily_value += shares * close_price

        capital = daily_value
        portfolio_value.append({'trade_date': trade_date, 'portfolio_value': capital / initial_capital})

        # === 记录每日持仓 ===
        for stock, shares in current_positions.items():
            close_price = last_prices.get(stock, np.nan)
            if not np.isnan(close_price):
                daily_positions.append({
                    'trade_date': trade_date,
                    'ts_code': stock,
                    'shares': shares,
                    'value': shares * close_price
                })

    portfolio_value_df = pd.DataFrame(portfolio_value)
    daily_positions_df = pd.DataFrame(daily_positions)

    return portfolio_value_df, daily_positions_df


def adjust_positions(positions_data, daily_market, capital):
    """
    按仓位权重分配资金，计算股数（支持停牌补全逻辑）
    :param positions_data: 当日选股结果（仓位）
    :param daily_market: 当日行情
    :param capital: 总资金
    :return: 股票 -> 持仓股数
    """
    positions = {}
    effective_weights = {}

    for _, row in positions_data.iterrows():
        ts_code = row['ts_code']
        weight = row['weight']
        price_row = daily_market[daily_market['ts_code'] == ts_code]

        if not price_row.empty:
            close_price = price_row['close'].values[0]
            shares = (capital * weight) / close_price
            positions[ts_code] = shares
            effective_weights[ts_code] = weight

    # 如果部分股票停牌（没有价格），这些股票权重要重新分配
    total_effective_weight = sum(effective_weights.values())

    if total_effective_weight < 1.0:
        for ts_code in effective_weights:
            effective_weights[ts_code] /= total_effective_weight

        for ts_code, weight in effective_weights.items():
            price_row = daily_market[daily_market['ts_code'] == ts_code]
            if not price_row.empty:
                close_price = price_row['close'].values[0]
                shares = (capital * weight) / close_price
                positions[ts_code] = shares

    return positions