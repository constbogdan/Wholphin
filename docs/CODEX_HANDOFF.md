# Codex handoff: Wholphin ecosystem

## Item 6 I06: ownership-aware hosted Upstream Sync

**IMPLEMENTED / OFFLINE VALIDATED; NATURAL HOSTED ACCEPTANCE PENDING.** Hosted Sync now loads
version 1 of `scripts/upstream_ownership_policy.json` from trusted downstream `main`. Exact
automation paths are FOLLOW, REVIEW or DOWNSTREAM-OWNED; unknown `.github/**` paths default to
REVIEW and ordinary paths to FOLLOW. Every upstream path remains in the observation with
status, old/new path and blob identities, ownership, policy version and candidate effect.
DOWNSTREAM-OWNED bytes or approved absence are preserved exactly but remain observable.
Cross-boundary renames and mixed FOLLOW automation beside owned automation escalate to review.

Machine outcomes distinguish no delta, all-excluded, ready/review/semantic candidates,
existing or created normal/Draft PRs, trust blocks and infrastructure/publication errors.
The final journal model no longer keys unresolved attention to the whole exact SHA pair.
Episode identity is policy version plus attention paths, their ownership/status and relevant
downstream blob identities, and textual-conflict signature. It excludes title and whole
downstream HEAD, so unrelated downstream commits reuse one Issue and Draft PR. Exact upstream,
downstream and run identities remain evidence; continued upstream movement in the same area
updates that episode without rewriting its Draft branch. Changed policy/attention signature or
relevant downstream bytes is a new problem; closed/rejected decisions are never reopened.

One unresolved Issue records first/latest observation, observation count and latest run URL.
Its title is the current `Risk · Debt · Age` view with optional `Attention`, never identity.
Risk starts Medium for attention, becomes High for workflow/Gradle/proto/schema/database paths,
Critical for signing/keystore/credential paths, and rises one level at five attention paths or
five same-area commits. Age never changes Risk. Debt points are baseline 1 plus extra attention
paths, extra same-area commits, one per ten clean paths, +2 at 3 days, +3 at 7 days and +3 at 21
days; Low is 0–2, Medium 3–4, High 5–7 and Critical 8+. Escalation is Attention for Critical
Risk, High/Critical Debt, High Risk at 3 days, or Medium+ Risk at 7 days.

Only existing `risk: *`, `debt: *` and conditional `attention` labels are applied. Missing
labels are reported for one-time external creation without permission expansion. No age or
redundant semantic label is created. No-delta and DOWNSTREAM-OWNED-only observations create no
Issue. Clean FOLLOW journals close after normal-PR handoff and remain history; REVIEW/conflict
journals stay open and link bidirectionally with their Draft PR. Downstream Issue/PR bodies are
now a quiet surface: upstream PR numbers, short commit identities and attention filenames are
sanitized inert text, while only downstream Draft/Issue/Actions links remain clickable. Rich
clickable upstream PR/commit/blob and corresponding Mosaic blob navigation lives in the Actions
summary. Retained observation/outcome JSON owns complete exact URL/SHA/ref/object provenance.
This three-surface boundary prevents routine downstream conversations from creating visible
upstream cross-references or mentions without concealing source identity.

Generated candidate commit messages and branch names contain fixed prose and SHA identities.
Normal FOLLOW candidates necessarily retain exact upstream commits and their original messages
as ancestry. GitHub's behavior when an already-known upstream commit with reference-like text
becomes reachable in a fork remains a separate platform question; do not rewrite ancestry or
commit messages merely to suppress hypothetical activity, and do not dispatch a hosted probe
without explicit approval.

The final Draft-vs-normal review retained Draft as a deliberate safety boundary, not merely
presentation metadata. The current protected-`main` ruleset requires a PR and `CI / Full
validation` but zero formal approvals; an open attention Issue, Risk/Debt/Age/Escalation and
passing CI communicate state without preventing merge. Draft is therefore the enforced
not-semantically-ready gate until a human resolves the candidate and deliberately marks it
ready. Draft PRs already remain visible, commentable, editable and CI-testable. Earlier
CodeRabbit or other reviewer engagement is a secondary integration benefit and must not
weaken this merge-safety invariant. Reconsider normal attention PRs only alongside an approved,
enforceable replacement merge gate.

Conflicts produce a deterministic Draft workspace, never conflict markers or an unresolved
index. Its commit has only the exact downstream parent, retains safe non-conflicting changes
and downstream conflict-path bytes, and adds `.upstream-sync/blocked-context.json`. It does not
claim upstream ancestry. Retry authentication therefore verifies that exact sole parent and
the context file's upstream/downstream/policy identities instead of incorrectly requiring the
blocked commit to contain upstream. Existing human work is never overwritten, closed PRs are not reopened,
pushes are non-force, and readiness/merge remains human-controlled.

The fixed UTC schedule is `0 6,15,21 * * *`: about 08:00/17:00/23:00 Bucharest in winter and
09:00/18:00/00:00 in summer. Evidence records configured cron separately from actual UTC
observation time. Label use is graceful and requires no new authority; App and job-token
permissions are unchanged. Repo Intelligence may later consume the complete
observation, including excluded paths, but is unchanged. Natural acceptance remains pending.
`main.yml` is now mechanically safe to remove only in a separate reviewed ownership follow-up;
I06 does not delete it. I07 is untouched.

All 53 hosted-sync tests now pass, including explicit three-observation idempotency, unrelated downstream
movement, continued same-area upstream movement, independent priority progression, label
replacement/missing-label behavior, clean/attention journal lifecycles, quiet hostile-input
Issue/PR surfaces, rich Actions navigation and retained exact artifact URLs in addition to the
established ownership, conflict, credential, drift and no-force fixtures. The complete offline
suite passes 157 tests with the one existing Windows executable-bit portability skip. I01–I05
delivery/security behavior remains intact.

## Item 6 I05: delivery presentation

**IMPLEMENTED / OFFLINE VALIDATED; PR → MAIN → DEVELOPMENT LIFECYCLE LABELS LIVE
VALIDATED; REMAINING NATURAL HOSTED ACCEPTANCE PENDING.** The
[I05 presentation ledger](ITEM_6_I05_PRESENTATION.md) records the before-edit name inventory,
consumer classifications, artifact map, implemented labels, APK migration and historical
body-only backfill plan. All workflow paths, job IDs, CI/Full validation, Development/recovery
sign API names, artifact prefixes/IDs, tags, manifest schema, installer alias and provenance
remain unchanged. Human workflow names use the Mosaic Release/Recovery/Promotion/Diagnostic
family; run names use real trigger-time source/build/artifact identity. No I06/I07 behavior,
inherited publisher deletion or external mutation is included.

The human-first run-name follow-up keeps these labels presentation-only. PR CI shows
`PR #N · <head branch>`; manual CI shows `Validate · <ref>`; protected-main push CI
returns whitespace from `run-name` so GitHub preserves its native merge/push title.
Development prefers the triggering CI `display_title`, then a labelled CI run number, then
the exact triggering SHA; manual Development uses its explicitly approved SHA. Stable shows
`Stable · from downstream-build-N`. No raw commit-message parsing, API call, new permission,
computed version claim or trust decision was added. Natural hosted acceptance must confirm
the documented whitespace fallback and Development title propagation; if the former does not
behave as documented, omit CI `run-name` entirely rather than replacing readable native titles
with plumbing or parsed merge text.

PR #30 live-validated that design end to end in the Actions list. PR CI displayed
`PR #30 · chore/item-6-lifecycle-labels`; protected-main CI retained GitHub's native
`Merge pull request #30 from constbogdan/chore/item-6-lifecycle-labels`; and the triggered
Development run displayed `Development · Merge pull request #30 from
constbogdan/chore/item-6-lifecycle-labels`. This confirms both the whitespace/native-title
fallback and `workflow_run.display_title` propagation. `CI` and `Full validation` remain
unchanged machine contracts. The inherited upstream `Development build` also remained visible
as a separate one-second skipped row; its downstream ownership/removal decision is deliberately
deferred to I06. Stable, recovery and signing-diagnostic run labels still await natural live
execution, and SHA remains only the truthful fallback when no better display identity exists.

Two negative findings determine the compatibility boundary. UpdateChecker reads the API
release `name` and Version matches the whole numeric string: branded API titles would break
installed clients, so `v1.0.N` stays and branded channel headings go into future release bodies.
Recovery also authenticates job display names from the jobs API, so adding YAML `name:` to
production `sign` would break old artifact consumers even with the internal ID unchanged.
Legacy signing-exercise artifact prefixes remain accepted but are not generated by current
production delivery. Existing published bodies are not rewritten on retries.

Outcome-first summaries distinguish publication, promotion, recovery checkpoint/original
build versus execution identity, non-APK skips, guard-rejected Development triggers and
failed stages. The guard explanation has no checkout/API/mutation authority and only runs
for triggers already rejected by the unchanged guard. Sync changes only human headings;
its escaped evidence, outcome/exit semantics, credentials and conflict policy remain intact.
Its summary formatter stays in the existing protected helper, avoiding a new sync dependency.

The existing main Release mapping is retained separately as a seven-day compressed Actions
diagnostic with source/version/build/run identity and mapping digest. It does not enter APK
transport, updater manifests or public Release assets. Missing/empty mapping fails visibly;
the next natural main Release build must validate that hosted path. The full offline suite
ran 135 tests: 134 passed, one existing Windows executable-bit skip. Ten new presentation
tests cover compatibility, summaries, guard execution, mapping identity and no historical
backfill on retry. Natural skip/publication/Stable/recovery/diagnostic/Sync acceptance is pending.

Read-only release inspection confirmed numeric titles and the Wholphin APK alias for builds
5/8/9/11 and Stable 5; current rolling and immutable 11 asset digests match. No APK signature
reverification or historical mutation occurred. Broader README presentation remains deferred.

**Separate pre-existing Stable follow-up:** `mosaic_stable.verify_manifest` calls
`verified_manifest` without forwarding the authenticated `buildWorkflow`, whose default is
the legacy Development workflow. A pure fixture with identical valid bytes/provenance except
`buildWorkflow = .github/workflows/ci.yml` fails with “Stable input differs from verified
development manifest.” This line is unchanged by I05 and current Stable tests use legacy
build provenance. Before promoting a new main-CI-produced build, address that compatibility
gap with exact producer-binding tests in a separately scoped fix; never bypass the check.

## Item 6 I04 audit and high-confidence cleanup

**IMPLEMENTED / OFFLINE VALIDATED / HOSTED HIGH-RISK PATH LIVE VALIDATED.**
PR #26 merged at `3907726ce38a03936e5853e5e8d36fff6d4486e9`. The user reports the latest
live Development eligibility as `skipped_non_apk` / `tooling-only` / `high` / `24` changed
paths, with Release build/sign/publish correctly skipped after merge. This is live acceptance
of the high-risk non-APK path, not evidence of a new signed release. Natural low-risk
non-Android and normal targeted-Android I03 PR acceptance/timings remain pending.
At that I04 checkpoint, I05/I06 implementation and automation deletion remained outside scope;
the current I05/I06 sections above supersede that historical status.

The merged hosted Linux fix preserves both stage-output assertions and reuses the current
PowerShell host's absolute executable path with PATH cleared inside the fixtures. Local
Windows supplied the hard-coded nested `powershell.exe`, masking the defect; Linux supplied
`pwsh` for the outer process but could not resolve that nested Windows executable. Both focused
tests passed locally; all 125 offline tests completed with 124 passes and the existing Windows
executable-bit fixture skip. Restoring the old executable in memory made both fixtures fail,
confirming that local regression coverage now catches the original portability mistake.

The audit covered every workflow, deterministic helper ownership, checkout/API/artifact
overhead, Gradle configuration-cache behavior, local I03 timings, recurring warnings,
GitHub App token transport, and failure/retry semantics. It deliberately did not begin I05.

The [upstream automation audit](ITEM_6_UPSTREAM_AUTOMATION_AUDIT.md) now records the complete
inventory, capability gaps, UX findings and proposed I06 path ownership. Inherited `main.yml`
is guarded and its publication contract is replaced: propose **DOWNSTREAM-OWNED**, but retain
it until the explicit Actions-noise versus modify/delete divergence decision. Conflicts arise
when upstream later edits the deleted path, not unconditionally on every sync. Inherited
`release.yml` is **REVIEW**: it really generates Appstore and Fire TV AABs and retains mappings;
Mosaic's universal-APK Stable promotion does not replace those capabilities. It does not itself
upload to stores, verify AAB signatures or generate changelogs.

History shows upstream `pr.yml` was deleted when downstream `ci.yml` was introduced in
`905680ca`; keep that mapped validation area **REVIEW**, not an assumption of upstream ci.yml
lineage. Shared setup originated upstream and currently matches upstream exactly: **FOLLOW**.
All current workflows omit run-name; computed classification/version outputs cannot directly
populate a trigger-time run-name. Preserve `CI` and `Full validation` because release artifact
authentication and required checks consume them. The audit proposes semantic change reporting
even for excluded paths so intentional downstream divergence does not blind Repo Intelligence.
No ownership policy or I05/I06 changes are implemented. The standalone signing exercise remains
a useful **DIAGNOSTIC** key-custody/disaster path; all active delivery/recovery/sync paths remain.

Canonical deterministic owners remain: `mosaic_version.py` for source/version identity,
`mosaic_change_classification.py` for release relevance and validation risk,
`mosaic_validation_policy.py` for validation tiers, `verify_mosaic_apk.py` for signed APK
verification, and `mosaic_signing_exercise.py` for APK ZIP/provenance transport. Sharing helpers
must never collapse signing Environments, job permissions, or publication authority.

The approved I04 set makes six narrow corrections. Full local validation still runs repository-wide
`pre-commit --all-files`, then separately runs pre-commit for reviewed non-ignored untracked
candidate paths because all-files only enumerates the Git index. Per-stage command output now uses
one UTF-8 `StreamWriter` opened with reader sharing; root `validation.log` remains a one-time
post-run compatibility snapshot. `.logs/` has one Git-ignore rule and `.vscode/tasks.json` remains
explicitly tracked. Release publishers reuse an identical release-list response only within the
same pre-mutation process window; mutable state is fetched again on later invocations. Sync Bot
tests transport a long punctuation-bearing JWT-style installation token unchanged through the
process environment and prove it never appears in arguments or errors. Finally, the signing
exercise sign-only job uses a shallow checkout: it authenticates exact clean HEAD/tree/commit time,
fixed epoch/baseline, run/attempt and APK digest without history-derived version allocation; the
build job still uses full history and owns allocation.

Measured locally with the same 5,000-line command fixture, stage capture improved from `7.504s`
with per-line `Add-Content` to `1.455s` with the single writer (about 81% faster). Focused output,
legacy-lock, untracked-scope, release/recovery/Stable, shallow-signing, and opaque-token tests pass.
The audit also established that `providers.exec` running `mosaic_version.py` is the source of
configuration-cache invalidation when SHA/tree/version/build-time/dirty identity changes; that is
required provenance input, not a cache bug, so the allocator is unchanged. Of 15 workflow
checkouts (13 full-depth), 9 uploads and 7 downloads, most correspond to deliberate trust/workspace
boundaries; the sign-only diagnostic checkout was the proven shallow exception. Room/API warnings
are inherited app debt, Gradle warnings are future dependency/build work, optional codec messages
are environmental, and Release lint debt remains a separate baseline.

Deferred: the `main.yml` divergence decision, inherited `release.yml` disposition, endpoint-specific
safe retries, broader helper consolidation, lifecycle/artifact naming (I05), and low/normal I03
hosted timing acceptance. Uncertainty continues to fail closed; I01 classification, I02 artifact
ownership, recovery, Stable exact-byte promotion, updater compatibility, and Upstream Sync authority
separation are unchanged.

## Item 6 I03: classifier-selected PR/local validation and concise logs

**IMPLEMENTED / OFFLINE VALIDATED / HOSTED HIGH-RISK PATH LIVE VALIDATED.** I03 consumes the
canonical I01 change classifier without merging release relevance and validation risk.
`scripts/mosaic_validation_policy.py` maps complete no-rename change ranges to three
validation paths: proven non-Android scope runs changed-scope pre-commit and offline
workflow/Python tests; normal Android scope adds deterministic package-level JVM filters;
unknown paths and explicit build, release, signing, updater, identity, persistence, and CI
boundaries select Full. New/moved paths remain visible, and an unmapped production path
uses the broad all-JVM fallback rather than silently running no test.

Local `Fast`, `Standard`, and `Full` commands remain stable and accept explicit
`-TestFilter` values. Fast is the smallest classifier-selected iteration path. Standard is
the normal completed-task handoff and adds the relevant changed-scope hygiene/tooling and,
for Android work, compile evidence. Full always runs all-files pre-commit, every offline
tooling test, and the combined complete default-debug Gradle graph. High/unknown scope can
escalate a Fast/Standard request. The formerly invalid no-filter VS Code Fast/Standard
tasks now work through classification; the only visible tasks remain Prepare PR and the
three validation levels.

PR `CI / Full validation` retains its required-check name but now classifies the synthetic
merge range. Low-risk docs/metadata and isolated tooling do not install Android or run
Gradle; normal app changes compile and run mapped focused JVM tests; sensitive or unknown
changes retain Full defaultDebug and the reusable PR Debug APK. Every PR summary reports
release relevance, validation risk, selected path, changed-path count, and checks actually
run. The policy and canonical classifier are loaded from the trusted PR base tree so a PR
cannot weaken its own gate; the initial rollout, where the base lacks I03, forces Full.
Push/manual protected-main behavior is intentionally unchanged: all-files pre-commit,
all offline tests, full defaultDebug, then conditional sequential authoritative Release
assembly. Development remains exact-artifact sign/verify/publish with zero Gradle.

`validate-local` and autonomous `prepare-pr` now use concise `[RUN]`/`[PASS]`/`[FAIL]`
stages without guessed Gradle percentages. Complete output is retained under
`.logs/validation/<run>/` and `.logs/prepare-pr/<run>/`; repository-root compatibility logs
remain replace-on-run. For validation, `validation.log` is assembled from the run summary and
stage logs and copied once after the run; it is not a concurrent live output sink. This avoids
the Windows file-lock failures caused by reopening the same root file with `Add-Content` for
every Gradle output line. A compatibility-copy failure produces one warning and cannot hide or
change the underlying command result. Failure output is a bounded error-pattern/tail excerpt that preserves
source `file:line[:column]` text plus an absolute full-log path. Prepare-pr still enforces
complete-scope confirmation, snapshot stability, exact staging/commit tree equality,
authenticated `gh`, no-force publication, and its two human authority boundaries.

Hosted high-risk evidence is complete: PR #25 run `34438367580` passed Full. The preceding
run `34437472660` failed only because the then-untracked `.vscode/tasks.json` lacked a final
newline. Earlier local Full had run `pre-commit --all-files`, which cannot enumerate untracked
files; this was a real candidate-coverage gap, not a Gradle/application failure. Full now adds
a reviewed-untracked pre-commit pass while retaining the repository-wide pass.

Protected-main run `34438714060` passed authoritative Full at
`7f68430a2eb47ced851269ab40519c2815e0c2e9` and skipped Release assembly for the non-APK
range. Development run `34439134293` classified all 17 paths from published baseline
`44e81da48ca50b70f1be364b3008294130d8721d` through that trusted main as
`tooling-only` / `high`, emitted `skipped_non_apk`, and skipped APK build/sign/publish in
about 16 seconds. Still pending: one naturally occurring low-risk non-Android PR and one
normal APK-relevant mapped-target PR; do not create artificial PRs solely for acceptance.

Deferred, not implemented: exact equality between a tested PR synthetic-merge tree and the
final protected `main^{tree}` may later allow reuse of Full-validation evidence. The PR
Release APK itself is not reusable under current Mosaic identity: `SOURCE_SHA`, `BUILD_TIME`,
and first-parent-derived version identity are commit-derived. Any uncertainty or tree
mismatch must continue to rebuild and validate protected main.

## Item 6 I02: authoritative main Release artifact ownership

