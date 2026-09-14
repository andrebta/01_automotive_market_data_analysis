CREATE OR REPLACE VIEW stg_fipe_prices AS
SELECT
    ano_referencia,
    mes_referencia,
    tipo_veiculo,
    codigo_fipe,
    nome_marca,
    nome_modelo,
    ano_modelo,
    zero_km,
    nome_combustivel,
    sigla_combustivel,
    valor_centavos,
    valor_formatado
FROM read_parquet('{{PROCESSED_FILE}}');