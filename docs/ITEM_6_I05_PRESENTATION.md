# I05 delivery presentation and compatibility ledger

Baseline: `27f264ee` before I05 edits. Inventory captured before implementation.

## Before-edit name inventory

SAFE COSMETIC: no machine lookup found. MACHINE CONTRACT: direct lookup/identity.
COMPATIBILITY-SENSITIVE: installed client, historical artifact or authentication dependency.
DEFER: inherited automation or separate migration.

### ci.yml

| Surface | Current value | Classification / consumer |
| --- | --- | --- |
| Workflow path | `.github/workflows/ci.yml` | MACHINE CONTRACT: workflow refs, event/artifact provenance; retain |
| Workflow display | CI | MACHINE CONTRACT: CI workflow_run trigger |
| Run name | absent | SAFE COSMETIC: trigger-time identity only |
| Job `full-validation` | Full validation | MACHINE CONTRACT: API job authentication; preserve visible name |
| Step in `full-validation` | `Checkout the code` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `full-validation` | `Setup Python` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `full-validation` | `Classify PR validation` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `full-validation` | `Run changed-range pre-commit` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `full-validation` | `Run repository-wide pre-commit` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `full-validation` | `Test hosted upstream safety and version allocation (offline fixtures)` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `full-validation` | `Classify complete unpublished Development range` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `full-validation` | `Setup` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `full-validation` | `Run full validation` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `full-validation` | `Run targeted Android validation` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `full-validation` | `Build authoritative unsigned Release after validation` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `full-validation` | `Prepare authoritative unsigned Release artifact` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `full-validation` | `Upload authoritative unsigned Release artifact` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `full-validation` | `Locate validated PR universal Debug APK` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `full-validation` | `Upload PR test APK` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `full-validation` | `Summarize PR test APK` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `full-validation` | `Summarize PR validation policy` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `full-validation` | `Upload test diagnostics` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |

### main.yml

| Surface | Current value | Classification / consumer |
| --- | --- | --- |
| Workflow path | `.github/workflows/main.yml` | MACHINE CONTRACT: workflow refs, event/artifact provenance; retain |
| Workflow display | Development build | DEFER: inherited publisher |
| Run name | absent | DEFER |
| Job `build` | build | DEFER |
| Step in `build` | `Checkout the code` | DEFER |
| Step in `build` | `Setup` | DEFER |
| Step in `build` | `Get version names` | DEFER |
| Step in `build` | `Build release app` | DEFER |
| Step in `build` | `Verify signatures` | DEFER |
| Step in `build` | `Copy APK to shorter names` | DEFER |
| Step in `build` | `Checksums` | DEFER |
| Step in `build` | `Upload mapping files` | DEFER |
| Step in `build` | `Delete ${{ env.TAG_NAME }} tag and release` | DEFER |

### mosaic-development-release.yml

| Surface | Current value | Classification / consumer |
| --- | --- | --- |
| Workflow path | `.github/workflows/mosaic-development-release.yml` | MACHINE CONTRACT: workflow refs, event/artifact provenance; retain |
| Workflow display | Mosaic development release | SAFE COSMETIC: no display-name authenticator |
| Run name | absent | SAFE COSMETIC: trigger-time identity only |
| Job `classify` | classify | SAFE COSMETIC display; internal ID/dependencies preserved |
| Step in `classify` | `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `classify` | `Classify complete unpublished Development range` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Job `sign` | sign | MACHINE CONTRACT: API job authentication; preserve visible name |
| Step in `sign` | `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `actions/setup-java@b6effb05e454b25005698d916606bdc6ffcbf961` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `android-actions/setup-android@40fd30fb8d7440372e1316f5d1809ec01dcd3699` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `Require exact main-CI artifact ID` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `Verify trusted unsigned input` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `Sign exact input without rebuilding` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `Verify signed identity and unchanged payload` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `Signing exercise summary` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Job `publish` | publish | SAFE COSMETIC display; internal ID/dependencies preserved |
| Step in `publish` | `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `publish` | `Require exact signing-job artifact ID` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `publish` | `actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `publish` | `Validate manifest before publication credential use` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `publish` | `Publish verified development bytes` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |

### mosaic-development-resume.yml

