"""
run_data.py

Driver script for IVolatility data ingestion and refresh.

Usage:
- initial historical pull
- periodic refresh
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from src.data.ivol_ingest import ingest_options_parallel
from src.utils.config import load_config
from src.data.refresh import refresh_options, refresh_futures


def main():
    load_dotenv()
    # --- load configs ---
    root = Path(__file__).resolve().parent

    load_dotenv(root / ".env")

    portfolio_cfg = load_config(root / "configs/portfolio.yaml")
    data_cfg = load_config(root / "configs/data.yaml")

    api_key = os.getenv("IVOL_API_KEY")
    if api_key is None:
        raise ValueError("IVOL_API_KEY must be set in .env file")

    tickers = portfolio_cfg["portfolio"]["tickers"]

    start = data_cfg["ivol"]["start"]
    end = data_cfg["ivol"]["end"]

    # ---------- OPTIONS ----------
    print("\n=== OPTIONS INGEST ===")

    for ticker in tickers:
        try:
            refresh_options(
                symbol=ticker,
                api_key=api_key,
                start=start,
                end=end,
            )
        except Exception as e:
            print(f"[ERROR] options {ticker}: {e}")

    #     # parallel version (for initial backfill)
    #     ingest_options_parallel(
    #     symbols=tickers,
    #     api_key=api_key,
    #     start=start,
    #     end=end,
    #     max_workers=2,   # safe default
    # )

    # ---------- FUTURES ----------
    # print("\n=== FUTURES INGEST ===")

    # futures_symbols = data_cfg["ivol"].get("futures_symbols", [])

    # for symbol in futures_symbols:
    #     try:
    #         refresh_futures(
    #             symbol=symbol,
    #             api_key=api_key,
    #             start=start,
    #             end=end,
    #         )
    #     except Exception as e:
    #         print(f"[ERROR] futures {symbol}: {e}")

    print("\n=== DATA INGEST COMPLETE ===")


if __name__ == "__main__":
    main()