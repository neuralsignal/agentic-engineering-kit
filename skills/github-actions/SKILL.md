---
name: github-actions
description: >
  Scaffold and audit general GitHub Actions workflows. Covers CI (pytest, ruff, mypy),
  Python toolchains (pixi, uv), PyPI publishing (OIDC trusted publisher), Docker
  (GHCR, multi-platform), security scanning (CodeQL, Trivy), release automation
  (release-please, git-cliff), Dependabot, PR automation, reusable workflows,
  environments, and GitHub Pages.
compatibility: Requires gh CLI and git. Designed for GitHub-hosted and self-hosted runners.
license: MIT
---

# GitHub Actions -- Pattern Catalog

Reference for authoring and auditing GitHub Actions workflows. Covers CI, packaging,
Docker, security, release automation, and workflow architecture patterns.

---

## Action Version Reference

| Action | Version | Notes |
|--------|---------|-------|
| `actions/checkout` | v5 | Node 24 |
| `actions/setup-python` | v5 | Built-in pip cache via `cache: pip` |
| `actions/cache` | v4 | v3 deprecated |
| `actions/upload-artifact` | v4 | Must match `download-artifact` major version |
| `actions/download-artifact` | v4 | |
| `actions/labeler` | v6 | Node 24; requires runner ≥v2.327.1 |
| `actions/stale` | v10 | Node 24 |
| `actions/configure-pages` | v5 | |
| `actions/upload-pages-artifact` | v3 | |
| `actions/deploy-pages` | v4 | |
| `prefix-dev/setup-pixi` | v0.9.4 | Cache on by default when `pixi.lock` present |
| `astral-sh/setup-uv` | v7 | Built-in cache with `enable-cache: true` |
| `docker/login-action` | v3 | |
| `docker/setup-buildx-action` | v3 | |
| `docker/setup-qemu-action` | v3 | |
| `docker/build-push-action` | v6 | |
| `docker/metadata-action` | v5 | |
| `github/codeql-action/{init,analyze,upload-sarif}` | v4 | |
| `aquasecurity/trivy-action` | 0.33.1 | Pin exact version (no `v` prefix) |
| `pypa/gh-action-pypi-publish` | release/v1 | Floating tag; auto-updates |
| `googleapis/release-please-action` | v4 | |
| `softprops/action-gh-release` | v2 | |
| `hynek/build-and-inspect-python-package` | v2 | |
| `orhun/git-cliff-action` | v4 | |
| `stefanzweifel/git-auto-commit-action` | v5 | |
| `pre-commit/action` | v3.0.1 | Maintenance-only; prefer pre-commit.ci service |

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

---

## 3. PyPI Publishing (Trusted Publisher / OIDC)

No stored API token. Configure the Trusted Publisher first in PyPI project Settings →
Publishing: owner, repo name, workflow filename, environment name.

### Two-job pattern (build then publish)

```yaml
name: Publish to PyPI
on:
  release:
    types: [published]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      - run: |
          pip install build
          python -m build
      - uses: actions/upload-artifact@v4
        with:
          name: release-dists
          path: dist/

  publish:
    runs-on: ubuntu-latest
    needs: build
    environment:
      name: pypi
      url: https://pypi.org/project/my-package/
    permissions:
      id-token: write    # required for OIDC exchange
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: release-dists
          path: dist/
      - uses: pypa/gh-action-pypi-publish@release/v1
```

### uv publish

```yaml
jobs:
  publish:
    runs-on: ubuntu-latest
    environment:
      name: pypi
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v5
      - uses: astral-sh/setup-uv@v7
      - run: uv build
      - run: uv publish    # detects OIDC automatically from id-token: write
```

### With hynek/build-and-inspect-python-package

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      package_name: ${{ steps.inspect.outputs.package_name }}
    steps:
      - uses: actions/checkout@v5
      - id: inspect
        uses: hynek/build-and-inspect-python-package@v2

  publish:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/project/${{ needs.build.outputs.package_name }}/
    permissions:
      id-token: write
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: Packages
          path: dist/
      - uses: pypa/gh-action-pypi-publish@release/v1
```

---

## 4. Docker: Build and Push to GHCR

### Full workflow with metadata and GHA cache

```yaml
name: Docker
on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  docker:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v5

      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix=sha-

      - uses: docker/setup-buildx-action@v3

      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Multi-platform build

```yaml
- uses: docker/setup-qemu-action@v3
- uses: docker/setup-buildx-action@v3
- uses: docker/build-push-action@v6
  with:
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ${{ steps.meta.outputs.tags }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### Registry cache (for large images where GHA 10 GB limit is too small)

```yaml
- uses: docker/build-push-action@v6
  with:
    push: true
    tags: ghcr.io/myorg/myapp:latest
    cache-from: type=registry,ref=ghcr.io/myorg/myapp:buildcache
    cache-to: type=registry,ref=ghcr.io/myorg/myapp:buildcache,mode=max
