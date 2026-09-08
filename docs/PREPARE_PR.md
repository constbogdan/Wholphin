# Safe pull-request preparation

`scripts/prepare-pr.ps1` is the preferred completion workflow for a reviewed Wholphin task. It automates mechanical Git work while retaining explicit human approval for scope, the staged snapshot, commit, and publication.

## Normal guided workflow

From a purpose-specific branch rooted in current `origin/main`:

``` powershell
.\scripts\prepare-pr.ps1
```

The script performs preflight, displays existing branch-only commits and paths separately from current working-tree candidates, allows numbered exclusions from the candidate set, and confirms the complete eventual PR scope. The total unique PR path count is prominent; tracked diff statistics are explicitly separate from untracked/new files so the latter cannot disappear visually from the review. It then runs local Standard validation by default, verifies that validation did not change the candidate snapshot, stages only confirmed candidate paths, displays the complete staged diff, confirms the title and commit, verifies that the produced commit tree is exactly the reviewed staged tree, then separately asks whether to push and create/provide the PR.

Standard validation requires actual focused JVM test patterns. Supply them up front or enter them when prompted:

``` powershell
.\scripts\prepare-pr.ps1 -TestFilter '*RelevantTest*'
```

When Standard is selected for ordinary work but no honest focused JVM test pattern applies, leave the pattern prompt blank. The guided workflow recommends switching to Full, with **yes** as the default. Accepting runs Full without inventing a filter; declining stops before staging. In non-interactive use, select `-Level Full` explicitly when no focused test exists.

Use Full locally for major architecture, release-sensitive work, an explicit requirement, or when no honest focused test applies:

``` powershell
.\scripts\prepare-pr.ps1 -Level Full
```

Upstream-sync branches automatically run Standard followed by Full and retain the semantic-resolution requirements in `docs/UPSTREAM_SYNC.md`. They still require meaningful focused JVM patterns and do not use the no-filter Full fallback.

## Approval and safety boundaries

The guided workflow requires confirmation of:

1. Exact changed-path scope before validation or staging.
2. The displayed staged snapshot before commit preparation.
3. The commit title and commit itself.
4. Push and PR publication after the commit.

It never resets, restores, cleans, stashes, force-pushes, merges, or deletes branches/worktrees. It refuses protected `main`, detached HEAD, active Git operations, unmerged paths, unexpected remotes, branches not descended from current `origin/main`, out-of-scope dirty work, ignored/local artifacts, stale validation state, staged-snapshot drift, and publication requiring a force push.

The safest v1 rule for parallel work is deliberate: once scope is confirmed, every dirty path must belong to it. Use a separate worktree rather than temporarily hiding unrelated changes.

## Resumable state and advanced phases

Human-readable state is stored at the Git path `.git/wholphin-prepare-pr-state.json` (or the worktree-specific equivalent). It records branch/base/HEAD, already committed PR paths and commits, confirmed candidate paths, their complete publication union, intended snapshot hash, validation results, staged snapshot/tree hashes, approved title, and completed phase. A changed branch, base, HEAD, working snapshot, or index invalidates the relevant phase.

Each invocation replaces the ignored repository-root `prepare-pr.log`. The log records timestamps, phases/results, branch/base/HEAD, confirmed scope, validation choice/result, snapshot and tree identities, staging/commit/publication outcomes, refusals/errors, actionable Git stderr, and a PR URL when one is known. The script does not log credentials, tokens, environment dumps, or PR-body contents, and always reports the log path at completion or failure.

Advanced/recovery commands are available when an intentional review stop occurs:

``` powershell
.\scripts\prepare-pr.ps1 -Phase Audit
.\scripts\prepare-pr.ps1 -Phase Validate -TestFilter '*RelevantTest*'
.\scripts\prepare-pr.ps1 -Phase Stage
.\scripts\prepare-pr.ps1 -Phase Commit -Title 'chore: describe the reviewed change'
.\scripts\prepare-pr.ps1 -Phase Publish
```

Automation and tests may use `-NonInteractive` with the corresponding `-ConfirmScope`, `-ConfirmCommit`, or `-ConfirmPublish` switch. Those switches are explicit approvals, not bypasses; all snapshot and safety checks still run.

## Validation and autofixes

Normal work uses local Standard validation followed by required GitHub `CI / Full validation`. Local Full remains appropriate for major checkpoints. Validation runs before real staging and is bound to a read-only, Git-filter-aware identity of each confirmed working entry, including mode, object type, object ID, and deletion state.

Standard and Full invoke repository-wide pre-commit, whose hooks may apply autofixes. If validation changes any file, prepare-pr stops without staging, reports the dirty paths, and requires review followed by a new Audit/Validate pass. Formatter changes are never silently included.

## Publishing and GitHub CLI

The first push uses `git push -u origin <branch>`; subsequent pushes use ordinary fast-forward `git push`. Remote divergence is refused and force push is never offered.

When authenticated `gh` is available, the script checks for an existing open PR before creating one. It reports an existing PR without modifying it. Without authenticated `gh`, commit and push still work and the script prints the exact GitHub compare/new-PR URL; it does not claim whether a PR already exists.

After publication, required CI remains pending and merge remains manual. Waiting with `gh pr checks --watch` is an optional follow-up, never part of the default workflow.

## After merge

From a clean working tree, update the local integration branch safely:

``` powershell
git switch main
git pull --ff-only origin main
```

Local/remote branch and worktree deletion remains manual and outside prepare-pr v1.

## Portability

Other downstream repositories should reuse this UX and safety contract, not Wholphin's implementation details. Seerr must supply its own pnpm validation, integration baseline, high-risk paths, workflow guards, artifacts, and release policy before adapting the flow.
