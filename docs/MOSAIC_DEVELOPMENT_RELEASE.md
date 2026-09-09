# Mosaic rolling development publication

Status: **IMPLEMENTED / LIVE PUBLICATION PENDING**. Automatic publication and stable
promotion remain disabled. Permanent signing is live-validated; updater routing is
merged and awaits a real release. Live device in-place update acceptance is NEXT after
the separately authorized first publication. Preserve installed Mosaic 1.0.3 unchanged.

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
publication integration still requires hosted acceptance. Secret presence checks report
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

## Separately authorized first live run

After this branch is reviewed and merged, wait for successful push CI on the exact main
commit to publish. Review and explicitly authorize that full SHA. Then, in PowerShell:

```powershell
# Paste the separately approved full main SHA; do not auto-follow a moving ref.
$approvedSha = '<approved-40-character-main-sha>'
gh workflow run mosaic-development-release.yml --repo constbogdan/Wholphin --ref main -f "expected_sha=$approvedSha"
```

A main advance between authorization and dispatch/build/publication causes rejection.
Honor any configured signing Environment approval. This document is the procedure,
not authorization to dispatch. No live publication occurred during implementation.

On installed **Mosaic 1.0.3**, enter this exact custom Update URL for the later authorized
in-place acceptance (the old binary consumes JSON and cannot normalize the web URL):

```text
https://api.github.com/repos/constbogdan/Wholphin/releases/tags/develop
```

Keep 1.0.3 installed; do not uninstall/reset data or replace it with Debug. Collect:
1.0.3 version/settings baseline, develop JSON name/alias, downloaded hash, certificate,
Android in-place install result, new version and preserved settings/data. Signing
acceptance alone does not establish this updater acceptance.

Capture workflow/run/attempt, authoritative CI run/attempt, exact SHA/tree/version,
immutable unsigned/signed artifact IDs and digests, manifest and tag object, release IDs,
prerelease/latest behavior and asset hashes. Keep step/job logs and timings for CI,
setup/cache, Release compilation/vital checks, transport, signing/verification and upload.
Compare against the proven exercise's **16m43s build / 34s signer**, distinguishing queue
and Environment wait from execution. Construct a measured validation-overlap matrix
before CI redesign; do not infer speedups solely from total run time.

Automatic main publication remains disabled: no push, schedule or workflow_run trigger.
After live publication/device acceptance, separately authorize wiring a successful-main
trigger to this same gate/build/shared-sign/publish flow and updating its dispatch-only
checks. Do not maintain a second publisher. Stable promotion remains separate.

References: [GitHub release REST contract](https://docs.github.com/en/rest/releases/releases),
[reusable workflow Environment secrets](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows).

## Manual post-build recovery

Implemented, pending live acceptance. Recovery uses **current protected-main tooling**
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

There is no metadata-level blocker to reusing this artifact. Its APK/provenance/digest
must still pass the hosted content checks; metadata alone is not acceptance. Retention,
deletion, failed current/original CI, non-main ancestry, changed signing policy, a newer
rolling release or conflicting immutable reservation can stop recovery. None is bypassed.
The earlier blanket instruction not to reuse this artifact reflected missing recovery
implementation, not a GitHub security requirement.

After this correction is merged, wait for successful main CI and separately approve its
full execution SHA. To recover the reported unsigned artifact (do not run without that
authorization):

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
Mosaic 1.0.3 unchanged until the separately authorized in-place updater acceptance.
