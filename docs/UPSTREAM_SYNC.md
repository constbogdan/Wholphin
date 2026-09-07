# Repository and upstream synchronization policy

This document is the authoritative policy for branch use and synchronization of the Wholphin fork.

## Remotes and integration baseline

- `origin` is `constbogdan/Wholphin`, our maintained fork.
- `upstream` is `damontecres/Wholphin`, the original Wholphin project.
- `origin/main` is the known-good integration branch: upstream Wholphin plus our validated enhancements.

`main` must remain buildable and validated. Do not perform active development directly on it. Update local `main` from `origin/main`, then create a purpose-specific branch.

## Branch classes

- `main`: known-good integration baseline; receives changes through pull requests and is the base for new work.
- `feature/<name>`: product work, such as `feature/watchlist`, `feature/collections`, or `feature/discovery-sources`.
- `fix/<name>`: focused correctness or regression fixes.
- `chore/<name>`: repository, tooling, and maintenance work, such as `chore/ci` or `chore/repository-policy`.
- `chore/sync-upstream-YYYY-MM-DD`: dedicated upstream integration branch created from current validated `main`.

Normal development follows:

```text
main
  -> feature/fix/chore branch
  -> implementation
  -> focused validation during development
  -> Standard validation for normally completed work
  -> Full validation for a major milestone when appropriate
  -> pre-commit/diff review for substantial milestones
  -> commit and push
  -> pull request into main
  -> merge
  -> update local main
```

Use the validation level defined by `docs/AGENTS.md`; Full validation is not required for every trivial change.

## Upstream synchronization

Never merge `upstream/main` directly into our `main`. Use this sequence:

```text
update local main from origin/main
  -> fetch upstream
  -> create chore/sync-upstream-YYYY-MM-DD from main
  -> merge upstream/main
  -> resolve conflicts deliberately, if any
  -> inspect high-risk auto-merges
  -> Standard validation
  -> Full validation
  -> complete the merge commit if conflicts required manual resolution
  -> push the sync branch
  -> pull request into our main
  -> merge the pull request
  -> update local main
```

The mechanical portion can be started from clean local `main` with:

```powershell
.\scripts\sync-upstream.ps1
```

The helper verifies the working tree and remotes, fetches `origin/main` and `upstream/main`, fast-forwards a strictly-behind local `main`, creates the dated sync branch, and runs a normal `git merge --no-edit upstream/main`. It never force-resets, overwrites a branch, resolves conflicts, pushes, creates a pull request, or merges a pull request.

If Git can merge without conflicts, normal Git behavior applies: it may report already up to date, fast-forward, or create the ordinary merge commit. The helper reports the result and stops for review and validation; it does not push or open a pull request.

If conflicts occur, the helper leaves the merge in progress, lists every unmerged file, exits non-zero, and requires manual semantic resolution:

```text
inspect and resolve conflicts
  -> git add resolved files
  -> Standard validation
  -> Full validation
  -> git commit
  -> git push -u origin chore/sync-upstream-YYYY-MM-DD
  -> pull request into main
```

Do not create or merge the sync pull request if validation fails. Diagnose and correct the integration on the sync branch.

## Conflict-resolution policy

Every resolution must preserve both upstream changes that should apply to us and our validated Wholphin behavior. Never mechanically choose `ours` or `theirs` unless inspection proves that one side completely supersedes the other.

For every conflict:

1. Inspect ours, upstream, and the common-base intent where useful.
2. Inspect surrounding callers and tests.
3. Preserve upstream fixes, refactors, and features that remain applicable.
4. Preserve validated enhanced behavior and architectural boundaries.
5. Remove local logic only when upstream genuinely supersedes it.
6. Avoid unrelated refactoring while resolving the merge.

`upstream/main` is the behavioral reference for deciding what Enhanced Wholphin OFF means. OFF removes enhanced capabilities; it does not disable independent upstream behavior, bug fixes, UI improvements, navigation fixes, ordering fixes, or every line that our fork has changed.

Conflict-sensitive integration areas currently include:

- `SeriesViewModel.kt` and `SeriesDetails.kt`
- `HomePage.kt` and `HomeViewModel.kt`
- `DownloadsPage.kt` and `NavDrawer.kt`
- Discover request and series code
- preferences and protobuf schema
- shared strings and resources

An automatic merge is only a textual result. If both sides changed related behavior in these areas, inspect the merged semantics even when Git reports no conflict.

## Validation

Use `.\scripts\validate-local.ps1` and follow the handoff conventions in `docs/AGENTS.md`.

- Run Standard validation after conflict resolution and semantic auto-merge review.
- Run Full validation before creating or merging the upstream-sync pull request.
- The resulting `chore/sync-upstream-*` pull request receives the same fork-owned `CI / Full validation` check as every other pull request to `main`.
- A merge or push to `main` runs that deterministic CI validation again against the integrated commit.
- If either fails, keep the work on the sync branch and investigate; do not advance the pull request.

CI requires no Jellyfin, Seerr, Servarr, download-client, extension-repository, or signing credentials. It does not replace deliberate conflict resolution, high-risk auto-merge inspection, or Android TV visual/focus/runtime validation.

## Reference sync: September 2026

The first completed lifecycle synchronized six upstream commits through `chore/sync-upstream-2026-09-07`, followed by a pull request into our `main` and a local-main fast-forward.

Conflicts occurred in `RequestSeasons.kt`, `SeriesViewModel.kt`, and `strings.xml`. Resolution incorporated upstream localized season formatting, the `MediaReportService` to `ServerReportService` refactor, and localized season/episode resources while preserving enhanced request-season behavior, `MediaProductStateCoordinator`, acquisition/integrity projection, exact season identity, Home Acquiring, and enhanced resources. High-risk auto-merged Series and Home files were reviewed. Standard and Full validation passed before the sync pull request was merged.

This is historical evidence for the process, not a prediction of future conflict files.

## Future automation

A later scheduled GitHub Action may detect new upstream commits, create or update a dedicated sync branch, attempt a normal merge, run CI when conflict-free, open a pull request, and report conflicts. It must never resolve semantic conflicts automatically. CI and scheduled synchronization are separate future infrastructure checkpoints.

After the fork-owned CI workflow is merged, first observe a successful `CI / Full validation` check on both a pull request and merged `main`. Only then create or update the `main` ruleset to require that stable check before merge. Repository settings are not configured by the workflow, and branch protection must not be documented as active until that manual step is complete.
