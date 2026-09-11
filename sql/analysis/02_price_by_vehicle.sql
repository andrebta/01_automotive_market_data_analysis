SELECT
    v.tipo_veiculo,
    COUNT(*) AS quantidade_registros,
    ROUND(AVG(f.valor_centavos) / 100.0) AS preco_medio
FROM
    fct_fipe_prices AS f
LEFT JOIN
    dim_vehicle as v
    ON f.vehicle_key = v.vehicle_key
GROUP BY
    v.tipo_veiculo
ORDER BY
    preco_medio DESC;