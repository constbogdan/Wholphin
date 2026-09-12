# Release Pipeline Simplification Plan

This document is the authoritative migration tracker for simplifying Mosaic's release pipeline. It records durable decisions and acceptance evidence without treating earlier architecture-review output as a fixed implementation checklist.

## Standing invariants

- Protected `main` remains release-authoritative.
- Under the current version semantics, Release assembly remains in the final protected-main commit context.
- Build code receives neither Android signing credentials nor release-mutation authority.
- Signing credentials exist only in the protected signing Environment and only in an isolated signing job that performs no Gradle/build work.
- Publication authority remains separate from signing credentials and consumes an exact verified signed artifact.
- Permanent signer, package, version, and payload verification remains mandatory.
- `versionCode` remains monotonic; release names and assets remain compatible with the installed updater.
- Immutable `downstream-build-N` Development identity and rolling `develop` remain operational contracts for now.
- Stable remains exact-byte promotion of an authenticated Development APK.
- Missing, ambiguous, stale, mismatched, or otherwise uncertain evidence fails closed.

## Rejected requirements

- Protected-main Debug Full does not need to rerun merely because a PR merged when authenticated evidence proves that the required PR Full tested the exact final Git tree.
- Signing isolation requires an isolated protected job, not inherently a separate workflow.
- Routine recovery does not inherently require a dedicated recovery workflow.
- GitHub-native lifecycle and provenance facts should not be copied into permanent custom state without a demonstrated consumer.

## Checkpoint 1 — exact-tree PR Full reuse

**Status: COMPLETE / OFFLINE + LOCAL FULL + LIVE VALIDATED.**

PR #42's required Full validation tested its synthetic merge checkout. On the resulting protected-main push, CI authenticated the corresponding PR, run, required Full job/step, retained evidence artifact, tested commit parents, and tested tree. The tested tree and final protected-main tree were identical:

`0f05f52063fa097892365b3b6d54123c8690243f`

Protected-main CI consequently reported `Debug Full validation: reused from PR`. Release assembly was correctly not required because the complete change was tooling-only.

This is sound because reuse is authorized by Git's canonical tree identity only after the evidence producer and exact tested context are authenticated. A Git tree identifies the complete tracked content, modes, and object identities. Equality therefore proves the final protected-main content is exactly the content that passed required Full validation; the optimization does not weaken the merge or release gate.

Fallback remains mandatory. Missing, mismatched, targeted-only, ambiguous, expired/stale, cancelled/failed, parent-inconsistent, API-unavailable, or otherwise untrusted evidence causes protected-main Full to execute normally.

Timing is operational evidence, not a correctness invariant: preceding protected-main runs took approximately `7m04s` and `6m20s`; the PR #42 protected-main run completed in approximately `1m58s`.

No Release assembly, signing, publication, Stable, recovery, versioning, or updater behavior changed in this checkpoint.

## Checkpoint 2 — consolidate Development delivery into protected-main CI

**Status: COMPLETE / OFFLINE + LOCAL FULL + LIVE VALIDATED.**

Target boundary:

``` text
protected-main workflow
  -> validation reuse/fallback
  -> Release build job
       no signing secrets
       no release mutation authority
  -> sign job
       protected signing Environment
       signing credentials available here only
       no Gradle/build execution
       no release publication authority
  -> publish job
       contents/release mutation authority
       no signing credentials
       consumes exact signed artifact
```

The protected-main `CI` workflow now implements this graph. The goal is to remove unnecessary cross-workflow artifact discovery and producer/run/attempt reconstruction from normal delivery while preserving the security properties enforced by build/sign/publish separation. Routine recovery state has not been removed.

### Implemented movement

- `release-build` depends on successful `full-validation`, classifies the complete unpublished range, and conditionally performs the same final-main Release assembly, unsigned provenance preparation, artifact upload, and mapping retention. It has read-only permissions, no Environment, and no secrets.
- `sign-development` consumes the exact same-run unsigned artifact ID, validates its source/tree/version/run/attempt/name and bytes, signs through the unchanged local action inside `release-sign`, and permanently verifies package/version/signer/payload before uploading the exact signed result. It has no Gradle command or release-write permission.
- `publish-development` consumes the exact signed artifact ID, reconstructs and verifies the publication manifest before credential use, rechecks that the source remains protected-main tip, and uses the existing idempotent publisher. It alone has `contents: write` and has no signing Environment or credentials.
- At Checkpoint 2 implementation time, the old `mosaic-development-release.yml` became an explicit exact-SHA manual fallback and `mosaic-development-resume.yml` remained unchanged. Both were retired later after native rerun acceptance and the consumer audit recorded below.

