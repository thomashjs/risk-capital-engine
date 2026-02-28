from src.utils.config import load_config
from src.data.loaders import load_prices
from src.data.features import compute_log_returns
from src.portfolio.pnl import compute_portfolio_pnl
from src.portfolio.positions import Portfolio


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

print(pnl.head())