# Upstream sync

The reusable workflow compares fork main with an explicitly configured upstream main. Git builds a two-parent candidate. Claude runs only for ordinary conflicts. A separate job verifies the candidate and queues a merge commit through the fork's required GitHub Actions check.

## Fork setup

- Pin the caller to a commit that contains both `.github/workflows/upstream-sync.yml` and `.github/scripts/upstream-sync.mjs`. The reusable workflow checks out its own script at that exact commit.
- Set the `upstream_repository` and `required_check` inputs. Use a stable check that aggregates the fork's whole CI matrix. Create an effective main ruleset that requires the check from the GitHub Actions integration and requires the candidate to be up to date. Keep the publisher outside bypass lists.
- Enable merge commits and GitHub auto-merge. Install the publishing GitHub App on the fork with Contents and Pull requests write permissions. Set `UPSTREAM_SYNC_APP_CLIENT_ID` and `UPSTREAM_SYNC_APP_PRIVATE_KEY` in the caller. The publisher uses a short-lived installation token. Using the workflow's own GitHub token for publication can leave CI in an approval-required state.
- Use the existing Claude inference credential for `CLAUDE_CODE_OAUTH_TOKEN`. The conflict job receives only a read-only GitHub token and the Claude credential. It never receives the publishing App key or token.
- Run the manual workflow in dry-run mode. It reports the exact SHAs and Git result. Verify a sampled non-dry PR starts CI and that GitHub merges it only after the required check passes. Set `UPSTREAM_SYNC_ENABLED=true` to enable the weekly run in a caller that uses this variable.

## Review and recovery

Incoming changes to GitHub workflows and release or agent-control settings stop before Claude, candidate publication, and CI. The run summary lists the affected paths. Review and merge such upstream changes separately.

The publisher updates one bot-owned branch using a lease and checks its PR's last published SHA. If a push succeeds before PR setup fails, a retry can resume only when the branch is already at the independently verified candidate commit. If a maintainer changed the branch or PR body, the publisher leaves those edits for review. A missing CI check, changed input ref, or failed candidate leaves fork main untouched. Pause the weekly run by clearing `UPSTREAM_SYNC_ENABLED`. Revert a bad completed sync using a reviewed PR.

Local fixtures exercise an already-current fork, clean merge, conflict resolution, unresolved or extra edits, protected paths, merge ancestry, and required check identity.

## Sources

- [GitHub reusable workflow identity](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts#job-context)
- [GitHub workflow token and PR events](https://docs.github.com/en/actions/concepts/security/github_token#when-github_token-triggers-workflow-runs)
- [Claude action security](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md)
