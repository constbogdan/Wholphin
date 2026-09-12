# Item 6 upstream automation audit

> Historical audit: the Mosaic Development Release and Development Recovery workflows inventoried
> below were later removed after native failed-job rerun replaced their remaining responsibilities.
> T0-1 CP2 subsequently removed the guarded inherited `main.yml` and `release.yml` workflows as
> explicit downstream-owned absences. Baseline T0 does not support their historical store/AAB
> distribution capability. The pinned inventory below remains evidence, not current workflow state.

Analysis checkpoint, 2026-09-10. Governing tracker: [Item 6 consolidation checklist](ITEM_6_CONSOLIDATION_CHECKLIST.md).
This inventory began read-only. I05 presentation and I06 ownership-aware Sync were subsequently
authorized and implemented separately; neither checkpoint removed inherited automation at that
time. T0-1 CP2 made the later removal decision recorded above.

Subsequent explicitly authorized I05 implementation is recorded in the
[presentation ledger](ITEM_6_I05_PRESENTATION.md). The inventory below remains the pinned
pre-I05 evidence. Workflow/run/summary wording and future bodies have since improved,
and main Release mapping retention is implemented with offline coverage, awaiting natural
hosted acceptance. API release titles and artifact prefixes remain unchanged because
installed updater/recovery consumers use them. The FOLLOW / REVIEW / DOWNSTREAM-OWNED
recommendations are now encoded in trusted policy v1. I06 observes and preserves exact
DOWNSTREAM-OWNED paths, sends REVIEW paths to Draft semantic review, and follows ordinary paths.
The historical retention recommendation is superseded by T0-1 CP2.

