COPY dim_date
TO 'data/gold/dim_date.parquet'
(FORMAT PARQUET);

COPY dim_vehicle
TO 'data/gold/dim_vehicle.parquet'
(FORMAT PARQUET);

COPY fct_fipe_prices
TO 'data/gold/fct_fipe_prices.parquet'
(FORMAT PARQUET);