| Surface | Current value | Classification / consumer |
| --- | --- | --- |
| Workflow path | `.github/workflows/mosaic-development-resume.yml` | MACHINE CONTRACT: workflow refs, event/artifact provenance; retain |
| Workflow display | Mosaic development resume | SAFE COSMETIC: no display-name authenticator |
| Run name | absent | SAFE COSMETIC: trigger-time identity only |
| Job `sign` | sign | MACHINE CONTRACT: API job authentication; preserve visible name |
| Step in `sign` | `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `actions/setup-java@b6effb05e454b25005698d916606bdc6ffcbf961` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `android-actions/setup-android@40fd30fb8d7440372e1316f5d1809ec01dcd3699` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `Authenticate original build artifact and source` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `Require exact build-job artifact ID` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `Verify trusted unsigned input` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `Sign exact input without rebuilding` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `Verify signed identity and unchanged payload` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `Preserve original identity and record recovery execution` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `Signing exercise summary` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Job `recover_signed` | recover_signed | SAFE COSMETIC display; internal ID/dependencies preserved |
| Step in `recover_signed` | `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `recover_signed` | `actions/setup-java@b6effb05e454b25005698d916606bdc6ffcbf961` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `recover_signed` | `android-actions/setup-android@40fd30fb8d7440372e1316f5d1809ec01dcd3699` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `recover_signed` | `Authenticate original build artifact and source` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `recover_signed` | `Require exact build-job artifact ID` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `recover_signed` | `actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `recover_signed` | `Reverify signed checkpoint without a signing key` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `recover_signed` | `actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Job `publish` | publish | SAFE COSMETIC display; internal ID/dependencies preserved |
| Step in `publish` | `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `publish` | `Require exact signing-job artifact ID` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `publish` | `actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `publish` | `Publish existing verified identity without rebuild or resign` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |

### mosaic-signing-exercise.yml

