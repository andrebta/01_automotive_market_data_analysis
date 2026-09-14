# Raw Data Dictionary

> **Scope:** This data dictionary describes the raw FIPE snapshot before standardization and transformation.
>
> Cardinalities, distinct counts and observed values documented here reflect the source dataset and may differ from the processed, Gold or Power BI layers after normalization rules are applied.

## Data Grain

One row represents the FIPE reference price for a specific FIPE code, model year, vehicle condition, fuel type, and reference period.

### Snapshot Key

The natural key for a single monthly FIPE snapshot is:

- `codigo_fipe`
- `ano_modelo`
- `zero_km`
- `sigla_combustivel`

This combination was validated as unique in the current snapshot.

### Historical Key

When multiple monthly snapshots are combined, the historical key becomes:

- `ano_referencia`
- `mes_referencia`
- `codigo_fipe`
- `ano_modelo`
- `zero_km`
- `sigla_combustivel`

The reference period is required to distinguish the same vehicle configuration across different FIPE snapshots.

---

## Column Dictionary

| Column | Type | Nullable | Observed Cardinality | Domain / Example | Business Meaning | Data Quality Notes |
|---|---|---:|---:|---|---|---|
| `tipo_veiculo` | string | No | 3 | `carro`, `caminhão`, `moto` | Vehicle category | Must belong to the known vehicle-type domain |
| `codigo_fipe` | string | No | 11,396 | `001001-4` | FIPE vehicle code | Required; functionally identifies one `nome_marca + nome_modelo` combination |
| `nome_modelo` | string | No | 11,391 | `Golf 1.6...` | Detailed vehicle model description | Required; high-cardinality categorical attribute; not globally unique across manufacturers |
| `nome_marca` | string | No | 231 | `VW`, `Fiat`, `BMW` | Vehicle manufacturer | Required; capitalization is not fully standardized in the raw layer. Brand-name casing variants are standardized in the processed layer using the mappings defined in `src/fipex/transformations.py` |
| `nome_combustivel` | string | No | 7 | `Gasolina`, `Diesel`, `Flex`, `Híbrido`, `Elétrico`, `Álcool`, `Gás Natural` | Fuel type description | Must maintain a 1:1 relationship with `sigla_combustivel` |
| `sigla_combustivel` | string | No | 7 | `g`, `d`, `f`, `h`, `l`, `e`, `n` | Fuel type code | Must maintain a 1:1 relationship with `nome_combustivel` |
| `ano_modelo` | float64 | Yes | 47 non-null values | `1981`–`2027`, plus `NULL` | Vehicle model year | `NULL` is valid only for zero-km records; model year `2027` is a legitimate observed value and must not be used to impute nulls |
| `zero_km` | bool | No | 2 | `True`, `False` | Indicates whether the record represents a zero-km vehicle | `True` if and only if `ano_modelo IS NULL` |
| `valor_centavos` | int64 | No | 44,368 | `1188200` | FIPE reference price stored in integer cents | Canonical monetary field; must be greater than zero |
| `valor_formatado` | string | No | 44,368 | `R$ 11.882,00` | FIPE reference price formatted in Brazilian Real | Derived display representation of `valor_centavos`; must match it exactly |
| `mes_referencia` | int32 | No | 1 | `9` | FIPE reference month | Snapshot-level metadata; must be between 1 and 12 |
| `ano_referencia` | int32 | No | 1 | `2026` | FIPE reference year | Snapshot-level metadata; must represent a valid reference year |

---

## Observed Domains

### Vehicle Type

The current snapshot contains three vehicle categories:

- `carro`
- `caminhão`
- `moto`

No unexpected or malformed vehicle-type values were identified.

### Fuel Type

The following bidirectional mappings were observed and validated:

| `nome_combustivel` | `sigla_combustivel` |
|---|---|
| `Gasolina` | `g` |
| `Diesel` | `d` |
| `Flex` | `f` |
| `Híbrido` | `h` |
| `Elétrico` | `l` |
| `Álcool` | `e` |
| `Gás Natural` | `n` |

