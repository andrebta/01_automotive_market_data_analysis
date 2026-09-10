CREATE OR REPLACE TABLE fct_fipe_prices (
    date_key INTEGER NOT NULL,
    vehicle_key BIGINT NOT NULL,
    valor_centavos BIGINT NOT NULL,
    PRIMARY KEY (date_key, vehicle_key),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (vehicle_key) REFERENCES dim_vehicle(vehicle_key)
);

INSERT INTO fct_fipe_prices
SELECT
    p.date_key,
    v.vehicle_key,
    p.valor_centavos
FROM int_fipe_prices AS p
JOIN dim_vehicle AS v
    ON p.codigo_fipe = v.codigo_fipe
    AND p.ano_modelo IS NOT DISTINCT FROM v.ano_modelo
    AND p.zero_km = v.zero_km
    AND p.sigla_combustivel = v.sigla_combustivel;