| Surface | Current value | Classification / consumer |
| --- | --- | --- |
| Workflow path | `.github/workflows/mosaic-signing-exercise.yml` | MACHINE CONTRACT: workflow refs, event/artifact provenance; retain |
| Workflow display | Mosaic signing exercise | SAFE COSMETIC: no display-name authenticator |
| Run name | absent | SAFE COSMETIC: trigger-time identity only |
| Job `build` | build | SAFE COSMETIC display; internal ID/dependencies preserved |
| Step in `build` | `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `build` | `./.github/actions/setup` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `build` | `pre-commit/action@2c7b3805fd2a0fd8c1884dcaebf91fc102a13ecd` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `build` | `Offline acceptance` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `build` | `Full Debug validation` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `build` | `Build unsigned Release after validation` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `build` | `Prepare exact universal unsigned input` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `build` | `actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Job `sign` | sign | SAFE COSMETIC display; internal ID/dependencies preserved |
| Step in `sign` | `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `actions/setup-java@b6effb05e454b25005698d916606bdc6ffcbf961` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `android-actions/setup-android@40fd30fb8d7440372e1316f5d1809ec01dcd3699` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `Require exact build-job artifact ID` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `Verify trusted unsigned input` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `Sign exact input without rebuilding` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `Verify signed identity and unchanged payload` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `sign` | `Signing exercise summary` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |

### mosaic-stable-promotion.yml

| Surface | Current value | Classification / consumer |
| --- | --- | --- |
| Workflow path | `.github/workflows/mosaic-stable-promotion.yml` | MACHINE CONTRACT: workflow refs, event/artifact provenance; retain |
| Workflow display | Mosaic stable promotion | SAFE COSMETIC: no display-name authenticator |
| Run name | absent | SAFE COSMETIC: trigger-time identity only |
| Job `verify` | verify | SAFE COSMETIC display; internal ID/dependencies preserved |
| Step in `verify` | `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `verify` | `actions/setup-java@b6effb05e454b25005698d916606bdc6ffcbf961` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `verify` | `android-actions/setup-android@40fd30fb8d7440372e1316f5d1809ec01dcd3699` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `verify` | `Authenticate immutable development source and download exact bytes` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `verify` | `Fresh public certificate package and version verification` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `verify` | `Require unchanged development manifest and exact signed hash` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `verify` | `actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Job `publish` | publish | SAFE COSMETIC display; internal ID/dependencies preserved |
| Step in `publish` | `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `publish` | `Require exact successful verification artifact ID` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `publish` | `actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `publish` | `Promote exact verified bytes to immutable stable and latest` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |

### release.yml

| Surface | Current value | Classification / consumer |
| --- | --- | --- |
| Workflow path | `.github/workflows/release.yml` | MACHINE CONTRACT: workflow refs, event/artifact provenance; retain |
| Workflow display | Create release | DEFER: inherited publisher |
| Run name | absent | DEFER |
| Job `publish` | publish | DEFER |
| Step in `publish` | `Checkout the code` | DEFER |
| Step in `publish` | `Setup` | DEFER |
| Step in `publish` | `Build app` | DEFER |
| Step in `publish` | `Verify signatures` | DEFER |
| Step in `publish` | `Copy APK to shorter names` | DEFER |
| Step in `publish` | `Checksums` | DEFER |
| Step in `publish` | `Upload AAB` | DEFER |
| Step in `publish` | `Upload mapping files` | DEFER |
| Step in `publish` | `Create GitHub release` | DEFER |

### upstream-sync.yml

| Surface | Current value | Classification / consumer |
| --- | --- | --- |
| Workflow path | `.github/workflows/upstream-sync.yml` | MACHINE CONTRACT: workflow refs, event/artifact provenance; retain |
| Workflow display | Upstream synchronization | SAFE COSMETIC: no display-name authenticator |
| Run name | absent | SAFE COSMETIC: trigger-time identity only |
| Job `observe` | observe | SAFE COSMETIC display; internal ID/dependencies preserved |
| Step in `observe` | `Checkout trusted workflow implementation` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `observe` | `Observe and attempt isolated integration (read-only token)` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `observe` | `Retain complete observation` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Job `publish` | publish | SAFE COSMETIC display; internal ID/dependencies preserved |
| Step in `publish` | `Checkout trusted workflow implementation` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `publish` | `Mint repository-scoped publication token` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `publish` | `Recheck exact inputs and publish or record blocked attempt` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |
| Step in `publish` | `Retain complete outcome` | SAFE COSMETIC; step IDs/outputs remain MACHINE CONTRACT |


## Other names and consumers inventoried before editing

| Surface | Current names | Classification and decision |
| --- | --- | --- |
| Summary headings | Mosaic Development eligibility; Mosaic development release verified; Mosaic signing exercise verified (Development/recovery/diagnostic); Mosaic PR validation; PR test APK available; Upstream observation | SAFE COSMETIC. Publish/skip/recovery/promotion lead with outcome. Diagnostic alone keeps diagnostic wording. PR headings retained. |
| Release titles | v1.0.N for rolling, immutable and Stable | COMPATIBILITY-SENSITIVE. UpdateChecker parses API name through Version.tryFromString/matchEntire; publisher, eligibility and Stable also validate exact title. Preserve. Put branded channel titles in bodies. |
| Release bodies | Mosaic development build + source/hash; Mosaic stable + promoted source/hash | SAFE COSMETIC for future publication, preserving provenance text. Historical changes DEFER until separately authorized. |
| Public APK | Wholphin-release.apk | COMPATIBILITY-SENSITIVE. UpdateChecker ASSET_NAME/preferredNames and exact two-asset publisher/Stable checks; retain. |
| Transport files | unsigned.apk, signed.apk, Mosaic-release.apk, provenance.json, verification.json, recovery.json | MACHINE CONTRACT: signer, public verifier, recovery and publisher; retain. |
| Manifest | mosaic-release.json, schema/source/run/signer/package/version fields | MACHINE CONTRACT: immutable annotated tag and exact asset digest verification; retain. |
| Tags | develop, downstream-build-N, mosaic-v1.0.N | MACHINE CONTRACT: updater resolver, ledger, eligibility, Stable and recovery; retain. |
| Local tasks | Mosaic: Prepare PR; Mosaic: Validate Fast/Standard/Full | SAFE COSMETIC but already accurate; preserve commands/parameters, prepare-pr/validate-local names, stage labels and logs. |
| Shared action labels | Setup / Setup the environment; Sign exact Mosaic APK / SDK signing only | SAFE COSMETIC but accurate; no action path or signer behavior change. |
| Inherited names and assets | Development build, Create release, mapping, AAB, upstream aliases/titles | DEFER: no inherited automation edits or removals. |

## Artifact compatibility map

| Current artifact name | Human meaning | Machine consumers | Safe to rename? | Proposed name |
| --- | --- | --- | --- | --- |
| unsigned-mosaic-main-ci-<version>-<sha>-run-<run>-attempt-<attempt> | Authoritative main unsigned Release | ci_artifact_name/trusted_ci_artifact; recovery | No, MACHINE CONTRACT | Preserve; label upload clearly |
| signed-mosaic-development-<version>-<sha>-run-<run>-attempt-<attempt> | Verified Development APK | Recovery artifact_metadata, signing-job immutable ID | No, COMPATIBILITY-SENSITIVE | Preserve |
| unsigned/signed-mosaic-signing-exercise-<version>-<sha>-run-<run>-attempt-<attempt> | Diagnostic transport; legacy Development artifacts | artifact_name, legacy recovery authentication | No, COMPATIBILITY-SENSITIVE | Preserve historical names; no current production generation uses this prefix |
| signed-mosaic-resume-<source>-run-<run>-attempt-<attempt> | Signed recovery checkpoint | artifact_metadata and original run/job checks | No, MACHINE CONTRACT | Preserve |
| verified-mosaic-resume-<source>-run-<run>-attempt-<attempt> | Reverified signed recovery transport | Current job output artifact ID | Defer, COMPATIBILITY-SENSITIVE | Preserve |
| stable-downstream-build-N-run-<run>-attempt-<attempt> | Verified Stable transport | Verify output immutable artifact ID | Defer, COMPATIBILITY-SENSITIVE | Preserve |
| wholphin-pr-<PR>-<head>-run-<run>-attempt-<attempt> | PR universal Debug APK | CI summary/retrieval docs | Defer, COMPATIBILITY-SENSITIVE | Preserve |
| default-debug-test-results | Failure diagnostics | Operator download | SAFE COSMETIC; no benefit now | Preserve |
| upstream-observation-<attempt>, upstream-outcome-<attempt> | Sync journal JSON | Operators/artifact evidence | Defer to I06 | Preserve |
| mapping, AAB | Inherited build diagnostics/bundles | Guarded upstream workflows | DEFER | Preserve |
| New: mapping-mosaic-main-ci-<version>-<sha>-run-<run>-attempt-<attempt> | Main Release R8 mapping plus identity/hash | Actions diagnostic only; no updater or recovery lookup | SAFE COSMETIC, new distinct prefix | Add; seven days, text compression 6 |

## Implemented I05 decisions

| Before | After | Run-name identity available at trigger time |
| --- | --- | --- |
| CI | CI (unchanged) | PR number + head branch; manual ref; blank push fallback preserves GitHub's native merge/push title |
| Mosaic development release | Mosaic — Development Release | Triggering CI `display_title`, then CI run number, then source SHA; manual runs use the approved SHA |
| Mosaic development resume | Mosaic — Development Recovery | Recover unsigned/signed artifact ID and original source SHA |
| Mosaic stable promotion | Mosaic — Stable Promotion | Stable · from approved downstream-build-N |
| Mosaic signing exercise | Mosaic — Signing Diagnostic | Diagnose signing from approved source SHA |
| Upstream synchronization | Upstream — Synchronization | Observe upstream and scheduled/manual event type |

The human-first follow-up labels PR validation as `PR #N · <head branch>`, while the CI
push expression intentionally resolves to whitespace so GitHub retains its native merge/push
title. Manual CI uses `Validate · <ref>`. Development reuses the triggering CI
`display_title`, falling back to the truthful CI run number and then source SHA; manual
Development uses its approved SHA. Raw commit-message text is not interpolated. Stable uses
its already-approved immutable build input. No fabricated Development build number, new API
lookup or dispatch handoff is introduced. Outcome/version remains in the summary, and Actions
still supplies its own success/failure/skipped status icon. The blank push fallback requires
natural hosted confirmation; if GitHub does not preserve its documented native-title fallback,
remove CI's custom `run-name` rather than parsing merge text.

