import pandas as pd
import pytest

from fipex.validation import validate_fipe_data

def make_valid_df():
    return pd.DataFrame({
        "mes_referencia": [9],
        "ano_referencia": [2026],
        "tipo_veiculo": ["carro"],
        "codigo_fipe": ["001001-4"],
        "nome_marca": ["Fiat"],
        "nome_modelo": ["Palio"],
        "ano_modelo": [2020],
        "zero_km": [False],
        "nome_combustivel": ["Gasolina"],
        "sigla_combustivel": ["g"],
        "valor_centavos": [4500000],
        "valor_formatado": ["R$ 45.000,00"],
    })

def test_validate_fipe_data_accepts_valid_data():
    df = make_valid_df()

    validate_fipe_data(df)

def test_validate_fipe_data_rejects_invalid_vehicle_type():
    df = make_valid_df()

    df.loc[0, "tipo_veiculo"] = "aviao"

    with pytest.raises(ValueError):
        validate_fipe_data(df)