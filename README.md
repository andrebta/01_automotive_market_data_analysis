# Automotive Market Data Analysis

End-to-end Data Engineering and Analytics project built with Brazilian automotive market data, covering data profiling, data quality, Python transformation, dimensional modeling, DuckDB/SQL analytics and Power BI visualization.

The project transforms raw FIPE market data into a reproducible analytical pipeline and a Gold layer ready for Business Intelligence consumption.

---

## Project Overview

The objective of this project is to build a complete analytical workflow, from raw automotive pricing data to a dimensional model consumed by Power BI.

The project covers:

- data profiling and exploratory analysis;
- data quality rules and automated validation;
- Python transformations;
- Parquet storage;
- DuckDB analytical processing;
- modular SQL layers;
- dimensional modeling with a Star Schema;
- Gold layer generation;
- automated end-to-end orchestration;
- automated tests;
- Power BI dashboard development;
- technical documentation and version control.

---

## Architecture

```text
Raw Parquet
    |
    v
Python Pipeline
    |
    |-- Schema validation
    |-- Data quality validation
    |-- Standardization
    |-- Transformations
    |
    v
Processed Parquet
    |
    v
DuckDB + SQL
    |
    |-- Staging
    |-- Intermediate
    |-- Marts
    |
    v
Gold Parquet
    |
    |-- dim_date.parquet
    |-- dim_vehicle.parquet
    |-- fct_fipe_prices.parquet
    |
    v
Power BI
```

The project follows a structure inspired by the Medallion Architecture:

```text
Bronze  -> data/raw
Silver  -> data/processed
Gold    -> DuckDB marts + data/gold
```

---

## Repository Structure