### Native same-run dependencies

- Pass the unsigned APK and its minimal integrity metadata through an immutable same-run artifact from build to sign.
- Pass the verified signed APK and publication manifest through an immutable same-run artifact from sign to publish.
- Use `needs` job results and exact artifact names/digests within the same run instead of discovering a separate workflow run and rebuilding its run/attempt identity.
- Do not remove a provenance field merely because it appears redundant; first prove it has no recovery, Stable, updater, audit, or external consumer.

Normal delivery no longer discovers an external producer workflow/run/attempt or authenticates a `workflow_run` event. Exact same-run artifact IDs and `needs` outputs replace that reconstruction. Build run/attempt remains in APK provenance because recovery, Stable/audit records, and retry identity still consume it. Source SHA/tree, version, artifact digest, signer/package/version/payload identity, and immutable publication identity continue protecting distinct properties.

### Failure, retry, and recovery behavior

- GitHub documents that **Re-run failed jobs** reruns failed jobs and their dependent jobs while retaining the original event's `GITHUB_SHA` and `GITHUB_REF`. Successful prerequisite jobs are not part of that rerun. The workflow run ID remains the run identity and `github.run_attempt` advances.
- GitHub's public contract does not fully describe cross-attempt `needs` output and artifact behavior, but Case A live acceptance now proves the behavior on which the current Sign path depends: **Re-run failed jobs** retained the successful Build, its outputs, and its exact attempt-1 unsigned artifact while rerunning Sign and dependent Publish only. Expiry or deletion remains terminal for artifact reuse.
- The Python verifier correctly permits a build attempt less than or equal to the current attempt only within the same run. That check is compatible with a legitimate rerun; the unproven boundary is recovering the exact prior-attempt ID and metadata before verification.
- A rerun preserves each job's declared permissions. Case A proved that the signing job references the protected signing Environment again before it runs or receives Environment secrets.
- Publication must retain current idempotency: never create conflicting `downstream-build-N` bytes, and update rolling `develop` only from the authenticated immutable result.
- A full-workflow rerun rebuilds and re-signs rather than resuming. Immutable publication conflict checks refuse different bytes under an already-reserved identity, so it is not the preferred recovery operation and may require explicit repair or a forward fix.
- The explicit manual fallback and dedicated recovery workflow remain in the repository pending a deliberate removal change, but this audit found no distinct current recovery responsibility that justifies either surface.

#### Native rerun recovery analysis

| Failure point | Correct recovery | Reason |
| --- | --- | --- |
| Build fails before unsigned upload | Native rerun sufficient | Failed build and its dependents rerun; there is no successful artifact to preserve. |
| Build succeeds; Sign fails before signed upload | Native rerun sufficient — **LIVE VALIDATED** | Run `34653375353` proved that **Re-run failed jobs** retained the successful Build and its exact attempt-1 unsigned artifact/outputs, reran the protected Sign job, then ran dependent Publish. |
| Sign uploads signed artifact; a later Sign step fails | Native rerun sufficient | No publication has occurred. Rerunning Sign may produce a fresh authenticated signed artifact, after which Publish consumes that exact output; preserving the earlier orphaned signed artifact adds no required property. |
| Build and Sign succeed; Publish fails before mutation | Native rerun sufficient — **LIVE VALIDATED** | Run `34673534555` proved that **Re-run failed jobs** retained Build and Sign plus the exact attempt-1 signed artifact, then reran Publish alone. |
| Immutable publication succeeds; rolling update fails | Native rerun plus idempotency is conceptually sufficient after handoff proof | The publisher authenticates/reuses the immutable record and resumes the rolling operation, but it still needs the exact signed artifact handoff. |
| Rolling update succeeds; final verification fails | Must inspect, then native rerun plus idempotency only if published state authenticates | The next run may confirm the exact terminal state; any mismatch must refuse rather than overwrite or roll back. Channel withdrawal or a known-bad published build belongs to I07. |
| Entire workflow is rerun | Must refuse conflicting output or forward-fix | It rebuilds/re-signs. Deterministic identity checks make this safe but not resumptive; different bytes under the immutable version cannot replace existing bytes. |
| Required artifact expired or was deleted | Custom recovery cannot reuse it; rebuild/forward-fix | Exact bytes no longer exist at the checkpoint. The current artifacts retain for seven days, shorter than GitHub's maximum rerun window. |
| Protected `main` advances after failure | Must refuse stale publication; normally forward-fix | The publication guard requires the source to remain current protected-main tip. Recovery can only be an explicitly reviewed exceptional operation under the existing recovery contract. |
| Artifact predates the single-workflow architecture | Retire when no unfinished publication consumes it | Native rerun cannot reconstruct the old graph, but the hosted audit found every retained historical Development checkpoint already published. Compatibility without a consumer is not a recovery requirement. |

