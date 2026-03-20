"""
options_loader.py

Query interface for options data stored locally.

Responsibilities:
- load processed options parquet
- filter by symbol, date range, strikes, maturities
- optionally trigger refresh if data is missing

This module NEVER directly calls the API.
"""

from pathlib import Path
import pandas as pd

# Optional import (only used if refresh=True)
try:
    from src.data.refresh import refresh_options
except ImportError:
    refresh_options = None


def load_options(
    symbol: str,
    start: str,
    end: str,
    processed_dir: str | Path = "data/processed/ivol",
    use_cache: bool = True,
    refresh: bool = False,
    api_key: str | None = None,
    strike_min: float | None = None,
    strike_max: float | None = None,
    call_put: str | None = None,
) -> pd.DataFrame:

    root = Path(__file__).resolve().parents[2]
    processed_dir = root / Path(processed_dir)
    parquet_file = processed_dir / f"options_{symbol}.parquet"

    if not parquet_file.exists():
        if not refresh:
            raise FileNotFoundError(f"No local data for {symbol}")
        if refresh_options is None:
            raise ImportError("refresh_options not available")
        if api_key is None:
            raise ValueError("api_key must be provided when refresh=True")
        print(f"No local data. Triggering initial ingest for {symbol}")
        refresh_options(symbol, api_key, start, end)

    df = pd.read_parquet(parquet_file)

    # --- ensure datetime ---
    if "date" not in df.columns:
        raise ValueError("Options data must contain 'date' column")

    df["date"] = pd.to_datetime(df["date"])

    # --- coverage check ---
    if use_cache:
        if not _data_covers_request(df, start, end):
            if not refresh:
                raise ValueError("Local data does not cover requested range")
            if refresh_options is None:
                raise ImportError("refresh_options not available")
            if api_key is None:
                raise ValueError("api_key must be provided when refresh=True")
            print(f"Refreshing missing data for {symbol}")
            refresh_options(symbol, api_key, start, end)
            df = pd.read_parquet(parquet_file)

    # --- filtering ---
    mask = (df["date"] >= start) & (df["date"] <= end)

    if strike_min is not None:
        mask &= df["strike"] >= strike_min

    if strike_max is not None:
        mask &= df["strike"] <= strike_max

    if call_put is not None:
        mask &= df["callPut"] == call_put

    df = df.loc[mask].copy()

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