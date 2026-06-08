# Advanced Workflow Architecture

Reusable workflows, composite actions, environments and deployment, GitHub Pages, and
the workflow syntax quick reference (permissions, concurrency, outputs, conditionals).

---

## 9. Reusable Workflows

### Defining

```yaml
# .github/workflows/ci-reusable.yml
on:
  workflow_call:
    inputs:
      python-version:
        type: string
        required: false
        default: '3.12'
      working-directory:
        type: string
        required: false
        default: '.'
    secrets:
      pypi-token:
        required: false
    outputs:
      test-passed:
        description: Whether tests passed
        value: ${{ jobs.test.outputs.passed }}

jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ${{ inputs.working-directory }}
    outputs:
      passed: ${{ steps.pytest.outcome }}
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}
          cache: pip
      - run: pip install -e ".[dev]"
      - id: pytest
        run: pytest tests/
```

### Calling

```yaml
jobs:
  # Same repo
  ci:
    uses: ./.github/workflows/ci-reusable.yml
    with:
      python-version: '3.12'
    secrets: inherit

  # External repo — pin to a SHA for security
  ci-external:
    uses: myorg/shared-workflows/.github/workflows/ci.yml@a1b2c3d4
    with:
      python-version: '3.12'

  # Matrix over environments
  deploy:
    strategy:
      matrix:
        target: [staging, production]
    uses: ./.github/workflows/deploy.yml
    with:
      environment: ${{ matrix.target }}
    secrets: inherit
```

Limits: max 10 nesting levels. Reusable workflows cannot forward environment secrets
(only repo/org secrets).

---

## 10. Composite Actions

File `.github/actions/setup-and-test/action.yml`:

```yaml
name: Setup Pixi and Test
description: Install pixi environment and run the test suite
inputs:
  working-directory:
    description: Directory containing pixi.toml
    required: false
    default: .
  test-command:
    required: false
    default: pixi run test
outputs:
  test-outcome:
    description: success or failure
    value: ${{ steps.run-tests.outcome }}
runs:
  using: composite
  steps:
    - uses: prefix-dev/setup-pixi@v0.9.4
      with:
        working-directory: ${{ inputs.working-directory }}
        cache: true
        frozen: true
    - id: run-tests
      working-directory: ${{ inputs.working-directory }}
      run: ${{ inputs.test-command }}
      shell: bash    # REQUIRED: composite action steps must declare shell explicitly
```

Calling:

```yaml
- uses: actions/checkout@v5
- uses: ./.github/actions/setup-and-test
  with:
    working-directory: agent-scheduler
    test-command: pixi run pytest
```

---

## 11. Environments and Deployment

```yaml
jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.myapp.com
    concurrency:
      group: staging-deploy
      cancel-in-progress: false    # never cancel an in-progress deploy
    steps:
      - run: echo "Deploy to staging"

  deploy-production:
    runs-on: ubuntu-latest
    needs: deploy-staging
    environment:
      name: production
      url: ${{ steps.deploy.outputs.url }}    # dynamic URL from step output
    steps:
      - id: deploy
        run: echo "url=https://myapp.com" >> $GITHUB_OUTPUT
```

Environment protection rules (Required reviewers, Wait timer, Deployment branches)
are configured in GitHub repo **Settings → Environments**, not in YAML.

---

## 12. GitHub Pages

```yaml
name: Deploy Docs
on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false    # avoid partial deploys

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/configure-pages@v5
      - run: |
          pip install mkdocs-material
          mkdocs build --site-dir _site
      - uses: actions/upload-pages-artifact@v3
        with:
          path: _site

  deploy:
    runs-on: ubuntu-latest
    needs: build
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

First deploy requires a one-time manual step: **Settings → Pages → Source: GitHub Actions**.

---

## 13. Workflow Syntax Quick Reference

### Permissions

```yaml
permissions:
  actions: read|write|none
  checks: read|write|none
  contents: read|write|none
  deployments: read|write|none
  id-token: write|none           # write required for OIDC (PyPI, cloud)
  issues: read|write|none
  packages: read|write|none      # write required for GHCR push
  pages: read|write|none
  pull-requests: read|write|none
  security-events: read|write|none    # write required for SARIF upload
  statuses: read|write|none
```

### Concurrency

```yaml
# Cancel older run when new push arrives (most common for CI)
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

# Do not cancel on release branches
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ !contains(github.ref, 'release/') }}
```

### Job defaults and timeout

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    defaults:
      run:
        shell: bash
        working-directory: ./src
    steps:
      - name: Slow step
        timeout-minutes: 10
        run: make build
```

### Job outputs between jobs

```yaml
jobs:
  job1:
    runs-on: ubuntu-latest
    outputs:
      artifact: ${{ steps.build.outputs.artifact-name }}
    steps:
      - id: build
        run: echo "artifact-name=dist-v1.2.3" >> $GITHUB_OUTPUT

  job2:
    needs: job1
    runs-on: ubuntu-latest
    steps:
      - run: echo "Artifact is ${{ needs.job1.outputs.artifact }}"
```

### Conditional execution

```yaml
- name: Only on main
  if: github.ref == 'refs/heads/main'
  run: echo "main"

- name: Skip bots
  if: github.actor != 'dependabot[bot]' && github.actor != 'renovate[bot]'
  run: echo "not a bot"

- name: Always run (even after failure)
  if: always()
  run: echo "cleanup"

- name: On failure only
  if: failure()
  run: notify slack
```

### Prevent infinite loops (auto-commit workflows)

```yaml
# Option 1: [skip ci] in commit message
- uses: stefanzweifel/git-auto-commit-action@v5
  with:
    commit_message: "chore: auto-update [skip ci]"

# Option 2: filter on actor
on:
  push:
    branches: [main]
jobs:
  sync:
    if: github.actor != 'github-actions[bot]'
```
