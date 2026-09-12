# Item 6 — Mosaic delivery and tooling consolidation

This document is the durable, multi-PR checklist for the 143 numbered requirements in the Item 6 specification. The source specification remains external planning input; this checklist records repository evidence, dependencies, readiness, and completion.

Status terms used below:

- **READY** — audit evidence is sufficient to begin a separately approved implementation checkpoint.
- **BLOCKED** — implementation needs additional evidence or an explicit external/user decision.
- **DEFERRED** — intentionally outside Item 6 implementation or scheduled after prerequisite checkpoints.
- Checked boxes mean the specified audit/document task is complete, not that later implementation covered by the same source requirements is complete.

## Current audit snapshot

- Audit date: 2026-09-09.
- Repository: `constbogdan/Wholphin`, `main` at `7881aa19850c46e53b43504c38a81a2e62dbb9a3`; `origin` and `upstream` have their documented meanings.
- Scope: read-only repository/hosted-run audit plus documentation updates. No workflow, script, application, GitHub setting, publication, or other external state was changed.
- Evidence: current workflows/scripts/tasks, durable local records, and read-only GitHub run/job logs cited in the I01/I02 evidence sections.
- Follow-up audit, 2026-09-10: [upstream automation inventory and ownership proposal](ITEM_6_UPSTREAM_AUTOMATION_AUDIT.md), pinned to merged PR #26/main `3907726ce38a03936e5853e5e8d36fff6d4486e9` and locally available upstream `1778bdb34caa699c0590232a7de709a889839765`. The inventory is historical evidence; separately authorized I05 and I06 implementation is recorded in their checkpoints below.
- Post-Item-6 baseline cleanup: T0-1 CP2 removed inherited `.github/workflows/main.yml` and
  `.github/workflows/release.yml`. Both are now explicit DOWNSTREAM-OWNED absences. The Appstore /
  Fire TV AAB behavior recorded in the historical audit is not a supported Baseline T0 channel.

## Audit and decision packages

- [x] **A01 — AUDIT — Freeze the live trust, identity, compatibility, and end-state contracts** (Items 1, 23, 35, 42, 49, 73, 76, 77, 79)
  - Evidence: Development is protected `main` → successful exact-main CI → unsigned Release → isolated Environment-bound signing → verification → immutable `downstream-build-N` plus rolling `develop`. Stable manually promotes authenticated exact signed Development bytes. Recovery resumes from unsigned or signed artifacts without Gradle.
  - Keep distinct: source SHA/tree, `versionName`/`versionCode`, immutable and rolling tags, APK digest, signer digest, and display name. Preserve `Wholphin-release.apk`, `mosaic-release.json`, existing tags/channels, permanent signer, installed builds, and updater behavior until an explicit tested migration.
  - Correction: Item 6's historical “Guided” wording is superseded by the operational autonomous `prepare-pr` v2 contract. The two human boundaries remain explicit publication authorization and later PR merge/reject.
  - Result: safety/compatibility constraints are **READY** as acceptance criteria for every implementation checkpoint.

- [x] **A02 — AUDIT — Map the current execution and SHA/trust graph** (Items 2, 51, 81–83, 141)
  - Current graph after I02: local `validate-local`/`prepare-pr` → PR `CI` on the synthetic merge checkout → protected-main merge → push `CI` on the actual main SHA → Debug validation → conditional sequential Release assembly and authenticated unsigned artifact → trusted `workflow_run` Development download/sign/verify/publish with zero Gradle → optional manual Stable promotion. Manual recovery and scheduled/manual Upstream Sync are separate guarded paths.
  - There is no separate merge-gate workflow: `.github/workflows/ci.yml` is both PR and main validation. `prepare-pr` validates the working snapshot and verifies staged/committed trees; hosted PR CI provides a clean merge-context run; main CI validates the actual merged SHA.
  - Workflow inventory:

    | Workflow | Trigger / SHA | Heavy work / artifact | Authority | Audit status |
    | --- | --- | --- | --- | --- |
    | `CI` | PR merge checkout; push `main`; manual | PR: trusted-base classification, relevant hygiene/tooling and targeted or Full Android evidence; Full-only PR Debug APK. Main/manual: all-files pre-commit, all Python tests, full defaultDebug; release-relevant main additionally assembles authenticated defaultRelease | read-only | I03 implemented/pending hosted tier acceptance; authoritative main validation and I02 Release-artifact owner unchanged |
    | `Development build` | push `main`, `develop/*` | upstream clean Release+Debug publisher | upstream-only write job | removed in T0-1 CP2; downstream-owned absence |
    | `Create release` | `v*` tag | upstream AAB/APK build and draft release | upstream-only write job | removed in T0-1 CP2; store/AAB ownership explicitly deferred |
    | `Mosaic development release` | successful main `CI`; exact-SHA manual | authenticate/download main-CI unsigned artifact, sign, verify, Development releases; zero Gradle | isolated sign; publish-only contents write | I02 complete: offline, local Full, hosted, publication, updater, and device accepted |
    | `Mosaic development resume` | manual exact inputs | artifact verification/sign or reverify; no Gradle | isolated sign or publish-only write | active recovery/live unsigned recovery |
    | `Mosaic signing exercise` | manual exact main SHA | full Debug + Release, signed test artifact | isolated sign; no release write | exercise; usefulness to decide |
    | `Mosaic stable promotion` | manual exact inputs | download/verify exact signed bytes; no build/sign | publish-only contents write | active/live validated, manual |
    | `Upstream synchronization` | fixed UTC 06:00/15:00/21:00; manual | ownership-aware isolated Git integration, journal and JSON evidence | observation read-only; scoped Issue/App publication only when required | I06 offline validated; natural per-outcome acceptance pending |

  - I02 evidence update: representative raw hosted logs now cover PR/main Debug, Development Release, and sequential Debug+Release execution. A naturally occurring clean Upstream candidate remains separate missing evidence and does not block I02.

- [x] **A03 — AUDIT — Establish the measured timing and validation-overlap baseline** (Items 3, 52, 84, 85)
  - Pre-I02 live ranges: ordinary main CI about 5–7 minutes; automatic Development build/sign/publish 9m55s/37s/18s (11m02s total); earlier signing exercise build/sign about 16m43s/34s; Stable verify/publish about 38s/20s; artifact recovery can perform zero Gradle work.
  - Confirmed repetition before I01/I02: every PR and resulting main push ran the same full defaultDebug graph; every APK-relevant main then separately compiled defaultRelease in Development. I01 removed Development work for proven non-APK ranges; I02 moved required Release assembly into the main-CI workspace. I03 now implements PR/local tiers; hosted timing acceptance remains pending.
  - Local Full invokes compile, test, and assemble in three Gradle processes; dependencies may be up-to-date, but configuration/task-graph setup repeats. Standard invokes the unit-test task repeatedly with separate filters. Hosted logs now establish the I02 boundary: Debug compilation executes once within CI's single invocation, limited common work is reusable across sequential variants, and Debug/Release KSP/Kotlin/packaging remain distinct.
  - Different evidence that must not be called redundant: working-tree local validation, PR synthetic merge validation, actual merged-main validation, Debug versus Release variants, isolated signing, and fresh promotion verification.
  - Target metrics: non-APK changes perform zero Android build/sign/release work; merged heavy Android evidence normally runs once; Release compiles once per release-relevant main state; sign/publish/promotion/recovery perform zero Gradle work.