The then-existing `mosaic-development-resume.yml` no longer owned routine pre-sign or pre-publication recovery. Its former responsibilities are classified below; they were not collapsed into a replacement state machine.

| Recovery responsibility | Classification | Durable conclusion |
| --- | --- | --- |
| Build succeeded; Sign failed before signed output | **REPLACED BY NATIVE RERUN** | Case A proves failed-job rerun retains the exact unsigned checkpoint and reruns Sign plus dependent Publish. |
| Sign succeeded; Publish failed before mutation | **REPLACED BY NATIVE RERUN** | Case B proves failed-job rerun retains the exact signed checkpoint and reruns Publish alone. |
| Pre-Checkpoint-2 cross-workflow unsigned/signed artifacts | **REMOVE — no remaining consumer** | The hosted inventory found all retained Development checkpoints already published; expiry does not strand an unfinished obligation. |
| Expired or deleted workflow artifact | **REMOVE — forward-fix** | Exact bytes are unavailable and cannot be recreated by recovery; build forward from current protected `main`, never infer substitute bytes. |
| Partial immutable tag/release/assets | **REMOVE — native rerun / manual inspection** | The idempotent publisher can authenticate and resume exact state. Conflicting state must refuse for inspection rather than enter a generic repair workflow. |
| Partial rolling `develop` update or conflicting remote state | **REMOVE — native rerun / manual inspection** | Retry exact state through the authoritative run; inspect any refusal and never overwrite ambiguity. |
| Stale `main` or ambiguous/foreign provenance | **REMOVE — refuse / forward-fix** | Fail-closed refusal is the desired terminal behavior; stale or untrusted sources should not be made publishable by a recovery Action. |
| Withdraw a published bad APK, roll back/repoint `develop`, or recover forward after publication | **BELONGS TO I07** | These are channel safety and rollback decisions, not routine delivery resumption. |

The current Recovery workflow should disappear from the normal Actions menu. Its historical inputs may be deliberately retired now: expiry need not be awaited because none represents unfinished publication. If a future real incident demonstrates a repeatable safe repair that native rerun, exact-state idempotency, forward-fix, and I07 cannot handle, design that narrowly from the incident rather than retaining the current general artifact-resume surface.

Cases A and B require no implementation change or new recovery state machinery. The live runs proved that the existing native rerun path carries the prior successful Build/Sign outputs and exact artifacts into later Sign or Publish attempts. Do not generalize that evidence to partial publication or exceptional checkpoints: if a future boundary lacks prior outputs while its exact artifact remains available, the smallest acceptable correction is a narrowly scoped GitHub-API resolver bound to one run, successful producer attempt, source SHA/tree, exact artifact identity, and authenticated payload/provenance. Ambiguity or absence must fail closed. If the required artifact is unavailable, use explicit recovery or a forward build rather than weakening identity checks.

The minimum routine-recovery live acceptance is complete: Case A proved a Sign refusal before key use/output mutation, and Case B proved a Publish refusal before release mutation. Both retained the same run ID, advanced the attempt, reused exact prior successful artifacts and job outputs, avoided redundant prerequisite work, and completed one idempotent publication.

#### Remaining Development Recovery surface audit (2026-09-12)

**Conclusion: COMPLETE / READ-ONLY EVIDENCE.** No retained pre-Checkpoint-2 artifact has a genuine unfinished publication consumer. The dedicated Recovery workflow and the manual Development fallback now duplicate native failed-job rerun or reject states that should instead be inspected and forward-fixed. Mosaic does not currently have a demonstrated break-glass case that justifies a normal manually runnable recovery Action.

The hosted inventory found the following retained historical checkpoints, all with seven-day retention:

