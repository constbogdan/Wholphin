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

**Status: IMPLEMENTED / OFFLINE VALIDATED; HOSTED ACCEPTANCE PENDING.**

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

- Build succeeds, signing fails: GitHub's **Re-run failed jobs** reuses the successful build job output and exact retained unsigned artifact ID; the verifier accepts an earlier attempt only within the same immutable run. It does not rebuild or publish.
- Signing succeeds, publication fails: **Re-run failed jobs** reuses the successful sign job output and exact retained signed artifact ID, then repeats manifest verification and idempotent publication only.
- Rerunning a workflow must derive the same source/version identity and refuse conflicting immutable output. It may reuse authenticated earlier-job output only when GitHub and artifact identity prove the exact attempt/source relationship.
- Publication must retain current idempotency: never create conflicting `downstream-build-N` bytes, and update rolling `develop` only from the authenticated immutable result.
- A full-workflow rerun may reproduce build/sign outputs, but immutable publication conflict checks still refuse different bytes under the same identity. The explicit manual fallback and dedicated recovery workflow remain until hosted retry evidence proves the same-run replacement for every supported checkpoint.

### Compatibility constraints

- Keep current `downstream-build-N`, rolling `develop`, asset names, metadata, updater behavior, and version allocation unchanged.
- Keep Stable as exact-byte promotion from the authenticated immutable Development publication.
- Keep Environment approval/protection on the signing job.
- Keep signing credentials absent from build and publish, and release-write authority absent from build and sign.

### Completion evidence

- Offline tests prove job permission/secret boundaries, exact artifact handoff, failure at every boundary, rerun/idempotency behavior, and unchanged release/update contracts.
- Local Full validation passes.
- Hosted acceptance proves a release-relevant protected-main run executes validation reuse/fallback -> Release build -> protected sign -> publish, with each job exposing only its authorized credentials and capabilities.
- Failure-path evidence proves build or signing success can be resumed without rebuilding or publishing conflicting bytes.

Offline focused evidence covers same-run/prior-attempt identity, wrong run/attempt/name/ID refusal, protected-main tip refusal, exact job dependencies, one automatic publisher, job permissions/secrets, zero-Gradle signing/publication, artifact-ID handoffs, unchanged permanent verification, and existing idempotent publication/recovery behavior. Hosted evidence remains required before this checkpoint is marked complete.

### Explicit exclusions

Checkpoint 2 does not add artifact attestations, reduce provenance fields speculatively, remove recovery, modify Stable, implement I07, or delete legacy workflows. Each is a later evidence-backed decision.

## Later decisions

After Checkpoint 2 is proven, reassess which cross-workflow authentication and dedicated recovery mechanisms have no remaining consumer. Challenge every retained custom mechanism: it must name the distinct property it protects. Prefer GitHub's native run, job dependency, Environment, artifact, and rerun semantics wherever they satisfy the requirement.

## Smallest next implementation branch

Use the current `chore/release-delivery-single-workflow` branch for review and hosted acceptance. The minimum live proof is one naturally release-relevant protected-main run showing validation reuse/fallback -> Release build -> protected sign -> publish, followed by an authorized failed-job retry exercise when a natural failure supplies that checkpoint. Preserve the manual fallback and recovery workflows until that evidence exists.

No identified property makes the one-workflow/three-job model inherently weaker. It becomes weaker only if implementation leaks signing credentials into build/publish, grants release mutation to build/sign, trusts mutable or ambiguous artifacts, drops permanent APK verification, changes version/update identities, or removes recovery before replacement is proven.