- [x] **A04 — AUDIT — Map artifact, provenance, recovery, and source-of-truth ownership** (Items 7, 8, 43, 44, 86, 94–96, 126–128)
  - Current artifact graph after I02: PR CI produces a universal defaultDebug APK retained 7 days. A release-relevant main CI validates Debug, then sequentially assembles the authoritative unsigned defaultRelease and uploads it under a source/version/run/attempt-bound name with a seven-day immutable artifact ID. Development authenticates that exact CI producer, run attempt, job, artifact ID/name/digest/timestamps and payload before Environment-bound signing → verified signed artifact → immutable GitHub prerelease + rolling Development prerelease. Stable downloads and re-verifies the immutable Development asset and publishes the exact bytes.
  - Recovery correctly authenticates original run/artifact/source/provenance and resumes at unsigned or signed checkpoints. Signing has read-only contents and no Gradle/release write; publication has write but no signing secret or Gradle.
  - I02 resolution: main CI now owns both required Debug evidence and the unsigned Release artifact in one sequential workspace. Debug and Release remain distinct bounded invocations; neither substitutes for the other, and their compilers are not run concurrently.
  - Reuse boundary: keep security-sensitive jobs explicit; share deterministic helpers/composite implementation underneath. Candidate canonical owners need consolidation for release relevance, risk, manifest verification, version allocation, and idempotency.

- [x] **A05 — AUDIT — Design independent release-relevance and validation-risk classification** (Items 4, 6, 9, 10, 41, 87–93, 135, 136)
  - Initial finding: no classifier existed; `CI` ran Android work for every PR/main change, and every successful main push could trigger Development Release even when only docs or isolated tooling changed. I01 implemented release skipping, I02 moved authoritative Release ownership, and I03 now implements PR/local validation consumption; hosted I03 acceptance remains open.
  - Required dimensions are independent: `apk-relevant | android-validation-only | tooling-only | docs-only | unknown` and `low | normal | high` risk. Release/signing workflow changes can be non-APK but high risk; ordinary app UI can be APK-relevant but normal risk.
  - Eligibility must compare the last successfully published Development source through current trusted main—not only the latest commit—so an earlier blocked APK change cannot be skipped after a tooling-only merge. Unknown and indirect security inputs escalate conservatively.
  - Preserve the deterministic commit-derived allocator and Android monotonicity. Version gaps caused by skipped non-APK commits are acceptable by default and safer than a contiguous-number migration.
  - Result: **IMPLEMENTED by I01 / OFFLINE + LIVE VALIDATED.** Hosted run `34379457375` proved the accumulated-range classifier and non-APK skip at main `7881aa19850c46e53b43504c38a81a2e62dbb9a3`. External branch/ruleset changes remain blocked.

- [x] **A06 — AUDIT — Define local/PR/main responsibility, test tiers, progress, tasks, and concurrency** (Items 5, 11–14, 38–40, 50, 53–55, 59–61, 80, 97–99, 132, 133, 137–139)
  - I03 implementation state: Fast/Standard derive deterministic relevant checks and accept explicit filters; Full keeps all-files pre-commit plus the complete defaultDebug graph. `prepare-pr` calls this policy and does not add a private Gradle graph.
  - Hosted PR CI is tiered while the required job name remains stable; protected-main/manual CI stays Full. PR concurrency still cancels only superseded runs by PR/ref; Development/Stable/recovery retain non-cancelling publication semantics.
  - Concise stages now point to complete ignored per-stage logs; root compatibility logs remain. Error excerpts are bounded and preserve source locations.
  - `prepare-pr` remains autonomous v2 with scope/tree/refusal guarantees and two human authority boundaries.
  - The no-filter VS Code defect is corrected by classifier-derived validation. `.vscode/tasks.json` is source-controlled and exposes no publication, rollback, Stable, or force operation.
  - Device smoke testing remains optional/advisory until runtime and reliability are measured; no personal backend credentials belong in CI.

- [x] **A07 — AUDIT — Identify cleanup, performance, warning, API, and retry candidates** (Items 15, 16, 56–58, 100–102, 129–131)
  - At audit time, `Development build` was guarded to upstream and became a one-second skipped workflow in this fork; `Create release` was likewise guarded but required a sync/compatibility decision because it recorded upstream store-flavor behavior. T0-1 CP2 later removed both after explicitly deferring store/AAB ownership. The standalone signing exercise remains useful for key custody/disaster diagnostics.
  - Gradle configuration executes `scripts/mosaic_version.py`; this is the leading explanation for external-Python configuration-cache invalidation, but causality and stable input alternatives still require measured proof.
  - Release lint debt (~252 errors/106 warnings) is not part of current required validation; introducing it as a blocking gate needs a baseline/migration. Other recurring Room/deprecation/optional-codec/Gradle warnings need separate ownership classification, not opportunistic fixes.
  - API calls, checkouts, manifest parsing, artifact transfers, and retries are **READY FOR MEASUREMENT**, not deletion. Mutations may retry only after idempotent state checks; rate limit, permission, not-found, conflict, and transient failures must remain distinguishable.

- [x] **A08 — AUDIT — Build a coherent naming, release-presentation, APK-alias, and documentation migration plan** (Items 17–20, 45–47, 103–107, 123–125)
  - Machine contracts (`develop`, `downstream-build-N`, `mosaic-v1.0.N`, version/digests/manifests) must remain stable while human workflow/job/step/release names become lifecycle-accurate.
  - Confirmed misleading wording remains in real Development signing summaries/artifact names. `Mosaic-release.apk` exists during signed transport, while published updater compatibility still requires `Wholphin-release.apk`.
  - Any asset migration must publish identical bytes under both names temporarily and atomically update updater preference/fallback tests; no duplicate build. Historical release title/body changes and metadata backfill require explicit approval and must never alter tags/assets/digests/latest semantics.
  - UTF-8/editorconfig/mojibake protection is a hard constraint. The formerly broken `PREPARE_PR` handoff anchor currently resolves to an existing heading; recheck links after documentation consolidation.

- [x] **A09 — AUDIT — Preserve and refine Upstream Sync outcomes, journal, conflicts, schedule, and concurrency** (Items 24–26, 62–64, 108–119, 134)
  - I06 result: observation remains read-only; repository-scoped App authority is minted only for normal, REVIEW or semantic-conflict candidate publication. Exact SHA-pair/policy identity, non-force publication, human-edit preservation and no automatic semantic resolution remain enforced.
  - Structured outcomes now distinguish no delta, all-excluded, ready/review/semantic candidates, existing/created normal or Draft PRs, expected block and infrastructure/publication failure. Clean candidate handoff closes its historical journal; REVIEW/conflict journals stay open, while no-delta and all-excluded observations remain machine evidence without Issues.
  - Safe Draft conflict workspaces use a downstream-only parent, downstream conflict bytes, non-conflicting context and deterministic JSON, with neither markers nor fabricated upstream ancestry. The real Series conflict remains a generic regression fixture, not a hard-coded resolution.
  - Schedule is fixed UTC 06:00/15:00/21:00, approximately 08:00/17:00/23:00 Bucharest in winter; DST drift and scheduler delay are explicit. Existing priority labels are used without permission broadening; missing labels require one-time external creation. Natural hosted acceptance is pending.

