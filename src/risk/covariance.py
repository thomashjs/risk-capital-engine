"""
covariance.py

Covariance estimation utilities for market risk models.

Includes:
- Sample covariance
- EWMA covariance (RiskMetrics-style)
"""

import numpy as np
import pandas as pd


def sample_covariance(returns: pd.DataFrame) -> np.ndarray:
    return returns.cov().to_numpy()


def ewma_covariance(
    returns: pd.DataFrame,
    lambda_: float = 0.94,
    burn_in: int = 126
) -> np.ndarray:

    if not 0.0 < lambda_ < 1.0:
        raise ValueError("lambda_ must be between 0 and 1.")

    if returns.empty:
        raise ValueError("Returns DataFrame is empty.")

    values = returns.to_numpy()
    n_obs, n_assets = values.shape

    if burn_in < 2:
        raise ValueError("burn_in must be >= 2.")
    if n_obs <= burn_in:
        raise ValueError("Not enough observations for burn-in window.")

    # initialize with sample covariance of the burn-in window
    init = values[:burn_in]
    cov = np.cov(init, rowvar=False)

    for t in range(burn_in, n_obs):
        r = values[t].reshape(-1, 1)
        cov = lambda_ * cov + (1.0 - lambda_) * (r @ r.T)

    return cov