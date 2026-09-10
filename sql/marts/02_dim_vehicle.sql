CREATE OR REPLACE TABLE dim_vehicle (
    vehicle_key BIGINT PRIMARY KEY,
    codigo_fipe VARCHAR NOT NULL,
    nome_marca VARCHAR NOT NULL,
    nome_modelo VARCHAR NOT NULL,
    tipo_veiculo VARCHAR NOT NULL,
    ano_modelo INTEGER,
    zero_km BOOLEAN NOT NULL,
    sigla_combustivel VARCHAR NOT NULL,
    nome_combustivel VARCHAR NOT NULL
);

INSERT INTO dim_vehicle
SELECT
    ROW_NUMBER() OVER (
        ORDER BY 
            codigo_fipe, 
            ano_modelo, 
            zero_km, 
            sigla_combustivel
    ) AS vehicle_key,
    codigo_fipe,
    nome_marca,
    nome_modelo,
    tipo_veiculo,
    ano_modelo,
    zero_km,
    sigla_combustivel,
    nome_combustivel
FROM int_vehicle;