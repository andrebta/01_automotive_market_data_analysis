SELECT
    v.nome_marca,
    v.nome_modelo,
    v.ano_modelo,
    v.zero_km,
    v.nome_combustivel,
    f.valor_centavos / 100.0 AS preco
FROM fct_fipe_prices AS f
JOIN dim_vehicle AS v
    ON f.vehicle_key = v.vehicle_key
ORDER BY f.valor_centavos DESC
LIMIT 20;