Each fuel description maps to exactly one fuel code, and each fuel code maps to exactly one fuel description.

### Model Year

The observed non-null model-year domain ranges from:

- Minimum: `1981`
- Maximum: `2027`
- Distinct non-null values: `47`

There are `1,931` null values in `ano_modelo`.

These null values correspond exactly to records where:

```text
zero_km = True
```

Likewise, records where:

```text
zero_km = False
```

must have a non-null `ano_modelo`.

The value `2027` is a legitimate observed model year in the raw dataset and must not be used as an imputation value for zero-km records with `ano_modelo = NULL`.

---

## Functional Dependencies

The following functional dependencies were identified during profiling.

### FIPE Code to Brand and Model

Each `codigo_fipe` maps to exactly one combination of:

```text
nome_marca + nome_modelo
```

Therefore:

```text
codigo_fipe
→ nome_marca + nome_modelo
```

### Brand and Model to FIPE Code

Each unique combination of:

```text
nome_marca + nome_modelo
```

maps to exactly one `codigo_fipe`.

Therefore:

```text
nome_marca + nome_modelo
→ codigo_fipe
```

### Fuel Description and Fuel Code

The relationship between `nome_combustivel` and `sigla_combustivel` is one-to-one:

```text
nome_combustivel ↔ sigla_combustivel
```

---

## Monetary Fields

### `valor_centavos`

`valor_centavos` is the canonical analytical representation of the FIPE price.

Example:

```text
1188200
```

represents:

```text
R$ 11.882,00
```

This field:

- must be greater than zero;
- is stored as an integer;
- should be used for analytical calculations;
- avoids locale-dependent parsing during transformations.

### `valor_formatado`

`valor_formatado` is a display-oriented representation of the same monetary value.

Expected Brazilian currency format:

```text
R$ X.XXX,XX
```

Example:

```text
R$ 11.882,00
```

The parsed monetary value must exactly match `valor_centavos`.

---

## Brand Standardization

The raw dataset contains capitalization variants for some manufacturer names.

Examples identified during profiling include:

```text
AGRALE → Agrale
FIAT → Fiat
FORD → Ford
HONDA → Honda
HYUNDAI → Hyundai
MERCEDES-BENZ → Mercedes-Benz
PEUGEOT → Peugeot
SUZUKI → Suzuki
VOLVO → Volvo
```

These values are intentionally documented here as raw-data inconsistencies.

Standardization is applied only in the processed layer through:

```text
src/fipex/transformations.py
```

As a consequence, the number of distinct manufacturer values may be lower in the processed, Gold and Power BI layers than in the raw dataset.

---

## Reference Period

The current raw dataset represents a single FIPE snapshot.

Observed reference period:

```text
ano_referencia = 2026
mes_referencia = 9
```

For a valid single-snapshot dataset:

- `ano_referencia` must contain exactly one distinct value;
- `mes_referencia` must contain exactly one distinct value;
- `mes_referencia` must be between `1` and `12`.

When multiple snapshots are combined historically, the reference period becomes part of the historical grain.

---

## Data Quality Summary

The main business and data-quality assumptions identified from the raw dataset are:

- `codigo_fipe` is mandatory;
- all fields except `ano_modelo` are expected to be non-null;
- `ano_modelo IS NULL` if and only if `zero_km = True`;
- the snapshot natural key must be unique;
- the historical natural key must be unique when multiple snapshots are combined;
- `tipo_veiculo` must belong to the known domain;
- fuel description and fuel code must preserve their 1:1 relationship;
- `codigo_fipe` and `nome_marca + nome_modelo` must preserve their observed functional dependencies;
- `valor_centavos` must be positive;
- `valor_centavos` and `valor_formatado` must represent the same monetary value;
- `valor_formatado` must follow Brazilian Real formatting;
- a single raw snapshot must contain exactly one reference period;
- manufacturer capitalization inconsistencies are expected in the raw layer and standardized downstream.

Detailed executable rules are documented in:

```text
docs/data_quality_rules.md
```
