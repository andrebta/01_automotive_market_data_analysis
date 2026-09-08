# Data Quality Rules

This document defines the data quality constraints identified during exploratory profiling of the FIPE dataset.

The rules describe expected structural, semantic, relational, and formatting properties that downstream ingestion and transformation pipelines should validate.

---

## Rule Summary

| Rule ID | Category | Column(s) | Rule | Severity |
|---|---|---|---|---|
| DQ001 | Completeness | `codigo_fipe` | Must not be null | Critical |
| DQ002 | Completeness | All columns except `ano_modelo` | Must not be null | Critical |
| DQ003 | Conditional Nullability | `ano_modelo`, `zero_km` | `ano_modelo IS NULL` if `zero_km = True` | Critical |
| DQ004 | Uniqueness | Snapshot key | Must be unique within a snapshot | Critical |
| DQ005 | Uniqueness | Historical key | Must be unique across historical snapshots | Critical |
| DQ006 | Domain | `tipo_veiculo` | Must belong to the expected vehicle-type domain | High |
| DQ007 | Referential Mapping | `nome_combustivel`, `sigla_combustivel` | Must maintain a bidirectional 1:1 relationship | High |
| DQ008 | Functional Dependency | `codigo_fipe`, `nome_marca`, `nome_modelo` | Each FIPE code must identify exactly one brand-model combination | Critical |
| DQ009 | Functional Dependency | `nome_marca`, `nome_modelo`, `codigo_fipe` | Each brand-model combination must identify exactly one FIPE code | High |
| DQ010 | Monetary Validity | `valor_centavos` | Must be greater than zero | Critical |
| DQ011 | Monetary Consistency | `valor_centavos`, `valor_formatado` | Both fields must represent exactly the same monetary value | Critical |
| DQ012 | Formatting | `valor_formatado` | Must follow the expected Brazilian currency format | Medium |
| DQ013 | Snapshot Consistency | `mes_referencia`, `ano_referencia` | Must each contain a single value within one snapshot | High |
| DQ014 | Domain | `mes_referencia` | Must be between 1 and 12 | Critical |
| DQ015 | Standardization | `nome_marca` | Case-insensitive duplicate brand variants must be detected | Medium |

---

## DQ001 — FIPE Code Completeness

### Rule

`codigo_fipe` must never be null.

```text
codigo_fipe IS NOT NULL
```

---

## DQ002 — General Completeness

### Rule

All columns except `ano_modelo` must not contain null values.

```text
ALL COLUMNS EXCEPT ano_modelo ARE NOT NULL
```

### Rationale

Exploratory profiling identified `ano_modelo` as the only column with expected null values.

All null values in `ano_modelo` are associated with `zero_km = True`, representing zero-kilometer vehicles rather than random missing data.

Therefore, null values in any other column should be treated as a data quality violation.

### Severity

**Critical**

---

## DQ003 — Conditional Model Year Nullability

### Rule

`ano_modelo` may be null only when `zero_km = True`.

```text
ano_modelo IS NULL IF AND ONLY IF zero_km = True
```

### Rationale

The profiling analysis identified a deterministic relationship between `ano_modelo` and `zero_km`:

- all records where `zero_km = True` have `ano_modelo = NULL`;
- all records where `ano_modelo = NULL` have `zero_km = True`;
- no non-zero-km vehicle has a null `ano_modelo`.

Therefore, the null state of `ano_modelo` carries business meaning and must be preserved explicitly.

`ano_modelo` must not be imputed with values such as `2027`, because `2027` is already a legitimate model year in the observed domain and would conflate two distinct business states.

### Severity

**Critical**

---

## DQ004 — Snapshot Grain Uniqueness

### Rule

The following column combination must uniquely identify each record within a single FIPE snapshot:

```text
codigo_fipe
+ ano_modelo
+ zero_km
+ sigla_combustivel
```

### Rationale

Duplicate analysis showed that apparent duplicates were explained by vehicle condition and fuel type.

The validated snapshot grain is therefore:

```text
codigo_fipe + ano_modelo + zero_km + sigla_combustivel
```

Each row represents one FIPE reference price for one unique combination of:

- FIPE code;
- model year;
- vehicle condition;
- fuel type.

