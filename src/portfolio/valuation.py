"""
valuation.py

Portfolio valuation and PnL functions for InstrumentPortfolio.
"""

from src.portfolio.instrument_portfolio import InstrumentPortfolio


def portfolio_value(portfolio: InstrumentPortfolio, factors: dict) -> float:
    return sum(inst.price(factors) for inst in portfolio.instruments)


def portfolio_pnl(
    portfolio: InstrumentPortfolio,
    f0: dict,
    f1: dict
) -> float:
    return portfolio_value(portfolio, f1) - portfolio_value(portfolio, f0)