CREATE OR REPLACE VIEW int_fipe_prices AS

SELECT
    ano_referencia * 100 + mes_referencia AS date_key,
    codigo_fipe,
    ano_modelo,
    zero_km,
    sigla_combustivel,
    valor_centavos
FROM stg_fipe_prices;