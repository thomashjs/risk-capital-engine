"""
scenarios.py

Scenario generation utilities for correlation stress.
"""

import numpy as np


def increase_correlation(
    cov: np.ndarray,
    target_corr: float,
    beta: float = 0.5
) -> np.ndarray:

    std = np.sqrt(np.diag(cov))
    target_cov = target_corr * np.outer(std, std)
    
    return (1 - beta) * cov + beta * target_cov