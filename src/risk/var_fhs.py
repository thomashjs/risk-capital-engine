"""
var_fhs.py

Filtered Historical Simulation (FHS) Value-at-Risk model.

Uses EWMA volatility filtering to standardize historical returns,
resamples shocks, then rescales them with current volatility.
"""

import numpy as np
import pandas as pd
from src.portfolio.positions import Portfolio


def _ewma_volatility(returns: pd.DataFrame, lambda_: float) -> pd.DataFrame:

    values = returns.to_numpy()
    n_obs, n_assets = values.shape

    vol = np.zeros((n_obs, n_assets))

    vol[0] = np.std(values, axis=0)

    for t in range(1, n_obs):
        vol[t] = np.sqrt(
            lambda_ * vol[t - 1] ** 2 +
            (1 - lambda_) * values[t - 1] ** 2
        )

    return pd.DataFrame(vol, index=returns.index, columns=returns.columns)


def fhs_var(
    returns: pd.DataFrame,
    portfolio: Portfolio,
    alpha: float,
    n_sims: int = 10000,
    lambda_: float = 0.94,
    seed: int | None = None
) -> float:

    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between 0 and 1.")

    if returns.empty:
        raise ValueError("Returns DataFrame is empty.")

    aligned = returns[portfolio.tickers]

    vol = _ewma_volatility(aligned, lambda_)

    standardized = aligned / vol

    shocks = standardized.to_numpy()

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