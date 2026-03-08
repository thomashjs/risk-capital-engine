"""
kupiec.py

Kupiec unconditional coverage test for VaR backtesting.

Tests whether the observed exception rate matches the expected
exception probability implied by the VaR confidence level.
"""

import numpy as np
import pandas as pd
from scipy.stats import chi2


def kupiec_test(
    backtest: pd.DataFrame,
    alpha: float
) -> dict:

    if "Exception" not in backtest.columns:
        raise ValueError("Backtest DataFrame must contain 'Exception' column.")

    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between 0 and 1.")

    exceptions = backtest["Exception"]

    n = len(exceptions)
    x = int(exceptions.sum())

    p = 1 - alpha
    phat = x / n

    if phat == 0 or phat == 1:
        return {
            "exceptions": x,
            "observations": n,
            "LR": np.inf,
            "p_value": 0.0
        }

    lr = -2 * (
        (n - x) * np.log((1 - p) / (1 - phat)) +
        x * np.log(p / phat)
    )

    p_value = 1 - chi2.cdf(lr, df=1)

    return {
        "exceptions": x,
        "observations": n,
        "LR": float(lr),
        "p_value": float(p_value)
    }