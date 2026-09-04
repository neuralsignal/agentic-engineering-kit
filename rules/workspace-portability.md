---
description: Workspace portability -- no hardcoded paths, config-derived roots
alwaysApply: true
---

# Workspace Portability

Never hardcode user-specific or machine-specific paths in documentation, agent instructions, or config files that are tracked in git. Hardcoded paths make the workspace non-portable across machines and users.

**Scope:** all files in the workspace, agent-consumed (rules, skills, READMEs) and human-facing (setup guides, architecture docs) alike. Agent docs use only relative paths from the workspace root; project-specific paths live in each project's config file. Generated, gitignored files may contain absolute paths since setup scripts produce them.

## How Paths Are Derived

- **Workspace root**: derived at runtime from the location of the script or package being executed (e.g., `Path(__file__).parent.parent`).
- **Runtime config paths**: relative paths in a project config resolve against the config file's directory, not process CWD. Resolve them explicitly (`config_dir / relative_path`) before file I/O; do not rely on a global `chdir` as the only correctness mechanism. Use explicit env var assignment (`os.environ[...] = ...`), never `setdefault`, when a config file is the authoritative source for a value. Document this in setup docs when commands may be run from different shells.

## Moving a conda-style project requires deleting its environment

**Moved a project directory? Delete its environment directory (`.pixi/`, `.conda/`, or equivalent) and reinstall — a plain reinstall will not repair it.**

A conda environment stores the absolute prefix it was created at, baked into binaries. Conda patches that prefix when it installs; a later install does not re-patch it. So moving a project directory leaves its environment pointing at the old path.

The failure is silent and misattributed. The clearest symptom is OpenSSL: its CA bundle path still names the pre-move directory, so the environment has **zero trust anchors** and rejects every TLS chain with `CERTIFICATE_VERIFY_FAILED — self-signed certificate in certificate chain`. Code using `requests`/`httpx` keeps working (they pass `certifi` explicitly), which hides the problem; database drivers with retry logic can turn it into a long hang rather than an error.

Nothing is lost by deleting — the environment directory is gitignored and rebuilt from the lock file. Audit every environment (the compiled binary holds the stale path, so `ssl/openssl.cnf` is the wrong probe):

```bash
for py in **/.pixi/envs/*/bin/python; do
  "$py" -c "import ssl,sys;print(sys.prefix, ssl.get_default_verify_paths().openssl_cafile)"
done   # the second path must sit inside the first
```
