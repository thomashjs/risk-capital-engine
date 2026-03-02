"""
var_parametric.py

Delta-Normal (Parametric) Value-at-Risk model.

Assumes multivariate normal asset returns and computes
portfolio VaR using covariance-based variance aggregation.

VaR = z_alpha * sigma_portfolio * notional
"""

from typing import Tuple
import numpy as np
import pandas as pd
from scipy.stats import norm
from src.portfolio.positions import Portfolio


def parametric_var(
    returns: pd.DataFrame,
    portfolio: Portfolio,
    alpha: float
) -> float:
    """
    Compute 1-day Delta-Normal VaR.

    Parameters
    ----------
    returns : Historical asset returns.
    portfolio : Portfolio object containing weights and notional.
    alpha : Confidence level (e.g. 0.99).

    Returns
    -------
    Positive VaR value.
    """

    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between 0 and 1.")

    if returns.empty:
        raise ValueError("Returns DataFrame is empty.")

    aligned: pd.DataFrame = returns[portfolio.tickers]

    cov_matrix: np.ndarray = aligned.cov().to_numpy()

    weights: np.ndarray = portfolio.weights

    portfolio_variance: float = float(weights.T @ cov_matrix @ weights)

    if portfolio_variance < 0.0:
        raise ValueError("Computed negative portfolio variance.")

    portfolio_std: float = float(np.sqrt(portfolio_variance))

    z_score: float = float(norm.ppf(alpha))

    var_value: float = z_score * portfolio_std * portfolio.notional

    return var_value