No duplicate rows should exist for this grain within the same snapshot.

### Severity

**Critical**

---

## DQ005 — Historical Key Uniqueness

### Rule

When multiple FIPE snapshots are combined, the historical key must uniquely identify each record.

The expected historical key is:

```text
ano_referencia
+ mes_referencia
+ codigo_fipe
+ ano_modelo
+ zero_km
+ sigla_combustivel
```

### Rationale

`mes_referencia` and `ano_referencia` are constant within the current dataset because the file represents a single monthly FIPE snapshot.

Although they do not discriminate rows inside the current snapshot, they define the temporal context of each observed price.

When multiple snapshots are appended into a historical dataset, both columns must become part of the key to prevent collisions between identical vehicle configurations observed in different reference periods.

### Severity

**Critical**

---

## DQ006 — Vehicle Type Domain

### Rule

`tipo_veiculo` must contain only values from the expected domain:

```text
carro
caminhão
moto
```

### Rationale

The observed domain contains exactly three categories:

- `carro`;
- `caminhão`;
- `moto`.

The domain is small, well-defined, and no formatting inconsistencies were observed during profiling.

Any additional value should therefore be treated as an unexpected domain value requiring investigation.

### Severity

**High**

---

## DQ007 — Fuel Name and Code Relationship

### Rule

`nome_combustivel` and `sigla_combustivel` must maintain a bidirectional one-to-one relationship.

```text
nome_combustivel -> sigla_combustivel
sigla_combustivel -> nome_combustivel
```

The observed mappings are:

| nome_combustivel | sigla_combustivel |
|---|---|
| Gasolina | g |
| Diesel | d |
| Flex | f |
| Híbrido | h |
| Elétrico | l |
| Álcool | e |
| Gás Natural | n |

### Rationale

Exploratory profiling confirmed that:

- each fuel name maps to exactly one fuel code;
- each fuel code maps to exactly one fuel name;
- the frequency distributions match across both columns;
- no unmatched fuel categories were observed.

This relationship represents a referential consistency constraint.

### Severity

**High**

---

## DQ008 — FIPE Code Functional Dependency

### Rule

Each `codigo_fipe` must identify exactly one combination of:

```text
nome_marca + nome_modelo
```

Formally:

```text
codigo_fipe -> nome_marca, nome_modelo
```

### Rationale

Profiling confirmed that each FIPE code maps to exactly one brand-model combination.

Therefore, a single `codigo_fipe` associated with multiple brand-model combinations would indicate a structural inconsistency in the dataset.

### Severity

**Critical**

---

## DQ009 — Brand-Model Functional Dependency

### Rule

Each combination of:

```text
nome_marca + nome_modelo
```

must identify exactly one `codigo_fipe`.

Formally:

```text
nome_marca, nome_modelo -> codigo_fipe
```

### Rationale

`nome_modelo` is not globally unique across manufacturers.

Five model names were identified as being shared across different manufacturers:

- `16-220 T 3-Eixos 2p (diesel)`;
- `16-220 Turbo 2p (diesel)`;
- `CR 125`;
- `CR 250`;
- `FENIX GOLD 240`.

The ambiguity disappears when `nome_marca` is included.

Therefore, the brand-model combination behaves as an alternate business identifier for `codigo_fipe`.

### Severity

**High**

---

## DQ010 — Positive Monetary Value

### Rule

`valor_centavos` must be strictly greater than zero.

```text
valor_centavos > 0
```

### Rationale

The current snapshot contains only positive vehicle prices.

No zero or negative values were observed.

The observed monetary range was:

```text
R$ 872,00
to
R$ 9.749.142,00
```

The lower and upper extremes were manually inspected and were considered semantically plausible for their associated vehicle records.

Therefore, statistical extremity alone should not invalidate a price, but zero or negative values should be rejected.

### Severity

**Critical**

---

## DQ011 — Monetary Field Consistency

### Rule

`valor_centavos` and `valor_formatado` must represent exactly the same monetary value.

The relationship must hold in both directions:

```text
valor_centavos -> valor_formatado
valor_formatado -> valor_centavos
```

Additionally, parsing `valor_formatado` into integer cents must produce the exact value stored in `valor_centavos`.