```

**Gotcha:** GHCR image names must be lowercase:
```yaml
- name: Lowercase repo name
  run: echo "REPO=${GITHUB_REPOSITORY,,}" >> $GITHUB_ENV
# then: ghcr.io/${{ env.REPO }}
```

---

## 5. Security Scanning

### CodeQL (Python)

```yaml
name: CodeQL
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '20 14 * * 1'    # Weekly Monday scan

jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      contents: read
    strategy:
      fail-fast: false
      matrix:
        include:
          - language: python
            build-mode: none    # Python is interpreted; no build step needed
    steps:
      - uses: actions/checkout@v5
      - uses: github/codeql-action/init@v4
        with:
          languages: ${{ matrix.language }}
          build-mode: ${{ matrix.build-mode }}
      - uses: github/codeql-action/analyze@v4
        with:
          category: '/language:${{ matrix.language }}'
```

### Trivy filesystem scan → Security tab

```yaml
jobs:
  trivy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    steps:
      - uses: actions/checkout@v5
      - uses: aquasecurity/trivy-action@0.33.1
        with:
          scan-type: fs
          scan-ref: .
          format: sarif
          output: trivy-results.sarif
          severity: CRITICAL,HIGH
      - uses: github/codeql-action/upload-sarif@v4
        if: always()
        with:
          sarif_file: trivy-results.sarif
```

### Trivy container scan (fail build on findings)

```yaml
- run: docker build -t myapp:${{ github.sha }} .
- uses: aquasecurity/trivy-action@0.33.1
  with:
    image-ref: myapp:${{ github.sha }}
    format: sarif
    output: trivy-results.sarif
    severity: CRITICAL,HIGH
    ignore-unfixed: true
    exit-code: '1'
- uses: github/codeql-action/upload-sarif@v4
  if: always()
  with:
    sarif_file: trivy-results.sarif
```

---

## 6. Release Automation

### release-please (conventional commits → auto version bump + changelog)

```yaml
name: Release Please
on:
  push:
    branches: [main]

permissions:
  contents: write
  pull-requests: write

jobs:
  release-please:
    runs-on: ubuntu-latest
    outputs:
      release_created: ${{ steps.release.outputs.release_created }}
      tag_name: ${{ steps.release.outputs.tag_name }}
    steps:
      - uses: googleapis/release-please-action@v4
        id: release
        with:
          release-type: python    # reads version from pyproject.toml
          # token: ${{ secrets.RELEASE_PLEASE_TOKEN }}   # PAT for CI checks on release PRs

  publish:
    needs: release-please
    if: needs.release-please.outputs.release_created == 'true'
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write
    steps:
      - uses: actions/checkout@v5
      - uses: astral-sh/setup-uv@v7
      - run: uv build
      - run: uv publish
```

Conventional commit bump rules:
- `fix:` → patch
- `feat:` → minor
- `feat!:` or `BREAKING CHANGE:` in body → major
- `chore:`, `docs:`, `refactor:`, `test:` → no version bump

### softprops/action-gh-release (tag-triggered, with asset upload)

```yaml
name: Release
on:
  push:
    tags: ['v*.*.*']

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v5
      - uses: astral-sh/setup-uv@v7
      - run: uv build
      - uses: softprops/action-gh-release@v2
        with:
          files: |
            dist/*.whl
            dist/*.tar.gz
          body_path: CHANGELOG.md
```

### git-cliff changelog generation

`cliff.toml` (minimal conventional commits config):

```toml
[changelog]
header = "# Changelog\n"
body = """
{% for group, commits in commits | group_by(attribute="group") %}
## {{ group | upper_first }}
{% for commit in commits %}
- {{ commit.message | upper_first }}\
{% endfor %}
{% endfor %}
"""

[git]
conventional_commits = true
filter_unconventional = true
commit_parsers = [
  { message = "^feat", group = "Features" },
  { message = "^fix", group = "Bug Fixes" },
  { message = "^docs", group = "Documentation" },
  { message = "^chore", skip = true },
  { message = "^refactor", skip = true },
]
```

```yaml
- uses: orhun/git-cliff-action@v4
  id: cliff
  with:
    config: cliff.toml
    args: --verbose --latest
  env:
    OUTPUT: CHANGELOG.md
    GITHUB_REPO: ${{ github.repository }}

- uses: stefanzweifel/git-auto-commit-action@v5
  with:
    commit_message: "docs: update CHANGELOG [skip ci]"
    file_pattern: CHANGELOG.md
```

---

## 7. Dependabot Configuration

File: `.github/dependabot.yml`

```yaml
version: 2
updates:
  - package-ecosystem: pip
    directory: /
    schedule:
      interval: weekly
      day: monday
      time: '05:00'
      timezone: Europe/Zurich
    groups:
      dev-dependencies:
        dependency-type: development
        update-types: [minor, patch]
    labels: [dependencies, python]
    versioning-strategy: increase
    ignore:
      - dependency-name: django
        update-types: [version-update:semver-major]

  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    labels: [dependencies, github-actions]

  - package-ecosystem: docker
    directory: /
    schedule:
      interval: weekly

  - package-ecosystem: npm
    directory: /frontend
    schedule:
      interval: weekly
    groups:
      react:
        patterns: ['react', 'react-dom', '@types/react*']
```

**Note:** Dependabot has no pixi ecosystem support. Point the `pip` ecosystem at
`pyproject.toml` for Python dependencies managed via pixi.

---

## 8. PR Automation

### Auto-labeler

Workflow `.github/workflows/labeler.yml`:

```yaml
name: Label PR
on:
  pull_request_target:
    types: [opened, synchronize]
jobs:
  label:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/labeler@v6
        with:
          sync-labels: true    # remove labels when globs no longer match
```

Config `.github/labeler.yml`:

```yaml
python:
  - changed-files:
      - any-glob-to-any-file: ['**/*.py', 'pyproject.toml', 'pixi.toml']

