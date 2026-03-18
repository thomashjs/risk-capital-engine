"""
stock.py

Stock instrument implementation.

Pricing is linear in spot:
value = shares * spot
"""

from .base import Instrument


class Stock(Instrument):

    def __init__(self, ticker: str, shares: float) -> None:
        self.ticker = ticker
        self.shares = shares

    def price(self, factors: dict) -> float:
        spot = factors["spot"][self.ticker]
        return self.shares * spot