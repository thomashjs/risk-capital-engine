"""
expected_shortfall.py

Expected Shortfall (ES) model.

Computes tail-conditional loss beyond the VaR threshold
using historical PnL distribution.
"""

import numpy as np
import pandas as pd


def historical_expected_shortfall(
    pnl: pd.Series,
    alpha: float
) -> float:
    """
    Compute historical Expected Shortfall.

    Parameters
    ----------
    pnl : pd.Series
        Historical portfolio PnL series.
    alpha : float
        Confidence level (e.g. 0.99).

    Returns
    -------
    float
        Positive ES number representing average tail loss.
    """

    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between 0 and 1.")

    if pnl.empty:
        raise ValueError("PnL series is empty.")

    quantile_level: float = 1.0 - alpha
    var_threshold: float = float(pnl.quantile(quantile_level))

    tail_losses: pd.Series = pnl[pnl <= var_threshold]

    if tail_losses.empty:
        raise ValueError("No tail observations found for ES calculation.")

    es_value: float = float(tail_losses.mean())

    return -es_value