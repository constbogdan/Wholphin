# Mosaic rolling development publication

Status: **COMPLETE / LIVE VALIDATED** for downstream development delivery and in-place
updating via unsigned-artifact recovery. Stable promotion + channel UX are IMPLEMENTED / LIVE STABLE PROMOTION PENDING. Automatic publication
remains disabled; CI/developer-velocity optimization remains pending.

Current implementation update: [Stable promotion and channel UX](MOSAIC_STABLE.md) are
IMPLEMENTED / LIVE STABLE PROMOTION PENDING. Earlier Stable NEXT statements in the acceptance evidence below
record that preceding checkpoint. Automatic development publication remains
disabled; this task did not promote, rebuild or re-sign the accepted development APK.

## Development delivery and in-place updater acceptance - COMPLETE / LIVE VALIDATED

This checkpoint records user-supplied hosted and device acceptance evidence. No live
operation was rerun while documenting it. The complete downstream development delivery
and in-place updater path is now operational. Automatic publication remains disabled;
stable promotion is NEXT and is not implemented by this checkpoint.

### Original build and recovered publication

The first normal development run targeted source
`41f9f83c36b8866211c9680d3b416d5ebede4888`, version `1.0.5`, versionCode `5`, intended
identity `downstream-build-5`. It successfully produced authoritative unsigned artifact
`10099950969`. Signing then failed because the refactored reusable signer received empty
Environment credentials; publication was skipped. This was an orchestration/Environment-
binding regression, not a failed key, certificate, APK or signing password. The precise
GitHub-side reason for the empty values was not independently established.

The reusable `mosaic-isolated-sign.yml` was replaced by ordinary signing jobs bound
directly to `mosaic-release-signing`. The actual signing commands remain shared in
`.github/actions/mosaic-sign-apk/action.yml`. Step-scoped credentials, read-only signing,
no PR signing credentials, safe presence-only diagnostics and zero signing-stage Gradle
work are preserved. No signing key or Environment secret replacement was needed.

Main CI passed for recovery tooling SHA
`7d55b98b22e2d440599dfef7288f2ac066a0f8b1`. The manually authorized
`mosaic-development-resume.yml` run used `checkpoint=unsigned`, original source
`41f9f83c36b8866211c9680d3b416d5ebede4888` and artifact `10099950969`. It successfully
authenticated the existing artifact, signed, verified and published it, with no build or
Gradle job. The prior instruction not to reuse this artifact was unnecessarily restrictive.
No recovery run ID was supplied for this checkpoint; none is inferred.

| Published property | Accepted value |
| --- | --- |
| Immutable provenance prerelease | `downstream-build-5` |
| Rolling prerelease | `develop` |
| Display version / versionCode | `v1.0.5` / `5` |
| Source SHA | `41f9f83c36b8866211c9680d3b416d5ebede4888` |
| APK alias | `Wholphin-release.apk` |
| Manifest | `mosaic-release.json` |
| Signed APK SHA-256 | `af0dcb7fb1c89800c61e7a7a0558cbb2e6fc65fbf880069dbe08c3c4df8bf578` |

The rolling and immutable releases exposed the same APK digest and provenance. Both are
GitHub prereleases, not stable/latest. Publication acceptance was achieved through the
recovery path; this is not evidence of a second successful uninterrupted normal run.

### Mosaic-driven in-place update

The previously installed signed Mosaic 1.0.3 was preserved until this test. Because it
predates downstream-routing defaults, its custom Update URL was manually set to:

```text
https://api.github.com/repos/constbogdan/Wholphin/releases/tags/develop
```

The offered update immediately changed from upstream `v1.0.7` to downstream `v1.0.5`.
Mosaic displayed release metadata for `Mosaic development build downstream-build-5`,
the published source SHA and signed SHA-256 above. This validates the API-format develop
routing, numeric version discovery and downstream release-note/source metadata contract.

