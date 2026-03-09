"""
pnl.py

Portfolio PnL engine.

Responsible for transforming asset return matrices into:
- Portfolio returns
- Portfolio PnL series
"""

import pandas as pd
import numpy as np
from .positions import Portfolio


def compute_portfolio_returns(
    returns: pd.DataFrame,
    portfolio: Portfolio
) -> pd.Series:

    aligned = returns[portfolio.tickers]
    portfolio_ret = aligned @ portfolio.weights
    return pd.Series(portfolio_ret, index=aligned.index)


def compute_portfolio_pnl(
    returns: pd.DataFrame,
    portfolio: Portfolio
) -> pd.Series:

    portfolio_returns = compute_portfolio_returns(returns, portfolio)
    return portfolio.notional * portfolio_returns