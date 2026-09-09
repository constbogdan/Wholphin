# Mosaic rolling development publication

## Automatic Development and channel migration acceptance

**COMPLETE / LIVE VALIDATED**, based on user-supplied hosted and device evidence.
PR #20 merged to protected main at `5818b605fe64fae97bdd20feed7b1df60600d08a`.
Main CI succeeded, then trusted workflow_run automatically started **Mosaic development
release #2**. No manual Development dispatch or signing Environment approval was needed.
The existing mosaic-release-signing Environment still isolates signing secrets.

| Evidence | Observed value |
| --- | --- |
| Version / immutable identity | v1.0.8 / downstream-build-8 |
| Source | `5818b605fe64fae97bdd20feed7b1df60600d08a` |
| Signed APK SHA-256 | `02498e1673326db0546d0db51879215fa322465911bcdb100828e0ed9fbb771e` |
| Build / sign / publish | 9m55s / 37s / 18s |
| Total | 11m02s |

Rolling develop updated automatically. Preserved Mosaic 1.0.5 discovered v1.0.8, displayed
correct downstream metadata and Mosaic development build downstream-build-8. The user
selected Download & Update; Mosaic downloaded the APK and Android updated it in place.
Installed v1.0.8 was confirmed, with existing application state/settings still present.
The exact stored URL `https://api.github.com/repos/constbogdan/Wholphin/releases/tags/develop`
migrated to **Update channel = Development**. Stable / Development / Custom are exposed;
Custom shows the advanced release-metadata API URL field. Fresh/default Stable remains
the implemented contract, not a separately reported fresh-install acceptance test.
The preserved device baseline is now 1.0.8; do not reset it to repeat earlier acceptance.

Discovery does not yet provide adequate proactive notification UX: normal use, leaving/
re-entering, and force-stop/reopen did not surface a proactive update message. The update
was visible in Settings/About. This acceptance proves delivery and migration, not a
working proactive notification/banner. Track the UX follow-up in the roadmap.

Development is now continuous delivery: protected main -> successful authoritative CI ->
automatic Development workflow -> Release build -> isolated signing -> verification ->
downstream-build-N -> rolling develop -> device discovery through normal checks.
Installation still requires user action. Stable promotion stays explicitly manual.
Earlier implementation-pending and manual-only checkpoints below are historical.

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

[Development workflow](../.github/workflows/mosaic-development-release.yml) now follows
successful `CI` completion through `workflow_run` (`completed`, branch main). Normal
publication needs no dispatch or SHA input: this task authorizes the guarded automatic
Development path after merge. Stable and exceptional recovery remain manual.

All jobs require canonical constbogdan/Wholphin, protected refs/heads/main and successful
push-CI provenance whose head repository/branch/SHA match the publication run's exact SHA.
The helper checks GitHub's event payload, CI path/ID, run ID and attempt against the API's
latest successful exact-source push CI and required Full validation job, before building
and again before publishing. Checkout always uses github.sha, never a substituted PR or
input SHA. The exact-SHA manual development dispatch remains available but is not needed
for normal publication.

GitHub workflow_run uses the default-branch SHA, which can differ from the completed CI
head SHA. We deliberately require equality and protected main tip. Superseded runs are
skipped by job guards or fail closed at the API gate; the newer main's successful CI
supplies the next eligible event. Main advancing during build can prevent publication;
artifacts remain available for authorized recovery. Shared publisher concurrency does not
cancel active releases; GitHub can coalesce pending runs. This does not promise a release
for every intermediate commit during rapid merges.

See [GitHub workflow_run semantics](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_run).
This privileged event must never accept PR/fork/manual CI as authority. No CI artifact
is consumed as publication authority; only authenticated main source is built.

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
| Stable channel | Separate manual `mosaic-v1.0.N` promotion | Exact signed bytes; see [Stable contract](MOSAIC_STABLE.md) |

Both development release kinds use `prerelease: true` and `make_latest: false`. The updater parses
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

## Exceptional manual development dispatch

Normal Development is automatic after successful main CI. Only for an exceptional explicitly
authorized dispatch (not a post-build retry), wait for successful exact-main push CI and approve
that full SHA. The retained command is:

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
URL preserved. That accepted 1.0.5 instance has now advanced to 1.0.8 in place; retain the current 1.0.8 baseline.

Capture workflow/run/attempt, authoritative CI run/attempt, exact SHA/tree/version,
immutable unsigned/signed artifact IDs and digests, manifest and tag object, release IDs,
prerelease/latest behavior and asset hashes. Keep step/job logs and timings for CI,
setup/cache, Release compilation/vital checks, transport, signing/verification and upload.
Compare against the proven exercise's **16m43s build / 34s signer**, distinguishing queue
and Environment wait from execution. Construct a measured validation-overlap matrix
before CI redesign; do not infer speedups solely from total run time.

Automatic main publication via successful CI workflow_run is now COMPLETE / LIVE VALIDATED.
It uses the same gate/build/shared-sign/publish flow; do not maintain a second publisher.
Stable remains separate and manual. The older dispatch-only boundary is superseded.

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

## First automatic Development acceptance (completed; retained procedure)

After review/merge, observe main push CI and the automatically created Mosaic development
release run. Do not dispatch another run. Record linked CI ID/attempt and common full SHA,
build/sign/publish results, immutable artifact IDs, version, fingerprint and signed hash.
Confirm downstream-build-N and develop expose identical APK/manifest bytes as prereleases;
Stable/latest must remain unchanged. CI re-runs after publication are not build recovery:
different run provenance or bytes cannot replace an existing build identity. Use existing
unsigned/signed recovery for post-build failures; recovery recognizes automatic producers
without making recovery itself automatic. Signing and publishing retries perform no Gradle.

Keep emulator 1.0.5 and its stored develop API URL intact. With automatic checks enabled,
verify discovery of the newer Development APK, in-app download/install, post-update launch,
migration to Update channel = Development and preserved settings/data. Do not reset or
reinstall using ADB. Discovery uses existing app checks, not server-pushed installation.
The selector is already merged and will be in the next build; no app changes are made here.

No new secrets/Environment/permissions are required. Existing Environment branch rules
must admit main; any required reviewers or wait timers still apply and can pause signing.
Fully unattended execution depends on a compatible existing approval policy. External
settings were not inspected or changed; no bypass is added. Existing tag/release rules must
permit the current publisher. The separate Release build still follows ordinary Debug CI;
measured item-6 validation/artifact-reuse optimization remains pending.
