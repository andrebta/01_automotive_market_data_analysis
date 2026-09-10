import pandas as pd


EXPECTED_COLUMNS = [
    "mes_referencia",
    "ano_referencia",
    "tipo_veiculo",
    "codigo_fipe",
    "nome_marca",
    "nome_modelo",
    "ano_modelo",
    "zero_km",
    "nome_combustivel",
    "sigla_combustivel",
    "valor_centavos",
    "valor_formatado",
]


SNAPSHOT_KEY = [
    "codigo_fipe",
    "ano_modelo",
    "zero_km",
    "sigla_combustivel",
]


EXPECTED_VEHICLE_TYPES = {
    "carro",
    "caminhão",
    "moto",
}


EXPECTED_FUEL_MAPPING = {
    "Gasolina": "g",
    "Diesel": "d",
    "Flex": "f",
    "Híbrido": "h",
    "Elétrico": "l",
    "Álcool": "e",
    "Gás Natural": "n",
}

EXPECTED_PROCESSED_DTYPES = {
    "mes_referencia": "int64",
    "ano_referencia": "int64",
    "ano_modelo": "Int64",
    "zero_km": "bool",
    "valor_centavos": "int64",
}

CURRENCY_PATTERN = r"^R\$ \d{1,3}(\.\d{3})*,\d{2}$"

# 1. Schema Validation

def validate_schema(df: pd.DataFrame) -> None:
    actual_columns = set(df.columns)
    expected_columns = set(EXPECTED_COLUMNS)

    missing_columns = expected_columns - actual_columns
    unexpected_columns = actual_columns - expected_columns

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    if unexpected_columns:
        raise ValueError(
            f"Unexpected columns: {unexpected_columns}"
        )

# 2. Completeness Validation

def validate_completeness(df: pd.DataFrame) -> None:
    codigo_fipe_nulls = df["codigo_fipe"].isna().sum()

    if codigo_fipe_nulls > 0:
        raise ValueError(
            f"DQ001 failed: codigo_fipe contains "
            f"{codigo_fipe_nulls} null values."
        )

    required_columns = [
        column
        for column in df.columns
        if column != "ano_modelo"
    ]

    null_counts = df[required_columns].isna().sum()
    columns_with_nulls = null_counts[null_counts > 0]

    if not columns_with_nulls.empty:
        raise ValueError(
            f"DQ002 failed: unexpected null values found:\n"
            f"{columns_with_nulls}"
        )

    invalid_null_model_year = df[
        df["ano_modelo"].isna()
        & ~df["zero_km"]
    ]

    invalid_zero_km = df[
        df["zero_km"]
        & df["ano_modelo"].notna()
    ]

    if not invalid_null_model_year.empty:
        raise ValueError(
            "DQ003 failed: ano_modelo is null "
            "for non-zero-km vehicles."
        )

    if not invalid_zero_km.empty:
        raise ValueError(
            "DQ003 failed: zero-km vehicles contain "
            "non-null ano_modelo."
        )

# 3. Grain Validation

def validate_snapshot_grain(df: pd.DataFrame) -> None:
    duplicate_mask = df.duplicated(
        subset=SNAPSHOT_KEY,
        keep=False,
    )

    duplicate_records = df.loc[duplicate_mask]

    if not duplicate_records.empty:
        raise ValueError(
            f"DQ004 failed: {len(duplicate_records)} rows "
            "violate the snapshot grain."
        )

# 4. Domain Validation

def validate_domains(df: pd.DataFrame) -> None:
    actual_vehicle_types = set(
        df["tipo_veiculo"].dropna().unique()
    )

    unexpected_vehicle_types = (
        actual_vehicle_types - EXPECTED_VEHICLE_TYPES
    )

    if unexpected_vehicle_types:
        raise ValueError(
            f"DQ006 failed: unexpected tipo_veiculo values: "
            f"{unexpected_vehicle_types}"
        )

    invalid_months = df[
        ~df["mes_referencia"].between(1, 12)
    ]

    if not invalid_months.empty:
        raise ValueError(
            f"DQ014 failed: {len(invalid_months)} rows contain "
            "invalid mes_referencia values."
        )

    reference_year = df["ano_referencia"].iloc[0]

    invalid_model_years = df[
        df["ano_modelo"].notna()
        & (
            (df["ano_modelo"] < 1900)
            | (df["ano_modelo"] > reference_year + 1)
        )
    ]

    if not invalid_model_years.empty:
        raise ValueError(
            "Invalid ano_modelo values found."
        )

# 5. Functional Dependecies

