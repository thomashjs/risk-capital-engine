"""
scenarios.py

Scenario generation utilities for correlation stress.
"""

import numpy as np


def increase_correlation(
    cov: np.ndarray,
    target_corr: float
) -> np.ndarray:

    std = np.sqrt(np.diag(cov))
    corr = cov / np.outer(std, std)

    n = corr.shape[0]
    stressed_corr = corr.copy()

    for i in range(n):
        for j in range(n):
            if i != j:
                stressed_corr[i, j] = target_corr

    stressed_cov = stressed_corr * np.outer(std, std)

    return stressed_cov