- [x] **A10 — AUDIT — Plan repository identity, metadata, review policy, and external GitHub organization** (Items 21, 22, 36, 37, 65–72, 78)
  - README/labels/issues/project/milestones/badges/backfill remain plans, not operational claims. Mosaic should identify as a personal experimental downstream, credit Wholphin, and encourage upstream/ecosystem reuse.
  - Deterministic checks remain required; advisory AI review must not become a security gate. Merge queue, CODEOWNERS, auto-merge, rulesets, security settings, labels, projects, milestones, and historical edits are **EXTERNAL / USER APPROVAL** work.
  - Keep taxonomy small and milestones capability/release-oriented rather than adding project-management bureaucracy.

- [x] **A11 — AUDIT — Define Development/Stable withdrawal and forward recovery** (Items 32–34, 120–122)
  - Final conclusion: Development always forward-fixes; rolling repoint/withdrawal does not help already-updated clients and has no demonstrated consumer. Immutable bad builds remain provenance records.
  - Stable recovery is urgent zero-input Hold when needed, then newer fixed Development → real-world validation → zero-input exact-byte Stable promotion. A catastrophic updater failure needs a newer APK with the same signer and package, installable without clearing data; ADB is not the sole documented path.
  - Rollback, repoint, unhold and generic remediation machinery are deliberately removed from the target architecture. Never mutate/re-version old APK bytes or delete history.

- [x] **D01 — DEFERRED — Preserve product/UI follow-ups outside Item 6** (Items 27–31, 140)
  - Separate future work: proactive non-nagging update notification, duplicate updater action ownership, update-state vocabulary, Settings redesign/channel-selector visuals, trustworthy telemetry research and UI-only download smoothing, and unrelated card/UI roadmap ideas.
  - These ideas are recorded but must not enter delivery/tooling consolidation PRs.

## Implementation checkpoints

- [x] **I01 — IMPLEMENT — Add canonical change classification and skip non-APK Development releases** (Items 4, 6, 9, 10, 41, 52, 87–93, 117–119, 128, 135, 136, 142)
  - Status: **COMPLETE / OFFLINE + LIVE VALIDATED.**
  - Depends on: A01–A05.
  - Completion criterion: one repository-owned, offline-tested classifier independently emits release relevance and validation risk; unknown/indirect inputs fail conservative; eligibility evaluates last published source through current main; proven non-APK ranges finish before Gradle/version/sign/publish and do not create a release, while a pending APK-relevant change cannot be skipped. Existing allocator and superseded-main rules remain unchanged.
  - Evidence: `scripts/mosaic_change_classification.py` is the single deterministic path classifier. It emits `apk-relevant | android-validation-only | tooling-only | docs-only | unknown` independently from `low | normal | high`, and only `apk-relevant` or `unknown` requires an APK release.
  - Evidence: Development eligibility authenticates the currently exposed rolling `develop` release against its immutable `downstream-build-N` annotated provenance, prerelease and exact two-asset digests. It then classifies `published source SHA..current trusted main SHA`; an absent/inconsistent publication, incomplete history, non-ancestor source or unclassified path fails to `unknown/high` and requires the release path.
  - Evidence: rename detection is disabled for the range diff so a moved/deleted APK input remains visible. Offline tests cover accumulated multi-commit APK relevance, independent risk, unknown inputs, production/build/proto/signing boundaries, non-ancestor history, mode-only changes where supported, source moves, authenticated/tampered publication state and workflow boundaries.
  - Evidence at I01 completion: `.github/workflows/mosaic-development-release.yml` gained a read-only `classify` job before setup, Gradle or version allocation. Proven non-APK ranges produced `skipped_non_apk`, gating the then-existing build/sign/publish chain. I02 subsequently moved the APK-relevant Release build to main CI without changing this accumulated-range skip contract.
  - Preserved: `mosaic_version.py`, exact-main/latest-successful-CI checks, superseded-main behavior, signing Environment, immutable provenance, recovery, Stable promotion and updater asset/version compatibility are unchanged.
  - Live evidence: workflow run `34379457375` at main `7881aa19850c46e53b43504c38a81a2e62dbb9a3` classified all 9 changed paths as `tooling-only`, risk `high`, outcome `skipped_non_apk`. Classify succeeded; build, sign, and publish were all skipped. The complete workflow took about 12 seconds and created no APK, version allocation, signature, immutable build, or rolling `develop` update.
  - Measured result: before I01 an equivalent tooling-only merge could enter roughly 11 minutes of Development build/sign/publish and publish a pointless app release; after I01 the proven non-APK range terminated after classification in about 12 seconds.

