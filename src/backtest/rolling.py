"""
rolling.py

Rolling backtesting framework for VaR models.

For each day after the initial estimation window:
- fit the selected VaR model on the trailing window
- forecast 1-day VaR
- observe next-day realized portfolio PnL
- record whether an exception occurred
"""

import pandas as pd
from src.portfolio.positions import Portfolio
from src.portfolio.pnl import compute_portfolio_pnl
from src.risk.var_historical import historical_var
from src.risk.var_parametric import parametric_var
from src.risk.var_montecarlo import mc_var
from src.risk.var_fhs import fhs_var


def rolling_var_backtest(
    returns: pd.DataFrame,
    portfolio: Portfolio,
    alpha: float,
    window: int,
    model: str,
    n_sims: int = 10000,
    lambda_: float = 0.94,
    seed: int | None = None
) -> pd.DataFrame:

    if returns.empty:
        raise ValueError("Returns DataFrame is empty.")

    if window <= 0:
        raise ValueError("window must be positive.")

    if len(returns) <= window:
        raise ValueError("Returns length must exceed backtest window.")

    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between 0 and 1.")

    aligned = returns[portfolio.tickers]

    portfolio_pnl = compute_portfolio_pnl(aligned, portfolio)

    dates = []
    var_values = []
    realized_pnl_values = []
    exceptions = []

    for t in range(window, len(aligned)):
        window_returns = aligned.iloc[t - window:t]
        next_day_pnl = float(portfolio_pnl.iloc[t])

        if model == "historical":
            window_pnl = portfolio_pnl.iloc[t - window:t]
            var_value = historical_var(window_pnl, alpha)
        elif model == "parametric_sample":
            var_value = parametric_var(
                window_returns,
                portfolio,
                alpha,
                method="sample"
            )
        elif model == "parametric_ewma":
            var_value = parametric_var(
                window_returns,
                portfolio,
                alpha,
                method="ewma",
                lambda_=lambda_
            )
        elif model == "mc_sample":
            model_seed = None if seed is None else seed + t
            var_value = mc_var(
                window_returns,
                portfolio,
                alpha,
                n_sims=n_sims,
                method="sample",
                seed=model_seed
            )
        elif model == "mc_ewma":
            model_seed = None if seed is None else seed + t
            var_value = mc_var(
                window_returns,
                portfolio,
                alpha,
                n_sims=n_sims,
                method="ewma",
                lambda_=lambda_,
                seed=model_seed
            )
        elif model == "fhs":
            model_seed = None if seed is None else seed + t
            var_value = fhs_var(
                window_returns,
                portfolio,
                alpha,
                n_sims=n_sims,
                lambda_=lambda_,
                seed=model_seed
            )
        else:
            raise ValueError(
                "model must be one of: "
                "'historical', 'parametric_sample', 'parametric_ewma', "
                "'mc_sample', 'mc_ewma', 'fhs'."
            )

        exception = next_day_pnl < -var_value

        dates.append(aligned.index[t])
        var_values.append(var_value)
        realized_pnl_values.append(next_day_pnl)
        exceptions.append(exception)
    
    result = pd.DataFrame(
        {
            "VaR": var_values,
            "PnL": realized_pnl_values,
            "Exception": exceptions,
        },
        index=dates,
        )
    result["Loss"] = -result["PnL"]
    result["Model"] = model
    result["Alpha"] = alpha
    
    return result