# Item 6 — Mosaic delivery and tooling consolidation

This document is the durable, multi-PR checklist for the 143 numbered requirements in the Item 6 specification. The source specification remains external planning input; this checklist records repository evidence, dependencies, readiness, and completion.

Status terms used below:

- **READY** — audit evidence is sufficient to begin a separately approved implementation checkpoint.
- **BLOCKED** — implementation needs additional evidence or an explicit external/user decision.
- **DEFERRED** — intentionally outside Item 6 implementation or scheduled after prerequisite checkpoints.
- Checked boxes mean the specified audit/document task is complete, not that later implementation covered by the same source requirements is complete.

## Current audit snapshot

- Audit date: 2026-09-09.
- Repository: `constbogdan/Wholphin`, clean `main` at `a1ffce53`; `origin` and `upstream` have their documented meanings.
- Scope: read-only repository audit plus this document. No workflow, script, application, GitHub setting, or external state was changed.
- Evidence: current workflows/scripts/tasks and durable live-validation records. No new hosted run was fetched; exact task-level hosted timing remains an evidence gap.

## Audit and decision packages

- [x] **A01 — AUDIT — Freeze the live trust, identity, compatibility, and end-state contracts** (Items 1, 23, 35, 42, 49, 73, 76, 77, 79)
  - Evidence: Development is protected `main` → successful exact-main CI → unsigned Release → isolated Environment-bound signing → verification → immutable `downstream-build-N` plus rolling `develop`. Stable manually promotes authenticated exact signed Development bytes. Recovery resumes from unsigned or signed artifacts without Gradle.
  - Keep distinct: source SHA/tree, `versionName`/`versionCode`, immutable and rolling tags, APK digest, signer digest, and display name. Preserve `Wholphin-release.apk`, `mosaic-release.json`, existing tags/channels, permanent signer, installed builds, and updater behavior until an explicit tested migration.
  - Correction: Item 6's historical “Guided” wording is superseded by the operational autonomous `prepare-pr` v2 contract. The two human boundaries remain explicit publication authorization and later PR merge/reject.
  - Result: safety/compatibility constraints are **READY** as acceptance criteria for every implementation checkpoint.

- [x] **A02 — AUDIT — Map the current execution and SHA/trust graph** (Items 2, 51, 81–83, 141)
  - Current graph: local `validate-local`/`prepare-pr` → PR `CI` on the synthetic merge checkout → protected-main merge → push `CI` on the actual main SHA → trusted `workflow_run` Development build/sign/publish → optional manual Stable promotion. Manual recovery and scheduled/manual Upstream Sync are separate guarded paths.
  - There is no separate merge-gate workflow: `.github/workflows/ci.yml` is both PR and main validation. `prepare-pr` validates the working snapshot and verifies staged/committed trees; hosted PR CI provides a clean merge-context run; main CI validates the actual merged SHA.
  - Workflow inventory:

    | Workflow | Trigger / SHA | Heavy work / artifact | Authority | Audit status |
    | --- | --- | --- | --- | --- |
    | `CI` | PR merge checkout; push `main`; manual | pre-commit, all Python tests, full defaultDebug compile/test/assemble; PR Debug APK | read-only | active, authoritative validation |
    | `Development build` | push `main`, `develop/*` | upstream clean Release+Debug publisher | upstream-only write job | guarded; sidebar noise / suspected downstream-obsolete |
    | `Create release` | `v*` tag | upstream AAB/APK build and draft release | upstream-only write job | guarded inherited publisher; retain pending policy decision |
    | `Mosaic development release` | successful main `CI`; exact-SHA manual | defaultRelease, unsigned/signed artifacts, Development releases | isolated sign; publish-only contents write | active/live validated |
    | `Mosaic development resume` | manual exact inputs | artifact verification/sign or reverify; no Gradle | isolated sign or publish-only write | active recovery/live unsigned recovery |
    | `Mosaic signing exercise` | manual exact main SHA | full Debug + Release, signed test artifact | isolated sign; no release write | exercise; usefulness to decide |
    | `Mosaic stable promotion` | manual exact inputs | download/verify exact signed bytes; no build/sign | publish-only contents write | active/live validated, manual |
    | `Upstream synchronization` | daily 06:23 UTC; manual | isolated Git integration and JSON evidence | observation read-only; scoped issue/App publication | active; blocked-path validated, clean publication still pending natural evidence |

  - Missing evidence: representative raw hosted logs for task-by-task PR/main execution and a naturally occurring clean Upstream candidate. This does not block the first classifier checkpoint.

