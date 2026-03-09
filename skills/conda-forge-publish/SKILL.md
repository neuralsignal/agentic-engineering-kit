---
name: conda-forge-publish
description: Publish Python packages to conda-forge — recipe authoring, staged-recipes PR submission, and feedstock maintenance.
---

# conda-forge Publish

End-to-end workflow for publishing a Python package to conda-forge. Covers recipe creation, PR submission to `conda-forge/staged-recipes`, and post-acceptance feedstock updates.

## When to Use

Use this skill when:

- A public Python package (already on PyPI) needs a conda-forge distribution
- The package has system-level dependencies (pandoc, tectonic, librsvg, etc.) that conda-forge can resolve automatically
- Updating an existing conda-forge feedstock after a new PyPI release

## Prerequisites

- Package is already published on PyPI with a stable release
- `gh` CLI authenticated (`gh auth status`)
- The PyPI package uses a standard build backend (hatchling, setuptools, flit, maturin)

## Workflow

### Phase 1: Create the Recipe

Create `recipe/recipe.yaml` in the package repo (for reference — the actual submission goes to staged-recipes).

Use the v1 recipe format (`schema_version: 1`). The key sections:

```yaml
schema_version: 1

context:
  version: "<PYPI_VERSION>"
  python_min: "<MIN_PYTHON_VERSION>"

package:
  name: <package-name>
  version: ${{ version }}

source:
  url: https://pypi.org/packages/source/<first-letter>/<package-name>/<package_name>-${{ version }}.tar.gz
  sha256: <SHA256_OF_SDIST>

build:
  noarch: python
  number: 0
  script: python -m pip install . -vv --no-deps --no-build-isolation

requirements:
  host:
    - python ${{ python_min }}.*
    - pip
    - <build-backend>
  run:
    - python >=${{ python_min }}
    - <runtime-dep-1>
    - <runtime-dep-2>
    # System deps available on ALL platforms via conda-forge:
    - pandoc >=3.5
    # Only add system deps if available on linux-64, osx-64, AND win-64.
    # Check https://anaconda.org/conda-forge/<pkg>/files before adding.

tests:
  - python:
      imports:
        - <package_name>
      pip_check: true
      python_version: ${{ python_min }}.*
  - script:
      - <cli-name> --help

about:
  homepage: https://github.com/<org>/<repo>
  repository: https://github.com/<org>/<repo>
  summary: <one-line description>
  description: |
    <multi-line description>
  license: <SPDX-identifier>
  license_file: LICENSE

extra:
  recipe-maintainers:
    - <github-username>
```

#### Recipe Decisions

| Decision | Rule |
|----------|------|
| `noarch: python` | Use for pure Python packages (no C extensions, no platform-specific code) |
| `--no-deps --no-build-isolation` | Always. conda handles deps; build isolation is redundant |
| Entry points | Do NOT add `entry_points` to `build:` — rattler-build v1 does not support it. pip reads `[project.scripts]` from `pyproject.toml` automatically during install |
| `python_min` context var | Required for `noarch: python`. Set to the package's minimum Python version (e.g., `"3.12"`). Use `${{ python_min }}.*` in host, `>=${{ python_min }}` in run, `python_version: ${{ python_min }}.*` in tests |
| `host` deps | The build backend (`hatchling`, `setuptools`, `flit-core`) + `pip` + `python ${{ python_min }}.*` |
| `run` deps | Mirror `[project.dependencies]` from pyproject.toml, plus system deps available on ALL platforms (linux-64, osx-64, win-64) via conda-forge. Omit system deps that aren't available on all platforms — document them as manual installs instead |
| `tests` section | Use v1 format: `- python: imports: [...]` and `- script: [...]`. Always include `pip_check: true` and `python_version: ${{ python_min }}.*` |
| `license` | SPDX identifier (e.g., `MIT`, `Apache-2.0`, `BSD-3-Clause`) |

#### Getting the SHA256

After the package is published to PyPI:

```bash
curl -s https://pypi.org/pypi/<package-name>/<version>/json | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print([u for u in d['urls'] if u['packagetype']=='sdist'][0]['digests']['sha256'])"
```

### Phase 2: Submit to conda-forge

1. **Fork** `conda-forge/staged-recipes`:

```bash
gh repo fork conda-forge/staged-recipes --clone=false
```

2. **Clone the fork** (shallow):

```bash
git clone --depth 1 git@github.com:<your-org>/staged-recipes.git /tmp/staged-recipes
```

