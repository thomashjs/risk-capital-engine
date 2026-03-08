import numpy as np
from src.risk.var_historical import historical_var
from src.risk.expected_shortfall import historical_expected_shortfall
from src.utils.config import load_config
from src.data.loaders import load_prices
from src.data.features import compute_log_returns
from src.portfolio.pnl import compute_portfolio_pnl
from src.portfolio.positions import Portfolio
from src.risk.var_parametric import parametric_var
from src.risk.covariance import sample_covariance, ewma_covariance
from src.risk.var_montecarlo import mc_var
from src.risk.var_fhs import fhs_var
from src.backtest.rolling import rolling_var_backtest

"""
tests expected shortfall and value-at-risk calculations using various methods
"""

portfolio_cfg = load_config("configs/portfolio.yaml")
risk_cfg = load_config("configs/risk.yaml")

tickers = portfolio_cfg["portfolio"]["tickers"]
notional = portfolio_cfg["portfolio"]["notional"]

prices = load_prices(
    tickers,
    start=risk_cfg["risk"]["start_date"],
    end=risk_cfg["risk"]["end_date"]
)

returns = compute_log_returns(prices)

portfolio = Portfolio.from_equal_weight(
    tickers=tickers,
    notional=notional
)

pnl = compute_portfolio_pnl(returns, portfolio)

alpha: float = 0.99

var_value: float = historical_var(pnl, alpha)
es_value: float = historical_expected_shortfall(pnl, alpha)

print("Historical VaR: ", var_value, "\nExpected Shortfall: ", es_value, "\nPortfolio Std: ", pnl.std())

### Test Parametric VaR calculation
param_var_sample = parametric_var(returns, portfolio, 0.99, method="sample")
param_var_ewma = parametric_var(returns, portfolio, 0.99, method="ewma")

print("Sample VaR:", param_var_sample)
print("EWMA VaR  :", param_var_ewma)

print("Sample portfolio std:",
      np.sqrt(portfolio.weights.T @ sample_covariance(returns) @ portfolio.weights))

print("EWMA portfolio std:",
      np.sqrt(portfolio.weights.T @ ewma_covariance(returns) @ portfolio.weights))

recent = returns.iloc[-250:]
recent20 = returns.iloc[-20:]
recent60 = returns.iloc[-60:]
print("250d portfolio std:",
      np.sqrt(portfolio.weights.T @ sample_covariance(recent) @ portfolio.weights))
print("20d portfolio std:",
      np.sqrt(portfolio.weights.T @ sample_covariance(recent20) @ portfolio.weights))
print("60d portfolio std:",
      np.sqrt(portfolio.weights.T @ sample_covariance(recent60) @ portfolio.weights))

### Test Monte Carlo VaR calculation
mc_var_value = mc_var(returns, portfolio, 0.99)

print("Monte Carlo VaR:", mc_var_value)

### Test Filtered Historical Simulation VaR calculation

fhs_value = fhs_var(returns, portfolio, 0.99)

print("FHS VaR:", fhs_value)

### Test rolling backtest
bt_hist = rolling_var_backtest(
    returns,
    portfolio,
    alpha=0.99,
    window=250,
    model="historical",
)

bt_ewma = rolling_var_backtest(
    returns,
    portfolio,
    alpha=0.99,
    window=250,
    model="parametric_ewma",
)

bt_fhs = rolling_var_backtest(
    returns,
    portfolio,
    alpha=0.99,
    window=250,
    model="fhs",
    n_sims=5000,
    seed=42,
)

print("Rolling backtest results:")
print("Head:", bt_hist.head())
print("Historical Exceptions:", bt_hist["Exception"].sum())
print("EWMA Exceptions:", bt_ewma["Exception"].sum())
print("FHS Exceptions:", bt_fhs["Exception"].sum())