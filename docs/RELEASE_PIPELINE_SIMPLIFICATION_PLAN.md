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
- `sign-development` consumes the exact same-run unsigned artifact ID, validates its source/tree/version/run/attempt/name and bytes, signs through the unchanged local action inside `mosaic-release-signing`, and permanently verifies package/version/signer/payload before uploading the exact signed result. It has no Gradle command or release-write permission.
- `publish-development` consumes the exact signed artifact ID, reconstructs and verifies the publication manifest before credential use, rechecks that the source remains protected-main tip, and uses the existing idempotent publisher. It alone has `contents: write` and has no signing Environment or credentials.
- The old `mosaic-development-release.yml` no longer has an automatic `workflow_run` trigger. It remains an explicit exact-SHA manual fallback using the previously proven cross-workflow authentication until hosted acceptance permits a later retirement decision. `mosaic-development-resume.yml` is unchanged.

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
- The explicit manual fallback and dedicated recovery workflow remain for unproven Case B, partial publication, expired/deleted artifacts, stale-main refusal, legacy checkpoints, and exceptional repair. They are no longer required for the now-proven routine Case A boundary.

#### Native rerun recovery analysis

| Failure point | Correct recovery | Reason |
| --- | --- | --- |
| Build fails before unsigned upload | Native rerun sufficient | Failed build and its dependents rerun; there is no successful artifact to preserve. |
| Build succeeds; Sign fails before signed upload | Native rerun sufficient — **LIVE VALIDATED** | Run `34653375353` proved that **Re-run failed jobs** retained the successful Build and its exact attempt-1 unsigned artifact/outputs, reran the protected Sign job, then ran dependent Publish. |
| Sign uploads signed artifact; a later Sign step fails | Custom recovery still required | The Sign job is failed and reruns, potentially signing/uploading again; the retained signed checkpoint is instead an exceptional artifact-recovery input. |
| Build and Sign succeed; Publish fails before mutation | Custom recovery still required today | Publish alone should rerun, but its signed artifact ID and build provenance arrive through prior successful jobs' `needs` outputs, whose cross-attempt availability is undocumented. |
| Immutable publication succeeds; rolling update fails | Native rerun plus idempotency is conceptually sufficient after handoff proof | The publisher authenticates/reuses the immutable record and resumes the rolling operation, but it still needs the exact signed artifact handoff. |
| Rolling update succeeds; final verification fails | Must inspect, then native rerun plus idempotency only if published state authenticates | The next run may confirm the exact terminal state; any mismatch must refuse rather than overwrite or roll back. Channel withdrawal or a known-bad published build belongs to I07. |
| Entire workflow is rerun | Must refuse conflicting output or forward-fix | It rebuilds/re-signs. Deterministic identity checks make this safe but not resumptive; different bytes under the immutable version cannot replace existing bytes. |
| Required artifact expired or was deleted | Custom recovery cannot reuse it; rebuild/forward-fix | Exact bytes no longer exist at the checkpoint. The current artifacts retain for seven days, shorter than GitHub's maximum rerun window. |
| Protected `main` advances after failure | Must refuse stale publication; normally forward-fix | The publication guard requires the source to remain current protected-main tip. Recovery can only be an explicitly reviewed exceptional operation under the existing recovery contract. |
| Artifact predates the single-workflow architecture | Existing custom recovery required | Native rerun cannot recreate the old cross-workflow producer relationship; `mosaic-development-resume.yml` deliberately authenticates those legacy checkpoints. |

`mosaic-development-resume.yml` therefore still has three distinct responsibilities. Its routine sign/publish resumption is a candidate for removal only after native handoff is proven. Its exact-artifact authentication, signed-checkpoint re-verification, partial-release repair, and stale/ambiguous refusal remain exceptional safety capabilities. Its support for pre-Checkpoint-2 artifacts is legacy compatibility and cannot be replaced by rerunning the new workflow. However, it is not currently a general fallback for a failed single-workflow run: both `artifact_metadata` and `validate_original_source` require a main-CI producer run to have overall conclusion `success`, which is false when its later Sign or Publish job failed. That restriction must not be relaxed without separately authenticating the successful producing job and exact failed-run checkpoint. Rollback or withdrawal of already-published bad Development bytes is not delivery recovery; it belongs to I07.

Case A now requires no implementation change or new recovery state machinery. The live run proved that the existing native rerun path carries the prior successful Build outputs and exact artifact into a later Sign attempt. Do not generalize that evidence to Case B or exceptional checkpoints: if a future boundary lacks prior outputs while its exact artifact remains available, the smallest acceptable correction is a narrowly scoped GitHub-API resolver bound to one run, successful producer attempt, source SHA/tree, exact artifact identity, and authenticated payload/provenance. Ambiguity or absence must fail closed. If the required artifact is unavailable, use explicit recovery or a forward build rather than weakening identity checks.

