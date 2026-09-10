CREATE OR REPLACE VIEW int_vehicle AS

SELECT DISTINCT
    codigo_fipe,
    nome_marca,
    nome_modelo,
    tipo_veiculo,
    ano_modelo,
    zero_km,
    sigla_combustivel,
    nome_combustivel
FROM stg_fipe_prices;

