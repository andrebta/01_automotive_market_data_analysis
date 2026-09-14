import re

import pandas as pd

from fipex.transformations import BRAND_MAPPING


# ============================================================
# 1. Schema Validation
# ============================================================

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

HISTORICAL_KEY = [
    "ano_referencia",
    "mes_referencia",
    "codigo_fipe",
    "ano_modelo",
    "zero_km",
    "sigla_combustivel",
]

EXPECTED_PROCESSED_DTYPES = {
    "mes_referencia": "int64",
    "ano_referencia": "int64",
    "tipo_veiculo": "object",
    "codigo_fipe": "object",
    "nome_marca": "object",
    "nome_modelo": "object",
    "ano_modelo": "Int64",
    "zero_km": "bool",
    "nome_combustivel": "object",
    "sigla_combustivel": "object",
    "valor_centavos": "int64",
    "valor_formatado": "object",
}


def validate_schema(df: pd.DataFrame) -> None:
    actual_columns = set(df.columns)
    expected_columns = set(EXPECTED_COLUMNS)

    missing_columns = expected_columns - actual_columns
    unexpected_columns = actual_columns - expected_columns

    if missing_columns:
        raise ValueError(
            f"DQ schema failed: missing columns: {sorted(missing_columns)}"
        )

    if unexpected_columns:
        raise ValueError(
            f"DQ schema failed: unexpected columns: {sorted(unexpected_columns)}"
        )


# ============================================================
# 2. Completeness Validation
# ============================================================

def validate_completeness(df: pd.DataFrame) -> None:
    required_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column != "ano_modelo"
    ]

    null_counts = df[required_columns].isna().sum()
    invalid_columns = null_counts[null_counts > 0]

    if not invalid_columns.empty:
        raise ValueError(
            "DQ002 failed: unexpected null values found:\n"
            f"{invalid_columns.to_dict()}"
        )

    invalid_zero_km = df["zero_km"] & df["ano_modelo"].notna()
    invalid_used = (~df["zero_km"]) & df["ano_modelo"].isna()

    if invalid_zero_km.any() or invalid_used.any():
        raise ValueError(
            "DQ003 failed: ano_modelo must be NULL if and only if "
            "zero_km is True."
        )


# ============================================================
# 3. Grain Validation
# ============================================================

def validate_snapshot_grain(df: pd.DataFrame) -> None:
    duplicated_rows = df.duplicated(
        subset=SNAPSHOT_KEY,
        keep=False,
    )

    if duplicated_rows.any():
        raise ValueError(
            "DQ004 failed: duplicate rows found for snapshot grain."
        )


def validate_historical_grain(df: pd.DataFrame) -> None:
    duplicated_rows = df.duplicated(
        subset=HISTORICAL_KEY,
        keep=False,
    )

    if duplicated_rows.any():
        raise ValueError(
            "DQ005 failed: duplicate rows found for historical grain."
        )


# ============================================================
# 4. Domain Validation
# ============================================================

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


def validate_domains(df: pd.DataFrame) -> None:
    invalid_vehicle_types = (
        set(df["tipo_veiculo"].dropna())
        - EXPECTED_VEHICLE_TYPES
    )

    if invalid_vehicle_types:
        raise ValueError(
            "DQ006 failed: unexpected tipo_veiculo values: "
            f"{sorted(invalid_vehicle_types)}"
        )

    invalid_months = ~df["mes_referencia"].between(1, 12)

    if invalid_months.any():
        raise ValueError(
            "DQ014 failed: mes_referencia must be between 1 and 12."
        )

    model_year_mask = df["ano_modelo"].notna()

    invalid_model_years = (
        (df.loc[model_year_mask, "ano_modelo"] < 1900)
        |
        (
            df.loc[model_year_mask, "ano_modelo"]
            > df.loc[model_year_mask, "ano_referencia"] + 1
        )
    )

    if invalid_model_years.any():
        raise ValueError(
            "Domain validation failed: implausible ano_modelo values found."
        )


def validate_reference_period(df: pd.DataFrame) -> None:
    reference_periods = df[
        ["ano_referencia", "mes_referencia"]
    ].drop_duplicates()

    if len(reference_periods) != 1:
        raise ValueError(
            "DQ013 failed: snapshot contains more than one "
            "reference period."
        )


# ============================================================
# 5. Functional Dependencies
# ============================================================

