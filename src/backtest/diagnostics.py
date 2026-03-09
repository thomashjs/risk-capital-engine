"""
diagnostics.py

Diagnostics and visualization utilities for VaR backtesting.

Provides tools to:
- visualize VaR forecasts vs realized portfolio losses
- highlight VaR breaches (exceptions)
- summarize exception statistics
"""

import pandas as pd
import matplotlib.pyplot as plt


def plot_var_vs_loss(backtest: pd.DataFrame) -> None:

    if "VaR" not in backtest.columns or "Loss" not in backtest.columns:
        raise ValueError("Backtest DataFrame must contain 'VaR' and 'Loss' columns.")

    plt.figure(figsize=(10, 5))
    plt.plot(backtest.index, backtest["Loss"], label="Loss")
    plt.plot(backtest.index, backtest["VaR"], label="VaR")
    plt.legend()
    plt.title("Portfolio Loss vs VaR")
    plt.xlabel("Date")
    plt.ylabel("Value")
    plt.tight_layout()
    plt.show()


def plot_exceptions(backtest: pd.DataFrame) -> None:

    if "Exception" not in backtest.columns:
        raise ValueError("Backtest DataFrame must contain 'Exception' column.")

    plt.figure(figsize=(10, 5))

    exception_dates = backtest.index[backtest["Exception"]]

    plt.plot(backtest.index, backtest["Loss"], label="Loss")
    plt.plot(backtest.index, backtest["VaR"], label="VaR")

    plt.scatter(
        exception_dates,
        backtest.loc[exception_dates, "Loss"],
        label="Exceptions"
    )

    plt.plot(backtest.index, backtest["VaR"], label="VaR")

    plt.legend()
    plt.title("VaR Exceptions")
    plt.xlabel("Date")
    plt.ylabel("Loss")
    plt.tight_layout()
    plt.show()


def exception_summary(backtest: pd.DataFrame) -> dict:

    if "Exception" not in backtest.columns:
        raise ValueError("Backtest DataFrame must contain 'Exception' column.")

    n = len(backtest)
    exceptions = int(backtest["Exception"].sum())
    rate = exceptions / n

    return {
        "observations": n,
        "exceptions": exceptions,
        "exception_rate": rate
    }