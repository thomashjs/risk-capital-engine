"""
run_stress.py

Utilities for applying stress scenarios to VaR models
and computing the resulting loss distributions.
"""

import pandas as pd
from src.portfolio.positions import Portfolio
from src.portfolio.pnl import compute_portfolio_pnl
from src.risk.var_historical import historical_var
from src.risk.var_parametric import parametric_var
from src.risk.var_montecarlo import mc_var
from src.risk.var_fhs import fhs_var
from src.backtest.rolling import rolling_var_backtest


def stress_var(
    stressed_returns: pd.DataFrame,
    portfolio: Portfolio,
    model: str,
    alpha: float,
    n_sims: int = 10000,
    lambda_: float = 0.94,
    seed: int | None = None
) -> float:

    if stressed_returns.empty:
        raise ValueError("Returns DataFrame is empty.")

    if model == "historical":
        pnl = compute_portfolio_pnl(stressed_returns, portfolio)
        return historical_var(pnl, alpha)

    elif model == "parametric_sample":
        return parametric_var(
            stressed_returns,
            portfolio,
            alpha,
            method="sample"
        )

    elif model == "parametric_ewma":
        return parametric_var(
            stressed_returns,
            portfolio,
            alpha,
            method="ewma",
            lambda_=lambda_
        )

    elif model == "mc_sample":
        return mc_var(
            stressed_returns,
            portfolio,
            alpha,
            n_sims=n_sims,
            method="sample",
            seed=seed
        )

    elif model == "mc_ewma":
        return mc_var(
            stressed_returns,
            portfolio,
            alpha,
            n_sims=n_sims,
            method="ewma",
            lambda_=lambda_,
            seed=seed
        )

    elif model == "fhs":
        return fhs_var(
            stressed_returns,
            portfolio,
            alpha,
            n_sims=n_sims,
            lambda_=lambda_,
            seed=seed
        )

    else:
        raise ValueError(
            "model must be one of: "
            "'historical', 'parametric_sample', 'parametric_ewma', "
            "'mc_sample', 'mc_ewma', 'fhs'."
        )
    
def run_stress(
    returns: pd.DataFrame,
    portfolio: Portfolio,
    start: str,
    end: str,
    model: str,
    alpha: float = 0.99,
    window: int = 250,
    lambda_: float = 0.94,
    n_sims: int = 10000,
    seed: int | None = None,
) -> pd.DataFrame:
    # Possible Optimization:
    # - for non-EWMA models, we can precompute the VaR values for the entire period
    # - for EWMA models, we can precompute the covariance up to crisis date without computing all the VaR values
    results = rolling_var_backtest(
        returns=returns,
        portfolio=portfolio,
        alpha=alpha,
        window=window,
        model=model,
        lambda_=lambda_,
        n_sims=n_sims,
        seed=seed,
    )
    return results.loc[start:end]