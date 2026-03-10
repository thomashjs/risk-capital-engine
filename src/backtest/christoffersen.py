"""
christoffersen.py

Christoffersen independence test and conditional coverage test for VaR backtesting.
"""

import numpy as np
import pandas as pd
from scipy.stats import chi2
from src.backtest.kupiec import kupiec_test

def christoffersen_test(
    backtest: pd.DataFrame
) -> dict:

    if "Exception" not in backtest.columns:
        raise ValueError("Backtest DataFrame must contain 'Exception' column.")

    exceptions = backtest["Exception"].astype(int).to_numpy()

    if len(exceptions) < 2:
        raise ValueError("Backtest must contain at least two observations.")

    n00 = n01 = n10 = n11 = 0

    for t in range(1, len(exceptions)):
        prev = exceptions[t - 1]
        curr = exceptions[t]

        if prev == 0 and curr == 0:
            n00 += 1
        elif prev == 0 and curr == 1:
            n01 += 1
        elif prev == 1 and curr == 0:
            n10 += 1
        else:
            n11 += 1

    pi0 = n01 / (n00 + n01) if (n00 + n01) > 0 else 0
    pi1 = n11 / (n10 + n11) if (n10 + n11) > 0 else 0
    pi = (n01 + n11) / (n00 + n01 + n10 + n11)

    if pi in (0, 1):
        return {
            "LR": np.inf,
            "p_value": 0.0
        }

    log_likelihood_indep = (
        (n00 + n10) * np.log(1 - pi) +
        (n01 + n11) * np.log(pi)
    )

    log_likelihood_markov = (
        n00 * np.log(1 - pi0) +
        n01 * np.log(pi0) +
        n10 * np.log(1 - pi1) +
        n11 * np.log(pi1)
    )

    lr = -2 * (log_likelihood_indep - log_likelihood_markov)

    p_value = 1 - chi2.cdf(lr, df=1)

    return {
        "n00": n00,
        "n01": n01,
        "n10": n10,
        "n11": n11,
        "LR": float(lr),
        "p_value": float(p_value),
    }

def christoffersen_conditional_coverage_test(
    backtest: pd.DataFrame,
    alpha: float
) -> dict:

    kupiec_result = kupiec_test(backtest, alpha)
    independence_result = christoffersen_test(backtest)

    lr_cc = kupiec_result["LR"] + independence_result["LR"]
    p_value = 1 - chi2.cdf(lr_cc, df=2)

    return {
        "LR": float(lr_cc),
        "p_value": float(p_value),
        "kupiec_LR": float(kupiec_result["LR"]),
        "independence_LR": float(independence_result["LR"]),
    }