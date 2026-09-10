import pandas as pd

from fipex.transformations import transform_fipe_data


def test_transform_fipe_data():
    df_raw = pd.DataFrame({
        "mes_referencia": [9],
        "ano_referencia": [2026],
        "tipo_veiculo": ["carro "],
        "codigo_fipe": ["001001-4 "],
        "nome_marca": ["FIAT"],
        "nome_modelo": ["Palio "],
        "ano_modelo": [2020],
        "zero_km": [False],
        "nome_combustivel": ["Gasolina "],
        "sigla_combustivel": ["g "],
        "valor_centavos": [4500000],
        "valor_formatado": ["R$ 45.000,00 "],
    })

    df = transform_fipe_data(df_raw)

    assert df.loc[0, "nome_marca"] == "Fiat"
    assert df.loc[0, "nome_modelo"] == "Palio"
    assert df.loc[0, "tipo_veiculo"] == "carro"
    assert df.loc[0, "sigla_combustivel"] == "g"
    assert str(df["ano_modelo"].dtype) == "Int64"