- [x] **I02 — IMPLEMENT — Consolidate authoritative main validation and Release artifact ownership** (Items 5, 7, 8, 43, 44, 52, 59, 73, 86, 94–96, 126–128, 133, 143)
  - Status: **COMPLETE / OFFLINE + LOCAL FULL + LIVE + DEVICE VALIDATED.** Depends on completed I01.
  - Completion criterion: the actual merged main SHA gains each required expensive proof once, one clear workflow produces the authenticated unsigned Release artifact for release-relevant state, and sign/publish/recovery consume exact immutable artifact IDs with no Gradle or weakened permissions. Debug/Release evidence changes are demonstrated, not assumed.
  - Implementation: exact protected-main push CI runs the unchanged Debug validation first, then only for `apk-relevant` or conservative `unknown` ranges runs the bounded Release assembly sequentially in the same workspace. It uploads the exact universal unsigned APK and provenance as `unsigned-mosaic-main-ci-1.0.N-<sha>-run-<ci-run>-attempt-<attempt>` with seven-day retention.
  - Authentication: Development independently retains I01 eligibility and exact-main/latest-successful-CI checks, then resolves exactly one unexpired artifact from that trusted CI run/attempt. It verifies immutable ID, exact name, digest, source/repository/run/job/timestamp ownership, provenance and APK bytes before signing. Caller-selected, missing, expired, ambiguous, wrong-SHA/run/name/digest artifacts fail closed.
  - Zero-Gradle boundary: the Development workflow has no setup composite, Gradle command, build job or rebuild fallback. Its only release-required path is authenticated cross-workflow download → unchanged Environment-bound sign/verify → publication-only job. Non-APK ranges still stop after I01 classification before main Release assembly or Development signing.
  - Recovery/compatibility: unsigned recovery accepts the new successful main-CI artifact while retaining legacy Development-build artifacts; signed recovery accepts current and legacy Development signed artifacts. Published manifests record the original CI build workflow/run/attempt. Stable continues exact-byte promotion and updater names/contracts are unchanged.
  - Offline evidence: all 65 `test_mosaic_*.py` tests pass (one Windows executable-bit fixture skipped). Coverage includes exact CI run/SHA/job/artifact binding; wrong/missing/expired/ambiguous artifact rejection; downloaded provenance/byte verification; zero-Gradle Development; non-APK gating; superseded-main protection; current and legacy unsigned/signed recovery; signing isolation; Stable promotion; and version contracts.
  - Live acceptance: PR #24 classified the visible Settings wording change `apk-relevant` / `normal` / `releaseRequired: true`. Protected-main CI run `34407365166`, attempt `1`, validated merged SHA `44e81da48ca50b70f1be364b3008294130d8721d`, then sequentially assembled version `1.0.11` and uploaded unsigned artifact ID `10126382836` (archive SHA-256 `2a3274203cc1b1815ed540b0a87c47a59379897e4f4fb4226f61126e70c35caa`; APK SHA-256 `76a5e078a43f75b28403131082882404dfbee286b9b50f58e826a6cea9e69db9`). Development run `34408806518`, attempt `1`, authenticated that exact producer/artifact/provenance, ran zero Gradle, signed and verified APK SHA-256 `98472b4e2537669b0894c6cf49ebc0c20229c633307f82b11da8e8e265d1c941`, and published byte-identical immutable `downstream-build-11` and rolling `develop` outputs with updater compatibility intact.
  - Device acceptance: Wholphin detected Development version `1.0.11` / code `11`; installing it displayed the accepted `Settings → More → Enhanced features` wording, proving the published APK contained the merged source change.
  - Measured live timing: protected-main Full `5m25s`; Release assembly `9m12s`; complete main CI `15m56s`; Development classify `11s`, sign `34s`, publish `17s`, complete workflow `1m13s`.
  - Follow-up checkpoint: **IMPLEMENTED / OFFLINE VALIDATED; HOSTED ACCEPTANCE PENDING.** Full PR CI retains its actual synthetic-merge SHA/tree in the existing Debug artifact identity. Protected-main authenticates the unique merged PR, exact parents, expected workflow/run/job/Full step, artifact ownership/digest and GitHub Git commit/tree; exact final `main^{tree}` equality reuses Debug Full evidence. Direct main, targeted/non-Android, failed/cancelled, missing/expired, stale/ambiguous, parent/tree mismatch and API uncertainty retain the existing main Full fallback. Current PR Release APK bytes remain non-reusable because `SOURCE_SHA`, `BUILD_TIME`, and first-parent-derived version identity are commit-context inputs; authoritative final-main Release assembly is unchanged.

- [ ] **I03 — IMPLEMENT — Optimize PR/local validation and human-facing progress** (Items 6, 11–14, 38–40, 50, 53–55, 59–61, 80, 97–99, 132, 137–139, 142, 143)
  - Status: **IMPLEMENTED / OFFLINE VALIDATED / HOSTED HIGH-RISK PATH LIVE VALIDATED.** Low-risk non-Android and normal targeted-Android hosted paths remain pending; do not manufacture PRs solely for acceptance.
  - Completion criterion: deterministic tiers run relevant checks with unknown paths escalating; local and GitHub output show truthful stages/timings while full logs remain available; no safety confirmation/tree identity is lost; VS Code tasks match real parameter contracts; no dangerous mutation task is exposed; checkpoint dry-run/offline and required live acceptance are documented.
  - Implementation evidence: `scripts/mosaic_validation_policy.py` reuses I01 classifications and independently selects `non-android`, `targeted-android`, or `full`. Normal Android paths map to auditable package test filters; direct test changes map by class; unmapped production paths use `com.github.damontecres.wholphin.*`; unknown, CI/workflow/action, build/package, release/signing/updater/identity and persistence inputs select Full. No-rename range discovery keeps moved/deleted inputs visible.
  - Local evidence: unchanged `-Level Fast|Standard|Full` commands now work without fake filters. Explicit filters remain supported. Fast runs the smallest selected path; Standard adds changed-scope pre-commit/offline tooling and Android compile evidence where applicable; Full uses all-files pre-commit, all offline tests and one combined full defaultDebug invocation. High/unknown scope escalates conservatively.
  - Hosted evidence: PR #25 run `34438367580` exercised the high-risk path and passed Full. Protected-main run `34438714060` then passed authoritative Full at SHA `7f68430a2eb47ced851269ab40519c2815e0c2e9`; Release assembly correctly skipped for the non-APK range. Development run `34439134293` classified all 17 paths from published baseline `44e81da48ca50b70f1be364b3008294130d8721d` through current main as `tooling-only` / `high`, emitted `skipped_non_apk`, and skipped build/sign/publish in about 16 seconds. The initial PR run `34437472660` failed only because the new untracked `.vscode/tasks.json` lacked its final newline; `pre-commit --all-files` in an earlier local Full could not see that then-untracked candidate. Full now retains all-files coverage and additionally checks reviewed untracked candidates.
  - UX evidence: shared PowerShell stage semantics use truthful `[RUN]`, `[PASS]`, `[FAIL]`, duration and absolute log paths. Complete per-stage logs live under ignored `.logs/validation/<run>/` and `.logs/prepare-pr/<run>/`; bounded failures preserve source locations. After the first external Full run exposed per-line `Add-Content` contention on the root compatibility log, validation changed to one live writer per stage and one end-of-run `validation.log` snapshot copy; focused Windows lock coverage and Fast validation pass. `prepare-pr` keeps snapshot/tree/refusal/publication safety and accepts classifier-selected Standard without explicit filters. `.vscode/tasks.json` is now source-controlled and exposes only Prepare PR plus Fast/Standard/Full validation.
  - Offline evidence: policy/tests cover low-risk non-Android, high-risk isolated tooling, normal APK, sensitive APK/release/build, unknown fallback, explicit/mapped/broad tests, VS Code tasks, stage success/failure/logs/error excerpts, PR summary wiring, unchanged main authority, and zero-Gradle Development. PowerShell parser and YAML parsing pass; repository-wide pre-commit and final handoff validation remain required.
  - Minimum live acceptance: (1) docs/isolated-tooling PR proves no Android setup/Gradle and accurate summary; (2) ordinary app PR proves mapped targeted compile/tests; (3) high-risk/unknown PR proves Full; (4) merged main proves Full plus conditional I02 Release artifact and unchanged zero-Gradle Development. Record elapsed times against the former 5–7 minute unconditional PR Full baseline.