| Historical source | Retained checkpoint evidence | Publication state | Conclusion |
| --- | --- | --- | --- |
| `41f9f83c36b8866211c9680d3b416d5ebede4888` / `1.0.5` | Failed legacy run `34340900095` left unsigned artifact `10099950969`; Recovery run `34346274309` produced signed recovery artifact `10101833558`. Both expire 2026-09-16. | Successfully published as `downstream-build-5`, then promoted as `mosaic-v1.0.5`. | The only real legacy recovery episode is complete; neither artifact is an outstanding input. |
| `5818b605fe64fae97bdd20feed7b1df60600d08a` / `1.0.8` | Legacy unsigned/signed artifacts `10107084985` / `10107114732`, expiring 2026-09-16. | Successfully published as `downstream-build-8`. | No recovery consumer. |
| `a1ffce537ec6616e2dd2da4adb27e99b34e58fe2` / `1.0.9` | Legacy unsigned/signed artifacts `10110181005` / `10110215004`, expiring 2026-09-16. | Successfully published as `downstream-build-9`. | No recovery consumer. |
| `44e81da48ca50b70f1be364b3008294130d8721d` / `1.0.11` | Pre-consolidation main-CI unsigned artifact `10126382836` and cross-workflow signed artifact `10126413183`, expiring 2026-09-16. | Successfully published as `downstream-build-11`. | No recovery consumer. |
| `f247fd71eb1ef2126407a160d029a4be6cbc018d` / `1.0.17` | Pre-consolidation unsigned/signed artifacts `10174338384` / `10174375305`, expiring 2026-09-17. | Successfully published as `downstream-build-17`. | No recovery consumer. |
| `94036a6f57907c1b1cf2f4f7a4f174fd986df5d4` / `1.0.19` | Pre-consolidation unsigned/signed artifacts `10181275416` / `10181296956`, expiring 2026-09-18. | Successfully published as `downstream-build-19`. | No recovery consumer. |

The retained `1.0.3` signing-diagnostic artifacts are not Development publication checkpoints and are not accepted by the Recovery workflow's producer-path checks. Gaps in version numbers correspond to non-APK skips or development history, not unpublished recovery obligations. Current rolling `develop` points to source `1d17c94ab86b3ed8d9e6e0f42398ac99e4d7eb23` / `1.0.29`, with byte-identical immutable `downstream-build-29`; no current tag, Release, updater record, or public asset depends on an Actions artifact remaining downloadable. Actions artifact IDs and build run/attempt remain useful historical provenance, but artifact retention is not part of the updater or Stable contract.

##### Capability disposition

| Current surface/capability | Classification | Reason |
| --- | --- | --- |
| Recovery `unsigned` mode: `expected_sha`, `source_sha`, exact `artifact_id`, `checkpoint=unsigned`; authenticate, download, sign, verify, re-upload, publish | **REMOVE — native rerun** | Case A proved the same run retains the exact successful unsigned artifact and Build outputs while failed Sign and dependent Publish rerun. |
| Recovery `signed` mode: the same three identity inputs plus `checkpoint=signed`; authenticate, reverify, re-upload, publish | **REMOVE — native rerun** | Case B proved Publish alone can rerun with the exact successful signed artifact and Sign output. Re-uploading it under a recovery identity adds no safety property. |
| Recovery `sign`, `recover_signed`, and `publish` jobs | **REMOVE — native rerun** | Their build/sign/publish boundaries are already present in the authoritative CI run. The Recovery publisher delegates to the same idempotent publication implementation. |
| `mosaic_resume.py` guard, recovery artifact lookup, recovery CLI modes, and recovery-manifest generation | **REMOVE — no remaining consumer** | These exist solely for the two Recovery modes. `recovery.json` is consumed only inside that workflow/tests and is not used by Stable, the updater, or public release verification. |
| Historical identity plus original producer/run/job authentication | **KEEP — Stable compatibility** | Stable Promotion authenticates existing immutable Development manifests, including builds produced before Checkpoint 2. These shared checks move to the surviving Development provenance module; they do not provide artifact recovery. |
| Manual `Mosaic — Development Release` fallback input and classify/sign/publish graph | **REMOVE — no remaining consumer** | It accepts only exact current protected `main`, not arbitrary historical sources, and therefore cannot rescue old retained checkpoints. For current-main failures it duplicates native rerun; for expired input it cannot recreate exact bytes; for superseded main it correctly refuses. |
| Legacy `workflow_run` event parsing, external CI-run/artifact discovery, and old CLI modes retained only by the manual fallback | **REMOVE — no remaining consumer** | Normal CI uses same-run `ci-*` modes and exact `needs` artifact IDs. Remove only fallback-exclusive branches; retain shared verification, classification, versioning, idempotent publication, and permanent provenance code. |
| Exact source/tree/version, APK/package/signer/payload, run/attempt, artifact digest, immutable identity, rolling identity, and Stable-consumed manifest fields | **KEEP — permanent boundary** | These authenticate build and publication identity independently of Recovery and remain consumed by normal CI, release audit, Stable, or updater compatibility. |
| Publisher handling of an interrupted immutable/rolling publication | **KEEP — idempotent publisher, not a separate recovery workflow** | Native rerun re-enters the same publisher. It resumes only exact matching state and refuses conflicting, orphaned, newer, foreign, or otherwise ambiguous remote state. |
| Bad already-published APK, withdrawal, rolling-channel rollback/repointing, and forward recovery after publication | **MOVE TO I07** | These are release-channel incident and rollback decisions, not delivery-job resumption. |