- [x] **A03 — AUDIT — Establish the measured timing and validation-overlap baseline** (Items 3, 52, 84, 85)
  - Live ranges: ordinary main CI about 5–7 minutes; automatic Development build/sign/publish 9m55s/37s/18s (11m02s total); earlier signing exercise build/sign about 16m43s/34s; Stable verify/publish about 38s/20s; artifact recovery can perform zero Gradle work.
  - Confirmed repetition: every PR and resulting main push runs the same full defaultDebug graph; every APK-relevant main then separately compiles defaultRelease. Tooling/docs-only main changes currently enter both Android CI and automatic Development Release.
  - Local Full invokes compile, test, and assemble in three Gradle processes; dependencies may be up-to-date, but configuration/task-graph setup repeats. Standard invokes the unit-test task repeatedly with separate filters. Exact executed-task duplication needs log/Build Scan measurement before consolidation.
  - Different evidence that must not be called redundant: working-tree local validation, PR synthetic merge validation, actual merged-main validation, Debug versus Release variants, isolated signing, and fresh promotion verification.
  - Target metrics: non-APK changes perform zero Android build/sign/release work; merged heavy Android evidence normally runs once; Release compiles once per release-relevant main state; sign/publish/promotion/recovery perform zero Gradle work.

- [x] **A04 — AUDIT — Map artifact, provenance, recovery, and source-of-truth ownership** (Items 7, 8, 43, 44, 86, 94–96, 126–128)
  - Current artifact graph: PR CI produces a universal defaultDebug APK retained 7 days; main CI does not retain its Debug APK. Development independently builds authoritative unsigned defaultRelease → seven-day immutable artifact ID → Environment-bound signer → verified signed artifact → immutable GitHub prerelease + rolling Development prerelease. Stable downloads and re-verifies the immutable Development asset and publishes the exact bytes.
  - Recovery correctly authenticates original run/artifact/source/provenance and resumes at unsigned or signed checkpoints. Signing has read-only contents and no Gradle/release write; publication has write but no signing secret or Gradle.
  - Confirmed opportunity: main CI and Development Release do not yet share an authoritative Release artifact. Whether Debug evidence can be replaced or combined with Release evidence is **BLOCKED** on task-graph/variant measurement; do not collapse variants by assumption.
  - Reuse boundary: keep security-sensitive jobs explicit; share deterministic helpers/composite implementation underneath. Candidate canonical owners need consolidation for release relevance, risk, manifest verification, version allocation, and idempotency.

- [x] **A05 — AUDIT — Design independent release-relevance and validation-risk classification** (Items 4, 6, 9, 10, 41, 87–93, 135, 136)
  - Initial finding: no classifier existed; `CI` ran Android work for every PR/main change, and every successful main push could trigger Development Release even when only docs or isolated tooling changed. I01 now implements the Development-release boundary only; PR/main validation optimization remains I02/I03.
  - Required dimensions are independent: `apk-relevant | android-validation-only | tooling-only | docs-only | unknown` and `low | normal | high` risk. Release/signing workflow changes can be non-APK but high risk; ordinary app UI can be APK-relevant but normal risk.
  - Eligibility must compare the last successfully published Development source through current trusted main—not only the latest commit—so an earlier blocked APK change cannot be skipped after a tooling-only merge. Unknown and indirect security inputs escalate conservatively.
  - Preserve the deterministic commit-derived allocator and Android monotonicity. Version gaps caused by skipped non-APK commits are acceptable by default and safer than a contiguous-number migration.
  - Result: **IMPLEMENTED by I01 / OFFLINE VALIDATED.** External branch/ruleset changes remain blocked, and hosted live acceptance is still required before I01 is complete.