Minimum live acceptance is one safely pre-publication failure at each boundary: (A) fail Sign before key use/output mutation, then **Re-run failed jobs** and prove Build did not rerun while the exact unsigned artifact ID was reused; (B) fail Publish before release mutation, then rerun failed jobs and prove neither Build nor Sign reran while the exact signed artifact ID was reused. Both must show the same run ID, higher attempt, repeated Environment gating for Sign, unchanged job permissions, and successful final idempotent publication.

The repository's actual `mosaic-release-signing` configuration was inspected on 2026-09-12. It has only a custom branch policy allowing `main`; it has no required-reviewer, wait-timer, or custom protection rule. The current Environment therefore cannot be rejected or held before secret admission and cannot provide Case A without configuration change. Cancelling the workflow is not an equivalent experiment: cancellation produces cancelled work rather than the documented failed-job boundary, and cancelling after the branch rule passes does not prove credentials were never admitted.

The least invasive controlled Case A experiment is an explicitly authorized, temporary Environment required-reviewer rule, not production failure code. Before merging a naturally useful APK-relevant PR, snapshot the Environment configuration, add one reviewer while retaining the `main` branch restriction and existing bypass policy, and prevent concurrent `main` merges for the short experiment. After Build uploads its exact unsigned artifact and Sign is waiting, reject the deployment. GitHub documents that rejection fails the workflow before the job starts or receives Environment secrets. Capture attempt-1 jobs and artifact identity, select **Re-run failed jobs**, confirm the run ID is unchanged and attempt increments, then approve the newly evaluated Environment gate. The run must prove Build did not execute again, Sign consumed the original artifact ID/name/digest and build outputs, and Publish produced one consistent immutable/rolling result. Restore and verify the exact original Environment configuration afterward. Every settings mutation and deployment decision requires explicit user authorization.

Stop if Sign does not wait, Build did not finish/upload, a concurrent `main` push occurs, rejection does not yield a failed rerunnable job, the original artifact becomes unavailable, Build reruns, any required `needs` output is empty, artifact identity differs, signing begins during attempt 1, or any release/tag mutation appears before the approved attempt-2 Publish. Do not deliberately damage a release or retain permanent failure plumbing for Case B; wait for a natural pre-mutation failure if a temporary reviewed boundary would cost more than the evidence is worth.

#### Case A native rerun live acceptance

**Status: COMPLETE / LIVE VALIDATED.** A temporary required-reviewer rule on `mosaic-release-signing` created the pre-secret refusal boundary without workflow, application, or failure-hook changes. Protected-main run `34653375353` built source `d628b335b97a59c5cb9b85c9bf86149a0eafefad` as version `1.0.28`. On attempt `1`, Full validation and the approximately `10m07s` Build succeeded, Sign was rejected while waiting for Environment review before key use, and Publish was skipped. No APK was signed and no tag, Release, asset, or updater state was mutated.

**Re-run failed jobs** kept run ID `34653375353`, incremented `run_attempt` to `2`, and did not rerun Full validation or Build. The Environment gate was evaluated again. After approval, Sign completed in approximately `32s` and Publish in approximately `22s`; the rerun took approximately `1m51s`, avoiding the `10m07s` rebuild. Sign authenticated and consumed exact unsigned artifact ID `10284309104`, named `unsigned-mosaic-main-ci-1.0.28-d628b335b97a59c5cb9b85c9bf86149a0eafefad-run-34653375353-attempt-1`, with archive SHA-256 `ded81c2cf4cb48ae363918ca9823c2e6d75742bb95906fd2fc3b813f93d2530c` and unsigned APK SHA-256 `2952b18b8b329b20ca8f54a60107392ac5c186b66c4d0480caa1bb9b54786c26`. Its provenance retained build run/attempt `34653375353/1` and source tree `50d42feb54a1d606eb6777d98668ef6c2a409a37`.

Attempt `2` produced signed artifact ID `10284454307`, named `signed-mosaic-development-1.0.28-d628b335b97a59c5cb9b85c9bf86149a0eafefad-run-34653375353-attempt-2`, and signed APK SHA-256 `55ede1fcb3c2df28ea35edd60ce9ac9fe2754f708911824b8c2910aa8980fe24`. Publication created/verified immutable `downstream-build-28` and updated rolling `develop`; both published APK assets were byte-identical to that signed digest and carried the expected version/source/build provenance. No duplicate or conflicting publication occurred.

The Actions UI hid attempt-1 artifacts in some later-attempt views, but the artifact API, job logs, verifier inputs, and published manifest provide the authoritative evidence: Sign selected the immutable numeric attempt-1 artifact ID rather than rebuilding or resolving by name alone. The temporary reviewer rule was removed after acceptance; `mosaic-release-signing` is restored to its original `main` branch policy with no required reviewers, wait timer, or custom protection rule, and administrator bypass remains disabled.