##### Exceptional-state policy

| State | Correct response after this audit |
| --- | --- |
| Build or Sign artifact still retained in the current failed run | Use **Re-run failed jobs**. |
| Partial immutable publication with exact matching tag/manifest/assets | First use native failed-job rerun; the existing publisher may resume exact state idempotently. If it refuses, inspect rather than bypassing the invariant. |
| Partial rolling `develop` replacement with exact authenticated current publication | First use native failed-job rerun. If remote state is incomplete or surprising, stop for manual inspection; do not add a generic repair mode without a real incident. |
| Expired/deleted artifact | Refuse and produce a new forward build from current protected `main`. Exact missing bytes cannot be recovered honestly. |
| Conflicting immutable tag/Release/assets | Refuse and manually investigate. Immutable conflicts must never be overwritten by automation. |
| Stale protected `main` | Refuse and forward-fix/build from the new tip. Publishing an old source is not recovery. |
| Ambiguous or foreign provenance | Refuse. Repair evidence only through an explicit audited procedure; never infer identity. |
| Bad bytes already exposed through Development | I07 withdrawal/rollback/forward-recovery policy. |

There is consequently no justified **KEEP — break-glass** job today. The distinct safety property is fail-closed diagnosis, which the normal publisher already provides; a second workflow does not make ambiguous state safer. A dedicated automated repair workflow should be introduced only in response to a demonstrated repeatable state whose safe transition cannot be expressed by native rerun, the exact-state idempotent publisher, forward-fix, or I07.

##### Current versus proposed operator and implementation surface

| Measure | Current | Proposed |
| --- | --- | --- |
| Recovery/fallback workflows in the Actions menu | 2: Development Recovery and manual Development Release fallback | 0; CI owns Development delivery, while Stable Promotion remains a separate human decision |
| Recovery modes/operator choices | Recovery unsigned or signed, each requiring three exact identity values plus a checkpoint choice; or manual fallback with an exact SHA | One routine action: **Re-run failed jobs** on the authoritative CI run |
| Recovery workflow jobs | 3 (`sign`, `recover_signed`, `publish`) | 0 additional jobs; reuse CI Build/Sign/Publish jobs |
| Dedicated recovery implementation | 227 workflow lines, 211 helper lines, 242 direct test lines, plus fallback-only compatibility branches/docs | Remove the dedicated workflow/helper/tests and fallback-only branches after updating operator docs/tests; retain shared publisher and provenance tests |
| Recovery-only durable/transport state | `checkpoint`, recovery execution SHA/run/attempt, input artifact ID/digest, and `recovery.json` | None; GitHub run/attempt, retained artifacts, and the permanent release manifest remain canonical |
| Routine steps | Discover four inputs, choose a checkpoint, dispatch another Action, then authenticate/republish | Open the failed authoritative run and select **Re-run failed jobs** |

The target Actions menu is therefore `Mosaic — CI & Development`, `Mosaic — Stable Promotion`, and `Upstream — Synchronization`, subject to any separate workflow-presentation naming decision. Development Recovery should not remain visible as a normal operator choice merely as insurance against hypothetical states.

The repository's actual `mosaic-release-signing` configuration was inspected on 2026-09-12. It has only a custom branch policy allowing `main`; it has no required-reviewer, wait-timer, or custom protection rule. The current Environment therefore cannot be rejected or held before secret admission and cannot provide Case A without configuration change. Cancelling the workflow is not an equivalent experiment: cancellation produces cancelled work rather than the documented failed-job boundary, and cancelling after the branch rule passes does not prove credentials were never admitted.

The least invasive controlled Case A experiment is an explicitly authorized, temporary Environment required-reviewer rule, not production failure code. Before merging a naturally useful APK-relevant PR, snapshot the Environment configuration, add one reviewer while retaining the `main` branch restriction and existing bypass policy, and prevent concurrent `main` merges for the short experiment. After Build uploads its exact unsigned artifact and Sign is waiting, reject the deployment. GitHub documents that rejection fails the workflow before the job starts or receives Environment secrets. Capture attempt-1 jobs and artifact identity, select **Re-run failed jobs**, confirm the run ID is unchanged and attempt increments, then approve the newly evaluated Environment gate. The run must prove Build did not execute again, Sign consumed the original artifact ID/name/digest and build outputs, and Publish produced one consistent immutable/rolling result. Restore and verify the exact original Environment configuration afterward. Every settings mutation and deployment decision requires explicit user authorization.

