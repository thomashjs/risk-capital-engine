from src.risk.var_historical import historical_var
from src.risk.expected_shortfall import historical_expected_shortfall
from src.utils.config import load_config
from src.data.loaders import load_prices
from src.data.features import compute_log_returns
from src.portfolio.pnl import compute_portfolio_pnl
from src.portfolio.positions import Portfolio
from src.risk.var_parametric import parametric_var

"""
tests expected shortfall and value-at-risk calculations using historical PnL data
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

print(var_value, es_value, pnl.std())

### Test Parametric VaR calculation
param_var: float = parametric_var(returns, portfolio, alpha)

print(f"Parametric VaR (99%): {param_var:,.2f}")