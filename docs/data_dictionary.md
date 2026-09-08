# Data Dictionary

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

- `codigo_fipe`
- `ano_modelo`
- `zero_km`
- `sigla_combustivel`
- `mes_referencia`
- `ano_referencia`

The reference period is required to distinguish the same vehicle configuration across different FIPE snapshots.

---

## Column Dictionary

| Column | Type | Nullable | Observed Cardinality | Domain / Example | Business Meaning | Data Quality Notes |
|---|---|---:|---:|---|---|---|
| `tipo_veiculo` | string | No | 3 | `carro`, `caminhão`, `moto` | Vehicle category | Must belong to the known vehicle-type domain |
| `codigo_fipe` | string | No | 11,396 | `001001-4` | FIPE vehicle code | Required; functionally identifies one `nome_marca + nome_modelo` combination |
| `nome_modelo` | string | No | 11,391 | `Golf 1.6...` | Detailed vehicle model description | Required; high-cardinality categorical attribute; not globally unique across manufacturers |
| `nome_marca` | string | No | 231 | `VW`, `Fiat`, `BMW` | Vehicle manufacturer | Required; capitalization is not fully standardized |
| `nome_combustivel` | string | No | 7 | `Gasolina`, `Diesel`, `Flex`, `Híbrido`, `Elétrico`, `Álcool`, `Gás Natural` | Fuel type description | Must maintain a 1:1 relationship with `sigla_combustivel` |
| `sigla_combustivel` | string | No | 7 | `g`, `d`, `f`, `h`, `l`, `e`, `n` | Fuel type code | Must maintain a 1:1 relationship with `nome_combustivel` |
| `ano_modelo` | float64 | Yes | 47 non-null values | `1981`–`2027`, plus `NULL` | Vehicle model year | `NULL` is valid only for zero-km records; model year `2027` is a legitimate observed value and must not be used to impute nulls |
| `zero_km` | bool | No | 2 | `True`, `False` | Indicates whether the record represents a zero-km vehicle | `True` if `ano_modelo IS NULL` |
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