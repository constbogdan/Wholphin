# Safe pull-request preparation

`scripts/prepare-pr.ps1` is Wholphin's publication command. Codex and repository tooling must not invoke it merely because work appears complete. Running it, or explicitly instructing Codex to run it, is the user's **READY TO PUBLISH** decision. The next normal human decision is **READY TO MERGE** after the pull request and required checks are available in GitHub.

## Normal autonomous workflow

From a purpose-specific branch rooted in current `origin/main`:

``` powershell
.\scripts\prepare-pr.ps1
```

After that one publication authorization, the script performs preflight, audits the complete eventual PR scope, selects validation, verifies snapshot stability, stages only the exact scope, verifies the staged tree, generates a Conventional Commit title, commits, verifies the committed tree, safely pushes, and delegates existing-PR lookup or PR creation to authenticated GitHub CLI. It does not ask routine scope, validation, stage, title, commit, push, or PR questions when policy provides one safe answer.

Supply actual focused JVM test patterns when they exist:

``` powershell
.\scripts\prepare-pr.ps1 -TestFilter '*RelevantTest*'
```

Explicit meaningful patterns select Standard. With no honest focused pattern, the script selects Full automatically and never invents a test. An explicit `-Level Full` remains available.

Use Full locally for major architecture, release-sensitive work, an explicit requirement, or when no honest focused test applies:

``` powershell
.\scripts\prepare-pr.ps1 -Level Full
```

Upstream-sync branches automatically run Standard followed by Full and retain the semantic-resolution requirements in `docs/UPSTREAM_SYNC.md`. They still require meaningful focused JVM patterns and do not use the no-filter Full fallback.

## Authority and safety boundaries

Publication starts only from an explicit user instruction such as “prepare the PR,” “publish this,” or an unambiguous equivalent. Passing tests or an agent's belief that work is ready is not authorization. Once authorized, the normal successful path has no further interaction before a PR exists.

It never resets, restores, cleans, stashes, force-pushes, merges, or deletes branches/worktrees. It refuses protected `main`, detached HEAD, active Git operations, unmerged paths, unexpected remotes, branches not descended from current `origin/main`, out-of-scope dirty work, ignored/local artifacts, stale validation state, staged-snapshot drift, and publication requiring a force push.

In a dedicated task worktree, one coherent non-ignored dirty set is selected automatically. Existing branch-only commits, tracked changes, legitimate new files, deletions, and mode/type changes all form the eventual PR scope. `-Files` and `-Exclude` remain advanced exact-scope controls; any remaining out-of-scope dirty path causes a refusal. Use a separate worktree rather than asking automation to guess ownership.

## Resumable state and advanced phases

Human-readable state is stored at the Git path `.git/wholphin-prepare-pr-state.json` (or the worktree-specific equivalent). It records branch/base/HEAD, already committed PR paths and commits, confirmed candidate paths, their complete publication union, intended snapshot hash, validation results, staged snapshot/tree hashes, approved title, and completed phase. A changed branch, base, HEAD, working snapshot, or index invalidates the relevant phase.

Each invocation replaces the ignored repository-root `prepare-pr.log`. The log records timestamps, phases/results, branch/base/HEAD, confirmed scope, validation choice/result, snapshot and tree identities, staging/commit/publication outcomes, refusals/errors, actionable Git stderr, and a PR URL when one is known. The script does not log credentials, tokens, environment dumps, or PR-body contents, and always reports the log path at completion or failure.

Advanced diagnostic commands remain available after an intentional stop:

``` powershell
.\scripts\prepare-pr.ps1 -Phase Audit
.\scripts\prepare-pr.ps1 -Phase Validate -TestFilter '*RelevantTest*'
.\scripts\prepare-pr.ps1 -Phase Stage
.\scripts\prepare-pr.ps1 -Phase Commit -Title 'chore: describe the reviewed change'
.\scripts\prepare-pr.ps1 -Phase Publish
```

The advanced phase/state interface does not define normal usage and is not a custom rollback engine. Recovery must use safe Git-native inspection and corrective operations without resetting, restoring, cleaning, or stashing unrelated work.

## Validation and autofixes

Validation selection is deterministic: meaningful explicit filters run Standard; no filters run Full; upstream-sync branches require meaningful Standard followed by Full. Validation runs before real staging and is bound to a read-only, Git-filter-aware identity of each intended working entry, including mode, object type, object ID, and deletion state.

Standard and Full invoke repository-wide pre-commit, whose hooks may apply autofixes. If validation changes any file, prepare-pr stops without staging, reports the dirty paths, and requires review followed by a new Audit/Validate pass. Formatter changes are never silently included.

## Publishing and GitHub CLI

The first push uses `git push -u origin <branch>`; subsequent pushes use ordinary fast-forward `git push`. Remote divergence is refused and force push is never offered.

Authenticated `gh` is required. The script checks `gh auth status` before pushing, reuses an existing open PR, or creates one with a factual generated title/body. Missing or unauthenticated `gh` stops before push with setup guidance; after setup, resume the already verified local commit with `.\scripts\prepare-pr.ps1 -Phase Publish`. There is no parallel PowerShell GitHub API or manual compare-URL fallback.

After publication, required CI remains pending and merge remains manual. Prepare-pr does not wait, poll, merge, bypass checks, rewrite a failed PR, or delete branches/worktrees.

## After merge

From a clean working tree, update the local integration branch safely:

``` powershell
git switch main
git pull --ff-only origin main
```

Local/remote branch and worktree deletion remains manual and outside prepare-pr v1.

## Portability

Other downstream repositories should reuse this UX and safety contract, not Wholphin's implementation details. Seerr must supply its own pnpm validation, integration baseline, high-risk paths, workflow guards, artifacts, and release policy before adapting the flow.

## Current boundary

Prepare-pr owns repository/worktree safety, complete-scope audit, repository-specific validation, exact staging, actionable Git diagnostics, Git index/tree identity, safe ordinary push, and PR handoff through `gh`. Required checks, durable PR status, review, merge, notifications, and post-publication recovery belong to GitHub.

Future upstream detection, security/review automation, development artifacts, release ownership, and specialized agents remain separate roadmap work and are not implied by prepare-pr.