The user selected **Download & Update**. Mosaic itself selected and downloaded
`Wholphin-release.apk` (approximately **26.40 MiB**). Android requested the first-use
unknown-apps permission for Wholphin/Mosaic; after **Allow from this source** was enabled,
Android accepted the APK as an update to the existing installation and completed it.
There was no application-ID or certificate conflict, uninstall/reinstall, ADB installation
or data clearing. This was a real self-update, proving Mosaic application identity and
permanent signing continuity across 1.0.3 -> 1.0.5.

Mosaic reopened and displayed **Wholphin updated to v1.0.5**. Existing application/library
state remained present. Installed-version metadata showed `v1.0.5`, `downstream-build-5`,
source `41f9f83c36b8866211c9680d3b416d5ebede4888` and the published signed hash/provenance.
The custom develop Update URL also survived. Settings/data preservation was therefore
live-observed; this does not claim exhaustive validation of every setting or device.
The accepted installed instance is now 1.0.5; do not restore/reset it to recreate 1.0.3.

### Recovery and remaining sequence

```text
build failure   -> rebuild
sign failure    -> reuse authoritative unsigned artifact
publish failure -> reuse verified signed artifact
```

Unsigned recovery is now LIVE VALIDATED. Signed recovery is implemented/offline-tested:
existing signed artifact -> authenticate/provenance-check -> fresh SDK verification ->
publish, without re-signing. No live signed-checkpoint retry was supplied as evidence.
Both recovery paths contain zero Gradle work; immutable accepted bytes remain protected.

1. **Permanent signing identity - COMPLETE / LIVE VALIDATED.**
2. **Updater routing - COMPLETE / LIVE VALIDATED.**
3. **Rolling development release - COMPLETE / LIVE VALIDATED.**
4. **Live device in-place update acceptance - COMPLETE / LIVE VALIDATED.**
5. **Stable promotion + channel UX - IMPLEMENTED / LIVE STABLE PROMOTION PENDING.**
6. **CI/developer-velocity optimization - PENDING.**

### Retained CI and developer-velocity evidence

Optimization is pending. Local `prepare-pr.ps1` performs work later repeated by hosted
CI; PR/main/signing paths repeat expensive Kotlin/Gradle work, with
`compileDefaultDebugKotlin` a major cost. Earlier signing acceptance measured roughly
**16m43s build versus 34s signing**; recent ordinary main CI took roughly **6-7 minutes**.
These are observed examples, not universal timing guarantees. Development publication
built Release after main CI because ordinary CI retains Debug artifacts. Successful
recovery now proves that a downstream-stage retry can perform zero Gradle work.

Retain authoritative unsigned/signed artifact reuse, change-aware validation, concurrent
independent PRs, GitHub merge-queue evaluation, faster PR feedback versus the Full merge
gate, improved GitHub/local progress/status UX, and quiet-by-default `prepare-pr.ps1`
with complete retained diagnostic logs. Use representative Actions logs to construct a
measured task-overlap/timing matrix before redesigning local/hosted validation. This
checkpoint changes no automation, stable promotion, CI or application behavior.


## Trusted build, sign and publish

[Development workflow](../.github/workflows/mosaic-development-release.yml) accepts
only manual dispatch in `constbogdan/Wholphin`, from protected `main`, with an approved
full `expected_sha` exactly equal to the dispatch SHA. The helper also verifies the
workflow path/ref and rechecks the protected main tip through GitHub immediately before
build and publication. A changed main tip or unfinished/failed CI stops the run.

The read-only gate identifies `ci.yml` by workflow ID and requires its latest push run
for that exact SHA/main/repository, completed successfully, with a successful exact-SHA
`Full validation` job in that run attempt. PR merge artifacts, caller-selected runs,
forks and arbitrary branches cannot supply trust. Existing required CI is unchanged.

1. Build: after that gate, assemble `defaultRelease` once with publication identity,
   full Git history and bounded workers. No second Full Debug compile/test/assembly.
   Release compilation and its existing assembly/vital checks remain necessary because
   ordinary CI currently produces Debug, not Release. Setup is reused; broader CI cache,
   change-aware validation and artifact promotion redesign remain deferred.