- [x] **A06 — AUDIT — Define local/PR/main responsibility, test tiers, progress, tasks, and concurrency** (Items 5, 11–14, 38–40, 50, 53–55, 59–61, 80, 97–99, 132, 133, 137–139)
  - Current local policy is Fast focused tests; Standard pre-commit + focused/acquisition regressions + compile; Full pre-commit + full defaultDebug compile/test/assemble. `prepare-pr` calls this policy and does not add a second private Gradle graph.
  - Current hosted CI is Full for all PRs and main pushes. PR concurrency cancels superseded runs by PR/ref; Development/Stable/recovery share a non-cancelling publication group. Keep cancellation away from signing/mutation without recovery semantics.
  - `validation.log` and `prepare-pr.log` preserve diagnostics, but console output still streams full Gradle output rather than the concise stage summaries requested by Item 6.
  - Correction: `prepare-pr` normal mode is autonomous v2, not interactive Guided. Preserve its scope/tree/refusal guarantees and two human authority boundaries while simplifying output only.
  - Concrete defect: `.vscode/tasks.json` invokes Fast and Standard without `-TestFilter`, but both levels require real focused JVM patterns. Those two tasks fail by contract; Full and Prepare PR remain usable. Fix in the local-experience checkpoint without inventing filters or exposing publish/promote shortcuts.
  - Device smoke testing remains optional/advisory until runtime and reliability are measured; no personal backend credentials belong in CI.

- [x] **A07 — AUDIT — Identify cleanup, performance, warning, API, and retry candidates** (Items 15, 16, 56–58, 100–102, 129–131)
  - High-confidence candidates: `Development build` is guarded to upstream and becomes a one-second skipped workflow in this fork; production Development still exposes “signing exercise” step/artifact wording. `Create release` is also upstream-guarded but retains upstream tag behavior and is not safe to delete without deciding sync/compatibility ownership. The standalone signing exercise may remain useful for key custody/disaster diagnostics.
  - Gradle configuration executes `scripts/mosaic_version.py`; this is the leading explanation for external-Python configuration-cache invalidation, but causality and stable input alternatives still require measured proof.
  - Release lint debt (~252 errors/106 warnings) is not part of current required validation; introducing it as a blocking gate needs a baseline/migration. Other recurring Room/deprecation/optional-codec/Gradle warnings need separate ownership classification, not opportunistic fixes.
  - API calls, checkouts, manifest parsing, artifact transfers, and retries are **READY FOR MEASUREMENT**, not deletion. Mutations may retry only after idempotent state checks; rate limit, permission, not-found, conflict, and transient failures must remain distinguishable.

- [x] **A08 — AUDIT — Build a coherent naming, release-presentation, APK-alias, and documentation migration plan** (Items 17–20, 45–47, 103–107, 123–125)
  - Machine contracts (`develop`, `downstream-build-N`, `mosaic-v1.0.N`, version/digests/manifests) must remain stable while human workflow/job/step/release names become lifecycle-accurate.
  - Confirmed misleading wording remains in real Development signing summaries/artifact names. `Mosaic-release.apk` exists during signed transport, while published updater compatibility still requires `Wholphin-release.apk`.
  - Any asset migration must publish identical bytes under both names temporarily and atomically update updater preference/fallback tests; no duplicate build. Historical release title/body changes and metadata backfill require explicit approval and must never alter tags/assets/digests/latest semantics.
  - UTF-8/editorconfig/mojibake protection is a hard constraint. The formerly broken `PREPARE_PR` handoff anchor currently resolves to an existing heading; recheck links after documentation consolidation.

