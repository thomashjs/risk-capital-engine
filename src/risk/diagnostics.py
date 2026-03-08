"""
diagnostics.py

Residual diagnostics for volatility filtering models.

Provides statistical checks to evaluate whether standardized
returns behave approximately iid in time.

Diagnostics include:
- Mean and variance checks
- Ljung-Box test for autocorrelation
- Ljung-Box test for volatility clustering
"""

import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox

def residual_diagnostics(
    standardized_returns: pd.DataFrame,
    lags: int = 10
) -> pd.DataFrame:
    
    z = standardized_returns.to_numpy()

    results = []

    for i, col in enumerate(standardized_returns.columns):

        series = z[:, i]

        mean = np.mean(series)
        var = np.var(series)

        lb = acorr_ljungbox(series, lags=[lags], return_df=True)
        lb_sq = acorr_ljungbox(series**2, lags=[lags], return_df=True)

        results.append({
            "asset": col,
            "mean": mean,
            "variance": var,
            "ljung_box_pvalue": lb["lb_pvalue"].iloc[0],
            "ljung_box_sq_pvalue": lb_sq["lb_pvalue"].iloc[0]
        })

    return pd.DataFrame(results)