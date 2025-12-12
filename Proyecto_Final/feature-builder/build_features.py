import argparse
import pandas as pd
import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, text

def get_engine():
    return create_engine(
        f"postgresql://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}"
        f"@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DB')}"
    )

def load_raw_prices(ticker, start_date=None, end_date=None):
    engine = get_engine()
    query = f"""
        SELECT *
        FROM {os.getenv('PG_SCHEMA_RAW')}.prices_daily
        WHERE ticker = :ticker
    """

    params = {"ticker": ticker}

    if start_date:
        query += " AND date >= :start_date"
        params["start_date"] = start_date

    if end_date:
        query += " AND date <= :end_date"
        params["end_date"] = end_date

    df = pd.read_sql(text(query), engine, params=params)

    #  Convertir explícitamente la columna date
    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values("date")
    return df


def compute_features(df):
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day_of_week"] = df["date"].dt.dayofweek

    df["return_close_open"] = (df["close"] - df["open"]) / df["open"]
    df["return_prev_close"] = df.groupby("ticker")["close"].pct_change()

    df["volatility_5d"] = (
        df.groupby("ticker")["return_prev_close"]
          .rolling(5)
          .std()
          .reset_index(level=0, drop=True)
    )

    df["ingested_at_utc"] = datetime.now(timezone.utc)
    df["run_id"] = os.getenv("RUN_ID")
    return df

def write_features(df, overwrite=False):
    engine = get_engine()

    table = f"{os.getenv('PG_SCHEMA_ANALYTICS')}.daily_features"

    if overwrite:
        print("Sobrescribiendo tabla completa…")
        df.to_sql("daily_features", engine, schema=os.getenv("PG_SCHEMA_ANALYTICS"),
                  if_exists="replace", index=False)
        return

    # Idempotente por PK (date, ticker)
    print("Insertando (idempotente)…")
    df.to_sql("daily_features", engine, schema=os.getenv("PG_SCHEMA_ANALYTICS"),
              if_exists="append", index=False, method="multi")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["full", "by-date-range"])
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--run-id")
    parser.add_argument("--overwrite", default="false")

    args = parser.parse_args()

    df = load_raw_prices(args.ticker, args.start_date, args.end_date)
    df = compute_features(df)

    write_features(df, overwrite=args.overwrite.lower() == "true")

    print(f"Procesadas {len(df)} filas para {args.ticker}")
    print(f"Fecha min: {df.date.min()}, max: {df.date.max()}")


if __name__ == "__main__":
    main()

