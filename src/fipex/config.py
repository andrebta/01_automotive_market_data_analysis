from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
GOLD_DATA_DIR = DATA_DIR / "gold"

SQL_DIR = PROJECT_ROOT / "sql"
DATABASE_FILE = DATA_DIR / "fipex.duckdb"

SNAPSHOT_ID = "2026_09"
DATA_FILE_NAME = f"fipex_prices_{SNAPSHOT_ID}.parquet"

RAW_FILE = RAW_DATA_DIR / DATA_FILE_NAME
PROCESSED_FILE = PROCESSED_DATA_DIR / DATA_FILE_NAME

DIM_DATE_FILE = GOLD_DATA_DIR / "dim_date.parquet"
DIM_VEHICLE_FILE = GOLD_DATA_DIR / "dim_vehicle.parquet"
FACT_PRICES_FILE = GOLD_DATA_DIR / "fct_fipe_prices.parquet"