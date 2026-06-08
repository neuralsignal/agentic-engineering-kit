# Publishing: PyPI and Docker

Package and image publishing patterns — PyPI via OIDC Trusted Publisher, and Docker
builds pushed to GHCR (multi-platform, caching).

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
