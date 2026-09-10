from pathlib import Path

import pandas as pd


def load_parquet(file_path: Path) -> pd.DataFrame:
    if not file_path.exists():
        raise FileNotFoundError(
            f"Parquet file not found: {file_path}"
        )

    return pd.read_parquet(file_path)


def save_parquet(
    df: pd.DataFrame,
    file_path: Path,
) -> None:
    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_parquet(
        file_path,
        index=False,
    )