Job display names now explain classification, publication, Stable verification/promotion,
recovery verification/publication, diagnostic build/sign and Sync observe/publish duties.
Internal IDs, `needs`, outputs and authority gates are preserved. Development and recovery
`sign` stay unchanged even as visible names: `mosaic_resume.successful_job` authenticates
those names through the API. CI's `Full validation` and historical `build` / `sign / sign`
acceptance remain intact. Step labels and summaries improve clarity around those contracts.

Production signing says “Mosaic signing verified.” The diagnostic explicitly reports no
GitHub Release publication or Stable/Development mutation. Failure-only steps identify the
failed stage and avoid claiming a publication completed. Final Published/Promoted/Recovered
summaries are appended only after the existing publisher/postcondition path returns.
Recovery reports checkpoint, input artifact, original source/build run, recovery tooling
source and execution run separately, and confirms zero Gradle work.

Non-APK eligibility leads with Skipped, relevance/risk/count and build/sign/publish not
required, while preserving protected-main validation. Its compare URL uses the authenticated
published source SHA and current source SHA, never moving tags. A small Development
explanation job runs only for protected downstream-main triggers rejected by the existing
job guard: failed/non-push CI, wrong origin, superseded SHA or mismatched manual approval.
It has no checkout, credentials, outputs, API calls or downstream dependencies; it explains
the existing decision rather than making it. Normal eligible runs allocate no runner for
that job. Later main-tip races still fail closed through existing authentication and logs.

