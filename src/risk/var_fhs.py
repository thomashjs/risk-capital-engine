"""
var_fhs.py

Filtered Historical Simulation (FHS) Value-at-Risk model.

Uses EWMA volatility filtering to standardize historical returns,
resamples shocks, then rescales them with current volatility.
"""

import numpy as np
import pandas as pd
from src.portfolio.positions import Portfolio
from src.risk.volatility import _ewma_volatility

def fhs_var(
    returns: pd.DataFrame,
    portfolio: Portfolio,
    alpha: float,
    n_sims: int = 10000,
    lambda_: float = 0.94,
    burn_in: int = 50,
    seed: int | None = None
) -> float:

    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between 0 and 1.")

    if returns.empty:
        raise ValueError("Returns DataFrame is empty.")

    aligned = returns[portfolio.tickers]

    vol = _ewma_volatility(aligned, lambda_)

    standardized = aligned / vol
    standardized = standardized.iloc[burn_in:] # discard burn-in period for better shock sampling

    shocks = standardized.dropna().to_numpy()

    if seed is not None:
        np.random.seed(seed)

    indices = np.random.randint(0, shocks.shape[0], n_sims)

    sampled_shocks = shocks[indices]

    current_vol = vol.iloc[-1].to_numpy()

    simulated_returns = sampled_shocks * current_vol

    portfolio_returns = simulated_returns @ portfolio.weights

    pnl_sims = portfolio_returns * portfolio.notional

    var_threshold = np.quantile(pnl_sims, 1 - alpha)

    return -float(var_threshold)