The Case A experiment required stopping if Sign did not wait, Build did not finish/upload, a concurrent `main` push occurred, rejection was not rerunnable, the artifact/outputs changed, signing began during attempt `1`, or publication mutated early. All conditions held during acceptance. Do not reuse that temporary Environment configuration or the removed Case B boundary for future testing.

#### Case A native rerun live acceptance

**Status: COMPLETE / LIVE VALIDATED.** A temporary required-reviewer rule on `mosaic-release-signing` created the pre-secret refusal boundary without workflow, application, or failure-hook changes. Protected-main run `34653375353` built source `d628b335b97a59c5cb9b85c9bf86149a0eafefad` as version `1.0.28`. On attempt `1`, Full validation and the approximately `10m07s` Build succeeded, Sign was rejected while waiting for Environment review before key use, and Publish was skipped. No APK was signed and no tag, Release, asset, or updater state was mutated.

**Re-run failed jobs** kept run ID `34653375353`, incremented `run_attempt` to `2`, and did not rerun Full validation or Build. The Environment gate was evaluated again. After approval, Sign completed in approximately `32s` and Publish in approximately `22s`; the rerun took approximately `1m51s`, avoiding the `10m07s` rebuild. Sign authenticated and consumed exact unsigned artifact ID `10284309104`, named `unsigned-mosaic-main-ci-1.0.28-d628b335b97a59c5cb9b85c9bf86149a0eafefad-run-34653375353-attempt-1`, with archive SHA-256 `ded81c2cf4cb48ae363918ca9823c2e6d75742bb95906fd2fc3b813f93d2530c` and unsigned APK SHA-256 `2952b18b8b329b20ca8f54a60107392ac5c186b66c4d0480caa1bb9b54786c26`. Its provenance retained build run/attempt `34653375353/1` and source tree `50d42feb54a1d606eb6777d98668ef6c2a409a37`.

Attempt `2` produced signed artifact ID `10284454307`, named `signed-mosaic-development-1.0.28-d628b335b97a59c5cb9b85c9bf86149a0eafefad-run-34653375353-attempt-2`, and signed APK SHA-256 `55ede1fcb3c2df28ea35edd60ce9ac9fe2754f708911824b8c2910aa8980fe24`. Publication created/verified immutable `downstream-build-28` and updated rolling `develop`; both published APK assets were byte-identical to that signed digest and carried the expected version/source/build provenance. No duplicate or conflicting publication occurred.

The Actions UI hid attempt-1 artifacts in some later-attempt views, but the artifact API, job logs, verifier inputs, and published manifest provide the authoritative evidence: Sign selected the immutable numeric attempt-1 artifact ID rather than rebuilding or resolving by name alone. The temporary reviewer rule was removed after acceptance; `mosaic-release-signing` is restored to its original `main` branch policy with no required reviewers, wait timer, or custom protection rule, and administrator bypass remains disabled.

PR #45 did not supply reusable PR Full evidence because its APK-relevant resource-only change selected the targeted-Android/normal PR validation path rather than the complete Full graph. Protected-main therefore correctly ran the Full fallback with `required PR Full evidence is missing or ambiguous`. This is expected fail-closed behavior, not a Case A defect. A future observability-only cleanup may distinguish missing from ambiguous evidence in diagnostics; no reuse predicate should be weakened.

#### Case B native rerun live acceptance

**Status: COMPLETE / LIVE VALIDATED.** Protected-main run `34673534555` built source `1d17c94ab86b3ed8d9e6e0f42398ac99e4d7eb23` (tree `a0d10a2a6c978b6839965635a08c5ddb742f526d`) as version `1.0.29`. Attempt `1` retained/reused protected-main validation evidence, completed Build and Sign exactly once, and then failed Publish at the authorized boundary after exact signed-artifact download, canonical manifest reconstruction, protected-main freshness, and manifest equality checks but immediately before the first publication mutation. No `downstream-build-29` existed and rolling `develop` was unchanged after that refusal.

Sign produced exact artifact ID `10291668087`, named `signed-mosaic-development-1.0.29-1d17c94ab86b3ed8d9e6e0f42398ac99e4d7eb23-run-34673534555-attempt-1`, with archive SHA-256 `c41823c752169fe56eeb4fdab44d15b3d84e9a42f958c35fd32ad45fa00bf16f`. The final run artifact view also retained attempt-1 unsigned artifact ID `10291054170` (archive SHA-256 `1e7648760073e4e44f2c60d6e361d35d1a8d558b5352b24c4b9d9f79a9802fe2`) and mapping artifact ID `10291104210` (archive SHA-256 `1368649e7cfc6dd6cc0b18337e98cb6ea758e020b66c8ac7e795b6f3979356e0`).

