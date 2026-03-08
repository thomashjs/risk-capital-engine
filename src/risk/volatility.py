import numpy as np
import pandas as pd

def _ewma_volatility(returns: pd.DataFrame, lambda_: float) -> pd.DataFrame:

    values = returns.to_numpy()
    n_obs, n_assets = values.shape

    vol = np.zeros((n_obs, n_assets))

    vol[0] = np.std(values, axis=0) # Initialize with sample std dev

    for t in range(1, n_obs):
        vol[t] = np.sqrt(
            lambda_ * vol[t - 1] ** 2 +
            (1 - lambda_) * values[t - 1] ** 2
        )

    return pd.DataFrame(vol, index=returns.index, columns=returns.columns)