documentation:
  - changed-files:
      - any-glob-to-any-file: ['docs/**', '**/*.md']

ci:
  - changed-files:
      - any-glob-to-any-file: ['.github/**']

dependencies:
  - changed-files:
      - any-glob-to-any-file: ['**/requirements*.txt', 'pixi.toml', 'pixi.lock', 'uv.lock']

breaking:
  - head-branch: ['^breaking/', 'breaking/']
```

Glob strategies: `any-glob-to-any-file` (OR) is the most common. Use `all-globs-to-all-files` (AND) only when all patterns must match all files.

### Stale bot

```yaml
name: Mark stale
on:
  schedule:
    - cron: '0 8 * * 1'
jobs:
  stale:
    runs-on: ubuntu-latest
    permissions:
      issues: write
      pull-requests: write
    steps:
      - uses: actions/stale@v10
        with:
          days-before-stale: 60
          days-before-close: 14
          stale-issue-label: stale
          stale-pr-label: stale
          stale-issue-message: >
            Marked stale due to inactivity. Will close in 14 days if no update.
          exempt-issue-labels: 'pinned,security,roadmap'
          exempt-pr-labels: 'pinned,wip'
          exempt-all-milestones: true
          operations-per-run: 100    # prevents rate-limit on large repos
```

### CODEOWNERS

File `.github/CODEOWNERS`:

```
# Default: everything requires core team review
*                   @org/core-team

# CI/CD changes
/.github/           @org/devops

# Python source
/src/               @org/data-team
/packages/          @org/data-team

# Docs
/docs/              @org/everyone
```

Rules: last matching pattern wins. Teams need explicit `write` repo access.
Enable "Require review from Code Owners" in branch protection settings.

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

---

## Common Gotchas

| Gotcha | Fix |
|--------|-----|
| `upload-artifact@v3` + `download-artifact@v4` | Major versions must match |
| `pull_request` from fork has no write access | Use `pull_request_target` for labeler/commenter workflows; read the security implications |
| `GITHUB_TOKEN` cannot trigger another workflow | Use a PAT or GitHub App token for cross-workflow triggers |
| Dependabot PRs cannot access org secrets | Add Dependabot-specific secrets in Settings → Secrets → Dependabot |
| `workflow_call` cannot forward environment secrets | Only repo/org secrets can be forwarded |
| Docker image name uppercase rejected by GHCR | `echo "REPO=${GITHUB_REPOSITORY,,}" >> $GITHUB_ENV` to lowercase |
| pixi.lock not committed | `setup-pixi` runs `--locked` by default; commit the lock file |
| CodeQL for Python: do not add `autobuild` step | Use `build-mode: none`; autobuild is for compiled languages only |
| release-please default token prevents CI on release PRs | Use a PAT (`secrets.RELEASE_PLEASE_TOKEN`) so push triggers CI |
| `pre-commit/action` is maintenance-only | Use pre-commit.ci service for PR checks; keep action for push CI |
| `cancel-in-progress: true` on deploy jobs | Set `cancel-in-progress: false` for deploys to avoid partial rollouts |
| Composite action `run:` steps missing `shell:` | Each `run:` step in a composite action requires explicit `shell: bash` |
| Matrix job outputs expose only last successful job | Use artifacts instead of job outputs for multi-job matrix data |
| release-please `release-type: python` needs `pyproject.toml` | Version must be in `[project] version = "x.y.z"` (not dynamic) |
