import tushare as ts
import pandas as pd
import time
import requests
from config import TUSHARE_TOKEN

# 设置Tushare Token
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

# 获取全市场股票列表（带重试）
def get_stock_list_with_retry(max_retries=5):
    """
    获取全市场股票列表，并加入重试机制，防止Tushare超时或限流导致失败
    """
    for attempt in range(max_retries):
        try:
            print(f"正在获取股票列表，尝试 {attempt+1}/{max_retries}...")
            stock_list = pro.stock_basic(exchange='', list_status='L')['ts_code'].tolist()
            print(f"成功获取股票列表，共 {len(stock_list)} 只股票")
            return stock_list
        except requests.exceptions.RequestException as e:
            print(f"获取股票列表失败，重试 {attempt+1}/{max_retries}，错误信息：{e}")
            time.sleep(5)  # 每次重试前等待5秒
    raise Exception("多次重试后，获取股票列表依然失败")

# 分批获取市场数据
def load_market_data(start_date='20230101', end_date='20240306', batch_size=50):
    """
    分批获取市场数据，每批最多获取batch_size只股票，每批之间延时5秒，防止Tushare限流
    """
    stock_list = get_stock_list_with_retry()

    all_data = []
    for i in range(0, len(stock_list), batch_size):
        batch = stock_list[i:i+batch_size]
        print(f"正在获取第 {i//batch_size + 1} 批市场数据，共 {len(batch)} 只股票...")
        for ts_code in batch:
            try:
                df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
                all_data.append(df)
            except Exception as e:
                print(f"获取 {ts_code} 行情数据失败，跳过。错误信息：{e}")
        time.sleep(5)  # 每批次间隔5秒，降低触发限流风险

    market_data = pd.concat(all_data, ignore_index=True)
    market_data['trade_date'] = pd.to_datetime(market_data['trade_date'])

    return market_data

# 分批获取财务数据
def load_financial_data(start_date='20230101', end_date='20240306', batch_size=50):
    """
    分批获取财务数据，每批最多获取batch_size只股票，每批之间延时5秒，防止Tushare限流
    """
    stock_list = get_stock_list_with_retry()

    all_data = []
    for i in range(0, len(stock_list), batch_size):
        batch = stock_list[i:i+batch_size]
        print(f"正在获取第 {i//batch_size + 1} 批财务数据，共 {len(batch)} 只股票...")
        for ts_code in batch:
            try:
                df = pro.fina_indicator(ts_code=ts_code, start_date=start_date, end_date=end_date)
                all_data.append(df)
            except Exception as e:
                print(f"获取 {ts_code} 财务数据失败，跳过。错误信息：{e}")
        time.sleep(5)  # 每批次间隔5秒，降低触发限流风险

    financial_data = pd.concat(all_data, ignore_index=True)
    financial_data['trade_date'] = pd.to_datetime(financial_data['trade_date'])

    return financial_data