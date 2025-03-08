# factor_scoring.py
# 使用LightGBM训练多因子评分模型，支持GridSearchCV超参优化+早停+特征重要性分析

import pandas as pd
import numpy as np
import lightgbm as lgb
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error
import os

# 模型保存路径
MODEL_PATH = 'score_model.lgb'
FEATURE_IMPORTANCE_PATH = 'feature_importance.csv'

def train_ml_model_with_tuning(factor_df, future_returns):
    """
    训练多因子评分模型（LightGBM），支持GridSearchCV超参优化+早停策略+特征重要性分析
    """
    X = factor_df.copy()
    y = future_returns.copy()

    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # LightGBM基础模型
    base_model = lgb.LGBMRegressor(boosting_type='gbdt', objective='regression', random_state=42)

    # 超参数搜索范围
    param_grid = {
        'num_leaves': [15, 31, 50],
        'learning_rate': [0.01, 0.05, 0.1],
        'n_estimators': [100, 200],
        'max_depth': [-1, 5, 10],
        'min_child_samples': [10, 20, 30]
    }

    # 超参搜索
    grid_search = GridSearchCV(
        base_model,
        param_grid,
        cv=5,
        scoring='neg_mean_squared_error',
        verbose=1,
        n_jobs=-1
    )
    grid_search.fit(X_train, y_train)

    # 最优参数和模型
    best_params = grid_search.best_params_
    print(f"【GridSearch最优参数】{best_params}")

    # 早停训练（使用最优参数）
    train_data = lgb.Dataset(X_train, label=y_train)
    valid_data = lgb.Dataset(X_test, label=y_test)

    params = {
        'objective': 'regression',
        'boosting_type': 'gbdt',
        'metric': 'rmse',
        'random_state': 42,
        'verbose': -1,
        **best_params
    }

    model = lgb.train(
        params,
        train_data,
        valid_sets=[train_data, valid_data],
        early_stopping_rounds=10,
        verbose_eval=False
    )

    # 评估测试集表现
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    print(f"【早停后最优模型测试集RMSE】{rmse:.5f}")

    # 保存模型
    model.save_model(MODEL_PATH)
    print(f"【评分模型已保存】{MODEL_PATH}")

    # 保存并可视化特征重要性
    save_and_plot_feature_importance(model, X_train.columns)

    return model

def save_and_plot_feature_importance(model, feature_names):
    """
    保存并可视化特征重要性
    """
    importance = model.feature_importance(importance_type='gain')
    importance_df = pd.DataFrame({'feature': feature_names, 'importance': importance})
    importance_df = importance_df.sort_values(by='importance', ascending=False)
    importance_df.to_csv(FEATURE_IMPORTANCE_PATH, index=False)

    print(f"【特征重要性已保存】{FEATURE_IMPORTANCE_PATH}")
    plot_feature_importance(importance_df)

def plot_feature_importance(importance_df):
    """
    画特征重要性柱状图
    """
    plt.figure(figsize=(10, 6))
    plt.barh(importance_df['feature'], importance_df['importance'], color='skyblue')
    plt.xlabel('Importance (Gain)')
    plt.title('Feature Importance')
    plt.gca().invert_yaxis()
    plt.grid(axis='x', linestyle='--', alpha=0.6)
    plt.show()

def load_ml_model():
    """
    加载LightGBM评分模型
    """
    if os.path.exists(MODEL_PATH):
        model = lgb.Booster(model_file=MODEL_PATH)
        print(f"【已加载评分模型】{MODEL_PATH}")
        return model
    else:
        raise FileNotFoundError("评分模型不存在，请先训练模型")

def score_stocks_ml(factor_df):
    """
    使用训练好的LightGBM模型对股票进行评分（预测未来收益率）
    """
    model = load_ml_model()
    scores = model.predict(factor_df)
    return pd.Series(scores, index=factor_df.index)