from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

RAW_FILE = RAW_DATA_DIR / "fipex_prices_2026_09.parquet"
PROCESSED_FILE = PROCESSED_DATA_DIR / "fipex_prices_2026_09.parquet"