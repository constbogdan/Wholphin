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
- `chore/sync-upstream-<full-upstream-SHA>-<full-downstream-SHA>`: deterministic hosted candidate for one exact input pair; see the hosted v2 section.

Normal development follows:

```text
main
  -> feature/fix/chore branch
  -> implementation
  -> focused validation during development
  -> user explicitly authorizes publication
  -> autonomous prepare-pr audit and classifier-selected validation
  -> exact stage / commit / push / PR via gh
  -> required GitHub risk-tiered PR validation
  -> user reviews completed PR and decides merge / reject
  -> update local main
```

Use the validation policy in [AGENTS.md](AGENTS.md#validation-workflow). Ordinary work uses classifier-selected Fast/Standard evidence, while unknown and sensitive scope escalates to Full. Manual upstream synchronization remains the explicit Standard-with-meaningful-filters then Full exception.

## Manual upstream synchronization

This section describes the existing workstation recovery/manual path. The separate
[hosted path](#hosted-upstream-synchronization-v2) prepares a candidate without
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
- The manual sync Standard pass uses changed-scope pre-commit and meaningful focused tests; the following Full pass uses repository-wide pre-commit and the complete default-debug graph. Both stop if a hook fails or applies an autofix.
- The resulting `chore/sync-upstream-*` pull request receives the same required fork-owned `CI / Full validation` job, with unknown/sensitive integration scope conservatively selecting its Full path.
- A merge or push to `main` runs that deterministic CI validation again against the integrated commit.
- If either fails, keep the work on the sync branch and investigate; do not advance the pull request.

CI requires no Jellyfin, Seerr, Servarr, download-client, extension-repository, or signing credentials. It does not replace deliberate conflict resolution, high-risk auto-merge inspection, or Android TV visual/focus/runtime validation.

## Reference sync: September 2026

The first completed lifecycle synchronized six upstream commits through `chore/sync-upstream-2026-09-07`, followed by a pull request into our `main` and a local-main fast-forward.

Conflicts occurred in `RequestSeasons.kt`, `SeriesViewModel.kt`, and `strings.xml`. Resolution incorporated upstream localized season formatting, the `MediaReportService` to `ServerReportService` refactor, and localized season/episode resources while preserving enhanced request-season behavior, `MediaProductStateCoordinator`, acquisition/integrity projection, exact season identity, Home Acquiring, and enhanced resources. High-risk auto-merged Series and Home files were reviewed. Standard and Full validation passed before the sync pull request was merged.

This is historical evidence for the process, not a prediction of future conflict files.

## Hosted upstream synchronization v2

Hosted observation loads a versioned policy from trusted downstream `main`:

- **FOLLOW**: normal integration candidate, still subject to automation/security review.
- **REVIEW**: Draft candidate requiring semantic review even when Git merges cleanly.
- **DOWNSTREAM-OWNED**: preserve Mosaic's bytes or approved absence while retaining upstream
  status/blob evidence. It never means invisible or a global `ours` strategy.

Unknown `.github/**` paths and ownership-crossing renames are REVIEW. `no_delta` and
DOWNSTREAM-OWNED-only observations retain complete machine evidence without opening an
attention Issue. A clean FOLLOW candidate creates a historical journal Issue, links the normal
PR and closes the Issue after handoff. REVIEW or textual conflict creates/reuses a Draft PR and
keeps one linked prioritized Issue open until semantic/manual work is resolved.

An unresolved episode is identified by trusted policy version plus the paths requiring
attention, their ownership/status and downstream blob identities, and their textual-conflict
signature. The identity deliberately excludes Issue title and the whole downstream HEAD, so
unrelated downstream movement does not create another Issue or Draft PR. The exact upstream
SHA and run remain observation evidence: additional upstream movement in the same unresolved
area updates the existing episode's evidence and priority without force-updating its Draft
branch. A changed attention signature, policy decision, relevant downstream blob, or deliberate
human disposition is materially different. Closed/rejected PRs are never reopened or recreated
automatically.

Conflict workspaces never contain unresolved indexes or conflict markers. Their deterministic
single-parent commit starts at downstream, carries safe non-conflicting changes, preserves
downstream conflict bytes, and records exact context in `.upstream-sync/blocked-context.json`.
It deliberately does not claim upstream ancestry; retries authenticate its sole parent and
context identities before reuse. Local `resolve-upstream` then authenticates the exact Draft,
recorded downstream baseline and current upstream ancestry before starting a real merge with the
recorded upstream SHA. Human/Codex resolves that active merge. The reviewed result must be a
two-parent commit whose first parent is the remote blocked Draft head and whose second parent is
the recorded upstream tip; the blocked Draft head is itself bound to the exact downstream baseline.
This parent shape lets publication fast-forward the same Draft without rewriting it. The committed
tree must equal the reviewed index and contain neither blocked context nor conflict markers.
Ready-for-review, CI, and merge/reject remain explicit human steps.

The schedule `0 6,15,21 * * *` is UTC: approximately 08:00/17:00/23:00 Bucharest in winter
and 09:00/18:00/00:00 in summer. GitHub cron does not follow DST and may start late; evidence
separates configured cron from actual observation time. The automation uses only existing
`risk: low|medium|high|critical`, `debt: low|medium|high|critical`, and conditional `attention`
labels. Missing labels are reported for one-time external creation; the App never creates them
or gains broader permissions. Complete observations retain excluded paths for future Repo
Intelligence without modifying that system.

**CURRENT CHECKPOINT:** I06 is implemented and offline validated; natural hosted acceptance
of each outcome remains pending.

```yaml
Detection: OPERATIONAL
Ownership-aware observation/journaling: IMPLEMENTED + OFFLINE TESTED
Normal/Draft candidate publication: NATIVE MERGE MODEL + OFFLINE TESTED
Natural hosted acceptance: PENDING BY OUTCOME
```

Historical v1 evidence, including no-delta run 34281315948 and conflict run 34346400694,
remains in `CODEX_HANDOFF.md`. It is not acceptance of I06 Draft conflict publication or
the three-observation schedule. One concurrency group still serializes runs and never
cancels an active publication.

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
- Classify the full merge-base-to-upstream path delta before integration. FOLLOW paths
  enter a normal candidate; REVIEW paths enter a Draft even without textual conflicts;
  DOWNSTREAM-OWNED paths retain the exact downstream bytes or absence while their
  upstream status/blob evidence remains recorded. If every path is owned, emit
  `observed_excluded` without a branch, PR, Issue or fabricated upstream ancestry.
- Prepare an isolated normal Git merge without choosing ours/theirs. A clean candidate
  has exact downstream/upstream parents; REVIEW makes it Draft. Fixed parent-derived
  timestamps and metadata make retries of the same SHA pair deterministic.
- A textual conflict becomes a deterministic single-parent Draft workspace. It retains
  the clean integration context, restores downstream bytes for unresolved paths and adds
  `.upstream-sync/blocked-context.json`; it never contains markers or claims upstream
  ancestry. `resolve-upstream` authenticates that transport workspace and starts the exact native
  merge locally. Human/Codex resolution must deliberately produce the reviewed merge tree;
  `prepare-pr` validates and preserves that existing merge commit and can only fast-forward the
  same Draft PR.
- Reuse an exact open PR only when its head equals the deterministic candidate.
  An open Draft carrying the same episode marker is also reused when unrelated downstream
  movement changes the exact-pair branch or continued upstream movement refreshes evidence.
  Its branch is not rewritten. Preserve human changes to existing branches or PRs; never force push.
- If any other sync PR is open (including a manual dated one), leave it unchanged
  and record a blocked attempt. Finish its review/merge or deliberately close it
  before proposing a different unresolved episode. Automation does not stack, rebase,
  overwrite or auto-close PRs.
- A closed PR for the exact pair is a human decision: do not reopen or recreate it
  automatically. A later distinct pair can be considered after older open PRs close.
  Intentional rejection of individual changes across all future upstream states is
  is not automated; reviewers must revisit prior rationale.
- A retry after successful push but failed PR creation reuses the exact remote
  branch. Different branch content fails closed. Recheck PR decisions before push.

The Issue records first/latest observation, count, latest run, current priority and its Draft
PR handoff. Downstream Issue and PR conversations are intentionally quiet: upstream PR numbers
are plain `PR N` text, commit identities are non-autolinking short code, attention paths are
filenames, upstream-controlled subjects/titles are sanitized, and no live upstream URL or
qualified reference is emitted. Their downstream Draft/Issue/run links remain clickable. The
Actions run summary owns rich operator navigation to upstream PRs, commits and exact upstream/
Mosaic file versions. The versioned JSON artifact owns complete exact URL/SHA/ref/object
provenance, including every changed path and ownership decision. This separation preserves
provenance and operator navigation without making routine Mosaic activity visible in upstream
Issue/PR timelines.

The generated candidate commit messages and branch names contain only fixed prose and SHA
identities. Normal FOLLOW candidates necessarily retain the original upstream commits and their
unaltered messages as ancestry. Whether GitHub re-emits cross-references when an already-known
upstream commit object becomes reachable in a fork is a separately tracked platform question;
I06 does not rewrite ancestry or upstream commit messages to suppress hypothetical activity.

### Risk, integration debt, age and escalation

These dimensions are deterministic and intentionally separate:

- **Risk** measures consequence. Any attention path starts Medium. Signing/keystore/credential
  paths are Critical; workflow, Gradle, protobuf/schema/database paths are High. Five or more
  attention paths or five or more commits touching the attention area raise Risk one level.
  Age never changes Risk.
- **Integration debt** measures catch-up cost. Its points are one baseline point, plus each
  additional attention path, each additional commit touching those paths, one point per ten
  otherwise-clean paths, two points at 3 days, three more at 7 days and three more at 21 days.
  `0–2 = Low`, `3–4 = Medium`, `5–7 = High`, and `8+ = Critical`.
- **Age** is elapsed time from the episode's first observation to latest observation, shown in
  hours below one day and whole days afterward. It has no label.
- **Escalation** becomes `Attention` for Critical Risk, High/Critical Debt, High Risk aged at
  least 3 days, or Medium-or-higher Risk aged at least 7 days. Otherwise it is `None`.

The Issue title is only the current priority view, for example
`Medium risk · Low debt · 6h` or `High risk · High debt · 7d · Attention`; it is never a
deduplication key. Existing dimension labels are replaced as values evolve, unrelated human
labels are preserved, and `attention` is present only while the escalation threshold is met.

### CI handoff and human semantic review

The detector does not run `validate-local.ps1` or duplicate Gradle validation.
The App-authored normal/Draft PR path targets `main` and triggers existing
`CI / Full validation`; I06 live handoff awaits a genuine upstream delta.
CI retains repository-wide pre-commit and the full compile/test/assembly graph,
and now includes offline hosted-helper safety tests. No required-check name or
repository rule is changed. An open candidate is not a validated integration.

Human review must inspect high-risk auto-merges even without textual conflicts:
Series/Home/Downloads, navigation, Discover requests, preferences/protobuf, shared
resources, acquisition/integrity and Enhanced Wholphin OFF behavior. Passing CI
does not authorize merge or substitute for this review or necessary device checks.
Textual conflicts remain blocked but now have a safe Draft workspace. Normal CI may
validate human/Codex resolution on that branch; changing Draft readiness and merge/reject
remain deliberate human actions. Ordinary Codex publication still follows `PREPARE_PR.md`.

### Resolving an attention candidate locally

Use the repository helper as the standard local entry point. With no argument it discovers open
I06 candidates and always presents a selector; direct use may supply the only operator identity:

``` powershell
.\scripts\resolve-upstream.ps1
.\scripts\resolve-upstream.ps1 -Pr 33
```

The helper verifies the repository, clean worktree (including untracked files), Git, authenticated
GitHub CLI, open I06 PR marker, linked journal, exact GitHub-provided head branch and current head
SHA before switching branches. It fetches that exact remote branch and either creates a tracking
branch or reuses an existing exact, non-divergent tracking branch. It never guesses a branch,
stashes, resets, cleans, force-checks out, force-pulls, pushes or mutates GitHub. Any identity,
evidence or local-branch uncertainty is a refusal.

Trusted machine evidence comes from the latest retained I06 outcome/observation artifact when
available and is bound to episode, repository, branch, run/attempt and candidate SHA. The durable
PR marker and linked journal provide the safe fallback when a retained artifact has expired.
Current PR checks provide concise CI status and the downstream run URL; brittle full-log scraping
is intentionally omitted. The helper prints an operator summary and creates the ignored local
prompt `.logs/upstream-resolution/pr-<N>/codex-prompt.md` with actual episode, priority, incoming
commit, attention-path, provenance and CI evidence.

The terminal does not duplicate that generated prompt. It prints only a concise instruction to
read `.logs/upstream-resolution/pr-<N>/codex-prompt.md` and carry it out exactly. The prompt requires
the final semantic-resolution report to provide the narrowest meaningful JVM test filters for the
later prepare-pr invocation, based on behavior actually changed or preserved. If no suitable test
exists, Codex must name the test that needs to be added. The resolver does not guess those semantic
filters before resolution, and prepare-pr enforcement is unchanged.

The local resolver does not impose additional global serialization when multiple durable candidates
already exist. Exact attention-path overlap, shared semantic production/ownership paths, upstream
ancestry and downstream observation baselines form a deterministic dependency graph. A proven predecessor is `Ready for resolution`; a dependent is
`Waiting on PR #N`; unrelated candidates are `Independent`. Closed/satisfied candidates are
`Superseded`. Incomparable ancestry or evidence observed against an older current-main baseline is
`Dependency ambiguous` and cannot be selected. The next hosted observation must recompute stale
scope/priority against authoritative main; the local helper never rebases or overwrites a Draft.
The current hosted I06 publisher still retains its earlier one-open-sync-PR guard, so normal hosted
operation does not yet create concurrent independent candidates. Changing that hosted creation
policy is a separate explicit follow-up, not part of this local operator helper.

The helper is re-entrant rather than long-running. First use selects, checks out, writes the prompt
and exits. After semantic edits, run the same task again on the candidate branch. It refreshes the
PR, journal, artifact, remote head, main and dependency graph; requires a normal descendant with a
non-empty resolution diff; rejects unrelated or unmapped scope; and derives focused JVM filters
from I03 mappings plus changed test classes. Filters must match source-controlled tests. The exact
scope and filters are displayed before `Ready to PUSH? [y/N]`; only explicit `y` delegates to
prepare-pr. Blank, EOF, cancellation or any drift performs no commit or push.

After that explicit authorization, `prepare-pr.ps1` updates the same existing candidate PR: its
upstream-sync branch pattern requires meaningful focused JVM filters followed by Full, its remote
check permits only a normal fast-forward push, and its PR lookup reuses the open PR by exact head
branch. It does not mark the Draft Ready. This remains conditional on the candidate descending
from current `origin/main`; if unrelated main movement makes that unprovable, prepare-pr refuses
and the operator must reconcile the candidate deliberately rather than bypassing the guard.

When that exact linked candidate is later merged, the canonical closed-PR event runs a terminal
journal finalizer. It authenticates the PR's I06 episode marker, deterministic SHA-pair branch,
same-repository head/base and merge identity, resolves exactly one Issue with the same marker,
records a deterministic merged terminal marker, removes only managed attention/risk/debt labels,
preserves unrelated labels and closes the Issue as completed. Exact reruns are no-ops. Missing,
ambiguous, altered or already-closed-without-matching-terminal evidence fails closed. This job can
write Issues but cannot write repository contents and does not mint an App token.

This lifecycle closure does not change ancestry policy. A conflict workspace and its ordinary
semantic-resolution commits may integrate upstream behavior without making the original upstream
commits ancestors, so GitHub can truthfully continue to show the fork behind. Preserving ancestry
would require a separately approved, tree-preserving two-parent merge commit after resolution and
validation, bound to the exact upstream range and reviewed resolved tree. Cherry-picking creates
new object identities and does not solve the behind count; rebasing or grafts rewrite or localize
history; and an unaudited `ours` merge can cause future sync detection to skip changes that were
never integrated. Until that design is implemented, do not fabricate ancestry.

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
only to the token action and only when ready, REVIEW or semantic-conflict state
requires a branch/PR mutation. Excluded and no-delta paths never mint it. Default
job-completion token revocation remains enabled. No PAT fallback or additional
App permissions are introduced.

The v1 workflow's first authorized manual detection smoke test succeeded as recorded
historically. I06's revised schedule, ownership outcomes, journals and Draft paths await
natural hosted execution. App setup and hosted operation grant no ordinary agent
publication or merge authority.

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
journal records. Only branch push and PR creation receive the scoped App token.
Neither checkout persists credentials; candidate Git operations receive no token.
Only the explicit push subprocess receives the publication credential. No build
or untrusted upstream code runs in a write-credential context.

### Operational records and failure recovery

There is no custom database, state branch or service. Last observed state is in run
summaries and versioned JSON; every non-empty exact upstream/downstream/policy state also
uses a `[upstream-sync]` journal Issue. Exact retries reuse the same Issue. A materially
new state supersedes and closes an older open journal rather than rewriting its meaning.
All-excluded observation and successful normal/Draft handoff close the journal; closure
means responsibility moved to the PR lifecycle, not that upstream was accepted. A
semantic-conflict Draft remains open with status `Blocked — semantic integration required`.

Expected blocked semantic state returns a structured outcome rather than impersonating a
crashed tool. Trust/provenance uncertainty and permission, rate-limit, not-found, transient
network or other required-operation failures still fail the job with their category and
durable evidence where identity permits. An Issue failure is visible but does not discard
an otherwise authenticated candidate PR. Labels remain optional and unimplemented because
no label/admin permission was added.

Ref and PR checks are repeated immediately before publication, but Git/GitHub do
not provide an atomic transaction across upstream, downstream, branch and PR state.
Later base changes remain visible on the PR and require current required CI/review.
Keep existing branch changes for human inspection; use corrective work, not force.
After an intentional upstream rewrite, reconcile/review the new lineage and its
retained observation anchors explicitly; there is no automated override/reset switch.

### FUTURE RI ENRICHMENT

Repo Intelligence is absent from the control path. Each job writes versioned JSON
and a workflow summary with repo/ref/SHA identities, comparison baseline, changed
paths, ownership/exclusion decisions, incoming commits/count, configured schedule and
observation time, workflow/run/attempt, candidate, outcome, conflict information and
PR/journal URLs where applicable. A later
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
