"""
instrument_portfolio.py

Portfolio representation for general instruments.

Stores a collection of Instrument objects.
Valuation and PnL are handled externally.
"""

from src.instruments.base import Instrument


class InstrumentPortfolio:

    def __init__(self, instruments: list[Instrument]) -> None:
        if len(instruments) == 0:
            raise ValueError("Portfolio must contain at least one instrument.")

        self.instruments = instruments