- [x] **A09 — AUDIT — Preserve and refine Upstream Sync outcomes, journal, conflicts, schedule, and concurrency** (Items 24–26, 62–64, 108–119, 134)
  - Current observe job is read-only; ready-only App authority publishes branches/PRs; blocked outcomes do not mint that authority. Exact SHA-pair identity, no force push, no automatic semantic resolution, and issue/PR deduplication are implemented.
  - Live blocked-path behavior is successful business-state evidence, not equivalent to broken infrastructure. Current docs record a later conflict pair (`SeriesOverview.kt`, `SeriesViewModel.kt`), superseding the Item 6 example paths; preserve exact evidence per candidate rather than hard-coding examples.
  - Structured outcomes should distinguish `ready`, `blocked`, `no_delta`, `superseded`, `skipped_non_apk`, and `error`; summaries should make required action obvious. The Issue is a journal, not the integration gate.
  - Current schedule is once daily at 06:23 UTC, not the desired ~08:00/17:00/23:00 Bucharest cadence. Timezone support and scheduler-delay evidence need confirmation before changing it.
  - Draft conflict PR design is **BLOCKED** on a safe representation that cannot resemble a merge-ready unresolved index. Labels/settings and live publication require explicit authorization.

- [x] **A10 — AUDIT — Plan repository identity, metadata, review policy, and external GitHub organization** (Items 21, 22, 36, 37, 65–72, 78)
  - README/labels/issues/project/milestones/badges/backfill remain plans, not operational claims. Mosaic should identify as a personal experimental downstream, credit Wholphin, and encourage upstream/ecosystem reuse.
  - Deterministic checks remain required; advisory AI review must not become a security gate. Merge queue, CODEOWNERS, auto-merge, rulesets, security settings, labels, projects, milestones, and historical edits are **EXTERNAL / USER APPROVAL** work.
  - Keep taxonomy small and milestones capability/release-oriented rather than adding project-management bureaucracy.

- [x] **A11 — AUDIT — Define Development/Stable withdrawal and forward recovery** (Items 32–34, 120–122)
  - Repointing rolling `develop` can protect devices that have not updated, but immutable bad builds remain provenance records. Already-updated devices require a fix/revert with a higher versionCode; normal Android downgrade is not a recovery plan.
  - Stable recovery remains newer fixed Development → real-world validation → explicit exact-byte Stable promotion. A catastrophic updater failure needs a newer APK with the same signer and package, installable without clearing data; ADB is not the sole documented path.
  - Operator rollback/repoint tooling is **BLOCKED** on explicit authorization and acceptance design. Never mutate/re-version old APK bytes or delete history.

- [x] **D01 — DEFERRED — Preserve product/UI follow-ups outside Item 6** (Items 27–31, 140)
  - Separate future work: proactive non-nagging update notification, duplicate updater action ownership, update-state vocabulary, Settings redesign/channel-selector visuals, trustworthy telemetry research and UI-only download smoothing, and unrelated card/UI roadmap ideas.
  - These ideas are recorded but must not enter delivery/tooling consolidation PRs.

## Implementation checkpoints

- [ ] **I01 — IMPLEMENT — Add canonical change classification and skip non-APK Development releases** (Items 4, 6, 9, 10, 41, 52, 87–93, 117–119, 128, 135, 136, 142)
  - Status: **IMPLEMENTED / OFFLINE VALIDATED — repository Full validation and minimum post-merge live acceptance pending.**
  - Depends on: A01–A05.
  - Completion criterion: one repository-owned, offline-tested classifier independently emits release relevance and validation risk; unknown/indirect inputs fail conservative; eligibility evaluates last published source through current main; proven non-APK ranges finish before Gradle/version/sign/publish and do not create a release, while a pending APK-relevant change cannot be skipped. Existing allocator and superseded-main rules remain unchanged.
  - Evidence: `scripts/mosaic_change_classification.py` is the single deterministic path classifier. It emits `apk-relevant | android-validation-only | tooling-only | docs-only | unknown` independently from `low | normal | high`, and only `apk-relevant` or `unknown` requires an APK release.
  - Evidence: Development eligibility authenticates the currently exposed rolling `develop` release against its immutable `downstream-build-N` annotated provenance, prerelease and exact two-asset digests. It then classifies `published source SHA..current trusted main SHA`; an absent/inconsistent publication, incomplete history, non-ancestor source or unclassified path fails to `unknown/high` and requires the release path.
  - Evidence: rename detection is disabled for the range diff so a moved/deleted APK input remains visible. Offline tests cover accumulated multi-commit APK relevance, independent risk, unknown inputs, production/build/proto/signing boundaries, non-ancestor history, mode-only changes where supported, source moves, authenticated/tampered publication state and workflow boundaries.
  - Evidence: `.github/workflows/mosaic-development-release.yml` now runs a read-only `classify` job before setup, Gradle or version allocation. Proven non-APK ranges produce `skipped_non_apk`; `build` is gated off and the unchanged `sign`/`publish` dependency chain consequently skips. APK-relevant or uncertain ranges retain the existing trusted build/sign/publish path.
  - Preserved: `mosaic_version.py`, exact-main/latest-successful-CI checks, superseded-main behavior, signing Environment, immutable provenance, recovery, Stable promotion and updater asset/version compatibility are unchanged.
  - Minimum live acceptance after merge: merge one known non-APK-only range after a published Development baseline and verify `classify=skipped_non_apk`, no build/sign/publish jobs and no tag/release/version allocation; the next APK-relevant merge must classify `apk-relevant` and complete the existing automatic Development path across the accumulated baseline-to-main range.