```text
01_automotive_market_data_analysis/
├── data/
│   ├── raw/
│   ├── processed/
│   └── gold/
├── docs/
│   ├── data_dictionary.md
│   ├── data_quality_rules.md
│   ├── dimensional_model.dbml
│   ├── star_schema.pdf
│   ├── powerbi_dashboard.pdf
│   └── images/
│       ├── star_schema.png
│       ├── powerbi_overview.png
│       ├── powerbi_brand_model.png
│       └── powerbi_year_price.png
├── notebooks/
│   ├── 01_fipex_exploration.ipynb
│   └── 02_fipex_transformation.ipynb
├── sql/
│   ├── staging/
│   ├── intermediate/
│   ├── marts/
│   ├── analysis/
│   └── export/
├── src/
│   └── fipex/
│       ├── __init__.py
│       ├── config.py
│       ├── io.py
│       ├── transformations.py
│       ├── validation.py
│       └── pipeline.py
├── tests/
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Data Source

The dataset used in this project comes from the FIPE-derived public dataset maintained by [FipeX Labs](https://github.com/fipex-labs/dataset).

The dataset contains Brazilian automotive market reference prices and includes information such as:

- reference year and month;
- vehicle type;
- FIPE code;
- manufacturer;
- model;
- model year;
- zero-kilometer indicator;
- fuel type;
- price.

The source dataset is distributed under the CC0 1.0 Universal license.

The project stores the source data in Parquet format to preserve data types and provide efficient analytical storage.

---

## Data Profiling and Grain

The initial dataset was explored in:

```text
notebooks/01_fipex_exploration.ipynb
```

Profiling was used to identify:

- null patterns;
- cardinality;
- functional dependencies;
- duplicate behavior;
- categorical domains;
- monetary consistency;
- the correct dataset grain.

### Snapshot Grain

The validated natural key for one monthly FIPE snapshot is:

```text
codigo_fipe
+ ano_modelo
+ zero_km
+ sigla_combustivel
```

### Historical Grain

When multiple monthly snapshots are combined, the reference period is also required:

```text
ano_referencia
+ mes_referencia
+ codigo_fipe
+ ano_modelo
+ zero_km
+ sigla_combustivel
```

---

## Data Quality

The raw data dictionary is available at:

[View Raw Data Dictionary](docs/data_dictionary.md)

The executable data quality rules are documented at:

[View Data Quality Rules](docs/data_quality_rules.md)

The pipeline validates, among other rules:

- expected schema;
- mandatory fields;
- conditional nullability;
- snapshot grain uniqueness;
- historical grain uniqueness;
- vehicle-type domain;
- valid reference months;
- fuel name/code consistency;
- FIPE code functional dependencies;
- positive monetary values;
- consistency between monetary representations;
- Brazilian currency formatting;
- single-snapshot reference-period consistency;
- manufacturer name standardization after transformation.

An important semantic rule identified during profiling is:

```text
ano_modelo IS NULL <-> zero_km = TRUE
```

These null values are intentionally preserved instead of being replaced by an artificial model year.

The observed value `2027` is a legitimate model year in the source data and is not used to impute zero-kilometer records.

---

## Python Transformation Layer

Reusable Python code is stored under:

```text
src/fipex/
```

Main responsibilities:

- `io.py`: dataset reading and writing;
- `transformations.py`: string cleanup, manufacturer-name standardization, datatype normalization and column ordering;
- `validation.py`: data quality checks before and after transformation;
- `config.py`: centralized project paths and snapshot configuration;
- `pipeline.py`: orchestration of the complete workflow.

### Snapshot Configuration

The current monthly snapshot is configured in:

```python
SNAPSHOT_ID = "2026_09"
```

inside:

```text
src/fipex/config.py
```

The raw and processed filenames are derived from this value, avoiding duplicated snapshot hardcoding across the pipeline.

---

## DuckDB and SQL Layer

DuckDB is used as the local analytical engine.

The SQL layer is divided into four areas.

### Staging

Provides a stable SQL interface over the processed Parquet dataset.

### Intermediate

Prepares reusable business entities and natural keys before dimensional modeling.

### Marts

Materializes the analytical Star Schema used by downstream consumers.

### Analysis

Contains analytical and validation queries used to verify the Gold layer before Power BI consumption.

The Python orchestrator renders the file-path placeholders used by the SQL scripts before executing them in DuckDB.

---

## Dimensional Model

The analytical layer follows a Star Schema with two dimensions and one fact table.

![Star Schema](docs/images/star_schema.png)

[View Star Schema PDF](docs/star_schema.pdf)

The source DBML is available at:

[View `dimensional_model.dbml`](docs/dimensional_model.dbml)

### `dim_date`

Contains FIPE reference-period attributes:

```text
date_key
ano_referencia
mes_referencia
ano_mes
trimestre
nome_mes
```

`date_key` follows the `YYYYMM` format.

Example:

```text
202609
```

### `dim_vehicle`

Represents one unique analytical vehicle configuration:

```text
vehicle_key
codigo_fipe
nome_marca
nome_modelo
tipo_veiculo
ano_modelo
zero_km
sigla_combustivel
nome_combustivel
```

`vehicle_key` is a technical surrogate key.

The natural key used to identify a vehicle configuration is:

```text
codigo_fipe
+ ano_modelo
+ zero_km
+ sigla_combustivel
```

### `fct_fipe_prices`

Stores FIPE price observations:

```text
date_key
vehicle_key
valor_centavos
```

The fact table grain is:

> One FIPE price for one vehicle configuration in one FIPE reference month.

Its primary key is:

```text
date_key + vehicle_key
```

The fact table references:

```text
dim_date.date_key
dim_vehicle.vehicle_key
```

---

## Monetary Modeling

The canonical monetary field is:

```text
valor_centavos
```

Prices are stored as integer cents instead of localized formatted strings.

For example:

```text
R$ 85.568,00 -> 8556800
```

This keeps analytical calculations independent from locale-specific formatting.

Currency formatting is applied only at the presentation layer.

---

## Gold Layer

The SQL pipeline exports the dimensional model as Parquet files:

```text
data/gold/
├── dim_date.parquet
├── dim_vehicle.parquet
└── fct_fipe_prices.parquet
```

These files form the analytical interface consumed by Power BI.

The BI layer therefore consumes curated Gold outputs instead of raw, processed, staging or intermediate data.

---

## End-to-End Pipeline

The full workflow can be executed with a single command:

```bash
python -m fipex.pipeline
```

The orchestrator performs:

```text
Raw Data
    |
    v
Python Validation
    |
    v
Python Transformation
    |
    v
Processed Parquet
    |
    v
DuckDB Staging
    |
    v
Intermediate SQL
    |
    v
Dimensional Marts
    |
    v
Gold Parquet
```

This removes the need to execute notebooks or individual SQL scripts manually during normal pipeline runs.

> **Current scope:** the pipeline processes one monthly FIPE snapshot per execution. The dimensional model and historical key are designed to support future multi-period ingestion.

---

## Automated Tests

The project includes automated tests with `pytest`.

Run them with:

```bash
pytest -v
```

The test suite covers core transformation and validation behavior, including:

- valid input acceptance;
- invalid vehicle-type rejection;
- zero-kilometer/model-year consistency;
- snapshot grain duplication;
- reference-period consistency;
- fuel mapping;
- positive prices;
- monetary-field consistency;
- processed-data validation;
- manufacturer-name standardization;
- shape preservation;
- unexpected business-value changes.

---

## Analytical SQL

The Gold layer is validated using SQL queries covering subjects such as:

- price by brand;
- price by vehicle type;
- price by fuel;
- most expensive vehicles;
- price distribution.

These queries are stored under:

```text
sql/analysis/
```

---

# Power BI Dashboard

Power BI consumes the three Parquet files generated in the Gold layer.

The semantic model follows the same Star Schema implemented in DuckDB:

```text
dim_date
    1
    |
    *
