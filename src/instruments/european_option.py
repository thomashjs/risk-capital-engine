"""
european_option.py

European option instrument using Black-Scholes pricing.

Assumes factors contain:
- "spot": dict[str, float]
- "vol": dict[str, float]
- "rate": float
- "time": float (time to maturity in years)
"""

from .base import Instrument
from .black_scholes import bs_call_price, bs_put_price


class EuropeanOption(Instrument):

    def __init__(
        self,
        ticker: str,
        strike: float,
        maturity: float,
        option_type: str,
        quantity: float
    ) -> None:

        if option_type not in ("call", "put"):
            raise ValueError("option_type must be 'call' or 'put'")

        self.ticker = ticker
        self.strike = strike
        self.maturity = maturity
        self.option_type = option_type
        self.quantity = quantity

    def price(self, factors: dict) -> float:
        S = factors["spot"][self.ticker]
        sigma = factors["vol"][self.ticker]
        r = factors["rate"]
        T = factors["time"]

        if self.option_type == "call":
            price = bs_call_price(S, self.strike, r, sigma, T)
        else:
            price = bs_put_price(S, self.strike, r, sigma, T)

        return self.quantity * price