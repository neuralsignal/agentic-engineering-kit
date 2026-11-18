# Maintainer automation

Keep CI, docs deployment, and publishing in each repository. Use one Claude workflow for an explicit request from a maintainer. To request implementation, write `@claude implement this issue and open a draft PR` in an issue comment. The action owns any resulting PR. Routine workflow dependency updates use Dependabot.

## Connect a Pixi repository

Add a caller job in the project's `.github/workflows/` directory. Replace `<reviewed-commit-sha>` with a published Agentic Engineering Kit commit that contains the reusable workflow.

```yaml
name: Claude Mention Handler

on:
  issue_comment:
    types: [created]

jobs:
  claude:
    permissions:
      contents: write
      pull-requests: write
      issues: write
      id-token: write
    uses: neuralsignal/agentic-engineering-kit/.github/workflows/maintainer-claude-pixi.yml@<reviewed-commit-sha>
    secrets:
      CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
```

The reusable workflow verifies that the request is from a maintainer and that any linked PR branch belongs to the same repository. It installs the locked Pixi environment and gives Claude a bounded run. The caller passes the inference credential explicitly. By default the action uses the installed Claude GitHub App. An existing repository-scoped custom GitHub credential can be passed as `CLAUDE_GITHUB_TOKEN` during migration. [Claude Action authentication](https://github.com/anthropics/claude-code-action/blob/main/docs/faq.md#triggering-and-authentication)

## Migrate an existing factory

1. Keep CI, docs, and release workflows enabled. Add a weekly `github-actions` Dependabot entry at root and keep the existing Pixi lockfile.
2. Run a maintainer request on a disposable issue and confirm that one draft PR appears and the expected CI starts. Send follow-ups in that PR's conversation to reuse its branch. Verify the existing release checks using the project's release procedure.
3. Disable the replaced factory workflows in GitHub Actions. Keep the rollback history in Git. Remove the retired files in a separate PR after the pilot passes and consumer references have been checked.
4. Repeat on the other repositories only after the pilot passes. Check the Actions run summary for progress.

For rollback, restore the previous caller revision and re-enable only the legacy workflows needed for the prior behavior. Capture the previous workflow and secret names before cutover.