fct_fipe_prices
    *
    |
    1
dim_vehicle
```

The dashboard contains three analytical pages.

## 1. FIPE Market Overview

Market-level overview including configuration count, model count, brand count, median price, maximum price, top brands by median price, portfolio variety and price behavior by model year.

![FIPE Market Overview](docs/images/powerbi_overview.png)

## 2. Brands and Models

Comparison of portfolio breadth, pricing and configuration variety across brands and models, including detailed brand-level metrics and model rankings.

![Brands and Models](docs/images/powerbi_brand_model.png)

## 3. Model Year and Prices

Analysis of configuration distribution by model year, price positioning and price-band distribution.

The dashboard supports interactive filtering by:

- brand;
- vehicle type;
- fuel type;
- model-year range.

![Model Year and Prices](docs/images/powerbi_year_price.png)

### Semantic Note

`vehicle_key` represents one unique analytical vehicle configuration rather than a physical vehicle unit.

The dashboard therefore uses:

```text
QTD. Configurações
```

when counting rows at the `vehicle_key` grain.

### Full Dashboard

[View complete Power BI dashboard as PDF](docs/powerbi_dashboard.pdf)

---

## Technology Stack

| Area | Technology |
|---|---|
| Programming | Python |
| Data Manipulation | Pandas |
| Storage | Parquet |
| Analytical Database | DuckDB |
| Data Modeling | SQL |
| Testing | Pytest |
| Dimensional Modeling | Star Schema / DBML |
| Visualization | Power BI |
| Version Control | Git / GitHub |
| Development Environment | VS Code |

---

## Key Engineering Decisions

### Parquet instead of CSV

Parquet preserves data types, provides compression and is better suited to analytical workloads.

### DuckDB as analytical engine

DuckDB provides lightweight SQL analytics directly over Parquet without requiring a database server.

### Modular SQL layers

Staging, intermediate and marts separate responsibilities and make transformations easier to understand and maintain.

### Surrogate vehicle key

The dimensional model uses a technical surrogate key instead of embedding business meaning into a concatenated identifier.

### Preservation of semantic nulls

Missing `ano_modelo` values associated with zero-kilometer vehicles are preserved instead of artificially imputed.

### Canonical monetary representation

Prices remain stored as integer cents until the presentation layer.

### Gold layer decoupled from Power BI

Power BI consumes curated analytical outputs rather than implementing core transformation rules itself.

### Centralized snapshot configuration

The monthly snapshot identifier is defined once in `config.py`, and downstream raw/processed paths are derived from it.

---

## Running the Project

### 1. Clone the repository

```bash
git clone https://github.com/andrebta/01_automotive_market_data_analysis.git
cd 01_automotive_market_data_analysis
```

### 2. Create the virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows:

```bash
.venv\Scripts\activate
```

Git Bash:

```bash
source .venv/Scripts/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

### 5. Run automated tests

```bash
pytest -v
```

### 6. Run the complete pipeline

```bash
python -m fipex.pipeline
```

After successful execution, the analytical datasets are generated under:

```text
data/gold/
```

---

## Documentation

- [Raw Data Dictionary](docs/data_dictionary.md)
- [Data Quality Rules](docs/data_quality_rules.md)
- [Dimensional Model - DBML](docs/dimensional_model.dbml)
- [Star Schema - PDF](docs/star_schema.pdf)
- [Power BI Dashboard - PDF](docs/powerbi_dashboard.pdf)
- [Source Dataset - FipeX Labs](https://github.com/fipex-labs/dataset)

---

## Project Outcome

This project delivers a reproducible end-to-end analytical data pipeline, starting with raw Brazilian automotive market data and ending with a dimensional model consumed by Power BI.

The project demonstrates practical application of:

```text
Data Profiling
Data Quality
Python ETL
Automated Validation
Parquet
DuckDB
SQL Transformation Layers
Dimensional Modeling
Star Schema
Surrogate Keys
Fact and Dimension Tables
Automated Testing
Pipeline Orchestration
Power BI
Git
Technical Documentation
```

The final result is not only a dashboard, but a complete analytical workflow that documents and automates the path from raw source data to a curated BI-ready data product.