PR #45 did not supply reusable PR Full evidence because its APK-relevant resource-only change selected the targeted-Android/normal PR validation path rather than the complete Full graph. Protected-main therefore correctly ran the Full fallback with `required PR Full evidence is missing or ambiguous`. This is expected fail-closed behavior, not a Case A defect. A future observability-only cleanup may distinguish missing from ambiguous evidence in diagnostics; no reuse predicate should be weakened.

#### Case B native rerun acceptance

**Status: PENDING LIVE ACCEPTANCE.** The acceptance branch contains a temporary pre-mutation refusal inside `ci-publish`, after exact signed-artifact/manifest reconstruction and current protected-main verification but immediately before `publish()` can create an immutable tag or alter rolling `develop`. It matches only attempt `1` of the uniquely allocated version `1.0.29` episode whose exact first parent is `d628b335b97a59c5cb9b85c9bf86149a0eafefad` and whose complete reviewed path set is embedded in the selector. Any intervening merge, extra/missing path, different repository/ref/event/SHA, different version, or later attempt bypasses the boundary rather than affecting an unrelated publication.

Live acceptance must prove that **Re-run failed jobs** keeps Validate, Build, and Sign successful without rerunning them; retains the successful Sign output and exact signed artifact ID from attempt `1`; and reruns Publish alone on attempt `2`, where the temporary boundary naturally does not apply. Publication must then produce one exact immutable/rolling result with no attempt-1 mutation. Remove `CASE_B_ACCEPTANCE_VERSION_CODE`, `CASE_B_ACCEPTANCE_PARENT_SHA`, `CASE_B_ACCEPTANCE_PATHS`, `require_case_b_acceptance_boundary()`, its call site, and their focused tests immediately after successful acceptance. Do not retain this experiment as recovery machinery.

### Compatibility constraints

- Keep current `downstream-build-N`, rolling `develop`, asset names, metadata, updater behavior, and version allocation unchanged.
- Keep Stable as exact-byte promotion from the authenticated immutable Development publication.
- Keep Environment approval/protection on the signing job.
- Keep signing credentials absent from build and publish, and release-write authority absent from build and sign.

### Completion evidence

- Offline tests prove job permission/secret boundaries, exact first-attempt artifact handoff, prior-attempt verifier acceptance, failure at modeled boundaries, publication idempotency, and unchanged release/update contracts. They do not prove GitHub's cross-attempt `needs` or artifact behavior.
- Local Full validation passes.
- Hosted acceptance proves a release-relevant protected-main run executes validation reuse/fallback -> Release build -> protected sign -> publish, with each job exposing only its authorized credentials and capabilities.
- Native failed-job rerun for Case A is live validated. Case B and exceptional/legacy recovery remain separate acceptance questions; the manual fallback and recovery workflow remain preserved safety tools and are not yet proven compatible with every overall-failed single-workflow producer.

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

This establishes exactly one automatic Development-delivery path. `.github/workflows/mosaic-development-release.yml` is no longer part of normal automatic delivery and remains only an explicit manual legacy fallback. Stable promotion, updater contracts, signing identity, version allocation, recovery, I06, the signing diagnostic, and permanent provenance fields were not changed.

### Explicit exclusions

Checkpoint 2 does not add artifact attestations, reduce provenance fields speculatively, remove recovery, modify Stable, implement I07, or delete legacy workflows. Each is a later evidence-backed decision.

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
- Preserve the manual legacy Development fallback, `Mosaic - Development Recovery`, signing diagnostic, cross-workflow compatibility/recovery code, and permanent provenance for Case B and exceptional/legacy responsibilities until equivalent behavior is live-proven.

### Workflow consolidation and removal

- Audit legacy, inherited, fallback, and diagnostic workflows only after their consumers and replacements are proven.
- Keep Stable Promotion separate: it represents a genuinely separate later human promotion decision.

For every candidate, challenge the requirement first, prefer native Git/GitHub behavior, and retain custom machinery only when it protects a distinct demonstrated property.

## Smallest next checkpoint

Do not implement a Case A recovery mechanism: native rerun is sufficient and live-proven. The next recovery-simplification checkpoint is evidence for Case B—a natural Publish failure before mutation followed by **Re-run failed jobs**, proving that successful Build and Sign do not rerun and the exact signed artifact remains available. Do not manufacture partial public Release state merely to obtain that evidence. Until it occurs, preserve the fallback/recovery machinery. The separate smallest observability candidate is to report `missing` and `ambiguous` PR Full evidence distinctly while retaining the same protected-main Full fallback.

No identified property makes the one-workflow/three-job model inherently weaker. It becomes weaker only if implementation leaks signing credentials into build/publish, grants release mutation to build/sign, trusts mutable or ambiguous artifacts, drops permanent APK verification, changes version/update identities, or removes recovery before replacement is proven.
