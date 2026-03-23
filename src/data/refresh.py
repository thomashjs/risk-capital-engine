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

from src.data.ivol_ingest import ingest_options_single, ingest_futures, _load_key_set, _save_key_set


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
    empty_path = processed_dir / f"empty_keys_{symbol}.parquet"
    failed_path = processed_dir / f"failed_keys_{symbol}.parquet"

    start_dt = pd.to_datetime(start)
    end_dt = pd.to_datetime(end)

    all_dates = set(pd.date_range(start_dt, end_dt, freq="B"))

    # ---------- existing data ----------
    if parquet_file.exists():
        df = pd.read_parquet(parquet_file)
        existing_keys = set(
        zip(pd.to_datetime(df["date"]), df["cp"])
    )
    else:
        existing_keys = set()

    # ---------- known skips ----------
    empty_keys = _load_key_set(empty_path)
    failed_keys = _load_key_set(failed_path)

    # ---------- compute missing ----------.
    missing_calls = []
    missing_puts = []
    for d in all_dates:
        if (d, "C") not in existing_keys and (d, "C") not in empty_keys and (d, "C") not in failed_keys:
            missing_calls.append(d)

        if (d, "P") not in existing_keys and (d, "P") not in empty_keys and (d, "P") not in failed_keys:
            missing_puts.append(d)

    
    if missing_calls:
        print(f"[options] Fetching {len(missing_calls)} missing CALL dates for {symbol}")
        ingest_options_single(
                symbol=symbol,
                api_key=api_key,
                dates=missing_calls,
                cp="C",
            )

    if missing_puts:
        print(f"[options] Fetching {len(missing_puts)} missing PUT dates for {symbol}")
        ingest_options_single(
                symbol=symbol,
                api_key=api_key,
                dates=missing_puts,
                cp="P",
            )

    if not missing_calls and not missing_puts:
        print(f"[options] Fully up to date: {symbol}")
        return

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