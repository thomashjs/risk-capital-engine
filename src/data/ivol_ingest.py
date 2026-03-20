"""
ivol_ingest.py

Bulk and incremental ingestion for IVolatility data.

Responsibilities:
- download raw option and futures data from IVolatility API
- support historical backfill and incremental refresh
- store raw data to disk
- append/update processed parquet datasets

This is NOT a query loader. It is an ingestion pipeline.
"""

from pathlib import Path
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed


BASE_URL = "https://restapi.ivolatility.com"


# ---------- helpers ----------

def _get(url: str, params: dict, retries: int = 5) -> pd.DataFrame:
    for i in range(retries):
        r = requests.get(url, params=params)

        # rate limit
        if r.status_code == 429:
            wait = 2 ** i
            print(f"Rate limited. Sleeping {wait}s...")
            time.sleep(wait)
            continue
        # server errors
        if r.status_code in (500, 502, 503):
            wait = 2 ** i
            print(f"Server error {r.status_code}. Retry {i+1}/{retries}...")
            time.sleep(wait)
            continue
        # other errors (non-retryable)
        if r.status_code != 200:
            print(f"[WARN] Skipping request: {r.status_code}")
            return pd.DataFrame()

        r.raise_for_status()
        data = r.json()

        if isinstance(data, dict):
            if "data" in data:
                data = data["data"]
            else:
                return pd.json_normalize(data)

        return pd.DataFrame(data)
    
    print("[WARN] Max retries exceeded → skipping")
    raise RuntimeError("Max retries exceeded")


def _date_range_chunks(start: str, end: str, days: int = 90):
    start_dt = pd.to_datetime(start)
    end_dt = pd.to_datetime(end)

    current = start_dt
    while current < end_dt:
        chunk_end = min(current + timedelta(days=days), end_dt)
        yield current.strftime("%Y-%m-%d"), chunk_end.strftime("%Y-%m-%d")
        current = chunk_end

def _load_date_set(path: Path) -> set[pd.Timestamp]:
    if not path.exists():
        return set()
    df = pd.read_parquet(path)
    return set(pd.to_datetime(df["date"]))


def _save_date_set(path: Path, dates: set[pd.Timestamp]) -> None:
    if not dates:
        return
    df = pd.DataFrame({"date": sorted(dates)})
    df.to_parquet(path)


# ---------- options ingestion ----------

def ingest_options_single(
    symbol: str,
    api_key: str,
    dates: list[pd.Timestamp],
    raw_dir: str | Path = "data/raw/ivol/options",
    processed_dir: str | Path = "data/processed/ivol",
) -> None:

    root = Path(__file__).resolve().parents[2]
    raw_dir = root / Path(raw_dir)
    processed_dir = root / Path(processed_dir)

    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    all_data = []

    empty_dates = set()
    failed_dates = set()

    for i, d in enumerate(dates):
        date_str = d.strftime("%Y-%m-%d")
        if i % 50 == 0:
            print(f"{symbol}: {i}/{len(dates)}")
        
        try:
            df = _get(
                f"{BASE_URL}/equities/eod/stock-opts-by-param",
                params={
                    "apiKey": api_key,
                    "symbol": symbol,
                    "tradeDate": date_str,
                    "dteFrom": 7,
                    "dteTo": 60,
                    "cp": "C",
                    "moneynessFrom": -10,
                    "moneynessTo": 10,
                },
            )
        except Exception as e:
            failed_dates.add(d)
            print(f"[WARN] {symbol} {date_str} failed: {e}")
            continue

        # Record empty dates
        if df.empty:
            empty_dates.add(d)
            continue

        if not df.empty:
            # attach trade date explicitly (important!)
            df["date"] = d
            df["symbol"] = symbol
            all_data.append(df)
        # rate limiting protection
        time.sleep(0.3)

    # save empty dates tracking
    empty_path = processed_dir / f"empty_dates_{symbol}.parquet"
    failed_path = processed_dir / f"failed_dates_{symbol}.parquet"

    existing_empty = _load_date_set(empty_path)
    existing_failed = _load_date_set(failed_path)

    _save_date_set(empty_path, existing_empty | empty_dates)
    _save_date_set(failed_path, existing_failed | failed_dates)

    if not all_data:
        print("No data downloaded.")
        return

    full_df = pd.concat(all_data, ignore_index=True)

    parquet_file = processed_dir / f"options_{symbol}.parquet"

    if parquet_file.exists():
        existing = pd.read_parquet(parquet_file)
        full_df = pd.concat([existing, full_df], ignore_index=True)

        # deduplicate (IMPORTANT: use subset if possible later)
        full_df = full_df.drop_duplicates()

    full_df.to_parquet(parquet_file)

    print(f"[{symbol}] Saved -> {parquet_file}")

# ------------------ parallel version --------------------

def ingest_options_parallel(
    symbols: list[str],
    api_key: str,
    dates: list[pd.Timestamp],
    processed_dir: str | Path = "data/processed/ivol",
    max_workers: int = 2,  # IMPORTANT: keep small to avoid 429
) -> None:

    root = Path(__file__).resolve().parents[2]
    processed_dir = root / Path(processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== PARALLEL OPTIONS INGEST ({len(symbols)} tickers) ===")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                ingest_options_single,
                symbol,
                api_key,
                dates,
                processed_dir = processed_dir,
            )
            for symbol in symbols
        ]

        for f in as_completed(futures):
            try:
                f.result()
            except Exception as e:
                print(f"[ERROR] {e}")

    print("\n=== INGEST COMPLETE ===")

# ---------- futures ingestion ----------

def ingest_futures(
    symbol: str,
    api_key: str,
    start: str,
    end: str,
    raw_dir: str | Path = "data/raw/ivol/futures",
    processed_dir: str | Path = "data/processed/ivol",
    chunk_days: int = 30,
) -> None:

    root = Path(__file__).resolve().parents[2]
    raw_dir = root / Path(raw_dir)
    processed_dir = root / Path(processed_dir)

    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    all_chunks = []

    for s, e in _date_range_chunks(start, end, chunk_days):
        print(f"Downloading futures {symbol}: {s} → {e}")

        df = _get(
            f"{BASE_URL}/futures/single-futures",
            {
                "apiKey": api_key,
                "symbol": symbol,
                "from": s,
                "to": e,
            },
        )

        if df.empty:
            continue

        file = raw_dir / f"{symbol}_{s}_{e}.csv"
        df.to_csv(file, index=False)

        all_chunks.append(df)

    if not all_chunks:
        print("No data downloaded.")
        return

    full_df = pd.concat(all_chunks, ignore_index=True)

    parquet_file = processed_dir / f"futures_{symbol}.parquet"

    if parquet_file.exists():
        existing = pd.read_parquet(parquet_file)
        full_df = pd.concat([existing, full_df], ignore_index=True)
        full_df = full_df.drop_duplicates()

    full_df.to_parquet(parquet_file)

    print(f"Saved processed futures -> {parquet_file}")