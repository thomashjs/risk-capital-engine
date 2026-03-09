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

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(backtest.index, backtest["Loss"], label="Loss")
    ax.plot(backtest.index, backtest["VaR"], label="VaR")
    ax.legend()
    ax.set_title(f"Portfolio Loss vs VaR ({backtest['Model'].iloc[0]})")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value")

    fig.tight_layout()
    plt.show()


def plot_exceptions(backtest: pd.DataFrame) -> None:

    if "Exception" not in backtest.columns:
        raise ValueError("Backtest DataFrame must contain 'Exception' column.")

    exception_dates = backtest.index[backtest["Exception"]]

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(backtest.index, backtest["Loss"], label="Loss")
    ax.plot(backtest.index, backtest["VaR"], label="VaR")

    ax.scatter(
        exception_dates,
        backtest.loc[exception_dates, "Loss"],
        c = "red",
        alpha=0.5,
        label="Exceptions",
        zorder=5
    )

    ax.legend()
    ax.set_title(f"VaR Exceptions ({backtest['Model'].iloc[0]})")
    ax.set_xlabel("Date")
    ax.set_ylabel("Loss")
    fig.tight_layout()
    plt.show()

def plot_var_comparison(backtests: dict[str, pd.DataFrame]) -> None:
    first = next(iter(backtests.values()))
    loss = first["Loss"]

    fig, ax = plt.subplots(figsize=(10,5))

    ax.plot(first.index, loss, color="black", label="Loss", alpha=0.6)

    for name, bt in backtests.items():
        ax.plot(bt.index, bt["VaR"], label=name, alpha=0.7)

    ax.legend()
    ax.set_title("VaR Model Comparison")
    ax.set_xlabel("Date")
    ax.set_ylabel("Loss")

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

def plot_exception_counts(backtests: dict[str, pd.DataFrame]) -> None:

    counts = {
        name: int(bt["Exception"].sum())
        for name, bt in backtests.items()
    }

    fig, ax = plt.subplots(figsize=(6,4))

    bars = ax.bar(list(counts.keys()), list(counts.values()))
    ax.bar_label(bars)
    ax.set_title("VaR Exceptions by Model")
    ax.set_ylabel("Count")
    fig.tight_layout()

    plt.show()