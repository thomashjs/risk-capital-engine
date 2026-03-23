"""
black_scholes.py

Black-Scholes pricing functions for European options.
"""

import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq


def bs_call_price(S, K, r, sigma, T):
    if T <= 0:
        return max(S - K, 0.0)

    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)


def bs_put_price(S, K, r, sigma, T):
    if T <= 0:
        return max(K - S, 0.0)

    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

def implied_vol_call(C, S, K, r, T):
    def objective(sigma):
        return bs_call_price(S, K, r, sigma, T) - C
    
    return brentq(objective, 1e-6, 5.0)