2. Transport: reuse `mosaic_signing_exercise.py` to select the exact UNIVERSAL entry in
   `app/build/outputs/apk/default/release/output-metadata.json`. Record source SHA/tree,
   epoch/upstream baseline, allocated version, clean publication status, source-derived
   build time, run/attempt and unsigned APK hash. Upload for seven days; pass the upload
   action's immutable numeric artifact ID, never a caller-selected name/run.
3. Sign: both the original exercise and the publisher bind their own read-only signing job
   to `mosaic-release-signing` and invoke the same
   [signing operation](../.github/actions/mosaic-sign-apk/action.yml). The Environment retains the existing four secrets; only the action invocation step
   receives them through its environment. Public input,
   alignment and unsigned checks precede secret injection; only SDK apksigner runs in
   the secret-bearing step. Cleanup removes temporary key material. No Gradle/cache or
   release write exists in this job. Existing payload comparison and
   `verify_mosaic_apk.py` enforce the pinned certificate, non-debuggable Mosaic package,
   allocated version and unsigned/source/run provenance.
4. Publish: a fresh job downloads only the sign job's immutable artifact ID, rejecting
   digest mismatch. It rechecks the acceptance record against the exact checkout's
   allocation, current run/attempt, pinned public policy and signed APK hash. Only this
   job has `contents: write`; its token is explicitly passed only to the publication
   command, with checkout credential persistence disabled. There is no signing
   Environment/key, Gradle invocation, Sync Bot credential, PAT or stable publisher.

The shared signing action retains the proven signing commands and isolation. Direct
Environment binding restores the successful standalone job structure; the corrected
unsigned-recovery publication integration is now live validated (evidence above). Secret presence checks report
only each required name as present/missing, failing before key-file creation. Seven-day unsigned/signed
Actions artifact names retain the proven format:
`unsigned-` / `signed-mosaic-signing-exercise-1.0.N-<sha>-run-<id>-attempt-<attempt>`.
The historical `signing-exercise` name describes the reused transport and does not
imply the new workflow publishes without authorization. Signed transfer contains
`Mosaic-release.apk` and `verification.json`.

## Release and identity contract

| Purpose | GitHub representation | Update rules |
| --- | --- | --- |
| Immutable build ledger | Annotated tag `downstream-build-N` at exact main source; tag message is canonical manifest JSON | Create only; never move/delete/replace through this publisher |
| Durable build assets | Prerelease attached to `downstream-build-N`, display name `v1.0.N` | Same accepted APK and manifest retained without expiry; never replace published assets |
| Rolling channel | Tag and reused prerelease `develop`, display name `v1.0.N` | Move only this tag; keep existing release ID; no downgrade |
| Stable channel | Not implemented | No stable/version release or `/latest` promotion |

Both release kinds use `prerelease: true` and `make_latest: false`. The updater parses
release **name**, not tag: `v1.0.N` satisfies the existing numeric parser. The publisher
exposes **`Wholphin-release.apk`** as the exact universal alias, plus
**`mosaic-release.json`**. No Debug/ABI aliases are advertised without corresponding
builds. Existing updater preference for a supported ABI followed by the universal
Release alias remains compatible, without generic fallback. No application code changes.
The immutable `downstream-build-N` tag is not an updater `v1.0.N` history tag; historical
installed-version notes may still be unavailable after develop moves. That existing
limitation does not block update discovery/download and is not changed here.

The annotated tag reserves the full manifest before release assets are written. Existing
identity must match exact source, bytes AND provenance, including original run/attempt.
The publisher verifies GitHub asset size/state/SHA-256 digest against local bytes;
missing digest, mismatch, missing published asset or unexpected asset fails closed.
An identical input is a no-op after complete verification. Draft uploads interrupted
midway can be resumed by this state machine only with the exact same manifest/bytes.
A fresh build/run/attempt normally changes provenance and is intentionally rejected
for a reserved N, even if APK bytes happen to match. No reproducibility claim is made.

Use the separately guarded [artifact recovery workflow](../.github/workflows/mosaic-development-resume.yml)
for post-build failures; a failed overall run does not invalidate a successful build/sign
job. Original build identity is preserved rather than rebound to a new run/attempt.
The normal workflow still enforces same-run inputs. See the recovery procedure below.
Never delete the ledger to make a conflicting rebuild pass.