**Re-run failed jobs** kept run ID `34673534555`, advanced to attempt `2`, and did not execute Validate, Build, or Sign again. Publish alone reran, recovered the successful Sign job output, downloaded the same numeric signed artifact ID `10291668087`, and published normally. Immutable release `downstream-build-29` is release ID `387460285`; its APK asset is ID `558646496`. Rolling `develop` is release ID `385461835`; its APK asset is ID `558646620`. Both APK assets are `27,702,722` bytes with SHA-256 `df362aa56f5e2b414f070c27dabb7d6bb8cc19e6887b1934bd32bef1e113f548`, exactly matching the authenticated signed result. Both manifests have SHA-256 `99426bbe8f82851661a5cb7672d9319c4029a6dcf72d33166fed3df099f1e86e` and preserve source/build provenance. There was one immutable publication, one rolling update, and no duplicate/conflicting release.

The temporary Case B selector, refusal function/call, and acceptance-only tests were removed immediately after proof. Production Publish again proceeds directly from protected-main/manifest verification to the unchanged idempotent publisher; no intentional Case B failure path remains.

### Compatibility constraints

- Keep current `downstream-build-N`, rolling `develop`, asset names, metadata, updater behavior, and version allocation unchanged.
- Keep Stable as exact-byte promotion from the authenticated immutable Development publication.
- Keep Environment approval/protection on the signing job.
- Keep signing credentials absent from build and publish, and release-write authority absent from build and sign.

### Completion evidence

- Offline tests prove job permission/secret boundaries, exact first-attempt artifact handoff, prior-attempt verifier acceptance, failure at modeled boundaries, publication idempotency, and unchanged release/update contracts. They do not prove GitHub's cross-attempt `needs` or artifact behavior.
- Local Full validation passes.
- Hosted acceptance proves a release-relevant protected-main run executes validation reuse/fallback -> Release build -> protected sign -> publish, with each job exposing only its authorized credentials and capabilities.
- Native failed-job rerun for both routine Case A and pre-mutation Case B is live validated. The obsolete manual fallback and recovery workflow are removed by the coherent recovery-surface checkpoint below.

Offline focused evidence covers same-run/prior-attempt identity, wrong run/attempt/name/ID refusal, protected-main tip refusal, exact job dependencies, one automatic publisher, job permissions/secrets, zero-Gradle signing/publication, artifact-ID handoffs, unchanged permanent verification, and existing idempotent publication/recovery behavior.

The first genuine APK-relevant application change, PR #44 (`feat: settings update consolidation`), completed the live acceptance cycle. Required PR Full run `34630460192`, attempt `1`, tested synthetic merge commit `5ba1cf6077e0f4ea4b18430294666d0c5a568326` for PR head `1fce1f74112581eb3fc019ea27520107ffc4d3a6`; its retained evidence artifact was ID `10276537040`, archive SHA-256 `6fe6bc34a96c6b8dee2d48d9c8d4ee023e373c5f30c442b38555ad84f14e40a4`. The tested tree was:

`4b6c988f260241eec9c041aca2a5b8ec632613b9`

PR #44 merged as protected-main source `f00cc9f7ceb0fbd6d3817923f5b2a6b02ec86b6e`, whose final tree was exactly the same. Protected-main `CI` run `34631121022`, attempt `1`, therefore authenticated and reused the required PR Debug Full evidence. Its visible dependent sequence completed successfully:

``` text
Full validation
  -> Build Development Release
  -> Sign Development
  -> Publish Development
```

Observed job durations were approximately `1m39s`, `10m09s`, `37s`, and `16s`, respectively. Final-context Release assembly produced version name `1.0.27` / version code `27` from source tree `4b6c988f260241eec9c041aca2a5b8ec632613b9`, with unsigned APK SHA-256 `a005cb2e6ea9826f908c1f1cef9f59b0eee2771967d5e3d53c286d7a85ec8efe`. Same-run unsigned artifact ID `10276721173` (archive SHA-256 `e906e47b2e89707755baa16b5c4c318b2147a10b1704bf807ce05f2929bd3471`) was authenticated before the protected signing job. Signing and the permanent package/version/signer/payload checks succeeded; signer SHA-256 remained `63756183d6e77b2a5e7cd69b409532ee0b3c4710e13a10228dfb58186f556b84`. Same-run signed artifact ID `10276014978` (archive SHA-256 `c44727843aadb6adf550367fcb920d06878ce915603fbc80e417b76e218edd32`) carried signed APK SHA-256 `4698253721210e05a1e57e84ff1158c277455d3a9837d39fa3ba29b15473b7dd` into the publication-only job.