**COMPLETE / OFFLINE + LOCAL FULL + LIVE + DEVICE VALIDATED.**
The governing matrix, exact run/task counts, implementation evidence, and final acceptance are in
[the Item 6 tracker](ITEM_6_CONSOLIDATION_CHECKLIST.md#i02-evidence-and-measurement-pass-2026-09-09).

Expected → Observed → Consequence: I02 was expected to remove genuinely duplicate heavy
work, but Debug and Release are not interchangeable proofs. PR/main CI run one
`defaultDebug` Gradle invocation; `compileDefaultDebugKotlin` appears through dependencies
but executes once. `defaultRelease` separately executes variant-specific proto, KSP,
Kotlin, resources, R8, vital lint, optimized packaging, and unsigned APK assembly. The
signing exercise demonstrated limited same-workspace reuse of common OpenAPI/proto outputs,
while both variant compilers remained necessary. A previously attempted combined
concurrent Debug+Release invocation exhausted hosted memory, so a single enlarged Gradle
command is a rejected initial design.

The implemented I02 boundary is therefore build-once ownership, not deletion of Release
evidence: PR synthetic-merge Debug validation remains unchanged; on an exact protected-main
push, CI classifies the full unpublished Development range, runs Debug validation, and then
conditionally runs the bounded Release assembly sequentially in the same workspace. CI
uploads the authoritative universal unsigned Release APK plus provenance under
`unsigned-mosaic-main-ci-1.0.N-<sha>-run-<ci-run>-attempt-<attempt>`, retained for seven
days. Proven non-APK ranges still complete without Release assembly.

Development retains I01 classification plus exact-main/latest-successful-CI trust, resolves
exactly one artifact from that CI run/attempt, and validates its immutable ID, exact name,
digest, source/repository/run/job/timestamp ownership, provenance and unsigned APK bytes.
Only then does the existing Environment-bound signer run. The Development workflow now has
no Gradle, setup composite, build job, or silent rebuild fallback; publication remains a
separate write-only authority without signing secrets. Missing, expired, ambiguous,
wrong-SHA/run/name/digest, or otherwise unauthenticated artifacts fail closed.

Recovery was extended without invalidating existing checkpoints. Unsigned recovery accepts
the new successful main-CI artifact and legacy Development-build artifacts; signed recovery
accepts current and legacy Development signed artifacts. New manifests identify
`.github/workflows/ci.yml` and the original CI run/attempt as the build producer. Stable
still promotes exact signed bytes, and `Wholphin-release.apk`, `mosaic-release.json`,
versions, tags, signer, and updater behavior are unchanged.

Final acceptance used PR #24 and protected-main SHA
`44e81da48ca50b70f1be364b3008294130d8721d`. Local Full passed repository-wide pre-commit,
production Kotlin compile, the full default-debug JVM suite, default-debug APK assembly,
and whitespace validation. Main CI run `34407365166`, attempt `1`, completed Full validation
before sequential Release assembly and produced version `1.0.11` unsigned artifact ID
`10126382836` (archive SHA-256 `2a3274203cc1b1815ed540b0a87c47a59379897e4f4fb4226f61126e70c35caa`;
unsigned APK SHA-256 `76a5e078a43f75b28403131082882404dfbee286b9b50f58e826a6cea9e69db9`).

Development run `34408806518`, attempt `1`, authenticated the exact repository, branch,
SHA, run, attempt, numeric artifact, provenance and digests; mismatches remained fail-closed.
It ran `classify → authenticate/download → sign → verify → publish` with zero Gradle.
Signing and verification produced APK SHA-256
`98472b4e2537669b0894c6cf49ebc0c20229c633307f82b11da8e8e265d1c941`; immutable
`downstream-build-11` and rolling `develop` publications were byte-identical where required,
with provenance and updater compatibility preserved. Timings were main Full 5m25s, Release
assembly 9m12s, complete main CI 15m56s, and Development classify/sign/publish 11s/34s/17s
(1m13s total).

Device acceptance completed the chain: Wholphin detected Development `1.0.11` / version code
`11`; the installed published APK displayed `Enables Downloads, acquisition tracking,
missing-season requests, and library diagnostics.` under `Settings → More → Enhanced
features`, proving the delivered bytes contained the accepted source change. Legacy recovery,
signing/provenance isolation, exact-byte Stable promotion, and updater contracts remain intact.

Future optimization, explicitly outside I02/I03: exact tree identity may permit reuse of
pre-merge **Full-validation evidence**, but not the current PR Release APK bytes. Mosaic's
`SOURCE_SHA`, `BUILD_TIME`, and first-parent-derived version identity bind those bytes to a
commit context. Any mismatch or uncertainty falls back to the proven protected-main Full
validation and Release-build path.

## Item 6 I01: canonical change classification and Development skip

**COMPLETE / OFFLINE + LIVE VALIDATED.** This checkpoint changes only Development release
eligibility. It does not begin I02 artifact/validation consolidation.

Expected → Observed → Consequence: the Development workflow previously built, allocated,
signed and published after every trusted `main` CI, including docs/tooling-only changes.
Eligibility cannot safely inspect only the newest commit because an earlier unpublished
APK change could otherwise be hidden by a later docs merge. The new canonical classifier
therefore compares the last successfully published Development `sourceSha` through the
current authenticated main SHA. Proven non-APK ranges finish as `skipped_non_apk` before
Android setup, Gradle, version allocation, signing or publication. APK-relevant and
uncertain ranges retain the complete existing path.

`scripts/mosaic_change_classification.py` owns repository path semantics and independently
emits release relevance (`apk-relevant`, `android-validation-only`, `tooling-only`,
`docs-only`, `unknown`) and validation risk (`low`, `normal`, `high`). These dimensions
must not be collapsed: a signing-workflow edit is non-APK but high risk, while an ordinary
production UI edit is APK-relevant but may be normal risk. Unknown inputs are always
`unknown/high` and require a release. Git rename detection is disabled for the range so
moving/deleting a production input cannot hide its old APK-relevant path.

The baseline is not trusted from the mutable `develop` tag alone. The publisher helper
cross-checks the exposed rolling prerelease/name/direct commit ref against the matching
annotated `downstream-build-N` tag, canonical manifest, immutable prerelease, and the exact
APK/manifest asset identities on both releases. Missing or inconsistent publication
state, incomplete Git history or a non-ancestor baseline fails conservatively into the
normal release path. This authentication deliberately reuses the existing public
provenance contract; it does not create a second ledger.

Workflow structure is classifier → conditional build → unchanged sign → unchanged
publish. Only `build` depends on and is gated by classifier output. Keeping the established
sign/publish dependency text intact preserves the isolated signing and publication proof
used by recovery and signing-boundary tests; when build skips, GitHub naturally skips both
downstream jobs. The version allocator, exact-main/latest-successful-CI and superseded-main
checks, signing/provenance boundaries, recovery, Stable promotion, asset names and updater
compatibility are unchanged.

Offline coverage includes independent relevance/risk, known indirect inputs, unknown
fallback, accumulated multi-commit ranges, mode-only changes where supported, APK-source
moves, ancestry failure, authenticated/tampered Development state, and the workflow job
boundary. Live run `34379457375` at main
`7881aa19850c46e53b43504c38a81a2e62dbb9a3` classified 9 changed paths as
`tooling-only` / risk `high`, emitted `skipped_non_apk`, and skipped build, sign, and
publish. It completed in about 12 seconds with no APK, version allocation, immutable
build, or rolling `develop` update. Before I01, an equivalent tooling-only merge could
spend roughly 11 minutes building/signing/publishing a pointless app release. See the
evidence/readiness state in
[the Item 6 tracker](ITEM_6_CONSOLIDATION_CHECKLIST.md#implementation-checkpoints).


## Historical v1 upstream publication diagnosis (superseded by I06)

This section preserves the evidence that motivated I06. Its ready-only token behavior,
no-PR conflict outcome and once-daily schedule are not current operating instructions;
use the I06 section at the top of this handoff and `UPSTREAM_SYNC.md`.

Audit of live run 34346400694 and artifacts 10101863873 / 10101871740 disproved the
suspected App-token binding failure. Both records say blocked: Textual conflicts require
human semantic resolution, in SeriesOverview.kt and SeriesViewModel.kt under
app/src/main/java/com/github/damontecres/wholphin/ui/detail/series/.
Upstream was `0b995b5404aba166a7931ade67ab1bc256f8418b`; downstream was
`7d55b98b22e2d440599dfef7288f2ac066a0f8b1`. The App mint step was skipped, correctly:
only ready candidates need Contents/PR write. Empty SYNC_PUBLISH_TOKEN was expected.
The publish job had Issues write; its durable issue attempt failed. Read-only repository
metadata now confirms has_issues=false. Historical response details were suppressed, so
this is the confirmed current external recording blocker, not evidence of invalid App keys.

Token wiring already matches the pinned official action: vars.SYNC_BOT_CLIENT_ID plus
secrets.SYNC_BOT_PRIVATE_KEY -> create-github-app-token, owner constbogdan/repositories
Wholphin -> steps.publication.outputs.token -> SYNC_PUBLISH_TOKEN -> only branch push/PR
creation subprocesses. No App permission, credential, fallback or token wiring change is
needed. Ready-candidate diagnostics report only present/missing and reject empty authority
before branch/PR mutation. Disabled Issues now has an explicit safe retained failure reason.
Observation remains read-only; the publish job retains its existing Issues-only repository
write permission for blocked records. The App is minted only for ready, never conflicts.
No Mosaic credentials or release behavior change.

**Next external step:** enable repository Issues (Settings -> General -> Features -> Issues)
with separate authorization. No setting was changed here. Then separately authorize a new
observation run after this branch is merged; do not re-run the old workflow revision:

```powershell
gh workflow run upstream-sync.yml --repo constbogdan/Wholphin --ref main
```

The next daily 06:23 UTC schedule also uses merged code. Conflicts should retain a durable
blocked issue and failed outcome; they must not mint an App token or create a sync PR.
A genuine ready candidate is required to exercise App-token publication and required PR CI.
The recorded Series conflicts still require human semantic resolution; this fix does not
resolve them or claim live branch/PR publication operational.

Reuse old artifacts as audit evidence, not executable authority. The old downstream SHA
is already stale. Fresh observation is inexpensive relative to APK validation and executes
no application build/tests; publication intentionally reobserves and validates exact refs,
remote tips and PR decisions. Avoid a historical-artifact resume mode. Existing branch/PR
reuse handles partial retries without force push. Prior checkpoint references to a credential
binding cause are superseded by this verified diagnosis.

Validation: 30 sync tests passed in the full focused run; the new workflow test initially
matched App permissions as repository permissions. After restricting that assertion to
the job permission block, its rerun passed. Actionlint/YAML, repository-wide pre-commit,
UTF-8/mojibake and diff checks passed. Local links were checked; only the pre-existing
PREPARE_PR.md current-workflow-continuity anchor is missing. No live retry was dispatched.

## Current release acceptance and next plumbing task

All six release milestones are COMPLETE / LIVE VALIDATED: permanent signing; updater
routing; rolling Development; device in-place updates; Stable promotion + channel UX;
and automatic Development delivery. User-supplied [automatic delivery evidence](MOSAIC_DEVELOPMENT_RELEASE.md#automatic-development-and-channel-migration-acceptance)
records PR #20/main `5818b605fe64fae97bdd20feed7b1df60600d08a`, automatic release #2,
v1.0.8/downstream-build-8, exact signed hash, 9m55s build / 37s sign / 18s publish / 11m02s
total, and no manual dispatch or Environment approval. The Environment still isolates keys.
Mosaic itself updated preserved 1.0.5 -> 1.0.8, retaining state/settings and migrating the
exact develop API URL to Development. Custom exposes its advanced API URL field.
Fresh/default Stable is implemented; no separate fresh-install observation was supplied.

[Stable acceptance](MOSAIC_STABLE.md#stable-promotion-acceptance) records unchanged build-5
bytes, mosaic-v1.0.5/latest, exact hash and 38s verify / 20s publish / ~1m05s total, with
no build/signing. Stable stays manual; Development is now continuous after successful CI.
Earlier pending statements are retained as historical evidence, superseded here.

The current device baseline is 1.0.8. Automatic discovery worked, but proactive notification
was absent during normal use, re-entry and force-stop/reopen; Settings/About exposed the
update. Track deduplicated non-blocking notification, duplicate Install update surfaces,
clear update states and broader Settings/selector presentation in the roadmap.

**NEXT plumbing: Upstream Sync publication credential binding.** Scheduled run
`34346400694` observed upstream successfully (observation artifact `10101863873`) but
publication failed because SYNC_PUBLISH_TOKEN was empty (outcome artifact `10101871740`).
Observation remains read-only and operational. Publication remains blocked; investigate
binding while retaining separate narrow publisher authority, never broadly elevating
GITHUB_TOKEN. No credential repair or external operation occurs in this checkpoint.

After that plumbing, the existing **Item 6 optimization/refactor/cleanup** workstream remains
pending. This historical workstream name is distinct from completed release milestone 6
(automatic delivery). Start with representative local/Actions task-timing-overlap analysis;
proposed changes to PR/main gates are investigation targets, not current permission to
weaken Full CI. Preserve [roadmap follow-ups](Wholphin_ROADMAP.md#post-delivery-optimization-and-product-follow-ups),
including telemetry-first fluid progress, safe forward recovery, naming cleanup and later
repository organization. Do not implement those ideas in this checkpoint.

## Historical automatic Development implementation checkpoint

## Automatic Development after trusted main CI

**IMPLEMENTED / LIVE AUTOMATIC ACCEPTANCE PENDING.** User confirms exact-byte Stable
promotion of downstream-build-5 complete. Stable remains manual; prior Stable-pending and
Development-manual checkpoints below are historical. Next acceptance: installed 1.0.5 ->
newer automatic Development, channel migration and preserved settings. Do not reset the device.

Expected -> Observed -> Consequence: workflow_run follows CI but github.sha is the default
branch tip, not necessarily triggering CI's head SHA. Require equality, canonical push/main,
protected current tip, latest successful CI run/attempt and Full validation before build and
again before publication. Superseded sources stop rather than substituting unvalidated code.
Rapid merges may coalesce candidates; main moving during build leaves recoverable artifacts.

Publication eligibility shares the guarded event validation; epoch/allocation/identity are
unchanged. Recovery recognizes automatic development producers as well as historical manual
runs; recovery itself stays manual. Build once after CI -> immutable unsigned ID -> direct
Environment-bound read-only signing -> verified signed ID -> separate Contents-write publisher.
Secrets stay step-only. No Stable workflow, signing action, app, CI graph or device changes.
Separate Release compilation still follows Full Debug CI; measured item-6 optimization remains
pending. CI re-runs cannot replace an already published identity with new bytes/run provenance.

[Development contract](MOSAIC_DEVELOPMENT_RELEASE.md#trusted-build-sign-and-publish) records
race behavior and first live acceptance. No new secrets/settings are required or configured.
Existing Environment reviewer policies, if any, still apply; they are not bypassed.

Validation: the complete 83-test Python suite had one signer-text comparison failure due
solely to the intended trigger difference. After narrowing that assertion to compare all
other signing job properties/steps, all eight signer tests passed; the other 82 suite tests
had passed. Repository-wide pre-commit and actionlint/YAML passed. UTF-8/mojibake, local
links/anchors and whitespace were checked; only the pre-existing PREPARE_PR.md reference
to the missing current-workflow-continuity anchor remains. No application/Gradle change
requires a new JVM run. Automatic publication and selector upgrade acceptance await merge.


## Historical stable implementation checkpoint

## Stable promotion and update channel selector implemented

**Stable promotion + channel UX - IMPLEMENTED / LIVE STABLE PROMOTION PENDING.**
Permanent signing, updater routing, development delivery and in-place update acceptance
remain COMPLETE / LIVE VALIDATED. CI/developer-velocity optimization remains PENDING.
The existing acceptance checkpoint below is preserved; its Stable NEXT status is
superseded by this implementation, not by a live promotion.

[Stable contract and exact first-promotion command](MOSAIC_STABLE.md) describes manual
approved downstream-build-N/source/hash promotion to an immutable mosaic-v1.0.N stable tag/release (numeric name v1.0.N),
fresh SDK verification, exact APK/manifest reuse, latest semantics and retry conflicts.
No build/signing occurs; only a separate publisher has Contents write, without key access.
Known-good downstream-build-5 remains the first candidate; its APK remains unchanged.

Updates now offers Stable / Development / Custom via the existing TV choice control.
Protobuf field 16 persists channel choice; unspecified records migrate from exact known
URLs. Current 1.0.5's preserved develop API URL becomes Development. Fresh/default is
Stable; unknown URLs become Custom. Explicit channel overrides retained inactive custom
URL state. All consumers share the resolver. Equal/older versions are not offered or
installed; switching newer Development to Stable waits without downgrade. Automatic
checks retain their current behavior. Live selector/device migration acceptance is pending.

Development publication remains manual after a protected-main merge and CI; there is no
automatic development publishing trigger or standing authorization added here. A later
selector-containing APK is needed to test the new UI: promoting unchanged 1.0.5 cannot
retrofit it. No stable release/tag, settings change or live dispatch occurred in this task.

Broader Settings redesign, cleaner General/Playback/Library/Downloads/Updates/Integrations/
Advanced groups, notification UX and consistent progress/status UX remain future work.
Retain prior CI timing/overlap, change-aware validation, concurrent PRs/merge queue and
quiet prepare-pr/full-log plans; this task implements none of that optimization.

Validation: Standard local validation passed with `*TestUpdateChecker*` and
`*VersionCompareTests*`, production Kotlin compilation and the acquisition/tracker/
pagination/downloads regression checks. Repository-wide pre-commit passed. The Python
suite passed 80 tests; the seven focused stable tests passed again after choosing the
collision-safe `mosaic-v1.0.N` tag. Actionlint/YAML, UTF-8/mojibake and whitespace checks
passed. Documentation links were checked; the pre-existing `PREPARE_PR.md` reference to
the missing `CODEX_HANDOFF.md#current-workflow-continuity` anchor remains outside this
change. Live stable promotion and selector/device acceptance remain pending.


## Mosaic development delivery and in-place updater acceptance - COMPLETE / LIVE VALIDATED

User-supplied acceptance establishes operational downstream delivery and Mosaic-driven
1.0.3 -> 1.0.5 updating. Full evidence, hash, recovery boundaries and timing observations
are in [the delivery acceptance record](MOSAIC_DEVELOPMENT_RELEASE.md#development-delivery-and-in-place-updater-acceptance---complete--live-validated).

The initial normal run built source `41f9f83c36b8866211c9680d3b416d5ebede4888`, version
1.0.5/code 5, unsigned artifact `10099950969`; signing-secret availability failed and
publication was skipped. This was an orchestration/Environment-binding regression, not
a key/certificate/APK/password failure. Ordinary Environment-bound jobs and the shared
`mosaic-sign-apk` action preserve step-only credentials, read-only signing, no PR secrets,
presence-only diagnostics and one signing implementation with no Gradle rebuild.

After successful CI for tooling `7d55b98b22e2d440599dfef7288f2ac066a0f8b1`, manually
authorized unsigned recovery authenticated, signed, verified and published that existing
artifact with zero build/Gradle work. `downstream-build-5` and rolling `develop` are
prereleases, not stable/latest, exposing identical `Wholphin-release.apk` and
`mosaic-release.json` provenance. Signed APK SHA-256:
`af0dcb7fb1c89800c61e7a7a0558cbb2e6fc65fbf880069dbe08c3c4df8bf578`.

The preserved 1.0.3 install used custom API URL
`https://api.github.com/repos/constbogdan/Wholphin/releases/tags/develop`; its offered
update changed from upstream v1.0.7 to downstream v1.0.5. Release metadata showed the
correct downstream build/source/hash. Mosaic's **Download & Update** selected and
downloaded the ~26.40 MiB APK itself. After Android's expected first-use **Allow from
this source** permission, the APK installed in place: no ID/certificate conflict,
uninstall, ADB install or data clearing. Mosaic reopened with **Wholphin updated to
v1.0.5**. Library/application state, installed build/source/hash metadata and the custom
develop URL remained present. Settings/data preservation is live-observed. The installed
baseline is now 1.0.5; earlier instructions to keep 1.0.3 are historical, not reset advice.

1. **Permanent signing identity - COMPLETE / LIVE VALIDATED.**
2. **Updater routing - COMPLETE / LIVE VALIDATED.**
3. **Rolling development release - COMPLETE / LIVE VALIDATED.**
4. **Live device in-place update acceptance - COMPLETE / LIVE VALIDATED.**
5. **Stable promotion - NEXT.**
6. **CI/developer-velocity optimization - PENDING.**

Retain build failure -> rebuild; sign failure -> reuse unsigned artifact; publish
failure -> reuse signed artifact. Unsigned recovery is live validated; signed recovery
is implemented/offline-tested, with no separate live signed-retry evidence supplied.
Automatic publication remains disabled. The uninterrupted normal workflow was not
rerun end-to-end successfully as part of the supplied evidence; delivery succeeded via recovery.

Retain the 16m43s build/34s signer and recent ~6-7 minute main CI observations. Local
prepare-pr work overlaps hosted CI; repeated Kotlin/Gradle compilation, especially
compileDefaultDebugKotlin, is costly. Release assembly currently follows Debug main CI;
artifact recovery proves zero-Gradle downstream retries. Future work includes authoritative
artifact reuse, change-aware validation, concurrent PRs/merge queue, fast feedback versus
Full gate, better local/GitHub progress UX, quiet prepare-pr with complete logs, and a
measured task-overlap/timing matrix from representative Actions logs before redesign.

Historical implementation checkpoints below retain their original investigation limits.
Their pending-first-publication/update and preserve-1.0.3 instructions are superseded by
this acceptance checkpoint. No functionality or external state changed while recording it.


## Artifact-based signing and publication recovery implemented

The prior blanket instruction not to reuse unsigned artifact 10099950969 was an
implementation limitation, not a GitHub security constraint. Original run 34340900095
failed only after successful build/artifact transfer for main source
41f9f83c36b8866211c9680d3b416d5ebede4888, version 1.0.5. Read-only GitHub metadata confirmed
its unexpired artifact/digest and successful producing job; hosted content checks remain
mandatory. See [audit evidence and exact recovery commands](MOSAIC_DEVELOPMENT_RELEASE.md#manual-post-build-recovery).

The manual resume workflow runs current approved protected-main tooling against the exact
approved old source/artifact. It validates original workflow/run/job/attempt ownership,
first-parent ancestry, original/current CI, artifact digest and exact original provenance.
Unsigned recovery signs existing bytes; signed recovery re-verifies existing bytes with
no Environment/key and no re-signing. Both reuse the publisher with zero Gradle work.
Normal build/sign/publish same-run gates remain unchanged. Original build run/version
identity remains in the manifest; a separate recovery.json records new execution evidence.
Published bytes and ledger are never replaced to accommodate a retry. Live resume is pending.


## Mosaic signing Environment binding correction - live retry pending

Expected: the extracted reusable signer would retain the previously validated Environment
credentials. Observed: development run 34340900095 built source
`41f9f83c36b8866211c9680d3b416d5ebede4888`, version 1.0.5, and transferred immutable
unsigned artifact `10099950969`; download/digest and unsigned checks passed, but all
four signing variables were empty. SDK signing failed; publication was never reached.
Consequence: restore ordinary signing jobs with direct `mosaic-release-signing`
Environment binding in both callers. Share only the SDK signing operation through
`.github/actions/mosaic-sign-apk/action.yml`; remove `mosaic-isolated-sign.yml`.

Read-only GitHub metadata confirmed all four expected Environment secret names exist;
no values were obtained. GitHub documentation says job-level Environment secrets are
available in reusable workflows and override caller secrets, so missing `secrets: inherit`
is NOT an established root cause. That option would unnecessarily inherit unrelated
repository secrets. `workflow_call.secrets` declares caller-supplied values; callers
cannot bind an Environment on a reusable-workflow invocation. The precise service-side
cause of empty values remains unconfirmed. This correction removes the failed boundary
without moving secrets, replacing keys or changing GitHub settings.

Only the shared action invocation receives the four step-scoped secrets. It reports
names as present or missing with tracing disabled and stops before key-file creation
if anything is empty. No private values, lengths or hashes are logged. Existing cleanup,
SDK signing, payload comparison, certificate/package/version/provenance checks, exact
artifact IDs and read-only signing permissions remain. Build and publisher logic are
unchanged. Tests enforce identical signing jobs and execute diagnostics with public
fixtures only; they do not simulate GitHub Environment secret resolution.

The original retry guidance below is superseded by the guarded artifact recovery
checkpoint above: use current merged tooling while preserving original artifact provenance.
GitHub rerun of the old failed job still uses old workflow code; use the new resume dispatch. Preserve the 1.0.3 device baseline. An unsigned artifact resume retains the original
version and must show all four names present, successful verification and publication
before proceeding to in-place acceptance. No live retry was dispatched for this fix.


## Mosaic rolling development release implemented - live publication pending

Permanent signing is COMPLETE / LIVE VALIDATED. Updater routing is merged and awaits
live release validation. The rolling development publisher is IMPLEMENTED / LIVE
PUBLICATION PENDING; live device in-place update acceptance is NEXT. Stable promotion
and CI/developer-velocity optimization remain PENDING. No release/tag/dispatch or
external settings change occurred during implementation; automatic publication is disabled.

[Development publication contract](MOSAIC_DEVELOPMENT_RELEASE.md) records the exact-SHA
manual gate, successful protected-main push CI reuse, Release-only build, shared isolated
signer, immutable artifact-ID handoffs, annotated downstream-build-N ledger, durable
prerelease assets and rolling develop update. Signing and publication perform zero
Gradle rebuilds. Existing exercise Full validation behavior is preserved; only its
signer job is extracted to a common workflow. Normal PR/required CI is unchanged.

Expected: publish existing validated source without another Full Debug validation.
Observed: ordinary main CI has no authoritative Release artifact to promote.
Consequence: require successful exact-main CI, build Release once with bounded workers,
then sign/verify/publish those bytes. Retain measured artifact-reuse work for later;
do not duplicate Debug tests merely to publish. Existing 16m43s/34s timings remain evidence.

Immutable identity is reserved before upload; conflicting bytes or original run/attempt
provenance fail closed. Rolling replacement temporarily drafts develop, so interrupted
publication may leave the channel unavailable. No atomic availability or byte-for-byte
reproducibility claim. Recovery must preserve the ledger and original artifacts; a new
run is not permission to replace N. See the contract for partial failure and settings limits.

Preserve installed signed Mosaic 1.0.3 unchanged. Its temporary custom URL must be the
JSON API endpoint `https://api.github.com/repos/constbogdan/Wholphin/releases/tags/develop`.
Later acceptance must prove discovery/download, Android in-place update and retained data.

Optimization remains planned: slim/quiet prepare-pr.ps1, complete logs with concise
summaries, measured local/hosted overlap using real Actions logs, change-aware validation,
fast PR feedback versus Full merge gate, concurrent PRs/merge queue evaluation,
authoritative main Release artifact reuse, and zero-build signing/publication.


Validation: all 61 repository offline Python tests passed; actionlint 1.7.12 accepted
all three workflows (embedded shellcheck/pyflakes disabled); repository-wide pre-commit
and explicit new-file hooks passed. UTF-8/mojibake scan passed across 18 Markdown files;
new local links/anchors resolve. The pre-existing PREPARE_PR.md link to missing
`CODEX_HANDOFF.md#current-workflow-continuity` remains unchanged. git diff --check passed.
Application/updater, allocator, pinned certificate and required ci.yml are unchanged.
No hosted execution or publication was performed; those results remain pending.

## Mosaic updater routing implemented - pending live release validation

Permanent signing is COMPLETE and operational. Updater routing is implemented in
`feat/mosaic-updater-routing`; rolling development release is NEXT. No release/tag,
updater-driven installation, signing/settings change or publication occurred here.
The existing installed signed Mosaic 1.0.3 remains the baseline for the future in-place
update acceptance; routing in a later build does not change that installed old binary.

`UpdateSourceResolver` supplies downstream stable/development metadata and installed
notes. Settings retain the editable Update URL: defaults are the human-facing GitHub
URLs for constbogdan/Wholphin latest and tags/develop, converted to GitHub JSON API
endpoints for requests. APK selection uses assets from that same resolved response.
Installed notes use the chosen source, then same-repository v-prefixed/unprefixed
version tags where supported, and require a version match. A moved rolling endpoint
cannot masquerade as the installed version's notes; absent matching history yields
"Release not found". Non-GitHub custom endpoints are not rewritten or given guessed
tag URLs. No independent upstream release-note lookup remains.

Migration: blank values and the exact old bundled API stable default migrate to the
new stable URL on preference deserialization/resolution. The stored preference has no
origin flag, so an intentional choice of that identical old default is indistinguishable
and also migrates. All other custom values remain, including an explicitly chosen old
upstream develop URL; users must change that override to Mosaic develop themselves.
This is a read-time normalization, persisted on a later preference save, not a schema
or application-ID migration. Existing upstream test fixtures remain intentional.

Version parsing/comparison is unchanged: release **name** must be numeric 1.0.N or
v1.0.N (legacy vX.Y.Z-N-gHASH also supported), not simply "develop". Future publication
must supply exact Wholphin-release[-ABI].apk and, if offered, Wholphin-debug[-ABI].apk
aliases pointing to the intended signed bytes. Selection prioritizes these aliases;
no Mosaic alias or fallback dependency was introduced. Download/install behavior,
signing, application ID, allocator and CI configuration are unchanged. Until downstream
releases exist, default metadata/notes may return no release; no upstream fallback.
Targeted TestUpdateChecker and VersionCompareTests passed, including intercepted-HTTP
source/notes/asset tests and serialized-preference migration. Production Kotlin compiled;
repository-wide pre-commit and explicit new-resolver hooks passed. Documentation links
and git diff --check passed. Standard validation also passed its acquisition model/tracker, pagination and Downloads
regression suites (4m49s total). Live release/update acceptance is still pending.

## Mosaic permanent signing acceptance - COMPLETE / OPERATIONAL

User-confirmed live acceptance: [run 34323962085](https://github.com/constbogdan/Wholphin/actions/runs/34323962085)
(Mosaic signing exercise), source `055dde77b00c9b6e814d1115422bc60f8fd334b3`, version
`1.0.3` / code `3`, applicationId `io.github.constbogdan.mosaic`. Hosted build succeeded
in approximately **16m43s**, isolated signing in **34s**. The sequential memory fix
therefore has successful hosted evidence; the earlier failed run never reached signing.

The downloaded `Mosaic-release.apk` and `verification.json` were independently checked:
apksigner verified one RSA-4096 signer matching the pinned permanent SHA-256, with
v1/v2/v3 true; aapt verified package/version; emulator installation succeeded and Android
reported code 3, name 1.0.3, minSdk 23, targetSdk 37 and PackageSignatures. Full public
certificate, signed/unsigned hashes, source/tree/upstream provenance and independent
verification details are retained in [signing acceptance evidence](MOSAIC_SIGNING.md#first-permanent-release-signing-acceptance).
These are user-supplied acceptance results; Codex did not handle keys or rerun signing.

Permanent identity, protected Environment secrets, isolated hosted signing without a
rebuild, provenance verification, APK identity and Android installation are now proven.
The key remains outside Git with two independent encrypted backups and tested recovery;
only public fingerprint/verification metadata is repository-visible. PR jobs have no
signing credentials. No GitHub Release was published by the exercise.
**Keep the installed Mosaic 1.0.3 instance as the future in-place updater test baseline.**

Acceptance-checkpoint sequence (superseded by routing implementation above):
permanent signing COMPLETE -> updater routing then NEXT -> rolling
development release -> live device in-place update acceptance -> stable promotion ->
CI/developer-velocity optimization. All later items remain pending. Preserve the
16m43s build / 34s signing timings and [optimization scope](MOSAIC_SIGNING.md#remaining-release-sequence):
slim/quiet prepare-pr.ps1; full diagnostic logs with concise console summaries; avoid
duplicate local/hosted validation; change-aware validation; fast PR feedback vs Full
merge gate; merge queue; authoritative main Release artifact reuse; zero-build signing/
publishing. Build a measured validation-overlap/timing matrix from representative
GitHub Actions logs before redesign. This checkpoint implements none of that work.

Historical entries below retain earlier investigation/validation limits. Their
unverified/pending-first-signing statements are superseded by this operational milestone.

## Hosted signing exercise memory correction (2026-09-09)

**Expected → Observed → Consequence**

- **Expected:** combined Full validation + unsigned Release build fits the hosted runner.
- **Observed (user-provided live evidence):** Debug and Release Kotlin compilation
  overlapped; `compileDefaultDebugKotlin` / `BuildToolsApiCompilationWork` failed with
  "Not enough memory to run compilation." The signing job was never reached.
  A backend reference to HomePageContent is not independent evidence of a source defect.
- **Consequence:** run Full Debug compile/tests/assembly first, then a separate unsigned
  Release assembly/vital graph after success. Both commands keep publication identity
  checks, use `--no-daemon --no-parallel --max-workers=1`, and share the same checkout.
  No checkout/ref change, clean, rebuild in signer, test exclusion or heap increase.

Inspection: tracked Gradle heap is `-Xmx2048m`, `org.gradle.parallel=true`; there is no
explicit worker limit, Kotlin daemon heap or compiler execution strategy override in
this workflow/setup/project configuration. AGP built-in Kotlin is enabled. Kotlin
normally uses a separate daemon and can inherit Gradle heap limits; the exact hosted
compiler process heap/runner memory was not measured here. Worker limits bound Gradle
scheduling, not every internal compiler thread or total RSS. Separate invocations
remove the observed cross-variant overlap. The inherited upstream-only main/release
workflows request an 8 GiB heap; that override is not applied to this exercise.
Normal PR CI already runs only the Debug graph and is unchanged.

Only this exercise receives worker/parallel limits. Secrets, Environment, exact-main-SHA
gates, unsigned provenance and artifact-ID transport remain unchanged. No HomePage or
other application code changed. At that checkpoint signing remained live-unverified;
the subsequent successful run 34323962085 is recorded above. No live run was dispatched
by Codex during the memory-fix task.

Validation: 23 focused exercise/version/verifier tests passed, including sequential
success-only steps and retained identity/secret checks. Repository-wide pre-commit,
actionlint, YAML/Bash syntax, documentation links and git diff --check passed. Both
local Gradle dry-run graphs accepted the worker flags and selected only their intended
variant; no compilation or JVM tests were rerun for this workflow-only correction.
Local dry runs omit publication mode because this is not a clean protected-main hosted
checkout; publication authorization is covered by offline fixtures. These checks do not
prove hosted memory recovery. See [Gradle CLI](https://docs.gradle.org/current/userguide/command_line_interface.html)
and [Kotlin compilation](https://kotlinlang.org/docs/gradle-compilation-and-caches.html)
for the scheduling flags and daemon-memory behavior.

## Mosaic isolated signing exercise implemented (2026-09-09)

IMPLEMENTATION CHECKPOINT (superseded by live acceptance above): the user reported `mosaic-release-signing` restricted to main and the four
MOSAIC Environment secrets configured externally. Permanent custody/public fingerprint
remained established. Isolated CI signing was then untested; it is now live-validated above.

The manual [signing exercise](MOSAIC_SIGNING.md#implemented-manual-hosted-exercise)
now implements Full Debug validation plus Release unsigned assembly and its existing vital checks,
immutable same-run artifact transport, isolated Environment signing without rebuilding,
public signer/package/version/provenance verification and unchanged-payload checks.
Only a canonical protected-main dispatch with an explicitly matching full SHA is
eligible. Secrets exist only in the signing step; all permissions remain read-only.
The allocator's narrow manual-event extension preserves push behavior and rejects
PR/unprotected/mismatched-SHA publication identities. Existing required CI is unchanged.

Signed/unsigned exercise artifacts have version/full-SHA/run/attempt names and 7-day
retention. Rerun the full workflow: failed-job-only reruns reject stale attempt input.
This is not durable release identity enforcement or publication; updater routing,
rolling develop and stable publication remain disabled. The exact separately authorized
first-run command is in the signing document.

Validation: 22 focused exercise/version/verifier tests passed, covering exact artifact
transport, tampering, immutable naming, event/ref/protection/SHA gating and signature/
package/version rejection. Actionlint 1.7.12, YAML structure and Bash syntax passed;
repository-wide pre-commit and final changed-file hooks passed. All local documentation
links/anchors resolve. No key or real signing command was executed. Gradle exposes no
`testDefaultReleaseUnitTest` task: use the existing complete defaultDebug JVM suite.
Local unsigned defaultRelease assembly completed, with the expected universal metadata,
Mosaic Release package/version, 16 KB ZIP alignment and absent signature confirmed using
public SDK tools. The exploratory comprehensive Release lint pass finished with 252 errors and
106 warnings (first: generated Seerr ApiClient Files.createTempFile requires API 26
while minSdk is 23).
Full Release lint is NOT a passed check or part of the existing/final CI graph; no
baseline or suppression was added. Its findings need a separate application lint audit. Existing
Full CI and Release assembly/vital validation are preserved. This local dirty-checkout
APK was not a publishable main artifact; hosted signing was then untested and is now
validated by run 34323962085 above.
The final exact task graph (Full Debug compile/tests/assembly plus defaultRelease
assembly and vital lint) subsequently passed: 190 tasks, four executed and 186
up-to-date, including reuse of the 551-test JVM suite. git diff --check passed.
Earlier pending external configuration/
future-only signer statements below are superseded by this checkpoint.

## Mosaic signing infrastructure prepared (2026-09-09)

HISTORICAL PREPARATION: Mosaic identity/versioning was merged on main through PR #13 (`28091249`).
On `chore/mosaic-release-signing`, signing infrastructure is PREPARED, not enabled.
See [MOSAIC_SIGNING](MOSAIC_SIGNING.md) for the signing boundary, exact Environment/
secret names, user-only keytool commands and backup/restore verification.

Gradle no longer decodes upstream signing secrets or reads a local signing override;
Release is explicitly unsigned. Debug signing remains unchanged. The inherited
upstream development/release workflows remain guarded off in our repository. No new
signing job or upload/publisher is enabled. Full CI remains read-only and PR jobs
receive no Release secrets. Main unsigned Release assembly/artifact transport and
trusted isolated signing job activation remain future implementation.

Public-only `scripts/verify_mosaic_apk.py` verifies SDK signature success, the expected
single signer, non-debuggable Mosaic package, allocated version and source record;
it emits an exclusive-create public hash/fingerprint/provenance record. The expected
fingerprint in `scripts/mosaic-signing.json` is pinned to the user-supplied permanent
certificate documented in [MOSAIC_SIGNING](MOSAIC_SIGNING.md#public-custody-checkpoint-2026-09-09).
Verification fails closed for a missing/malformed policy or any different signer. It cannot open a keystore or sign.
Authenticated input provenance, pre/post signing payload checks and durable accepted
record storage must be wired into the future isolated signing job; this verifier is
not a substitute for those trust boundaries. Tests use synthetic public outputs only.

Permanent key: ESTABLISHED, USER-CONTROLLED. The user confirms two independent
encrypted backups and successful restore/hash/certificate/private-key-access checks.
Only the public certificate fingerprint is repository-visible; Codex handled no
private material. Real isolated CI signing is UNTESTED. Environment `mosaic-release-signing` and
MOSAIC_SIGNING_KEY / MOSAIC_KEY_ALIAS / MOSAIC_KEY_PASSWORD /
MOSAIC_KEYSTORE_PASSWORD: PENDING EXTERNAL CONFIGURATION. Updater routing, rolling
develop, stable Release and visual rebranding remain pending. Codex performed no key generation,
key reading, secret upload, Environment/settings changes or APK publication.
No Sync Bot credential is reused. The dedicated custody document is explicitly allowed
by .gitignore; PKCS12/private-key-container ignore coverage was extended.

Validation: the existing Full CI Gradle graph (defaultDebug compile, all 551 JVM
tests and assembly) and defaultRelease manifest processing passed. Repository-wide
pre-commit and explicit hooks for new files passed. Six focused public-verifier
tests passed, including SDK failure, incorrect/multiple signers, package/version,
Debug rejection and incomplete provenance. The full offline Python suite also passed
(42 tests before adding the sixth focused verifier case). Before public fingerprint registration, the unset-fingerprint CLI was also verified
to fail before tool execution/output creation. SDK apksigner help confirmed the documented signing
and verification flags; no signing command was executed. Local documentation link
targets and git diff --check passed. Real permanent-key signing/verification remains
unexercised, as required by the manual-key boundary.

Public-fingerprint checkpoint validation: all seven signing-verifier tests passed,
including the repository policy's exact approved certificate and rejection of a
different/one-digit-altered certificate. Repository-wide pre-commit, explicit new-file
hooks, 43 local documentation links/anchors and git diff --check passed. Earlier
key-creation-pending audit statements below are historical; custody is now established,
while isolated CI signing was then disabled. Signing is now operational as recorded
above; updater routing and rolling/stable publication remain disabled.

## Mosaic technical identity and versions implemented (2026-09-09)

On `chore/downstream-release-identity`, the approved Release ID is now
`io.github.constbogdan.mosaic`, Debug adds `.debug`, and Kotlin namespace remains
`com.github.damontecres.wholphin`. This is technical identity only: display name/icon/
theme, permanent signing, updater routing, rolling develop and stable releases remain
pending. Existing PR #12 runtime evidence below refers to the OLD Debug ID; it is not
runtime validation of this newly identified build. A new Debug installation has fresh data.

The frozen epoch `bc13bf8fdb360c90b44ca0cc85802fa796d3bd08` was verified as current
HEAD/origin/main, the PR #12 merge baseline. `scripts/mosaic_version.py` allocates N
from that epoch's index in HEAD's first-parent chain, with `versionName=1.0.N` and
positive `versionCode=N` for eligible publication. It rejects shallow/missing history,
non-first-parent epochs, overflow and invalid publication context. Upstream merges
add one mainline step; upstream v*/p* tags do not affect allocation. Git replacement
objects are disabled for identity reads. Python 3 and Git are now explicit Gradle
configuration prerequisites, already present in CI/workstation validation tooling.

Ordinary local/PR builds are previews (`PUBLICATION_IDENTITY=false`), not proof of
main publication eligibility. At the epoch N=0, preview uses name 1.0.0/code 1 so this
uncommitted implementation can build; publication rejects N=0. First eligible main
commit has N=1/name 1.0.1/code 1. Feature/PR previews can share codes with future main
builds and must never be promoted. `-PmosaicPublication=true` invokes strict allocation:
clean worktree, canonical GitHub push/main event and exact GITHUB_SHA, N>0. This checks
execution context, not branch protection or CI success; future publishers must verify
those independently. No publisher is implemented/enabled here.

BUILD_TIME now uses HEAD commit time in milliseconds, not wall-clock time. Generated
BuildConfig separately records SOURCE_SHA, UPSTREAM_BASELINE (reviewed integrated anchor,
not a newly fetched upstream tip), SOURCE_DIRTY and PUBLICATION_IDENTITY. A dirty
preview identifies the base commit and explicitly flags modifications. This does not
establish byte-for-byte reproducibility: dependency/toolchain inputs, signing, generated
archives and local native libraries still require provenance and byte verification.

The helper can emit an APK hash record with `--publication --apk <signed-apk>` and
compare an existing immutable record with `--published-record <record.json>`. Any
changed bytes/provenance reject reuse. Tests exercise this guard; future publication
must durably retain/check that record before every upload, including first-publication
races. No release ledger, signed APK, record persistence or publisher is created here.
Same source rebuild retains version identity; it never automatically permits replacing
previously distributed bytes. Changed bytes require a new main commit/version.

Provider authorities already follow applicationId/context.packageName. The exported
playback action now uses `${applicationId}.PLAYBACK`; IntentService accepts the current
BuildConfig.APPLICATION_ID action plus legacy upstream action for explicit compatibility.
Kotlin package imports are preserved. The existing `wholphin:` protocol remains unchanged
for compatibility; implicit URI dispatch can still be ambiguous beside upstream. Scheme
migration/verified links are future integration decisions, not part of the visual rebrand.

The existing universal APK name/directory contract remains
`app/build/outputs/apk/default/debug/Wholphin-default-debug-<versionName>-<versionCode>.apk`.
PR artifact selection uses Gradle metadata and is independent of package ID or old Git
version names. CI no longer fetches upstream version tags; full source history remains
required. CI now includes the focused version allocator fixtures with the existing
offline hosted-safety suite; required Full validation and publication permissions remain.

Validation completed: 9 focused version/history/byte-record tests passed; the existing
28 hosted-upstream tests also passed (combined earlier run: 35 tests, followed by the
expanded 9-test version suite). Final Full Gradle compile, 551 JVM tests, Debug APK
assembly and Release manifest processing passed in 3m 36s after the fixture update.
Merged Release/Debug package IDs, provider/ACRA authorities, playback/fixture actions,
upstream Kotlin namespace, generated source/time fields and actual APK manifest were
inspected. The existing PR artifact selector accepted the new universal APK.
Repository-wide pre-commit passed after its Gradle formatting correction; new Python
files were checked explicitly. Actionlint/YAML, local doc links and git diff --check
passed. No runtime installation, byte-for-byte reproducibility or production-signing
claim is made. Existing codec/deprecation warnings remain. Updater endpoints still
point upstream; Mosaic updater migration must precede a usable Release update channel.

## Downstream Release identity contract proposal (2026-09-09)

**CURRENT:** design checkpoint on `chore/downstream-release-identity` at
`bc13bf8fdb360c90b44ca0cc85802fa796d3bd08`. Existing continuity edits are preserved.
PR #12 -> required Full CI -> exact seven-day Debug artifact -> downloaded ->
installed and run successfully on the Android emulator is live accepted; see
[the exact evidence](#pr-debug-apk-artifacts-2026-09-09). No downstream signed Release,
rolling development Release or stable Release is implemented.

**APPROVED CONTRACT / constraints from the user:** a one-time sideload/reinstall is
acceptable; upstream-signed in-place compatibility is not required. PR Debug remains
separate from Release identity. No Release secrets reach PR or untrusted upstream
code. Build, signing and publication credentials are separated; human release approval
and validated-source provenance remain mandatory. **Mosaic** is now the approved
working downstream product name; the installed application identity is not changed.

**APPROVED AND IMPLEMENTED:** application identity and epoch/first-parent version
allocation, as recorded in the newer checkpoint above. Signing, tag/publication and
updater designs below remain FUTURE IMPLEMENTATION; no release authority follows
from implementing identity/versioning.

### Identity and first installation

**APPROVED:** working product name Mosaic; Release applicationId
`io.github.constbogdan.mosaic`; Debug ID `io.github.constbogdan.mosaic.debug`;
Kotlin packages/namespace `com.github.damontecres.wholphin` remain unchanged.
This supersedes the provisional product-domain proposal; no domain acquisition or
namespace-control condition remains on this user-approved GitHub-based ID. Keep this
technical ID even if the GitHub owner/repository or display branding changes later.
It can technically change before first downstream Release, but after the first
published signed Mosaic Release it is treated as permanent alongside signer continuity.
Changing ID later creates a separate app/data boundary. Display name/icon/theme remain
Wholphin today; full visual Mosaic branding is a separate pending task.

Keeping the upstream ID would marginally reduce build configuration changes, but
would not preserve compatibility with upstream's certificate. It prevents side-by-side
installation and invites updater/signature confusion. With one user, a separate ID
now avoids a second future migration. New ID means separate Android UID/storage,
preferences, databases, permissions and login state. No automatic transfer from
upstream or the current Debug app is promised; sign in/reconfigure, or separately
design an explicit export/import. Do not copy private app data or uninstall automatically.

Implementation inventory confirmed `${applicationId}.provider` and
`${applicationId}.androidx-startup` in the manifest, with updater FileProvider access
based on context.packageName. Those already follow the installed identity. In contrast,
the exported playback action and IntentService use
`com.github.damontecres.wholphin.PLAYBACK`, and the manifest accepts `wholphin:` URIs.
Those are public protocol identifiers, not Kotlin imports. With the approved ID,
provider authorities become `io.github.constbogdan.mosaic.provider` and the corresponding
Debug authority through existing applicationId placeholders. No provider changes are
implemented here. Custom schemes are not globally reserved: prefer explicit package
targeting, and use verified App Links only after domain ownership is established.
Coexisting apps can both
resolve the legacy scheme: future implementation should add downstream action
`io.github.constbogdan.mosaic.PLAYBACK` and scheme `mosaicstream`, generate
package-targeted internal/TV intents, and explicitly decide legacy alias support.
Do not silently remove the legacy integration or globally replace package strings.
Audit TV-provider launch URIs, manifest class resolution, instrumentation, merged
manifests and external clients. WorkManager names are app-scoped; source package
references/generated Seerr API packages need no branding rewrite.

The implemented Debug ID is `io.github.constbogdan.mosaic.debug`, requiring a new
test installation. Fixture broadcast action and operational adb commands follow the
new ID; receiver Kotlin class names remain upstream-compatible. Debug never becomes
a Release update path.
If Play distribution is later added, register the chosen ID and deliberately align
Play app-signing identity with sideload releases; upload-key reset is not sideload
signing-key recovery. No Play ownership/availability is claimed by choosing a string.

### Signing and credential custody

One permanent owner-controlled downstream Release key signs BOTH development and
stable APKs. Record the public certificate and SHA-256 fingerprint in reviewed local
policy and release manifests; verify final APKs against that fingerprint, not merely
that some signature is valid. The prior audit's upstream certificate is evidence only,
not our identity. Do not request upstream private material.

Generate only after approval in a controlled offline/local ceremony. Keep at least
two encrypted backups in independent locations, record alias/format/password recovery
in a password manager, and verify a restore before relying on the key. GitHub is an
execution copy, not the only backup. A future protected `downstream-signing` Environment
can hold `DOWNSTREAM_SIGNING_KEY`, `DOWNSTREAM_KEY_ALIAS`,
`DOWNSTREAM_KEY_PASSWORD`, `DOWNSTREAM_KEY_STORE_PASSWORD`; base64 is encoding, not
encryption. No keystore/password goes into Git, logs, artifacts, caches or PR runs.
Normal local development uses Debug; exceptional local Release signing requires
explicit access to the owned key outside the checkout, never automatic secret import.

Use a secret-free protected-main build job, followed by a trusted isolated signer
running pinned SDK tools only against validated APK bytes. Do not run Gradle, hooks,
repo scripts from the candidate or downloaded executables with the key present. A
separate publisher has no signing key and only repository Contents write. Restrict
signing to successful exact-main candidates and reviewed workflow identity; a branch
name alone is not proof that upstream-derived code is trusted. Review publisher changes
and protect the Environment/workflows. Initially require signing approval; unattended
main signing needs an explicit bounded standing authorization later. Stable promotion
always needs human release approval and need not receive the key again.

Key loss without backup ends same-identity sideload updates. Replacement generally
requires a new app identity or uninstall/reinstall and data migration. Authorized
Android signing lineage/rotation is platform-dependent and requires old-key authority;
do not plan routine rotation or assume compatibility across supported older TVs.
Compromise requires a separate incident/migration decision. Release key, ephemeral
Debug keys and Wholphin Sync Bot credentials remain entirely separate.
[Android signing guidance](https://developer.android.com/studio/publish/app-signing).

### Deterministic versions

| Option | Assessment |
| --- | --- |
| Inherited v*/p* tag count + git describe | Reject: unrelated/imported tags alter codes; multiple builds share codes; upstream names govern ordering. |
| Wall-clock timestamp | Reject as primary identity: clock/rerun ambiguity, bounds and reproducibility concerns. |
| GitHub run number | Workable with one allocator, but workflow recreation/reset and separate stable workflows require state/migration; reruns are execution rather than source identity. |
| Explicit incrementing version file | Deterministic and branch-independent, but needs a reviewed bump for every distributable change and conflict/allocation handling. |
| Anchored protected-main first-parent sequence | Recommend for this main-only publication model: one source position, one code; imported side history/tags cannot inflate or reset it. |

Approved frozen epoch **A = `bc13bf8fdb360c90b44ca0cc85802fa796d3bd08`** (current
post-PR-12 main baseline). For an eligible protected-main commit C strictly after A:

```text
N = git rev-list --first-parent --count A..C
versionCode = N
versionName = 1.0.N
GitHub Release name = v1.0.N
```

Store A and the schema in reviewed downstream version configuration; never recalculate
A from a moving branch/tag. Require full history, A actually on C's first-parent chain,
C a validated protected-main commit, and 1 <= N <= 2100000000. Code 1 is valid for the
new ID; upstream/debug code 58 belongs to other installed IDs. Main history must never
be rewritten or replaced with upstream history. An upstream merge contributes one
mainline step, regardless of imported commits/tags. Gaps from skipped/failed builds
are fine. Feature branches, PR merge refs and maintenance branches cannot independently
allocate distributable Release codes. Hotfixes must integrate into main before release;
parallel independently versioned release branches would require a new allocator design.

Same C means same N across reruns; run ID/attempt is separate evidence. Every NEW
installable payload must have a greater code: publish once per N, record signed APK
hashes, never replace N with different bytes. If dependencies/toolchain/signing output
change, require a new main commit and N; a rerun reuses existing accepted artifacts or
fails if hashes differ. Resolve dynamic dependencies, record dependency/toolchain inputs
and make BUILD_TIME deterministic from source for reproducible rebuild attempts. These
changes improve reproducibility but do not justify claiming byte equality without hashes.

`1.0.N` is a downstream release sequence, not upstream feature SemVer. Its numeric patch
provides strict ordering with the EXISTING Version parser; it does not include channel
or branding text. Record full source SHA, upstream version/anchor and build inputs in
embedded build provenance and the manifest/notes, not an ordering-significant git suffix.
Upstream version changes affect informational provenance only. Any later major/minor
or epoch change must explicitly preserve both versionCode and updater ordering.
[Android version constraints](https://developer.android.com/studio/publish/versioning).

Examples: main candidate N=1 is 1.0.1/code 1; next main N=2 is 1.0.2/code 2.
Promoting candidate 2 to stable retains EXACTLY 1.0.2/code 2 and bytes. This is a channel
promotion, not a new update. Candidate 3 sorts above it in development. A development
user at 3 who selects stable at 2 must wait for stable >=3; never offer a downgrade.
Stable publishes in increasing N relative to prior stable; rolling publishes increasing
N relative to prior rolling. Out-of-order jobs must refuse to move either channel back.

### Tags, rolling release and stable promotion

Canonical repository stays `constbogdan/Wholphin`. Create an immutable
`downstream-build-N` tag at exact C for each accepted signed build, and retain its
manifest/checksums/mapping/unsigned-to-signed identity evidence for recovery/promotion.
No `v*`/`p*` downstream version tag collides with imported upstream tag conventions.
Stable promotion adds immutable `downstream-v1.0.N` at the same C, with Release name
`v1.0.N`, prerelease false, explicit latest marking after approval. Stable never runs
an independent tag-derived build or increments the version on promotion. Verify the
existing immutable build record and target SHA before adding a stable tag.

Keep `develop` as the intentionally mutable development alias and update its existing
prerelease rather than deleting/recreating the release. Name remains `v1.0.N`, prerelease
true, latest false. Reserve immutable build evidence independently of this alias. Upload
and verify uniquely versioned assets before switching updater aliases/metadata, serialize
publication without mid-publication cancellation, and remove obsolete assets only after
success. GitHub tag, release metadata and asset replacement are not one transaction;
keep the previous APK available, record partial state and make retries idempotent. The
future updater must preflight the downloaded package/code/signer against advertised
identity so partial alias updates fail closed rather than install a different build.

Moving `develop` is a destructive tag-ref update and MUST receive a narrowly scoped
exception in the future approved publisher contract; this proposal does not authorize
it today. No force update of main or immutable build/stable tags. If the user rejects
that exception, use immutable development releases plus a channel resolver instead,
which requires a different updater endpoint contract. Do not enable repository release
immutability indiscriminately over the deliberately mutable rolling release. Always
store exact C and hashes in notes/manifest; mutable develop is never source provenance.

### Unified updater and sideload contract

Built-in source configuration has one canonical owner/repository and channel resolver:

```text
stable default: https://api.github.com/repos/constbogdan/Wholphin/releases/latest
development:    https://api.github.com/repos/constbogdan/Wholphin/releases/tags/develop
installed stable notes: /releases/tags/downstream-v1.0.N
```

Main-built and stable-promoted APKs use the SAME stable default so promotion requires
no byte changes. Early testers explicitly select development after sideload. Before
first stable exists, stable checking reports no published stable release, not an
upstream fallback. Preserve editable Update URL; a channel selector is a future UX
option. Migrate only recognized legacy upstream stable/develop defaults when applicable;
preserve arbitrary custom URLs. New-ID installs start fresh, so do not imply old private
preferences migrate automatically.

Remove the architectural split between getLatestRelease and getRelease: both use a
shared ReleaseSource abstraction. For GitHub API overrides, derive the same owner/repo
and downstream tag strategy; arbitrary custom sources must supply a supported installed
notes resolver or report notes unavailable, never silently query upstream. Installed
version notes first request the immutable stable tag for N. If not promoted, only use
rolling notes when they match installed N; otherwise show an immutable source/build
link using embedded C/downstream-build-N, not notes for a newer version. A richer
per-build historical-notes store is optional future work, not necessary for updates.

Retain `Wholphin-release-<ABI>.apk`, `Wholphin-release.apk` and optional legacy
`Wholphin.apk` aliases on both channels; keep current first-supported-ABI/universal
selection initially. Immutable long assets can add N and full SHA. No brand change
should remove old machine aliases before a client migration. Version parsing can stay
unchanged for `1.0.N`, but Gradle version allocation, stable-tag notes lookup, source
routing and defensive package/version/signer verification require implementation/tests.
Null asset/malformed metadata must disable installation with a useful error. Do not
call the current updater production-ready solely because these endpoints are specified.

First install: user downloads the owned Release APK, verifies provenance/fingerprint,
and sideloads; Android asks for installation permission. It can coexist with upstream
and Debug and initially has fresh settings. Future same-ID/same-key updates with
higher N are detected/downloaded and confirmed by Android's installer, preserving
app data subject to deliberate schema migration. No silent install, automatic uninstall
or in-place upstream-signed migration. Stable/development share identity and key;
channel switching never bypasses version monotonicity.

### Build-once, authority and implementation sequence

Main builds the exact candidate once under authoritative CI with required tests plus
release/minification checks, then isolated signing validates APK identity/certificate.
Keep Debug PR CI as independent pre-merge validation. Cache is acceleration, not evidence.
Signed main bytes are reused for development distribution and later stable promotion;
retain APKs and mappings outside expiring PR artifact retention for the support lifetime.
If an old candidate's exact artifact is unavailable, do not rebuild different bytes
under the same published N: recover it or create/validate a new main candidate.
Current Git-derived metadata and BUILD_TIME must be replaced/frozen first, so promotion
is a FUTURE contract, not a property already established by current Gradle.

Prefer GitHub-native GITHUB_TOKEN with Contents write ONLY in the publisher. Separate
protected `downstream-stable-release` approval from signing custody. No PAT or new App
is required for ordinary release asset/tag API writes; if later downstream workflow
triggering genuinely requires an App, design a separate narrowly scoped release App.
Never reuse Wholphin Sync Bot or its key. Protect immutable tag namespaces and the
signing/publishing workflow; retain upstream-only guards on inherited publishers.
Environment protection availability and exact repository rules need read-only review
in the authorized implementation task, not configuration during this design checkpoint.

Future sequence:

1. ID and frozen epoch/name scheme are approved and implemented in the current
   checkpoint. Key custody and bounded develop alias policy still need separate
   authorization before irreversible work.
2. Identity/version allocation and focused history/byte-record tests are implemented.
   Future publisher integration must enforce durable same-code byte records, trusted
   workflow/source identity and channel ordering; optional protocol migration remains
   separate from this compatibility-preserving identity update.
3. Implement common updater routing/notes, preference behavior and package/code/signer
   checks; keep PR artifact validation intact. Test missing stable and malformed assets.
4. Separately authorize key generation, restore verification, public fingerprint
   recording and GitHub Environment secrets/rules. No key creation in this task.
5. Implement trusted main build -> isolated sign -> explicit artifact verification ->
   authorized rolling publisher, including partial-publication recovery and mappings.
6. Authorize first sideload and two successive same-key device updates retaining data;
   verify Debug/upstream coexistence, TV intents, permissions and minified behavior.
7. Enable stable promotion only after human release approval and exact-byte evidence;
   confirm channel ordering. Signing/release ownership and rollback remain explicit.

Validation for this checkpoint: implementation/manifest/workflow reads, prior public
certificate audit, Android/GitHub primary documentation and local Git first-parent
inspection. No build, signing, device install or live release exercise was performed.
Engineering remains read-only. Existing PR #12 acceptance remains the runtime evidence.

## PR Debug APK artifacts (2026-09-09)

**OPERATIONAL + LIVE VALIDATED.** The PR-only success path
in `CI / Full validation` now uploads the exact universal defaultDebug APK already
produced by its existing Gradle validation graph. No rebuild or additional Gradle
invocation, signing/release secret, write permission, tag or Release is introduced.
Push/main and manual runs do not upload test APKs in this implementation.

Live acceptance supplied by the user: [PR #12](https://github.com/constbogdan/Wholphin/pull/12)
ran authoritative Full CI in [run 34284819578](https://github.com/constbogdan/Wholphin/actions/runs/34284819578).
It reused the existing universal defaultDebug APK without an additional Gradle build
and uploaded this seven-day Actions artifact:

```text
wholphin-pr-12-b6792823d870ec62d2255255ece3543752364618-run-34284819578-attempt-1
```

Contained APK: `Wholphin-default-debug-1.0.7-45-g2d198b0f-58.apk`.
The exact artifact was downloaded from GitHub Actions, installed and successfully
run on the Android emulator. A previously installed Debug build caused initial
ambiguity; after removing that old Debug installation and installing the exact PR
artifact, live validation succeeded. This records an emulator acceptance, not a
claim of Android TV device testing or cross-certificate in-place update compatibility.
Do not infer a full tested SHA from the abbreviated hash in the APK filename.
The artifact is expiring evidence; these identities preserve the checkpoint after expiry.

Normal retrieval model:

```text
PR -> required Full CI -> exact CI-produced Debug APK
   -> 7-day GitHub Actions artifact -> optional emulator/Android TV validation
```

```text
PR Debug artifact = OPERATIONAL + LIVE VALIDATED
main rolling development Release = NOT IMPLEMENTED
downstream stable Release = NOT IMPLEMENTED
```

PR Debug artifacts are test builds, separate from the future downstream Release
signing/update identity. Rolling/stable releases remain blocked on a separately
approved application identity, permanent signing key and versioning contract.

Selection reads `app/build/outputs/apk/default/debug/output-metadata.json`, requires
one UNIVERSAL output with no ABI filters, and verifies its APK exists and is nonempty.
The uploaded file is `app/build/outputs/apk/default/debug/<outputFile>`; current naming
is `Wholphin-default-debug-<versionName>-<versionCode>.apk`. Missing/invalid outputs
fail the step instead of silently claiming availability. The upload follows successful
Full validation and retains the APK for seven days with no extra ZIP compression.

Artifact name:
`wholphin-pr-<PR>-<full-head-SHA>-run-<run-ID>-attempt-<run-attempt>`.
Head SHA identifies the proposal; the tested SHA is github.sha, the default PR merge
checkout, and may differ. The job summary records both, PR base SHA, PR number, run
ID/attempt, APK path, retention and Debug installation caveats. Its download link
comes directly from upload-artifact's artifact-url output and requires GitHub access.
Find it through the PR's Full validation check / Actions run summary.

```text
gh run download <run-id> --repo constbogdan/Wholphin --name <artifact-name>
adb install -r "Wholphin-default-debug-<versionName>-<versionCode>.apk"
```

The CLI extracts the single APK into the download directory. Debug uses
`com.github.damontecres.wholphin.debug` and installs separately from Release Wholphin.
Runner/local Debug certificates can differ: replacement may fail; any uninstall and
loss of test-app data requires a deliberate user decision. This is an expiring test
artifact, not an in-app update endpoint or production/minified Release acceptance.

**Future:** main Debug artifact retention would reuse its existing output with only
upload/storage cost, but remains out of scope. Downstream development and stable
releases, signing, updater routing and versioning remain future work. The following
audit retains the detailed rationale; its PR-artifact proposal is now implemented
by this checkpoint, while its release-channel proposals remain unimplemented.

Original local implementation validation (preceding live acceptance): actionlint/YAML passed; inline selection ran against the existing local
Gradle metadata/APK, and fixture checks rejected missing/invalid output. Summary tests
confirmed head/tested SHA distinction and run identity. Static checks preserve the
Full check name, read-only permissions, PR-success gates, seven-day retention and one
Gradle invocation. Repository-wide `pre-commit run --all-files` and
`git diff --check` passed. No APK was rebuilt or uploaded during local verification.

## Downstream APK, signing and updater audit (2026-09-09)

**AUDIT + PROPOSED DESIGN ONLY.** No workflow, application, signing, release,
settings or Engineering changes. Local HEAD is `7385b3ec` on
`chore/apk-artifacts-update-path`; the three existing dirty continuity documents
were preserved. Public upstream main was verified as
`1778bdb34caa699c0590232a7de709a889839765`, matching local `upstream/main`.
The Gradle configuration, updater and version implementation match that upstream
ref. Inherited development/stable publishers differ only by downstream-disable
repository guards. Sources below are implementation evidence, not future capability.

### Exact updater contract

Sources: [UpdateChecker](../app/src/main/java/com/github/damontecres/wholphin/services/UpdateChecker.kt),
[Version](../app/src/main/java/com/github/damontecres/wholphin/util/Version.kt),
[update UI](../app/src/main/java/com/github/damontecres/wholphin/ui/setup/InstallUpdatePage.kt),
[preferences](../app/src/main/java/com/github/damontecres/wholphin/preferences/AppPreference.kt),
[Gradle](../app/build.gradle.kts).

- Default stable endpoint is `https://api.github.com/repos/damontecres/Wholphin/releases/latest`.
  Advanced settings expose a free-text Update URL and automatic-check switch (default
  true). There is no typed stable/development channel model. Development is selected
  by using `https://api.github.com/repos/damontecres/Wholphin/releases/tags/develop`.
  Existing persisted preferences will not automatically change when the default changes.
- The default flavor enables updating; appstore/firetv disable it. Appstore retains
  Discover; firetv disables Discover. Startup and settings can check for updates.
  The 12-hour logic throttles notification toasts, not all network requests.
- The response must be one GitHub Release object. It parses **name**, not tag_name,
  into a Version, plus published_at, body and assets. It does not filter prerelease,
  compare publication time, or validate target_commitish. Release notes render Markdown
  and extract `<!-- app-note:... -->` comments. A valid version can produce a Release
  with a null download URL; the install call force-unwraps that URL, and the install
  page does not disable its button for missing assets or an older/equal version.
- Version accepts exactly optional `v`, three numeric components, optionally
  `-<count>-g<alphanumeric hash>`. Branded titles, `-beta`, `+metadata` and arbitrary
  SemVer prereleases do not parse. Ordering compares major/minor/patch then commit
  count (missing means zero); hash and Android versionCode are not ordering inputs.
  Two different hashes at the same count are not newer. A same-base stable version
  is not newer than its positive-count development version. Data-class equality
  includes the hash, so isLessThan has an additional same-order/different-hash edge.
- Selection checks only the first supported ABI, then universal fallbacks. Debug:
  `Wholphin-debug-<ABI>.apk`, then `Wholphin-debug.apk`. Release:
  `Wholphin-release-<ABI>.apk`, then `Wholphin-release.apk`, then `Wholphin.apk`.
  Only browser_download_url is used. Versioned filenames alone do not work.
  Upstream stable's `Wholphin-<ABI>.apk` aliases are not selected: it falls back to
  `Wholphin.apk`. No second supported ABI is attempted. Debug has no release fallback.
- Installed-version release notes separately hard-code upstream
  `/releases/tags/v<major>.<minor>.<patch>` in getRelease(), ignoring the configured
  Update URL and development suffix. Changing the preference alone does not reroute
  this lookup.
- Download uses OkHttp, progress callbacks and a fixed `Wholphin.apk` Downloads name.
  Android Q+ uses MediaStore, with a file fallback; older versions use public Downloads
  and storage permissions. Installation launches the OS installer via a content URI
  and ACTION_INSTALL_PACKAGE (legacy pre-N ACTION_VIEW path also exists). FileProvider
  authority uses the installed package ID. The manifest requests package installation;
  the OS/user handles unknown-source permission and confirmation. No silent install,
  explicit installation-result tracking, or rollback is implemented here.
- The updater performs no APK checksum/digest verification, expected-certificate pin,
  package/version preflight or asset-origin allowlist. Android's installer supplies
  signature compatibility enforcement; HTTPS is not a downstream signer check.
  Failed downloads surface errors; cancellation cancels the coroutine, not an explicit
  OkHttp Call.cancel. Cleanup deletes matching Wholphin APK download entries.

### Upstream release and build contract

Sources: [development workflow](../.github/workflows/main.yml),
[stable workflow](../.github/workflows/release.yml), [CI](../.github/workflows/ci.yml),
[setup](../.github/actions/setup/action.yml). Public releases inspected:
[stable v1.0.7](https://github.com/damontecres/Wholphin/releases/tag/v1.0.7),
[rolling develop](https://github.com/damontecres/Wholphin/releases/tag/develop).

Development triggers on main and develop/* pushes upstream. Full-history checkout
feeds git describe. Main maps to release tag `develop`; develop/* replaces the first
slash with a dash. Release title is `git describe --tags --match 'v*' --long`;
latest stable comparison uses the nearest matching tag. It builds
`clean assembleDefaultRelease assembleDefaultDebug`, verifies all APK signatures,
copies short aliases alongside long filenames, prints SHA256 checksums to logs,
uploads mapping.txt as an Actions artifact, then deletes the old rolling release/tag
and recreates a prerelease with `--latest=false`. It targets a mutable branch name,
not an explicitly captured commit. Cancellation is enabled; delete/recreate and
branch movement leave avoidable publication races. Notes point to upstream stable,
the API development endpoint and a GitHub comparison. This workflow has no Full
unit-test gate of its own.

Stable triggers on pushed `v*` tags. It runs
`clean bundleAppstoreRelease bundleFiretvRelease`, then `assembleDefaultRelease`.
It verifies APK signatures (not the AABs), prints APK/AAB hashes, uploads AAB and
mapping Actions artifacts, and creates a draft GitHub release with `--latest`,
`--verify-tag`, title equal to the tag and initially empty notes. A human must publish
the draft. The workflow consumes tags; it does not choose/increment a semantic version.
There is no automated store upload in these workflows.

Gradle versionName is `git describe --tags --long --match=v*`, without leading v.
versionCode is the number of locally present `v*` and `p*` tags, not reachable commits
or published builds. Stable v1.0.7 and current develop both have code 58, despite
names `1.0.7-0-g2b9af1e8` and `1.0.7-11-g1778bdb3`. Additional/unrelated tags or
incomplete tag inventory can change the same source's versionCode. BUILD_TIME uses
wall-clock time, so rebuilding identical source is not byte-identical by assumption.

Default APK outputs are universal plus armeabi-v7a, arm64-v8a and x86_64, named
`Wholphin-default-<debug|release>-<versionName>-<versionCode>[-<ABI>].apk`.
Universal has no ABI suffix. ABI splitting is disabled when task names contain bundle;
thus stable deliberately uses a second assemble invocation. Release is minified,
resource-shrunk and non-debuggable; Debug is unminified/debuggable with `.debug` ID.
Optional local/prebuilt ffmpeg, AV1 and mpv dependencies depend on local AARs or
Extensions credentials. Current downstream CI supplies neither upstream Extensions
credentials nor those ignored local AARs; device feature parity cannot be inferred
from the same Gradle task name.

Public releases contain long names and short aliases with identical corresponding
hashes. Workflow SHA256 output is log-only; no checksum manifest is uploaded by the
source workflows. GitHub asset metadata now includes digest values, but the updater
ignores them. Mapping artifacts are workflow artifacts, not GitHub Release assets;
retention is unspecified (repository default), so durable crash-symbol retention is
not established. apksigner verify proves APK integrity, not comparison to a pinned
expected identity. Although CI enables v4 signing, downloaded APK verification without
an idsig does not prove v4; no idsig release-upload contract exists.

### Signing evidence and compatibility

Public APKs were downloaded to the OS temporary audit directory and inspected with
Android build-tools 36.0.0 apksigner/aapt, never executed or installed. Hashes matched
GitHub's advertised digests. No upstream private material was requested or accessed.

| Sample | Public certificate SHA-256 | APK SHA-256 |
| --- | --- | --- |
| v1.0.7 arm64 Release | `e54fda99b452214b3522deb5de14e2dddc06da8de5db1fa7591dce2d80af96a8` | `f13b23577f79d530e5f4a5e56a85b96f91b06c155fb6d4ccc638bf688a9fa39e` |
| develop arm64 Release at 1778bdb3 | `e54fda99b452214b3522deb5de14e2dddc06da8de5db1fa7591dce2d80af96a8` | `00588f7d3b234980ba836365580c8608206c2bc1bd07c98d4adc470620ac3a5b` |
| develop arm64 Debug at 1778bdb3 | `9c7d7b1faf5527a6141d21598e4f35fe799f81e1c0a07a62e4be4297c0a3c040` | `e716249f41e6de770db836aeb9dc330555dd0916597e1a7130c6ec185ef32e73` |

Release certificate DN is `C=US, O=Wholphine, OU=com.github.damontecres, CN=Damontecres`.
The sampled Release APKs verify v1/v2/v3. Debug verifies v1/v2 and uses Android Debug
DN. These establish the sampled GitHub APK identity, not every historic or store APK;
Play app-signing/distribution certificates were not inspected.

Application ID and namespace are `com.github.damontecres.wholphin`; Debug ID is
`com.github.damontecres.wholphin.debug`. The existing local arm64 Debug APK at
`1.0.7-41-g6b1fc54b`, code 58, uses Android Debug certificate SHA-256
`df7df2092bbe09d236045c224c4a8007c7d01e3d56a6626af1eac2eb2eec1e6d` (v1/v2).
This is an older local output, not proof of a build at current HEAD. No local release
signing override was found. Release is unsigned without CI signing or an explicit
local signing-config override. CI signing requires CI=true and nonblank KEY_ALIAS;
SIGNING_KEY is a base64 keystore decoded to app/ci.keystore, with KEY_PASSWORD and
KEY_STORE_PASSWORD. Debug never selects that release signing config.

Our current CI builds defaultDebug with the runner's default debug key. It neither
imports nor persists a designated debug key, and retains no success APK, so its exact
historic certificate is unavailable from this workflow contract. Do not assume
compatibility between runner instances, local Debug or upstream Debug. Read-only
repository secret-name inventory contained only SYNC_BOT_PRIVATE_KEY; the release
list was empty. No environment-secret inventory or private values were inspected.

Android requires the same application ID and compatible signing identity for an
in-place update, with downgrade constraints on versionCode. An independently
created downstream key cannot replace an upstream-signed installation of the same
ID: installation is rejected, typically UPDATE_INCOMPATIBLE. Changing URL/name/code
cannot bypass this. Supported signing-key rotation requires an authorized lineage;
it is not a workaround when the original signing authority is unavailable.
Uninstall/reinstall loses app-local data unless separately exported/restored. A new
ID installs alongside upstream with separate data. Debug and Release currently
coexist rather than update each other because their IDs differ, regardless of keys.
A label/icon rebrand need not change ID or certificate; changing ID creates a new app.
See [Android update rules](https://developer.android.com/google/play/app-updates),
[signing](https://developer.android.com/studio/publish/app-signing) and
[versioning](https://developer.android.com/studio/publish/versioning).

### Recommended channels and artifact contract (not implemented)

The proposed PR/main/stable model is appropriate, with release authorization and
signing separated from untrusted PR execution. No permanent develop branch is needed.

| Channel | Proposed output and authority |
| --- | --- |
| PR | Required Full CI's exact defaultDebug universal APK; optional arm64/armeabi splits for download size and x86_64 for emulator work. Seven-day Actions artifact, no Release or production signing secret. |
| main | Exact validated main SHA, defaultRelease build, persistent downstream release certificate, rolling downstream `develop` prerelease. Initially also retain main Debug as a short-lived artifact, not an updater promise. |
| stable | Explicitly approved versioned signed defaultRelease, latest stable GitHub Release, same downstream ID/key as main for channel switching. Store bundles and signing ownership are separately deferred. |

PR artifact container: `wholphin-pr-<PR>-default-debug-<full-build-SHA>-<run-attempt>`;
main test container: `wholphin-main-default-debug-<full-SHA>-<run-attempt>`.
Use the actual built SHA (PR CI normally builds a synthetic merge SHA); record PR
head/base as additional metadata. Keep Gradle APK filenames inside, plus a manifest
of source/tree, run ID/attempt, variant, application ID, versions, dependency/toolchain
identity, APK SHA256 and signer fingerprint. A signed manifest/provenance can be a
later hardening step; never call an unauthenticated checksum proof of authorship.

Download the named artifact from the successful run, e.g.
`gh run download <run-id> --repo constbogdan/Wholphin --name <exact-artifact-name> --dir <destination>`.
Compare its APK hash/identity with the run evidence, then use the TV installer or
`adb install -r <exact-apk>`. Signature mismatch requires an explicit test-app
reinstall/data decision, never automatic uninstall. Actions artifacts require an
appropriate GitHub session and expire; they are not release URLs for the in-app updater.
Debug is appropriate for functional/focus/navigation testing, but not sufficient
for minification, production performance or release-signing acceptance. Keep PR
keys disposable initially; never expose a persistent production key to PR code.

Public downstream API sources should be `/repos/constbogdan/Wholphin/releases/latest`
and `/repos/constbogdan/Wholphin/releases/tags/develop`. Preserve machine-compatible
`Wholphin-release-<ABI>.apk` and `Wholphin-release.apk` aliases on BOTH channels;
optionally keep `Wholphin.apk` for old release clients. Long asset names should carry
variant, version/code and SHA. Do not promise Debug updater support without a deliberate
persistent non-production signing identity. Release **name** must remain parser-compatible
until the parser changes; put branding/channel prose in the body, not the title.
Include exact SHA, CI run, upstream baseline, changes, known issues, signer/hash
manifest and installation compatibility in release notes. Retain mapping by exact
release SHA/build for at least the distributed binary's support lifetime, not default
short Actions retention. Publish checksums for all final signed APKs and aliases.

### Build-once design and downstream-specific work

Today PR and main each run Full Debug; inherited development/stable jobs are skipped
on our repository. There is no third downstream build today. Enabling the old main
publisher would add clean Debug+Release builds after main CI, without a dependency
on its success. compileDefaultDebugKotlin/test/assemble in one Gradle invocation
share the task graph; these are not three independent compilation builds.

Keep PR and actual-main validation initially: synthetic PR merge SHA versus committed
main SHA, changing tags, BUILD_TIME and dependencies prevent assuming equivalence.
Eliminate the independent development rebuild first. One main build/validation graph
should produce Debug test artifacts and the unsigned Release candidate once, with
release-specific checks. A trusted signing stage can sign the exact unsigned payload
without recompiling; the publication stage consumes the resulting verified artifact.
Validate final signed manifest, expected certificate, APK integrity and install/upgrade
behavior. Passing Debug unit tests alone is not a minified Release runtime guarantee.

Prefer jobs in one guarded workflow/run. If workflow_run is introduced, require success,
canonical repository, push/main event, exact head SHA, trusted workflow identity and
run-specific artifacts; never publish PR artifacts or execute downloaded scripts in
privileged jobs. Separate build (read), signing (key only) and publishing (Contents
write only). No production secret in PR runs or checkout hooks/Gradle execution during
signing. No release capability is added to Wholphin Sync Bot.

Stable can promote already signed validated bytes only if the APK's embedded version,
ID, dependencies and SHA already meet the stable contract. Retitling a development
APK does not change its embedded version. If version inputs/source differ, build and
validate a new release candidate; do not relabel it as reuse. Preserve immutable
build manifests/artifact identity. Cache dependencies, not trust decisions; remove
routine clean from the unified graph after measuring. Never skip actual-main checks
based solely on matching source trees, which omit Git-derived/version/time inputs.

Before production publishing, choose a permanent downstream-owned application ID
(recommended for side-by-side upstream installs) and release key, with secure backup.
This decision is needed before the first durable downstream install, not a request
for rebranding now. Keeping the current ID is possible but demands explicit upstream
uninstall/migration and cannot preserve upstream signing compatibility. Namespace,
labels and asset aliases can remain stable independently of a future product name.
Centralize canonical repository/channel endpoints and release-note lookup; migrate
only known legacy/default preferences deliberately, preserve custom URLs, and test
migration. A future typed channel setting can retain advanced URL override. Keep old
machine asset aliases through a documented updater transition.

Replace tag-count versionCode and upstream-tag-derived downstream ordering before
rolling publication. Use one bounded, monotonic downstream build sequence across
main/stable, with retries reusing the same immutable build identity and every new
installable build exceeding the prior code. A single canonical workflow counter with
a documented offset/reset migration is one implementation option; independent workflow
run counters are not safe. Persist assigned version inputs in build evidence. Until
parser changes, use compatible numeric names and ensure stable sorts above prior
development names (same-base stable would not). Downstream stable tags should occupy
a separate namespace, e.g. `downstream-vX.Y.Z`; changing tag patterns requires explicit
Gradle/version and installed-notes lookup changes. Do not import upstream v*/p* tags
into the downstream version namespace. An explicit version manifest is preferable to
implicit tag inventory; test channel switching and downgrade behavior before rollout.

### Required setup, reuse, blockers and implementation sequence

No release credentials are configured by this audit. Future setup: persistent
downstream keystore/alias/passwords (the existing SIGNING_KEY, KEY_ALIAS, KEY_PASSWORD,
KEY_STORE_PASSWORD interface can be reused or deliberately renamed); protected signing
and stable-release environment/approval; expected public fingerprint in reviewed config;
canonical repository/IDs/URLs; bounded downstream tag/release authority and retention.
Use the ordinary job GITHUB_TOKEN with Contents write only in publication, not a PAT
or the sync App. No Actions/workflows/admin permission is inherently needed for release
upload. Optional private Extensions access is a separate dependency decision, not an
upstream credential entitlement. Preserve inherited upstream-only publisher guards;
add a separate downstream-owned guarded path instead of simply removing them.

Reusable: SDK/setup versions, Gradle flavors and ABI generation, defaultRelease
optimization, OS installer transport/progress UI, parser and machine aliases under
the stated constraints, PR Full check, signature verification tooling and mapping
production. Needs downstream ownership: key/ID, endpoint/default preference migration,
installed-release notes lookup, version allocation/tag patterns, release authorization,
exact-SHA artifact promotion, expected-signer/hash verification, release notes,
retention and optional media dependency inputs. Broad checksum/manifest improvements
need corresponding updater tests if the app will enforce them.

Concrete sequence (all implementation remains unapproved in this audit):

1. Add seven-day success artifacts to existing Full CI without additional builds or
   secrets; manifest the actual built SHA and document Debug install limitations.
2. Approve permanent application ID/key custody and a downstream version/channel
   contract; decide optional codec dependencies. Keep main publication disabled meanwhile.
3. Implement endpoint/notes/preference migration and version allocation with regression
   tests for parsing, missing assets, ABI fallback, ordering, reruns and channel switches.
4. Add main Release build/checks to the authoritative graph, isolated signing and
   exact-artifact downstream rolling publication. Pin signer, verify final hashes,
   preserve mapping and guard against stale/out-of-order publishers. Do not cancel a
   publication halfway through or delete the current usable release before replacement
   assets have been prepared/verified; design recovery and immutable build evidence.
5. Perform separately authorized Android TV tests: clean install, successive same-key
   update retaining data, expected mismatch rejection, permissions, failed/null download,
   minified release behavior and stable/development transitions. Never infer these from
   this read-only audit.
6. Add separately approved stable promotion/versioned-release mechanics only after
   those gates. Preserve human merge/release approval and later rollback work.

Blockers for rolling/stable publishing: no downstream key/identity decision, current
upstream endpoints, unsafe version allocation, no validated Release artifact promotion,
no demonstrated persistent Debug identity, missing production install/migration tests,
and unresolved optional-codec parity. None blocks retaining existing PR Debug output.
Existing TestUpdateChecker covers five develop asset-selection cases; VersionCompareTests
covers ordinary ordering/string cases. Neither proves download/install/signature,
channel migration, malformed metadata or downstream version correctness. Tests were
read, not rerun; no Gradle build or device installation was performed. Public APK
integrity/certificate inspection and doc whitespace/link checks are this audit's
validation. See [GitHub artifact semantics](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts)
and [apksigner](https://developer.android.com/tools/apksigner).

## Hosted upstream synchronization v1: historical implementation

Implemented 2026-09-08 on initially clean `chore/upstream-detection`, based on
`6b1fc54b`. The original implementation task changed workflow/helper/tests and continuity only. No application
code, real sync branch/PR, commit, push, merge, App, secret or setting was created.

**V1 IMPLEMENTATION AT THAT CHECKPOINT:** `upstream-sync.yml` observed official/main and downstream/main
daily at 06:23 UTC or on manual dispatch, with isolated normal integration and full-SHA
pair branches. Its read job and publication job independently inspect current refs;
publication fails on drift. It preserves older open PRs and human-modified branches,
does not reopen an exact closed pair, and records actionable blocks in GitHub issues.
The normal PR CI owns Full validation; the hosted candidate path never runs workstation
`validate-local.ps1`. The existing manual recovery path retains Standard then Full.

**V1 OPERATIONAL CHECKPOINT (2026-09-09, user-reported live evidence):**
`.github/workflows/upstream-sync.yml` is merged on `main`. Wholphin is the first
live implementation of GitHub-owned hosted upstream detection.

```yaml
Detection: OPERATIONAL
Hosted sync candidate/PR publication: IMPLEMENTED + OFFLINE TESTED
Live publication path: AWAITING FIRST REAL UPSTREAM DELTA
```

The first manual hosted smoke test succeeded:
[run 34281315948](https://github.com/constbogdan/Wholphin/actions/runs/34281315948).
Upstream SHA: `1778bdb34caa699c0590232a7de709a889839765`.
Downstream SHA: `7385b3ecb59908676ab38611527f45f72268fe9a`.
Ancestry validation succeeded, outcome was `no_delta`, and incoming commits were
`0`. No branch or PR was needed. This proves the live detection/no-change path,
not App-token branch/PR publication or its PR CI handoff. Those await a genuine
upstream delta; do not manufacture one for testing.

**Wholphin Sync Bot** is installed only on `constbogdan/Wholphin`, with Contents
read/write, Pull requests read/write and Metadata read. Repository variable
`SYNC_BOT_CLIENT_ID` and secret `SYNC_BOT_PRIVATE_KEY` are configured externally.
The pinned official token action v3 uses `client-id`, exact repository scope and
only Contents/PR write. Read/blocked-issue subprocesses exclude the App token;
only explicit branch push/PR creation uses it. The no-delta run does not mint it.
See [publication acceptance](UPSTREAM_SYNC.md#least-privilege-and-activation-prerequisites).

Local workstation validation is not part of the normal hosted sync path. GitHub
PR CI remains authoritative for candidate validation; semantic review and human
merge/reject remain required. GitHub owns deterministic execution; Repo Intelligence
owns discovery/history/analysis and stays outside the control path. Optional
asynchronous consumption of observations remains future work.

The following implementation and wiring results are historical evidence, preceding
the successful live detection checkpoint. This documentation-only update performs
no dispatch, publication, settings change or new product validation.

Wiring validation on 2026-09-09: **28 offline tests passed** in 116.875s,
including operation-scoped GitHub subprocess credentials. Actionlint 1.7.12,
YAML/input/scope/exposure assertions, Python syntax and local Markdown destinations
passed. `pre-commit run --all-files`, explicit checks covering the new untracked
files, and `git diff --check` passed. Read-only GitHub name listings confirmed
`SYNC_BOT_CLIENT_ID` and `SYNC_BOT_PRIVATE_KEY`; no credential values were read.
The pinned action manifest was checked for `client-id` support. These checks do
not prove live App authentication or PR CI triggering.

The App token grants only Contents/PR write on this repository and is supplied only
to explicit push/PR creation. A separate repository token owns read queries and
Issues-write blocked records. Both candidate checkouts disable hooks/global config
and run no upstream application/build code. Changes to `.github/` or the hosted helper
stop for manual automation review, preserving publishers and avoiding workflow-write
permission. Required CI now also runs the offline hosted-helper safety suite.

Non-obvious recovery boundaries:

- The initial reviewed upstream anchor is `1778bdb34caa699c0590232a7de709a889839765`.
  Published branch refs (including interrupted push-before-PR attempts), PR head refs
  and validated blocked-observation markers supply later anchors.
  Rewrites, missing ancestry, and ambiguous merge bases fail closed. A rejected
  rewrite must not become a trusted anchor. There is no automatic anchor reset.
- Candidate commit identity is deterministic from the normal merge tree, exact
  parents, fixed message/author and parent-derived timestamp. This lets a retry after
  push/PR API failure reuse its branch. Changed human content is preserved, never forced.
- One older open sync PR blocks newer proposals. Closing an exact pair is respected;
  rejecting one patch forever across newer pairs is not represented by v1.
- Blocked issues are deduplicated by pair/reason, retained even after closing, and
  never auto-closed. Full JSON artifacts supplement durable identities/reasons rather
  than owning them. If issue recording is unavailable, the run stays failed and asks
  for manual preservation; no implementation can guarantee API writes during outage.
- GitHub main/PR/ref checks are not one atomic transaction. Final checks reduce drift;
  later base movement still requires current PR CI and semantic review. No force,
  auto-merge, branch deletion, callback, dispatch or Repo Intelligence dependency exists.

**FUTURE RI ENRICHMENT:** a read-only consumer can ingest versioned observation/outcome
JSON, exact identities, ranges, paths, time/run links, outcome and PR/issue URLs.
It remains optional and outside the control path. Engineering's saved architecture
review supplies rationale; repository-local upstream policy owns this implementation.

Validation performed for this implementation:

- **27 offline unittest scenarios passed** in 102.285s using disposable Git
  repositories and mocked GitHub interactions. Coverage includes no delta, accepted
  ancestry, normal/divergent integration, conflict, remote identity, rewrites,
  orphan publication anchors, SHA/commit deduplication, existing/closed/older PRs,
  human-modified heads/branches, failed push/PR recovery, missing credentials,
  credential isolation, escaped PR metadata and durable blocked records.
- **actionlint 1.7.12 passed** for both changed workflows (shellcheck/pyflakes
  integrations disabled; Python syntax checked separately with `ast.parse`).
  All workflow YAML parsed; trigger, permission, required-CI name/path and inherited
  publisher-guard contracts were inspected deterministically.
- **`pre-commit run --all-files` passed**, including KTLint. Sandbox access to its
  existing cache initially failed; rerunning with that cache accessible passed.
  Explicit scoped pre-commit checks also include new/untracked helper/test/workflow
  files, which the tracked-inventory all-files command does not cover.
- Local Markdown destinations/new hosted anchors and normal repository
  **`git diff --check` passed**. An exploratory check with `core.autocrlf=false`
  misinterpreted existing Windows CRLF content; use the repository's normal Git
  line-ending configuration, not an override. No line-ending migration was made.
- Application code, inherited publisher YAML and the manual sync helper were
  unchanged. Index remained unstaged and HEAD stayed `6b1fc54b`.

No Gradle/workstation validation, real publication, App configuration or live
required-CI run was performed. The local fixture suite and static workflow checks
establish implementation behavior, not deployed Actions behavior.

## Historical workflow continuity before hosted v1

Audited 2026-09-08.

**CURRENT:** Autonomous PR handoff v2 is implemented, validated, dogfooded and integrated on `main`. Authenticated `gh` created [PR #9](https://github.com/constbogdan/Wholphin/pull/9) from `chore/prepare-pr-v2`; GitHub reports it merged at `2026-09-08T18:17:22Z`, with merge commit `c10c234360c75e8d08a5489b10ece5b01c634164`. The implementation branch tip is `e59ef6fe` (following `d1635423`). V1 previously merged through PR #8.

This documentation audit began on clean `docs/workflow-continuity` at `c10c2343`, also the locally recorded `main` and `origin/main`, with no active Git operation. These are audit-time observations; inspect the repository again next session. Repository-local documents are authoritative; the older sibling `C:\Projects\Wholphin\docs` copies are not the operating source.

Read [AGENTS.md](AGENTS.md) for permanent rules, [PREPARE_PR.md](PREPARE_PR.md) for current publication behavior, [UPSTREAM_SYNC.md](UPSTREAM_SYNC.md) for semantic integration policy, and [the roadmap](Wholphin_ROADMAP.md#downstream-repository-maintenance-standardization) for ordered milestones. Ordinary publication has two human decisions: explicit authorization to publish, then review of the completed PR and merge/reject. After authorization, the normal successful audit/validation/stage/commit/push/PR path is autonomous; implementation completion alone never authorizes it.

### Evidence and limits

- The user reported successful Full local validation in `00:03:06.9035470` during v2 work. That earlier run's complete log is no longer the current saved log; preserve it as supplied evidence, not a freshly reproduced measurement.
- The saved `validation.log` inspected for this audit records a later successful Full run in `00:04:41.7049780`, completed at `2026-09-08T21:10:40+03:00`: repository-wide pre-commit, production compile, complete default-debug JVM tests, APK assembly and whitespace checks passed.
- The saved `prepare-pr.log` records automatic Full selection without filters, unchanged validated/staged snapshot `b80acea4bce6c9b8912f0a40a97293e960f2c6435b7268db17bfc8bcfbeccada`, committed tree `a12ceee0d635145ce2ffb34e7e2fb263f0b6f384`, commit `e59ef6fe`, and PR #9 creation at `2026-09-08T21:10:52+03:00`. These ignored logs are replaced by subsequent invocations; this record preserves their material evidence.
- A read-only authenticated `gh` query confirmed PR #9 merged and its [Full validation check passed in 6m11s](https://github.com/constbogdan/Wholphin/actions/runs/34261503421/job/102180313528). The `main` rules API confirmed required PR integration, blocked deletion/non-fast-forward updates and required check context `Full validation` (the job in workflow `CI`, documented as `CI / Full validation`). Human merge/reject is operating policy; the ruleset requires zero formal approving reviews.
- Tracked CI performs repository-wide pre-commit and the same Full compile/test/assembly graph as local validation; only failure test diagnostics are uploaded today. Both inherited development and stable publishers are canonical-upstream gated. Successful PR/main APK retention, upstream detection, security/review adoption and downstream releases remain unimplemented milestones.

**APPROVED NEXT:** P1 GitHub upstream detection/safe sync PRs, PR/main debug APK retention, CI performance profiling and simple rollback/recovery policy. **FUTURE:** P2 established security/dependency/review tooling and lightweight-change validation; P3 release ownership and downstream portability; specialized semantic agents later. Keep prepare-pr thin and use GitHub for unattended repository state. Seerr standardization remains deferred pending deliberate `origin/develop` versus `upstream/develop` reconciliation; the five-commit gap below is historical audit evidence, not a fresh Seerr measurement.

One implementation boundary matters for sync recovery: prepare-pr refuses active merges. Resolve semantically, stage resolved files, run Standard then Full and complete the local merge first; only then use explicitly authorized prepare-pr publication. Do not interpret the sync helper's local merge commit as authority to push.

## Historical implementation and investigation record

The following snapshots preserve discoveries, rejected approaches and prior validation. Old branch/worktree inventories, sandbox limitations and statements such as "current" or "now" describe their checkpoint, not today's workspace. The current continuity section and linked policy documents supersede old operating instructions. Existing legacy text-encoding damage is preserved rather than attempting an unrelated bulk rewrite.

1. Workspace and sandbox warning
The real ecosystem workspace is:
C:\Projects\Wholphin\
├── Wholphin\
├── seerr\
├── Sonarr\
├── Radarr\
├── jellyfin\
├── qBittorrent\
├── sabnzbd\
└── docs\
The primary application repository is:
C:\Projects\Wholphin\Wholphin
This Codex session still advertises P:\Wholphin as its writable root. That path is obsolete and invalid. Commands using it fail with Windows error 267.
The repositories under C:\Projects\Wholphin are readable through sandbox escalation, but the stale sandbox configuration makes continued editing unreliable. Start the new session with C:\Projects\Wholphin or C:\Projects\Wholphin\Wholphin as its actual workspace root.
Do not recreate or use P:\Wholphin.
2. Product and architectural direction
Read these first:
- [AGENTS.md](AGENTS.md)
- [Wholphin_ROADMAP.md](Wholphin_ROADMAP.md)
The central product direction is that Wholphin should behave like one integrated media application. Jellyfin, Seerr, acquisition tracking, Discover, Downloads, Watchlist, Collections, and future suggestions should not become isolated feature silos.
State that will eventually need to be reusable across multiple surfaces includes:
- Local/Jellyfin availability.
- Partial availability.
- Persistent library integrity or “Incomplete” state.
- Seerr request and approval state.
- Acquisition state.
- Jellyfin readiness/playability.
- Watchlist membership.
- Collections and franchise relationships.
- Quality-upgrade state.
Two boundaries are especially important:
1. Acquisition lifecycle and library integrity are different dimensions.
2. Seerr availability and Jellyfin playability are not equivalent.
The extended Seerr experience must remain optional. Ordinary Jellyfin browsing and playback must remain usable when Seerr is absent, disconnected, or disabled.
3. Repository inventory
Wholphin
Path:
C:\Projects\Wholphin\Wholphin
Branch:
feature/seerr-download-status
HEAD:
6d664dc1 Merge pull request #1 from constbogdan/feature/seerr-missing-seasons
main, origin/main, and origin/feature/seerr-download-status currently point to the same commit. The acquisition/Downloads implementation is primarily uncommitted working-tree work.
Current tracked modifications
M app/src/main/java/com/github/damontecres/wholphin/MainActivity.kt
M app/src/main/java/com/github/damontecres/wholphin/data/AppDatabase.kt
M app/src/main/java/com/github/damontecres/wholphin/services/SeerrService.kt
M app/src/main/java/com/github/damontecres/wholphin/services/hilt/DatabaseModule.kt
M app/src/main/java/com/github/damontecres/wholphin/ui/detail/discover/DiscoverMovieViewModel.kt
M app/src/main/java/com/github/damontecres/wholphin/ui/detail/discover/DiscoverSeriesViewModel.kt
M app/src/main/java/com/github/damontecres/wholphin/ui/detail/series/SeriesViewModel.kt
M app/src/main/java/com/github/damontecres/wholphin/ui/nav/Destination.kt
M app/src/main/java/com/github/damontecres/wholphin/ui/nav/DestinationContent.kt
M app/src/main/java/com/github/damontecres/wholphin/ui/nav/NavDrawer.kt
M app/src/main/res/values/strings.xml
M app/src/main/seerr/seerr-api.yml
Current untracked files
app/src/main/java/com/github/damontecres/wholphin/data/SeasonIntegrityDao.kt
app/src/main/java/com/github/damontecres/wholphin/data/model/DownloadsMembership.kt
app/src/main/java/com/github/damontecres/wholphin/data/model/SeasonIntegrity.kt
app/src/main/java/com/github/damontecres/wholphin/data/model/SeerrAcquisition.kt
app/src/main/java/com/github/damontecres/wholphin/data/model/TvAcquisitionProjection.kt
app/src/main/java/com/github/damontecres/wholphin/services/JellyfinAcquisitionReadinessService.kt
app/src/main/java/com/github/damontecres/wholphin/services/SeasonIntegrityService.kt
app/src/main/java/com/github/damontecres/wholphin/services/SeerrAcquisitionLedger.kt
app/src/main/java/com/github/damontecres/wholphin/services/SeerrAcquisitionTracker.kt
app/src/main/java/com/github/damontecres/wholphin/services/SeerrRequestPagination.kt
app/src/main/java/com/github/damontecres/wholphin/ui/downloads/DownloadsPage.kt
app/src/test/java/com/github/damontecres/wholphin/data/model/SeerrAcquisitionTest.kt
app/src/test/java/com/github/damontecres/wholphin/services/SeerrAcquisitionTrackerTest.kt
app/src/test/java/com/github/damontecres/wholphin/services/SeerrRequestPaginationTest.kt
app/src/test/java/com/github/damontecres/wholphin/ui/downloads/DownloadsPageTest.kt
There are no staged changes.
These changes are intentional feature work. Do not reset, clean, stash, or delete any of them.
The tracked diff currently reports roughly 349 insertions and 13 deletions, but that excludes all untracked acquisition and Downloads files.
Seerr
Path:
C:\Projects\Wholphin\seerr
Current branch:
pr-1055-current
The tree is clean.
Relevant local commits:
f10fc38f feat: configure Servarr download queue size
a4455f9f fix: enforce Servarr command polling deadline
09504031 fix: improve Servarr download queue syncing
49d17e31 Updated queue pageSize to get more than 10 downloading items in Sonarr/Radarr
This is no longer merely an uncommitted fix/servarr-download-queue-sync tree. The work is committed locally on pr-1055-current.
Important modified-by-feature files:
- server/api/servarr/base.ts
- server/api/servarr/base.test.ts
- server/lib/downloadtracker.ts
- server/lib/downloadtracker.test.ts
- server/job/schedule.ts
- server/lib/settings/index.ts
- src/components/Settings/SonarrModal/index.tsx
- src/components/Settings/RadarrModal/index.tsx
- src/i18n/locale/en.json
- seerr-api.yml
Do not casually rewrite this branch while working on Wholphin.
Sonarr
Path:
C:\Projects\Wholphin\Sonarr
Branch:
v5-develop
Tree is clean. No changes were made during this work.
Radarr
Path:
C:\Projects\Wholphin\Radarr
Branch:
develop
Tree is clean. No changes were made during this work.
Jellyfin
Path:
C:\Projects\Wholphin\jellyfin
Branch:
master
Tree is clean. No changes were made during this work.
qBittorrent
Path:
C:\Projects\Wholphin\qBittorrent
Branch:
master
Tree is clean. No changes were made during this work.
SABnzbd
Path:
C:\Projects\Wholphin\sabnzbd
Branch:
develop
Tree is clean. No changes were made during this work.
4. End-to-end ecosystem flow
Wholphin request UI
  → Seerr POST/PUT /request
  → Seerr records MediaRequest/SeasonRequest
  → Seerr tells Sonarr/Radarr to add/search/monitor media
  → Sonarr/Radarr sends a grab to qBittorrent or SABnzbd
  → download client downloads the release
  → Sonarr/Radarr periodically and eventfully refresh monitored downloads
  → Sonarr/Radarr exposes current work through /queue
  → Sonarr/Radarr imports completed files into the media library
  → active /queue records disappear
  → Jellyfin filesystem monitoring/library scans discover imported files
  → Jellyfin creates playable movie/series/season/episode items
  → Seerr later reconciles Jellyfin availability through its own scans
  → Wholphin independently checks Jellyfin readiness
Authority by stage
Concept	Authority
User request intent and approval	Seerr MediaRequest / season request
Monitoring/search command accepted	Sonarr/Radarr
Current bytes, remaining time, download-client state	Sonarr/Radarr /queue, sourced from the client
Torrent/NZB transfer itself	qBittorrent or SABnzbd
Download completion according to the client	Download client
Import, replacement, rename and library placement	Sonarr/Radarr
File exists in the media library	Filesystem plus Sonarr/Radarr
Jellyfin has discovered it	Jellyfin library database
Actually navigable/playable in Wholphin	Jellyfin item and media source
Seerr “available”	Seerr’s most recent media-server reconciliation
Persistent library completeness	Not yet fully implemented in Wholphin


5. Important ID relationships
Never substitute one identity for another without verification.
Common identifiers
- TMDB ID:
  - Primary cross-system movie/series identity between Seerr and Wholphin.
  - Used when locating corresponding Jellyfin media.
  - Wholphin readiness lookup verifies TMDB identity before treating a Jellyfin search result as authoritative.
- TVDB ID:
  - Important inside Sonarr and episode metadata.
  - Can help correlate TV media but is not the main Wholphin readiness key currently.
- Seerr request ID:
  - Identifies one request record.
  - A TV series can have multiple requests for different seasons.
  - Must remain part of TV acquisition ledger identity; otherwise separate requests for the same series contaminate one another.
- Seerr media ID:
  - Identifies Seerr’s media record.
  - Not a Jellyfin item ID.
  - Multiple requests can reference the same media record.
- Sonarr series ID / Radarr movie ID:
  - Appears as externalId in Seerr downloadStatus.
  - Scoped to a particular Servarr server.
- downloadId:
  - Identifies an underlying download-client acquisition.
  - Useful for grouping projected queue records.
  - Not globally unique.
  - Not sufficient as the sole logical identity.
  - A season pack can produce many episode queue records sharing one downloadId.
- Jellyfin series/movie/season/episode UUID:
  - Authority for local navigation.
  - Readiness stores:
    - movie item ID;
    - series item ID;
    - season item IDs by season number;
    - episode item IDs by season and episode number.
- Season and episode numbers:
  - Canonical TV-level correlation inside a verified series.
  - Season 0 means Specials and requires deliberate handling.
  - Do not invent episode numbers from counts.
6. Existing Wholphin request and series work
The committed feature/seerr-missing-seasons work is already merged into the current branch.
Relevant commits include:
84a95852 Add requestable missing seasons to series details
93fee50f Improve TV season request dialog
20d916bc Filter actionable request seasons
f64f8d5d Fix season request status overlay
2ec57684 Show series availability in details header
6c7dd83e Refresh merged seasons after Jellyfin updates
Series details
Key files:
- [SeriesViewModel.kt](C:/Projects/Wholphin/Wholphin/app/src/main/java/com/github/damontecres/wholphin/ui/detail/series/SeriesViewModel.kt)
- [SeriesDetails.kt](C:/Projects/Wholphin/Wholphin/app/src/main/java/com/github/damontecres/wholphin/ui/detail/series/SeriesDetails.kt)
SeriesState.seasons remains the original Jellyfin season list used by episode loading and navigation.
SeriesState.detailsSeasons is a separate merged details-only representation. This preserves the lazy Jellyfin pager and normal episode path.
updateSeerrDetails():
- Indexes Jellyfin seasons by season number.
- Indexes Seerr seasons by season number.
- Produces one SeriesDetailsSeason per unioned season number.
- Prefers the real Jellyfin item whenever it exists.
- Uses Seerr poster/year/request information only for missing seasons.
Missing Seerr-only cards:
- Are greyed.
- Remain enabled and D-pad focusable.
- Reuse SeasonCard, including its normal focus border and scale.
- Show normalized names: Specials for 0 and Season N otherwise.
- Keep Seerr artwork.
- Show episode count when known.
- Show PendingIndicator for pending/processing.
- Show PartiallyAvailableIndicator for partial availability.
- Open the existing RequestSeasonsDialog.
The series header uses whole-series discoverSeries.availability:
- AVAILABLE → AvailableIndicator
- PARTIALLY_AVAILABLE → PartiallyAvailableIndicator
Other series-level statuses are intentionally not shown.
Request dialog
RequestSeasons.kt now has the compact TV-oriented layout:
- Submit at top.
- Submit explicitly receives initial focus only once.
- Preselected season immediately below when supplied.
- More Seasons collapsed initially for a targeted season.
- Generic Discover flow uses Seasons, initially expanded.
- Advanced Options collapsed initially.
- Existing server, 4K, profile and root-folder controls retained.
- Expanded lists filter out fully available, non-actionable seasons.
- D-pad focus and scroll behavior were polished to avoid repeated jumps.
- Season labels are generated from season number.
- Existing pending/available/requestable icons are reused.
Do not reimplement this request flow elsewhere.
7. Existing Wholphin acquisition model
Important files
- [SeerrAcquisition.kt](C:/Projects/Wholphin/Wholphin/app/src/main/java/com/github/damontecres/wholphin/data/model/SeerrAcquisition.kt)
- [TvAcquisitionProjection.kt](C:/Projects/Wholphin/Wholphin/app/src/main/java/com/github/damontecres/wholphin/data/model/TvAcquisitionProjection.kt)
- [DownloadsMembership.kt](C:/Projects/Wholphin/Wholphin/app/src/main/java/com/github/damontecres/wholphin/data/model/DownloadsMembership.kt)
- [SeerrAcquisitionLedger.kt](C:/Projects/Wholphin/Wholphin/app/src/main/java/com/github/damontecres/wholphin/services/SeerrAcquisitionLedger.kt)
- [SeerrAcquisitionTracker.kt](C:/Projects/Wholphin/Wholphin/app/src/main/java/com/github/damontecres/wholphin/services/SeerrAcquisitionTracker.kt)
- [JellyfinAcquisitionReadinessService.kt](C:/Projects/Wholphin/Wholphin/app/src/main/java/com/github/damontecres/wholphin/services/JellyfinAcquisitionReadinessService.kt)
- [SeerrRequestPagination.kt](C:/Projects/Wholphin/Wholphin/app/src/main/java/com/github/damontecres/wholphin/services/SeerrRequestPagination.kt)
- [DownloadsPage.kt](C:/Projects/Wholphin/Wholphin/app/src/main/java/com/github/damontecres/wholphin/ui/downloads/DownloadsPage.kt)
Request state versus acquisition state
SeerrRequestState carries:
- Request, media and TMDB IDs.
- Requester ID/name.
- Movie/TV and normal/4K identity.
- Request status.
- Whole-media Seerr availability.
- Requested-season availability and updatedAt.
- Expected episode counts.
- Requested season numbers.
- Request timestamps.
- Jellyfin readiness and observed readiness timestamps.
SeerrAcquisitionState is separate:
- Queueing
- None
- Processing
- Movie
- Tv
Queueing means Wholphin successfully submitted the request but has not yet reconciled it from fresh authoritative Seerr/Jellyfin data. It is not download progress.
Immediate request representation
The three successful request paths register Queueing and then wake the tracker:
- DiscoverMovieViewModel.request()
- DiscoverSeriesViewModel.request()
- SeriesViewModel.request()
The missing-season flow uses SeriesViewModel.request().
A failed submission must not register Queueing.
Queueing has a 15-minute safety TTL. It must not disappear merely because /request contains the new request; it should be removed season-by-season only when an authoritative Downloads row can replace that exact target.
Polling
The tracker is application-scoped and exposes a StateFlow.
Implemented intent:
- Poll immediately on foreground start.
- Normal foreground cadence: about 30 seconds.
- Downloads-visible cadence: about 8 seconds.
- refreshNow() wakes the same loop; it does not create a per-request polling loop.
- Stop/suspend when not foreground or Seerr is unavailable.
- Retain the last good snapshot on network failure.
- Global/account-wide request tracking, not current-user-only.
- Requester identity is preserved for future filtering/notifications.
Movie progress
Movies use byte progress:
fraction = (size - sizeLeft) / size
Movie lifecycle logic was deliberately stabilized and should not be changed as part of TV work.
TV ledger
The TV ledger exists because Sonarr queue records disappear independently after transfer/import.
Important identity properties include:
- Request ID.
- Normal versus 4K.
- Season number.
- Episode number where known.
- Media/Servarr identity.
- downloadId as supporting rather than sole identity.
The request ID was added after a real cross-season contamination bug: historical Season 3 and current Season 4 requests for the same series were sharing queue timing/progress.
The ledger preserves:
- Current queue entries.
- A two-poll provisional grace after disappearance.
- Maximum known total/completed bytes for a logical entry.
- Whether progress was genuinely observed.
- A durable in-memory fact that successful transfer completion was explicitly observed.
observedSuccessfulTransferCompletion is set only from strong current evidence such as:
- positive total size with sizeLeft == 0; or
- a recognized completed/successful queue status.
It is not inferred from:
- disappearance;
- timeLeft == 00:00:00 alone;
- historical maximum progress;
- request status.
This completion fact survives the ordinary two-poll grace while Jellyfin catches up. It is still not local availability.
The ledger is in memory. It does not survive app restart.
Canonical TV projection
toTvSeasonTargets() is the canonical season-granular projection.
Each target is keyed conceptually by:
(requestId, is4k, seasonNumber)
One row is emitted per requested season.
It merges:
- Current assigned episode queue entries.
- Retained ledger entries.
- Truly seasonless entries only when attribution is unambiguous.
- Requested-season status/timestamps.
- Expected episode count.
- Jellyfin episode and full-season readiness.
A TV series-level fallback should exist only if no season-level request/acquisition information exists.
A known Season 4 entry must never be attached to Season 3 just because Season 3 is the only requested season in another historical request.
TV lifecycle
Internal lifecycle:
- QUEUED
- IN_PROGRESS
- FINISHING
- AVAILABLE
User-visible wording:
- Queueing
- Queued
- In progress
- Finishing
- Available
Avoid “Downloading” in Downloads because queue status alone does not prove bytes are moving.
Rules:
- Queued: no genuine measurable activity.
- In progress: meaningful season acquisition activity exists, but season-wide finalization is not established.
- Finishing: strong acquisition finalization or requested-season completion exists, but Jellyfin is not fully ready.
- Available: Jellyfin confirms all expected episodes.
Temporary empty queues or one episode disappearing do not make an entire season Finishing.
Episode-normalized progress
For ordinary/ambiguous episode acquisition:
season fraction =
  sum(per-episode contribution) / expected episode count
For each expected episode:
- Jellyfin playable → 1.0.
- Current or grace-retained measurable acquisition → byte fraction.
- Explicitly observed successful transfer completion → 1.0 provisionally.
- Otherwise → 0.
Jellyfin-confirmed progress is authoritative. Provisional Seerr progress is allowed to regress when its evidence disappears, fails, is replaced, or expires.
Do not clamp overall progress to its historical maximum.
Full-season pack handling
Seerr/Sonarr can project one season pack as many episode queue rows with:
- the same downloadId;
- identical title;
- identical size/sizeLeft;
- identical timeLeft and ETA;
- different nested episode identities.
Naively episode-normalizing only the projected subset badly under-reports a pack. A pack covering 10 projected records in a 22-episode season capped near 10/22 ≈ 45%, even if the underlying pack was nearly complete.
TvAcquisitionProjection.kt classifies groups as:
- FULL_SEASON_ACQUISITION
- EXPLICIT_EPISODES
- AMBIGUOUS
Full-season extrapolation requires more than shared downloadId. It requires coherent shared transport data and a release title indicating the requested season without an episode token, episode range, or partial qualifier.
Ambiguous cases remain conservatively episode-normalized.
Final progress is:
confirmedFraction = Jellyfin playable / expected count
fullSeasonFraction = greatest valid full-season acquisition fraction
episodeFraction = existing episode-normalized contribution

displayedFraction =
    max(confirmedFraction, fullSeasonFraction, episodeFraction)
Do not add Jellyfin episode units to the full-season byte fraction; that double-counts the same content.
Timing and ETA
For current genuine TV activity:
1. Positive valid timeLeft is primary.
2. ETA is derived as device current time plus timeLeft.
3. Raw estimatedCompletionTime is only an ETA-only fallback if no positive duration exists and the timestamp is future-valid.
4. Independent episodes choose the largest positive remaining duration; durations are never summed.
5. Retained/grace-only evidence does not supply timing.
6. Queued and Finishing rows do not retain stale timing.
This changed after Seerr returned internally inconsistent pairs such as a sensible five-minute duration with an absolute ETA months away.
8. Downloads UI and navigation
DownloadsPage consumes only SeerrAcquisitionTracker; it must not refetch Seerr independently.
Sections are exclusive:
- Active.
- Processing/waiting.
- Recently Completed.
One stable key is retained throughout transitions:
movie: request ID based identity
TV: {requestId}_season_{seasonNumber}
The same acquisition must never appear in two sections simultaneously. Duplicate keys previously caused:
IllegalArgumentException: Key "572_season_1" was already used
Do not hide duplicate projection bugs by prefixing section names or adding arbitrary suffixes.
Recently Completed:
- Rolling previous 7 days. This gives users who return after several days useful operational completion history without turning Downloads into a long-term request archive.
- No fixed count cap.
- Recomputed from timestamps on each refresh.
- media.updatedAt must never be used as completion time.
- Requested season updatedAt is a fallback only when that requested season is actually completed/available.
- Tracker-observed Jellyfin readiness time is preferred when available.
- First observation of content that is already Jellyfin-ready is not a readiness transition and must not be stamped with the current time. Only an observed not-ready → ready transition receives `now`; an already-ready prior state retains its existing readiness timestamp. With no prior state, request/season availability timestamps may provide the conservative historical fallback above.
Navigation:
- Not Jellyfin-ready → Seerr Discover details.
- Jellyfin-ready movie → Jellyfin movie details.
- Jellyfin-ready TV season → Jellyfin series with SeasonEpisodeIds.
Current direct season implementation in DownloadsPage.kt:
Destination.SeriesOverview(
    itemId = seriesId,
    type = BaseItemKind.SERIES,
    seasonEpisode = SeasonEpisodeIds(seasonId, seasonNumber, null, null),
)
If the Jellyfin season ID is unavailable, it safely falls back to series-level navigation. It never guesses by title.
Focus behavior has custom one-shot restoration for:
- Returning from details.
- A focused acquisition moving between sections during live refresh.
- A focused item disappearing.
Do not continuously call requestFocus() during recomposition.
9. Seerr acquisition data exposed to Wholphin
The vendored Wholphin OpenAPI schema was extended to model:
- MediaInfo.downloadStatus
- MediaInfo.downloadStatus4k
- queue entries with:
  - externalId
  - estimatedCompletionTime
  - mediaType
  - size
  - sizeLeft
  - status
  - timeLeft
  - title
  - downloadId
- nested TV episode data:
  - seriesId
  - seasonNumber
  - episodeNumber
  - title
  - hasFile
- season request createdAt and updatedAt
- malformed/partial optional users where required
Generated Kotlin must be regenerated from schema. Never hand-edit generated Seerr client files.
Malformed queue entries such as {} are filtered as absent. They cannot create an active acquisition.
Malformed transient requestedBy: {} or modifiedBy: {} objects must not fail the whole request page; requester identity is preserved whenever valid fields exist.
10. Seerr backend work
DownloadTracker behavior
Relevant files:
- server/lib/downloadtracker.ts
- server/job/schedule.ts
- server/entity/Media.ts
Media.downloadStatus and downloadStatus4k are populated from the process-local DownloadTracker.
They are not durable acquisition history. Once a queue entry is absent from the tracker snapshot, Seerr does not retain it there.
DownloadTracker.updateDownloads() is single-flight:
- Concurrent callers receive the active promise.
- Sonarr and Radarr categories refresh in parallel.
- Independent physical servers refresh in parallel.
- One server failure is caught per server and does not stop others.
- A failed server retains its previous snapshot.
The scheduled Download Sync remains one minute.
Forced Servarr refresh
Current flow:
POST /command { name: RefreshMonitoredDownloads }
→ capture exact returned command ID
→ poll GET /command/{id}
→ require status=completed and result=successful
→ fetch /queue
→ replace that server’s snapshot
Failed, aborted, cancelled, orphaned, unsuccessful, or timed-out commands do not replace the previous snapshot.
The command deadline is enforced on each Axios request:
- Remaining time is calculated immediately before the poll.
- No request starts at or after the deadline.
- Poll timeout is min(existing Axios timeout, remaining command time).
- A request timeout caused by the overall deadline becomes the existing RefreshMonitoredDownloads timeout error, not a misleading generic fetch failure.
The successful command condition was verified against current Sonarr/Radarr types:
status = completed
result = successful
Configurable queue size
The current Seerr branch implements per-server:
downloadQueueSize?: number
Defaults to 10 for old and new configurations.
Validation:
- Integer only.
- Minimum 1.
- Maximum 1000.
- Zero is rejected; it does not mean unlimited.
Sonarr and Radarr modals contain localizable:
- Label.
- Description.
- Factual performance warning.
The warning explains that larger values may affect constrained CPUs, I/O-limited systems, or very large queues.
The current implementation requests:
GET /queue?includeEpisode=true&page=1&pageSize=configuredLimit
and validates that the response contains the expected number up to min(totalRecords, configuredLimit).
This is the maintainer-directed configurable-page-size interpretation, not an unconditional “download every page until the entire queue is exhausted” design. Default behavior remains 10.
When multiple Seerr logical configurations point at one physical Servarr server, Seerr fetches the maximum configured limit once and slices the result for each logical server configuration.
Runtime validation already performed
A real Grey’s Anatomy Season 2 Sonarr season pack produced 27 episode projections sharing one downloadId.
Observed outcome with the patched Seerr instance:
- The Servarr refresh command completed successfully.
- Queue retrieval occurred afterward.
- All 27 records were returned instead of the former default 10.
- Episode identities 1–27 were preserved.
- Shared downloadId did not incorrectly deduplicate them.
- Seerr downloadStatus exposed all 27 episode projections.
- Wholphin could consume the complete set.
A separate individual-episode acquisition was also observed to verify distinct downloadId handling and independent episode projection.
Failure/timeout/atomic replacement behavior was covered with automated tests, not destructive production-service manipulation.
11. Sonarr/Radarr and download clients
Sonarr
Important files include:
- src/NzbDrone.Core/Jobs/TaskManager.cs
- src/NzbDrone.Core/Jobs/Scheduler.cs
- src/NzbDrone.Core/Download/TrackedDownloads/DownloadMonitoringService.cs
- src/NzbDrone.Core/Download/TrackedDownloads/TrackedDownloadService.cs
- src/NzbDrone.Core/Download/DownloadProcessingService.cs
- src/NzbDrone.Core/Queue/QueueService.cs
- src/NzbDrone.Core/Download/RefreshMonitoredDownloadsCommand.cs
- download-client implementations under src/NzbDrone.Core/Download/Clients/
Current Sonarr schedules RefreshMonitoredDownloadsCommand every one minute, not the historical two minutes.
DownloadMonitoringService also reacts to relevant events and uses debounce/command-queue behavior. Refresh:
- Calls configured download clients for queue/history state.
- Builds tracked-download state.
- Updates QueueService.
- Schedules processing of monitored downloads.
- Recognizes finished downloads and passes them to import processing.
QueueService is an in-memory current projection. Its entries disappear after the tracked download is removed/imported.
Radarr
Radarr uses the same general architecture and command model:
- Periodic monitored-download refresh.
- Download-client queue/history retrieval.
- Tracked download projection.
- Completed download processing/import.
- /queue API over the current projection.
Movie correlation is simpler because there is no season/episode projection, but upgrades and replacements remain important.
qBittorrent
Sonarr/Radarr query the qBittorrent Web API through their download-client proxy and map torrents to DownloadClientItem objects.
The client owns:
- Torrent hash/download ID.
- Transfer state.
- Total and remaining bytes.
- Ratio/seeding status.
- Completion state.
- Save path.
Sonarr/Radarr own media correlation and import decisions.
Wholphin should not integrate directly with qBittorrent for this feature.
SABnzbd
Sonarr/Radarr’s SABnzbd integration queries queue and history APIs.
For example, the Servarr Sabnzbd adapter maps:
- SAB job ID → DownloadId.
- Size and Sizeleft → total/remaining bytes.
- Timeleft → remaining time.
- SAB queue state → queued/downloading/paused.
SABnzbd additionally has post-processing and archive extraction stages. Transfer completion does not necessarily mean import readiness.
Again, Servarr is the correct normalization boundary. Wholphin should not depend directly on SABnzbd.
12. Jellyfin readiness
Important distinction:
download client completed
≠ Sonarr/Radarr imported
≠ Jellyfin discovered
≠ Jellyfin item is playable
Jellyfin may discover imported content through filesystem monitoring or a later library scan. Seerr separately runs Jellyfin recently-added/full scans to update its own availability database.
Wholphin’s JellyfinAcquisitionReadinessService does not wait solely for Seerr:
- It searches Jellyfin.
- Verifies the expected TMDB identity.
- Resolves movie/series item IDs.
- Fetches season and episode children.
- Keeps season item IDs and episode item IDs.
- Treats a movie as ready only when its Jellyfin item is usable.
- Treats a season as fully ready only when expected playable episodes are present.
Readiness identity is retained across later Seerr snapshots. A fresh Seerr object with empty readiness must not erase a previously resolved Jellyfin ID.
The Seerr jellyfinMediaId field is not used as the readiness/navigation authority because it can lag behind actual Jellyfin state.
13. Non-obvious discoveries and negative knowledge
These are the conclusions a developer is most likely to miss by reading only the final code.
Seerr Processing is not active download proof
Initial expectation:
Processing likely means the item is downloading.

Observed:
- Processing records can remain stale or broken for days.
- Processing may exist before any queue entry appears.
- Processing with empty downloadStatus cannot justify a percentage.
- Visible Downloads waiting membership therefore has only a short timestamp-based grace.
Design consequence:
- Request state and acquisition state remain separate.
- “Downloading” is not inferred from Processing.
Queue status downloading is not proof bytes are moving
A sequential item waiting behind another acquisition may already report status=downloading while:
sizeLeft == size
Design consequence:
- Queued remains until sizeLeft < size or a decrease is observed between polls.
- Do not classify purely from the status string.
Queue disappearance is ambiguous
Initial temptation:
If it vanished from /queue, it finished.

Wrong because it may have:
- completed and moved to import;
- failed;
- been removed;
- been replaced;
- disappeared between polls;
- been temporarily absent during reconciliation.
Design consequence:
- Disappearance alone is never completion.
- Ordinary partial evidence expires and may regress.
- Only explicitly observed transfer completion gets durable in-memory provisional credit.
- Jellyfin is still required for Available.
Seerr media.updatedAt is not a completion timestamp
It can change because of unrelated media refresh/reconciliation work.
Design consequence:
- Never use it for Recently Completed.
- Use observed Jellyfin readiness time.
- Use request/season updatedAt only as a fallback when the corresponding request target is actually completed.
Whole-series TV availability cannot decide season completion
A series may remain Partially Available because other seasons are absent even though the requested season is complete.
Design consequence:
- Use request.seasons[] status and timestamps.
- Evaluate Jellyfin readiness per requested season.
- Do not require top-level media status to become Available.
media.seasons and request.seasons are semantically different
Completion fallback belongs to the requested season state, not the generic media-season list.
Shared downloadId can represent many episode rows
The Grey’s Anatomy validation showed 27 episode queue rows sharing one underlying season-pack ID.
Design consequence:
- Do not deduplicate rows merely by downloadId.
- Preserve nested episode identity.
- For progress, analyze grouped acquisition scope rather than either summing identical bytes 27 times or counting only projected episodes blindly.
Shared downloadId alone does not prove a full-season pack
It may describe a multi-episode range or partial pack.
Strong pack classification also requires:
- matching target season;
- coherent shared bytes/timing;
- multiple projected episode records;
- season-level release title;
- absence of episode/range/partial qualifiers.
Ambiguous groups remain conservative.
Episode-normalized progress is correct only for ordinary episode acquisitions
It works well for independent episode downloads and allows honest regression.
It under-reports an underlying season pack projected onto fewer records than the expected episode count.
The current hybrid max merge exists specifically because of this real-world observation.
Do not make progress globally monotonic
The Season 4 trace showed a legitimate provisional regression around:
58% → 54% → 50%
Provisional queue evidence expired or was replaced. Jellyfin-confirmed contribution did not regress.
A historical maximum clamp would conceal failed/replaced provisional work.
Explicit transfer completion must be distinguished from disappearance
The 20% → 0% In progress → Available case occurred because all provisional entries expired before Jellyfin reconciliation, even though Sonarr had completed all episodes.
Design consequence:
- Retain only explicit successful completion evidence.
- Do not generally retain historical progress.
- During the completed-transfer/Jellyfin gap, show Finishing below 100%.
Seerr raw ETA can be nonsensical
Observed combinations included:
timeLeft ≈ 00:05:58
estimatedCompletionTime months in the future
Sonarr’s remaining duration was sensible.
Design consequence:
- Positive timeLeft wins.
- Derive local ETA from current device time plus duration.
- Raw ETA is fallback-only.
Timing can leak across historical requests without request-scoped identity
Season 3 once displayed Season 4’s exact timing because ledger matching used series/media identity too broadly.
Design consequence:
- TV ledger identity includes request ID and season.
- Queue entries with a known different season are never treated as unassigned.
Initial Queueing can disappear too early
A successful request may appear immediately in /request but not yet qualify for a Downloads row.
Removing local Queueing merely because the request exists creates a blank interval.
Design consequence:
- Queueing is removed only when an authoritative target-level Downloads representation can replace it.
- Multi-season requests reconcile season-by-season.
Jellyfin can know before Seerr
Imported media can be in Jellyfin while Seerr still says Pending or Processing because Seerr’s media-server scan has not reconciled yet.
Design consequence:
- Direct Jellyfin readiness checks are authoritative for playability.
- Wholphin does not wait for Seerr’s next Jellyfin Recently Added scan.
- Seerr status remains useful for intent/history, not final navigation authority.
Seerr can still miss short-lived acquisitions
Even with fixed queue depth and forced refresh:
grabbed
→ downloaded
→ imported
→ removed from active Servarr queue
can happen entirely between Seerr Download Sync runs.
Seerr then misses:
- live byte progress;
- queue state;
- download ID;
- exact transfer-completion transition.
Final state may still be recovered later from:
- Servarr history/import events;
- Seerr media reconciliation;
- Jellyfin presence.
No Servarr history reconciliation has been implemented. It was investigated as a future independent Seerr contribution.
Availability and acquisition are independent dimensions
An already available movie or episode can simultaneously be downloading a quality upgrade.
Therefore a single enum where Available overrides Downloading is insufficient as a general long-term model.
Current Wholphin code partially separates these concepts through Seerr availability, acquisition state, and Jellyfin readiness. Preserve that direction.
Request causality must not be invented
Sonarr/Radarr acquisitions can originate outside Seerr. Retries and upgrades may not correspond cleanly to a current request.
Do not attach Servarr history to a Seerr request solely because timestamps are nearby. History can be media/Servarr-associated without certain request causality.
14. Servarr history investigation: not implemented
The proposed durable architecture was:
Seerr request          = request intent/approval
Servarr /queue         = live progress and ETA
Servarr public history = durable acquisition lifecycle evidence
Jellyfin               = final availability/playability
Important conclusions:
- /history/since can recover persistent grabbed/imported/failed/ignored events.
- Incremental reconciliation must handle inclusive timestamps, identical timestamps, unstable ordering and persistent row IDs.
- A cursor must not advance until state changes and checkpoint are safely committed.
- downloadId is supporting correlation, not globally unique identity.
- History should not imply request causality unless correlation is certain.
- Availability and acquisition remain separate dimensions.
Adversarial design review concluded that the first upstream contribution should be smaller than a full three-entity Wholphin-oriented projection.
Reasonable phases:
- Checkpoint only: supports incremental reads but loses durable projected state and is not useful enough alone.
- Checkpoint plus small persistent acquisition ledger: smallest generally useful Seerr design.
- Full target/episode projection: useful for rich clients but too large and too Wholphin-specific for the first upstream PR.
No code for history reconciliation was written.
It is not necessarily the immediate next Seerr PR. The queue correctness/configurability work should be reviewed independently first.
15. Interrupted persistent incomplete-season task
Requirement
A season can remain incomplete long after its acquisition disappears from Downloads history. Persistent library integrity must therefore be independent of SeerrAcquisitionTracker.
Intended definition:
Incomplete =
    released/expected episodes are known
    AND Jellyfin playable episodes are missing
    AND missing episodes are not covered by active acquisition evidence
Examples:
Incomplete — 3 episodes missing
Avoid lifecycle wording such as Stalled.
Implemented: SeasonIntegrity.kt
File exists:
- [SeasonIntegrity.kt](C:/Projects/Wholphin/Wholphin/app/src/main/java/com/github/damontecres/wholphin/data/model/SeasonIntegrity.kt)
Intended entity fields:
- Jellyfin user row ID.
- Jellyfin series UUID.
- Season number.
- TMDB ID.
- Jellyfin season UUID when known.
- Expected episode count.
- Exact expected episode-number set when known.
- Playable episode count.
- Missing episode count.
- Exact missing episode numbers where known.
- incomplete.
- Last reconciliation timestamp.
Intended composite primary key:
(jellyfinUserRowId, seriesItemId, seasonNumber)
Intended foreign key:
jellyfinUserRowId → JellyfinUser.rowId
ON DELETE CASCADE
ON UPDATE CASCADE
Intended indexes:
- Jellyfin user row ID.
- Series item ID.
It also contains:
- SeasonIntegrityExpectation
- internal SeasonAcquisitionCoverage
- pure calculateSeasonIntegrity()
The calculation:
- Ignores season 0/Specials.
- Ignores expectations with nonpositive counts.
- Uses exact expected numbers when available.
- Otherwise uses count-based fallback without inventing missing episode numbers.
- Removes playable episodes.
- Removes missing episodes currently covered by active acquisition.
- Marks the remainder Incomplete.
Critical verified problem
The current file is syntactically invalid because annotation string values lost their quotes during the failed/stale sandbox editing path:
tableName = season_integrity
parentColumns = [rowId]
childColumns = [jellyfinUserRowId]
indices = [Index(jellyfinUserRowId), Index(seriesItemId)]
primaryKeys = [jellyfinUserRowId, seriesItemId, seasonNumber]
These should be string literals.
Do not assume this file compiles.
Status: Partially implemented and currently broken.
Implemented: SeasonIntegrityDao.kt
File exists:
- [SeasonIntegrityDao.kt](C:/Projects/Wholphin/Wholphin/app/src/main/java/com/github/damontecres/wholphin/data/SeasonIntegrityDao.kt)
It contains:
- observeSeries(userId, seriesItemId): Flow<List<SeasonIntegrity>>
- getSeries(userId, seriesItemId)
- upsert(items)
Status: Implemented but uncompiled/unvalidated.
No deletion/pruning query exists yet.
Partially implemented: Room database
[AppDatabase.kt](C:/Projects/Wholphin/Wholphin/app/src/main/java/com/github/damontecres/wholphin/data/AppDatabase.kt) currently has:
- SeasonIntegrity added to entities.
- Database version changed from 35 to 36.
- AutoMigration(35, 36).
- seasonIntegrityDao().
- converters between nullable Set<Int> and comma-separated strings.
[DatabaseModule.kt](C:/Projects/Wholphin/Wholphin/app/src/main/java/com/github/damontecres/wholphin/services/hilt/DatabaseModule.kt) provides SeasonIntegrityDao.
Critical status:
- There is no generated Room schema 36.json.
- Existing schemas stop at 35.
- Auto-migration has not been validated.
- Formatting/line endings are mixed in the edited portions.
- No compile has been run since these changes.
Status: Partially implemented, not validated.
Partially implemented: SeasonIntegrityService.kt
File exists:
- [SeasonIntegrityService.kt](C:/Projects/Wholphin/Wholphin/app/src/main/java/com/github/damontecres/wholphin/services/SeasonIntegrityService.kt)
Current responsibilities:
- Observe stored integrity entries for a series.
- Merge stored expectations with newly supplied expectations.
- Recursively fetch Jellyfin Season and Episode children.
- Treat episodes with media sources as playable.
- Resolve season UUIDs by season number.
- Obtain active acquisition coverage from SeerrAcquisitionTracker.
- Calculate and upsert reconciled rows.
Current active coverage behavior:
- Queueing and Processing are treated as whole-season coverage.
- Assigned TV queue entries cover their episode numbers.
- A genuinely unassigned active entry can cover a sole requested season.
- Problem entries are excluded.
Risks requiring review:
- Treating every Seerr Processing request as whole-season coverage may hide a persistent incomplete state indefinitely if Processing is stale. Earlier acquisition work proved Processing can be stale.
- Coverage currently looks primarily at present-in-queue entries; explicitly completed-but-retained acquisition evidence may need deliberate interpretation.
- Service compilation has not been verified.
- Exception/error handling and graceful degradation need review.
- No pruning strategy exists for obsolete stored seasons.
- It currently persists complete observations as incomplete=false; that is arguably useful because it retains expectations for later regression detection, but the intended semantics should be confirmed.
Status: Partially implemented, not integrated or validated.
Planned only: SeriesViewModel integration
SeriesViewModel does not inject or call SeasonIntegrityService.
SeriesState has no integrity field.
SeriesDetailsSeason has no integrity field.
Expected/released episode metadata is not yet converted from TvDetails.
Planned behavior:
- Derive released expected episodes from Seerr/TMDB season episode metadata.
- Prefer exact episode-number sets with release/air dates at or before today.
- Use count-only fallback conservatively if exact numbers are unavailable.
- Never count unreleased future episodes as missing.
- Never invent episode numbers from only a count.
- Reconcile when a series is opened/refreshed.
- Observe persisted rows so UI updates when reconciliation completes.
- Reconcile after relevant local refresh/deletion updates.
- Potentially reconcile when acquisition coverage materially changes while the page is alive, without hitting Jellyfin on every unchanged poll.
Status: Planned only.
Planned only: UI
No Incomplete badge or missing-count text has been added.
Natural integration point:
- SeriesDetails season row.
- Reuse SeasonCard.artworkOverlay so the indicator participates in the existing focused transform.
- Do not place an outer overlay that remains stationary during card zoom.
- Render persisted incomplete state for the corresponding season.
- Avoid contradictory acquisition/status overlays.
Potential wording resources:
- Incomplete
- singular: 1 episode missing
- plural: {count} episodes missing
Specials/season 0 should not receive false integrity warnings.
Status: Planned only.
Planned only: tests
No SeasonIntegrity tests exist.
Required focused cases include:
1. All expected episodes playable → complete.
2. Missing episode without active coverage → incomplete.
3. Exact missing numbers retained.
4. Active acquisition covers some missing episodes.
5. Whole-season coverage suppresses current unattended missing state.
6. Acquisition disappears while episodes remain absent → incomplete persists/reappears.
7. Explicit counts do not create fake episode numbers.
8. Future/unreleased episodes excluded by expectation derivation.
9. Season 0 ignored.
10. Jellyfin later reaches full readiness → incomplete clears.
11. Per-user/per-series keys isolate state.
12. Stored expectations survive a later reconciliation lacking fresh Seerr metadata.
13. Room migration/schema validation.
14. Graceful behavior without Seerr.
15. Stale Processing does not hide integrity indefinitely.
16. Reconciliation design considerations
Recommended minimum trigger:
- Opening the series details page.
- Explicit series refresh.
- Existing Jellyfin season refresh paths.
Possible later triggers:
- Opening a season.
- Relevant Jellyfin library change events.
- Lightweight periodic reconciliation.
Do not add all triggers in the first implementation if they broaden the patch substantially. The minimum product requirement is self-healing when the user revisits or refreshes the series.
Important data rule:
- Exact released episode numbers are best.
- episodeCount can include future episodes.
- Air dates can be missing, delayed, or timezone-sensitive.
- Count-only fallback must be conservative.
Important persistence rule:
- If only incomplete=true rows are stored and a complete row is deleted, Wholphin may lose the expected episode metadata needed to detect a later library regression without Seerr.
- Persisting the latest complete observation as incomplete=false retains useful expectation state.
- “Clear the Incomplete state” can mean clearing the visible flag rather than deleting all reconciliation metadata.
This should be decided explicitly rather than accidentally.
17. Validation history
Wholphin
Before the interrupted integrity work, the acquisition and missing-season features were repeatedly compiled and unit-tested with:
:app:compileDefaultDebugKotlin
:app:testDefaultDebugUnitTest
git diff --check
The user manually confirmed the core missing-season feature worked on Android TV.
The Downloads/acquisition implementation received extensive focused tests covering:
- Movie progress.
- TV season aggregation.
- 4K isolation.
- Pagination.
- Queue churn.
- Retry/replacement identities.
- Readiness transitions.
- Section membership.
- Duplicate keys.
- Queueing reconciliation.
- Full-season packs.
- ETA selection.
- Navigation.
- Focus restoration state helpers.
Important caveat:
The newly added SeasonIntegrity files and Room version 36 changes have not been compiled or tested. The model file currently contains known invalid annotation syntax. Any older green build does not validate this interrupted work.
Seerr
The queue work was validated with focused commands including:
pnpm test server/api/servarr/base.test.ts server/lib/downloadtracker.test.ts
pnpm typecheck:server
pnpm exec eslint server/api/servarr/base.ts server/api/servarr/base.test.ts
pnpm exec prettier --check server/api/servarr/base.ts server/api/servarr/base.test.ts
git diff --check
pnpm build
The session history states these passed after the deadline review correction and configurable queue work.
Runtime validation against real Sonarr also passed the >10-record regression using 27 episode projections.
No destructive failure test was run against production services; those cases used mocks.
18. Known risks and unresolved questions
- SeasonIntegrity.kt currently cannot compile because Room annotation strings lost quotes.
- Room schema 36 has not been generated.
- AutoMigration 35→36 has not been validated.
- Set<Int>? converter behavior must be verified with Room schema generation.
- Expected released-episode derivation remains unimplemented.
- Ongoing seasons and missing air dates require conservative handling.
- Treating Processing as active full-season coverage conflicts with the observed possibility of stale Processing.
- In-memory acquisition completion evidence disappears on app restart.
- Persistent incomplete state must not depend on temporary tracker retention.
- A historical item may lack fresh Seerr metadata after restart; persisted expectations are intended to bridge that gap.
- No Servarr durable-history reconciliation exists.
- Queue entries can complete entirely between Seerr’s one-minute syncs.
- Seerr’s queue snapshot remains process-local and transient.
- Future quality upgrades require simultaneous “available” and “acquiring” state.
- Active acquisitions initiated outside Seerr may not correlate to a request.
- Avoid title matching as authoritative Jellyfin identity.
- Keep season 0 deliberate.
- Never use Seerr’s whole-series partial status as proof a requested season is incomplete or complete.
- Do not use media.updatedAt for completion time.
- Do not infer Available from 100% transfer progress.
- Do not use queue disappearance as success.
- Do not use shared downloadId alone to declare a season pack.
- Do not create another request implementation for missing seasons.
- Do not redesign SeriesState.seasons; the details-only merge already exists.
- Do not manually edit generated Seerr Kotlin.
- Do not clean untracked acquisition files.
19. Terminology and invariants
Requested
Seerr accepted a user’s request. It says nothing by itself about queue presence, byte progress, import, or playability.
Queueing
Wholphin submitted successfully but has not yet reconciled authoritative acquisition/request state.
Queued
An authoritative request/acquisition representation exists, but no genuine transfer progress is observed.
In progress
Real acquisition activity exists. This does not mean imported or playable.
Finishing
Strong transfer/request completion evidence exists, but Jellyfin does not yet confirm complete local readiness.
Seerr Available
Seerr’s media reconciliation says content is available. This may lag Jellyfin or describe a broader media object than the requested season.
Jellyfin Ready
Wholphin resolved and verified the corresponding Jellyfin item and found usable media. For a TV season, current full readiness means the expected playable episode count is satisfied.
Incomplete
Released/expected content is missing from Jellyfin and the missing content is not currently accounted for by active acquisition coverage.
Incomplete is persistent library state, not an acquisition lifecycle stage.
Partially Available
Some content exists, but not all. At whole-series level this does not identify which requested season is complete.
20. Roadmap state
Already complete or substantially implemented:
- Missing season placeholders on series pages.
- Direct missing-season requests.
- Compact request dialog.
- Series availability badge.
- Acquisition domain model.
- Downloads page.
- Movie and TV progress.
- Jellyfin readiness.
- Episode and season identities.
- Available season direct navigation.
- Canonical TV projection.
- Queueing and request wake-up.
- Full-season pack handling.
- Temporary acquisition tracing removed.
- Seerr queue-depth and synchronization corrections.
Currently interrupted:
- Persistent incomplete-season/library-integrity state.
This task enables:
- Durable “Incomplete — N episodes missing.”
- Self-healing season integrity after Downloads history expires.
- Future collection/suggestion/library badges based on reusable integrity state.
Do not implement future Watchlist, Collections, notifications, quality upgrades, or periodic Servarr history in the same patch.
The roadmap should be updated only after persistent integrity is complete and validated.
21. Exact continuation sequence
1. Re-establish a correct workspace
Start Codex with:
C:\Projects\Wholphin
or:
C:\Projects\Wholphin\Wholphin
Confirm P:\Wholphin is absent from sandbox roots.
2. Re-read instructions and record baseline
Read:
docs\AGENTS.md
docs\Wholphin_ROADMAP.md
Then record:
git branch --show-current
git status --short -uall
git diff --name-only
git diff --stat
Do not clean the tree.
3. Repair only the interrupted syntax first
Inspect SeasonIntegrity.kt and restore the Room annotation string literals.
Do not assume any other partial patch is correct.
4. Run an early compile before more implementation
Run:
.\gradlew :app:compileDefaultDebugKotlin --no-daemon
This should reveal Room/model/service issues before UI work is added.
5. Review the persistence semantics
Confirm:
- Whether complete observations remain stored as incomplete=false.
- How obsolete season rows are pruned.
- How stale Processing coverage is handled.
- Whether exact expected-number sets can be obtained safely.
6. Add pure model tests
Create focused SeasonIntegrityTest coverage before integrating the ViewModel.
7. Integrate reconciliation into SeriesViewModel
Inject SeasonIntegrityService.
At minimum:
- Reconcile on series open after local series and Seerr metadata are known.
- Observe the DAO.
- Refresh on existing series update paths.
- Keep SeriesState.seasons unchanged.
- Add integrity as separate reusable state.
8. Add SeriesDetails UI
Reuse SeasonCard.artworkOverlay.
Add localized text:
Incomplete
N episodes missing
Do not recreate card focus transforms.
9. Generate and inspect Room schema 36
Ensure:
app/schemas/com.github.damontecres.wholphin.data.AppDatabase/36.json
is generated and correct.
Verify the 35→36 migration.
10. Validate in increasing scope
Recommended order:
.\gradlew :app:testDefaultDebugUnitTest --tests "*SeasonIntegrity*" --no-daemon
.\gradlew :app:compileDefaultDebugKotlin --no-daemon
.\gradlew :app:testDefaultDebugUnitTest --no-daemon
git diff --check
git status --short -uall
Then perform Android TV manual checks:
- Fully complete season: no warning.
- One or more unexplained missing episodes: Incomplete badge/count.
- Missing episode actively acquiring: not counted as unattended.
- Acquisition disappears without Jellyfin readiness: Incomplete remains/reappears.
- Jellyfin later discovers all expected episodes: state clears.
- Season 0: no false warning.
- Card focus border/zoom unaffected.
- Seerr disconnected: base Jellyfin series still works.
- App restart: stored incomplete state remains and self-heals on series reopen.
11. Update roadmap only after success
Mark the implemented persistence/reconciliation items complete only after migration, unit tests, and emulator behavior pass.
12. Leave untouched
- Existing acquisition ledger semantics.
- Movie lifecycle.
- Polling cadence.
- Request flow.
- Generated Seerr Kotlin.
- Seerr repository.
- Sonarr/Radarr/Jellyfin/download-client repositories.
- Existing untracked Downloads/acquisition files except where the integrity implementation directly requires integration.
Write the exact first actions you recommend the new agent take after reading this handoff.
1. Open C:\Projects\Wholphin\Wholphin with a correct writable root and verify branch/status.
2. Read `docs/AGENTS.md` and `docs/Wholphin_ROADMAP.md`.
3. Save the full dirty-tree file list; do not reset or clean it.
4. Open SeasonIntegrity.kt and repair the lost Room annotation quotes.
5. Inspect SeasonIntegrityDao.kt, SeasonIntegrityService.kt, AppDatabase.kt, and DatabaseModule.kt as unvalidated partial work.
6. Run .\gradlew :app:compileDefaultDebugKotlin --no-daemon before adding any further feature code.
7. Fix only compile/migration defects attributable to the partial integrity work.
8. Add pure SeasonIntegrity tests.
9. Decide and document stale Processing coverage and complete-row persistence semantics.
10. Integrate reconciliation into SeriesViewModel and SeriesDetails only after the persistence layer is green.

22. Persistent integrity continuation (2026-09-04)

Workspace correction

**Expected → Observed → Consequence**

The inherited handoff warned that only obsolete `P:\Wholphin` was advertised writable. The current session instead exposes the repositories under `C:\Projects\Wholphin` as normal writable roots and does not expose `P:\Wholphin`. Continue using only the `C:` workspace.

The command shell does not inherit Java/Gradle home settings. Builds succeed when scoped to Android Studio's bundled JBR at `C:\Program Files\Android\Android Studio\jbr` and the existing Gradle cache at `C:\Users\const\.gradle`. The first early compile failed for environment reasons; after applying those command-scoped settings it exposed one real source defect: `SeasonIntegrityService` lacked the `com.github.damontecres.wholphin.data.ServerRepository` import. Restoring that import made the early compile pass and generated Room schema 36.

Persistence and coverage decisions

- Complete reconciliations remain persisted with `incomplete=false`. This retains released-episode expectations so a later Jellyfin regression can be detected even when Seerr metadata is unavailable.
- Do not prune a stored season merely because a later Seerr response omits it. API absence is not authoritative deletion and pruning would discard the durable expectation. User removal still cascades through the `JellyfinUser` foreign key. A future broader pruning policy requires an authoritative series-removal signal rather than transient metadata absence.
- **Expected → Observed → Consequence:** the interrupted service treated every Seerr `Processing` request as whole-season acquisition coverage, but earlier runtime evidence established that `Processing` can remain stale for days without queue activity. `Processing` now supplies no integrity coverage. Recent local `Queueing` still supplies temporary whole-target coverage; queue-backed non-problem TV entries supply episode coverage, with genuinely unassigned active evidence covering a sole requested season.
- Released expectations are derived only from exact positive episode numbers with parseable air dates on or before the device's current date. Future and undated episodes are excluded. When detailed episode metadata is absent, Wholphin does not use `episodeCount` as a count-only fallback because it can include future episodes; stored expectations remain available instead.
- Exact acquisition coverage is intersected with the exact expected-number set. An unrelated/out-of-range queue episode must not reduce the missing count.

Implementation state after continuation

- Repaired Room annotation literals and missing service import.
- Added focused pure calculation tests, including disappearance/reappearance, exact-number coverage, count fallback, full-season coverage, and Specials exclusion.
- Added released-expectation tests for future, undated, count-only, and Specials behavior.
- `SeriesViewModel` observes persisted integrity separately from `SeriesState.seasons`, reconciles on details open/Seerr refresh and explicit refresh, and degrades by logging reconciliation errors without breaking the base Jellyfin page.
- `SeriesDetails` renders `Incomplete` and the localized missing-episode count through `SeasonCard.artworkOverlay`, so it shares the card focus transform. The integrity indicator takes precedence over request/partial overlays to avoid contradictory card status.
- Schema `app/schemas/com.github.damontecres.wholphin.data.AppDatabase/36.json` was generated and contains the intended composite key, user cascade, converters-backed TEXT fields, and both indexes.

Seerr season-detail correction

**Expected → Observed → Consequence**

The generated `TvDetails.seasons[]` type permits an `episodes` field, which initially suggested `/tv/{id}` could directly supply exact episode dates. Actual Seerr code disproves this: `mapTvDetails()` uses `mapSeasonResult()`, which emits season summaries without episodes; only `GET /tv/{id}/season/{seasonNumber}` uses `mapSeasonWithEpisodes()`. Wholphin must fetch the season-detail endpoint before deriving released episode numbers. The implementation now fetches those details in parallel only for locally present non-Special seasons during series reconciliation. A failed season metadata call is logged and omitted, allowing persisted expectations and the base Jellyfin page to continue working.

Validation note

Focused `*SeasonIntegrity*` JVM tests pass after adding `SeasonIntegrityDao` to the existing Hilt test replacement database module. The first full `testDefaultDebugUnitTest` run reached test execution but remained silent for several minutes and was manually stopped. A later clean resumed run completed successfully in 2m53s, so the full default-debug JVM suite is green; preserve the earlier interruption as execution history rather than a product failure. Production compilation is also green. Android migration/device and TV UI behavior remain to be validated.

An emulator was available and a focused 35→36 Room migration instrumentation test was added to `TestDbMigrations`. Attempting to run it did not reach instrumentation: the existing `defaultDebugAndroidTest` source set fails compilation in unrelated `InstrumentedBasicUiTests` because Compose test and AndroidX test symbols are unresolved (and the pre-existing `AndroidJUnit4` import in `TestDbMigrations` is unresolved). Do not interpret this as a 35→36 migration failure; the Android test harness must compile before the focused migration can execute. The generated schema and production Room/KSP compilation remain green.

23. Local validation workflow

Historical note: before I03, `Fast` and `Standard` required explicit filters and streamed complete command output. The current contract is documented at the top of this handoff and in `AGENTS.md`: classifier-selected no-filter operation is supported, output is concise, and full per-stage logs are retained. The script still never runs `clean`.

Environment behavior

**Expected → Observed → Consequence**

Ordinary shells may not provide `JAVA_HOME`, and sandboxed Codex shells can otherwise resolve Gradle's home incorrectly. The script honors a valid existing `JAVA_HOME` or `java.exe` on `PATH`, then falls back to Android Studio's bundled JBR under `%ProgramFiles%\Android\Android Studio\jbr`. When `GRADLE_USER_HOME` is unset it derives `%USERPROFILE%\.gradle`; no username-specific path is stored in the repository.

Enabled local optimizations

- Normal validation uses the Gradle daemon; `--no-daemon` is intentionally absent. CI remains unchanged because short-lived isolated CI workers have different lifecycle requirements.
- `org.gradle.caching=true` enables Gradle's task output cache.
- `org.gradle.parallel=true` is safe for the two-module app/stub dependency graph. Its benefit is expected to be modest because this is not a large multi-project build.
- `org.gradle.configuration-cache=true` was verified against the actual `:app:compileDefaultDebugKotlin` graph, including OpenAPI generation, Room/KSP, protobuf, and the MPV stub. The first cache-enabled compile stored an entry and completed in 1m19s; the immediately repeated no-change compile explicitly reused it and completed in 3s. A first Fast targeted-test run stored its task-specific entry in about 1m32s; the repeated run reused it and completed in about 4.35s.
- Existing Gradle incremental compilation remains enabled by default. No `clean` is used locally because it would discard those incremental and cached outputs.

Investigated but not changed

- The daemon heap remains 2 GiB. Current compilation and tests complete without memory pressure, so increasing it toward CI's 8 GiB would consume more local memory without evidence of benefit.
- No worker-count override was added; Gradle should size workers for the machine, and the project has only two modules.
- Android instrumentation is not part of Standard or Full yet. The existing `defaultDebugAndroidTest` source set currently does not compile due to unresolved Compose/AndroidX test dependencies described above; adding a predictably failing step would make the validator misleading. Restore the test harness first, then add connected checks deliberately.
- Repository CI `clean` and `--no-daemon` behavior was left untouched. This task optimizes reusable local development, not isolated CI/release reproducibility.

Historical validation levels before repository-wide pre-commit parity (current commands/policy are in [AGENTS.md](AGENTS.md#validation-workflow))

- Fast: explicitly filtered default-debug JVM tests only; these naturally compile the required production/test graph.
- Standard: explicitly filtered tests for the current change, production Kotlin compile, focused acquisition/Downloads regressions, and `git diff --check`.
- Full: production Kotlin compile, the complete default-debug JVM suite, default-debug APK assembly, and `git diff --check`. During ordinary implementation it can be handed off for user-run validation; explicitly authorized prepare-pr publication now runs it autonomously.

24. Persistent snapshot design superseded

The full persisted Season Integrity snapshot described in sections 16–22 was implemented and evaluated, then deliberately rejected before schema 36 shipped. Preserve those sections as design history; the conclusions below supersede their persistence semantics.

**Expected → Observed → Consequence**

Persisting complete and incomplete rows initially appeared necessary to remember released-episode expectations across app restarts and Seerr outages. The same rows also persisted live Jellyfin counts, missing numbers, and acquisition-adjusted conclusions. Those derived values could be displayed before a fresh reconciliation and therefore made a stale observation look like current library truth. Schema 36 has been reshaped directly: Wholphin persists only exact released-episode expectations and their user/series/season/TMDB identity plus update time. Playable, physically missing, actively covered, unattended missing, and incomplete are calculated in memory from a fresh Jellyfin inventory whenever the series is opened or refreshed.

Product boundary

- Wholphin provides contextual diagnostics; it does not continuously audit or repair the whole library.
- No background or periodic integrity reconciliation is introduced.
- A missing or untrustworthy expectation produces no complete/incomplete claim.
- Current acquisition coverage may suppress the user-facing unattended warning, but never changes the physical missing set.
- Stale Seerr `Processing` remains insufficient acquisition proof.

Implementation consequences

- `season_integrity_expectations` contains no live Jellyfin or derived missing fields.
- Stored conclusions are no longer observed by `SeriesViewModel`; each displayed warning follows a fresh Jellyfin inventory query.
- Detailed Seerr season metadata is fetched for uncached local seasons, or for all local seasons only on explicit refresh. Routine Seerr updates reuse the cache.
- Jellyfin season/episode traversal is shared by acquisition readiness and live integrity evaluation, preserving playable episode IDs and exact season navigation.
- The earlier no-pruning decision remains conservative: transient Seerr absence does not delete trusted expectations, and Jellyfin user deletion still cascades them.

25. Standard validation test isolation

**Expected → Observed → Consequence**

The first external Standard run after the expectation-cache reduction passed focused Season Integrity tests and production compilation. Its combined acquisition regression invocation reached `:app:testDefaultDebugUnitTest` without reporting individual tests, and the user stopped it about 30 seconds later. No assertion failure, exception, `BUILD FAILED`, or failure XML was produced; Gradle left only zero-byte in-progress result files. This is consistent with the previously observed silent test-task behavior—the earlier full JVM suite also appeared idle for minutes before completing in 2m53s—and is not evidence of a specific failed test or deadlock.

The combined filter also selected both `SeerrAcquisitionTest` and the much larger coroutine-based `SeerrAcquisitionTrackerTest`, plus `SeerrRequestPaginationTest` and the large `DownloadsPageTest`, so its last console line cannot identify a class. Standard validation now runs those four classes as separate fail-fast steps. This adds small Gradle invocation overhead but makes a future stop/failure attributable to a single class. For an apparent stall inside one class, rerun that exact class externally with Gradle `--info` before changing product code.

The isolated tracker class subsequently stalled after eight completed tests while consuming CPU. Its tests inject virtual time and do not depend on wall-clock delays. The test helper creates a tracker whose independent `SupervisorJob` uses the same `TestCoroutineScheduler`; each test previously called `stopForeground()` only after all assertions. If an assertion failed, cleanup was skipped and the infinite polling loop could keep advancing virtual time, hiding the assertion behind an apparent hang. JUnit 4's default method hash order identified `multiSeasonQueueingReconcilesOnlyRepresentedSeason` as the likely ninth method; the cleanup change confirmed it by exposing its `queueingRequests.single()` failure in 0.287 seconds. The helper now registers `stopForeground()` with `runTest`'s `backgroundScope` completion so failures terminate polling and become reportable. This is test-harness cleanup, not a change to acquisition semantics or the production singleton lifecycle.

The isolated assertion was also a fixture lifecycle defect rather than a readiness regression. It registered Queueing before the tracker collected its initial Seerr session; `resetSession(session)` then correctly cleared session-scoped Queueing and ledger state, leaving `.single()` with an empty list. The test now establishes the session against an empty snapshot, registers the multi-season submission, then publishes authoritative season-1 evidence and requests a refresh. This matches the production request lifecycle and preserves the invariant that only represented season 1 reconciles while sibling season 2 remains Queueing. Shared Jellyfin inventory extraction does not participate in the tracker's internal test constructor and did not cause the failure.

The complete tracker class then exposed the same fixture-ordering defect in `requestPresenceAloneDoesNotRemoveQueueingWithoutAuthoritativeRow` and `futureAuthoritativeTimestampDoesNotCreateQueueingVisibilityGap`. Several neighboring reconciliation tests happened to pass for the wrong reason because the initial session reset erased Queueing before their expected-empty assertions. **Expected → Observed → Consequence:** those tests appeared to validate authoritative replacement, but they registered local Queueing before the tracker had established its session, so they were actually validating session cleanup. All Queueing reconciliation fixtures now start the tracker against an empty authoritative snapshot, allow the initial session/poll to run, register Queueing, and only then publish replacement evidence and request refresh. The production tracker was not changed: request presence alone and a future/skewed timestamp remain insufficient replacement proof; eligible queued, active acquisition, and Jellyfin-ready evidence still reconcile Queueing; TV reconciliation remains season-specific.

The validator's first logging correction converted native PowerShell output/error-record objects to strings before passing them to `Add-Content`. A later successful Standard run disproved that as a complete fix: repeated per-line `Add-Content` writer creation still intermittently emitted `Stream was not readable` while Gradle continued. The validator now opens one `StreamWriter` in truncate/create mode for the entire invocation, permits concurrent readers such as the IDE, auto-flushes every line, and disposes it in `finally`. This preserves one fresh current `validation.log` per run without repeatedly reopening the file.

External Standard validation after these corrections completed successfully in 4m02s. All seven isolated steps passed: targeted Season Integrity JVM tests, production Kotlin compilation, acquisition model tests, the complete 26-test acquisition tracker class, Seerr pagination tests, Downloads page tests, and `git diff --check`. The logger produced a complete final summary without the prior unreadable-stream error. The remaining `git diff --check` messages are Git's informational LF-to-CRLF working-copy warnings, not whitespace failures.

Recently Completed retention correction

The readiness transition timestamp must describe an observed transition, not tracker startup. **Expected → Observed → Consequence:** first observation of already-playable Jellyfin content was stamped with the current poll time, causing arbitrarily old movies and TV seasons to appear newly completed. With no previous tracker state, ready content now receives no invented Jellyfin-ready timestamp. A previous not-ready state followed by ready is stamped with the current time, while a previous ready state retains its existing timestamp. Downloads continues to prefer a genuine Jellyfin-ready timestamp and may conservatively fall back to the corresponding Seerr request/season availability timestamp; `media.updatedAt` remains prohibited because unrelated metadata refreshes mutate it.

The rolling Recently Completed window is seven days rather than 24 hours. Seven days lets users return after several days and still see operational outcomes, while natural time-based expiry keeps Downloads from becoming a request archive. There is no completed-item count cap. Prior Jellyfin readiness is merged into fresh snapshots before retention filtering so every genuine completion inside the seven-day window remains eligible even beyond the separate terminal-request sampling set.

Cold-start readiness rehydration

**Expected → Observed → Consequence**

After reinstall, Seerr availability timestamps could reconstruct Recently Completed membership, but in-memory `jellyfinReadiness` and Jellyfin IDs were empty. The tracker does not publish between metadata enrichment and readiness resolution; `retainJellyfinReadiness()` only preserves IDs inside the current process and cannot restore them after restart. The actual mismatch was between resolution paths: Discover `GO TO` uses Seerr's explicit `mediaInfo.jellyfinId`, while `JellyfinAcquisitionReadinessService` ignored that ID and relied on a title search limited to 20 Jellyfin results followed by TMDB matching. Thus Discover could navigate while Downloads remained unresolved during the same session.

Readiness reconstruction now prefers the explicit Seerr-provided Jellyfin ID as a lookup key. It fetches that item fresh from Jellyfin, verifies its ID and media kind, and still requires media sources for movie readiness or the shared series inventory for TV season readiness and exact season IDs. If the explicit lookup does not resolve, the prior title/TMDB search remains as fallback; if neither resolves, readiness remains false and `DownloadDisplayItem.destination()` correctly falls back to Discover. Seerr `AVAILABLE` alone is still never treated as Jellyfin readiness.

The inverse independence is equally important: readiness is not gated on Seerr `AVAILABLE` or on a populated Seerr Jellyfin ID. Focused service tests protect both a missing hint and a stale/unresolvable hint while Seerr still reports `PROCESSING`; independent Jellyfin title/TMDB discovery can establish playability in either case. Treat `jellyfinId` only as an optional exact lookup optimization, never as the authority or a prerequisite.

Focused external validation for the cold-start correction passed across `JellyfinAcquisitionReadinessServiceTest`, `SeerrAcquisitionTrackerTest`, and `DownloadsPageTest`. An initial test-compilation failure was limited to untyped MockK request matchers; specifying `GetItemsRequest` exposed the intended `ids`/`searchTerm` properties, after which the readiness service test and the combined three-class suite passed.

Focused external validation passed for the complete `SeerrAcquisitionTrackerTest` and `DownloadsPageTest` classes in 2m02s after this correction. This confirms the readiness transition rules and seven-day Downloads projection together; broader Standard validation remains the final regression checkpoint.

External Standard validation then completed successfully in 5m14s. The task-targeted tracker and Downloads tests, production Kotlin compilation, stable acquisition/tracker/pagination/Downloads regression groups, and `git diff --check` all passed. The seven-day Recently Completed correction is therefore green at the normal regression checkpoint.

26. Deterministic series season ordering

**Expected → Observed → Consequence**

The series overview requested Jellyfin seasons with `IndexNumber ASC`, but exposed the returned lazy `ApiRequestPager` directly to the season tabs. Real Jellyfin responses were not consistently ordered, so the same UI could show Season 2 before Season 1. The details-card projection was already deterministic because it sorts numeric season keys. `SeriesViewModel.getSeasons()` now materializes the small paged season result and normalizes it by the actual Jellyfin `indexNumber`; Season 0/Specials sorts first, matching the existing numeric convention, and missing numbers sort last. Direct Downloads navigation remains ID-based: after sorting, the initial tab index is found using the unchanged Jellyfin season ID (with the existing season-number fallback behavior inside `checkNumberOrId`). Do not replace this with title sorting or reintroduce reliance on server result order.

A later runtime report correlated reverse ordering with a Jellyfin Sort Title on only one season (`indexNumber` values remained correct). The current source already normalized `SeriesViewModel` state, and Standard validation does not install the compiled app, so an older deployed APK is a plausible explanation and must be ruled out during manual verification. As a defensive final-boundary invariant, `SeriesOverview` now also derives one numeric `indexNumber`-ordered collection and uses that exact collection for tab rendering, initial episode loading, and tab-change lookup. This prevents any future unsorted state producer from making metadata such as Sort Title affect visible order or index-to-season actions. ID-based initial selection remains calculated after ViewModel normalization and is unchanged.

External Standard validation for this correction completed successfully in 3m14s with `SeriesSeasonOrderingTest` as the explicit targeted filter. Production compilation and the stable acquisition model, acquisition tracker, Seerr pagination, Downloads page, and whitespace regression steps all passed. Direct season navigation had already been manually validated before this ordering-only correction; the next manual check is that a Downloads deep link still selects the intended season while the tab headers remain numerically ordered.

The persistent validation-log writer was subsequently exercised by an external Fast validation run, not merely a synthetic file-access probe. The targeted JVM tests completed successfully in 1m06s, `validation.log` contained the complete success footer, and a post-run scan found zero `Add-Content` or `Stream was not readable` matches. This confirms the single invocation-scoped `StreamWriter` correction under real Gradle output; the former per-line `Add-Content` implementation must not be restored.

27. Unresolved TV cold-start destination gate

The earlier cold-start readiness conclusion was incomplete for TV. **Expected → Observed → Consequence:** the explicit Seerr Jellyfin ID can resolve the Jellyfin series, and `JellyfinSeriesInventoryService` can reconstruct numeric season IDs plus playable episode IDs before the tracker publishes. When Seerr metadata also supplies the requested season's expected episode count, `seasonReady(...)` is true and the row is legitimately projected as `AVAILABLE`. On first observation, however, transition stamping intentionally leaves `jellyfinSeasonReadySinceEpochMillis` empty so it does not invent a completion time; the row remains in Recently Completed using the historical Seerr season-availability timestamp. `DownloadDisplayItem.destination()` incorrectly requires that absent ready-since entry before consulting the reconstructed series/season IDs, so it falls back to Discover despite current Jellyfin readiness being proven. Movies work because their destination path requires the reconstructed movie ID but does not require `jellyfinReadySinceEpochMillis`.

This is a navigation-condition bug, not failure to retain history or reconstruct TV identity. Completed TV navigation now gates on current `jellyfinReadiness.seasonReady(seasonNumber, seasonEpisodeCounts[seasonNumber])`, while continuing to require the verified Jellyfin series/season identity for exact-season navigation. The ready-since timestamp remains completion-history metadata and is not a prerequisite for navigation. No timestamp is synthesized and Seerr `AVAILABLE` is not readiness proof. Existing seams are `JellyfinAcquisitionReadinessServiceTest` for inventory reconstruction, `SeerrAcquisitionTrackerTest` for cold-start publication/transition stamping, and `DownloadsPageTest` for the final destination predicate.

The initial focused run exposed three older Downloads fixtures that claimed current readiness using only a historical ready-since timestamp. The fixtures were corrected to include positive expected counts and matching playable episode identities, including Season 0/Specials; no Specials-specific production exception was introduced. A focused `DownloadsPageTest` run then passed in 16s, followed by successful external Standard validation in 5m41s across targeted tests, production Kotlin compilation, all stable acquisition/Downloads regression groups, and the whitespace check.

Pre-checkpoint review found one stale series refresh path created by the season-ordering materialization. `getSeasons()` now returns a numerically sorted plain `List<BaseItem?>`, but `SeriesViewModel.refresh()` still attempted `(state.value.seasons as? ApiRequestPager<*>)?.refresh()`. That cast could no longer succeed, so explicit refresh updated Seerr metadata, released-episode expectations, and the fresh integrity inventory while reusing the old visible Jellyfin season collection. Refresh now re-runs `getSeasons()`, publishes the fresh numerically ordered collection, and passes it to `updateSeerrDetails()`. Selection is correlated by exact Jellyfin season ID; a surviving selection moves to its new sorted index, while a removed selection falls back to the first ordered season and reloads that season's episodes on the Overview page. The `seasons is ApiRequestPager<*>` compatibility branch in `updateSeerrDetails()` remains obsolete but harmless and was intentionally left outside the fix.

28. Pre-UI checkpoint audit and Full validation

The supplied external Full validation completed successfully in 5m21s: production Kotlin compilation, the complete default-debug JVM unit suite, default-debug APK assembly, and `git diff --check` all passed. This supersedes the preceding focused and Standard checkpoints; no redundant Gradle run is needed before creating the pre-UI engineering checkpoint.

The final audit found no accidental debug surface, temporary file, duplicate readiness implementation, or surviving persistent complete/incomplete snapshot. The remaining ready-since timestamp checks belong to recent-history membership/projection and ledger retention, not current navigation authority. Numeric season sorting at both ViewModel materialization and the final series-tab boundary is intentional defense against Jellyfin response and Sort Title ordering. The obsolete `ApiRequestPager` compatibility branch inside `updateSeerrDetails()` is harmless legacy code and is not used by explicit refresh.

The checkpoint architecture is therefore: Jellyfin remains playability authority; Seerr `jellyfinId` is only an optional lookup hint; request, acquisition, and availability are separate dimensions; Recently Completed is an uncapped rolling seven-day operational history; exact TV navigation requires current authoritative season readiness plus Jellyfin series/season IDs; and incomplete-season diagnostics persist only released-episode expectations while deriving the current conclusion contextually. The tree is suitable for a Git checkpoint before UI work. The Room 35-to-36 migration instrumentation path remains subject to the already documented pre-existing Android-test dependency limitation and was not part of the Full JVM/APK workflow.

29. Enhanced-feature gating boundary and implementation plan

The first gating inventory incorrectly treated Discover as a fork-added surface. **Expected → Observed → Consequence:** names such as `SeerrDiscoverPage` suggested that Discover belonged to the recent acquisition work, but Git history shows upstream commit `4c7c465c` added Wholphin's Seerr integration and the current `upstream/main` already contains `Destination.Discover`, `DiscoveredItem`, `DiscoverMoreResult`, all five Discover tabs, Seerr search/request history, request actions, availability indicators, and Seerr-similar enrichment on Movie, Series, and Person pages. The new master must therefore leave those upstream surfaces and behaviors intact. It gates only fork-added acquisition, Downloads, merged/missing-season, request-more-seasons-on-Jellyfin-Series, added series availability, and contextual integrity capabilities. Improved request-dialog presentation, numeric season ordering, exact-ID navigation, refresh fixes, and focus/scroll fixes are independent improvements and remain active.

The gating architecture uses protobuf DataStore for user intent and a central semantic capability resolver. Consumers observe capabilities such as Downloads, acquisition tracking/progress, missing seasons, Series request enhancements, and season integrity rather than a raw master Boolean. Initially one master drives all capabilities; future sub-switches can be resolved centrally without rewriting consumers. Seerr configured, Seerr reachable, and enhanced features enabled remain independent facts. Low-level `SeerrService`, integrity, Jellyfin inventory, and readiness services stay preference-agnostic; gating belongs at lifecycle, navigation, ViewModel projection, and source-activation boundaries.

Runtime OFF policy: stop and deactivate acquisition polling promptly; clear or hide transient tracker/Queueing state; remove Downloads navigation and reject a restored Downloads route; republish open Jellyfin Series pages from the local Jellyfin season collection without placeholders, acquisition overlays, added availability, or Incomplete diagnostics; and suppress acquisition-only side effects after otherwise normal upstream request submission. Do not delete Seerr configuration or persisted released-episode expectations. Runtime ON restores navigation and eligible foreground polling/enrichment, including an immediate tracker refresh consistent with its existing lifecycle. Upstream Discover remains available under its existing `SeerrServerRepository.active` rule in either state.

Implementation checkpoints are: (A) migration-safe master preference, capability model/resolver, and focused default/dependency tests; (B) thin application lifecycle controller and tracker deactivation tests; (C) Downloads navigation/direct-route gating; (D) Series local-only versus enhanced projection; (E) acquisition-only side-effect gating in upstream Discover request ViewModels and remaining call-site audit; (F) one user-facing master switch, followed by ON/OFF regression validation. The feature gate controls whether independent domain sources are active/exposed and must not collapse library/playability, request/availability, acquisition, integrity, watchlist, or quality into a single status.

Implementation chose a protobuf tri-state rather than a Boolean: a fresh DataStore default is explicitly disabled, an absent/unspecified field from an installation whose preferences predate the feature resolves enabled to preserve existing behavior, and subsequent user choices persist explicit enabled/disabled values. `EnhancedFeatureGate` begins in a not-loaded/disabled state so background work cannot start during DataStore loading. The initial semantic capability set is Downloads, acquisition tracking, acquisition progress, missing seasons, Series request enhancements, and season integrity; dependency resolution centrally removes Downloads/progress when acquisition tracking is unavailable, although only the master switch is currently exposed.

`EnhancedFeatureController` is the thin foreground-policy owner. Activity foreground alone no longer starts acquisition polling: controller state combines foreground with the acquisition capability, uses ordinary stop on background to retain the established session behavior, and uses tracker deactivation on feature OFF to cancel work, reset fast polling, and clear session/ledger/Queueing projections. Downloads is omitted from the drawer; a restored/direct Downloads route is redirected to Home once gate state is loaded, with `DestinationContent` also rendering Home defensively during the transition. Discover routes remain untouched. `SeriesViewModel` observes the capability alongside existing Seerr activity, publishes local Jellyfin seasons and clears only fork-added Series projection fields when disabled, and defensively guards Series-only request actions. Upstream Discover requests still submit/cancel normally; only their post-success local Queueing registration and tracker refresh are suppressed. Search, Movie, Person, and upstream Seerr-similar behavior required no gate.

Action-side checks alone were rejected as insufficient because a toggle can race between a ViewModel check and tracker mutation. The production tracker therefore also receives a semantic acquisition-enabled predicate and defensively rejects start, refresh, fast-polling, and Queueing registration while disabled. Its internal test constructor defaults this predicate to enabled, preserving all existing tracker fixtures and semantics.

External validation for the completed gating implementation passed at both checkpoints. Fast validation compiled the application and passed `EnhancedFeatureGateTest`, `EnhancedFeatureControllerTest`, and `SeerrAcquisitionTrackerTest` in 4m17s. Standard validation then completed successfully in 6m15s across those targeted tests, production Kotlin compilation, acquisition model and tracker regressions, Seerr pagination, Downloads page regressions, and `git diff --check`. The implementation is therefore green at the normal regression checkpoint; runtime TV verification of live ON/OFF presentation remains useful but is not a known automated-validation failure.

Manual runtime testing subsequently confirmed intended ON/OFF behavior and that upstream Discover remains intact. One minor UI issue is deferred: on Series navigation the contextual `Incomplete` pill can briefly appear, disappear, and reappear as projection/reconciliation state settles. Do not change the current badge experiment or integrity semantics while building the identity foundation.

30. Shared media identity and acquisition-index checkpoint plan

The next shared-state step must remain incremental and reversible. `MediaKey` is an optional correlation seam, not a replacement for `BaseItem`, `DiscoverItem`, Jellyfin pagers, ViewModels, destinations, cards, or validated acquisition models. No existing screen is required to consume it, no combined state is persisted, and no network or tracker lifecycle behavior changes. Prefer isolated pure mappings and a read-only adapter over `SeerrAcquisitionTracker.state`; future Watchlist, Collections, quality, Discover, or UI branches must be able to proceed without adopting this layer.

Identity safety rules: Jellyfin UUID identity is scoped to a Jellyfin server; TMDB catalog identity includes explicit movie/series media type; seasons and episodes are scoped below a known series identity and numeric season/episode; Season 0 is valid identity without implying integrity semantics. Seerr request IDs, Seerr media IDs, Servarr IDs, and `downloadId` are not media identity. Title/year matching is never authoritative. Missing safe provider identity remains unresolved, except that an existing Jellyfin item may still expose its server-scoped local identity.

The acquisition index will preserve collisions rather than choosing one request as truth: a logical media key maps to an ordered list of request-scoped acquisition entries, retaining request ID and 4K distinction. Movie requests index at movie identity; TV projections index each represented/requested season independently beneath series identity. Unresolved catalog acquisitions are omitted deliberately. Disabled tracker state naturally yields an empty index because deactivation clears published requests and Queueing state; the adapter performs no additional polling or network work.

Implemented identity shape: `MediaKey.Catalog` contains typed movie/series TMDB identity; `MediaKey.Local` contains Jellyfin server UUID, item UUID, and explicit local media type; `MediaKey.Season` and `MediaKey.Episode` require a known catalog or local series parent and non-negative numeric coordinates. Jellyfin movie/series mapping prefers a valid positive TMDB provider ID and otherwise returns local identity. Jellyfin descendants use hierarchical identity only when the caller supplies a known series key and the required numbers; otherwise their safe server-scoped local item identity remains available. Discover movie/TV IDs map to typed TMDB catalog keys; people, unknown types, non-positive IDs, and malformed provider IDs are never guessed from titles.

`AcquisitionStateIndex` is an isolated read-only `StateFlow<AcquisitionIndexSnapshot>` over tracker snapshots. It indexes movie requests by typed catalog key and TV requests under every non-negative requested or authoritatively represented season. Values are deterministic lists ordered by request ID, normal before 4K, and authoritative before provisional Queueing. This deliberately preserves multiple requests, quality variants, and simultaneous authoritative/Queueing representations rather than silently overwriting one. Entries without safe TMDB/type identity, and TV entries without any season scope, are exposed in `unresolved` instead of assigned a false key. The adapter performs no lifecycle calculation, mutation, persistence, or network work, and no existing consumer was migrated to it.

External Standard validation for the identity/index checkpoint completed successfully in `00:08:19.0908900`. Targeted `MediaKeyTest` and `AcquisitionStateIndexTest`, production Kotlin compilation, acquisition model regressions, acquisition tracker regressions, Seerr pagination regressions, Downloads page regressions, and the Git whitespace check all passed. The complete log is `C:\Projects\Wholphin\Wholphin\validation.log`. The isolated compatibility seam is therefore validated without migrating any existing consumer.

31. Keyed integrity-state source checkpoint

The second shared-state domain is exposed through an additive read-only `IntegrityStateSource`. `SeasonIntegrityService` remains the sole owner of expectation persistence, fresh Jellyfin inventory lookup, acquisition-coverage reconciliation, and complete/incomplete calculation. After an existing contextual `evaluate()` call finishes, it replaces that series' in-memory observation in an internal store; the keyed source never starts evaluation, performs network work, polls, or writes Room state. No UI or existing ViewModel consumes the source yet.

Integrity is indexed primarily as `MediaKey.Season(MediaKey.Local(serverId, seriesItemId, SERIES), seasonNumber)`. This is deliberate: the state describes one Jellyfin library observation, while persisted rows are scoped to a Jellyfin user and series UUID. A positive cached/evaluation TMDB ID is carried only as an optional catalog-season alias on the exposed state. It is not promoted to the primary key because the current integrity layer does not persist a verified local-to-catalog alias contract and a catalog-only key could collapse independent local observations. The future coordinator will need an explicit, verified alias/join step to combine this local integrity key with the catalog-keyed `AcquisitionStateIndex`; title/year matching remains forbidden.

`MediaKey.Local` remains server-scoped rather than user-scoped because Jellyfin item identity is shared by users on one server. User isolation is enforced at the source boundary: observations carry the originating Jellyfin user row and are exposed only for the currently active server/user session. A session switch cannot expose another user's cached observation. Season 0 remains representable by the identity adapter even though the current integrity calculation intentionally emits no Specials conclusion.

The exposed `IntegrityState` preserves explicit COMPLETE/INCOMPLETE assessment, missing count, exact missing numbers when known, and the current expected/playable/physical-missing/acquisition-covered sets. Absence from the requested-key map represents UNKNOWN; the adapter does not manufacture a conclusion. Its shape can also preserve a count-only result with null exact-number fields without inventing episode numbers, although current released-expectation derivation deliberately produces only safe exact-number observations. Empty requested keys, no active user, a disabled integrity capability, or no matching observation all produce an empty map. Disabling therefore hides enhanced integrity state without deleting persisted expectations or altering the existing Series projection.

External Standard validation for the keyed integrity-source checkpoint completed successfully in `00:07:46.6195703`. The focused `IntegrityStateSourceTest`, production Kotlin compilation, established acquisition model and tracker regressions, Seerr pagination regressions, Downloads page regressions, and `git diff --check` all passed. The complete log is `C:\Projects\Wholphin\Wholphin\validation.log`.

32. Combined acquisition + integrity product-state checkpoint

The first combined layer is an additive read-only `MediaProductStateCoordinator`. Its immutable `MediaProductState` contains the complete ordered list of indexed acquisition entries plus an optional integrity observation. It observes `AcquisitionStateIndex` and `IntegrityStateSource`, applies no lifecycle or rendering policy, performs no network work or polling, persists nothing, and is not a source of truth. Requested keys remain present even when both enhanced domains are absent, so base/local media identity does not depend on either capability.

Exact-key merging alone was rejected because acquisition is primarily catalog-keyed while integrity is primarily local-Jellyfin-keyed. The deliberately small resolution seam is `SeasonMediaAlias`, which permits only a server-scoped local SERIES season and a typed TMDB SERIES season with the same numeric season. Resolution is bidirectional for the requested observation only; it is not a global alias graph. The coordinator also accepts the catalog-season alias already carried by a current integrity observation. Conflicting aliases are treated as ambiguous and are not used to attach acquisition state. Missing aliases leave whichever independent facts are safely keyed rather than using title/year, request, Seerr media, or Servarr identity to guess.

Multiple acquisition entries remain intact. Direct-key facts are retained, and safely aliased facts are combined without selecting a preferred request. Source capability behavior remains independent: an empty/disabled acquisition index removes acquisition only, while an empty/disabled integrity source removes integrity only. The coordinator contains no raw master-toggle check.

The first migrated consumer is the existing Jellyfin Series details season-card projection. `SeasonIntegrityService.evaluate()` still owns and triggers contextual reconciliation exactly as before; after it publishes the result, `SeriesViewModel` requests product state for the current server-scoped series seasons and supplies exact typed TMDB season aliases when Seerr series identity is safely known. `SeriesDetailsSeason.integrity` now carries the coordinator's `IntegrityState`, but `SeriesDetails` still evaluates the same `incomplete` condition and missing count. The current Incomplete pill, focused subtitle, priority, dimensions, request flow, season collection, and navigation are unchanged. Acquisition state is available in the combined result but is intentionally not presented yet.

This is the only migrated consumer. Existing BaseItem/DiscoverItem models, other ViewModels/cards, Downloads, pagers, navigation, acquisition calculations, integrity reconciliation, and persistence remain unchanged. The deferred initial-load Incomplete-pill flicker is expected to remain because the Series projection still clears enhanced state before contextual evaluation repopulates it; eliminating that sequencing is outside this architecture checkpoint.

External Standard validation for the combined product-state checkpoint completed successfully in `00:06:04.0352664`. Its targeted coordinator and Series projection tests, production Kotlin compilation, established acquisition model and tracker regressions, Seerr pagination regressions, Downloads page regressions, and `git diff --check` all passed. The complete log is `C:\Projects\Wholphin\Wholphin\validation.log`.

33. Series season-card acquisition-progress experiment

The first acquisition presentation outside Downloads is deliberately limited to the existing Series details season card. `SeriesViewModel` keeps an active observation of `MediaProductStateCoordinator` for the current local season keys, so acquisition-index changes update the card projection without querying the tracker or Seerr from Compose. The projected `SeriesDetailsSeason.acquisitionProgress` is presentation-only and does not alter acquisition lifecycle state.

A rail is eligible only when the combined state contains exactly one acquisition entry, that entry resolves to the same season's existing TV aggregate, the aggregate has the established `hasActiveProgress` evidence, is not `isFinishing`, and exposes a finite fraction strictly between zero and one. Multiple request/quality entries are intentionally treated as ambiguous rather than aggregated. Queueing, Processing, queued-without-measured-progress, Finishing, complete, invalid, and absent/disabled acquisition state expose no rail.

`SeasonCard` gained one optional `artworkProgress` parameter. When present, it renders within the transformed artwork box using the same bottom-start geometry, `Cards.playedPercentHeight`, and tertiary theme color as the existing Jellyfin playback-progress treatment. Existing callers default to no rail. If the card already has a visible Jellyfin playback-progress fraction, playback takes precedence and the acquisition rail is suppressed so two bottom-edge bars are never drawn. The rail and top-left Incomplete badge may coexist because integrity remains independently calculated and can legitimately report uncovered missing episodes while another acquisition has measurable progress; no new Repairing/Reacquiring priority was invented.

No text, percentage, ETA, pill, indeterminate state, or other card/screen was added. The Incomplete badge, focused subtitle, card dimensions, focus behavior, request flow, and existing playback rendering are unchanged. Capability OFF removes acquisition entries at the source/index boundary, so the rail disappears without a raw UI feature check. The deferred initial-load Incomplete-pill flicker remains outside this experiment. This visual is provisional until manually reviewed on Android TV.

The first manual comparison exposed a projection mismatch rather than a rendering defect. **Expected → Observed → Consequence:** the Series rail initially read the raw `SeerrAcquisitionState.Tv` queue aggregate, while Downloads displayed the episode-normalized result from `toTvSeasonTargets()` / `analyzeTvSeasonAcquisition(...)`. Raw bytes can materially differ from season display progress when a queue row represents one episode, a season pack, or when Jellyfin has already confirmed playable episodes. `SeasonCard` was already filling the full artwork width correctly, so its geometry must not be adjusted to compensate.

`TvSeasonAcquisitionProjection` is the canonical TV season display projection. `AcquisitionStateIndex` now derives each requested season's existing `TvSeasonTarget` once through `toTvSeasonTargets()` and carries it beside the request-scoped indexed acquisition. This retains separate request IDs, normal/4K variants, and multiple projections without selecting a winner. Cross-screen consumers of shared media state must use that canonical target/projection rather than the raw TV aggregate. The Series card keeps its conservative exactly-one-acquisition rule, but its fraction now comes from the indexed canonical aggregate, matching Downloads without duplicating normalization in the ViewModel or Compose.

External Standard validation for the canonical shared TV progress correction completed successfully in `00:11:17.8705068`, including the focused index/coordinator tests, production Kotlin compilation, established acquisition/tracker/pagination/Downloads regressions, and `git diff --check`.

34. Shared artwork-progress seam and second card consumer

`ItemCardImage` owns only the geometry and precedence of the bottom-edge artwork rail. It accepts an optional UI-only `CardMediaPresentation` and does not import product state, acquisition records, feature gates, Seerr models, or integrity models. Existing playback progress remains controlled by the existing `showOverlay` behavior. When a visible valid playback fraction exists it wins; otherwise an explicitly supplied valid acquisition fraction may use the same full-width container, thickness, clipping, and tertiary color. At most one rail is rendered. Focus captions, integrity meaning, acquisition selection, and status priority remain outside the shared image primitive.

`SeasonCard` retains its source-compatible `artworkProgress` input but now forwards it as presentation to `ItemCardImage`; its duplicate rail renderer was removed. The second real consumer is deliberately limited to movie cards on the finite Seerr Requests page. `SeerrRequestsViewModel` observes shared product state for typed TMDB movie keys and a pure projector requires exact Seerr request ID plus normal/4K identity before exposing the canonical movie aggregate fraction. Empty acquisition state (including enhanced capability OFF), unrelated requests, ambiguous matching records, Queueing/Finishing, and invalid progress yield no presentation. The upstream Requests page and `DiscoverItemCard` remain functional because all new inputs default to absent and cards contain no feature checks.

TV Discover/Requests progress remains deferred. A TV request can span multiple season-scoped canonical projections, and no series-poster aggregation or winner policy has been defined. GridCard, Library, Search, Home, Collections, Downloads, and other Discover consumers were not migrated. This keeps the proof incremental and prevents a card-level component from inventing cross-season semantics or accumulating unrelated status badges.

35. Series non-determinate acquisition-pill experiment

The next visual experiment remains limited to Jellyfin Series Details season cards. `CardMediaPresentation` now has a narrow `CardAcquisitionState` with only `QUEUEING`, `QUEUED`, and `FINISHING`; it does not introduce a universal primary state, arbitrary strings, integrity, watchlist, or quality fields. The pure Series projection maps local unreconciled `SeerrAcquisitionState.Queueing` to Queueing, canonical `TvSeasonLifecycle.QUEUED` to Queued, canonical Finishing to Finishing, and eligible canonical In-progress to the existing determinate fraction with no pill state. Canonical Available, absent state, unsafe identity, and ambiguous multiple acquisition records expose neither acquisition pill nor rail.

All three non-determinate states use one provisional cool-purple visual family: an 8sp semibold white text pill, 70% translucent `AppColors.Discover.Purple`, 4dp rounded corners, and the same compact top-left padding/geometry as the amber Incomplete pill. Focus does not change or expand it, normal season metadata remains visible, and no icon, spinner, animation, focused explanation, or non-determinate rail was added. The bottom rail therefore continues to mean that a meaningful numeric fraction exists.

Temporary coexistence follows the pre-existing Series rendering structure rather than establishing a permanent cross-domain priority system. Incomplete remains the single top-left pill when integrity is incomplete; a determinate acquisition rail may still coexist with it. When Incomplete is absent, a Queueing/Queued/Finishing pill is shown. On unavailable placeholders that pill occupies the existing top-left state position ahead of Pending/Partially Available, so text pills are not stacked; this priority is local to the experiment and must be judged on Android TV before wider reuse. Movie Requests progress, other Discover cards, GridCard, Library, Search, Home, Collections, Downloads, and TV series-poster aggregation remain unchanged.

Manual Android TV validation confirmed the experiment against live acquisition transitions. One season visibly progressed through Queueing -> Queued -> In progress, temporarily returned to Queued when authoritative state no longer exposed a meaningful numeric fraction, resumed In progress when measurable progress returned, and finally displayed Finishing. Concurrent Season 3 and Season 4 acquisitions retained independent state and presentation rather than collapsing into a series-wide winner. A season also transitioned successfully from a Seerr-backed placeholder card to the real Jellyfin season card after import/discovery without losing its acquisition presentation. **Expected -> Observed -> Consequence:** the keyed, request-scoped canonical season projection survived both simultaneous season activity and replacement of placeholder UI identity with authoritative Jellyfin season identity; the Series card experiment therefore reflects live lifecycle changes without requiring card-local acquisition logic. The temporary Queued phase remains an observed legitimate consequence of determinate-rail eligibility requiring a current meaningful fraction, not evidence that the renderer lost the acquisition.

36. Acquisition visibility outside the local library

Normal Movies and Series libraries remain strictly Jellyfin-local. A requested or acquiring title must not be inserted into their ordinary grids as a synthetic catalog item before Jellyfin discovers it. Library membership and acquisition activity are separate dimensions even when shared identity lets Wholphin follow the same logical title across both.

The primary lightweight pre-library surface will be a transient Home **Acquiring** row above existing content such as Recently Released and Recently Added. It represents current Queueing, Queued, In progress, and Finishing items and disappears completely when empty so the established Home layout closes the space naturally. Downloads remains the detailed operational surface for every active acquisition plus its rolling recent-history window. Discover remains exploration/request; the future Watchlist is the persistent local-or-non-local catalog of user interest. Movies and Series may later receive separate Acquiring rows, but those must remain distinct from their Jellyfin-local grids.

Movie cards may show exact lifecycle and reliable progress where identity is unambiguous. Series posters must not aggregate season percentages; they answer only whether acquisition activity exists somewhere within the series, while Series Details and Downloads retain exact season-scoped lifecycle and progress. Acquisition summary, library availability, integrity, and future Watchlist membership remain independent state rather than one combined status.

The intended product transition is **Discover / Watchlist -> Acquiring -> Jellyfin discovery -> Recently Added / normal library**. Jellyfin discovery, not Seerr availability or request presence, admits an item to the local library. Shared catalog/local identity should allow presentation to continue across that transition without moving acquisition authority into library queries. Empty or capability-disabled acquisition state yields no transient row and requires no raw feature-toggle checks in cards. This records direction only: Home, Movies, and Series acquisition rows are not implemented by this decision.

37. Indexed series-acquisition summary foundation

`SeriesAcquisitionSummary` deliberately contains only `NONE` and `ACTIVE`. It answers whether current acquisition work exists somewhere inside a series; it does not select a season/request/quality winner, aggregate percentages, or reproduce Queueing/Queued/In progress/Finishing at series level. `PROBLEM` remains deferred because failure/attention is independent of current activity and should not be collapsed into this Boolean summary.

The canonical `TvSeasonTarget.hasCurrentAcquisitionWork` fact is calculated beside `toTvSeasonTargets()`, not in the new index or UI. It is true for local provisional Queueing; a non-problem queue entry that is currently present; a non-successful non-problem entry retained by the existing `TV_PROGRESS_GRACE_POLLS` window; or explicit successful-transfer evidence still waiting for authoritative Jellyfin season readiness. A live queue entry therefore keeps an already-playable quality upgrade active. Bare Seerr `Processing`, availability without acquisition evidence, problem-only entries, expired provisional evidence, and completed evidence after Jellyfin readiness are false. This introduces no new timeout and leaves detailed lifecycle/progress unchanged.

`SeriesAcquisitionSummaryIndex` is an additive read-only singleton over `AcquisitionStateIndex.state`. Once per acquisition snapshot it folds qualifying `MediaKey.Season` entries by their typed TMDB `MediaKey.Catalog(SERIES, tmdbId)` parent and stores only ACTIVE keys; absence means NONE. Multiple seasons, requests, replacements, and normal/4K variants reduce with Boolean `any`, while unresolved identity is omitted rather than title/year matched. `observe(keys)` filters this already-derived shared map, so a page/grid needs one observation rather than per-card/per-season collectors, network calls, Jellyfin scans, or repeated full-history work. Complexity follows the tracker's currently retained acquisition records, not library size.

Catalog-series identity lets a future Watchlist or Discover placeholder consume the same summary before Jellyfin import and lets a local Jellyfin series with a verified TMDB provider ID continue using it afterward. A local series without verified catalog identity remains unresolved; no global alias graph was added. Tracker deactivation naturally empties the acquisition index and summary index, so future cards need no raw feature-toggle check. `MediaProductStateCoordinator`, cards, Home, Library, Discover, Watchlist, Downloads, navigation, persistence, and polling were not migrated or changed in this checkpoint. The foundation is intended for the future transient Home Acquiring row and optional later series-card consumers.

38. Home Acquiring data/source checkpoint

The movie counterpart to TV current-work evidence is `SeerrRequestAcquisition.hasCurrentMovieAcquisitionWork`, calculated in the acquisition model rather than Home presentation. It is true for local Queueing; a non-problem entry currently present in the queue; a non-successful entry inside the existing `TV_PROGRESS_GRACE_POLLS` ledger window; or explicit successful-transfer evidence still awaiting Jellyfin movie readiness. A live queue entry remains active when an already-playable movie is being upgraded or replaced. Bare Processing, availability without acquisition evidence, problem-only entries, expired provisional evidence, and successful completion after Jellyfin readiness are false. The existing grace constant is reused despite its TV-specific name; no new timeout or tracker behavior was introduced.

`HomeAcquiringSource` is a Home-specific, data-only singleton over `AcquisitionStateIndex.state`. It projects one shared `StateFlow<HomeAcquiringState>` and does no polling, network work, Jellyfin scan, persistence, or per-card collection. `HomeAcquiringItem` carries typed catalog identity, enriched `DiscoverItem` metadata, a separately verified Jellyfin movie/series item ID, optional unambiguous movie `CardMediaPresentation`, coarse series summary, immutable request time, and the contributing request IDs. Missing safe catalog identity or missing usable Discover metadata omits the visual item rather than inventing title/artwork identity.

Items deduplicate only by typed TMDB movie/series catalog key. Multiple requests, normal/4K variants, replacements, and multiple active seasons reduce to one logical card. Conflicting movie presentations preserve membership but expose no exact presentation instead of selecting a winner. Series membership reuses `toSeriesAcquisitionSummaries()` and remains only ACTIVE/NONE: there is no season winner or cross-season percentage. Verified navigation identity comes exclusively from `JellyfinAcquisitionReadiness`; the Seerr-carried `DiscoverItem.jellyfinItemId` remains metadata/hint rather than navigation authority.

Ordering is stable: newest parseable immutable request `createdAt` first, then highest request ID when timestamps are absent/equal, with media type and TMDB ID as deterministic final ties. Progress, lifecycle, `updatedAt`, queue order, and Jellyfin discovery never reorder the row. Because catalog identity is stable, a non-local item and its later Jellyfin-local form retain the same Home projection key while the verified destination ID appears reactively.

Checkpoint 1 intentionally does not modify `HomeViewModel`, `HomePage`, Home focus restoration, configured `HomeRowConfig`, cards, strings, navigation contracts, or any library query. Tracker deactivation empties the acquisition index and therefore this source naturally, without a raw feature-toggle check. The transient leading row, stable-key focus behavior, and Android TV presentation remain deferred to the explicit Checkpoint 2 UI task.
# Home acquisition Checkpoint 1 validation

The shared Home acquisition projection/source checkpoint passed external Standard validation: targeted JVM tests, production Kotlin compile, acquisition model and tracker regressions, Seerr pagination regressions, Downloads page regressions, and Git whitespace checks. Total elapsed time was `00:06:27.2001194`; the validation log was `C:\Projects\Wholphin\Wholphin\validation.log`.

## Home Acquiring UI integration

Home observes `HomeAcquiringSource` once in `HomeViewModel` and carries its items beside, rather than inside, the configured `homeRows`. `HomePageContent` renders a separately keyed optional leading `Acquiring` item, while configured rows keep their original `RowColumn` indices and stable `configured:<index>` keys. Acquiring cards use typed `MediaKey.Catalog` identity and dedicated focus requesters; removal retains the same key when possible, selects the nearest surviving card once, or falls back once to the first populated configured row when the whole row disappears. A newly appearing row does not request focus. The selected catalog key is saved independently so return navigation can restore it without redefining configured Home focus semantics.

Cards reuse `DiscoverItemCard` and the shared `CardMediaPresentation`. Movies show exact unambiguous lifecycle/progress. Series and ambiguous movie variants show only a coarse `Acquiring` pill and never a synthesized percentage. On this Home row only, dynamic acquisition state replaces the passive media-type pill when they compete; the default `DiscoverItemCard` policy remains unchanged elsewhere. Verified Jellyfin identity navigates to the normal movie/series destination; otherwise the upstream Discover details fallback remains. Backdrop/header content comes directly from enriched `DiscoverItem` metadata, without manufacturing a `BaseItem` or issuing Home-specific requests.

This UI remains provisional until Android TV validation covers live insertion/removal, D-pad focus, return restoration, reactive local-destination changes, and enhanced OFF/ON behavior.

**Expected → Observed → Consequence:** typed `MediaKey.Catalog` was expected to be suitable as the stable key for the Home Acquiring `LazyRow`; Android Compose lazy state immediately rejected it because lazy item keys must be Bundle-saveable. The lazy key is therefore the deterministic string `acquiring:<MOVIE|SERIES>:<tmdbId>`, while focus, state, and navigation continue using the typed catalog key. Do not make the domain identity Parcelable solely for Compose. Ordinary `remember` inputs may retain typed keys; only lazy/saveable-state boundaries require the primitive representation.

### Home TV season-card correction

The preceding coarse Home UI checkpoint passed external Standard validation before this migration (targeted JVM tests, production Kotlin compile, acquisition model/tracker, Seerr pagination, Downloads page, and whitespace checks; `00:07:02.8718711`).

The earlier coarse Home series-card decision above is superseded for Home only. Android TV review established that Home Acquiring is more useful when it answers which exact season is active. `HomeAcquiringSource` now emits movies under `MediaKey.Catalog(MOVIE, tmdbId)` and TV under `MediaKey.Season(MediaKey.Catalog(SERIES, tmdbId), seasonNumber)`. Duplicate requests and quality variants reduce only within that exact logical season; conflicting presentations retain membership but fall back to coarse `Acquiring` rather than selecting a winner. `SeriesAcquisitionSummaryIndex` remains unchanged because coarse series posters in Watchlist, Library, Collections, Discover, and Search still need ACTIVE/NONE semantics.

TV lifecycle presentation is derived through the same shared `IndexedAcquisition.tvSeasonCardPresentation()` used by Series Details: Queueing and Queued use pills, active canonical progress uses the bottom rail, and Finishing uses its pill. Home uses the enriched series poster/title/backdrop plus a localized `Season N` or `Specials` caption. It does not fetch season artwork or metadata, manufacture a Jellyfin `BaseItem`, scan the library, or add per-card collectors.

The typed season key remains stable through placeholder, Jellyfin discovery, import, and readiness; verified Jellyfin IDs enrich navigation without replacing identity. No verified series ID opens Discover, a verified series ID opens local Series Details, and verified series plus season IDs use the shared exact `SeasonEpisodeIds` destination helper. Full-season readiness is not required merely to navigate to an already verified partial season. Focus persistence adds the season number, and the Bundle-safe lazy key is `acquiring:SERIES:<tmdbId>:season:<seasonNumber>`. The migration remains provisional pending Android TV validation.

### Debug-only Home acquisition fixture harness

Android TV acquisition UI iteration has a debug-only, in-memory fixture harness at the `HomeAcquiringStateProvider` boundary. Release binds that neutral interface directly to the real `HomeAcquiringSource`; debug binds it to a selector that exposes either the untouched real source or one fixed `HomeAcquiringState`. Fixture definitions, controller, Hilt binding, and ADB receiver live in `src/debug`, while the release binding lives in `src/release`. The initial mode is always `real`, selection is not persisted, and fake and real items are never merged.

This boundary is intentional. Fixtures exercise the real Home row composition, cards, Bundle-safe lazy keys, D-pad focus behavior, insertion/removal, and navigation fallback without constructing queue records or injecting into `SeerrAcquisitionTracker`, `AcquisitionStateIndex`, or `MediaProductStateCoordinator`. They cannot write Room, DataStore, integrity expectations, request APIs, or backend state, and they do not affect Downloads or Series Details. Default fixture identities are catalog-only and contain no invented Jellyfin UUIDs.

Switch live while Home remains composed with:

``` powershell
adb shell am broadcast -n com.github.damontecres.wholphin.debug/com.github.damontecres.wholphin.ui.main.HomeAcquiringFixtureReceiver -a com.github.damontecres.wholphin.debug.ACQUISITION_FIXTURE --es scenario tv_multi_season
```

Tokens are `real`, `empty`, `movie_states`, `tv_multi_season`, `mixed`, `focus_before`, `focus_card_removed`, and `focus_row_removed`. Select `focus_before`, focus the known removable card, then select `focus_card_removed` or `focus_row_removed` to test deterministic fallback. These fixtures validate UI/runtime behavior only; real Seerr -> Servarr -> download client -> Jellyfin -> Wholphin integration still requires real end-to-end validation.

### Home Acquiring spacing and leading-row removal stabilization

The transient row originally duplicated normal `ItemRow` geometry internally—8dp between its title and LazyRow plus 8dp vertical LazyRow content padding—but also carried an additional outer 8dp bottom pad. Removing only that outer pad makes the following configured header appear sooner without changing card dimensions, card internals, horizontal spacing, focus styling, or global Home geometry.

The reported final-row visual shift has a concrete structural contributor: both the Acquiring item and configured Home items used `animateItem(placementSpec = null)`, explicitly disabling placement animation. When the leading Acquiring item disappeared, every configured item changed LazyColumn position in one frame at the same time the focused row issued its configured fallback request. Configured item keys were already stable, and the focus projection already chose a nearby surviving acquisition card or one configured fallback only; those rules were not replaced. Placement animation is now restored for these LazyColumn items, and focus resolution explicitly returns `Unchanged` when Acquiring did not own focus, preventing a non-focused removal from requesting focus.

Manual confirmation remains required with `focus_before` → `focus_card_removed` → `focus_row_removed` while Home stays visible. The code-path cause is established, but the post-fix visual result must remain recorded as unconfirmed until that Android TV sequence is run.

#### Correction: exact native Home-row spacing

The preceding conclusion that Acquiring's outer 8dp bottom padding was extra was disproved by comparing the complete native and transient rendering paths. **Expected → Observed → Consequence:** removing the apparent extra pad was expected to tighten Acquiring toward native rhythm; configured `ItemRow` also has 8dp LazyRow bottom content padding and its Home wrapper retains another 8dp bottom padding, while Acquiring after that change retained only the internal 8dp; Acquiring therefore differed structurally from native rows by exactly 8dp.

Both paths now use one shared `homeRowBottomPadding` value of 8dp at the LazyColumn-item wrapper. Together with each row's existing 8dp LazyRow bottom content padding, both produce the same 16dp effective distance from the bottom of the card/caption layout to the next row header. No title spacing, card/caption dimensions, focus scaling, placement animation, or focus policy changed. Android TV confirmation should use `tv_multi_season` or `mixed` and compare the next configured header directly below Acquiring.

#### Correction: caption height was the remaining mismatch

The equal wrapper padding above removed one structural discrepancy but did not explain the remaining visual height difference. **Expected → Observed → Consequence:** matching the native wrapper and LazyRow padding was expected to match native Home rhythm; Home Acquiring still rendered `DiscoverItemCard`/`SeasonCard` captions beneath 172dp artwork while ordinary poster-only Home rows did not; the captions, rather than another padding value, were the remaining row-height difference.

Home Acquiring now uses a narrow poster-only wrapper around `ItemCardImage` for both movies and TV seasons. It preserves the 172dp 2:3 artwork footprint, focusable TV `Card`, canonical acquisition presentation, full-width bottom progress rail, top-left lifecycle indicator, and all existing typed identity/focus/navigation behavior. TV seasons add only a compact upper-right `S<number>` overlay (`S0` for Specials), using the existing translucent black rounded corner-label vocabulary. Movie and season titles are intentionally absent below the card because the focused Home header supplies catalog identity. The shared 8dp wrapper padding remains: it is native row structure, not caption compensation. Android TV validation remains required with `tv_multi_season`, `movie_states`, and `mixed`.

#### Final alignment cause: nested bring-into-view policy

Poster-only Android TV validation showed identical card footprints but left the focused Acquiring row approximately one 8dp unit higher than a focused configured row, exposing a sliver of the following row's cards. Static row geometry was already equal. **Expected → Observed → Consequence:** the leading Acquiring item was expected to inherit native Home focus positioning; configured rows restore the captured default `LocalBringIntoViewSpec` around each inner `ItemRow`, while the separately inserted Acquiring `LazyRow` inherited `ScrollToTopBringIntoViewSpec` directly; Acquiring focus therefore traversed a different nested scroll policy despite matching dimensions and padding.

The Acquiring item now uses the same `CompositionLocalProvider(LocalBringIntoViewSpec provides defaultBringIntoViewSpec)` boundary as configured rows. Home's outer `LazyColumn` retains its existing scroll-to-top behavior, while the nested horizontal row uses the native/default bring-into-view policy. No dimensions, padding, focus identity, focus fallback, or card presentation changed. This should put the next configured header/card boundary at the same viewport position as native row transitions; confirm with the `tv_multi_season` fixture before treating the visual issue as runtime-closed.

#### Native `ItemRow` mechanics reused

The default bring-into-view boundary alone did not eliminate the small Android TV positioning difference. Static geometry was already equivalent; the remaining parallel implementation still lacked `ItemRow`'s row-entry requester, inner focus group/requester/restorer, remembered horizontal state, and remembered preferred-card path. Copying selected modifiers would preserve two subtly different focus implementations.

`ItemRow` is already generic, so Home Acquiring now uses it directly with its custom `HomeAcquiringItem` data and poster-only card content. The only shared API addition is the optional `itemKey: ((index: Int, item: T?) -> Any)? = null`, forwarded directly to Compose `itemsIndexed`. Existing callers omit it and retain the previous unkeyed behavior. Acquiring supplies its existing Bundle-saveable `acquiring:<type>:<tmdbId>[:season:<number>]` string; typed `MediaKey` remains the product/focus/navigation identity.

Direct reuse did not require an externally controlled-focus API. `ItemRow` continues to own native row entry and restoration. Existing acquisition-specific per-card requesters remain handles on the same focus targets for logical-key restoration and removal reconciliation; they do not replace `ItemRow` internals. Poster dimensions, overlays, ordering, outer leading-row key, configured `RowColumn` indices, feature gating, and acquisition semantics are unchanged. Android TV validation is still required for normal positioning plus `focus_before` → `focus_card_removed` → `focus_row_removed`; if requester interaction appears at runtime, do not broaden `ItemRow` into a general focus-controller framework.

#### Home Acquiring end action

Home Acquiring is intentionally a glanceable active-acquisition preview; Downloads remains the complete operational acquisition surface. A single trailing arrow now connects those levels by navigating to the existing `Destination.Downloads`.

The implementation reuses `ItemRow`'s existing `showViewMore`/`viewMoreCardContent` slot and Wholphin's existing poster-footprint `ViewMoreCard` with its caption disabled. `ItemRow` gained only an optional `viewMoreKey: Any? = null`, forwarded to the existing trailing lazy item; omitted values preserve every prior caller's behavior. Home supplies the Bundle-saveable constant `acquiring:more`, which cannot collide with `acquiring:MOVIE:...` or `acquiring:SERIES:...:season:...`. The action is a Home UI concern and is not represented by `MediaKey`, `HomeAcquiringSource`, acquisition ordering, or deduplication.

The action is rendered last after all acquisition media and only inside the already-conditional non-empty Acquiring row. It uses `ItemRow`'s native focus mechanics and adds no second focus controller. Selecting it uses the same navigation manager and Downloads destination as the rest of the app; no special filter or duplicate route exists. Android TV validation remains required for end-of-row traversal, return from Downloads, insertion/removal before the stable end key, and whole-row disappearance while the action is focused.

#### Home Acquiring checkpoint complete — Android TV validation passed

Final Android TV runtime validation passed for the complete Home Acquiring surface. Mixed movie and exact TV-season items render with the poster-only Home footprint; TV retains `S#` identity; and Queueing, Queued, determinate progress, and Finishing presentation behave correctly. Native `ItemRow` focus/scroll mechanics, stable focus restoration, dynamic card/row insertion and removal, nearby-card selection, and whole-row fallback all behaved correctly across the debug mixed, movie, TV, and focus-removal scenarios.

The same runtime pass confirmed continuity across non-local catalog identity to verified Jellyfin-local identity/navigation, without destabilizing the logical Home card. The trailing `ViewMoreCard` remains last, receives normal D-pad focus, opens the existing Downloads destination, and returns sanely to Home. Disabling enhanced acquisition naturally empties the source and removes the entire row—including the end action—without changing base Home. The Home Acquiring roadmap checkpoint is therefore complete; the debug fixture harness remains a development aid rather than evidence for backend integration behavior.

### Canonical card acquisition presentation consolidation

Card-level movie acquisition presentation now has one pure shared policy in `CardMediaPresentation.kt`. An individual `IndexedAcquisition` first has to satisfy the existing canonical `hasCurrentMovieAcquisitionWork` rule. Queueing maps to Queueing, current non-measurable work maps to Queued, successful transfer awaiting Jellyfin maps to Finishing, and only a currently `DOWNLOADING` aggregate with observed live progress maps to a determinate rail. Availability, stale Processing, problem-only state, expired retained entries, readiness/history retention, and completed work without a live replacement yield no active card presentation.

**Expected → Observed → Consequence:** accepting every non-zero aggregate fraction was expected to provide useful Requests progress, but a queue-classified item could retain a tiny fraction that rendered as a visible card rail while Downloads rounded it to `Queued · 0%`. A fraction is therefore no longer sufficient evidence by itself: the shared movie projector requires canonical current work plus downloading/activity semantics. Downloads retains its richer independent section/label projection for now; its lifecycle membership and percentage presentation are deliberately deferred to the next checkpoint.

The same projector supports two selection scopes without duplicating lifecycle rules. Discover Requests filters by exact request ID and normal/4K identity, then reduces through the shared policy. Home and future catalog consumers reduce all current movie projections for a typed catalog key: identical results remain exact, while conflicting lifecycle or progress variants become coarse `Acquiring`; fractions are never averaged and a request is never chosen by recency or ID. Historical entries are ignored when current work exists, and an all-historical set produces no presentation.

TV season card presentation now explicitly requires `TvSeasonTarget.hasCurrentAcquisitionWork` before mapping Queued, In progress, or Finishing. Tracker/index history remains available for Downloads and reconciliation, but retained terminal targets cannot produce stale ordinary-card pills or rails. Clearing the acquisition source continues to clear presentation through the existing `MediaProductStateCoordinator`/consumer replacement path. A last published upstream snapshot can still remain visible until a successful tracker update proves changed queue/readiness state; that polling-lag possibility is separate from the corrected presentation-policy defect.

This consolidation checkpoint passed external Standard validation on 2026-09-06 in `00:04:53.6766272`: focused card/Home projection tests, production Kotlin compile, acquisition model and tracker regressions, Seerr pagination regressions, Downloads page regressions, and Git whitespace checks all passed. The complete log is `C:\Projects\Wholphin\Wholphin\validation.log`. Android TV fixture sanity remains the final presentation confirmation; no Downloads lifecycle work was included in this checkpoint.

### Downloads availability/acquisition orthogonality

Downloads now treats current acquisition and current Jellyfin readiness as independent facts. Projection order is current work first, then recent ready history: when the same logical request has an active upgrade, replacement, re-acquisition, or quality-variant transfer, it appears once in Active or Processing even if an older copy is already playable. It becomes Recently Completed only after current work has ended and the existing seven-day completion rule admits it. This avoids duplicating one logical request as simultaneous operational and historical rows.

**Expected -> Observed -> Consequence:** Jellyfin readiness was expected to describe whether the media can currently be played, but Downloads used it as an acquisition terminal condition. A ready movie or season could therefore hide live replacement work, while retained queue fractions let Downloads say `In progress` when the shared Home/card policy said `Queued`. Downloads now consumes the same pure current-work card projection for operational movie and exact-season lifecycle classification. Queueing, Queued, and Finishing never expose determinate progress; only canonical In progress does. Downloads may still add richer timing and navigation, and independently published polling snapshots may briefly differ, but identical authoritative snapshots no longer have contradictory lifecycle semantics.

For a Jellyfin-ready TV season with replacement work, the current acquisition fraction is projected without counting the already-playable episodes from the old copy as completion of the new transfer. This remains the canonical `TvSeasonTarget` acquisition calculation rather than a UI-specific percentage. Existing readiness continues to authorize local navigation but does not terminate or overwrite the operational acquisition state.

Seerr `AVAILABLE` remains neither Jellyfin readiness nor proof that acquisition has ended. When transfer evidence is complete but authoritative Jellyfin readiness has not been established, Downloads conservatively retains the movie or season as Finishing. It does not invent readiness or a completion timestamp.

This Downloads lifecycle checkpoint passed external Standard validation on 2026-09-06 in `00:04:53.6766272`: targeted JVM tests, production Kotlin compile, acquisition model and tracker regressions, Seerr pagination regressions, Downloads page regressions, and Git whitespace checks all passed. The complete log is `C:\Projects\Wholphin\Wholphin\validation.log`.


## External Discovery: source ownership and contribution boundaries

> Superseded for autobrr Fresh by the Fresh section below. The durable inbox recommendation remains historical webhook research, not the current Fresh design.

Architecture established by the completed reviews; no Discovery implementation has been started or completed. This section records the review snapshot of 2026-09-06 against official Seerr develop `a3dbbd94`. Recheck upstream status before contributing; the architectural distinctions below do not depend on the PRs retaining their current status.

### Upstream landscape and negative knowledge

- [Issue #1837](https://github.com/seerr-team/seerr/issues/1837) is the umbrella external/dynamic Discovery-source request. Its TMDB-list slice is useful independently, but implementing that slice does not fulfill all external-source ambitions.
- [PR #1896](https://github.com/seerr-team/seerr/pull/1896), reviewed at `453fc01b`, is historical TMDB-list work and must not be ported wholesale. Its final v3 helper reads `results` instead of `items`, ignores requested pages, and fabricates single-page totals. The route uses unsafe mapper casts, accepts weakly validated IDs, and turns upstream failures into empty HTTP 200 responses. It lacks the requested Cypress coverage and carries unrelated TVDB changes that still exclude season zero, despite zero being valid specials. The branch previously contained 121 commits; reducing that history to 18 commits did not remove all unrelated changes. Resolved review threads did not reliably mean the final code was correct. The PR was closed for inactivity, not because maintainers rejected the TMDB-list concept.
- Do not preserve the historical assumption that TMDB v3 lists are unpaginated. Read-only public requests during review returned distinct pages from `/3/list/{id}`, with `items`, `page`, `total_pages`, and `total_results`. Conversely, the narrow v4 interface in #1896 did not prove v4 returns IDs only: current official v4 examples contain full movie metadata. Unsafe typing needs correction, but mandatory per-item hydration should follow actual payload requirements rather than that bot-review assumption.
- [PR #3344](https://github.com/seerr-team/seerr/pull/3344), reviewed at `a75550c6`, has useful normalized resolved-media/list concepts: typed movie/TV TMDB identity, optional existing metadata, ordered paginated results, and per-user enrichment after shared caching. It is not an ingestion foundation: its input already requires canonical identity, and its read-through cache cannot retain unresolved events or source membership. Its closure message cited excessive scope and insufficient demonstrated human review/oversight. Preserve these lessons rather than submitting another oversized replacement; do not treat its closure as a rejection of all list support.
- [PR #3066](https://github.com/seerr-team/seerr/pull/3066), reviewed at `459fb3bb`, is active external HTTP/JSON provider work. Its persisted entity stores URL/authentication/mapping/cache configuration. During a Discover read it retrieves reconstructible external content, extracts TMDB/TVDB IDs, hydrates, caches metadata, and attaches local media state. Entries without those IDs are dropped; IMDb and title/year resolution are absent. Later commits fixed per-user cache leakage and bounded hydration within one invocation, but did not add durable retries, cross-delivery deduplication, or membership retention. Deduplication before hydration does not merge different external IDs that later resolve to the same canonical title. Failed retrieval/hydration can still look like empty or reduced content.

### Expected → Observed → Consequence

**Expected:** a generic external-provider implementation such as #3066 might provide the natural base for autobrr/webhook Discovery.

**Observed:** #3066 owns provider configuration and pull-time HTTP retrieval/hydration/caching. It does not own durable observations, unresolved events, retry state, source membership, or push retention. #3344/#1896 likewise do not provide a durable inbound-event lifecycle. A cached list can be fetched again from its owner; an accepted ephemeral webhook cannot be assumed recoverable from its producer.

**Consequence:** develop push/webhook-backed Discovery as a separate isolated feature on current Seerr develop. Share only the downstream canonical identity/normalization, local enrichment, and Discover-rendering boundaries with pull/list providers. #3066 must not become a prerequisite. Do not create fake polling/provider URLs merely to force local observations through its HTTP retrieval model.

### Validated producer model and semantic boundaries

The real producer has been validated externally: autobrr consumes FileList IRC announcements and NZBGeek Newznab feed entries, applies filters externally, and can POST a normalized observation such as:

```json
{
  "title": "Marshmallow",
  "year": 2025,
  "type": "movie",
  "season": 0,
  "episode": 0,
  "imdbId": "",
  "tmdbId": ""
}
```

IDs are optional; the empty strings above represent absent identifiers. autobrr is one possible producer, not a Seerr domain concept. External filtering and transport validation do not mean Seerr ingestion or identity resolution has been implemented.

Observed Discovery content is not Watchlist membership, request intent, or acquisition state. Do not use Watchlist as the observation store, mutate it on delivery, create requests automatically, or create local Media records merely to represent an observation. Existing local availability may enrich a resolved card without changing those independent dimensions.

### Required push lifecycle

The minimal logical shape is: authenticated generic ingress → durable observation/inbox → bounded asynchronous identity resolution → canonical source membership → ordinary Discover results. These are responsibility boundaries, not a commitment to a table count or generalized provider/plugin framework.

- Validate a bounded payload and source authorization; persist before a fast acknowledgement such as HTTP 202. Do not block webhook delivery on TMDB resolution. Acknowledgement means durable acceptance, not successful matching or requesting.
- Inbox/processing state must survive restart. Make repeated delivery safe and bound asynchronous work across bursts. This sample has no producer event ID, so do not assume exact delivery identity or exactly-once transport.
- Distinguish resolved, ambiguous/unmatched, retryable provider failure, and invalid input. Prefer validated typed TMDB identity, then external-ID mapping such as IMDb → TMDB, then cautious title/year/type resolution. Never silently choose the first search result when ambiguous or infer movie identity solely because a numeric ID resolves as a movie.
- Canonical membership is scoped by `(sourceId, mediaType, tmdbId)`. Repeated releases of the same movie/series converge to one Discovery item, including observations initially carrying different external identifiers. Deduplicate after canonical resolution, not only before hydration.
- Season/episode values remain observation context; TV Discovery normally deduplicates at series level. Movie `season: 0`/`episode: 0` does not imply season identity. A series release year is not necessarily its premiere year.
- Retention of observations and source membership is independent of metadata-cache expiry. Metadata can be fetched again; cache eviction must not erase accepted observations or remove retained membership. Retryable lookup failures must not be recorded as confirmed no-match results.

### Current Seerr reuse points and caveats

- `server/api/themoviedb/index.ts`: reuse TheMovieDb metadata methods and `getByExternalId()` for IMDb/TVDB mapping. `getShowByTvdbId()` can resolve a TVDB reference without introducing the broader TVDB-enrichment path merely for identity.
- `searchMovies()` / `searchTvShows()` provide useful title/year primitives, but currently swallow upstream errors and return empty results. A durable resolver needs an error-preserving adaptation before it can distinguish no match from provider failure. `server/lib/search.ts` demonstrates interactive external-ID handling; it is not a durable resolution policy.
- `server/models/Search.ts`: reuse `mapMovieDetailsToResult()`, `mapTvDetailsToResult()`, and `mapSearchResults()` after validating media identity/shape. These shared mappers already existed during #1896; they are not a reason to copy its duplicated dispatch or unsafe casts.
- `server/entity/Media.ts::getRelatedMedia()`: enrich per user using typed IDs after shared metadata caching, preventing one user's Watchlist relationship from leaking through globally cached results.
- `server/entity/DiscoverSlider.ts` and existing settings routes: retain a source/slider reference in `data`, not an accumulated event payload. Current entities provide no suitable dynamic-source membership/inbox store; TypeORM/database infrastructure is reusable, but that domain persistence is new.
- `src/components/MediaSlider/index.tsx` and Discover's type switch provide ordinary final presentation. The existing editor's preview-count gate conflates a valid empty/filter-hidden source with invalid configuration; source validity must not depend on visible-card count. MediaSlider also needs explicit empty/error handling. Full-page `useDiscover` currently deduplicates by numeric ID alone, so mixed movie/TV reuse needs typed identity handling.
- Current bounded TMDB CacheStore/LRU infrastructure is reusable for metadata, not event durability. #3066's standalone NodeCache and #3344's custom cache assumptions should not be transplanted into current develop. Existing scheduled jobs are not a durable inbox/worker.

Pull/list sources and push/webhook sources should converge after canonical identity/normalization, without unnecessarily sharing ingestion lifecycle.

### Contribution strategy and workspace isolation

We have [already contacted the #3066 author offering help](https://github.com/seerr-team/seerr/pull/3066#issuecomment-5557940195). No author/maintainer reply was present at the review snapshot. Preserve that discussion and PR/issue history; do not race upstream work or casually open a competing/duplicate replacement while the conversation is active. If welcomed, help #3066 within its own pull-provider scope. The offer is not a commitment to base webhook ingestion on it.

Keep contributions small, focused, reviewable, and demonstrably human-reviewed. Separate webhook work can remain locally useful even if upstream declines it. If #3066 later merges or evolves, share/refactor downstream normalization only where it removes real duplication; do not retrofit webhook persistence into its pull cache model. Architecture and contribution strategy are established, but no new product implementation is committed to or completed; the roadmap has intentionally not been updated.

Parallel workspaces:

- `C:\Projects\Wholphin\seerr` → `pr-1055-current`: existing Servarr work. Do not disturb its worktree or branch.
- `C:\Projects\Wholphin\seerr-discovery` → `feature/discovery-sources`: Discovery research/future isolated work, based on official `upstream/develop` at `a3dbbd94` for these reviews. Local `pr-1896` is a review reference, not a branch to merge or cherry-pick wholesale.

## Fresh: rebuildable recent-media intersection

Fresh Checkpoints 1 and 2 are implemented locally in `C:\Projects\Wholphin\seerr-discovery` on `feature/fresh`. It supersedes earlier webhook/durable-observation recommendations for autobrr. No dependency on #1896, #3344, or #3066 was introduced; the independent `seerr` / `pr-1055-current` worktree remains untouched.

**Expected -> Observed -> Consequence:** earlier research treated releases as events requiring durable acceptance. The refined product is recent Seerr Discover candidates intersected with a selected autobrr filter's retained history. Both inputs are reconstructible, and Fresh should age out with them. No observation/membership database, migrations, durable checkpoint, whole-TMDB title resolver, Watchlist/request effects, or permanent tracker-availability assertion is appropriate.

### Backend semantics and ownership

- `createFreshMediaState(config)` remains the projection seam. `FreshService` is the application-scoped coordinator: it owns one state instance, recreates it when configuration changes, and supplies both ordered results and typed `(mediaType, tmdbId)` membership. The row and badge remain deferred. Disabled sources create no clients, timers, or requests.
- Candidates use existing TMDB Discover methods with inclusive UTC dates from 90 days before today through today: movie primary release date and TV first air date. Factory clients inherit server Discover region/original-language and locale, without hardcoded sample scores, providers or languages. Candidate pages are all visited and dates rechecked locally. No HTTP request to Seerr itself, per-release TMDB search, or per-card autobrr request is needed.
- Matching indexes title/original_title and name/original_name with NFKC, lower case, apostrophe removal, punctuation/spacing folding, preserved diacritics and token order. Movies require the parsed movie year; TV release year is not assumed to be premiere year. Ambiguous or unmatched aliases are omitted. No fuzzy framework was introduced.
- The adapter uses X-API-Token, no redirects, a 2 MiB response bound, and no response cache. It projects only mediaType/title/year/observedAt. Raw names, URLs, quality fields, action diagnostics and HTTP errors are neither returned nor retained. Types 9 and 6/11 map to movie and TV. FILTER_APPROVED and selected filter evidence are required. ID selection checks action_status.filter_id; name selection is exact top-level filter equality and does not identify later filters visible only in action records. Prefer ID selection; delayed action evidence appears on a later rebuild.
- All retained release pages are scanned, then selected locally. q=filter is a prefix search and may miss releases stored under an earlier filter. Cursors are exclusive descending IDs; every nonempty page still returns a cursor. SQLite can reuse deleted IDs. Do not add a last-ID or timestamp early exit. Timestamps are not guaranteed to follow ID order.
- Identity is `(mediaType, tmdbId)`. Membership includes every matched candidate; maximumItems limits only ordered row output. Multiple encodes/episodes collapse. firstSeenAt is the earliest qualifying observation retained inside the rolling 90-day observation window. Sorting is descending firstSeenAt, then type and ID. Finding N unique items is not enough to stop traversal: older pages can change earliest time and row order.
- Ordering is intentionally not lifetime-stable: if cleanup/window expiry removes the earliest observation, a later retained one can become firstSeenAt. Preserving lifetime entry time would require the persistence explicitly rejected by the product definition. Deleted/aged-out evidence disappears on rebuild.
- Rebuilds publish atomically after complete scans. Concurrent refreshes share one promise. Before the first success, provider/shape/pagination failures expose unavailable with an empty projection. After a success, a transient failure retains the last complete in-memory projection and marks it stale; the next success replaces it atomically, including a valid empty result. Ready/empty is distinct from unavailable. Status errors are fixed sanitized text. Callers receive defensive copies; restart still rebuilds without a saved cursor.
- Guardrails: 100 rows per release page, 1,000 release pages, 500 candidate pages per media type, 15-second HTTP timeouts. Exceeding budgets fails closed. Large histories may need later source/API optimizations, not silent partial results. Cross-page reads are not snapshots; this is a periodically rebuilt best-effort intersection.
- Autobrr only stores matched history when active actions exist. A plain Test action can preserve collection without a webhook/download action. Filter order and earlier successful actions can prevent the selected filter running. Checkpoint 2 connection diagnostics should distinguish connected/empty from proven collection. Seerr does not change autobrr configuration.

### Application-managed backend (Checkpoint 2)

- Fresh settings persist with normal Seerr settings and default disabled: enabled, normalized autobrr base URL, API token, numeric filter ID, refresh interval (60-3600 seconds), and maximum row size (1-100). Existing settings merge with defaults. URL credentials/query/fragment and token control characters are rejected. The token uses replacement semantics and is never returned by settings or status APIs. Filter ID is used because Release action evidence exposes the stable numeric `filter_id`; name selection cannot reliably cover later action records.
- Startup configures the singleton after Seerr network/proxy initialization. Enabling/configuring performs one initial refresh. A completion-based one-shot timer schedules the next refresh, so slow scans do not overlap. Scheduled and manual requests share the same generation-scoped promise. Reconfiguration cancels the active timer and invalidates the old generation, preventing a completed old request from installing a duplicate timer. There is no durable Fresh state or separate shutdown contract.
- Admin endpoints are `GET/PUT /api/v1/settings/fresh`, `GET /api/v1/settings/fresh/status`, `POST /api/v1/settings/fresh/refresh`, and `POST /api/v1/settings/fresh/test`. Test reads one bounded Release page, verifies parsing/auth/reachability, and reports only `success`, `filterObserved`, and a sanitized message. Empty history is a successful connection with unproven filter observation. These routes inherit Seerr's ADMIN middleware.
- Authenticated consumers use `GET /api/v1/fresh`. It returns the normal Seerr page-shaped envelope with mapped movie/TV results, `freshFirstSeenAt`, projection status, and last successful refresh. Ordering and maximum item count come from the shared projection. It never exposes autobrr release names, URLs, action/download fields, credentials, or filter internals. Disabled/unavailable Fresh returns a clean empty response and cannot affect ordinary Discover routes.
- Status is memory-only and includes enabled/configured, availability (`disabled`, `idle`, `ready`, `stale`, or `unavailable`), refreshing, last successful/attempted refresh, item count, and fixed sanitized error text. Neither status nor public configuration includes the stored token.

### Seerr Fresh row (Checkpoint 3A)

- Fresh is a fixed built-in row immediately above the configurable Discover sliders. This makes the discovery shortcut prominent without adding a persisted `DiscoverSliderType`, changing existing slider order, or implying that the backend-disabled feature can be enabled from Discover customization. The fixed row is omitted while an administrator edits slider layout so it cannot be mistaken for a reorderable entry.
- `FreshProvider` at the Discover boundary makes one authenticated SWR request to `/api/v1/fresh`; `FreshSlider` consumes that shared context and does not request the separate status endpoint. The row renders nothing while loading, when the request fails, for `disabled`/`unavailable`, or when results are empty. A `stale` response with retained results remains visible. Errors stay isolated from the surrounding Discover sliders.
- The backend result array is mapped in place with no frontend sorting, pagination, or Fresh-specific filtering, preserving backend order and maximum count. Movie and TV entries both use the existing `TitleCard`, passing the backend TMDB ID and media type; established `/movie/:id` and `/tv/:id` navigation, availability, request, watchlist, and progress behavior therefore remain shared. The provider owns the only Fresh fetch and adds no per-card Fresh/autobrr calls.
- At completion of Checkpoint 3A, the reusable Fresh card indicator remained deferred; the following section records its Checkpoint 3B implementation.
- Checkpoint 3A passed external Standard validation on 2026-09-06 in `00:01:06.5918629`: focused Fresh tests, Fresh formatting, Fresh lint, server typecheck, client typecheck, and Git whitespace checks. The complete log is `C:\Projects\Wholphin\seerr-discovery\validation.log`.

### Shared Fresh card indicator (Checkpoint 3B)

- `FreshProvider` owns the single Discover-page SWR cache entry and derives a memoized `Set` keyed as `movie:<tmdbId>` or `tv:<tmdbId>`. Both the Fresh row and card lookups consume this context. Typed keys prevent movie/TV numeric-ID collisions; disabled, unavailable, failed, and empty responses produce an empty membership set, while stale retained results remain members. Cards perform only an in-memory lookup.
- `TitleCard` has an explicit `showFresh` opt-in. The main Discover component wraps its ordinary mixed-media `MediaSlider` instances to enable it. The opt-in does not extend to the Fresh row itself (where the label would be redundant), Plex Watchlist, Recently Added/Jellyfin content, Recent Requests, Create Slider previews, detail recommendations, library pages, Downloads, or other `TitleCard` consumers.
- The Fresh pill stacks beneath the existing movie/series type pill inside the poster's transformed overlay. Availability/progress remains at the opposite edge and hover watchlist/blocklist actions retain their existing layer and behavior. Fresh has no navigation or request precedence and uses the existing localized `Fresh` label.
- The frontend seam is reusable for later Seerr surfaces, but Wholphin should continue consuming the product API `/api/v1/fresh` rather than depending on Seerr React context or card details.
- Checkpoint 3B passed external Standard validation on 2026-09-06 in `00:01:06.8009510`: 34 focused Fresh tests, Fresh formatting, Fresh lint, server typecheck, client typecheck, and Git whitespace checks. The complete log is `C:\Projects\Wholphin\seerr-discovery\validation.log`.
- Focused `src` tests run under `server/tsconfig.json`, whose path override retains `@server` but not the client `@app` alias, while ESLint rejects cross-directory relative imports. The shared `/api/v1/fresh` response types therefore live in `server/interfaces/api/freshInterfaces.ts`; backend and frontend can both reference that contract through `@server`. Keep pure same-directory helper imports relative. The initial 3B validation runs exposed both constraints before lint/type validation completed.

### Discovery Sources settings and candidate policy (Checkpoint 3C)

- Administrator configuration lives at Settings -> Discovery Sources. The Fresh form exposes enabled, autobrr base URL, write-only replacement token, numeric filter ID, refresh interval, maximum items, rolling candidate-window days, movie query, and series query. The Release adapter does not expose a verified safe filter-list endpoint, so the UI deliberately retains a numeric field labelled `Seerr Discovery` rather than scraping or inventing enumeration. Sanitized availability/item count/last success and Test Connection reuse the Checkpoint 2 admin APIs.
- The autobrr filter and Seerr candidate queries are independent axes: filter ID selects qualifying release events from autobrr history; the movie/TV Discover policies select the media universe; Fresh is their typed-title intersection. Changing either setting recreates the same singleton projection consumed by `/api/v1/fresh`, the row, and indicators. No consumer knows how candidates were filtered.
- Candidate inputs accept relative or fully qualified `/discover/movies?...`, `/api/v1/discover/movies?...`, `/discover/tv?...`, and `/api/v1/discover/tv?...` forms. Hostnames are parsed but discarded and never trusted or requested. Storage is a canonical relative page path plus sorted allowlisted static query parameters. Duplicate, empty, overlong, cross-media, unknown, and unsupported route/parameter input is rejected. `page` is accepted then discarded.
- The allowlist mirrors the current main Discover route vocabulary: genre, keywords/exclusions, original language, runtime/vote bounds, providers/region, certification fields, and valid media-specific sort values; movies additionally allow studio, while TV allows network and status. Movie primary-release dates and TV first-air dates are recognized but removed. Other routes and parameters are intentionally unsupported.
- `candidateWindowDays` defaults to 90 for migrated/legacy settings and is bounded to 1-3650. Every refresh computes UTC date-only start/today bounds and injects movie `primaryReleaseDateGte/Lte` or TV `firstAirDateGte/Lte`; the same start bounds retained release observations. Thus pasted absolute dates cannot freeze the projection. Blank optional queries reproduce the validated Checkpoint 1/2 90-day behavior. A `server` language token expands to the current server original-language setting; other encoded language values survive canonicalization.
- Fresh still invokes `TheMovieDb.getDiscoverMovies/getDiscoverTv` directly, using the same underlying implementation as Seerr's routes and normal full pagination. It never calls Seerr over HTTP. The only narrow Discover refactor is exporting those existing option interfaces so the normalized internal call remains type checked.
- Manual runtime diagnosis found that TMDB Discover movie payloads can omit `media_type`. The projection already retains authoritative typed identity separately, so API mapping must select `mapMovieResult`/`mapTvResult` from the projection's `mediaType`, never infer it again from the optional raw payload. The Fresh row and membership index preserve the API type, including `(movie, tmdbId) != (tv, same tmdbId)`.
- Apparent browser-page refreshes during local validation were Next.js development compilation/HMR. The dev server specifically warned that `127.0.0.1` made `/_next/webpack-hmr` cross-origin; use `http://localhost:5056` for this local runtime so HMR keeps its normal origin. Fresh's SWR request disables focus revalidation and has no polling interval; settings save performs cache mutation/rerender only; and the Fresh scheduler is server-only with no browser transport or document/navigation API. A scheduled projection refresh cannot initiate a browser document reload.

### Manual source-clear validation

**Expected -> Observed -> Consequence:** Fresh is intentionally transient and rebuildable from autobrr Release history; Seerr does not persist historical Fresh membership independently. Manual validation began with live matched media and a rendered Fresh row. After autobrr Releases history was cleared and Fresh completed its next refresh, the projection became empty and the row disappeared.

This confirms that qualifying autobrr evidence is the source of truth. Clearing Release history clears the current Fresh dataset after the next successful refresh, and autobrr retention bounds how far back Fresh can reconstruct state. This is intentional, not a data-loss defect. Any future requirement for membership to outlive Release history would be an explicit product and persistence change.

### Performance and scaling audit

- One refresh retrieves every configured movie candidate page, then every TV candidate page, then walks autobrr Release pages sequentially at 100 rows per request. The observed 592-movie/51-TV example is 30 + 3 TMDB method calls. Autobrr request count is `ceil(retained rows / 100) + 1` because an empty page terminates traversal: 20 -> 2, 100 -> 2, 500 -> 6, 1,000 -> 11, and 5,000 -> 51. A 1,000-page guard fails closed before unbounded traversal; successful histories are therefore below roughly 100,000 rows.
- TMDB Discover uses Seerr's shared `tmdb` LRU (1,000 keys, six-hour TTL). Identical same-day query/page keys cost 33 external calls cold and zero warm for the observed example. Rolling UTC date bounds change the keys daily, and configuration changes also create new keys. Candidate query constraints can materially reduce result pages. The broad-query guard is 500 pages per media type; that pathological ceiling can consume the entire TMDB cache and is an accepted safety backstop, not a recommended operating point.
- Complete pagination is currently required for correctness: TMDB ordering is independent of autobrr matches, and later candidate pages may contain a match. Autobrr must also scan past the visible row limit to find typed membership and the earliest retained observation for duplicate encodes/episode bursts. The Release API boundary cannot safely filter by top-level filter name because action `filter_id` may differ; no last-ID/time shortcut is valid without a stronger upstream API contract.
- Matching is indexed: candidate aliases build a `Map<type:title, Map<typed-id,candidate>>`, each release performs one normalized map lookup, matches deduplicate in a typed-ID map, and only unique matches are sorted. Computational cost is approximately O(candidate aliases + retained releases + unique matches log unique matches), with no candidate-by-release nested scan. Duplicate encodes and TV episodes repeat cheap lookups and converge to one projection item.
- At the observed candidate size, temporary candidates/alias maps are normally low-single-digit MB and the retained projection is smaller. Only one 100-row autobrr page/raw response is live at a time (also bounded to 2 MB). A pathological 20,000-candidate ceiling can reach tens of MB temporarily. Refresh atomically replaces arrays/maps/sets; stale state retains one last-good projection, and old generations are not accumulated.
- Disabled Fresh constructs no clients, timer, or source requests. Enabled work runs without browsers and is shared across all users. `/api/v1/fresh` only maps the bounded in-memory projection; it never refreshes. The completion-based timer waits the configured interval after each run, failures retain stale state, and failures retry at the normal interval rather than tightly. A manual refresh and scheduled refresh are single-flight. The audit fixed the reverse overlap case: if a timer joins an already-running manual refresh, its scheduling intent is now retained so the lifecycle cannot silently stop.
- A five-minute interval is reasonable for small histories. At 1,000 retained rows it means 11 uncached autobrr calls per run; at 5,000 it means 51, or about 14,688 local API calls/day, which is operationally moderate and can become unreasonable if responses are slow. Use a longer configured interval for several-thousand-row histories. A future autobrr API that filters reliably by action filter ID would be the meaningful optimization; client-side early termination or top-level-name filtering would weaken correctness.
- The Discover page owns one SWR key and one memoized typed membership `Set`; cards perform O(1) lookups with no per-card requests or polling. Context updates can rerender the Discover subtree once when initial data arrives, but backend scheduled refreshes are not pushed to browsers. Outside opted-in Discover sliders, `showFresh=false` reduces work to the existing context read and Boolean check.
- The initial row shift was real and timing-dependent: `FreshProvider` previously mounted only after Discover settings resolved, and no row space was reserved. It now starts concurrently at the page boundary and uses the existing slider placeholders while Fresh is unresolved. Ready content replaces reserved space; disabled, failed, unavailable, and empty responses collapse cleanly without delaying unrelated Discover requests.

### Validation and deferred work

Deterministic coverage is in `server/lib/fresh/candidateQuery.test.ts`, `server/lib/fresh/fresh.test.ts`, `server/lib/fresh/service.test.ts`, `server/routes/fresh.test.ts`, `src/components/Discover/FreshSlider/freshRow.test.ts`, and `src/context/FreshContext.test.ts`: projection matching, stale/recovery behavior, lifecycle scheduling and invalidation, disabled operation, bounds, secret replacement/non-disclosure, sanitized connection tests, mapped API ordering, typed identity, and source-field exclusion. No test accesses live autobrr or TMDB.

The feature worktree's uncommitted `scripts/validate-local.ps1` adapts Fast/Standard/Full semantics to Node tests and TypeScript, but its parameter interface is Seerr-specific and must not be treated as a Wholphin command or copied into the future Seerr baseline without review. It writes ignored validation.log and invokes node:test directly: the repository's existing reporter wrapper does not propagate failing tests to the process exit code. Standard adds focused Fresh server/UI formatting and lint plus server and client typechecking; Full additionally includes all tests and repository lint. Checkpoint 3C passed external Standard validation on 2026-09-06 in `00:01:13.6567361`: focused Fresh tests, Fresh formatting, Fresh lint, server typecheck, client typecheck, and Git whitespace checks. The complete log is `C:\Projects\Wholphin\seerr-discovery\validation.log`.

The post-3C local-runtime fixes (write-only token placeholder, projection-authoritative movie/TV API mapping, and focused presentation coverage) passed external Standard validation on 2026-09-06 in `00:01:20.5643966`: 45 focused Fresh tests, Fresh formatting, Fresh lint, server typecheck, client typecheck, and Git whitespace checks. The complete log is `C:\Projects\Wholphin\seerr-discovery\validation.log`.

The Fresh performance-audit fixes (manual/scheduled overlap scheduling and cold-load row reservation) passed external Standard validation on 2026-09-06 in `00:01:30.9238364`: focused Fresh tests, Fresh formatting, Fresh lint, server typecheck, client typecheck, and Git whitespace checks. The complete log is `C:\Projects\Wholphin\seerr-discovery\validation.log`.

The remaining planned Fresh work is Wholphin consumption of `/api/v1/fresh`. No durable history or generic provider framework is implied.

## Authoritative TV seasons when request metadata is incomplete

**Expected → Observed → Consequence:** the acquisition ledger intentionally accepts a TV request with no `requestedSeasonNumbers` when authoritative queue evidence already carries a safely assigned season number. Canonical `toTvSeasonTargets()` nevertheless iterated only the request payload, so `AcquisitionStateIndex` could expose an exact `MediaKey.Season` with a null target; Home and `SeriesAcquisitionSummaryIndex` then correctly omitted it, while Downloads bypassed exact-season projection and could create a movie-like fallback. Canonical TV target identity is now the deterministic numeric union of requested season numbers and the existing ledger-assigned `SeerrAcquisitionState.Tv.seasons` keys. No new title parsing, queue-position inference, expected-count inference, or other assignment algorithm was introduced; Season 0 remains valid.

Consumers continue to rely on the canonical target rather than recalculating lifecycle. An authoritatively assigned season therefore flows naturally through the index, exact Home season cards, series ACTIVE summary, and Downloads exact-season rows even when Seerr omitted the requested-season list. Genuinely unassigned TV evidence remains unresolved in the shared index: Home and series summary do not invent season identity. Downloads alone retains a bounded operational `${requestId}_tv` row and replaces it with `${requestId}_season_${seasonNumber}` once existing authoritative assignment becomes available; it never uses the movie suffix for TV.

The shared-presentation consolidation also intentionally means an absent retained queue entry can temporarily present as Queued with no zero-width progress rail before live progress resumes, and zero-remaining work presents as Finishing in Processing. Older Downloads fixtures that expected `0%` or Active during those states were corrected to the already manually validated lifecycle; acquisition semantics were not weakened.

External Full validation for the consolidated acquisition/Home foundation passed on 2026-09-07 in `00:01:21.5762407`. Production Kotlin compilation, the complete default-debug JVM unit suite, default-debug APK assembly, and Git whitespace checks all passed. The complete log is `C:\Projects\Wholphin\Wholphin\validation.log`; this supersedes the preceding focused and Standard validation handoffs for the pre-Watchlist checkpoint.

## First completed upstream synchronization lifecycle

The first full repository lifecycle completed in September 2026: validated feature work entered our `main` through a pull request, a dedicated `chore/sync-upstream-2026-09-07` branch was created from that integration baseline, six commits from `upstream/main` were merged, the sync branch passed Standard and Full validation, and a sync pull request returned the result to our `main` before local `main` was fast-forwarded.

Conflicts were limited to `RequestSeasons.kt`, `SeriesViewModel.kt`, and `strings.xml`. Resolution retained upstream localized season formatting, localized season/episode resources, and the `MediaReportService` to `ServerReportService` refactor while preserving enhanced request-season behavior, `MediaProductStateCoordinator`, acquisition/integrity projection, exact season identity, Home Acquiring, and existing enhanced resources. Auto-merged Series and Home integration files were reviewed because textual merge success was not treated as semantic proof. Standard validation passed, followed by Full validation in `00:04:28.8850388` across production Kotlin compilation, the complete default-debug JVM unit suite, APK assembly, and whitespace checks.

Permanent remote, branching, conflict-resolution, validation, and upstream-sync policy now lives in `docs/UPSTREAM_SYNC.md`. The safe mechanical entry point is `scripts/sync-upstream.ps1`; it intentionally stops on conflicts and never resolves, pushes, opens, or merges a pull request automatically.

## Fork-owned GitHub Actions validation

Historical CI-foundation state: pull requests, pushes/merges, and manual dispatches initially all ran the complete defaultDebug graph in the stable `CI / Full validation` job. I03 supersedes the PR execution policy while retaining that job name and the authoritative Full main/manual behavior. Full Git history remains required because application versioning uses Git tags and `git describe`.

The CI job has only `contents: read`, references no repository secrets, uses the existing single Gradle cache supplied by `actions/setup-java`, and uploads default-debug XML/HTML test diagnostics for seven days only when the job fails. Assembly is validation only; the debug APK is not uploaded. The shared Android setup retains upstream's proven package list for Build Tools 36.0.0 and NDK setup; it does not explicitly request the compile-SDK platform package.

**Expected -> Observed -> Consequence:** the upstream sync introduced a PR build plus a write-enabled development-release workflow, but those are upstream publishing infrastructure rather than the fork's validation contract. The old PR workflow was removed after its unique pre-commit behavior was incorporated into `ci.yml`, preventing duplicate PR builds. The development-release job remains easy to compare with upstream but is guarded to `damontecres/Wholphin`, so an ordinary push to `constbogdan/Wholphin:main` cannot delete or recreate releases or consume signing/extension credentials. Explicit `v*` tag release automation remains unchanged and separate.

Local Fast/Standard/Full validation remains authoritative for iteration and semantic handoff. In particular, an upstream synchronization still requires local Standard validation after conflict resolution and local Full validation before its PR; the PR then receives the same CI gate automatically. CI does not replace semantic merge review or Android TV visual, D-pad/focus, fixture, and real Jellyfin/Seerr/Servarr runtime validation.

Historical state at the initial CI implementation: branch protection was not enabled by workflow files and still required a manual repository ruleset. This was subsequently completed; the permanent current state is documented under **Permanent local and CI validation parity** below.

### Transitional formatting enforcement

**Expected -> Observed -> Consequence:** the first fork CI run was expected to validate the new workflow, but the inherited pre-commit action defaults to `--all-files` while local Full validation runs Gradle plus `git diff --check` and never established repository-wide KTLint/EOF compliance. CI therefore found pre-existing fork formatting debt across acquisition/Home Kotlin sources and three fork-maintained files with noncanonical EOFs; this was not a compile, test, or application-behavior failure.

Historical transitional state: until the dedicated `chore/format-baseline` cleanup was completed, automatic CI pre-commit enforcement was intentionally limited to the actual changed commit range. Pull requests compared GitHub's immutable pull-request base SHA with its head SHA, and pushes compared the event's `before` SHA with the pushed SHA. This temporary debt boundary is retired; it is retained here only to explain the earlier CI decision.

The planned formatting-baseline change must remain mechanical and separate from application work: normalize known EOF debt, apply the pinned KTLint configuration to the fork-owned Kotlin delta, inspect the resulting diff, and run Full validation. Once the repository has a clean baseline, CI must return to `pre-commit --all-files`, and local Standard/Full validation should incorporate the same formatting contract so local success cannot silently disagree with CI again.

### Android 37 CI setup correction

**Expected -> Observed -> Consequence:** because the app declares compile/target SDK 37, the first fork CI setup explicitly requested `platforms;android-37` from `sdkmanager`; the configured SDK channel did not publish that package and setup failed before Gradle ran. Upstream added Android 17/API 37 while leaving its successful Ubuntu setup on `tools`, `platform-tools`, Build Tools 36.0.0, and NDK 29.0.14206865. The fork therefore restores that exact package list and lets the runner/Android Gradle Plugin use the required platform through the same supported path as upstream. Do not downgrade compile SDK or guess an explicit platform package solely from `compileSdk` when maintaining this workflow.

### Canonical upstream version tags in fork CI

Full Git history from the checkout repository is necessary but not sufficient for Wholphin versioning: `constbogdan/Wholphin` currently mirrors the commit graph but no tags, while `app/build.gradle.kts` requires reachable `v*` tags for `git describe` and counts both `v*` and `p*` tags for its version metadata. A detached synthetic pull-request merge is valid; without tags, `git describe --tags --long --match=v*` fails with exit 128 before project configuration completes.

CI therefore imports only `refs/tags/v*` and `refs/tags/p*` directly from `damontecres/Wholphin` immediately after checkout, without force, credentials, or writes to either remote. This is a permanent part of the maintained-downstream build model: upstream owns the canonical Wholphin version-tag namespaces, while the fork supplies its own commits and pull-request merge ref. Do not replace this with a fabricated version fallback or assume `fetch-depth: 0` can retrieve refs absent from the fork remote.

## Repository formatting baseline

The dedicated `chore/format-baseline` branch establishes repository-wide compliance with the existing `.pre-commit-config.yaml` and `.editorconfig`; neither configuration was changed. An isolated clone preview was completed before the working tree was touched, then the same pinned hooks were applied to the real branch. The formatter baseline changed 55 existing files before this handoff entry: 53 Kotlin/Kotlin-script files and two EOF-only files (`app/schemas/com.github.damontecres.wholphin.data.AppDatabase/36.json` and `docs/fixture/fixture_commands.md`). The line-oriented formatter diff was 1,859 insertions and 1,144 deletions. Every resulting real-tree file matched the isolated preview byte-for-byte, and every formatted Kotlin file was already part of the fork delta from `upstream/main`; no otherwise-unchanged upstream Kotlin file was swept into the baseline.

KTLint 1.8.0 performed import ordering, indentation/wrapping, braces, trailing-comma, and equivalent string-template normalization. Its only non-auto-fixable finding was `IntegrityObservationStore._observations`: the private backing-property name did not match an internal rather than public property. The rule was not disabled or suppressed; the private field was mechanically renamed to `mutableObservations`, with no API or behavior change. Review found no import-set changes and no runtime string-value change; KTLint's removal of redundant braces around `separator` interpolation in `TvAcquisitionProjection.kt` preserves the same regex strings.

After convergence, a complete `pre-commit run --all-files` passed: XML, YAML, EOF, trailing whitespace, KTLint, and both debug guards were green. External Full validation then passed on 2026-09-08 in `00:07:27.8885381`: production Kotlin compilation, the complete default-debug JVM unit suite, default-debug APK assembly, and Git whitespace checks were all successful. The complete log is `C:\Projects\Wholphin\Wholphin\validation.log`. The formatting-baseline pull request has since merged into `main`.

### Permanent local and CI validation parity

The formatting-baseline changed-range policy described here was retired when all-files parity became operational. I03 later introduced a different, intentional PR-range policy: PRs validate their complete synthetic-merge change range according to deterministic risk/relevance, while protected-main and manual CI continue repository-wide pre-commit plus Full.

I03 supersedes the local tier details: Standard uses changed-scope pre-commit and classifier-selected tests, while Full retains all-files pre-commit and the complete graph. Fast is the smallest relevant path. Tool discovery remains non-mutating: validation uses `pre-commit` from `PATH` or `python -m pre_commit`, exposes resolved `JAVA_HOME\bin` only to the process, and never installs dependencies. Autofix drift still stops before staging/publication.

The current flow is local classifier-selected Fast/Standard or explicit Full, then required risk-tiered PR validation, then authoritative protected-main all-files pre-commit + Full. Manual upstream sync remains Standard with meaningful filters followed by Full. Semantic conflict review and Android TV/manual integration validation remain separate where applicable.

External Full validation of the permanent parity implementation passed on 2026-09-08 in `00:06:41.1655165`. Repository-wide pre-commit, production Kotlin compilation, the complete default-debug JVM unit suite, default-debug APK assembly, and Git whitespace checks all passed. The complete log is `C:\Projects\Wholphin\Wholphin\validation.log`.

### Downstream workflow portability boundary

Wholphin is now the reference workflow for other independently maintained downstream repositories: one protected integration branch (`main` for Wholphin), purpose-specific branches and pull requests, repository-specific Fast/Standard/Full validation, local/required-CI parity, deliberate upstream synchronization, guarded release automation, and repo-local agent/handoff documentation. Its CI, protected-main ruleset, formatting baseline, and local/CI validation parity are operational; `chore/validation-parity` merged through pull request #7 before the `chore/prepare-pr` milestone began. Shared tooling should standardize those safety guarantees without pretending that Android/Gradle and Node/pnpm repositories have the same validation implementation. Automated upstream-change detection and conflict-safe sync-PR preparation follows prepare-pr; automation may prepare an integration but must never resolve semantic conflicts automatically. The resulting model can then be adapted to Seerr, the other pending repository activities, and future modified services.

The first Seerr portability audit was intentionally read-only. A clean isolated worktree now exists at `C:\Projects\Wholphin\seerr-maintenance` on `chore/repository-standardization`, based exactly on the then-current `origin/develop` commit `d7dc7bdd`; neither the clean `seerr` worktree on `pr-1055-current` nor the dirty `seerr-discovery` worktree on `feature/fresh` was modified. The isolated worktree also remains unmodified.

**Expected -> Observed -> Consequence:** Seerr could not safely receive the Wholphin policy mechanically. Its upstream branch model is `develop`; its downstream `origin/develop` was five commits behind the locally known `upstream/develop`; and several inherited workflows can publish containers/charts/pages, create tags/releases, push commits, or mutate issues and pull requests without one consistent canonical-upstream repository guard. Seerr also had no repo-local agent/handoff/upstream policy or committed Fast/Standard/Full helper at that baseline. Seerr standardization is therefore a separate milestone with repository-specific Node/pnpm validation. Its first task must deliberately reconcile the five-commit `origin/develop` versus `upstream/develop` gap before establishing and protecting the fork's downstream integration baseline; do not copy the untracked feature-work validation script or modify either existing Seerr worktree as a shortcut.

## Historical prepare-pr v1 workflow (superseded by v2)

V1 merged through PR #8. Its repeated confirmations, Standard default and compare-URL fallback below are historical dogfooding behavior; [PREPARE_PR.md](PREPARE_PR.md) defines the current autonomous, authenticated-gh path.

The Wholphin v1 implementation is deliberately one guided command, `scripts/prepare-pr.ps1`, with internal/resumable Audit, Validate, Stage, Commit, and Publish phases. Repository-specific base/remotes, high-risk advisory paths, artifact refusals, validation entry point, and upstream-sync branch pattern live in `scripts/prepare-pr.config.psd1`; this is a portability seam, not a generic cross-repository framework. Detailed operator guidance lives in `docs/PREPARE_PR.md`, and the downstream pull-request template replaces the inherited contribution-oriented wording.

**Expected -> Observed -> Consequence:** a normal dirty task tree needs convenient automation, but validating while unrelated changes remain would prove a different snapshot from the intended commit. Guided mode therefore discovers every non-ignored changed path, allows numbered exclusions, and requires explicit scope confirmation; v1 then refuses any remaining out-of-scope staged, unstaged, or untracked path and recommends a separate worktree. Ignored paths are governed first by `.gitignore`; high-confidence local/sensitive artifacts are refused, while legitimate tracked generated material such as Room schemas is only flagged by the configurable review-sensitive patterns.

After scope confirmation, read-only `git hash-object` calls plus a deterministic manifest compute a Git-filter-aware hash of the intended files/deletions; no temporary index or object-writing flag is used. In v1, Standard validation was the normal default; an explicit Full option was available, while `chore/sync-upstream-*` automatically requires Standard then Full. The snapshot hash and complete dirty-path set are checked again after validation. Any pre-commit/autofix drift stops before staging and invalidates the result. Real staging is therefore the first intentional index mutation and uses only `git add -A -- <confirmed paths>`; the staged blob/deletion manifest must equal the validated snapshot before the staged tree is recorded and the complete diff is shown.

In v1, commit and publication were separate approvals. The commit requires a displayed, explicit title and unchanged staged tree. Publication refuses protected `main`, dirty post-commit state, remote divergence, and any push requiring force; it uses `git push -u origin <branch>` initially and an ordinary push thereafter. Authenticated GitHub CLI use checks for an existing PR and never duplicates or silently edits it. V1 permitted commit/push without authenticated `gh` and printed a compare/new-PR URL without claiming whether a PR already existed; v2 removed this fallback. Required `CI / Full validation`, CI waiting, and merge remain outside automatic v1 completion.

The workflow was acceptance-tested in disposable local repositories after the read-only snapshot design replaced the earlier prospective-index approach. New-file and deletion snapshots passed Audit -> Standard validation -> exact staging with identical intended/staged hashes; a validator-induced file mutation failed validation, reported drift, and left the index untouched. PowerShell parsing, configuration import, real-worktree read-only Audit, conflict-marker detection, and `git diff --check` also passed. No commit, push, PR, or real-worktree staging was performed. At that v1 checkpoint, the session did not expose `gh`, so existing-PR detection/creation had only static review and the compare-URL fallback was used. This limitation is superseded: authenticated `gh` is now required and v2 successfully created PR #9.

The pre-merge operating-model benchmark identified four P0 boundaries. Audit now treats existing branch-only commits/paths plus confirmed dirty candidates as the complete eventual PR scope, while staging still applies only to candidates. Candidate/staged identity includes Git mode, object type, object ID, and deletion state. After commit, `HEAD^{tree}` must equal the reviewed staged tree before publication state is saved. Git stderr is captured separately and retained in failure diagnostics instead of being discarded as PowerShell error records. Finally, the inherited stable `v*` release job now carries the same canonical `damontecres/Wholphin` repository guard as upstream development-release automation, so downstream tags cannot invoke that upstream-owned publisher.

Disposable P0 acceptance covered: two branch-only paths across existing commits appearing separately from two dirty candidates in the complete publication union; a staged `100644` -> `100755` executable-mode change retaining an identical intended/staged snapshot; a synthetic Windows-compatible `120000` symlink index entry retaining mode, blob type, and object identity; a pre-commit hook changing the committed tree and causing an explicit post-commit mismatch refusal while resumable state remained at Staged; actionable native Git stderr on an allowed-failure command; protected `main` refusal; and a divergent disposable remote branch refusing publication without changing the remote ref. Repository-wide pre-commit then passed using the same pinned configuration with Java added only to the validation process environment.

### Historical v1 dogfooding corrections

**Expected -> Observed -> Consequence:** guided preparation defaulted to Standard validation, but tooling/docs-only work had no honest focused JVM test pattern and `validate-local.ps1` correctly refused Standard without one. The v1 correction described filters as focused JVM test patterns, accepted explicit patterns unchanged, and—only for ordinary non-sync work—offered a recommended/default switch to Full when the prompt was left blank. Declining stopped before staging; v2 now makes this selection without a prompt. Upstream-sync branches retain their stronger Standard-with-meaningful-filters followed by Full contract.

The audit now prominently reports the total unique eventual PR path count and labels tracked diff statistics separately from included untracked/new files. Each invocation also replaces the ignored repository-root `prepare-pr.log`, recording nonsensitive operational evidence: timestamps, phase/results, branch/base/HEAD, confirmed publication paths, validation choice/result, snapshot/tree identities, staging/commit/publication outcomes, refusals/errors, useful Git stderr, and a PR URL when known. Resumable state and snapshot guarantees remain authoritative; the log is diagnostic evidence rather than an approval bypass.

## Maintained-downstream tooling benchmark

The September 2026 benchmark compared Wholphin's local validation, CI, upstream-sync, release guards, and prepare-pr workflow with upstream Wholphin and the isolated Seerr maintenance baseline, then checked the design against native GitHub capabilities and common hosted tools. The review was read-only for code, Git state, settings, workflows, scripts, installations, and external services; these documentation changes only preserve its conclusions.

### Evidence and engineering assessment

- **Appropriately engineered/current:** protected PR-only `main`; stable required `CI / Full validation`; repository-wide pre-commit parity; one shared Gradle validation graph without `clean`; minimal CI permissions; pinned Actions; explicit import of upstream version tags; canonical-upstream guards on inherited development and stable release workflows; semantic/manual upstream conflict resolution; repository-local operating knowledge; and prepare-pr's complete-scope audit, exact staging, actionable Git stderr, and Git tree verification.
- **Overengineered for the target flow:** prepare-pr v1's interactive multi-phase workflow engine, durable local resume state, repeated approval prompts, and parallel GitHub-CLI/compare-URL paths. Those were defensible while dogfooding a dirty shared worktree, but isolated task worktrees plus a protected PR boundary make much of the local orchestration redundant. Cheap fail-closed scope and tree checks remain worthwhile.
- **Underengineered:** there is no automated upstream-change detector, successful development APK retention, downstream-owned release path, explicit rollback runbook, or complete dependency/security-review policy. GitHub settings such as secret scanning and Dependabot enablement are not proven by repository files. Required checks cover correctness but CI performance has not been profiled systematically.

**Expected -> Observed -> Consequence:** standardizing every downstream repository by copying Wholphin would reduce apparent variation, but Seerr's `develop` integration model, pnpm/Node/Cypress validation, multi-architecture containers, Helm/Pages publishers, CodeQL/Trivy jobs, GitHub App usage, and extensive write-enabled workflows are materially different. Standardize the safety contract—protected integration, PR-only changes, local/CI parity, semantic sync resolution, minimal permissions, guarded publishers, and repo-local documentation—not branch names or build implementations. Seerr standardization remains deferred until its five-commit `origin/develop`/`upstream/develop` gap is deliberately reconciled.

### Patterns to adopt and reject

Useful Seerr patterns are separate lint/build/test concerns, mature Renovate grouping and action-digest pinning, CodeQL and Trivy coverage, path-scoped documentation checks, container signing/SBOM/attestation for real releases, and GitHub-native labels/issues as durable operational state. Its scheduled maintenance and multi-architecture release workflows demonstrate capabilities, not safe defaults: every inherited write, publish, tag, Pages, chart, issue, and PR mutation path needs a downstream ownership/permission guard first.

Useful upstream Wholphin patterns are Git-derived versioning, development/stable artifact construction, signature/checksum verification, and GitHub Releases. The downstream should not simply enable the inherited publishers: a successful protected-main build artifact is distinct from a signed release, and downstream versioning/signing/promotion/rollback ownership must be designed explicitly.

Build-versus-buy conclusions:

| Concern | Direction | Reason |
| --- | --- | --- |
| Repository validation | Keep custom, thin | Build graphs are repository-specific; CI invokes the same deterministic contract. |
| PR/status/review/merge/notifications | Use GitHub + `gh` | GitHub already owns durable state, permissions, required checks, and the approval boundary. |
| Upstream detection | Small GitHub workflow | Comparison and normal merge are deterministic; semantic conflict resolution is not. |
| Dependency updates | Renovate or Dependabot, one owner per ecosystem | Buying maintained update logic is safer than custom parsers; avoid duplicate bots and upstream-owned dependency noise. |
| Security scanning | GitHub native first | Secret scanning, dependency alerts/review, and CodeQL integrate with protected PRs; add release provenance tools only when releases exist. |
| AI review | Trial as non-blocking | It may find semantic issues but is probabilistic, consumes repository access/credits, and must not replace tests or human review. |
| Releases | Compose native primitives when ownership is defined | GitHub Releases, generated notes/release-please, artifact attestations, SBOM, and signing can help, but no generic release framework currently matches both Android and Seerr. |

Industry principles affecting the design are: least-privilege tokens; immutable/pinned third-party Actions; isolated ephemeral workspaces; deterministic and reproducible required checks; fail-closed publication; protected branches; GitHub-native durable status; short retention for development artifacts; explicit provenance for distributable releases; and corrective commits or revert PRs rather than destructive history rewriting. Agents are best placed after these boundaries exist—for semantic conflict analysis, failure triage, and drafting—not as autonomous authorities for objective validation, conflict resolution, release promotion, or merge.

### Target direction, trials, and unknowns

The current happy path is: implementation in an isolated worktree -> explicit user publication authorization -> complete scope audit -> deterministic local validation -> exact stage/commit and tree verification -> push and PR creation with `gh` -> required GitHub checks -> optional advisory review -> human merge. Failure before publication leaves the worktree intact; after publication use a corrective commit or GitHub revert PR. Never reset a shared dirty tree as automated recovery.

Move unattended schedules, upstream detection, PR/check state, review/merge, development artifacts, security reporting, and notifications to GitHub. Keep repository discovery, local validation, exact staging, and cheap tree identity local. Prioritize short-retention PR and main default-debug APK artifacts at P1. At P2, evaluate Codex PR review, CodeRabbit and Copilot review before custom review automation; verify current access, signal quality, cost and eligibility at adoption time. The benchmark did not establish review entitlements from an existing subscription; its pricing observations are not current eligibility claims. GitHub App installations and repository rules/settings also cannot be inferred completely from tracked files and require a separate read-only settings audit.

The former P1 prepare-pr direction became the immediate P0 v2 milestone and is integrated through PR #9. Its two human decisions and all snapshot/tree/publication safety remain current. I03 supersedes only validation selection: autonomous Standard now uses deterministic scope classification and mapped coverage without requiring a supplied filter; sensitive/unknown scope escalates to Full, while explicit filters remain supported. Prepare-pr still verifies drift, stages exactly, derives an honest Conventional Commit title, verifies `HEAD^{tree}`, safely pushes, and delegates PR lookup/creation to authenticated `gh`.

**Expected -> Observed -> Consequence:** v1's repeated confirmations protected a shared dirty-worktree prototype but created decision fatigue after the user had already requested publication. Those prompts and the unauthenticated manual compare-URL fallback were removed from the normal path. The Git-native identity checks, refused-artifact audit, complete branch-plus-working scope, detailed `prepare-pr.log`, safe fast-forward publication, and diagnostic phase/state interface remain. Missing/unauthenticated `gh`, ambiguous/out-of-scope changes, validation/autofix drift, title ambiguity, tree mismatch, remote divergence, or policy violations stop closed without destructive recovery. Once a PR exists, GitHub owns required checks and mergeability; prepare-pr does not poll, repair, merge, or clean up.

The next separate maintenance checkpoint is GitHub-hosted upstream-change detection, followed by the other P1 milestones in the roadmap. PR/main APK retention, CI profiling and recovery policy are approved next; security/review tooling, releases, specialized agents and Seerr portability follow later. None is operational merely because prepare-pr v2 merged.

The adjacent local-validation quality-of-life work is intentionally small: every phase now prints an ISO timestamp and `Running...`, then reports its completion timestamp and existing elapsed duration. Standard/Full resolve `pre-commit` from `PATH` first and fall back to `python -m pre_commit`; failure guidance is explicit when neither command is available. Output, autofix warnings, exit-code propagation, Java process-environment setup, and `validation.log` behavior remain unchanged.

### Prepare-pr v2 GitHub CLI quoting correction

**Expected -> Observed -> Consequence:** the first real `-Phase Publish` dogfood successfully verified the committed tree and pushed `chore/prepare-pr-v2`, but Windows PowerShell split the inline `--jq '.[] | "#\(.number) \(.url)"'` expression before `gh` received it. GitHub CLI rejected the stray `\(.url)` argument, so existing-PR lookup failed safely and no PR was created. Publication now calls `gh pr list --repo <repo> --base <base> --head <branch> --state open --json number,url` with no jq program and parses the JSON in PowerShell. Existing PRs are still reported and reused; an empty array still proceeds to exactly one `gh pr create`. The authenticated-`gh` requirement, no-duplicate rule, safe push behavior, and resumable `-Phase Publish` boundary are unchanged.
