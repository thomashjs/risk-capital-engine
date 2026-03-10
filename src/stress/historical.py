"""
historical.py

Historical stress testing utilities.
Extracts stress windows from historical return series.
"""

import pandas as pd


def stress_window(
    returns: pd.DataFrame,
    start: str,
    end: str
) -> pd.DataFrame:
    return returns.loc[start:end]