def validate_functional_dependencies(
    df: pd.DataFrame,
) -> None:
    fuel_pairs = df[
        ["nome_combustivel", "sigla_combustivel"]
    ].drop_duplicates()

    for _, row in fuel_pairs.iterrows():
        fuel_name = row["nome_combustivel"]
        fuel_code = row["sigla_combustivel"]

        expected_code = EXPECTED_FUEL_MAPPING.get(fuel_name)

        if expected_code != fuel_code:
            raise ValueError(
                "DQ007 failed: unexpected fuel name/code mapping found: "
                f"{fuel_name} -> {fuel_code}"
            )

    codes_per_vehicle = (
        df.groupby(
            ["nome_marca", "nome_modelo"]
        )["codigo_fipe"]
        .nunique()
    )

    if (codes_per_vehicle > 1).any():
        raise ValueError(
            "DQ009 failed: one brand/model combination maps "
            "to multiple codigo_fipe values."
        )

    vehicles_per_code = (
        df.groupby("codigo_fipe")[
            ["nome_marca", "nome_modelo"]
        ]
        .apply(
            lambda group: group.drop_duplicates().shape[0]
        )
    )

    if (vehicles_per_code > 1).any():
        raise ValueError(
            "DQ008 failed: one codigo_fipe maps to multiple "
            "brand/model combinations."
        )


# ============================================================
# 6. Monetary Validation
# ============================================================

CURRENCY_PATTERN = re.compile(
    r"^R\$ \d{1,3}(?:\.\d{3})*,\d{2}$"
)


def parse_brl_to_cents(value: str) -> int:
    normalized_value = (
        value
        .replace("R$ ", "")
        .replace(".", "")
        .replace(",", ".")
    )

    return int(round(float(normalized_value) * 100))


def validate_monetary_fields(df: pd.DataFrame) -> None:
    invalid_values = df["valor_centavos"] <= 0

    if invalid_values.any():
        raise ValueError(
            "DQ010 failed: valor_centavos must be greater than zero."
        )

    invalid_format = ~df["valor_formatado"].str.match(
        CURRENCY_PATTERN,
        na=False,
    )

    if invalid_format.any():
        raise ValueError(
            "DQ012 failed: invalid Brazilian currency format found."
        )

    parsed_values = df["valor_formatado"].apply(
        parse_brl_to_cents
    )

    inconsistent_values = (
        parsed_values != df["valor_centavos"]
    )

    if inconsistent_values.any():
        raise ValueError(
            "DQ011 failed: valor_centavos and valor_formatado "
            "represent different monetary values."
        )


# ============================================================
# 7. Processed Data Validation
# ============================================================

def validate_processed_dtypes(df: pd.DataFrame) -> None:
    expected_dtypes = {
        "mes_referencia": {"int64"},
        "ano_referencia": {"int64"},
        "tipo_veiculo": {"object", "str"},
        "codigo_fipe": {"object", "str"},
        "nome_marca": {"object", "str"},
        "nome_modelo": {"object", "str"},
        "ano_modelo": {"Int64"},
        "zero_km": {"bool"},
        "nome_combustivel": {"object", "str"},
        "sigla_combustivel": {"object", "str"},
        "valor_centavos": {"int64"},
        "valor_formatado": {"object", "str"},
    }

    invalid_dtypes = {}

    for column, accepted_dtypes in expected_dtypes.items():
        actual_dtype = str(df[column].dtype)

        if actual_dtype not in accepted_dtypes:
            invalid_dtypes[column] = {
                "expected": sorted(accepted_dtypes),
                "actual": actual_dtype,
            }

    if invalid_dtypes:
        raise ValueError(
            "Processed dtype validation failed: "
            f"{invalid_dtypes}"
        )

def validate_shape_preservation(
    df_raw: pd.DataFrame,
    df: pd.DataFrame,
) -> None:
    if df_raw.shape != df.shape:
        raise ValueError(
            "Processed shape validation failed: "
            f"raw shape {df_raw.shape} != "
            f"processed shape {df.shape}."
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

    for column in unchanged_columns:
        raw_values = df_raw[column].reset_index(drop=True)
        processed_values = df[column].reset_index(drop=True)

        equal_values = (
            raw_values.eq(processed_values)
            |
            (
                raw_values.isna()
                & processed_values.isna()
            )
        )

        if not equal_values.all():
            raise ValueError(
                "Processed value validation failed: "
                f"unexpected changes found in '{column}'."
            )


def validate_standardized_brands(
    df: pd.DataFrame,
) -> None:
    non_standard_brands = {
        original
        for original, standardized in BRAND_MAPPING.items()
        if original != standardized
    }

    invalid_brands = (
        set(df["nome_marca"].dropna())
        & non_standard_brands
    )

    if invalid_brands:
        raise ValueError(
            "DQ015 failed: non-standard brand names found: "
            f"{sorted(invalid_brands)}"
        )


# ============================================================
# 8. Main Validation Orchestrator
# ============================================================

def validate_fipe_data(df: pd.DataFrame) -> None:
    validate_schema(df)
    validate_completeness(df)
    validate_snapshot_grain(df)
    validate_historical_grain(df)
    validate_domains(df)
    validate_reference_period(df)
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
    validate_standardized_brands(df)