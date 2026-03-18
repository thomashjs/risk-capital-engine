"""
base.py

Defines the base Instrument interface for all tradable assets.

All instruments must implement:
- price(factors): current market value
- pnl(f0, f1): PnL between two factor states

Factors are passed as dictionaries and must be consistent across the system.
"""

from abc import ABC, abstractmethod


class Instrument(ABC):

    @abstractmethod
    def price(self, factors: dict) -> float:
        """Return current market value given risk factors."""
        raise NotImplementedError

    def pnl(self, f0: dict, f1: dict) -> float:
        """Default PnL via full revaluation."""
        return self.price(f1) - self.price(f0)