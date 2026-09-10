SELECT * FROM int_fipe_prices;

SELECT * FROM int_vehicle;

SELECT * FROM dim_date;

SELECT * FROM dim_vehicle;

SELECT * FROM fct_fipe_prices;

SELECT
    d.ano_mes,
    v.nome_marca,
    v.nome_modelo,
    ROUND((AVG(f.valor_centavos) / 100.0), 2) AS preco_medio
FROM fct_fipe_prices AS f
JOIN dim_date AS d
    ON f.date_key = d.date_key
JOIN dim_vehicle AS v
    ON f.vehicle_key = v.vehicle_key
GROUP BY
    d.ano_mes,
    v.nome_marca,
    v.nome_modelo
ORDER BY preco_medio DESC;