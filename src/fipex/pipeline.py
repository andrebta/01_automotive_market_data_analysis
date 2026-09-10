from fipex.config import RAW_FILE, PROCESSED_FILE
from fipex.io import load_parquet, save_parquet
from fipex.transformations import transform_fipe_data
from fipex.validation import (
    validate_fipe_data,
    validate_processed_data,
)


def run_pipeline() -> None:
    df_raw = load_parquet(RAW_FILE)

    validate_fipe_data(df_raw)

    df = transform_fipe_data(df_raw)

    validate_processed_data(df_raw, df)

    save_parquet(df, PROCESSED_FILE)


if __name__ == "__main__":
    run_pipeline()