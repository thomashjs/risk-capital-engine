"""
var_parametric.py

Delta-Normal (Parametric) Value-at-Risk model.

Assumes multivariate normal asset returns and computes
portfolio VaR using covariance-based variance aggregation.

VaR = z_alpha * sigma_portfolio * notional

Supports:
- Sample covariance
- EWMA covariance
"""

from typing import Tuple
import numpy as np
import pandas as pd
from scipy.stats import norm
from src.portfolio.positions import Portfolio
from src.risk.covariance import sample_covariance, ewma_covariance


def parametric_var(
    returns: pd.DataFrame,
    portfolio: Portfolio,
    alpha: float,
    method: str = "sample",
    lambda_: float = 0.94
) -> float:

    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between 0 and 1.")

    if returns.empty:
        raise ValueError("Returns DataFrame is empty.")

    aligned = returns[portfolio.tickers]

    if method == "sample":
        cov = sample_covariance(aligned)
    elif method == "ewma":
        cov = ewma_covariance(aligned, lambda_)
    else:
        raise ValueError("method must be 'sample' or 'ewma'.")

    weights = portfolio.weights
    portfolio_variance = float(weights.T @ cov @ weights)

    if portfolio_variance < 0.0:
        raise ValueError("Computed negative portfolio variance.")

    portfolio_std: float = float(np.sqrt(portfolio_variance))
    z_score = float(norm.ppf(alpha))
    var_value = z_score * portfolio_std * portfolio.notional

    return var_value

def parametric_var_from_cov(
    cov: np.ndarray,
    portfolio: Portfolio,
    alpha: float
) -> float:

    z = norm.ppf(alpha)

    w = portfolio.weights
    port_std = np.sqrt(w @ cov @ w)

    return float(z * port_std * portfolio.notional)