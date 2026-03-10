"""
reporting.py

Utilities for summarizing stress test results.
"""

import numpy as np
import pandas as pd


def stress_loss_distribution(
    returns: pd.DataFrame,
    weights: np.ndarray,
    notional: float
) -> pd.Series:

    # Maybe design issue? Weights should initialized to series with tickers as index?
    portfolio_returns = returns @ pd.Series(weights, index=returns.columns)
    pnl = portfolio_returns * notional

    return -pnl