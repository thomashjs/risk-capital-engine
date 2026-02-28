"""
positions.py

Defines the Portfolio object and portfolio construction logic.

This module is responsible only for portfolio structure:
- Tickers
- Weights
- Notional exposure

Valuation and PnL logic are handled separately.
"""

import numpy as np


class Portfolio:

    def __init__(
        self,
        tickers: list[str],
        weights: np.ndarray,
        notional: float
    ) -> None:

        if len(tickers) != len(weights):
            raise ValueError("Tickers and weights must have equal length.")

        if not np.isclose(np.sum(weights), 1.0):
            raise ValueError("Portfolio weights must sum to 1.")

        self.tickers = tickers
        self.weights = np.array(weights)
        self.notional = notional

    @classmethod
    def from_equal_weight(
        cls,
        tickers: list[str],
        notional: float
    ) -> "Portfolio":

        n = len(tickers)
        weights = np.ones(n) / n
        return cls(tickers, weights, notional)