def validate_functional_dependencies(
    df: pd.DataFrame,
) -> None:
    expected_fuel_code = df["nome_combustivel"].map(
        EXPECTED_FUEL_MAPPING
    )

    invalid_fuel_mapping = df[
        df["sigla_combustivel"] != expected_fuel_code
    ]

    if not invalid_fuel_mapping.empty:
        raise ValueError(
            f"DQ007 failed: {len(invalid_fuel_mapping)} rows "
            "contain inconsistent fuel mappings."
        )

    fipe_code_mapping = (
        df[
            ["codigo_fipe", "nome_marca", "nome_modelo"]
        ]
        .drop_duplicates()
        .groupby("codigo_fipe")
        .size()
    )

    invalid_fipe_codes = fipe_code_mapping[
        fipe_code_mapping > 1
    ]

    if not invalid_fipe_codes.empty:
        raise ValueError(
            f"DQ008 failed: {len(invalid_fipe_codes)} "
            "codigo_fipe values map to multiple brand-model "
            "combinations."
        )

    brand_model_mapping = (
        df[
            ["nome_marca", "nome_modelo", "codigo_fipe"]
        ]
        .drop_duplicates()
        .groupby(["nome_marca", "nome_modelo"])
        .size()
    )

    invalid_brand_models = brand_model_mapping[
        brand_model_mapping > 1
    ]

    if not invalid_brand_models.empty:
        raise ValueError(
            f"DQ009 failed: {len(invalid_brand_models)} "
            "brand-model combinations map to multiple "
            "codigo_fipe values."
        )

# 6. Monetary Validation

def validate_monetary_fields(df: pd.DataFrame) -> None:
    invalid_values = df[
        df["valor_centavos"] <= 0
    ]

    if not invalid_values.empty:
        raise ValueError(
            f"DQ010 failed: {len(invalid_values)} rows contain "
            "non-positive valor_centavos values."
        )

    valid_currency_format = (
        df["valor_formatado"]
        .str.match(CURRENCY_PATTERN, na=False)
    )

    invalid_currency_format = df[
        ~valid_currency_format
    ]

    if not invalid_currency_format.empty:
        raise ValueError(
            f"DQ012 failed: {len(invalid_currency_format)} rows "
            "contain invalid valor_formatado values."
        )

    parsed_centavos = (
        df["valor_formatado"]
        .str.replace("R$ ", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", "", regex=False)
        .astype("int64")
    )

    monetary_mismatch = df[
        df["valor_centavos"] != parsed_centavos
    ]

    if not monetary_mismatch.empty:
        raise ValueError(
            f"DQ011 failed: {len(monetary_mismatch)} rows contain "
            "inconsistent monetary representations."
        )

# 7. Processed Data Validation

def validate_processed_dtypes(df: pd.DataFrame) -> None:
    dtype_mismatches = {}

    for column, expected_dtype in EXPECTED_PROCESSED_DTYPES.items():
        actual_dtype = str(df[column].dtype)

        if actual_dtype != expected_dtype:
            dtype_mismatches[column] = {
                "expected": expected_dtype,
                "actual": actual_dtype,
            }

    if dtype_mismatches:
        raise TypeError(
            f"Unexpected processed dtypes: {dtype_mismatches}"
        )


def validate_shape_preservation(
    df_raw: pd.DataFrame,
    df: pd.DataFrame,
) -> None:
    if df_raw.shape != df.shape:
        raise ValueError(
            f"Shape changed during transformation: "
            f"raw={df_raw.shape}, processed={df.shape}"
        )


def validate_unchanged_values(
    df_raw: pd.DataFrame,
    df: pd.DataFrame,
) -> None:
    unchanged_columns = [
        "mes_referencia",
        "ano_referencia",
        "ano_modelo",
        "zero_km",
        "valor_centavos",
    ]

    unexpected_changes = {}

    for column in unchanged_columns:
        raw_values = df_raw[column]
        processed_values = df[column]

        both_null = raw_values.isna() & processed_values.isna()

        equal_values = (
            raw_values.eq(processed_values)
            .fillna(False)
            | both_null
        )

        changed_count = (~equal_values).sum()

        if changed_count > 0:
            unexpected_changes[column] = changed_count

    if unexpected_changes:
        raise ValueError(
            f"Unexpected value changes detected: {unexpected_changes}"
        )

# 8. Main Validation Orchestrator

def validate_fipe_data(df: pd.DataFrame) -> None:
    validate_schema(df)
    validate_completeness(df)
    validate_snapshot_grain(df)
    validate_domains(df)
    validate_functional_dependencies(df)
    validate_monetary_fields(df)

def validate_processed_data(
    df_raw: pd.DataFrame,
    df: pd.DataFrame,
) -> None:
    validate_fipe_data(df)
    validate_processed_dtypes(df)
    validate_shape_preservation(df_raw, df)
    validate_unchanged_values(df_raw, df)