- [ ] **I02 — IMPLEMENT — Consolidate authoritative main validation and Release artifact ownership** (Items 5, 7, 8, 43, 44, 52, 59, 73, 86, 94–96, 126–128, 133, 143)
  - Status: **BLOCKED on task/variant and artifact-retention measurements.** Depends on I01.
  - Completion criterion: the actual merged main SHA gains each required expensive proof once, one clear workflow produces the authenticated unsigned Release artifact for release-relevant state, and sign/publish/recovery consume exact immutable artifact IDs with no Gradle or weakened permissions. Debug/Release evidence changes are demonstrated, not assumed.

- [ ] **I03 — IMPLEMENT — Optimize PR/local validation and human-facing progress** (Items 6, 11–14, 38–40, 50, 53–55, 59–61, 80, 97–99, 132, 137–139, 142, 143)
  - Status: **READY after I01 policy exists; task-graph changes need measurement.**
  - Completion criterion: deterministic tiers run relevant checks with unknown paths escalating; local and GitHub output show truthful stages/timings while full logs remain available; no safety confirmation/tree identity is lost; VS Code tasks match real parameter contracts; no dangerous mutation task is exposed; checkpoint dry-run/offline and required live acceptance are documented.

- [ ] **I04 — IMPLEMENT — Remove proven dead work and consolidate measured tooling hot spots** (Items 15, 16, 56–58, 100–102, 126–131, 142)
  - Status: **PARTLY READY** (upstream-only sidebar noise and naming); broader cleanup waits for I02/I03 measurements.
  - Completion criterion: every deletion has caller/operator evidence, one canonical helper owns each deterministic contract, API/checkouts/artifact transfers are reduced without stale security state, transient retries are bounded/idempotent, and retained upstream/recovery/exercise paths have an explicit purpose.

- [ ] **I05 — IMPLEMENT — Apply coherent lifecycle naming and compatible release presentation** (Items 17–20, 42, 45–47, 57, 77, 103–107, 123–125, 142, 143)
  - Status: **READY for vocabulary proposal; BLOCKED for asset/historical mutations.** Depends on stabilized I02/I04 names.
  - Completion criterion: a reviewed before/after map is applied consistently to human-facing workflows/jobs/steps/artifacts/docs; stable machine contracts remain compatible; signing-exercise wording disappears from production paths; any APK alias migration proves identical bytes and old-updater fallback; historical changes occur only with approval.

- [ ] **I06 — IMPLEMENT — Refine Upstream Sync journaling, outcome semantics, and cadence** (Items 23–26, 62–64, 108–119, 128–131, 134, 142, 143)
  - Status: **READY for offline outcome/summary and schedule design; BLOCKED for labels, live mutation, and Draft-conflict workspace.** Independent after I01 shared classification boundaries settle.
  - Completion criterion: expected outcomes are structured and visually distinct from errors; identical observations are idempotent/concurrency-safe; journal and PR roles are explicit; schedule intent/DST/delay are documented; clean/blocked offline cases pass; no semantic conflict is auto-resolved and no raw conflict markers/index are published.