Publication created immutable `downstream-build-27` (release ID `387246656`) and updated rolling `develop` (release ID `385461835`) with the same `Wholphin-release.apk` bytes and unchanged `mosaic-release.json` contract. The immutable and rolling APK assets both report SHA-256 `4698253721210e05a1e57e84ff1158c277455d3a9837d39fa3ba29b15473b7dd`; version, source, run/attempt, package, signer, updater, and Stable-promotion identities remain compatible. Earlier I01 live evidence already proved that a non-APK merge terminates before Release assembly, signing, and publication.

This established exactly one automatic Development-delivery path. At that checkpoint the old workflow remained an explicit manual legacy fallback; the later consumer audit and native-rerun proofs authorized its removal. Stable promotion, updater contracts, signing identity, version allocation, I06, the signing diagnostic, and permanent provenance fields were not changed.

### Explicit exclusions

Checkpoint 2 did not initially remove recovery. The later evidence-backed recovery-surface checkpoint below removes only the now-obsolete fallback and resume machinery without changing Stable or I07.

## Future checkpoints and candidates

### Validation-selection simplification

- Keep `prepare-pr` conservative by default while allowing Codex to propose relevant JVM and offline-tooling scopes.
- Make `prepare-pr` independently prove that requested scopes are safe for the complete PR diff; never trust a narrower proposal merely because it is faster.
- Allow irrelevant offline suites to be skipped when the classifier proves they add no evidence, rather than always running all tooling tests.
- Retain standalone Fast, Standard, and Full modes for debugging and explicit assurance.
- Later allow Codex to configure a VS Code **Prepare PR - Current task** invocation only with parameters that the policy independently validates.

### Actions presentation cleanup

- Evaluate concise protected-main labels `Validate -> Build -> Sign -> Publish` without changing `CI` / `Full validation` or any required-check identity unless every branch-protection/check consumer is deliberately migrated.
- Prefer concise stage summaries over duplicated lifecycle state, with a final Publish summary showing the completed Development identity and stage results.

### Recovery simplification

- Treat native **Re-run failed jobs** as the proven routine recovery for a pre-sign Case A failure: successful Build and its exact unsigned artifact survive while Sign and dependent Publish rerun.
- Remove the manual Development fallback and `Mosaic — Development Recovery` after this consumer audit, together with only their exclusive compatibility code/tests/docs. Preserve the signing diagnostic and permanent provenance because they have separate consumers.

### Workflow consolidation and removal

- Audit legacy, inherited, fallback, and diagnostic workflows only after their consumers and replacements are proven.
- Keep Stable Promotion separate: it represents a genuinely separate later human promotion decision.

For every candidate, challenge the requirement first, prefer native Git/GitHub behavior, and retain custom machinery only when it protects a distinct demonstrated property.

## Development Recovery removal checkpoint

**IMPLEMENTED / OFFLINE + LOCAL FULL VALIDATED; HOSTED ACCEPTANCE PENDING.** Native failed-job rerun is sufficient and live-proven for both routine boundaries. The coherent removal deletes `.github/workflows/mosaic-development-resume.yml`, `.github/workflows/mosaic-development-release.yml`, `scripts/mosaic_resume.py`, their exclusive tests/state/presentation, and fallback-only dispatch/cross-workflow branches. No replacement recovery abstraction is added. The complete offline suite passed 202 tests with one expected Windows skip, and Full validation passed repository-wide pre-commit, the tooling suite, the full default-debug graph, APK assembly, and whitespace checks.

Stable still needs to authenticate already-published historical Development manifests. The history reconstruction and original producer/run/job checks therefore moved into `mosaic_development_release.py`; the legacy workflow path remains only as an accepted historical `buildWorkflow` value. It cannot dispatch, locate an artifact, sign, or publish.

The permanent operating model is:

- routine Build/Sign/Publish failure: GitHub **Re-run failed jobs**;
- inconsistent or ambiguous remote state: fail closed and inspect;
- stale source or expired/deleted artifact: forward-fix from current protected `main`;
- bad published APK, withdrawal, rolling rollback/repointing, or post-publication recovery: I07.

No identified property makes the one-workflow/three-job model inherently weaker. It becomes weaker only if implementation leaks signing credentials into build/publish, grants release mutation to build/sign, trusts mutable or ambiguous artifacts, drops permanent APK verification, changes version/update identities, or removes recovery before replacement is proven.
