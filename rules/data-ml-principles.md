---
description: Data, ML, and pipeline engineering principles -- notebooks vs source, experiment provenance, feature hygiene, schema safety, pipeline testing, monitoring
alwaysApply: true
---

# Data and ML Engineering Principles

Tactical principles for data science, machine learning, and pipeline work. See the Data, ML, and Pipeline Engineering section in `CONSTITUTION.md` for the foundational axioms.

## Notebooks for Exploration, Source Files for Repetition

Notebooks (Jupyter, Marimo, R Markdown) are for discovery, prototyping, and communication. They are not production pipelines.

- Extract reusable ETL, feature engineering, and data loading code from notebooks into proper modules.
- If a piece of code is run more than once across notebooks, it belongs in a shared package.
- Notebooks that must run in a specific order to produce a result are a pipeline disguised as exploration -- refactor into an automated pipeline.

## Experiment Provenance

Every experiment run must log:

- Parameters used (full config dict, not just the ones you changed)
- Data snapshot or version identifier
- Random seed
- Metrics produced
- Model artifact location (path, registry URI)
- Git SHA and branch at time of run

If you cannot reproduce a result from its log, the experiment is invalid. Verbal recollection of "what I tried" is not provenance.

Track human-level metrics alongside model metrics. A model that scores well on AUC but produces unusable predictions for domain experts is not useful. Complement quantitative metrics with qualitative error analysis -- manually inspect the worst predictions and document the patterns.

## Feature Hygiene

- Document every feature: what it represents, where it comes from, how it is computed, and who owns it.
- Clean up unused features. Features without documentation or an active consumer are tech debt.
- When a feature's upstream data source changes, re-validate the feature's behavior -- do not assume the change is benign.
- Monitor feature coverage: if a feature that was populated for 90% of examples drops to 60%, that is a bug, not a trend.
- Avoid features that leak the label or that are proxies for the target computed after the prediction point. Time-travel leakage is the single most common source of inflated offline metrics.

## No Data in Version Control

- Raw data, model artifacts, intermediate outputs, and large generated files do not belong in git.
- Use data versioning tools (DVC, lakehouse versioning) or cloud storage (S3, ADLS, DBFS).
- Exceptions: small lookup tables, config files, and schema definitions that rarely change.
- Commit the code that produces data, not the data itself.

## Schema Changes Are Breaking Changes

- Treat data schema modifications (column renames, type changes, nullable changes, column removal) with the same rigor as API breaking changes.
- Document consumer impact before making the change.
- Coordinate rollout: update producers and consumers together, or version the schema.
- Add schema validation checks that fail loudly when the upstream schema drifts from what the pipeline expects.

## Data Pipeline Testing

Data pipelines require testing beyond standard unit tests. Code correctness alone does not guarantee data correctness.

- **Row count assertions** -- After each pipeline stage, assert that output row counts are within expected bounds. A join that silently drops 40% of rows is a data bug, not a code bug.
- **Distribution checks** -- Validate that value distributions in key columns remain stable across runs. A numeric column that suddenly shifts from mean=50 to mean=5000 signals upstream corruption.
- **Schema validation** -- Assert column names, types, and nullability at stage boundaries. Use schema validation libraries (Great Expectations, Pandera, Pydantic) rather than manual checks.
- **Referential integrity** -- When joining tables, verify that foreign keys match. Log and investigate unmatched keys rather than silently dropping them.
- **Idempotency tests** -- Run the pipeline twice on the same input. The outputs must be identical. If they differ, the pipeline has hidden state.

## Model Monitoring in Production

A model that passes offline evaluation and degrades silently in production is worse than one that crashes.

- **Prediction distribution tracking** -- Monitor the distribution of model outputs (scores, classes, predictions) over time. A sudden shift in prediction distribution without a corresponding shift in inputs indicates model drift or data corruption.
- **Input drift detection** -- Track the distributions of input features in production against the training data distributions. Alert when drift exceeds a configured threshold (e.g., PSI > 0.2, KS test p < 0.01).
- **Offline-online metric comparison** -- Regularly compare offline evaluation metrics against observed production outcomes. A growing gap between offline and online performance signals training-serving skew.
- **Data freshness checks** -- Set staleness thresholds for all upstream data sources. If a table that should refresh daily is 3 days old, the pipeline should fail or alert -- not silently serve stale predictions.
- **Shadow scoring** -- When deploying a new model version, run it in shadow mode alongside the production model and compare outputs before switching traffic.