Sync receives presentation-only headings for no delta, ready/existing/published PR,
semantic block and infrastructure/publication error. Full escaped JSON, machine outcomes,
exit codes, schedules, issue/PR logic, permissions and conflict authority are unchanged.
OperationError remains a Blocked subclass; it changes the human diagnosis only. I06's
FOLLOW / REVIEW / DOWNSTREAM-OWNED proposal is unchanged and unimplemented.

## Release titles, bodies and APK migration

The requested titles `Mosaic v1.0.N — Stable/Development/Development Build N` are implemented
as **body headings**, not API release names. `UpdateChecker.getRelease` reads JSON `name`,
passes it to `Version.tryFromString`, and that parser matches the entire numeric version.
Changing the API name would make installed clients fail to read the release. Publisher,
eligibility and Stable also explicitly validate `v1.0.N`. All API names remain numeric.

New bodies distinguish rolling preview, immutable archive and Stable exact-byte promotion;
retain version/build/source/hash/manifest information; link the exact source commit; and
provide channel/install guidance and APK download links. Immutable bodies use immutable
build download URLs. Rolling download links intentionally track that channel; compare
links never use moving tags. No AI-generated changelog or new API call is needed. Already
published immutable/Stable bodies are not edited on retry; I05 affects future publication.

APK migration is **DEFERRED**. `getDownloadUrl` prefers the Wholphin prefix and
`Wholphin-release.apk`; the published manifest's `assetName` and strict two-asset checks
in Development/Stable also bind that name. Simply adding a third alias would fail current
inventory authentication, and rewriting an immutable manifest would violate its ledger.

Concrete future migration sequence:

1. Define a new, backward-readable asset-inventory/manifest policy without rewriting old
   annotated tags, manifests or releases. Enumerate current/legacy recovery and promotion
   consumers and any older tooling still usable for retries.
2. Ship an application update that prefers Mosaic naming with Wholphin fallback, and
   separately design a version-discovery fallback before any API title migration. Keep
   numeric API names and the legacy installer available to old clients throughout.
3. Atomically update publisher, eligibility, Stable, recovery and tests to accept the
   precise approved dual-alias set with identical APK digest/size/bytes, rejecting unexpected
   extras. Preserve old two-asset inputs and old manifest `assetName` interpretation.
4. Test old and new installed versions, both aliases, missing preferred alias fallback,
   immutable retries, partial-upload recovery, Stable exact-byte promotion and channel
   migration. No rebuild or resigning to create an alias.
5. Retire the legacy alias only under a separate approved compatibility policy. There is
   no safe date inferred merely from publishing one new app build. No such retirement is I05.

## Mapping diagnostic decision

Implemented as a small addition to the existing authoritative CI Release path. After main
Release preparation/upload, copy `app/build/outputs/mapping/defaultRelease/mapping.txt`
into a separate runner-temporary directory. `mapping.json` records the mapping SHA-256,
`downstream-build-N`, producer workflow and the already prepared unsigned source record
(version, source/tree, build time, run/attempt, unsigned APK hash). No extra Gradle command.

Upload `mapping-${steps.main-release.outputs.name}` with seven-day retention and text
compression 6. It has no signing/updater/recovery consumer, does not enter the unsigned
APK transport directory, and is never a public Release asset. Missing/empty mapping fails
the diagnostic step visibly rather than silently claiming retained evidence; since CI is
authoritative, such a failure also prevents normal release consumption. This is an explicit
new diagnostic completeness check. The next natural Release build must verify the mapping
path and name on the hosted runner. Existing minification settings remain unchanged.

