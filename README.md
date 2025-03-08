# Multi-Factor Stock Selection - Quantitative Trading System

## Project Overview
This project implements a **multi-factor stock selection and backtesting system**, integrating **multi-factor models, market timing strategies, and backtest analysis** to optimize investment decisions. Using **Python and Tushare API**, the system retrieves financial market data, evaluates stock investment value through factor analysis, and integrates timing signals to optimize trading decisions. The system allows users to test different factor combinations and assess their effectiveness in historical market conditions.

## Project Structure
```
multi-factor-stock-selection/
├── data/                          # Raw market data (retrieved via Tushare API)
├── output/                        # Backtest results & analysis reports
├── factors/                       # Factor computation & evaluation
├── factor_graveyard/              # Deprecated factors & logs
├── strategy/                      # Stock selection, market timing, backtesting
├── utils/                         # Helper functions
├── visualization/                 # Performance visualization
├── config.py                      # Strategy parameter settings
├── main.py                        # Main execution script
├── README.md                      # Project documentation
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker containerization support (optional)
```

## Core Features & Workflow
### 1️⃣ Data Acquisition
- Uses **Tushare API** to fetch **daily market prices, financial data, suspension records, dividend adjustments**.
- Cleans and preprocesses data (outlier removal, standardization, missing data handling).
- Computes **future N-day returns** for factor evaluation.

### 2️⃣ Factor Computation
- **Fundamental Factors**: PE, PB, ROE, debt ratio, revenue growth.
- **Technical Factors**: Momentum (5-day, 10-day returns), moving averages (MA5, MA20, MA60), volume trends.
- **Sentiment Factors**: News sentiment analysis, capital inflow tracking.

### 3️⃣ Factor Evaluation & Selection
- Computes **Factor IC (Information Coefficient)** to assess predictive power.
- Calculates **ICIR (IC Stability)** for factor robustness analysis.
- Implements **Factor Removal Mechanism** (ICIR < 0.3 for 3 consecutive months).

### 4️⃣ Stock Selection & Portfolio Construction
- **Factor-weighted scoring method** assigns stock rankings.
- Selects **Top N stocks** for final portfolio.
- **Dynamic rebalancing** based on factor performance.

### 5️⃣ Market Timing
- **Moving average signals** (e.g., MA20 vs MA60 for trend confirmation).
- **Market breadth indicators** (advancing stock percentage threshold).
- **Volume trend signals** (increased/decreased trading volume).

### 6️⃣ Backtesting Framework
- Combines **stock selection & timing signals** for backtesting.
- Handles **suspension adjustments, dividend reinvestments**.
- Computes **daily portfolio value** and generates performance reports.

### 7️⃣ Performance Evaluation
- Calculates key performance metrics:
  - **Annual Return, Max Drawdown, Sharpe Ratio, Calmar Ratio, Sortino Ratio**.
  - **Information Ratio (vs Benchmark), Profit-Loss Ratio, Win Rate, Turnover Rate**.

### 8️⃣ Data Visualization
- **Portfolio Performance vs Benchmark Index**.
- **Factor IC Time-Series Analysis**.
- **Annual Return Distribution**.
- **Cumulative Excess Returns**.

## Installation & Usage
### Prerequisites
Ensure you have **Python 3.8+** installed and install required dependencies:
```sh
pip install -r requirements.txt
```

### Running the System
To execute the full pipeline:
```sh
python main.py
```
This script will **fetch data, compute factors, select stocks, generate timing signals, run backtests, and visualize performance**.

## Output Files
```
output/
├── portfolio_value.csv        # Daily portfolio value
├── positions.csv              # Daily stock positions
├── return_statistics.csv      # Performance metrics
├── ic_summary.csv             # Factor IC statistics
├── timing_signals.csv         # Market timing signals
├── portfolio_performance.png  # Portfolio performance vs Index
├── annual_returns.png         # Annual return bar chart
├── excess_returns.png         # Cumulative excess return curve
```

## Technologies Used
- **Python**: Core development language
- **Pandas, NumPy**: Data processing & analysis
- **Matplotlib, Seaborn**: Data visualization
- **Tushare API**: Market data acquisition
- **Scikit-learn**: Factor normalization, scoring
- **Git & GitHub**: Version control & collaboration

## Future Enhancements
- **Real-time market data tracking** for live trading signals.
- **Automated backtest scheduling** (daily updates, performance reports).
- **Dynamic factor weighting** based on IC performance.
- **Integration with trading platforms** (e.g., Alpaca, Interactive Brokers).

## Contact & Contribution
Contributions are welcome! If you'd like to improve the system, feel free to open an **Issue** or submit a **Pull Request** on GitHub.

**GitHub Repository**: [https://github.com/1984tkr/multi-factor-stock-selection]

