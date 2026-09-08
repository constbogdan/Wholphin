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
- `chore/sync-upstream-<full-upstream-SHA>-<full-downstream-SHA>`: deterministic hosted candidate for one exact input pair; see the hosted v1 section.

Normal development follows:

```text
main
  -> feature/fix/chore branch
  -> implementation
  -> focused validation during development
  -> user explicitly authorizes publication
  -> autonomous prepare-pr audit and validation (Standard with meaningful filters, Full otherwise)
  -> exact stage / commit / push / PR via gh
  -> required GitHub Full validation
  -> user reviews completed PR and decides merge / reject
  -> update local main
```

Use the validation policy in [AGENTS.md](AGENTS.md#validation-workflow). Ordinary iteration can use focused checks; current prepare-pr publication uses Full when no meaningful focused JVM filter exists. A trivial-change exemption remains future work.

## Manual upstream synchronization

This section describes the existing workstation recovery/manual path. The separate
[hosted path](#hosted-upstream-synchronization-v1) prepares a candidate without
workstation validation and relies on required PR CI before human merge/reject.

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
  -> user explicitly authorizes publication
  -> prepare-pr validates and publishes the sync PR through gh
  -> required GitHub Full validation
  -> user reviews and decides merge / reject
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
  -> user explicitly authorizes publication
  -> prepare-pr with meaningful -TestFilter (Standard then Full)
  -> required CI and human PR review / merge decision
```

Do not create or merge the sync pull request if validation fails. Diagnose and correct the integration on the sync branch.

An in-progress merge must first be resolved, staged, validated, and completed with its local merge commit; prepare-pr refuses active Git operations even when all conflict markers are gone. That local integration step does not authorize push or PR creation. After the merge is complete, semantic review is finished, and the user explicitly authorizes publication, `scripts/prepare-pr.ps1` performs the mechanical publication preparation. It recognizes `chore/sync-upstream-*` and requires Standard followed by Full local validation before staging, commit, or publication. This support does not resolve conflicts, select `ours`/`theirs`, replace high-risk auto-merge review, or weaken any step above.

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

The Standard/Full workstation sequence below applies to manual synchronization
and local conflict recovery. Hosted conflict-free candidates instead receive
lightweight structural checks followed by the existing required PR Full CI. Neither
path removes semantic review or required runtime/device validation before merge.

Use `.\scripts\validate-local.ps1` and follow the handoff conventions in `docs/AGENTS.md`.

- Run Standard validation after conflict resolution and semantic auto-merge review.
- Run Full validation before creating or merging the upstream-sync pull request.
- Standard and Full both begin with repository-wide `pre-commit run --all-files` and stop before Gradle if a hook fails or applies an autofix. Inspect any resulting diff before rerunning.
- The resulting `chore/sync-upstream-*` pull request receives the same fork-owned `CI / Full validation` check as every other pull request to `main`.
- A merge or push to `main` runs that deterministic CI validation again against the integrated commit.
- If either fails, keep the work on the sync branch and investigate; do not advance the pull request.

CI requires no Jellyfin, Seerr, Servarr, download-client, extension-repository, or signing credentials. It does not replace deliberate conflict resolution, high-risk auto-merge inspection, or Android TV visual/focus/runtime validation.

## Reference sync: September 2026

The first completed lifecycle synchronized six upstream commits through `chore/sync-upstream-2026-09-07`, followed by a pull request into our `main` and a local-main fast-forward.

Conflicts occurred in `RequestSeasons.kt`, `SeriesViewModel.kt`, and `strings.xml`. Resolution incorporated upstream localized season formatting, the `MediaReportService` to `ServerReportService` refactor, and localized season/episode resources while preserving enhanced request-season behavior, `MediaProductStateCoordinator`, acquisition/integrity projection, exact season identity, Home Acquiring, and enhanced resources. High-risk auto-merged Series and Home files were reviewed. Standard and Full validation passed before the sync pull request was merged.

This is historical evidence for the process, not a prediction of future conflict files.

## Hosted upstream synchronization v1

**CURRENT CHECKPOINT (2026-09-09):** `.github/workflows/upstream-sync.yml` is
merged on `main`; `scripts/hosted_upstream.py` implements the candidate path.

```yaml
Detection: OPERATIONAL
Hosted sync candidate/PR publication: IMPLEMENTED + OFFLINE TESTED
Live publication path: AWAITING FIRST REAL UPSTREAM DELTA
```

The user reports the first manual hosted smoke test succeeded:
[run 34281315948](https://github.com/constbogdan/Wholphin/actions/runs/34281315948).
Upstream was `1778bdb34caa699c0590232a7de709a889839765`; downstream was
`7385b3ecb59908676ab38611527f45f72268fe9a`. Ancestry validation succeeded,
`outcome: no_delta`, incoming commits: `0`. No branch or PR was needed, so live
App-token branch/PR publication and candidate PR CI handoff remain unverified.

The workflow runs only in `constbogdan/Wholphin` on `main`, manually through
`workflow_dispatch` or daily at **06:23 UTC**. Schedules are best-effort: every run
fetches current refs and catches up; there is no timestamp watermark to advance.
One concurrency group serializes runs without canceling an active publication.

The read job and publication job each use a fresh process-owned temporary Git
repository. Trusted helper code comes from the workflow's downstream main SHA,
outside the integration checkout. Both canonical fetch and push identities are
validated exactly before publication:

```text
origin   https://github.com/constbogdan/Wholphin.git
upstream https://github.com/damontecres/Wholphin.git
```

Only official `refs/heads/main` is fetched from upstream. Full ancestry is retained;
no application scripts, local Actions, hooks, filters, build tools or upstream code
are executed in the candidate checkout. System/global Git configuration is disabled.
The publisher repeats observation and requires the read job's exact upstream and
downstream SHA pair, then checks remote main tips immediately before publication.
Ref drift stops the run for a fresh observation; main is never pushed or modified.

### Detection, integration and deduplication

- The reviewed initial ancestry anchor is
  `1778bdb34caa699c0590232a7de709a889839765`, already contained in downstream main
  at implementation. Downstream must retain it. Upstream must descend from that
  anchor and every retained hosted PR/validated blocked-observation anchor.
- Hosted branch refs retain attempts interrupted between push and PR creation;
  hosted PR head refs retain attempted ancestry even after branch deletion.
  Blocked issues record validated observations. A missing object, rewrite or rollback
  that breaks these proofs stops for human judgment. A rejected rewrite is not
  promoted into a new trusted observation anchor.
- If upstream HEAD is already an ancestor of downstream main, succeed with
  `no_delta`: no branch, PR, issue or comment. The run summary/JSON still records it.
- Otherwise require a single merge base and enumerate `downstream..upstream`.
  Changed paths describe merge-base-to-upstream; incoming commits exclude commits
  already reachable downstream. The comparison baseline is not a custom sync ledger.
- Branch identity is `chore/sync-upstream-<full-upstream-SHA>-<full-downstream-SHA>`.
  The dated branch convention remains for the manual helper only.
- Prepare an ordinary two-parent merge: normal Git merge with `--no-ff --no-commit`,
  without ours/theirs or semantic resolution. On success, check the index for
  conflicts/whitespace and produce the merge commit from that tree with exact
  downstream/upstream parents. Fixed parent-derived timestamps and commit metadata
  make retries of the same pair deterministic with the same Git implementation.
- If integration changes `.github/` or the hosted helper itself, stop for explicit
  manual automation review. Existing CI and publisher guards must not be silently
  replaced by upstream content. This also avoids granting App workflow-write access.
- Reuse an exact open PR only when its head equals the deterministic candidate.
  Preserve human changes to existing branches or PRs; never force push.
- If any other sync PR is open (including a manual dated one), leave it unchanged
  and record a blocked attempt. Finish its review/merge or deliberately close it
  before proposing a newer pair. V1 does not stack, rebase, overwrite or auto-close PRs.
- A closed PR for the exact pair is a human decision: do not reopen or recreate it
  automatically. A later distinct pair can be considered after older open PRs close.
  Intentional rejection of individual changes across all future upstream states is
  outside v1; reviewers must revisit prior rationale.
- A retry after successful push but failed PR creation reuses the exact remote
  branch. Different branch content fails closed. Recheck PR decisions before push.

The PR records upstream base/head, downstream baseline, candidate SHA, incoming
commit count/list, changed paths, textual-conflict status, run identity and pending
Full CI. Large deltas that cannot fit complete PR metadata stop for manual handling;
blocked issues retain identities and bounded lists with explicit counts.

### CI handoff and human semantic review

The detector does not run `validate-local.ps1` or duplicate Gradle validation.
The implemented App-authored PR path targets `main` and is designed to trigger
existing `CI / Full validation`; that live handoff awaits a genuine upstream delta.
CI retains repository-wide pre-commit and the full compile/test/assembly graph,
and now includes offline hosted-helper safety tests. No required-check name or
repository rule is changed. An open candidate is not a validated integration.

Human review must inspect high-risk auto-merges even without textual conflicts:
Series/Home/Downloads, navigation, Discover requests, preferences/protobuf, shared
resources, acquisition/integrity and Enhanced Wholphin OFF behavior. Passing CI
does not authorize merge or substitute for this review or necessary device checks.
Textual conflicts produce no candidate PR; resolve deliberately through the manual
path above. Ordinary Codex publication still follows `PREPARE_PR.md`.

### Least privilege and activation prerequisites

A read-only settings query on 2026-09-08 returned
`default_workflow_permissions: read` and
`can_approve_pull_request_reviews: false`. Repository secrets were empty.
Under the current setting, `GITHUB_TOKEN` cannot create PRs. Even when permitted,
GitHub documents approval-required PR workflow runs for token-created PRs, while
App installation tokens allow the normal unattended trigger path:
[GITHUB_TOKEN behavior](https://docs.github.com/en/actions/concepts/security/github_token).

The user confirmed external setup complete on 2026-09-09: **Wholphin Sync Bot**
is installed only on `constbogdan/Wholphin`, with Contents read/write, Pull requests
read/write and Metadata read. Repository variable `SYNC_BOT_CLIENT_ID` and secret
`SYNC_BOT_PRIVATE_KEY` are configured. The earlier empty-secret result is historical.
No credentials or settings were changed by this implementation task.

The pinned official `actions/create-github-app-token` v3 action uses `client-id`
and `private-key`, explicitly restricts `owner`/`repositories` to
`constbogdan/Wholphin`, and requests only Contents/PR write. The key is supplied
only to the token action, only for a ready candidate in the publish job. Default
job-completion token revocation remains enabled. No PAT fallback or additional
App permissions are introduced. Missing/invalid credentials fail closed through
the separate repository-token blocked-issue path.

The workflow is published on `main` and its first authorized manual detection
smoke test succeeded as recorded above. The daily schedule is eligible to run;
this checkpoint does not claim a separately observed scheduled run. App setup and
hosted operation grant no ordinary agent publication or merge authority.

For a separately authorized follow-up dispatch when a genuine upstream delta exists:

``` powershell
gh workflow run upstream-sync.yml --repo constbogdan/Wholphin --ref main
```

Inspect exact candidate branch/PR identities and required PR Full CI; an authorized
repeat can verify reuse without another branch/PR. A no-delta run skips token
creation and cannot establish App/PR-path operation. Do not fabricate a delta to
force publication. Dispatching another branch skips jobs because execution is
intentionally guarded to `main`. No follow-up run was executed for this docs update.

The read job's repository token has Contents/PR/Issues read. The publish job's
repository token has Contents/PR read and **Issues write**, solely for durable
blocked records. Only branch push and PR creation receive the scoped App token.
Neither checkout persists credentials; candidate Git operations receive no token.
Only the explicit push subprocess receives the publication credential. No build
or untrusted upstream code runs in a write-credential context.

### Operational records and failure recovery

There is no custom database, state branch or service. Last observed state is in
run summaries and observation JSON; actionable validated observations also appear
in PRs/blocked issues. Last attempted state is represented by the SHA-pair branch,
PR or blocked issue. Last accepted state is actual main ancestry and merged PR/Git
metadata, never an observation flag. Retain PRs and blocked issues as audit evidence.
No-delta observations have only run retention; v1 cannot detect a transient rewrite
that occurred and disappeared entirely between observations.

Conflicts, rewrites, automation changes, stale refs, existing different work, failed
push and failed PR creation leave a failed publication job and actionable summary.
The helper creates a `[upstream-sync blocked]` issue keyed by exact SHA pair and
reason, reusing it on identical retries even if it was closed. It never automatically
closes issues. New pairs/reasons can create new records; old records remain evidence.

The issue retains exact identities, the reason, run link and conflict/path evidence;
the full JSON artifact is supplemental (14-day retention), never the sole intended
record of an actionable block. Identity rejection forbids issue publication too.
If GitHub/API/issue permissions are unavailable, a durable issue cannot be guaranteed:
the run stays failed, reports the recording failure and requires a human to preserve
the identities/diagnostics in GitHub before retrying. Do not count that as success.
Workflow cancellation/runner loss may similarly need manual run investigation.

Ref and PR checks are repeated immediately before publication, but Git/GitHub do
not provide an atomic transaction across upstream, downstream, branch and PR state.
Later base changes remain visible on the PR and require current required CI/review.
Keep existing branch changes for human inspection; use corrective work, not force.
After an intentional upstream rewrite, reconcile/review the new lineage and its
retained observation anchors explicitly; v1 has no automated override/reset switch.

### FUTURE RI ENRICHMENT

Repo Intelligence is absent from the control path. Each job writes versioned JSON
and a workflow summary with repo/ref/SHA identities, comparison baseline, changed
paths, incoming commits/count, observation time, workflow/run/attempt, candidate,
outcome, conflict information and PR/blocked-issue URLs where applicable. A later
read-only consumer may ingest these records asynchronously. No callback, dispatch,
RI credential, external database or synchronous analysis dependency exists.

### Implementation validation

Run the offline helper suite without GitHub interactions:

```powershell
python -B -m unittest discover -s scripts -p test_hosted_upstream.py -v
```

Tests create disposable Git repositories and mock GitHub. Their fixture-only force
push simulates an upstream rewrite; production publication never force pushes.
Validate workflow YAML/actionlint, Python syntax, repository-wide pre-commit and
`git diff --check`. Newly untracked implementation files also need explicit
pre-commit file checks because `--all-files` follows Git's tracked inventory.
Do not run the hosted helper against a developer checkout or create a real sync PR
as an implementation test. Live branch/PR publication and its CI handoff await the first genuine upstream delta.

## Onboarding another maintained downstream repository

Wholphin defines the workflow and safety guarantees, not a universal build implementation. Use this checklist when adapting the model to Seerr or another independently maintained service:

- [ ] Identify and verify `origin` and `upstream`.
- [ ] Establish and protect the downstream integration branch (one appropriate protected branch, not necessarily `main`).
- [ ] Establish feature/fix/chore branch and PR-only integration policy.
- [ ] Inspect every inherited workflow and its permissions, triggers, secrets, writes, publishing, and artifacts.
- [ ] Define repository-specific Fast, Standard, and Full validation equivalents where appropriate.
- [ ] Establish local/required-CI validation parity.
- [ ] Add required, read-only PR CI.
- [ ] Guard or disable inherited release and publishing automation until downstream ownership is explicit.
- [ ] Add a safe upstream-sync helper that stops for semantic conflict resolution.
- [ ] Document high-risk merge surfaces and semantic conflict policy.
- [ ] Establish repository-local agent, handoff, roadmap, and upstream-policy documentation.
- [ ] Add a guarded `prepare-pr` workflow.
- [ ] Add automated upstream-change detection and sync-PR preparation without automated conflict resolution.
- [ ] Define downstream build, artifact, versioning, signing, and release ownership.

Seerr standardization remains deferred until `origin/develop` versus `upstream/develop` divergence is deliberately reconciled. Seerr likely retains `develop`, which is part of its upstream integration and development-container lifecycle; it needs pnpm/Node/Docker validation and repository-specific release handling. Wholphin itself needs no permanent staging/develop branch; see the [PR/device validation model](Wholphin_ROADMAP.md#pre-main-validation-model).

Do not copy Wholphin's Gradle tasks, Windows prerequisites, CI runner, tag-fetch behavior, or artifact assumptions blindly. Each repository must derive its build toolchain, validation commands, language/runtime requirements, formatting and lint tooling, CI runner, required secrets, artifact and release behavior, upstream tag/versioning requirements, and high-risk merge surfaces. The target is the same workflow and safety guarantees with a repository-specific implementation.
