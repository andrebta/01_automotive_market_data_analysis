SELECT
    v.nome_combustivel,
    COUNT(*) AS quantidade_registros,
    ROUND(AVG(f.valor_centavos) / 100.0, 2) AS preco_medio
FROM fct_fipe_prices AS f
JOIN dim_vehicle AS v
    ON f.vehicle_key = v.vehicle_key
GROUP BY v.nome_combustivel
ORDER BY quantidade_registros DESC;