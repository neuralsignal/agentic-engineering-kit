# Security Scanning and Automation

Security scanning (CodeQL, Trivy), release automation (release-please, git-cliff),
Dependabot configuration, and PR automation (labeler, stale bot, CODEOWNERS).

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
