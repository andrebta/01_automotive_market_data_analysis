# Data Quality Rules

This document defines the main data quality rules identified during profiling of the FIPE dataset and implemented in the project validation layer.

Executable validations are implemented in:

```text
src/fipex/validation.py
```

Transformation-related standardization rules are implemented in:

```text
src/fipex/transformations.py
```

---

## Rule Summary

| Rule ID | Category | Column(s) | Rule | Severity | Validation Layer |
|---|---|---|---|---|---|
| DQ001 | Completeness | `codigo_fipe` | Must not be null | Critical | Raw / Processed |
| DQ002 | Completeness | All columns except `ano_modelo` | Must not be null | Critical | Raw / Processed |
| DQ003 | Conditional Nullability | `ano_modelo`, `zero_km` | `ano_modelo IS NULL` if and only if `zero_km = True` | Critical | Raw / Processed |
| DQ004 | Uniqueness | Snapshot key | Must be unique within a snapshot | Critical | Raw / Processed |
| DQ005 | Uniqueness | Historical key | Must be unique across historical snapshots | Critical | Historical datasets |
| DQ006 | Domain | `tipo_veiculo` | Must belong to the expected vehicle-type domain | High | Raw / Processed |
| DQ007 | Referential Mapping | `nome_combustivel`, `sigla_combustivel` | Present values must follow the expected 1:1 mapping | High | Raw / Processed |
| DQ008 | Functional Dependency | `codigo_fipe`, `nome_marca`, `nome_modelo` | Each FIPE code must identify exactly one brand-model combination | Critical | Raw / Processed |
| DQ009 | Functional Dependency | `nome_marca`, `nome_modelo`, `codigo_fipe` | Each brand-model combination must identify exactly one FIPE code | High | Raw / Processed |
| DQ010 | Monetary Validity | `valor_centavos` | Must be greater than zero | Critical | Raw / Processed |
| DQ011 | Monetary Consistency | `valor_centavos`, `valor_formatado` | Both fields must represent exactly the same monetary value | Critical | Raw / Processed |
| DQ012 | Formatting | `valor_formatado` | Must follow the expected Brazilian currency format | Medium | Raw / Processed |
| DQ013 | Snapshot Consistency | `mes_referencia`, `ano_referencia` | A single snapshot must contain exactly one reference period | High | Snapshot |
| DQ014 | Domain | `mes_referencia` | Must be between 1 and 12 | Critical | Raw / Processed |
| DQ015 | Standardization | `nome_marca` | Non-standard brand variants must not remain after transformation | Medium | Processed |

---

## DQ001 — FIPE Code Completeness

### Rule

`codigo_fipe` must never be null.

```text
codigo_fipe IS NOT NULL
```

### Rationale

The FIPE code is a core business identifier and participates in the natural key of the dataset.

### Severity

**Critical**

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

`ano_modelo` must be null if and only if `zero_km = True`.

```text
ano_modelo IS NULL IF AND ONLY IF zero_km = True
```

Therefore:

```text
zero_km = True
→ ano_modelo IS NULL
```

and:

```text
zero_km = False
→ ano_modelo IS NOT NULL
```

### Rationale

The profiling analysis identified a deterministic relationship between `ano_modelo` and `zero_km`.

The null state of `ano_modelo` carries business meaning and must be preserved explicitly.

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

Each row represents one FIPE reference price for one unique vehicle configuration within a single reference period.

Duplicate rows for this grain are invalid.

### Severity

**Critical**

---

## DQ005 — Historical Key Uniqueness

### Rule

When multiple FIPE snapshots are combined, the historical key must uniquely identify each record:

```text
ano_referencia
+ mes_referencia
+ codigo_fipe
+ ano_modelo
+ zero_km
+ sigla_combustivel
```

### Rationale

`mes_referencia` and `ano_referencia` define the temporal context of each observed price.

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

The observed domain contains exactly three categories and no malformed values were identified during profiling.

Any additional value should be treated as unexpected and investigated.

### Severity

**High**

---

## DQ007 — Fuel Name and Code Relationship

### Rule

Whenever a fuel value is present, `nome_combustivel` and `sigla_combustivel` must match the expected mapping:

| `nome_combustivel` | `sigla_combustivel` |
|---|---|
| `Gasolina` | `g` |
| `Diesel` | `d` |
| `Flex` | `f` |
| `Híbrido` | `h` |
| `Elétrico` | `l` |
| `Álcool` | `e` |
| `Gás Natural` | `n` |

The validation does not require all seven fuel types to appear in every dataset subset.

### Rationale

Exploratory profiling confirmed that each observed fuel description maps to exactly one fuel code and each fuel code maps to exactly one fuel description.

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

A single `codigo_fipe` associated with multiple brand-model combinations would indicate a structural inconsistency.

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

The ambiguity disappears when `nome_marca` is included, so the brand-model combination behaves as an alternate business identifier for `codigo_fipe`.

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

Statistical extremity alone should not invalidate a price, but zero or negative values should be rejected.