GitHub release asset replacement is not transactional. The publisher temporarily hides
an existing rolling release as draft, moves ONLY `develop` via the Git refs API, replaces
its two assets, verifies them, then exposes the prerelease. Existing release ID is reused.
A failed transition may leave develop unavailable; it must not serve new metadata with
old APKs. Durable immutable-build assets survive independently. In-flight old downloads
may fail during rollover and need retry; atomic availability is not claimed.

Immutability is enforced by this publisher, not a new repository ruleset. Administrators
can still alter unprotected tags/assets externally; do not do so. Existing immutable
GitHub releases cannot act as a rolling channel: the helper rejects an immutable develop
release. Before first publication, confirm repository release-immutability settings and
existing tag rules permit a mutable develop channel and creating downstream-build tags.
Do not weaken protected main or change settings automatically. External immutable-release
policy may require a separate architecture decision; no settings are changed here.

## Machine-readable manifest

`mosaic-release.json` schema 1 is canonical sorted UTF-8 JSON. Fields:

- `applicationId`, `versionName`, `versionCode`;
- `sourceSha`, `sourceTree`, `upstreamBaseline`;
- `buildWorkflow`, `buildRunId`, `buildRunAttempt`, `publication`;
- `unsignedApkSha256`, `signedApkSha256`, `signerSha256`;
- `immutableIdentity`, `rollingChannel`, `assetName`;
- `source`: full original unsigned provenance, including epoch/build time and run/attempt.

The tag embeds the same manifest bytes uploaded alongside the exact signed APK.
Publication timestamp is intentionally omitted from this deterministic identity record;
GitHub release timestamps and Actions logs record publication events separately.
The original signing policy and permanent key remain unchanged.

## Separately authorized normal publication

For a future separately authorized normal publication, wait for successful push CI on the exact main
commit to publish. Review and explicitly authorize that full SHA. Then, in PowerShell:

```powershell
# Paste the separately approved full main SHA; do not auto-follow a moving ref.
$approvedSha = '<approved-40-character-main-sha>'
gh workflow run mosaic-development-release.yml --repo constbogdan/Wholphin --ref main -f "expected_sha=$approvedSha"
```

A main advance between authorization and dispatch/build/publication causes rejection.
Honor any configured signing Environment approval. This document is the procedure,
not authorization to dispatch. No live publication occurred during implementation.

Historical bootstrap used for the successful **Mosaic 1.0.3 -> 1.0.5** acceptance
(the old binary consumed JSON and could not normalize the web URL):

```text
https://api.github.com/repos/constbogdan/Wholphin/releases/tags/develop
```

The 1.0.3 installation was updated in place through Mosaic, with state and the custom
URL preserved. Retain the accepted 1.0.5 instance for subsequent update checks.

Capture workflow/run/attempt, authoritative CI run/attempt, exact SHA/tree/version,
immutable unsigned/signed artifact IDs and digests, manifest and tag object, release IDs,
prerelease/latest behavior and asset hashes. Keep step/job logs and timings for CI,
setup/cache, Release compilation/vital checks, transport, signing/verification and upload.
Compare against the proven exercise's **16m43s build / 34s signer**, distinguishing queue
and Environment wait from execution. Construct a measured validation-overlap matrix
before CI redesign; do not infer speedups solely from total run time.

Automatic main publication remains disabled: no push, schedule or workflow_run trigger.
Live publication/device acceptance is complete; any future wiring of a successful-main
trigger to this same gate/build/shared-sign/publish flow and changes to its dispatch-only
checks still require separate authorization. Do not maintain a second publisher. Stable promotion remains separate.

