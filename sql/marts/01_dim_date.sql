CREATE OR REPLACE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    ano_referencia INTEGER NOT NULL,
    mes_referencia INTEGER NOT NULL,
    ano_mes VARCHAR NOT NULL,
    trimestre VARCHAR NOT NULL,
    nome_mes VARCHAR NOT NULL
);

INSERT INTO dim_date
SELECT DISTINCT
    ano_referencia * 100 + mes_referencia AS date_key,
    ano_referencia,
    mes_referencia,
    printf('%04d-%02d', ano_referencia, mes_referencia) AS ano_mes,
    'Q' || CAST(CEIL(mes_referencia / 3.0) AS INTEGER) AS trimestre,
    CASE mes_referencia
        WHEN 1 THEN 'Janeiro'
        WHEN 2 THEN 'Fevereiro'
        WHEN 3 THEN 'Março'
        WHEN 4 THEN 'Abril'
        WHEN 5 THEN 'Maio'
        WHEN 6 THEN 'Junho'
        WHEN 7 THEN 'Julho'
        WHEN 8 THEN 'Agosto'
        WHEN 9 THEN 'Setembro'
        WHEN 10 THEN 'Outubro'
        WHEN 11 THEN 'Novembro'
        WHEN 12 THEN 'Dezembro'
    END AS nome_mes
FROM stg_fipe_prices;