### Severity

**Critical**

---

## DQ011 — Monetary Field Consistency

### Rule

`valor_centavos` and `valor_formatado` must represent exactly the same monetary value.

Parsing `valor_formatado` into integer cents must produce the exact value stored in `valor_centavos`.

### Rationale

Profiling confirmed a bidirectional one-to-one relationship between both monetary fields.

Therefore:

- `valor_centavos` is the canonical numerical field;
- `valor_formatado` is a derived presentation field.

Any discrepancy between the two is a data quality violation.

### Severity

**Critical**

---

## DQ012 — Brazilian Currency Formatting

### Rule

`valor_formatado` must follow the expected Brazilian currency representation:

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

The field is presentation-oriented and must remain parseable into the canonical numeric representation stored in `valor_centavos`.

### Severity

**Medium**

---

## DQ013 — Snapshot Reference Consistency

### Rule

A dataset representing one monthly FIPE snapshot must contain exactly one unique combination of:

```text
ano_referencia
+ mes_referencia
```

For the current snapshot:

```text
ano_referencia = 2026
mes_referencia = 9
```

### Rationale

Both columns are snapshot-level metadata.

Multiple reference periods inside a single input snapshot would indicate that different monthly snapshots were mixed unexpectedly.

When multiple snapshots are intentionally combined into a historical dataset, this rule must be applied at the individual snapshot level rather than across the complete historical dataset.

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

`mes_referencia` represents the calendar month associated with the FIPE reference period and must remain inside the valid calendar-month domain.

### Severity

**Critical**

---

## DQ015 — Brand Name Standardization

### Rule

Case-insensitive duplicate variants of `nome_marca` must be standardized during transformation.

The following variants were identified during profiling:

| Canonical brand | Raw variants |
|---|---|
| `Agrale` | `AGRALE`, `Agrale` |
| `Fiat` | `FIAT`, `Fiat` |
| `Ford` | `FORD`, `Ford` |
| `Honda` | `HONDA`, `Honda` |
| `Hyundai` | `HYUNDAI`, `Hyundai` |
| `Mercedes-Benz` | `MERCEDES-BENZ`, `Mercedes-Benz` |
| `Peugeot` | `PEUGEOT`, `Peugeot` |
| `Suzuki` | `SUZUKI`, `Suzuki` |
| `Volvo` | `VOLVO`, `Volvo` |

After transformation, non-standard variants must no longer be present.

### Rationale

These differences do not represent distinct business entities and artificially increase the observed cardinality of `nome_marca`.

Standardization is implemented in:

```text
src/fipex/transformations.py
```

Validation is performed on the processed dataset.

### Severity

**Medium**

---

## Additional Domain Validation — Model Year Plausibility

When `ano_modelo` is not null, it must satisfy:

```text
ano_modelo >= 1900
```

and:

```text
ano_modelo <= ano_referencia + 1
```

This allows legitimate future model-year values such as `2027` in the 2026 reference snapshot.

---

## Processed Data Integrity Checks

In addition to the business data quality rules, the processed dataset is validated for transformation integrity.

### Expected Data Types

The processed dataset must contain compatible data types for:

- reference year and month;
- nullable model year;
- boolean zero-km indicator;
- integer monetary value;
- textual categorical fields.

Text columns may use either Pandas `object` or string-compatible dtypes depending on the Pandas version.

### Shape Preservation

The transformation layer must not unexpectedly add or remove rows or columns.

Expected condition:

```text
raw.shape = processed.shape
```

### Unchanged Business Values

The following fields must not be altered by standardization:

```text
mes_referencia
ano_referencia
ano_modelo
zero_km
valor_centavos
```

Only fields explicitly targeted by transformations, such as manufacturer naming and string cleanup, may change.

---

## Validation Principles

The rules above should be applied according to the following principles:

- violations of **Critical** rules should block ingestion or publication of the affected dataset;
- violations of **High** rules should fail validation unless explicitly reviewed and accepted;
- violations of **Medium** rules should be corrected during transformation and may be surfaced as warnings during profiling;
- statistical outliers must not automatically be classified as invalid values without supporting semantic evidence;
- deterministic relationships identified during profiling should be treated as enforceable data contracts for downstream processing.

---

## Validation Flow

```text
Raw Dataset
    |
    v
Schema Validation
    |
    v
Completeness Validation
    |
    v
Snapshot Grain Validation
    |
    v
Historical Grain Validation
    |
    v
Domain Validation
    |
    v
Reference Period Validation
    |
    v
Functional Dependency Validation
    |
    v
Monetary Validation
    |
    v
Transformation
    |
    v
Processed Dataset Validation
    |
    v
Data Type Validation
    |
    v
Shape Preservation
    |
    v
Unchanged Value Validation
    |
    v
Brand Standardization Validation
```

---

## Rule Coverage

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

These rules constitute the initial data quality contract derived from exploratory profiling and enforced by the current FIPE processing pipeline.
