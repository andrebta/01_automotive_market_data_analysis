import duckdb

from fipex.config import (
    RAW_FILE,
    PROCESSED_FILE,
    GOLD_DATA_DIR,
    DATABASE_FILE,
    SQL_DIR,
)
from fipex.io import load_parquet, save_parquet
from fipex.transformations import transform_fipe_data
from fipex.validation import validate_fipe_data, validate_processed_data


SQL_FILES = [
    SQL_DIR / "staging" / "01_stg_fipe_prices.sql",
    SQL_DIR / "intermediate" / "01_int_vehicle.sql",
    SQL_DIR / "intermediate" / "02_int_fipe_prices.sql",
    SQL_DIR / "marts" / "01_dim_date.sql",
    SQL_DIR / "marts" / "02_dim_vehicle.sql",
    SQL_DIR / "marts" / "03_fct_fipe_prices.sql",
    SQL_DIR / "export" / "01_export_gold.sql",
]


def run_python_pipeline() -> None:
    print("Running Python pipeline...")

    df_raw = load_parquet(RAW_FILE)
    validate_fipe_data(df_raw)

    df = transform_fipe_data(df_raw)
    validate_processed_data(df_raw, df)

    save_parquet(df, PROCESSED_FILE)

    print("Python pipeline completed.")


def prepare_gold_directory() -> None:
    GOLD_DATA_DIR.mkdir(parents=True, exist_ok=True)

    for file_path in GOLD_DATA_DIR.glob("*.parquet"):
        file_path.unlink()


def execute_sql_file(
    connection: duckdb.DuckDBPyConnection,
    file_path,
) -> None:
    sql = file_path.read_text(encoding="utf-8")
    connection.execute(sql)

    print(f"Executed: {file_path.relative_to(SQL_DIR)}")


def run_sql_pipeline() -> None:
    print("Running SQL pipeline...")

    prepare_gold_directory()

    connection = duckdb.connect(str(DATABASE_FILE))

    try:
        connection.execute("DROP TABLE IF EXISTS fct_fipe_prices;")
        connection.execute("DROP TABLE IF EXISTS dim_vehicle;")
        connection.execute("DROP TABLE IF EXISTS dim_date;")

        for sql_file in SQL_FILES:
            execute_sql_file(connection, sql_file)
    finally:
        connection.close()

    print("SQL pipeline completed.")


def run_pipeline() -> None:
    print("Starting FIPEX pipeline...")

    run_python_pipeline()
    run_sql_pipeline()

    print("FIPEX pipeline completed successfully.")


if __name__ == "__main__":
    run_pipeline()