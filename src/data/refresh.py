"""
refresh.py

Refresh logic for IVolatility datasets.

Responsibilities:
- detect missing data ranges
- call ingestion functions only where needed
- support backfill, forward update, and overwrite

This module orchestrates ingestion. It does NOT load or filter data.
"""

from pathlib import Path
import time
import pandas as pd

from src.data.ivol_ingest import ingest_options_single, ingest_futures, _load_date_set, _save_date_set


# ---------- helpers ----------

def _get_existing_range(parquet_file: Path) -> tuple[pd.Timestamp, pd.Timestamp] | None:
    if not parquet_file.exists():
        return None

    df = pd.read_parquet(parquet_file)

    if df.empty:
        return None

    df["date"] = pd.to_datetime(df["date"])

    return df["date"].min(), df["date"].max()


# ---------- options ----------

def refresh_options(
    symbol: str,
    api_key: str,
    start: str,
    end: str,
    processed_dir: str | Path = "data/processed/ivol",
    overwrite: bool = False,
) -> None:

    root = Path(__file__).resolve().parents[2]
    processed_dir = root / Path(processed_dir)

    parquet_file = processed_dir / f"options_{symbol}.parquet"
    empty_path = processed_dir / f"empty_dates_{symbol}.parquet"
    failed_path = processed_dir / f"failed_dates_{symbol}.parquet"

    start_dt = pd.to_datetime(start)
    end_dt = pd.to_datetime(end)

    existing = _get_existing_range(parquet_file)

    # ---------- no existing data ----------
    if existing is None:
        print(f"[options] No existing data -> full ingest {symbol}")
        dates = list(pd.date_range(start, end, freq="B"))
        ingest_options_single(symbol, api_key, dates)
        return

    all_dates = set(pd.date_range(start_dt, end_dt, freq="B"))

    # ---------- existing data ----------
    if parquet_file.exists():
        df = pd.read_parquet(parquet_file)
        existing_dates = set(pd.to_datetime(df["date"]))
    else:
        existing_dates = set()

    # ---------- known skips ----------
    empty_dates = _load_date_set(empty_path)
    failed_dates = _load_date_set(failed_path)

    # ---------- compute missing ----------
    missing_dates = sorted(
        all_dates - existing_dates - empty_dates - failed_dates
    )

    if not missing_dates:
        print(f"[options] Fully up to date: {symbol}")
        return

    print(f"[options] Fetching {len(missing_dates)} missing dates for {symbol}")

    # ---------- ingest only missing ----------
    chunk_size = 20

    for i in range(0, len(missing_dates), chunk_size):
        chunk = missing_dates[i:i+chunk_size]

        ingest_options_single(
            symbol=symbol,
            api_key=api_key,
            dates=chunk,
        )

        time.sleep(2)  # rate limiting protection

    print(f"[options] Refresh complete for {symbol}")


# ---------- futures ----------

def refresh_futures(
    symbol: str,
    api_key: str,
    start: str,
    end: str,
    processed_dir: str | Path = "data/processed/ivol",
    overwrite: bool = False,
) -> None:

    root = Path(__file__).resolve().parents[2]
    processed_dir = root / Path(processed_dir)
    parquet_file = processed_dir / f"futures_{symbol}.parquet"

    start_dt = pd.to_datetime(start)
    end_dt = pd.to_datetime(end)

    existing = _get_existing_range(parquet_file)

    if existing is None:
        print(f"[futures] No existing data → full ingest {symbol}")
        ingest_futures(symbol, api_key, start, end)
        return

    existing_start, existing_end = existing

    if overwrite:
        print(f"[futures] Overwriting window {symbol}: {start} → {end}")

        df = pd.read_parquet(parquet_file)
        df["date"] = pd.to_datetime(df["date"])

        df = df.loc[(df["date"] < start_dt) | (df["date"] >= end_dt)]

        df.to_parquet(parquet_file)

        ingest_futures(symbol, api_key, start, end)
        return

    # backfill
    if start_dt < existing_start:
        print(f"[futures] Backfilling {symbol}: {start} → {existing_start}")
        ingest_futures(symbol, api_key, start, existing_start.strftime("%Y-%m-%d"))

    # forward update
    if end_dt > existing_end + pd.Timedelta(days=1):
        print(f"[futures] Forward updating {symbol}: {existing_end} → {end}")
        ingest_futures(
            symbol,
            api_key,
            (existing_end + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
            end,
        )

    print(f"[futures] Refresh complete for {symbol}")