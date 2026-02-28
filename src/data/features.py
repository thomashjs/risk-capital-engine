import numpy as np
import pandas as pd


def compute_log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Compute daily log returns from price data.

    Parameters
    ----------
    prices : pd.DataFrame
        Adjusted close prices indexed by date.

    Returns
    -------
    pd.DataFrame
        Log returns indexed by date.
    """
    returns = (prices / prices.shift(1)).apply(np.log)
    return returns.dropna()


def compute_simple_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Compute daily simple returns from price data.

    Parameters
    ----------
    prices : pd.DataFrame
        Adjusted close prices indexed by date.

    Returns
    -------
    pd.DataFrame
        Simple returns indexed by date.
    """
    returns = prices.pct_change()
    return returns.dropna()