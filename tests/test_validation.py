import pandas as pd
import pytest

from fipex.validation import (
    validate_fipe_data,
    validate_processed_data,
)


def make_valid_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "mes_referencia": [9, 9],
            "ano_referencia": [2026, 2026],
            "tipo_veiculo": ["carro", "carro"],
            "codigo_fipe": ["001001-0", "001002-9"],
            "nome_marca": ["Fiat", "Ford"],
            "nome_modelo": ["Modelo A", "Modelo B"],
            "ano_modelo": pd.Series([2020, 2021], dtype="Int64"),
            "zero_km": [False, False],
            "nome_combustivel": ["Gasolina", "Flex"],
            "sigla_combustivel": ["g", "f"],
            "valor_centavos": [5000000, 7500000],
            "valor_formatado": ["R$ 50.000,00", "R$ 75.000,00"],
        }
    )


def test_validate_fipe_data_accepts_valid_data() -> None:
    df = make_valid_df()

    validate_fipe_data(df)


def test_validate_fipe_data_rejects_invalid_vehicle_type() -> None:
    df = make_valid_df()
    df.loc[0, "tipo_veiculo"] = "barco"

    with pytest.raises(
        ValueError,
        match="DQ006",
    ):
        validate_fipe_data(df)


def test_validate_fipe_data_rejects_invalid_zero_km_rule() -> None:
    df = make_valid_df()
    df.loc[0, "zero_km"] = True

    with pytest.raises(
        ValueError,
        match="DQ003",
    ):
        validate_fipe_data(df)


def test_validate_fipe_data_accepts_zero_km_with_null_year() -> None:
    df = make_valid_df()

    df.loc[0, "zero_km"] = True
    df.loc[0, "ano_modelo"] = pd.NA

    validate_fipe_data(df)


def test_validate_fipe_data_rejects_duplicate_snapshot_grain() -> None:
    df = make_valid_df()

    duplicated_row = df.iloc[[0]].copy()
    df = pd.concat(
        [df, duplicated_row],
        ignore_index=True,
    )

    with pytest.raises(
        ValueError,
        match="DQ004",
    ):
        validate_fipe_data(df)


def test_validate_fipe_data_rejects_multiple_reference_periods() -> None:
    df = make_valid_df()
    df.loc[1, "mes_referencia"] = 8

    with pytest.raises(
        ValueError,
        match="DQ013",
    ):
        validate_fipe_data(df)


def test_validate_fipe_data_rejects_invalid_fuel_mapping() -> None:
    df = make_valid_df()
    df.loc[0, "sigla_combustivel"] = "x"

    with pytest.raises(
        ValueError,
        match="DQ007",
    ):
        validate_fipe_data(df)


def test_validate_fipe_data_rejects_non_positive_price() -> None:
    df = make_valid_df()
    df.loc[0, "valor_centavos"] = 0

    with pytest.raises(
        ValueError,
        match="DQ010",
    ):
        validate_fipe_data(df)


def test_validate_fipe_data_rejects_inconsistent_monetary_fields() -> None:
    df = make_valid_df()
    df.loc[0, "valor_formatado"] = "R$ 60.000,00"

    with pytest.raises(
        ValueError,
        match="DQ011",
    ):
        validate_fipe_data(df)


def test_validate_processed_data_accepts_valid_processed_data() -> None:
    df_raw = make_valid_df()
    df = df_raw.copy()

    validate_processed_data(
        df_raw,
        df,
    )


def test_validate_processed_data_rejects_non_standard_brand() -> None:
    df_raw = make_valid_df()
    df = df_raw.copy()

    df.loc[0, "nome_marca"] = "FIAT"

    with pytest.raises(
        ValueError,
        match="DQ015",
    ):
        validate_processed_data(
            df_raw,
            df,
        )


def test_validate_processed_data_rejects_shape_change() -> None:
    df_raw = make_valid_df()
    df = df_raw.iloc[[0]].copy()

    with pytest.raises(
        ValueError,
        match="shape",
    ):
        validate_processed_data(
            df_raw,
            df,
        )


def test_validate_processed_data_rejects_unexpected_value_change() -> None:
    df_raw = make_valid_df()
    df = df_raw.copy()

    df.loc[0, "valor_centavos"] = 9999999
    df.loc[0, "valor_formatado"] = "R$ 99.999,99"

    with pytest.raises(
        ValueError,
        match="unexpected changes",
    ):
        validate_processed_data(
            df_raw,
            df,
        )