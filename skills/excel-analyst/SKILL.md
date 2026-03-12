---
name: excel-analyst
description: Build professional Excel financial models (P&L, DCF, Budget vs Actuals, Scenario Analysis) from a YAML model spec with named ranges, styled sheets, and Excel formulas.
---

# Excel Analyst Skill

Build financial Excel models from declarative YAML specs. The skill generates workbooks with three sheets (Assumptions, Inputs, Model), registers assumption cells as Excel named ranges, and writes formula-based projections using openpyxl.

## Locations

- Skill scripts: `skills/excel-analyst/scripts/`
- Templates: `skills/excel-analyst/templates/`
- Default style config: bundled in `excel_model/defaults/default_style.yaml` (used when `--style` omitted)
- Core library: [`excel-model`](https://pypi.org/project/excel-model/) PyPI package

## Running Scripts

All scripts run via pixi.

```
cd skills/excel-analyst && pixi run python scripts/<SCRIPT> <ARGS>
```

## Script Reference

### `scripts/build_model.py`

Build an Excel financial model from a YAML spec.

**Required args:**
- `--spec` — Path to model spec YAML (use a template or custom spec)
- `--output` — Path for output `.xlsx` file

**Required args (continued):**
- `--mode` — `batch` (JSON to stdout) or `interactive` (verbose narrative)

**Optional args:**
- `--style` — Path to style config YAML (defaults to bundled style if omitted)
- `--data` — Path to input data file (`.xlsx`, `.csv`, `.parquet`, `.json`, `.yaml`, `.md`)

**Batch mode exit codes:**
- `0` = success, stdout: `{"status": "ok", "output": "/abs/path/model.xlsx"}`
- `1` = error, stdout: `{"status": "error", "message": "..."}`

**Examples:**

```bash
# P&L from template, no input data, batch mode (bundled style defaults)
cd skills/excel-analyst && pixi run python scripts/build_model.py \
  --spec templates/p_and_l.yaml \
  --output /tmp/pl_model.xlsx \
  --mode batch

# P&L with custom style and historical CSV data, interactive mode
cd skills/excel-analyst && pixi run python scripts/build_model.py \
  --spec templates/p_and_l.yaml \
  --output /tmp/pl_model.xlsx \
  --style style_config.yaml \
  --data /tmp/historical_data.csv \
  --mode interactive

# DCF model
cd skills/excel-analyst && pixi run python scripts/build_model.py \
  --spec templates/dcf.yaml \
  --output /tmp/dcf_model.xlsx \
  --mode batch

# Scenario analysis
cd skills/excel-analyst && pixi run python scripts/build_model.py \
  --spec templates/scenario_analysis.yaml \
  --output /tmp/scenario_model.xlsx \
  --mode batch

# Or use the CLI directly
cd skills/excel-analyst && pixi run excel-model build \
  --spec templates/p_and_l.yaml \
  --output /tmp/pl_model.xlsx
```

### `scripts/validate_spec.py`

Validate a model spec YAML (and optionally the data column mapping).

**Required args:**
- `--spec` — Model spec YAML path

**Optional args:**
- `--data` — Input data file to validate column mapping

**Exit codes:** `0` = valid (prints "OK"), `1` = invalid (prints errors one per line)

**Examples:**

```bash
cd skills/excel-analyst && pixi run python scripts/validate_spec.py \
  --spec templates/p_and_l.yaml

cd skills/excel-analyst && pixi run python scripts/validate_spec.py \
  --spec my_model.yaml \
  --data /tmp/data.csv
```

### `scripts/describe_model.py`

Dry-run description of what `build_model.py` would produce. No file written.

**Required args:**
- `--spec` — Model spec YAML path
- `--format` — `text` (human-readable) or `json` (machine-readable)

**Examples:**

```bash
cd skills/excel-analyst && pixi run python scripts/describe_model.py \
  --spec templates/dcf.yaml \
  --format text

cd skills/excel-analyst && pixi run python scripts/describe_model.py \
  --spec templates/scenario_analysis.yaml \
  --format json
```

## Template Reference

All templates live in `skills/excel-analyst/templates/`. Copy and customize them for specific models.

| Template | Model Type | Granularity | Periods | Use Case |
|----------|-----------|-------------|---------|----------|
| `p_and_l.yaml` | `p_and_l` | annual | 2 hist + 3 proj | Standard income statement |
| `dcf.yaml` | `dcf` | annual | 2 hist + 5 proj | Discounted cash flow valuation |
| `budget_vs_actuals.yaml` | `budget_vs_actuals` | monthly | 12 periods | Monthly BvA reporting |
| `scenario_analysis.yaml` | `scenario` | annual | 2 hist + 3 proj | Base/Bull/Bear scenarios |
| `custom.yaml` | `custom` | annual | 3 periods | Blank slate for custom models |

## Model Spec Schema

A model spec YAML has these top-level fields:

```yaml
model_type: p_and_l     # p_and_l | dcf | budget_vs_actuals | scenario | custom
title: ""
currency: USD           # ISO 4217
granularity: annual     # monthly | quarterly | annual | auto
start_period: "2025"    # "2025" | "2025-Q1" | "Q1 2025" | "2025-01" | "Jan 2025"
n_periods: 3
n_history_periods: 2

metadata:
  preparer: ""
  date: ""
  version: "1.0"

assumptions: []         # list of AssumptionDef
line_items: []          # list of LineItemDef
scenarios: []           # ScenarioDef — scenario model only
column_groups: []       # ColumnGroupDef — BvA/scenario only
inputs:
  source: ""            # file path (or empty — filled by --data arg)
  period_col: period
  sheet: ""             # xlsx only
  value_cols: {}        # {line_item_key: source_column_name}
```

### AssumptionDef

```yaml
- name: RevenueGrowthRate   # CamelCase — becomes the Excel named range name
  label: Revenue Growth Rate
  value: 0.10
  format: percent           # number | percent | currency | integer
  group: Growth             # groups assumptions into sections on the Assumptions sheet
```

### LineItemDef

```yaml
- key: revenue              # unique identifier, referenced by formula_params
  label: Revenue            # display label (leading spaces = visual indent)
  formula_type: growth_projected
  formula_params:
    growth_assumption: RevenueGrowthRate
  is_subtotal: false        # light fill + top border
  is_total: false           # darker fill + double bottom border
  section: Revenue          # groups rows with a section header
```

## Formula Types

| Type | Description | Required params |
|------|-------------|-----------------|
| `input_ref` | History: `=Inputs!$C$5`; projection: routes to `projected_type` | `projected_type`, `growth_assumption` (for projection) |
| `growth_projected` | `=C10*(1+RevenueGrowthRate)` | `growth_assumption` |
| `pct_of_revenue` | `=C10*COGSMargin` | `revenue_key`, `rate_assumption` |
| `sum_of_rows` | `=C10+C11+C12` | `addend_keys: [key1, key2]` |
| `subtraction` | `=C10-C11` | `minuend_key`, `subtrahend_key` |
| `ratio` | `=C10/C11` | `numerator_key`, `denominator_key` |
| `growth_rate` | `=(C10/B10)-1` | `value_key` |
| `discounted_pv` | `=C10/(1+WACC)^1` | `cashflow_key`, `rate_assumption` |
| `terminal_value` | `=C10*(1+TGR)/(WACC-TGR)` | `cashflow_key`, `growth_assumption`, `rate_assumption` |
| `npv_sum` | `=SUM(pvs)+pv_terminal` | `pv_fcf_key`, `pv_terminal_key` |
| `variance` | `=actual-plan` | `plan_key`, `actual_key` |
| `variance_pct` | `=(actual-plan)/ABS(plan)` | `plan_key`, `actual_key` |
| `constant` | literal number | `value` |
| `custom` | raw formula with `{col_letter}` tokens | `formula` |

## Workbook Layout

Every model produces three sheets:

**Assumptions sheet:**
- Row 1: merged title header
- Row 2: column headers (Parameter | Named Range | Value | Format)
- Grouped by `group` with section header rows
- Column C = the named range target cell

**Inputs sheet:**
- Row 1: merged title "Historical Input Data"
- Row 2: "Line Item" + history period labels
- One row per `value_cols` mapping with historical data

**Model sheet:**
- Row 1: merged title header
- Row 2: period labels (history = gray tint, projection = dark header)
- Frozen panes at B3
- Per-section: section header row + line item rows
- Subtotal rows: light fill + top border
- Total rows: darker fill + double bottom border

## Agent Workflow

For a typical financial model build:

1. Choose a template or write a custom spec YAML
2. Run `validate_spec.py` to check the spec
3. Run `describe_model.py --format text` to confirm the expected output
4. Run `build_model.py --mode batch` to generate the Excel file

## Dependencies

| Package | Purpose |
|---------|---------|
| excel-model | Core library (formula engine, Excel writer, loaders, spec dataclasses) |
| openpyxl | Excel file generation (transitively via excel-model) |
| polars | Data loading and DataFrame processing (transitively via excel-model) |
| pyyaml | YAML spec and config parsing |
| pytest | Test runner |
| hypothesis | Property-based testing |

## Gotchas

### `input_ref` formula type requires `line_item_key` matching a `value_cols` key

When using `formula_type: input_ref`, the `line_item_key` (set to the spec's line item `key`) must match a key in `spec.inputs.value_cols`. If the input data doesn't have a column mapped for that key, the formula engine raises a `KeyError`. Always ensure your `inputs.value_cols` mapping covers all line items with `input_ref`.

### `variance` / `variance_pct` formula types reference other line items by key

The `plan_key` and `actual_key` in `variance` formula params must be keys of other line items in the same spec (not column names from input data). Make sure the referenced line items exist in `line_items` before the variance row.

### Scenario model named ranges use `{ScenarioName}{AssumptionName}` format

Each scenario assumption gets a prefixed named range (`BaseRevenueGrowthRate`, `BullRevenueGrowthRate`). Formula params reference the base assumption name; the scenario prefix is applied automatically by the formula engine based on `scenario_prefix`.

### History periods in P&L with `input_ref` need data loaded via `--data`

History columns for `input_ref` line items emit `=Inputs!$C$5` references. If no `--data` is provided, those Inputs sheet cells are empty (formulas will evaluate to 0 or blank in Excel). This is valid — just provide `--data` when historical data exists.

### `start_period` must match the `granularity` format

| Granularity | Valid `start_period` examples |
|-------------|-------------------------------|
| `annual` | `"2025"` |
| `quarterly` | `"2025-Q1"`, `"Q2 2026"` |
| `monthly` | `"2025-01"`, `"Jan 2025"` |
| `auto` | any of the above (auto-detected) |

Mismatched formats cause a `ValueError` at period generation time.