- [ ] **I07 — IMPLEMENT — Add explicit Development/Stable withdrawal and recovery operations** (Items 8, 32–35, 43, 76, 77, 120–122, 124, 143)
  - Status: **BLOCKED — explicit operator design and user approval required.** Depends on I02 artifact ownership.
  - Completion criterion: authenticated exact-byte Development repoint and forward-recovery runbooks distinguish not-yet-updated from already-updated devices; Stable emergency promotion remains exact-byte/manual; immutable history and signer/version monotonicity are preserved; failure and live acceptance procedures are documented.

- [ ] **D02 — DOCUMENT — Consolidate operational documentation after each checkpoint** (Items 45–47, 51, 62, 70–72, 75, 119, 123–125)
  - Status: **ONGOING.**
  - Completion criterion: operational docs describe only current behavior; handoff retains expensive historical lessons/corrections; links/UTF-8 checks pass; each checkpoint reports old/new graph, measured savings, evidence retained, risks, compatibility, and next work.

- [ ] **E01 — EXTERNAL / USER APPROVAL — Apply GitHub settings/metadata or mutate historical/public state** (Items 36, 37, 40, 65–69, 78, 93, 106, 115, 120, 122, 138, 139)
  - Status: **BLOCKED by design until separately authorized.**
  - Completion criterion: a reviewed proposal identifies exact setting/object mutations, permissions, rollback, cost/eligibility, and security impact; the user explicitly authorizes execution. Repository code may prepare proposals/tests but cannot imply these controls are live.

- [ ] **V01 — VALIDATE — Keep every checkpoint independently safe and produce the final Item 6 report** (Items 48, 74, 75, 142, 143)
  - Status: **READY as the governing validation gate.**
  - Completion criterion: every PR leaves main buildable and Development/Stable/recovery/updater contracts usable; infrastructure changes receive strong old/new offline coverage and the minimum approved live acceptance; quick wins and caution items remain explicit; final before/after matrix and measured outcomes satisfy Item 74.

## Initial audit report (A–O)

### A. Executive summary

1. The delivery chain is live and security boundaries are sound; optimize around it rather than replacing it.
2. The largest confirmed waste is unconditional Android CI and Development Release for non-APK changes.
3. PR and main both run Full defaultDebug; main then triggers a separate defaultRelease compilation. Some repetition proves different trees/variants, so task-level consolidation needs measurement.
4. Exact unsigned/signed artifact recovery and exact-byte Stable promotion already prove zero-build downstream stages are practical.
5. Release relevance and validation risk need separate deterministic, conservative classifiers.
6. Main CI should ultimately own authoritative merged-state evidence/artifact production, but Debug/Release consolidation is not yet proven.
7. Upstream-only `Development build`/`Create release` are safely guarded; the former is high-confidence sidebar noise, while deletion of either awaits an explicit compatibility/upstream-maintenance decision.
8. `prepare-pr` is autonomous v2; historical Guided requirements are superseded. Its safety checks remain valuable, but output is not yet concise.
9. Fast/Standard VS Code tasks are currently invalid because they supply no required focused test filter.
10. Security settings, labels, historical releases, merge queue, and live workflow operations remain explicit external decisions.

### B. Current execution graph

```text
working tree -> validate-local/prepare-pr -> exact local commit
             -> PR CI (synthetic merge, full defaultDebug, PR Debug artifact)
             -> protected main
             -> main CI (actual merged SHA, full defaultDebug)
             -> classify last published Development source..current main
                -> proven non-APK: skipped_non_apk
                -> APK-relevant/unknown: Development defaultRelease build
                   -> unsigned artifact -> Environment-bound sign
                   -> verify -> signed artifact
                   -> immutable downstream-build-N + rolling develop

downstream-build-N -> manual Stable verify -> exact-byte mosaic-v1.0.N
unsigned/signed checkpoint -> manual resume -> sign/reverify -> publish
scheduled/manual sync -> read-only observe -> ready PR or durable blocked record
```

### C. Workflow inventory

See A02. Active trust paths are `CI`, Development release/resume, Stable promotion, and Upstream Sync. Signing exercise is diagnostic. Inherited publishers are repository-guarded, not currently downstream publication paths.