Evidence is pinned to downstream `3907726ce38a03936e5853e5e8d36fff6d4486e9`
(PR #26, local HEAD and origin/main) and the locally available upstream/main
`1778bdb34caa699c0590232a7de709a889839765`. This is an audit of the checked-out fork
and that upstream snapshot, not a claim to have refreshed upstream or inspected live
GitHub settings. The working tree was clean on `chore/item-6-upstream-automation-audit`.
The latest 24-path hosted eligibility result below is user-reported; no run ID was supplied.

## A. Executive summary

I04 is **IMPLEMENTED / OFFLINE VALIDATED / HOSTED HIGH-RISK PATH LIVE VALIDATED**.
The latest Development result is `skipped_non_apk`, `tooling-only`, risk `high`,
24 changed paths. Release build/sign/publish correctly skipped after merge. This does
not mean protected-main Full validation skipped. The tracker and handoff record the
single-writer logger, untracked candidate linting, `.logs/` ignore, opaque App-token
coverage, same-process API reuse, shallow sign-only exercise checkout, and hosted
Linux PowerShell correction. Low-risk non-Android and normal targeted-Android I03
acceptance/timings still await natural PRs. The shallow diagnostic signer and App-token
publication are not separately proven live by a non-APK skip; retain their existing
offline evidence and accept them on a naturally needed exercise/genuine sync delta.

The fork contains eight workflows and two composite actions. Two workflows are
inherited publisher copies; the setup composite is inherited. Upstream's PR workflow
has already been removed and replaced by Mosaic CI, so it is included as a comparison
and future sync-policy path. There is no upstream `ci.yml` at the audited upstream SHA.

Recommended ownership at the audited 2026-09-10 snapshot (superseded for the two inherited
publishers by T0-1 CP2):

- `main.yml`: **DOWNSTREAM-OWNED**. Mosaic replaces its delivery contract, but should
  still learn from its mapping retention and release-body usability. Retain the guarded
  copy for now; deletion is a later choice, preferably after I06 ownership handling.
- `release.yml`: **REVIEW**. Appstore/Fire TV AAB production and mapping retention are
  real gaps in Mosaic's APK-only delivery. Stable is not a complete replacement.
- Upstream `pr.yml` and downstream `ci.yml`: **REVIEW** as a mapped validation area.
  Upstream runner, dependency, SDK and test changes remain valuable integration input.
- `actions/setup/action.yml`: **FOLLOW**, with normal automation/security review.
  Its current contents are byte-identical to the audited upstream copy.
- Mosaic-only workflows and signer composite: **DOWNSTREAM-OWNED**.

Upstream's release pipeline is shorter and its version-oriented presentation is clearer.
Mosaic has stronger exact-artifact, isolated-signing, provenance, immutable-history and
recovery guarantees. Adopt useful presentation and diagnostic retention without
copying upstream's secret-bearing Gradle job or destructive rolling-release replacement.

## B. Full workflow/action inventory

Source references: [downstream automation tree](https://github.com/constbogdan/Wholphin/tree/3907726ce38a03936e5853e5e8d36fff6d4486e9/.github)
and [upstream automation tree](https://github.com/damontecres/Wholphin/tree/1778bdb34caa699c0590232a7de709a889839765/.github).
All current workflow jobs use `ubuntu-latest`. Composite actions inherit the caller's
runner and token permissions; they cannot establish a protected Environment themselves.

### Inherited Development publisher

| Field | Finding |
| --- | --- |
| Upstream file | `.github/workflows/main.yml` ([upstream reference](https://github.com/damontecres/Wholphin/blob/main/.github/workflows/main.yml)) |
| Upstream workflow/action name | `Development build` |
| Purpose | Publish moving development previews for main and development branches. |
| Trigger | Push to `main` or `develop/*`; the fork adds `github.repository == 'damontecres/Wholphin'` to its only job. |
| Build/test/release behavior | Full checkout; shared setup; tag-derived version; `clean assembleDefaultRelease assembleDefaultDebug --no-daemon`; Gradle receives signing and extension credentials; verifies all APK signatures; creates short-name copies; prints hashes; deletes then recreates the branch's prerelease. No explicit unit-test or pre-commit invocation in this workflow. |
| Permissions | `build`: `contents: write`; no separate read-only build or signing Environment. |
| Artifacts/releases produced | `mapping` Actions artifact, compression 6, no explicit retention; all output APKs including short copies become release assets. Rolling `develop` for main, branch name with slash replaced for development branches; prerelease, not latest; release title uses `git describe`. Both Debug and Release, ABI splits and universal outputs are covered by the Gradle configuration. |
| Mosaic counterpart, if any | CI protected-main Full plus conditional unsigned Release; Mosaic Development classify/sign/publish; CI Full PR Debug artifact. |
| Capability overlap | Validation/build infrastructure, signed default Release, signature checking, rolling prerelease, updater-compatible APK alias. |
| Capability gap | Mosaic does not publish branch-specific previews, all ABI APKs, main Debug release assets, or mapping artifacts. Its universal APK distribution is intentional; mapping retention is a useful diagnostic gap. |
| Useful implementation technique | Shared setup, APK compression avoidance elsewhere in upstream release tooling, text mapping compression, branch-aware compare/install links, cancel obsolete development builds. The shell pipeline is easy to inspect but does not authenticate source/artifact ownership like Mosaic. |
| Presentation/UX comparison | Clear purpose name and branch/update instructions; version-oriented release title; no explicit run-name or job summary. Fork guard leaves skipped run noise. Mosaic summaries explain eligibility/provenance better, but production signing still says “exercise.” |
| Recommended ownership | **DOWNSTREAM-OWNED**: intentionally replaced release contract, not merely a heavily edited file. Observe future upstream changes without normal integration. |

### Inherited tag publisher

| Field | Finding |
| --- | --- |
| Upstream file | `.github/workflows/release.yml` ([upstream reference](https://github.com/damontecres/Wholphin/blob/main/.github/workflows/release.yml)) |
| Upstream workflow/action name | `Create release` |
| Purpose | Prepare tagged stable APK release and store-flavor bundles. |
| Trigger | Push tag `v*`; fork adds canonical-upstream repository guard to `publish`. |
| Build/test/release behavior | Full checkout/setup; `clean bundleAppstoreRelease bundleFiretvRelease`, then `assembleDefaultRelease`; upstream Gradle signs Release using injected credentials. Lists AAB/APK files, verifies APK signatures only, creates short APK copies, hashes APKs and AABs, prepares draft GitHub release. No explicit test/pre-commit step or store upload. |
| Permissions | `publish`: `contents: write`; build, credentials and release mutation share one job. |
| Artifacts/releases produced | `AAB` artifact for both bundle flavors, compression 0; `mapping` artifact, compression 6; neither declares retention. GitHub draft uses existing `v*` tag (`--verify-tag`), tag title, `--latest`, empty notes (`-n ""`), and APK assets only. AABs are Actions artifacts, not attached by the release command. |
| Mosaic counterpart, if any | Development produces signed universal default APK; Stable manually promotes its exact bytes to `mosaic-v1.0.N` and latest. |
| Capability overlap | Stable APK distribution, version titles, digest evidence, signing and release preparation. Mosaic adds provenance, exact-byte promotion, anti-rollback and recovery. |
| Capability gap | No Mosaic AAB generation/delivery/signing contract, store-flavor acceptance, mapping retention, or human-edited draft-release notes step. Upstream also has no automatic changelog generation or store deployment. |
| Useful implementation technique | Separate AAB and mapping artifacts; compression chosen by content; release draft for editorial review; existing-tag check. |
| Presentation/UX comparison | `Create release` and tag-based release title are concise. No explicit run-name, no job summary, and blank initial release body; the observed “Release v1.0.7” run list cannot be attributed to a run-name expression in this file. |
| Recommended ownership | **REVIEW**: preserve guarded copy and surface store/build changes for semantic review. Stable replaces the APK promotion responsibility, not the entire upstream contract. |

### Upstream PR validation, already replaced in the fork

| Field | Finding |
| --- | --- |
| Upstream file | `.github/workflows/pr.yml`, absent downstream ([pinned upstream source](https://github.com/damontecres/Wholphin/blob/1778bdb34caa699c0590232a7de709a889839765/.github/workflows/pr.yml)) |
| Upstream workflow/action name | `PR` |
| Purpose | Pre-commit gate followed by Debug build and unit tests. |
| Trigger | `pull_request`, no target-branch restriction. |
| Build/test/release behavior | Separate `pre-commit` and dependent `build` jobs; both full checkout; Python/pre-commit then shared Android setup; `clean assembleDefaultDebug testDefaultDebugUnitTest --no-daemon`. Collects APK/AAB path string as step output. No publication. |
| Permissions | No explicit permissions block; effective token access depends on repository/event defaults. Do not describe this as explicitly hardened read-only. |
| Artifacts/releases produced | None uploaded. `BUILD_DIRS_ARTIFACT=build-dirs` is unused here; collected `apks` output has no consumer in this file. |
| Mosaic counterpart, if any | `.github/workflows/ci.yml`, `CI / Full validation`. |
| Capability overlap | Pre-commit, shared SDK/JDK/Gradle cache, default Debug assembly and JVM tests. |
| Capability gap | Upstream targets all PR bases; Mosaic intentionally targets main. Mosaic adds trusted-base classification, offline tests, diagnostics and real PR APK upload. No missing upstream upload implementation to copy. |
| Useful implementation technique | Explicit pre-commit-before-build dependency and readable major stages; continue reviewing upstream test/task and SDK changes. Two jobs also mean duplicate checkout/setup overhead. |
| Presentation/UX comparison | Upstream's `pre-commit` and `build` jobs show phases immediately. Mosaic's stable `Full validation` job name is less precise for tiered PRs, but summaries accurately describe selected checks. |
| Recommended ownership | **REVIEW**, mapped to downstream CI. Preserve absence of the old file while porting useful changes semantically; REVIEW does not mean resurrect it. |

### Inherited shared setup action

| Field | Finding |
| --- | --- |
| Upstream file | `.github/actions/setup/action.yml` ([local source](../.github/actions/setup/action.yml)) |
| Upstream workflow/action name | `Setup` |
| Purpose | Install common Python, JVM, Android SDK and native build prerequisites. |
| Trigger | Composite call from current CI and signing-exercise build; also guarded inherited main/release. Upstream PR calls its counterpart. |
| Build/test/release behavior | Python 3.14; Zulu JDK 21 with `cache: gradle`; build-tools 36.0.0 and NDK 29.0.14206865; setup-android; Linux NDK/toolchain PATH entries. No build or release itself. |
| Permissions | Caller token/runner context; no explicit secrets or publication operation. Executes third-party setup actions pinned to SHAs. |
| Artifacts/releases produced | None explicitly; setup-java configures a Gradle cache, and SDK versions/PATH are exposed to subsequent steps. |
| Mosaic counterpart, if any | This same action serves Mosaic build jobs. Sign/verify jobs deliberately use smaller Java/SDK-only setup. |
| Capability overlap | Common build prerequisites are already shared. |
| Capability gap | No specialized `gradle/actions/setup-gradle` usage, measured cache telemetry, or platform-neutral native PATH. Current callers are Linux, so the latter is not an active portability defect. |
| Useful implementation technique | One pinned setup owner; SDK/NDK compatibility changes and action updates remain valuable. |
| Presentation/UX comparison | Generic `Setup` wrapper, readable inner steps. Improve labels later only if useful; no need to replace the action. |
| Recommended ownership | **FOLLOW**, subject to semantic/security review for executable automation. Current content matches upstream exactly despite earlier downstream edits. |

### Mosaic-owned and replacement inventory

The following table completes the inventory of every current file. Detailed CI/action
comparisons appear in F/G; the inherited entries above cover main, release and setup.

| File / display name | Trigger, purpose and behavior | Permissions / boundary | Artifacts and UX | Ownership |
| --- | --- | --- | --- | --- |
| [ci.yml](../.github/workflows/ci.yml) / `CI` | PR to main, main push, manual; trusted-base PR tiers; pre-commit/offline checks; targeted or Full Android; main Full followed by conditional unsigned Release. | Workflow `contents: read`; no signing secrets; release gate checks fork, protected-main push. One `Full validation` job, 30-minute limit. | PR universal Debug APK, main unsigned APK/provenance, failure test reports; seven days, APK compression 0; detailed PR/artifact summaries. | **REVIEW** validation area; introduced downstream. |
| `mosaic-development-release.yml` / `Mosaic development release` (removed historical workflow) | Completed CI on main or explicit expected-SHA dispatch; guards authenticated successful protected-main push/current SHA. | Historical audit evidence only; delivery now lives in protected-main CI. | Replaced by the same-run Build/Sign/Publish chain. | **REMOVED** |
| `mosaic-development-resume.yml` / `Mosaic development resume` (removed historical workflow) | Manually resumed an exact unsigned/signed checkpoint. | Historical audit evidence only; routine recovery now uses native failed-job rerun. | No unfinished legacy consumer remained. | **REMOVED** |
| [mosaic-stable-promotion.yml](../.github/workflows/mosaic-stable-promotion.yml) / `Mosaic stable promotion` | Manual approved tooling/source SHAs, immutable build and APK digest; fresh public verification followed by exact-byte promotion. No Gradle or resigning. | Read-only verification, contents-write publisher; no signing secrets. | Seven-day verified Stable transport; immutable `mosaic-v1.0.N`, latest stable, APK and manifest. Release title `v1.0.N`; no dedicated final Actions publication summary. | **DOWNSTREAM-OWNED** |
| [mosaic-signing-exercise.yml](../.github/workflows/mosaic-signing-exercise.yml) / `Mosaic signing exercise` | Manual exact protected-main SHA; full checks and bounded sequential Debug/unsigned Release build, isolated signing/verification. Diagnostic key-custody/recovery exercise. | Contents read; signing Environment only on signer; shallow signer checkout, full build checkout; no publisher. | Unsigned/signed seven-day artifacts; signing summary, no GitHub Release. “Publication is a separate job” is misleading here because this workflow has no publication job. | **DOWNSTREAM-OWNED** |
| [upstream-sync.yml](../.github/workflows/upstream-sync.yml) / `Upstream synchronization` | Manual or `23 6 * * *`; read-only isolated integration observation, then recheck and guarded candidate PR or blocked issue. No Android build/release. | Observe contents/PR/issues read; publish job contents/PR read and issues write; App token contents/PR write only for ready branch/PR publication. | Observation/outcome JSON, 14 days; candidate branch/PR or blocked issue, human summary. No automated merge. | **DOWNSTREAM-OWNED** |
| [mosaic-sign-apk/action.yml](../.github/actions/mosaic-sign-apk/action.yml) / `Sign exact Mosaic APK` | Called by Development, unsigned recovery and exercise sign jobs; SDK signs an already authenticated unsigned APK. | Caller must provide protected Environment and step-scoped secrets; temporary PKCS12, restrictive permissions, cleanup trap, no Gradle/network publication. | `signed.apk` in caller temp directory; no artifact upload itself; credential-presence messages omit values. | **DOWNSTREAM-OWNED** |

Development, resume and Stable share `mosaic-development-release` concurrency with
`cancel-in-progress: false`, serializing release-state mutations. Exercise has its own
non-cancelling group; Sync its own non-cancelling group. CI cancels superseded work by
PR/ref. Inherited main cancels by workflow/ref; inherited release and upstream PR have
no explicit concurrency. This distinction should survive naming changes.

## C. Upstream to Mosaic counterpart table

| Upstream responsibility | Mosaic counterpart | Equivalence limit |
| --- | --- | --- |
| `pr.yml` pre-commit/build/test | CI classifier-selected PR checks, protected-main Full | Main-only PR policy; adds actual retained PR APK and diagnostics. |
| `main.yml` Release/Debug build | CI main Debug plus conditional unsigned Release | No branch publisher or retained main Debug release asset. |
| `main.yml` signing/publish | Development isolated signer plus publisher | Universal Release only; stronger provenance and immutable build history. |
| `main.yml` mapping and release instructions | No retained mapping; technical release body | Mapping, compare link and concise install/channel guidance are gaps. |
| `release.yml` stable APK | Stable exact-byte promotion | Deliberately no rebuild/resign. |
| `release.yml` Appstore/Fire TV AABs | No delivery counterpart; flavors remain in Gradle | Requires separate distribution and bundle-signing contract. |
| `release.yml` draft notes | Programmatic draft-to-publication safety transition | Not an editorial approval stage; no automatic changelog in either path. |
| `actions/setup` | Same composite in CI/exercise | SDK-only signer setup is deliberately separate. |
| No upstream counterpart | Resume, signing exercise, Sync, signer composite | Downstream trust/recovery requirements. |

## D. main.yml recommendation

Every meaningful upstream capability is accounted for below.

| Capability | Mosaic today / disposition |
| --- | --- |
| Automatic main and development-branch previews | Main delivery is covered. Branch previews are intentionally absent; PR Debug artifacts cover pre-main device trials without granting branch signing authority. |
| Full tag history and `git describe` versions | Full history remains necessary for Mosaic's frozen-epoch first-parent allocator. Do not copy tag-derived allocation. |
| Latest stable tag and branch-aware rolling tag | Mosaic uses authenticated published baseline, immutable build ledger and rolling `develop`; no per-branch channel. |
| Shared Java/SDK/NDK/cache setup | Already inherited. No distinct upstream Gradle setup action exists here. |
| 8 GiB Gradle override, `clean`, Debug+Release one invocation | Do not adopt mechanically. Mosaic has measured bounded sequential Release settings and reusable outputs; upstream does not provide evidence that its memory/clean choices improve this fork. |
| Secret-bearing signed Release build and extension credentials | Replaced by unsigned CI and isolated signer; do not reintroduce credentials to Gradle. |
| All ABI/universal Debug and Release APK publication | Mosaic selects one universal Release and PR Debug for a smaller distribution contract. Per-ABI downloads and main Debug retention require demonstrated demand. |
| APK signature verification and SHA-256 output | Mosaic additionally verifies pinned signer, package, version, payload and provenance; retain those stronger checks. |
| Short APK aliases | Existing `Wholphin-release.apk` is the updater contract. An I05 human-name change is not authority to change that asset. |
| Mapping artifact | Missing in active Mosaic delivery; worth retaining from the existing minified build with exact source/version/artifact metadata, without rebuild. |
| Delete/recreate moving prerelease | Replaced by state-aware exact-byte publication and immutable archive. Do not copy `gh release delete ... || true`. |
| Prerelease/not-latest, title and install/compare body | Channel semantics covered; human compare/install content worth adopting. |
| Per-ref cancellation | Appropriate for disposable validation/build work; unsafe to copy onto Mosaic's mutating publication pipeline. |

The file differs from upstream by only the added repository guard. Nevertheless,
**DOWNSTREAM-OWNED is safe as a proposed contract classification**: Mosaic consciously
replaced branch/tag-derived, in-build signing and rolling-release authority. Missing
mapping retention does not make that whole publisher the desired downstream contract.

Deleting the guarded copy later would improve the Actions list, but saves essentially
no build work because its job already skips. The trade-off is **cleaner downstream
Actions / less dead workflow noise vs future modify/delete divergence during upstream
sync**. Such conflict occurs when a later upstream edit intersects the downstream
deletion, not on every sync regardless of its contents. The earlier handoff's blanket
“every sync” wording was too broad.

Recommendation: retain now, consider deletion after I06 explicitly handles ownership.
If upstream later changes it, observe the exact old/new blobs and semantic capabilities,
report why it is excluded, preserve the downstream copy or intentional absence, and
integrate the rest only through the approved guarded sync path. Never silently drop
the observation, recreate a deleted publisher, or automatically merge its new authority.

## E. release.yml recommendation

The actual file proves Stable is only a partial substitute. Its bundle tasks generate
`appstore` and `firetv` AABs; default Release assembly also creates APK splits/universal
outputs. Upstream's Gradle Release signing configuration applies when its signing
credentials are present. The verification step checks APKs, not AAB signatures; listing
and hashing a bundle is not proof of store acceptance. There is no Play/Amazon upload,
store credential configuration, bundle validation command, or generated changelog in
the workflow. The GitHub release body explicitly starts empty.

Mosaic retains those flavors: appstore disables self-updating and requires Leanback;
firetv also disables Discover. But Mosaic's current Release Gradle configuration is
explicitly unsigned, and its SDK signer verifies/signs APKs only. Simply removing the
guard or calling the old bundle tasks would not establish a safe store release path.

For today's GitHub universal-APK distribution, Stable fully covers stable promotion.
For potential Google Play/Fire TV distribution, bundle production, upload-key versus
app-signing identity, flavor behavior, store accounts, version sequencing, artifact
retention and store acceptance need a separately approved design. Store direction is
an open product decision, not an I05 naming task. Keep `release.yml` **REVIEW**, guarded,
and available as a source of future store/build improvements.

## F. ci.yml recommendation

Git history establishes that `905680ca` introduced fork `ci.yml` and deleted `pr.yml`.
Mosaic CI is a downstream-authored replacement with inherited techniques, not a
heavily edited upstream file of the same name.

| Area | Inherited / upstream | Mosaic-specific / review value |
| --- | --- | --- |
| Gradle setup/cache | Shared setup-java Gradle cache; wrapper-driven commands | Task/output and configuration cache enabled in fork Gradle properties; preserve identity-sensitive invalidation. Evaluate future upstream cache changes with measurements. Neither tree currently uses setup-gradle. |
| JVM/Android/native | Zulu 21, Python 3.14, SDK build-tools/NDK and Ubuntu | Python also runs before optional Android setup for policy/offline checks. Keep following toolchain compatibility and action SHA updates. |
| Validation | Pre-commit, Debug assembly, JVM tests | Trusted-base PR tiers, mapped tests/fallback, offline safety tests; authoritative main Full. No broad Release lint/device/instrumentation proof should be inferred from either workflow's task list. |
| PR artifacts | Upstream merely collects an unused path output | Mosaic uploads validated universal Debug APK with PR/head/tested/base identity and download instructions. |
| Concurrency | Upstream PR has none | Mosaic cancels superseded PR/ref validation; keep mutation groups separate. |
| Runner/resource policy | ubuntu-latest and upstream 8 GiB override | Main Release bounded with `--no-parallel --max-workers=1`, 30-minute CI timeout. Review upstream runner/AGP/resource changes, do not import larger heap or `clean` blindly. |
| Permissions | Upstream PR inherits defaults | Mosaic explicitly contents-read, no signing secrets, protected-main conditional artifact owner. |
| Structure/UX | Two readable phase jobs, two full checkouts | Single authoritative required job; detailed tier summary, failure diagnostics, main artifact handoff. |

Use **REVIEW** for the mapped area. Continue surfacing upstream task, dependency,
runner, caching, concurrency and PR artifact changes. An upstream improvement may be
ported into CI without reviving `pr.yml`. The `CI` workflow trigger name and
`Full validation` job name are machine dependencies: Development uses `workflows: [CI]`
and the Python authenticator uses `CI_JOB = 'Full validation'`; required checks also
depend on that identity. I05 must not casually rename them or alter the required gate.

## G. .github/actions findings

`setup/action.yml` originated upstream in `6be2662d` (experimental MPV backend).
History includes upstream tool/action upgrades and downstream `905680ca` / `e9d8f2f3`
setup changes; current upstream-to-downstream diff is empty. This supports **FOLLOW**,
not a downstream ownership claim based on commit authorship alone. Its four current
callers are CI, signing-exercise build, inherited main and inherited release. CI and
exercise still need it even if both inherited publishers disappear.

The action executes in build workspaces and changes SDK/PATH/cache state, so upstream
changes remain a supply-chain and reproducibility boundary. Review new downloaded
code, secret requirements, cache scope and native PATH changes before integration.
SDK-only sign/verify jobs intentionally avoid the full setup's Python/NDK/cache scope;
consolidating them just to reduce repetition would expand their trust/runtime surface.

`mosaic-sign-apk/action.yml` originated downstream in `5fd771ec`, the signer Environment
binding fix. It is the canonical shared signing operation, not a duplicate of the
Python public verifier or APK transport helper. Development, unsigned recovery and
exercise call it after input authentication; Stable and signed recovery do not need
a private key. It signs with SDK 36.0.0, temporary PKCS12 custody, environment-password
arguments, v1/v2/v3 enabled and v4 disabled, with cleanup and private diagnostic suppression.
The caller, not the composite, enforces protected-main authorization and Environment
scope. Keep **DOWNSTREAM-OWNED**, while reviewing upstream/SDK signing improvements
as ideas rather than importing upstream's Gradle-secret design.

Historical `native-build/action.yml` is not in either audited current tree. No additional
local/composite action was found under `.github/actions/**`; this audit does not propose
restoring historical actions or deleting shared setup because of caller counts.

## H. Useful upstream capabilities worth adopting

“Yes” means a future scoped proposal is worthwhile; it does not authorize implementation.

| Upstream capability/technique | Source workflow/action | Mosaic equivalent today | Gap | Worth adopting? | Why | Proposed checkpoint |
| --- | --- | --- | --- | --- | --- | --- |
| Retain minification mappings | main/release | Minified Release built, mapping not uploaded | Crash deobfuscation evidence disappears | Yes | Upload existing mapping tied to exact build; no rebuild or publisher asset change | Separate artifact/diagnostic follow-up after this audit |
| Content-appropriate compression | release AAB/mapping uploads | APK transports already compression 0 | Mapping retention absent | Yes | Keep binary archives uncompressed, compress text mappings | Mapping follow-up |
| Shared pinned toolchain setup | setup | Same action already used | No adoption gap | Yes, continue | Upstream compatibility and action updates remain useful | I06 FOLLOW review |
| Gradle dependency cache | setup-java | Same cache plus fork Gradle caching | No proven new upstream cache improvement | Yes, retain | Measure hit/miss and cost before changing cache owner | Future measured build checkpoint |
| Dedicated setup-gradle | None in audited upstream | Not present | Not an upstream capability to copy | No in this audit | A separate comparative experiment needs evidence | Future profiling only |
| AAB flavor generation | release | Flavor definitions, no active bundle delivery | Store artifacts/signing/acceptance | Yes, if stores approved | Preserve upstream knowledge; not required for GitHub APK delivery | Separate distribution design |
| Draft before publication | release | Internal draft staging | No editorial notes checkpoint | Yes, for manual Stable if desired | Human release notes can be reviewed without rebuilding | I05 notes design, later approved behavior work |
| Compare/update instructions | main release body | Source/hash/provenance body | Little user-facing change/install guidance | Yes | Link the relevant immutable range and channel safely | I05 |
| Automatic changelog generation | Neither publisher | Neither publisher | Human-readable changes | No upstream implementation to copy | Upstream release uses empty notes; design separately | I05 proposal |
| Short aliases | main/release | `Wholphin-release.apk` | Branding mismatch only | No new alias now | Existing updater depends on stable name | I05 compatibility map |
| ABI-specific and main Debug release assets | main/release | Universal APK and PR Debug | Optional smaller downloads/main Debug retention | No without demand | Extra artifacts and updater selection complexity | Distribution follow-up |
| 8 GiB heap / clean builds | main/release/pr | Bounded sequential Release, cached outputs | No demonstrated benefit | No | Could increase cost/memory pressure and discard reuse | Measured resource tuning only |
| Cancel obsolete runs | main | CI already cancels by PR/ref | No validation gap | Yes, retain scope | Do not cancel mutating release jobs halfway through | I05 preserve; I06 concurrency review |
| Simpler phase labels/version titles | PR/release | Generic run names; technical summaries | Actions list lacks identity/outcome | Yes | Improve scanability without changing trust contracts | I05 |
| In-job signing/write authority | main/release | Isolated signer/read-only build | Upstream is less isolated | No | Preserve secret and publication boundaries | Permanent invariant |
| Delete/recreate rolling release and ignore delete error | main | Idempotent immutable/rolling publisher | No recovery benefit | No | Mosaic preserves evidence and rechecks exact bytes | Preserve recovery; I07 if approved |
| Retry/recovery | No dedicated upstream recovery | Unsigned/signed resume and exact-byte retries | Endpoint-specific transient retries still deferred | No upstream technique to copy | Generic retries could hide ambiguous mutations | Future evidence-based retry work |
| Existing-tag verification | release | Annotated immutable source ledger | Already stronger identity checks | Yes, retain principle | Never replace exact source/digest proof with tag existence alone | Ongoing release invariants |
| Runner/tool action updates | all/upstream setup | ubuntu-latest, pinned actions | Future changes may fix compatibility | Yes, review | Follow supported build changes without assuming performance | I06/normal dependency review |

## I. Actions/release UX patterns worth adopting in I05

All eight current workflows and all three audited upstream workflows omit `run-name`.
Upstream release's display name is `Create release`, its job is `publish`, and its
release title is the tag. The user's observed `Release v1.0.7` / `Release v1.0.6` run
rows are clearer, but the YAML does not prove how those exact rows were produced.
GitHub uses event-specific information when run-name is absent; an explicit run-name
can use `github` and `inputs`, not later job outputs.
See [GitHub workflow syntax: run-name](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#run-name).

| Surface | Current finding | Proposed I05 direction |
| --- | --- | --- |
| Workflow display names | Development/resume/Stable/exercise distinguish operations, but inconsistent capitalization and repeated generic runs | Coherent family such as `Mosaic — Development Release`, `Mosaic — Stable Promotion`, `Mosaic — Development Recovery`, `Mosaic — Signing Diagnostic`; leave CI name unless every dependent contract is deliberately migrated. |
| Run names | No explicit identities in YAML | Use information known at trigger time: Development CI run number/source SHA; manual recovery checkpoint/artifact; Stable approved build. Do not invent a version from github.run_number. |
| Desired version/outcome row | `v1.0.N · downstream-build-N` or `Skipped · tooling-only` is attractive | Put exact computed identity/outcome in summary and later job labels. A top-level run-name cannot read classification outputs; achieving that exact automatic row would require separately reviewed event/orchestration changes, not a cosmetic expression. |
| Job names | Mostly IDs (`classify`, `sign`, `publish`, `recover_signed`); CI `Full validation` is a contract | Add clear human phase names to non-contract jobs after auditing consumers. CI tier precision belongs in its existing summary until a coordinated gate migration is approved. |
| Major steps | Good verbs such as authenticate, verify and promote; unnamed action steps; “Signing exercise summary” in production | Keep security-relevant distinctions; call production signing production, recovery recovery, and diagnostic exercise diagnostic. Fix exercise summary's nonexistent publication-job implication. |
| Summaries | Eligibility reports outcome/risk/baseline/current SHA/24 paths; PR includes checks/download; signer summary technical; no final release-link summary in publisher scripts | Lead with published/skipped/failed outcome and version/build or reason; release/download links and short changes first, provenance next. Report failed-CI/superseded-source guards truthfully; they currently can skip before eligibility emits a summary. |
| Artifact names | Identity/run/attempt-rich transports; PR starts `wholphin-pr`; legacy exercise terms remain | Improve labels/download guidance first. Artifact matching is authenticated in Python; do not rename transport formats as incidental UX work. |
| Release titles | Both Mosaic channels already use `v1.0.N` | Preserve version-parser compatibility; distinguish channel in human body. The main weakness is Actions run presentation, not absent version release titles. |
| Release bodies | Development: build/source/hash/manifest; Stable: promoted-from/source/hash | Borrow upstream's readable channel/install/compare links; compare authenticated immutable identities, not a moving tag that can later mean different bytes. |
| Non-APK skips | Successful eligibility with downstream jobs skipped, generic Actions row | Summary heading like `Skipped · tooling-only`, count/risk/reason and “Release build/sign/publish not required”; do not turn an expected skip into a failure or claim Full main validation was omitted. |

Machine compatibility includes `CI`, `Full validation`, workflow file paths, artifact
prefixes/IDs, `downstream-build-N`, `develop`, `mosaic-v1.0.N`, `Wholphin-release.apk`,
`mosaic-release.json`, signer identity and updater parsing. A future before/after map
must identify each consumer before applying a human-facing rename.

## J. FOLLOW / REVIEW / DOWNSTREAM-OWNED path proposal

This table was the proposed policy and is now implemented by the versioned trusted
`scripts/upstream_ownership_policy.json`; that file is the active authority.

| Exact path | Proposed ownership | Integration interpretation |
| --- | --- | --- |
| `.github/workflows/main.yml` | **DOWNSTREAM-OWNED** | Preserve guarded copy or approved absence; observe upstream delivery ideas. |
| `.github/workflows/release.yml` | **REVIEW** | Keep guard; assess store/build changes semantically. |
| `.github/workflows/pr.yml` (absent) | **REVIEW** | Map useful upstream changes into CI; do not recreate automatically. |
| `.github/workflows/ci.yml` | **REVIEW** | Downstream implementation of mapped validation area; future same-path addition/collision requires review. |
| `.github/actions/setup/action.yml` | **FOLLOW** | Normal integration candidate, with automation/security checks. |
| `.github/workflows/mosaic-development-release.yml` | **DOWNSTREAM-OWNED** | Own delivery/eligibility contract. |
| `.github/workflows/mosaic-development-resume.yml` | **DOWNSTREAM-OWNED** | Own recovery/source identity contract. |
| `.github/workflows/mosaic-stable-promotion.yml` | **DOWNSTREAM-OWNED** | Own exact-byte Stable authority. |
| `.github/workflows/mosaic-signing-exercise.yml` | **DOWNSTREAM-OWNED** | Own diagnostic custody contract. |
| `.github/workflows/upstream-sync.yml` | **DOWNSTREAM-OWNED** | Own sync authority and publication policy. |
| `.github/actions/mosaic-sign-apk/action.yml` | **DOWNSTREAM-OWNED** | Own isolated signer operation. |
| New/unmapped automation paths | **REVIEW** by default | Surface new capability/security boundary; never silently exclude or trust it. |

FOLLOW means upstream evolution is normally wanted; REVIEW means semantic integration
is necessary; DOWNSTREAM-OWNED means intentional replacement, with continued observation.
Path ownership does not waive permissions review or authorize automatic PR merge.

## K. Upstream Sync implications for I06

Current v1 attempts an ordinary isolated two-parent merge and blocks publication when
integration changes `.github/` or the hosted helper. It has no ownership overlay. A
clean textual merge of setup is therefore not permission to publish automation today.
Historical note: the blanket guard was correct at audit time. I06's versioned ownership policy,
Draft review path and tests now supersede it.

Proposed behavior:

1. Load an exact-path/versioned policy from trusted downstream main, never the incoming
   upstream tree. Record policy version, downstream/upstream SHAs, merge base and range.
2. Observe every upstream automation change before applying ownership. Record old/new
   blob IDs, add/modify/delete/rename status, source commit links, counterpart, ownership,
   semantic summary and exclusion/review rationale. Keep observation separate from integration.
3. Preserve the downstream state (including deliberate deletion) for DOWNSTREAM-OWNED
   paths in a deterministic integration overlay. Resolve only that already-approved
   ownership choice; never apply global `ours`, broadly ignore `.github`, or auto-resolve
   unrelated conflicts. Renames crossing ownership boundaries and cross-file dependencies
   require semantic review; a helper change can invalidate a preserved workflow.
4. FOLLOW stays an integration candidate; REVIEW produces explicit semantic review and
   a counterpart suggestion. Preserve repository guards and least privilege. Any change
   to executable automation still needs the separately approved automation publication
   path; the current App token does not receive broader workflow authority by implication.
5. Deduplicate by observed range/blob identity/policy decision, so unchanged excluded
   content does not create repeated meaningless blocked issues. A new blob, changed
   dependency or changed policy must surface again. Record acknowledged and integrated
   states separately, including exclusions in a mixed application+automation candidate.
6. Define the all-excluded-delta case explicitly: retain a durable observed/excluded
   result and evidence; do not claim Git ancestry has advanced without a real merge.
   If I06 instead proposes an ancestry-only merge, it still needs an explicit reviewed
   two-parent candidate and Full CI. Policy bookkeeping must not silently manufacture
   accepted upstream ancestry or conceal unreviewed changes.
7. Test retained/deleted owned files, later upstream modifications, add/delete/rename,
   unknown paths, REVIEW mapping to absent pr.yml, mixed changes, stale policy/SHA drift,
   all-excluded observations, retries/deduplication and cross-file security dependencies.
   Human merge/reject, deterministic candidates and no force-push remain intact.

Repo Intelligence should consume all observations, including intentionally excluded
paths. It should rank meaningful SDK/cache/build/signing/AAB/UX changes, link exact
upstream evidence and downstream counterpart, and propose a scoped idea without
repeatedly demanding restoration of intentionally replaced automation. Deduplicate
acknowledged findings by content/decision, but reopen on material changes. Sync answers
“should these bytes integrate?”; Repo Intelligence answers “is there something useful
to learn or adapt?” Neither should treat exclusion as invisibility. No Repo Intelligence
code or configuration is changed by this audit.

## L. Files/workflows safe to remove later

Only inherited `main.yml` is currently a justified workflow-removal candidate, subject
to the explicit Actions-noise versus modify/delete trade-off and a later authorized
change. It has no local workflow/action callers or Mosaic release/recovery consumers;
its job guard disables fork execution. Recheck current callers/triggers at removal time.
No mapping/AAB capability should be accidentally claimed as already adopted by deleting it.

The old `pr.yml` is already absent; do not treat that as a new deletion task. No shared
composite or other active workflow is recommended for removal. Historical names or
few callers alone are insufficient evidence of dead work.

## M. Files/workflows that should remain

Keep CI, Development, resume, Stable, Sync and the signing diagnostic. Each has a
distinct validation, delivery, recovery, mutation or custody responsibility. Keep both
composites; setup has active build callers and signer has three protected callers.
Keep inherited release guarded for store/AAB review. Keep main guarded until the later
ownership/deletion decision. Preserve all helper/API/artifact trust boundaries and
the original purpose of the two PowerShell output regression tests.

## N. Open questions

- Is Mosaic distribution expected to include Google Play or Fire TV stores? If so,
  define bundle signing, accounts, package/flavor identity, versioning and acceptance
  independently of APK Stable promotion.
- Should exact-build R8 mappings be retained, for how long, and with which access?
  They need not become public release assets or change the two-asset updater contract.
- Is removing one skipped inherited Development entry worth divergence now, or should
  it wait for I06's ownership-aware integration handling? Recommendation: wait.
- Is a trigger-time source/CI identity sufficient for the Actions run row, with computed
  version/outcome in the summary, or is a separately designed naming handoff warranted?
- Should manual Stable promotion have an editorial notes checkpoint, and what verified
  source range should Development change notes cover?
- How should I06 represent all-excluded upstream deltas without confusing observation,
  acceptance and Git ancestry? How will REVIEW changes reach the manual automation path?
- Natural acceptance remains for low/normal I03 PR paths and their timings, a needed
  shallow signing diagnostic, and genuine App-token sync publication/PR CI. Do not
  manufacture releases, dispatches or sync deltas to close those entries.
- The latest I04 live run URL/ID is not included in the supplied result. Preserve the
  user-reported acceptance without inventing traceability; attach it when available.

Historical audit stop point: documentation/status updates only. Later authorized I05/I06 implementation,
workflow/action edits or removal, publication and GitHub settings changes remain undone.
