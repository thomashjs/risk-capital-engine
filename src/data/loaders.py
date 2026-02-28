from pathlib import Path
import pandas as pd
import yfinance as yf


def load_prices(
    tickers: list[str],
    start: str,
    end: str,
    raw_dir: str | Path = "data/raw",
    processed_dir: str | Path = "data/processed",
    save: bool = True
) -> pd.DataFrame:
    """
    Download and prepare adjusted close prices for a list of tickers.

    Prices are downloaded from Yahoo Finance and optionally saved to disk
    in both raw CSV format and cleaned parquet format.

    Parameters
    ----------
    tickers : list[str]
        List of ticker symbols.
    start : str
        Start date (YYYY-MM-DD).
    end : str
        End date (YYYY-MM-DD).
    raw_dir : str or Path
        Directory for storing raw downloaded CSV files.
    processed_dir : str or Path
        Directory for storing cleaned parquet files.
    save : bool
        Whether to persist data to disk.

    Returns
    -------
    pd.DataFrame
        DataFrame of adjusted close prices indexed by date.
    """

    raw_dir = Path(raw_dir)
    processed_dir = Path(processed_dir)

    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    data = yf.download(
        tickers=tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False
    )

    if data is None or data.empty:
        raise ValueError("Downloaded price data is empty.")

    # Handle multi-index columns
    if isinstance(data.columns, pd.MultiIndex):
        prices = data["Close"]
    else:
        prices = data

    if isinstance(prices, pd.Series):
        prices = prices.to_frame()
        
    prices = prices.dropna(how="all")

    if save:
        prices.to_csv(raw_dir / "prices_raw.csv")
        prices.to_parquet(processed_dir / "prices_clean.parquet")

    return prices