### D. Measured timing/overlap matrix

See A03. Confirmed waste: Android/release work for tooling-only main changes. Suspected optimization: local multi-invocation Gradle and Debug/Release overlap; requires actual executed-task evidence.

### E. Gradle/task overlap

Local Standard starts up to six Gradle invocations; local Full starts three. Hosted CI runs one defaultDebug invocation. Signing exercise runs separate full Debug and defaultRelease invocations. Development builds only defaultRelease after successful main defaultDebug CI. Similar task names do not establish same variant or tree evidence.

### F. Artifact/provenance graph

See A04. The strongest reusable seams are immutable numeric Actions artifact IDs, provenance manifests, APK/source/tree digests, immutable Development releases, and exact-byte Stable promotion.

### G. Release-relevance classifier implementation

I01 uses repository-owned rules with outputs `apk-relevant`, `android-validation-only`, `tooling-only`, `docs-only`, `unknown`. It evaluates the complete publication backlog from the authenticated last successful Development source to current main. Production source/resources/manifests/dependencies/build/codegen are APK-relevant; tests/automation are validation-relevant; docs/metadata are normally non-Android; unknown or indirect release/security inputs escalate. PR/main validation-tier consumption remains I03.

### H. Risk classifier implementation

I01 emits separate `low`, `normal`, `high` output. Signing, release, updater, identity, packaging, persistence migration, security automation, and their imported helpers are high risk. Ordinary app work is normal; proven docs/metadata can be low. Consuming this risk in PR/local validation remains I03; Stable remains explicit human promotion.

### I. Dead/redundant candidates

- High confidence: downstream-visible one-second skipped `Development build`; production “signing exercise” labels.
- Medium confidence: inherited `Create release`, standalone signing exercise, repeated manifest/API helpers—retain until operator/upstream use is proven absent or consolidated.
- Not dead: recovery workflows, exact-byte verification, repository guards, upstream observation, and legacy APK alias.

### J. Naming/UX proposal

Use lifecycle stages `Classify`, `Validate`, `Build`, `Sign`, `Verify`, `Publish`, `Recover`. Candidate workflow names remain `CI — Pull Request/Main`, `Mosaic — Development Release/Recovery/Stable Promotion`, and `Upstream — Synchronization`; retain machine IDs where dispatch/artifact/updater compatibility depends on them.

### K. Upstream Sync refinement proposal

Preserve observation/authority separation and exact-pair idempotency. Improve outcome conclusions and summaries first, then journal lifecycle and three-times-daily scheduling. Treat conflict Draft PRs and labels as later, separately accepted work.

### L. Target architecture

```text
PR -> classify risk/relevance -> relevant fast checks -> merge
main -> authoritative heavy validation once
     -> if release-relevant: authoritative Release once -> sign -> verify -> Development
     -> if non-APK: record skip, no Android/version/sign/release
known-good immutable Development -> explicit exact-byte Stable promotion
```

### M. Checkpoint order

I01 classifier/skip → I02 main artifact consolidation → I03 PR/local tiers and progress → I04 proven cleanup/performance → I05 naming/compatibility → I06 Upstream refinements. I07 recovery operations follows stable artifact ownership. D01 stays outside Item 6; D02 and V01 apply throughout.

### N. Expected measurable savings

- Proven non-APK PRs/merges: Android compile and Development build/sign/publish reduced to zero.
- APK-relevant merged state: target one authoritative heavy main graph and one Release compilation, subject to variant evidence.
- Signing/publishing/Stable/recovery: retain zero Gradle work.
- Skips: seconds rather than current multi-minute Android + roughly 11-minute Development delivery.
- Exact future runner savings remain ranges until representative raw hosted task logs are captured.

### O. Risks and open questions

- Need raw hosted task logs/Build Scan-quality evidence before changing Debug/Release task coverage or Gradle invocation boundaries.
- I01 resolved the last-published-source contract offline; its remaining evidence gap is the minimum post-merge `skipped_non_apk` live run followed by an APK-relevant accumulated-range run.
- Need confirmation of GitHub timezone schedule syntax, scheduler delay, merge-queue/settings/plan availability, release immutability, labels/issues state, and security tooling eligibility before external changes.
- Need updater-version coverage before removing `Wholphin-release.apk`.
- Need a safe non-merge-ready conflict workspace before Draft conflict PR automation.
- Need separate authorization for settings, releases, labels, projects, workflows dispatch, rollback, or publication.

