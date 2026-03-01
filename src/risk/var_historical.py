"""
var_historical.py

Historical Value-at-Risk (VaR) model.

Computes empirical quantile-based VaR from realized
portfolio PnL distributions.
"""

from typing import Union
import numpy as np
import pandas as pd


def historical_var(
    pnl: pd.Series,
    alpha: float
) -> float:
    """
    Compute historical Value-at-Risk.

    Parameters
    ----------
    pnl : pd.Series
        Historical portfolio PnL series (positive = gain, negative = loss).
    alpha : float
        Confidence level (e.g. 0.99).

    Returns
    -------
    float
        Positive VaR number representing loss threshold.
    """

    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between 0 and 1.")

    if pnl.empty:
        raise ValueError("PnL series is empty.")

    quantile_level: float = 1.0 - alpha
    var_threshold: float = float(pnl.quantile(quantile_level))

    return -var_threshold