## Historical release inspection and one-time backfill plan

Read-only GitHub inspection on 2026-09-10 found the following actual release IDs. All
currently have API title `v1.0.N`, two assets (`Wholphin-release.apk`, `mosaic-release.json`),
and `draft=false`. Inspected public manifests for builds 5, 8, 9 and current 11 all use
schema 1 and the legacy asset name. Build 11 records `.github/workflows/ci.yml`; older
records name `.github/workflows/mosaic-development-release.yml`. Preserve that distinction.

| Release ID | Tag | Title | State / backfill candidate |
| --- | --- | --- | --- |
| 385512947 | mosaic-v1.0.5 | v1.0.5 | Stable; body-only candidate |
| 385461798 | downstream-build-5 | v1.0.5 | Immutable identity archive; body-only candidate |
| 385556133 | downstream-build-8 | v1.0.8 | Immutable identity archive; body-only candidate |
| 385612826 | downstream-build-9 | v1.0.9 | Immutable identity archive; body-only candidate |
| 385869688 | downstream-build-11 | v1.0.11 | Immutable identity archive; body-only candidate |
| 385461835 | develop | v1.0.11 | Mutable channel; body-only candidate bound to inspected source |

The API currently reports `immutable=false`; this does not remove Mosaic's own immutable
identity/byte guarantees. Current rolling/immutable build 11 APK digests agree at
`98472b4e2537669b0894c6cf49ebc0c20229c633307f82b11da8e8e265d1c941`, and manifest asset digests
agree at `0399ebb4bcf67f78ab24c0954c10eb270ebe804476d6b24cfbcec45a9169e10e`. Stable/build 5
APK digests also agree. Inspection did not download APKs or reverify signatures; it does
not replace the recorded release acceptance.

No historical changes are authorized or performed. Proposed one-time process:

1. Refresh the explicitly selected release IDs and `/releases/latest`, resolve exact tag
   objects/target/source, read canonical manifests and inventory asset IDs/sizes/digests.
   Authenticate each manifest against its annotated identity before generating prose.
2. Save a local before snapshot with old title/body, source, flags/latest identity and
   assets. Generate a reviewable per-ID body-only diff with the corresponding rolling,
   immutable or Stable template. Use old authenticated source versions, not current HEAD.
3. Preserve title `v1.0.N`. Branded API title backfill is unsafe for installed clients and
   current tool checks; defer it even if a GitHub metadata edit itself is technically possible.
4. Obtain explicit authorization for those exact body diffs. A future tool should default
   to dry-run with no mutation method invoked; no backfill executable is added by I05.
5. Re-read and refuse drift, especially a newer `develop` target. Update body metadata
   only; explicitly preserve existing latest/prerelease/draft semantics according to the
   API contract. Never create/delete tags, upload/delete assets, change targets, rewrite
   manifests or touch APK bytes. Verify latest and every snapshotted non-body field after
   each write; stop on any discrepancy rather than continuing blindly.
6. Retain before/after evidence and body-only restoration data. This is editorial recovery,
   not I07 release rollback; restoring prose must not move release/channel state.

Broader README/fork presentation remains deferred. Preserve the agreed direction: Mosaic
is a personal downstream Wholphin fork and actively encourages useful Mosaic features,
fixes and designs to be adopted by Wholphin or other relevant open-source projects.

## Validation and natural acceptance

The offline presentation fixtures cover preserved updater titles/assets, distinct release
bodies with provenance, no historical backfill on retry, publication/recovery/Stable
summaries, 24-path non-APK output, actual execution of the guard-summary script, escaped
Sync diagnostics, current job/workflow names, and mapping bytes/identity/hash/missing input.
Existing release/recovery/signing/Stable/Sync tests remain authoritative for trust behavior.

The human-first lifecycle-label follow-up is live validated through PR #30:

``` text
PR:           PR #30 · chore/item-6-lifecycle-labels
Main:         Merge pull request #30 from constbogdan/chore/item-6-lifecycle-labels
Development:  Development · Merge pull request #30 from constbogdan/chore/item-6-lifecycle-labels
```

