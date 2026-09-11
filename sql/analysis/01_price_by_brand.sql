SELECT
    v.nome_marca,
     COUNT(*) AS quantidade_registros,
    ROUND(AVG(f.valor_centavos) / 100.0 , 2) AS media_preco
FROM
    fct_fipe_prices AS f
LEFT JOIN
    dim_vehicle AS v
    ON f.vehicle_key = v.vehicle_key
GROUP BY
    v.nome_marca
ORDER BY
    media_preco DESC;