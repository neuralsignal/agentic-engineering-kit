# CI Workflows and Python Toolchains

Continuous-integration patterns (pytest, ruff, mypy, pre-commit, cross-matrix) and
Python toolchain setups (pixi, uv, pip caching).

---

## 1. CI Patterns

### pytest + coverage

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ['3.11', '3.12', '3.13']
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
      - run: pip install -e ".[dev]"
      - run: |
          pytest tests/ \
            --junitxml=junit/test-results-${{ matrix.python-version }}.xml \
            --cov=mypackage \
            --cov-report=xml \
            --cov-report=term-missing
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: pytest-results-${{ matrix.python-version }}
          path: junit/test-results-${{ matrix.python-version }}.xml
```

### Ruff lint + format check

```yaml
- uses: actions/checkout@v5
- uses: actions/setup-python@v5
  with:
    python-version: '3.x'
- run: pipx install ruff
- run: ruff check --output-format=github .
- run: ruff format --diff .
```

### Mypy

```yaml
- run: pip install mypy
- run: mypy src/ --strict --ignore-missing-imports
```

### Pre-commit

```yaml
name: pre-commit
on:
  pull_request:
  push:
    branches: [main]
jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v5
      - uses: pre-commit/action@v3.0.1
```

### OS cross-matrix

```yaml
strategy:
  fail-fast: false
  max-parallel: 4
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ['3.11', '3.12']
    exclude:
      - os: windows-latest
        python-version: '3.11'
runs-on: ${{ matrix.os }}
```

---

## 2. Python Toolchain Setups

### pixi (prefix-dev/setup-pixi)

```yaml
# Basic
- uses: prefix-dev/setup-pixi@v0.9.4
  with:
    pixi-version: v0.62.2
    cache: true     # default: on when pixi.lock is present
    frozen: true    # fail if lock would need to change
- run: pixi run test

# Matrix over pixi environments
strategy:
  matrix:
    environment: [py311, py312]
steps:
  - uses: prefix-dev/setup-pixi@v0.9.4
    with:
      environments: ${{ matrix.environment }}
  - run: pixi run -e ${{ matrix.environment }} test

# Cache writes only on main push (save cache quota on PRs)
- uses: prefix-dev/setup-pixi@v0.9.4
  with:
    cache: true
    cache-write: ${{ github.event_name == 'push' && github.ref_name == 'main' }}

# Monorepo: subdirectory pixi project
- uses: prefix-dev/setup-pixi@v0.9.4
  with:
    working-directory: ./packages/my-project

# Use pixi shell for all steps (no `pixi run` prefix needed)
- uses: prefix-dev/setup-pixi@v0.9.4
  with:
    activate-environment: true
- run: python -m pytest tests/

# Use pixi as the shell for a single step
- run: pytest tests/
  shell: pixi run bash -e {0}
```

`pixi.lock` must be committed to the repo. `setup-pixi` runs `--locked` by default and fails if the lock would change.

### uv (astral-sh/setup-uv)

```yaml
# Basic
- uses: astral-sh/setup-uv@v7
  with:
    enable-cache: true
- run: uv sync --locked --all-extras --dev
- run: uv run pytest tests/

# Matrix
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
steps:
  - uses: astral-sh/setup-uv@v7
    with:
      python-version: ${{ matrix.python-version }}
      enable-cache: true
  - run: uv sync --locked
  - run: uv run pytest

# Prune stale cache entries after run
env:
  UV_CACHE_DIR: /tmp/.uv-cache
steps:
  - uses: actions/cache@v4
    with:
      path: /tmp/.uv-cache
      key: uv-${{ runner.os }}-${{ hashFiles('uv.lock') }}
      restore-keys: uv-${{ runner.os }}-
  - run: uv cache prune --ci
```

### pip caching

```yaml
# Via setup-python (preferred — no manual cache config needed)
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: pip
    cache-dependency-path: |
      pyproject.toml
      requirements*.txt

# Via actions/cache (explicit)
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt', '**/pyproject.toml') }}
    restore-keys: ${{ runner.os }}-pip-
```
