"""
futures_loader.py

Query interface for futures data stored locally.

Responsibilities:
- load processed futures parquet
- filter by symbol and date range
- optionally trigger refresh if data is missing

This module NEVER directly calls the API.
"""

from pathlib import Path
import pandas as pd

try:
    from src.data.refresh import refresh_futures
except ImportError:
    refresh_futures = None


def load_futures(
    symbol: str,
    start: str,
    end: str,
    processed_dir: str | Path = "data/processed/ivol",
    use_cache: bool = True,
    refresh: bool = False,
    api_key: str | None = None,
) -> pd.DataFrame:

    root = Path(__file__).resolve().parents[2]
    processed_dir = root / Path(processed_dir)
    parquet_file = processed_dir / f"futures_{symbol}.parquet"

    if not parquet_file.exists():
        if not refresh:
            raise FileNotFoundError(f"No local data for {symbol}")
        if refresh_futures is None:
            raise ImportError("refresh_futures not available")
        if api_key is None:
                raise ValueError("api_key must be provided when refresh=True")
        
        print(f"No local data. Triggering initial ingest for {symbol}")
        refresh_futures(symbol, api_key, start, end)

    df = pd.read_parquet(parquet_file)

    if "date" not in df.columns:
        raise ValueError("Futures data must contain 'date' column")

    df["date"] = pd.to_datetime(df["date"])

    # --- coverage check ---
    if use_cache:
        if not _data_covers_request(df, start, end):
            if not refresh:
                raise ValueError("Local data does not cover requested range")
            if refresh_futures is None:
                raise ImportError("refresh_futures not available")
            if api_key is None:
                raise ValueError("api_key must be provided when refresh=True")
            
            print(f"Refreshing missing data for {symbol}")
            refresh_futures(symbol, api_key, start, end)
            df = pd.read_parquet(parquet_file)

    # --- filtering ---
    df = df.loc[(df["date"] >= start) & (df["date"] <= end)].copy()

    return df


def _data_covers_request(
    df: pd.DataFrame,
    start: str,
    end: str
) -> bool:

    if df.empty:
        return False

    start_dt = pd.to_datetime(start)
    end_dt = pd.to_datetime(end)

    if df["date"].min() > start_dt:
        return False

    # end is exclusive
    if df["date"].max() < end_dt - pd.Timedelta(days=1):
        return False

    return True