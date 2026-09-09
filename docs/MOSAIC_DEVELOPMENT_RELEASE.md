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
3. Sign: both the original exercise and the publisher call the same
   [isolated signer](../.github/workflows/mosaic-isolated-sign.yml). Its protected
   `mosaic-release-signing` Environment retains the existing four secrets. Public input,
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

The shared signer retains the proven signing commands and isolation; extraction and
publication integration still require hosted acceptance. Seven-day unsigned/signed
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

Do not use GitHub's rerun-failed-jobs as a recovery shortcut: current run-attempt binding
rejects old artifacts. Before reservation, rerun the entire workflow after exact-SHA
reauthorization. After reservation, preserve original artifacts and public state; stop
for a separately reviewed recovery using exact accepted bytes, or publish a newer
protected-main version. This task does not provide a user-selected artifact recovery
bypass. Never delete the ledger to make a conflicting rebuild pass.

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
