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

## When to Use

Use this skill when scaffolding new GitHub Actions workflows or auditing existing ones:
- Setting up CI (pytest, ruff, mypy, pre-commit) for a Python repo (pixi, uv, or pip)
- Publishing packages to PyPI (OIDC trusted publisher) or images to GHCR
- Adding security scanning (CodeQL, Trivy) or release automation (release-please, git-cliff)
- Configuring Dependabot, PR automation, reusable workflows, environments, or GitHub Pages

## Decision Guide

| You want to… | Go to |
|--------------|-------|
| Run tests / lint / type-check on push or PR | [CI workflows](references/ci-workflows.md) |
| Set up pixi, uv, or pip with caching | [CI workflows](references/ci-workflows.md) |
| Publish a package to PyPI (no stored token) | [Publishing](references/publishing.md) |
| Build and push a Docker image to GHCR | [Publishing](references/publishing.md) |
| Scan code/containers (CodeQL, Trivy) | [Security and automation](references/security-and-automation.md) |
| Automate versioning and changelogs | [Security and automation](references/security-and-automation.md) |
| Configure Dependabot or PR labeling/stale bots | [Security and automation](references/security-and-automation.md) |
| Factor shared logic into reusable/composite workflows | [Advanced](references/advanced.md) |
| Deploy with environments or publish to GitHub Pages | [Advanced](references/advanced.md) |
| Look up permissions, concurrency, conditionals syntax | [Advanced](references/advanced.md) |

Start by pinning action versions from the table below, then jump to the relevant reference.

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

## References

Detailed pattern catalogs live in `references/`:

- [CI workflows](references/ci-workflows.md) — CI patterns (pytest, coverage, ruff, mypy, pre-commit, OS cross-matrix) and Python toolchain setups (pixi, uv, pip caching).
- [Publishing](references/publishing.md) — PyPI publishing via OIDC trusted publisher (build/publish, uv publish, build-and-inspect) and Docker builds to GHCR (metadata, multi-platform, registry cache).
- [Security and automation](references/security-and-automation.md) — security scanning (CodeQL, Trivy), release automation (release-please, gh-release, git-cliff), Dependabot config, and PR automation (labeler, stale bot, CODEOWNERS).
- [Advanced](references/advanced.md) — reusable workflows, composite actions, environments and deployment, GitHub Pages, and the workflow syntax quick reference (permissions, concurrency, job outputs, conditionals, loop prevention).

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