3. **Create branch, copy recipe**:

```bash
cd /tmp/staged-recipes
git checkout -b <package-name>
mkdir -p recipes/<package-name>
cp <path-to-repo>/recipe/recipe.yaml recipes/<package-name>/recipe.yaml
```

4. **Commit and push**:

```bash
git add recipes/<package-name>/recipe.yaml
git commit -m "Add <package-name> recipe"
git push -u origin <package-name>
```

5. **Create PR** against `conda-forge/staged-recipes`:

```bash
gh pr create --repo conda-forge/staged-recipes \
  --title "Add <package-name>" \
  --body "<description of the package and why conda-forge is valuable (e.g., system deps)>

Checklist

- [x] Title of this PR is meaningful
- [x] License file is packaged
- [x] Source is from official source (PyPI sdist)
- [x] Package does not vendor other packages
- [x] No static libraries
- [x] Build number is 0
- [x] Tarball (url) used, not repo
- [x] GitHub user listed in maintainer section confirms willingness
" \
  --head <your-org>:<package-name>
```

6. **Ping the review team**:

```bash
gh pr comment <PR_NUMBER> --repo conda-forge/staged-recipes \
  --body "@conda-forge/help-python, ready for review!"
```

7. **Clean up**:

```bash
rm -rf /tmp/staged-recipes
```

### Phase 3: Post-Acceptance

After the staged-recipes PR is merged, conda-forge creates a feedstock repo at `conda-forge/<package-name>-feedstock`. You are auto-added as maintainer.

#### Updating for a New Release

When a new version is published to PyPI:

1. A bot (usually `regro-cf-autotick-bot`) opens a PR on the feedstock with the version bump
2. Review the PR — check that deps haven't changed
3. If deps changed, update `recipe/recipe.yaml` in the feedstock PR
4. Merge the PR — conda-forge CI builds and publishes the new version

#### Manual Feedstock Update

If the bot hasn't opened a PR:

```bash
gh repo clone conda-forge/<package-name>-feedstock /tmp/<package-name>-feedstock
cd /tmp/<package-name>-feedstock
git checkout -b bump-<new-version>
```

Edit `recipe/recipe.yaml`:
- Update `version` in the `context` section
- Update `sha256` (get from PyPI, see command above)
- Reset `build.number` to `0`
- Update `run` deps if changed

```bash
git add recipe/recipe.yaml
git commit -m "Update to <new-version>"
git push -u origin bump-<new-version>
gh pr create --title "Update to <new-version>"
```

## Gotchas

| Issue | Fix |
|-------|-----|
| `lock-file not up-to-date` in CI after version bump in pixi.toml | Run `pixi install` locally to regenerate `pixi.lock` before committing. Add a pre-commit hook (see below). |
| `noarch: python` but package has C extensions | Remove `noarch: python` and add `${{ compiler('c') }}` to `build` requirements |
| SHA256 placeholder committed | Get the real hash only after PyPI publish; use a follow-up commit or PR |
| Staged-recipes PR sits for weeks | Ping `@conda-forge/help-python` in a comment; ask on [conda-forge Zulip](https://conda-forge.zulipchat.com) |
| Build fails on all platforms for `noarch: python` | Missing `python_min` context variable. Without it, CI may test against a Python version that doesn't satisfy the `>=` constraint. Add `python_min: "<version>"` to `context` and use it in host/run/tests |
| `unknown field 'entry_points'` in build | rattler-build v1 does not support `entry_points` in `build:`. Remove it — pip reads `[project.scripts]` from `pyproject.toml` automatically |
| `noarch` package fails on win_64 only | A `run` dependency isn't available on win-64 in conda-forge. Check each system dep at `https://anaconda.org/conda-forge/<pkg>/files`. Remove unavailable deps from `run` and document them as manual installs |
| `pip_check` fails in tests | A run dependency is missing or version-pinned too tightly |
| Protected main branch blocks SHA256 update | Create a separate branch/PR for the SHA256 fill (can't push directly to main) |

### Pre-commit Hook for pixi.lock

Add to `.pre-commit-config.yaml` to prevent stale lockfile commits:

```yaml
- repo: local
  hooks:
    - id: pixi-lock
      name: pixi lock
      entry: bash -c 'pixi install --locked 2>/dev/null || { pixi lock && git add pixi.lock; }'
      language: system
      files: pixi\.toml$
      pass_filenames: false
```
