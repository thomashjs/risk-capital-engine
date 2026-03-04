from pathlib import Path
import pandas as pd
import yfinance as yf


def load_prices(
    tickers: list[str],
    start: str,
    end: str,
    raw_dir: str | Path = "data/raw",
    processed_dir: str | Path = "data/processed",
    use_cache: bool = True,
    save: bool = True
) -> pd.DataFrame:
    """
    Download and prepare adjusted close prices for a list of tickers.

    Prices are downloaded from Yahoo Finance and optionally saved to disk
    in both raw CSV format and cleaned parquet format.
"""

    raw_dir = Path(raw_dir)
    processed_dir = Path(processed_dir)

    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

### Check for cached data before downloading
    parquet_file = processed_dir / "prices_clean.parquet"
    if use_cache and parquet_file.exists():
        print("Cached prices available")
        prices_cached = pd.read_parquet(parquet_file)
        if _data_covers_request(prices_cached, tickers, start, end):
            print("Cached data covers request. Loading from cache.")
            return prices_cached.loc[start:end, tickers]
    
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

def _data_covers_request(
    prices: pd.DataFrame,
    tickers: list[str],
    start: str,
    end: str
) -> bool:

    if not all(t in prices.columns for t in tickers):
        return False

    end_dt = pd.to_datetime(end)

    # yfinance end date is exclusive
    if prices.index.max() < end_dt - pd.Timedelta(days=1):
        return False

    return True