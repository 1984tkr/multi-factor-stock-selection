import pandas as pd
import matplotlib.pyplot as plt

def plot_ic_time_series(ic_df, selected_factors=None, output_file='output/ic_time_series.png'):
    """
    绘制单因子IC时间序列图

    :param ic_df: 每日IC数据（index=日期，列=因子名）
    :param selected_factors: 需要绘制的因子列表（None表示全部因子）
    :param output_file: 保存路径
    """
    plt.figure(figsize=(12, 6))

    factors = selected_factors if selected_factors else ic_df.columns.tolist()

    for factor in factors:
        plt.plot(ic_df.index, ic_df[factor], label=factor)

    plt.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    plt.legend()
    plt.title('因子IC时间序列')
    plt.xlabel('Date')
    plt.ylabel('IC')
    plt.grid(True)

    plt.savefig(output_file)
    plt.close()

    print(f"✅ 因子IC时间序列图已保存至 {output_file}")