### Rationale

Profiling confirmed a bidirectional one-to-one relationship between both monetary fields.

No mismatches were found after converting `valor_formatado` back into integer cents and comparing the result with `valor_centavos`.

Therefore:

- `valor_centavos` is the canonical numerical field;
- `valor_formatado` is a derived presentation field.

Any discrepancy between the two should be considered a data quality violation.

### Severity

**Critical**

---

## DQ012 — Brazilian Currency Formatting

### Rule

`valor_formatado` must follow the expected Brazilian currency representation.

Expected format:

```text
R$ X.XXX,XX
```

Examples:

```text
R$ 872,00
R$ 45.320,00
R$ 1.250.000,00
```

### Rationale

All observed values in `valor_formatado` conform to the Brazilian currency formatting convention used in the dataset.

The field is presentation-oriented and must remain parseable into the canonical numeric representation stored in `valor_centavos`.

### Severity

**Medium**

---

## DQ013 — Snapshot Reference Consistency

### Rule

`mes_referencia` and `ano_referencia` must each contain exactly one unique value within a single snapshot.

```text
COUNT_DISTINCT(mes_referencia) = 1
COUNT_DISTINCT(ano_referencia) = 1
```

### Rationale

Both columns are snapshot-level metadata.

In the current dataset, each contains a single unique value across all records, which is expected because the file represents one FIPE monthly snapshot.

Multiple values inside a single input snapshot would indicate that different reference periods were mixed unexpectedly.

### Severity

**High**

---

## DQ014 — Reference Month Domain

### Rule

`mes_referencia` must contain an integer value between `1` and `12`.

```text
1 <= mes_referencia <= 12
```

### Rationale

`mes_referencia` represents the calendar month associated with the FIPE reference period.

Although the current snapshot contains only one month value, the field must remain constrained to the valid calendar-month domain in all future snapshots.

### Severity

**Critical**

---

## DQ015 — Brand Name Standardization

### Rule

Case-insensitive duplicate variants of `nome_marca` must be detected and normalized before downstream analytical use.

The following variants were identified during profiling:

| Normalized brand | Observed variants |
|---|---|
| `agrale` | `AGRALE`, `Agrale` |
| `fiat` | `FIAT`, `Fiat` |
| `ford` | `FORD`, `Ford` |
| `honda` | `HONDA`, `Honda` |
| `hyundai` | `HYUNDAI`, `Hyundai` |
| `mercedes-benz` | `MERCEDES-BENZ`, `Mercedes-Benz` |
| `peugeot` | `PEUGEOT`, `Peugeot` |
| `suzuki` | `SUZUKI`, `Suzuki` |
| `volvo` | `VOLVO`, `Volvo` |

### Rationale

Case-insensitive grouping of `nome_marca` identified multiple textual representations of the same manufacturer.

These differences do not represent distinct business entities and artificially increase the observed cardinality of the column.

Unlike `nome_modelo`, where no capitalization-only duplicates were identified, `nome_marca` requires explicit standardization.

A canonical capitalization strategy should therefore be applied during transformation.

### Severity

**Medium**

---

## Validation Principles

The rules above should be applied according to the following principles:

- violations of **Critical** rules should block ingestion or publication of the affected dataset;
- violations of **High** rules should fail validation unless explicitly reviewed and accepted;
- violations of **Medium** rules may allow pipeline execution, but should generate a warning and be corrected during transformation;
- statistical outliers must not automatically be classified as invalid values without supporting semantic evidence;
- deterministic relationships identified during profiling should be treated as enforceable data contracts for downstream processing.

---

## Rule Coverage

The current rule set covers the following data quality dimensions:

| Dimension | Covered Rules |
|---|---|
| Completeness | DQ001, DQ002, DQ003 |
| Uniqueness | DQ004, DQ005 |
| Domain Validity | DQ006, DQ010, DQ014 |
| Referential Consistency | DQ007 |
| Functional Dependency | DQ008, DQ009 |
| Monetary Consistency | DQ010, DQ011 |
| Formatting | DQ012 |
| Snapshot Consistency | DQ013 |
| Standardization | DQ015 |

These rules constitute the initial data quality contract derived from the exploratory profiling of the FIPE dataset.