## Coverage table

The table assigns every source requirement one primary checklist owner. Implementation entries intentionally cite overlapping requirements where those constraints must be re-applied.

| Item | Checklist entry |
| ---: | :--- |
| 1 | A01 |
| 2 | A02 |
| 3 | A03 |
| 4 | A05 |
| 5 | A06 |
| 6 | A05 |
| 7 | A04 |
| 8 | A04 |
| 9 | A05 |
| 10 | A05 |
| 11 | A06 |
| 12 | A06 |
| 13 | A06 |
| 14 | A06 |
| 15 | A07 |
| 16 | A07 |
| 17 | A08 |
| 18 | A08 |
| 19 | A08 |
| 20 | A08 |
| 21 | A10 |
| 22 | A10 |
| 23 | A01 |
| 24 | A09 |
| 25 | A09 |
| 26 | A09 |
| 27 | D01 |
| 28 | D01 |
| 29 | D01 |
| 30 | D01 |
| 31 | D01 |
| 32 | A11 |
| 33 | A11 |
| 34 | A11 |
| 35 | A01 |
| 36 | A10 |
| 37 | A10 |
| 38 | A06 |
| 39 | A06 |
| 40 | A06 |
| 41 | A05 |
| 42 | A01 |
| 43 | A04 |
| 44 | A04 |
| 45 | A08 |
| 46 | A08 |
| 47 | A08 |
| 48 | V01 |
| 49 | A01 |
| 50 | A06 |
| 51 | A02 |
| 52 | A03 |
| 53 | A06 |
| 54 | A06 |
| 55 | A06 |
| 56 | A07 |
| 57 | A07 |
| 58 | A07 |
| 59 | A06 |
| 60 | A06 |
| 61 | A06 |
| 62 | A09 |
| 63 | A09 |
| 64 | A09 |
| 65 | A10 |
| 66 | A10 |
| 67 | A10 |
| 68 | A10 |
| 69 | A10 |
| 70 | A10 |
| 71 | A10 |
| 72 | A10 |
| 73 | A01 |
| 74 | V01 |
| 75 | V01 |
| 76 | A01 |
| 77 | A01 |
| 78 | A10 |
| 79 | A01 |
| 80 | A06 |
| 81 | A02 |
| 82 | A02 |
| 83 | A02 |
| 84 | A03 |
| 85 | A03 |
| 86 | A04 |
| 87 | A05 |
| 88 | A05 |
| 89 | A05 |
| 90 | A05 |
| 91 | A05 |
| 92 | A05 |
| 93 | A05 |
| 94 | A04 |
| 95 | A04 |
| 96 | A04 |
| 97 | A06 |
| 98 | A06 |
| 99 | A06 |
| 100 | A07 |
| 101 | A07 |
| 102 | A07 |
| 103 | A08 |
| 104 | A08 |
| 105 | A08 |
| 106 | A08 |
| 107 | A08 |
| 108 | A09 |
| 109 | A09 |
| 110 | A09 |
| 111 | A09 |
| 112 | A09 |
| 113 | A09 |
| 114 | A09 |
| 115 | A09 |
| 116 | A09 |
| 117 | A09 |
| 118 | A09 |
| 119 | A09 |
| 120 | A11 |
| 121 | A11 |
| 122 | A11 |
| 123 | A08 |
| 124 | A08 |
| 125 | A08 |
| 126 | A04 |
| 127 | A04 |
| 128 | A04 |
| 129 | A07 |
| 130 | A07 |
| 131 | A07 |
| 132 | A06 |
| 133 | A06 |
| 134 | A09 |
| 135 | A05 |
| 136 | A05 |
| 137 | A06 |
| 138 | A06 |
| 139 | A06 |
| 140 | D01 |
| 141 | A02 |
| 142 | V01 |
| 143 | V01 |