This proves that the blank protected-main `run-name` fallback preserves GitHub's native merge
title and that Development receives the triggering CI `display_title`. `CI` and `Full
validation` remain unchanged machine contracts. The inherited upstream `Development build`
still appears as a separate one-second skipped row; its downstream ownership/removal decision
is deferred to I06. Stable remains configured as `Stable · from downstream-build-N`, but
Stable, recovery and signing-diagnostic labels have not yet run naturally and are not claimed
as live validated. SHA remains a fallback only where no better human-readable identity exists.

Natural acceptance remains pending for the other I05 delivery surfaces:

- Next non-APK Development range: truthful Skipped summary and count/risk; no Release/sign/publish.
- Next real APK Development: source-based run row, main mapping download and JSON binding,
  signed/Published summaries, body headings and unchanged numeric title/updater assets.
- Next Stable promotion: manual authorization, Promoted summary and exact Development bytes.
- Next real recovery: unsigned/signed checkpoint, original source/build versus recovery run,
  no Gradle, no misleading exercise text.
- Next needed signing diagnostic: diagnostic-only name/summary, no channel/release mutation.
- Next natural Sync observation: useful ready/no-delta/blocked/error heading, unchanged JSON,
  exit code, issue/PR behavior and authority.

Do not manufacture a release, recovery, diagnostic or Sync delta for presentation testing.
No I06/I07 work, external writes, staging, commits, pushes or dispatches are part of I05.

## Validation result and separate known limitation

Full offline suite: 135 tests, 134 passed and the existing Windows executable-bit fixture
skipped. The final ten focused I05 tests passed after the summary formatter was kept in
its existing Sync owner. Changed-file pre-commit, YAML parsing, UTF-8 and link checks passed.
A structured baseline comparison confirmed unchanged triggers, permissions/concurrency,
existing job guards/dependencies/outputs and action inputs/artifact names. Application code,
inherited publishers, composite actions, local task commands and allocator were untouched.

Separate pre-existing Stable limitation: verify_manifest defaults reconstructed buildWorkflow
to the legacy Development producer. A valid fixture changed only to main-CI buildWorkflow
is rejected. I05 preserves that function and authorization semantics; the handoff records
the required separately scoped producer-compatibility fix before main-CI Stable promotion.
Earlier Stable build-5 live acceptance does not cover main-CI-produced versions.

## Files changed

- [.github/workflows/ci.yml](../.github/workflows/ci.yml)
- [.github/workflows/mosaic-development-release.yml](../.github/workflows/mosaic-development-release.yml)
- [.github/workflows/mosaic-development-resume.yml](../.github/workflows/mosaic-development-resume.yml)
- [.github/workflows/mosaic-signing-exercise.yml](../.github/workflows/mosaic-signing-exercise.yml)
- [.github/workflows/mosaic-stable-promotion.yml](../.github/workflows/mosaic-stable-promotion.yml)
- [.github/workflows/upstream-sync.yml](../.github/workflows/upstream-sync.yml)
- [.gitignore](../.gitignore)
- [docs/CODEX_HANDOFF.md](CODEX_HANDOFF.md)
- [docs/ITEM_6_CONSOLIDATION_CHECKLIST.md](ITEM_6_CONSOLIDATION_CHECKLIST.md)
- [docs/ITEM_6_I05_PRESENTATION.md](ITEM_6_I05_PRESENTATION.md)
- [docs/ITEM_6_UPSTREAM_AUTOMATION_AUDIT.md](ITEM_6_UPSTREAM_AUTOMATION_AUDIT.md)
- [docs/MOSAIC_DEVELOPMENT_RELEASE.md](MOSAIC_DEVELOPMENT_RELEASE.md)
- [docs/MOSAIC_SIGNING.md](MOSAIC_SIGNING.md)
- [docs/MOSAIC_STABLE.md](MOSAIC_STABLE.md)
- [scripts/hosted_upstream.py](../scripts/hosted_upstream.py)
- [scripts/mosaic_delivery_output.py](../scripts/mosaic_delivery_output.py)
- [scripts/mosaic_development_release.py](../scripts/mosaic_development_release.py)
- [scripts/mosaic_resume.py](../scripts/mosaic_resume.py)
- [scripts/mosaic_signing_exercise.py](../scripts/mosaic_signing_exercise.py)
- [scripts/mosaic_stable.py](../scripts/mosaic_stable.py)
- [scripts/mosaic_validation_policy.py](../scripts/mosaic_validation_policy.py)
- [scripts/test_mosaic_delivery_output.py](../scripts/test_mosaic_delivery_output.py)
