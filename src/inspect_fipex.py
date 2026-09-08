from pathlib import Path
import pandas as pd

DATA_PATH = Path("data/raw/fipex_prices_2026_09.parquet")

df = pd.read_parquet(DATA_PATH)

print("\n--- First rows ---")
print(df.head())

print("\n--- Shape ---")
print(df.shape)

print('\n--- Columns ---')
print(df.columns.tolist())

print('\n--- Data types ---')
print(df.dtypes)

print('\n--- Missing values ---')
print(df.isna().sum())

print("\n--- Unique values per column ---")
for column in df.columns:
    print(f"{column}: {df[column].nunique()}")

print("\n--- Duplicate rows ---")
print(df.duplicated().sum())

print("\n--- Sample values ---")
for column in df.columns:
    print(f"\n{column}:")
    print(df[column].dropna().unique()[:10])

print("\n--- Missing ano_modelo by zero_km ---")
print(
    df[df["ano_modelo"].isna()]
    ["zero_km"]
    .value_counts()
)

print("\n--- Missing ano_modelo sample ---")
print(
    df[df["ano_modelo"].isna()][
        [
            "codigo_fipe",
            "nome_modelo",
            "nome_marca",
            "zero_km",
            "valor_formatado"
        ]
    ].head(20)
)

key_columns = [
    "codigo_fipe",
    "ano_modelo",
    "zero_km",
    "mes_referencia",
    "ano_referencia"
]

print("\n--- Duplicate logical keys ---")
print(
    df.duplicated(
        subset=key_columns,
        keep=False
    ).sum()
)

duplicates = df[
    df.duplicated(
        subset=key_columns,
        keep=False
    )
].sort_values(key_columns)

print(duplicates)