References: [GitHub release REST contract](https://docs.github.com/en/rest/releases/releases),
[reusable workflow Environment secrets](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows).

## Manual post-build recovery

Unsigned recovery is LIVE VALIDATED; signed recovery remains implemented/offline-tested. Recovery uses **current protected-main tooling**
with a separately approved full execution SHA, plus the approved **original source SHA**
and immutable **artifact ID**. It never checks out or executes the old source or artifact
contents. Source must remain on the current main first-parent chain after the pinned epoch;
full history reconstructs its exact version/tree/time/upstream provenance. Original-source
and current-tooling push CI must both be successful. No normal-path gate is bypassed.

The helper validates GitHub artifact ID, repository/run ownership, canonical workflow,
manual main event, source SHA, original attempt, exact artifact name, non-expiration,
SHA-256 digest availability and successful producing job. Artifact creation must fall
within that job's timestamps. A failed overall run is allowed when its producing job
succeeded. Cross-run downloads explicitly specify the validated run ID, exact artifact
ID and repository, use a read-only token and fail on digest mismatch. Unsigned content
must match the original hash/source/version/run record and have no signatures; alignment
and SDK unsigned checks remain mandatory. Neither old source scripts nor APK code execute.

| Failure | Recovery |
| --- | --- |
| Build failed | Normal authorized build; no accepted artifact exists |
| Signing failed | `checkpoint=unsigned`: reuse successful build artifact; sign exact bytes |
| Publication failed | `checkpoint=signed`: reuse successful sign artifact; reverify and publish without re-signing |

Unsigned recovery uses the same Environment-bound signing action and pinned public
verification policy. Signed recovery has **no signing Environment or signing secrets**;
it reruns SDK signature/package/version verification and compares the complete record
before publishing. The publisher remains a separate Contents-write job. Both paths share
the normal publisher, immutable identity checks, rollback rejection and concurrency group.
There are no Gradle commands, build fallbacks, signing in the publisher or automatic triggers.

Original `source.runId` / `runAttempt`, source SHA/version and manifest remain unchanged.
`recovery.json` separately records execution SHA/run/attempt, checkpoint and original
artifact ID/digest; it is retained with the accepted Actions artifact. Recovery evidence
is not inserted into the immutable manifest, so an exact signed-artifact retry reproduces
the original ledger. Conflicting previously reserved bytes still fail closed.

Read-only audit of the reported failure confirmed:

```text
original run: 34340900095 (failure; build success, sign failure, publisher skipped)
source: 41f9f83c36b8866211c9680d3b416d5ebede4888
version: 1.0.5
unsigned artifact ID: 10099950969
archive digest: sha256:fac141c030861285ef3ca555754997bf598f1829e9743b117d84486737be1b61
created: 2026-09-09T10:42:00Z
expires: 2026-09-16T10:41:58Z
build job: 2026-09-09T10:34:06Z through 10:42:03Z, success
```

This initial metadata audit was subsequently followed by successful hosted content
checks and unsigned recovery, as recorded above. Metadata alone is not acceptance. Retention,
deletion, failed current/original CI, non-main ancestry, changed signing policy, a newer
rolling release or conflicting immutable reservation can stop recovery. None is bypassed.
The earlier blanket instruction not to reuse this artifact reflected missing recovery
implementation, not a GitHub security requirement.

After this correction is merged, wait for successful main CI and separately approve its
full execution SHA. The original recovery used the following procedure (historical reference, not
authorization to republish accepted build 5):

```powershell
$recoverySha = '<approved-full-current-main-tooling-sha>'
gh workflow run mosaic-development-resume.yml --repo constbogdan/Wholphin --ref main -f "expected_sha=$recoverySha" -f source_sha=41f9f83c36b8866211c9680d3b416d5ebede4888 -f artifact_id=10099950969 -f checkpoint=unsigned
```

For publication failure, use the same command with `checkpoint=signed`, the original
source SHA and the successful sign job's artifact ID. Both normal-development signed
artifacts and `signed-mosaic-resume-<source>-run-<id>-attempt-<attempt>` artifacts from
successful recovery sign jobs are supported. A retry of a failed publication-recovery
run can select that same original signed artifact again. The intermediate
`verified-mosaic-resume-...` transfer is not a new build/sign checkpoint.

Preserve signed artifact IDs and download/back up accepted public APK/provenance before
the seven-day retention expires. Expired Actions artifacts cannot be recovered by ID;
recovery from durable release assets needs a separately reviewed retrieval path. Do not
substitute a rebuilt or re-signed APK for an already reserved identity. Keep installed
Mosaic 1.0.5 installation and retained settings after the accepted in-place update.