- [ ] **I04 — IMPLEMENT — Remove proven dead work and consolidate measured tooling hot spots** (Items 15, 16, 56–58, 100–102, 126–131, 142)
  - Status: **IMPLEMENTED / OFFLINE VALIDATED / HOSTED HIGH-RISK PATH LIVE VALIDATED.** Merged through PR #26 at `3907726ce38a03936e5853e5e8d36fff6d4486e9`. Low/normal I03 natural hosted acceptance remained a follow-up; I05 and I06 were implemented in later checkpoints.
  - Latest live acceptance (user-reported): Development eligibility emitted `skipped_non_apk`, release relevance `tooling-only`, validation risk `high`, and `24` changed paths. Release build/sign/publish correctly skipped after merge; protected-main validation remains authoritative. No synthetic publication or workflow dispatch is needed to repeat this evidence.
  - Hosted portability correction: both stage-output integration fixtures now launch the current PowerShell host's absolute executable path instead of hard-coded `powershell.exe`. Their empty-PATH regression setup retains every blank-line and single-writer assertion. Windows had masked the nested-command defect by providing `powershell.exe`; hosted Linux provided `pwsh` only. Local focused tests passed; the complete 125-test offline suite passed with one existing Windows executable-bit fixture skip (124 passes).
  - Completion criterion: every deletion has caller/operator evidence, one canonical helper owns each deterministic contract, API/checkouts/artifact transfers are reduced without stale security state, transient retries are bounded/idempotent, and retained upstream/recovery/exercise paths have an explicit purpose.
  - Workflow decisions at I04: the [full automation audit](ITEM_6_UPSTREAM_AUTOMATION_AUDIT.md) classified `main.yml` as **DOWNSTREAM-OWNED**, `release.yml` and the upstream `pr.yml` → downstream `ci.yml` area as **REVIEW**, and shared setup as **FOLLOW**. T0-1 CP2 later removed both inherited publishers and changed `release.yml` to a downstream-owned approved absence after explicitly deferring Appstore/Fire TV AAB distribution. Signing exercise remains **DIAGNOSTIC**.
  - Canonical owners: `mosaic_version.py` owns version identity; `mosaic_change_classification.py` owns release relevance/risk; `mosaic_validation_policy.py` owns validation selection; `verify_mosaic_apk.py` owns signed APK verification. APK ZIP/provenance transport remains in `mosaic_signing_exercise.py`. Security-sensitive jobs/Environments remain separate even when deterministic helpers are shared.
  - Measured overhead: the audit counted 15 checkouts (13 full-depth), 9 artifact uploads and 7 downloads. Most are deliberate trust/workspace boundaries. The signing-exercise sign-only checkout was the proven exception: its check now authenticates exact clean HEAD, `HEAD^{tree}`, commit time, fixed epoch/baseline, run/attempt and APK digest from a shallow checkout without re-running history-based allocation; build still retains full history.
  - Implemented hot spots: Full now runs reviewed untracked candidate paths through pre-commit after repository-wide `--all-files`; `.logs/` is ignored once without hiding tracked `.vscode/tasks.json`; each stage keeps one UTF-8 `StreamWriter` open while root `validation.log` remains a one-time post-run compatibility copy; immutable same-process release-list snapshots are reused only before mutation; long JWT-style GitHub App installation tokens are covered as opaque environment-only values and never logged; and signing-exercise sign-only checkout uses `fetch-depth: 1`.
  - Measured logger result: an identical local 5,000-line capture fell from `7.504s` with per-line `Add-Content` to `1.455s` with one stage writer (about 81% faster), while focused contention/output tests preserved complete logs and reported no `Stream was not readable` or sharing violation.
  - Configuration-cache finding: Gradle configuration invokes `scripts/mosaic_version.py` through `providers.exec`; source SHA/tree/version/build-time/dirty output legitimately changes across source identities. This is expected identity tracking, not an I04 defect, and the allocator remains unchanged. The 119-test offline suite previously measured about 176.5 seconds internally versus about 237 seconds as a logged stage; `test_hosted_upstream.py` (~120 seconds) and `test_mosaic_version.py` (~17 seconds) dominate substantive test time.
  - Warning ownership: Room index and diagnostic/update API warnings are inherited application debt; Gradle/configuration-resolution warnings belong to future dependency/build migration; Media3 codec/libMPV messages are expected environment diagnostics; Release lint debt remains a separate broad baseline. None is opportunistically changed here.
  - At I04, deletion of `main.yml` was deferred alongside lifecycle/artifact presentation, broad retries, configuration-derived version identity, and permission/Environment consolidation. T0-1 CP2 later completed the separately reviewed inherited-workflow deletion; the other boundaries remain governed by their own checkpoints.

- [ ] **I05 — IMPLEMENT — Apply coherent lifecycle naming and compatible release presentation** (Items 17–20, 42, 45–47, 57, 77, 103–107, 123–125, 142, 143)
  - Status: **IMPLEMENTED / OFFLINE VALIDATED; PR → MAIN → DEVELOPMENT LIFECYCLE LABELS LIVE VALIDATED; REMAINING NATURAL HOSTED ACCEPTANCE PENDING.** Asset/API-title migration and historical writes remain deferred. [I05 ledger](ITEM_6_I05_PRESENTATION.md) contains the complete pre-edit name/consumer inventory, artifact table, decisions and backfill plan.
  - Implemented: coherent workflow display names and trigger-time run identities; safe job/step labels; Published/Promoted/Recovered/Skipped/failure summaries; diagnostic-only wording; distinct future rolling/archive/Stable bodies with source/install guidance; immutable-SHA eligibility compare links; presentation-only Sync headings with unchanged machine outcomes/exit codes. Guard-rejected Development triggers get a read-only explanation, without granting release eligibility.
  - Human-first run-name follow-up: PR CI uses `PR #N · <head branch>`; protected-main pushes deliberately use the documented blank fallback to preserve GitHub's native merge/push title; Development reuses the triggering CI `display_title` with CI-run-number then SHA fallbacks; manual Development keeps the approved SHA; Stable uses `Stable · from downstream-build-N`. No API, commit-message parsing or machine identity depends on these labels. PR #30 live-validated the complete presentation chain as `PR #30 · chore/item-6-lifecycle-labels` → native `Merge pull request #30 from constbogdan/chore/item-6-lifecycle-labels` → `Development · Merge pull request #30 from constbogdan/chore/item-6-lifecycle-labels`.
  - Preserved: all workflow paths, internal IDs/outputs/dependencies, `CI`, `Full validation`, production `sign` API names, signing/Environment/Stable authority, artifact prefixes/IDs, tags, version allocator, manifest and updater identity. Installed UpdateChecker parses API `name`, so `v1.0.N` remains; branded channel titles are body headings. Existing APK aliases and exact two-asset inventory remain unchanged; their coordinated migration is planned, not implemented.
  - Mapping: main Release's existing R8 mapping becomes a separate seven-day Actions diagnostic, compression 6, bound to exact source/version/build/run and mapping SHA-256. No rebuild, signer/updater input or public release asset. Missing/empty mapping fails visibly; hosted retention acceptance awaits the next actual Release build.
  - Offline evidence: full suite ran 135 tests, 134 passed and one existing Windows executable-bit fixture skipped. New coverage exercises updater compatibility, release bodies, summary outcomes, guard explanation, historical retry immutability and mapping identity. No releases were manufactured or historical metadata edited.
  - Historical natural-acceptance status: the inherited upstream `Development build` appeared as a separate one-second skipped row; T0-1 CP2 later removed it as an explicit downstream-owned absence. Other I05 acceptance and the Stable producer migration are recorded in their later checkpoints.
  - Completion criterion: a reviewed before/after map is applied consistently to human-facing workflows/jobs/steps/artifacts/docs; stable machine contracts remain compatible; signing-exercise wording disappears from production paths; any APK alias migration proves identical bytes and old-updater fallback; historical changes occur only with approval.

