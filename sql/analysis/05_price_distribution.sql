SELECT
    CASE
        WHEN f.valor_centavos < 5000000 THEN 'Até R$ 50 mil'
        WHEN f.valor_centavos < 10000000 THEN 'R$ 50 mil a R$ 100 mil'
        WHEN f.valor_centavos < 20000000 THEN 'R$ 100 mil a R$ 200 mil'
        WHEN f.valor_centavos < 50000000 THEN 'R$ 200 mil a R$ 500 mil'
        WHEN f.valor_centavos < 100000000 THEN 'R$ 500 mil a R$ 1 milhão'
        ELSE 'Acima de R$ 1 milhão'
    END AS faixa_preco,
    COUNT(*) AS quantidade_veiculos,
    ROUND(AVG(f.valor_centavos) / 100.0, 2) AS preco_medio
FROM fct_fipe_prices AS f
GROUP BY
    CASE
        WHEN f.valor_centavos < 5000000 THEN 'Até R$ 50 mil'
        WHEN f.valor_centavos < 10000000 THEN 'R$ 50 mil a R$ 100 mil'
        WHEN f.valor_centavos < 20000000 THEN 'R$ 100 mil a R$ 200 mil'
        WHEN f.valor_centavos < 50000000 THEN 'R$ 200 mil a R$ 500 mil'
        WHEN f.valor_centavos < 100000000 THEN 'R$ 500 mil a R$ 1 milhão'
        ELSE 'Acima de R$ 1 milhão'
    END
ORDER BY MIN(f.valor_centavos);