import pandas as pd


BRAND_MAPPING = {
    "AGRALE": "Agrale",
    "FIAT": "Fiat",
    "FORD": "Ford",
    "HONDA": "Honda",
    "HYUNDAI": "Hyundai",
    "MERCEDES-BENZ": "Mercedes-Benz",
    "PEUGEOT": "Peugeot",
    "SUZUKI": "Suzuki",
    "VOLVO": "Volvo",
}


STRING_COLUMNS = [
    "tipo_veiculo",
    "codigo_fipe",
    "nome_marca",
    "nome_modelo",
    "nome_combustivel",
    "sigla_combustivel",
    "valor_formatado",
]


COLUMN_ORDER = [
    "ano_referencia",
    "mes_referencia",
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


def standardize_brand_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["nome_marca"] = df["nome_marca"].replace(BRAND_MAPPING)

    return df


def strip_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for column in STRING_COLUMNS:
        df[column] = df[column].str.strip()

    return df


def standardize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["mes_referencia"] = df["mes_referencia"].astype("int64")
    df["ano_referencia"] = df["ano_referencia"].astype("int64")
    df["ano_modelo"] = df["ano_modelo"].astype("Int64")
    df["zero_km"] = df["zero_km"].astype("bool")
    df["valor_centavos"] = df["valor_centavos"].astype("int64")

    return df


def reorder_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df[COLUMN_ORDER].copy()


def transform_fipe_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = strip_string_columns(df)
    df = standardize_brand_names(df)
    df = standardize_dtypes(df)
    df = reorder_columns(df)

    return df