- [x] **I06 — IMPLEMENT — Native upstream synchronization, ownership, and semantic resolution** (Items 23–26, 62–64, 108–119, 128–131, 134, 142, 143)
  - Status: **COMPLETE / LIVE VALIDATED.** Native Git ancestry and the candidate PR are the canonical lifecycle. No custom journal Issue, Risk/Debt/Age/Escalation state, Issue labels, or merged-episode finalizer remains.
  - Live evidence: run `34701161886` created clean native FOLLOW PR #55 for three upstream commits through `4a118b6d…`; candidate `ffc02344…`, PR-tested merge `15d4d939…`, and final main `1c3247af…` shared tree `dffa12e7…`. Required PR Full run `34701197155` passed; protected-main run `34702111274` authenticated artifact `10300078947`, reused exact-tree evidence, and published Development v1.0.37. Run `34702881758` then returned quiet `no_delta`.
  - Preserved safety: complete-range ownership classification; fail-closed unknowns; exact refs, parents, tree and provenance; deterministic branch/PR reuse; valid historical orphan rewrite anchors; refusal for current-pair malformed or ambiguous candidates; no force push, auto-merge, auto-resolution, or reopening; Draft gate for REVIEW/conflict; required CI; human merge/reject authority; scoped App token; quiet human surfaces and rich machine/Actions provenance.
  - Conflict path: the local resolver authenticates the PR and recorded upstream/downstream identities, starts/continues the exact native merge, confines semantic choices to the human/Codex resolution, requires meaningful focused JVM filters, and permits publication only as a reviewed two-parent merge with the expected parents/tree and no markers. This path remains offline validated pending a natural live textual conflict; no fabricated hosted state is required for I06 completion.
  - Operational model: fixed UTC schedule `0 6,15,21 * * *` plus manual dispatch; observe is read-only; publish mutates only the deterministic branch/PR when needed. `no_delta` and all-excluded outcomes publish no candidate state. PR merge/close and accepted ancestry terminate the episode natively.
  - Removal evidence: the redundant finalizer run `34702111386` failed after successful integration and Issue #54 had already closed, proving it guarded no distinct property. CP5 removed Issue/journal creation and parsing, priority arithmetic/labels, finalizer trigger/job/CLI, Issue permissions, and Issue-based resolver fallback while preserving authenticated PR evidence and retained JSON artifacts.
  - Validation: focused hosted-sync and resolver suites pass (54 and 34 tests). Coverage retains no-delta, clean/REVIEW/conflict candidates, ownership, exact topology, rewrite/orphan/ambiguity/drift refusals, quiet surfaces, scoped credentials, required-CI handoff, and PR-evidence fallback after artifact expiry.
  - Completion criterion: **SATISFIED.** Outcomes are structured; retries are deterministic; native PR/Git state owns lifecycle; schedule intent is documented; clean and blocked offline cases pass; no semantic conflict is automatically resolved or published with markers/unresolved index.

- [x] **I07 — IMPLEMENT — Hold the currently advertised Stable while forward-fixing** (Items 8, 32–35, 43, 76, 77, 120–122, 124, 143)
  - Status: **COMPLETE / LIVE VALIDATED.** The I02 artifact-ownership dependency is satisfied.
  - Evidence: [the durable I07 design](I07_PUBLISHED_RELEASE_REMEDIATION.md) records why Development remediation and rollback/repoint machinery have no consumer. Hold run `34690727709` authenticated and held v1.0.5 while preserving its tag/assets and leaving `/latest` empty. Native failed-job rerun then retained successful validation/Build after the renamed `release-sign` Environment initially lacked its migrated secrets; configured signing produced Development v1.0.34 / `downstream-build-34`. Stable Promotion run `34694610864` exercised `release-promote` and promoted the exact Development APK digest `1d84dfb922765b28f75e422e25b7fbdc5123beb86fc0148d5e324f5547514e5d`; v1.0.34 is latest and held v1.0.5 remains preserved. Permanent Stable operation is zero-input Prepare authentication followed by Environment-authorized Release with post-approval protected-main/candidate reauthentication. `release-sign`, `release-promote`, and `release-hold` record human authority independently from machine authentication of what may be signed, promoted, or held.
  - Completion criterion: a live authorized run proves exact Stable authentication, metadata-only hold, tag/APK/manifest preservation, `/latest` fallback or absence, repeat-run cascade refusal, and recovery through normal higher-version Development plus exact-byte Stable Promotion. Development remains forward-fix-only; signer/version monotonicity and immutable history remain unchanged.

### Post-Item-6 transition

