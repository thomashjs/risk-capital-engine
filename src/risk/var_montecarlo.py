"""
var_montecarlo.py

Monte Carlo Value-at-Risk model.

Simulates joint asset returns from a fitted multivariate
distribution and computes the portfolio loss distribution.
"""

import numpy as np
import pandas as pd
from src.portfolio.positions import Portfolio
from src.risk.covariance import sample_covariance, ewma_covariance


def mc_var(
    returns: pd.DataFrame,
    portfolio: Portfolio,
    alpha: float,
    n_sims: int = 10000,
    method: str = "sample",
    lambda_: float = 0.94,
    mean_zero: bool = False,
    seed: int | None = None
) -> float:

    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between 0 and 1.")

    if returns.empty:
        raise ValueError("Returns DataFrame is empty.")

    aligned = returns[portfolio.tickers]

    # Sample mean as default; can optionally set to 0
    if mean_zero:
        mu = np.zeros(len(portfolio.tickers))
    else:
        mu = aligned.mean().to_numpy()

    if method == "sample":
        cov = sample_covariance(aligned)
    elif method == "ewma":
        cov = ewma_covariance(aligned, lambda_)
    else:
        raise ValueError("method must be 'sample' or 'ewma'.")

    if seed is not None:
        np.random.seed(seed)

    sims = np.random.multivariate_normal(mu, cov, n_sims) # assume r_t are i.i.d. normal with sample cov conditioned on t
                                                          # EWMA doesn't assume identical distributions, cov varies with t
    portfolio_returns = sims @ portfolio.weights

    pnl_sims = portfolio_returns * portfolio.notional

    var_threshold = np.quantile(pnl_sims, 1 - alpha)

    return -float(var_threshold)

'''
Monte Carlo VaR from covariance matrix.
'''
def mc_var_from_cov(
    cov: np.ndarray,
    portfolio: Portfolio,
    alpha: float,
    n_sims: int = 10000,
    mu: np.ndarray | None = None,
    seed: int | None = None
) -> float:

    if mu is None:
        mu = np.zeros(len(portfolio.tickers))

    if seed is not None:
        np.random.seed(seed)

    sims = np.random.multivariate_normal(mu, cov, n_sims)

    portfolio_returns = sims @ portfolio.weights
    pnl_sims = portfolio_returns * portfolio.notional

    var_threshold = np.quantile(pnl_sims, 1 - alpha)

    return -float(var_threshold)