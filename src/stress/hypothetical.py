"""
hypothetical.py

Hypothetical stress scenario transformations applied
to return series.
"""

import pandas as pd


def apply_vol_scaling(
    returns: pd.DataFrame,
    scale: float
) -> pd.DataFrame:
    return returns * scale