I06 and I07 are **COMPLETE / LIVE VALIDATED**. The next top-level program is
[Baseline T0](Wholphin_ROADMAP.md#current-engineering-program-baseline-t0): T0-1 Cleanup & Operator Experience, T0-2 Full Engineering / Process
Audit, then T0-3 Documentation, Wiki & Roadmap. Baseline T0 is not an application release and must
not be declared until its audit has no unresolved/unaccepted blocker and the current architecture is
navigable from `docs/README.md`. T0-1 CP1 is complete: the authoritative
[operator UX inventory and implementation ledger](T0_1_OPERATOR_UX_INVENTORY.md) defines the
finite CP2–CP8 work. Next is CP2 Remove obsolete surfaces.

- [ ] **D02 — DOCUMENT — Consolidate operational documentation after each checkpoint** (Items 45–47, 51, 62, 70–72, 75, 119, 123–125)
  - Status: **ONGOING.**
  - Completion criterion: operational docs describe only current behavior; handoff retains expensive historical lessons/corrections; links/UTF-8 checks pass; each checkpoint reports old/new graph, measured savings, evidence retained, risks, compatibility, and next work.

- [ ] **E01 — EXTERNAL / USER APPROVAL — Apply GitHub settings/metadata or mutate historical/public state** (Items 36, 37, 40, 65–69, 78, 93, 106, 115, 120, 122, 138, 139)
  - Status: **BLOCKED by design until separately authorized.**
  - Completion criterion: a reviewed proposal identifies exact setting/object mutations, permissions, rollback, cost/eligibility, and security impact; the user explicitly authorizes execution. Repository code may prepare proposals/tests but cannot imply these controls are live.

- [ ] **V01 — VALIDATE — Keep every checkpoint independently safe and produce the final Item 6 report** (Items 48, 74, 75, 142, 143)
  - Status: **READY as the governing validation gate.**
  - Completion criterion: every PR leaves main buildable and Development/Stable/recovery/updater contracts usable; infrastructure changes receive strong old/new offline coverage and the minimum approved live acceptance; quick wins and caution items remain explicit; final before/after matrix and measured outcomes satisfy Item 74.

## I02 evidence and measurement pass (2026-09-09)

**Evidence status:** **I02 COMPLETE / ACCEPTED.** The measured table remains the pre-I02 baseline; the final local, hosted, publication, updater, and device evidence is recorded in the I02 checklist entry above.

### Measured execution matrix

| Path / source | Exact command and variant | Measured work | Duration / cache | SHA or tree and unique evidence |
| --- | --- | --- | --- | --- |
| PR CI Full, run `34377847639` | `./gradlew :app:compileDefaultDebugKotlin :app:testDefaultDebugUnitTest :app:assembleDefaultDebug --no-daemon` (`defaultDebug`) | One invocation; 89 actionable: 63 executed, 26 from cache. Debug OpenAPI/proto/KSP/Kotlin, tests, resources, packaging and APK assembly. | Gradle 5m34s; job 7m08s; configuration cache calculated/stored. | Synthetic merge `299582995c44ed997d7d416ef4054f6fc893a64d`, tree `ed413be3339e3a705c36a03bb623b5e73cc5044d`. Proves the PR merge context and supplies the seven-day universal Debug artifact. |
| Main CI Full, APK-relevant sample `34357387164` | Same single `defaultDebug` invocation | 89 actionable: 63 executed, 26 from cache. | Gradle 5m49s; job 7m28s; configuration cache stored. | Exact main `5818b605fe64fae97bdd20feed7b1df60600d08a`, tree `705576739a6270d52feaee446a10930b48e52bd5`. Proves the actual merged main source later used by Development. |
| Main CI Full, I01 run `34378690101` | Same single `defaultDebug` invocation | 89 actionable: 63 executed, 26 from cache. | Gradle 5m35s; job 7m22s; configuration cache stored. | Exact main `7881aa19850c46e53b43504c38a81a2e62dbb9a3`, tree `ed413be3339e3a705c36a03bb623b5e73cc5044d`. Confirms main still receives authoritative Debug validation before I01 classifies Development. |
| Development Release, run `34358202702` | `./gradlew :app:assembleDefaultRelease -PmosaicPublication=true --no-daemon --no-parallel --max-workers=1` (`defaultRelease`) | 105 actionable: 93 executed, 12 from cache. Release proto/KSP/Kotlin/resources/manifests, R8, vital lint, optimized resources and unsigned APK assembly. | Gradle 9m01s; build 9m55s; sign 37s; publish 18s; workflow 11m02s; configuration cache stored. | Exact main `5818b605fe64fae97bdd20feed7b1df60600d08a`, the same source as the APK-relevant main-CI sample. Produces the authoritative unsigned Release artifact. |
| Development Release, run `34365894312` | Same bounded `defaultRelease` invocation | 105 actionable: 93 executed, 12 from cache. | Gradle 7m10s; build 8m18s; sign 41s; publish 25s; workflow 9m36s; configuration cache stored. | Exact main `a1ffce53`; tree `e21c1e8...`. Confirms the Release cost range and that sign/publish already perform zero Gradle work. |
| Signing exercise, run `34323962085` | Sequential Debug Full invocation, then bounded `:app:assembleDefaultRelease -PmosaicPublication=true` | Debug: 89 actionable, 55 executed, 34 cache. Release: 105 actionable, 89 executed, 13 cache, 3 up-to-date. Common OpenAPI/proto extraction reused in-workspace; variant-specific KSP/Kotlin both executed. | Debug 6m03s; Release 9m21s; build job 16m43s; sign 34s. Separate configuration-cache entries stored. | Exact main `055dde77...`, tree `36aa5e90...`. Demonstrates useful same-workspace reuse, but also confirms Debug and Release compilers/codegen are distinct evidence. |
| Local Full at current main | `compileDefaultDebugKotlin`, `testDefaultDebugUnitTest`, then `assembleDefaultDebug` as three invocations | 31, 69 and 73 actionable tasks respectively; all up-to-date in this warm workspace. | 3.019s, 3.762s and 3.292s; configuration cache reused; complete local run 39.43s including 28.96s pre-commit. | Main `7881aa19850c46e53b43504c38a81a2e62dbb9a3`. Proves local working-tree policy; warm local timings do not predict clean hosted execution. |

### Confirmed overlap and non-redundant evidence

- In hosted CI, `compileDefaultDebugKotlin` is an explicit requested task and a dependency of later tasks, but Gradle executes it once within the single invocation. Repeated appearances in the graph are not repeated compilation.
- PR and main CI intentionally repeat the Debug graph against different commit identities: the synthetic PR merge versus the actual merged main SHA. In the measured I01 case their trees matched, but build metadata includes source SHA/time/version inputs, so the PR artifact cannot be relabeled as the authoritative main Release artifact.
- Debug and Release share inputs and some generated/extracted work, but variant-specific proto/KSP/Kotlin/resource/package work is real. Release additionally performs R8, vital lint and optimized Release packaging. Debug JVM tests exist only on `defaultDebug`; there is no equivalent required Release unit-test suite.
- Same-workspace sequential execution can reuse common OpenAPI/proto outputs. It cannot make Debug KSP/Kotlin proof stand in for Release KSP/Kotlin or packaging proof.
- A previously tested combined concurrent Debug+Release Gradle invocation exhausted hosted memory while Debug and Release Kotlin compilers overlapped. The safe initial I02 shape is sequential bounded invocations in one job/workspace, not one enlarged invocation.

### Implemented authoritative owner and I02 shape

1. Keep PR CI validating the synthetic merge with the existing `defaultDebug` graph and PR Debug artifact.
2. Make main CI the authoritative owner of the merged-main unsigned `defaultRelease` APK. Run the existing Debug validation first, then—only for `apk-relevant` or conservative `unknown` classification—run the bounded Release assembly sequentially in the same job/workspace.
3. Add a non-privileged main-event classification use of the same I01 rules before Release work. Do not weaken the existing Development eligibility check, which must still authenticate exact main, latest successful CI and the last published source-to-main range.
4. Upload the exact universal unsigned Release APK and provenance bound to the main CI run/attempt, source SHA/tree, version, digest and immutable numeric artifact ID, retaining the current seven-day checkpoint model.
5. Reduce Development to classify/trust, locate and download that exact main-CI artifact, authenticate its original producer, then use the unchanged isolated sign → verify → publish chain. Development should run zero Gradle.
6. Preserve unsigned/signed recovery, exact-byte Stable promotion, asset naming and updater behavior. Missing, expired, ambiguous or unauthenticated main artifacts must fail closed rather than rebuild silently in a privileged stage.

The provenance checker now supports the narrow cross-workflow boundary above: it validates the original main-CI workflow/run/attempt, successful exact-SHA `Full validation` job, immutable artifact ID, exact source/version/run-bound artifact name, digest, creation window and downloaded payload. It does not accept an arbitrary caller-supplied producer or artifact name.

### Expected savings and remaining risks

- I02 does not eliminate the required Release compilation. It moves that work from the privileged Development workflow to authoritative main CI and reuses common outputs in one checkout/workspace.
- The visible Development path fell from 9m36s–11m02s to 1m13s total in live acceptance, including 34s signing and 17s publication. Confirmed savings include removal of the second checkout/setup/build ownership and same-workspace reuse; the necessary Release compilation now occurs in main CI.
- Main CI is longer by design: live acceptance measured protected-main Full at 5m25s, sequential Release assembly at 9m12s, and the complete CI job at 15m56s, below the 30-minute timeout.
- Do not remove Debug assembly or merge Debug/Release task invocations during I02. Any broader validation-tier reduction belongs to I03 and requires its own evidence.
- The former open questions are resolved as follows: source/version/run/attempt-bound `mosaic-main-ci` artifact naming, seven-day retention, exact immutable-ID selection, authenticated CI producer/job/timestamps/digest, fail-closed missing/expired/ambiguous handling, and live timing/end-to-end acceptance. Signing permissions, Environment isolation, recovery, Stable and updater compatibility remain fixed constraints, not optimization targets.

## Initial audit report (A–O)

### A. Executive summary

1. The delivery chain is live and security boundaries are sound; optimize around it rather than replacing it.
2. The largest confirmed waste is unconditional Android CI and Development Release for non-APK changes.
3. PR and main both run Full defaultDebug; main then triggers a separate defaultRelease compilation. Some repetition proves different trees/variants, so task-level consolidation needs measurement.
4. Exact unsigned/signed artifact recovery and exact-byte Stable promotion already prove zero-build downstream stages are practical.
5. Release relevance and validation risk need separate deterministic, conservative classifiers.
6. Main CI owns authoritative merged-state Debug evidence and conditional unsigned Release artifact production through completed, live-accepted I02.
7. T0-1 CP2 removed upstream-only `Development build` / `Create release` after the explicit compatibility decision; both paths are downstream-owned absences and store/AAB distribution is deferred.
8. `prepare-pr` is autonomous v2; historical Guided requirements are superseded. Its safety checks remain valuable, but output is not yet concise.
9. I03 makes no-filter Fast/Standard VS Code tasks valid through deterministic classification while retaining explicit real filters.
10. Security settings, labels, historical releases, merge queue, and live workflow operations remain explicit external decisions.

### B. Current execution graph

```text
working tree -> classifier-selected validate-local/prepare-pr -> exact local commit
             -> PR CI (synthetic merge, relevant checks; Full + Debug artifact only when required)
             -> protected main
             -> classify last published Development source..current main
             -> main CI (actual merged SHA, full defaultDebug)
                -> proven non-APK: no Release assembly; Development records skipped_non_apk
                -> APK-relevant/unknown: sequential defaultRelease assembly
                   -> authenticated unsigned main-CI artifact
                   -> Development exact-artifact download -> Environment-bound sign
                   -> verify -> signed artifact
                   -> immutable downstream-build-N + rolling develop

downstream-build-N -> manual Stable verify -> exact-byte mosaic-v1.0.N
unsigned/signed checkpoint -> manual resume -> sign/reverify -> publish
scheduled/manual sync -> read-only observe -> ready PR or durable blocked record
```

### C. Workflow inventory

See A02. Active trust paths are `CI`, Development release/resume, Stable promotion, and Upstream Sync. Signing exercise is diagnostic. Inherited publishers are repository-guarded, not currently downstream publication paths.

### D. Measured timing/overlap matrix

See [the I02 evidence pass](#i02-evidence-and-measurement-pass-2026-09-09). The table measures the pre-I02 PR/main Debug, two Development Release runs, and the sequential signing exercise. Final live acceptance measured the new main-CI and artifact-only Development graph in the completed I02 entry.

### E. Gradle/task overlap

Local Standard starts up to six Gradle invocations; local Full starts three. Hosted CI runs one `defaultDebug` invocation, and `compileDefaultDebugKotlin` executes once even though later requested tasks depend on it. For release-relevant main pushes, I02 then runs a separate bounded `defaultRelease` invocation in the same workspace. Common OpenAPI/proto outputs can be reused while Debug and Release KSP/Kotlin/resources/packaging remain variant-specific. A combined concurrent Debug+Release invocation previously exhausted hosted memory, so the implemented graph remains sequential.

### F. Artifact/provenance graph

See A04. The strongest reusable seams are immutable numeric Actions artifact IDs, provenance manifests, APK/source/tree digests, immutable Development releases, and exact-byte Stable promotion.

### G. Release-relevance classifier implementation

I01 uses repository-owned rules with outputs `apk-relevant`, `android-validation-only`, `tooling-only`, `docs-only`, `unknown`. It evaluates the complete publication backlog from the authenticated last successful Development source to current main. Production source/resources/manifests/dependencies/build/codegen are APK-relevant; tests/automation are validation-relevant; docs/metadata are normally non-Android; unknown or indirect release/security inputs escalate. PR/main validation-tier consumption remains I03.

### H. Risk classifier implementation

I01 emits separate `low`, `normal`, `high` output. Signing, release, updater, identity, packaging, persistence migration, security automation, and their imported helpers are high risk. Ordinary app work is normal; proven docs/metadata can be low. Consuming this risk in PR/local validation remains I03; Stable remains explicit human promotion.

### I. Dead/redundant candidates

- Resolved after Item 6: T0-1 CP2 removed downstream-visible `Development build` and inherited
  `Create release`; historical AAB knowledge remains in the automation audit.
- Retain/investigate separately: standalone signing diagnostic, repeated manifest/API helpers,
  exact-byte verification, upstream observation, and legacy APK alias.

### J. Naming/UX proposal

Use lifecycle stages `Classify`, `Validate`, `Build`, `Sign`, `Verify`, and `Publish`. Current delivery lives in `CI`; Stable Promotion and Upstream Synchronization remain separate. The former Development Release/Recovery Actions are historical evidence only; retain machine IDs where artifact/updater compatibility still depends on them.

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

- Proven non-APK Development ranges: I01 now reduces build/sign/publish from roughly 11 minutes to a measured 12-second classification-only run. PR/main validation optimization remains I03.
- APK-relevant merged state: retain one authoritative main Debug graph and one Release compilation; I02 moves Release ownership to main CI and removes Gradle from Development rather than pretending the variants are duplicates.
- Signing/publishing/Stable/recovery: retain zero Gradle work.
- Live I02 Development latency fell from the 9m36s–11m02s baseline to 1m13s total: classify 11s, sign 34s and publish 17s, with zero Gradle. Release compilation moved into the sequential protected-main CI workspace rather than disappearing.

### O. Risks and open questions

- I01's required non-APK live acceptance is complete. A later APK-relevant accumulated range must continue to exercise the unchanged conservative branch, but that is ongoing regression acceptance rather than an I01 completion blocker.
- I02 authenticates the original main-CI run/attempt and immutable artifact ID across workflows rather than trusting caller inputs; offline negative coverage and hosted live acceptance are green.
- Main CI and same-workspace execution were measured live. Keep sequential bounded Debug then Release invocations because concurrent compilers previously exceeded hosted memory.
- Missing/expired main artifacts must fail closed without rebuilding in the privileged sign/publish path. Debug assembly reduction, PR/local tiering and broader task-graph changes remain I03.
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
