# Mosaic Stable channel and promotion

Status: **Stable promotion COMPLETE / LIVE VALIDATED** (through downstream-build-34). Permanent signing, downstream
routing, development delivery and in-place updater acceptance remain COMPLETE / LIVE
VALIDATED. Channel selector and existing-user migration are now LIVE VALIDATED through 1.0.5 -> 1.0.8. CI/developer-velocity optimization remains pending. No stable release was created
while implementing this contract.

## Stable promotion acceptance

Current operation supersedes the historical form procedure below. Stable Promotion is a
zero-input manual **Prepare -> Release** workflow. Prepare resolves the current rolling
`develop` publication and derives/authenticates protected-main tooling, its immutable
`downstream-build-N`, source SHA/tree, signed APK hash, version, producer run/attempt,
tag/release/assets, signer, package and payload. Its compact summary is `Ready to release:
[v1.0.N](exact authenticated APK URL) · ✓ Authenticated`. Release alone uses
`release-promote`; after approval it reauthenticates protected main and proves rolling
`develop` still identifies the exact prepared candidate before invoking the unchanged
exact-byte publisher. Movement or ambiguity refuses instead of selecting another build.

I07 forward-recovery acceptance promoted `downstream-build-34` unchanged in run
`34694610864`. Stable release `387569996` / v1.0.34 became latest with APK SHA-256
`1d84dfb922765b28f75e422e25b7fbdc5123beb86fc0148d5e324f5547514e5d`, identical to
Development. The held v1.0.5 release remains preserved as a prerelease.

The workflow displays **Mosaic — Stable Promotion** and uses the fixed run identity
**Stable Promotion**. Its successful summary leads with the exact authenticated candidate
and APK link. API title `v1.0.N`, workflow path, verification/publisher separation, manual
authorization and assets remain unchanged. New bodies use a branded Stable heading;
historical bodies are not changed. See the [I05 ledger](ITEM_6_I05_PRESENTATION.md).

User confirms downstream-build-5 / v1.0.5 was promoted unchanged to tag `mosaic-v1.0.5`;
the reported release label is **Mosaic stable 1.0.5**. `/releases/latest` resolves to it.
The updater-visible numeric release-name contract below remains `v1.0.N`; this checkpoint
records the supplied label without changing publisher metadata or parser behavior.
Signed APK SHA-256 remains exactly
`af0dcb7fb1c89800c61e7a7a0558cbb2e6fc65fbf880069dbe08c3c4df8bf578`.
Verification took 38s, publication 20s, total approximately 1m05s. There was no Gradle
build and no signing. Stable promotion is COMPLETE / LIVE VALIDATED and remains manual.

## Exact-byte stable promotion

[Manual promotion workflow](../.github/workflows/mosaic-stable-promotion.yml) runs only
in constbogdan/Wholphin on protected main. The four former form values remain exact
authenticated machine facts, but are derived automatically from current protected main
and the current authenticated rolling/immutable Development state. Current-tooling and
original-source CI must pass. Original source must be on the current main first-parent
chain after the pinned epoch. Old source is never executed.

Its final operator-facing job sequence is **Prepare → Release**. Prepare is read-only and
has no mutation Environment. Release alone uses `release-promote`; approval authorizes
the mutation but does not replace the authentication and freshness checks below.

The read-only verification job authenticates the annotated development tag, its canonical
manifest, published development prerelease and exact asset IDs. It downloads the existing
`Wholphin-release.apk` and `mosaic-release.json`; GitHub asset digests, sizes and downloaded
bytes must agree with the ledger and authenticated candidate. Full source/tree/upstream/version
provenance is checked against Git objects and the original successful build job. Fresh SDK
apksigner/aapt verification enforces the pinned single signer, non-debuggable
`io.github.constbogdan.mosaic`, original version and signed hash. No key is available.

Only the separate Release job gets Contents write (plus Actions read). It receives the
successful verification job's immutable Actions artifact ID with digest mismatch rejection,
then rechecks the original source release, manifest, APK and acceptance record. No signing
credentials, Sync Bot, Gradle build, repackaging, alignment mutation or re-signing
exists in promotion. Transport archives do not alter the APK file's bytes.

| Identity | Contract |
| --- | --- |
| Development origin | Existing annotated `downstream-build-N` and its prerelease |
| Stable tag | Annotated `mosaic-v1.0.N` at the SAME original source commit |
| Stable release name | `v1.0.N` |
| Stable assets | Exact `Wholphin-release.apk` and exact `mosaic-release.json` from development |
| Stable visibility | `prerelease: false`; publish with `make_latest: true` |
| Development | Remains prerelease; `develop` and its assets are not changed |

The local inherited upstream `v1.0.5` tag already exists at
`cbcdb73a45c15b297060e7900f8b7b32cf90332d`; its name cannot safely serve as the permanent
Mosaic namespace even if a remote has not published it. Product-prefixed stable tags
avoid upstream-fetch collisions. No inherited tag is moved or deleted. The numeric
release **name**, not its tag, is what the updater compares.

The stable tag reserves the same canonical provenance before upload. Missing assets can
be added only to a matching draft. Published stable assets/tags are never replaced,
moved, deleted or re-uploaded by this publisher. A matching completed retry verifies exact
assets and performs no mutation. Unknown stable ownership, newer stable versions,
conflicting tags/bytes/manifests or missing published assets fail closed. `/releases/latest`
must identify the promoted stable after completion; numeric rollback is refused.

The stable manifest stays byte-identical to the development manifest. Its
`immutableIdentity: downstream-build-N` and `rollingChannel: develop` describe its origin,
not a stable updater redirect. Stable has independent versioned assets and does not depend
on mutable develop after publication. The shared resolver now tries `mosaic-v1.0.N` for downstream installed-version notes
before legacy version tags; custom repository lookup remains unchanged. No new version identity is allocated by promotion.

Immutability is enforced by the publisher's create-only ledger and conflict checks. This
task adds no external GitHub ruleset or release-immutability setting; administrators could
still mutate externally unprotected objects. Do not do that. Existing rules must permit
creating mosaic-v1.0.N tags/releases with GITHUB_TOKEN Contents write. `release-promote`
adds human authorization but no secrets. External settings were not inspected or changed in this implementation;
permission/rule conflicts must stop publication, never cause a bypass or replacement.

## Retry without build or signing

```text
build failure -> rebuild
sign failure -> reuse authoritative unsigned artifact
development publication failure -> reuse verified signed artifact
stable publication failure -> reauthenticate the exact signed development artifact
```

Retry the zero-input workflow from current protected main. Prepare resolves and
authenticates the then-current Development candidate. The
publisher resumes matching drafts without replacing existing assets. It downloads from
the durable immutable development release, so promotion is independent of seven-day
Actions artifact retention. After a successful stable publication, identical retry verifies
idempotency; an older promotion cannot roll latest back after a newer stable exists.
Development delivery and Stable/Hold publication share the publisher concurrency group.
No heavy validation/build is introduced by a promotion retry.

## Update channel preference and migration

The Updates section uses the existing remote/TV choice control: **Stable**, **Development**,
**Custom**. Automatically check for updates keeps its existing behavior. Only Custom shows
the URL editor; normal users do not need to edit GitHub endpoints. Other Settings sections
are unchanged.

A protobuf `update_channel` field (16) stores the explicit choice. Unspecified legacy
records migrate deterministically using their existing URL:

| Existing configuration | Migrated channel |
| --- | --- |
| Fresh/default or blank legacy URL | Stable |
| Exact bundled downstream stable web/API endpoint | Stable |
| Exact old bundled upstream stable API default | Stable (existing default migration retained) |
| Exact downstream develop web/API endpoint | Development |
| Any other existing URL | Custom, preserving its value |

An explicit stored channel remains authoritative on subsequent loads. Stable resolves
`https://api.github.com/repos/constbogdan/Wholphin/releases/latest`; Development resolves
`https://api.github.com/repos/constbogdan/Wholphin/releases/tags/develop`. Custom uses its
stored release API URL, retaining the existing web-to-API normalization where applicable.
An invalid/empty explicit Custom URL does not silently switch to Stable. A retained custom
URL is ignored in Stable/Development and reappears when Custom is selected; there is no
hidden active override. Fresh/default configurations select Stable. No stable release yet
means no offered Stable update, never an upstream/develop fallback.

Startup automatic checks, manual discovery/download and installed-version notes all
obtain the chosen URL through the shared resolver. Numeric comparison is preserved;
notifications and the installation screen do not offer equal/older versions. A newer
Development installation switched to Stable waits until Stable overtakes it; no downgrade
or uninstall/reset occurs. Invalid sources can report no newer update or an error.

The live 1.0.5 installation's exact manually retained downstream develop API URL migrates
to **Development** when a future selector-containing APK is installed. Promoting the old
build 5 does NOT add the selector to its bytes. It remains the already accepted version
and source; an installed 1.0.5 will not receive an equal-version update solely because the
same bytes are now Stable. Selector exposure, existing-user migration and Custom field exposure were accepted in
1.0.8; presentation/focus polish remains future UX work.

## First live stable promotion procedure (completed; retained reference)

Candidate: `downstream-build-5`, version 1.0.5/code 5, source
`41f9f83c36b8866211c9680d3b416d5ebede4888`, signed SHA-256
`af0dcb7fb1c89800c61e7a7a0558cbb2e6fc65fbf880069dbe08c3c4df8bf578`.
Its build, permanent signing, development publication, real Mosaic download, Android
in-place update, launch and settings preservation are already live validated. No reason
to rebuild or re-sign it has been identified.

That first promotion used four manually supplied machine identities. They remain useful
historical evidence, but current operation derives and authenticates the same facts from
protected main and current Development state. Use the GitHub **Run workflow** control
without inputs, inspect Prepare's authenticated candidate, and authorize Release through
`release-promote`. This document is not live-promotion authorization.

## Current development automation boundary

Development now follows successful protected-main push CI automatically; see the
[current Development contract](MOSAIC_DEVELOPMENT_RELEASE.md#trusted-build-sign-and-publish).
The automatic trigger and device delivery are COMPLETE / LIVE VALIDATED. No normal manual dispatch
is required. Device checks are unchanged and installs remain user-driven. Stable remains
manual, its exact-byte publisher is unchanged, and `release-promote` is the human
authorization boundary.

Future UX TODOs remain separate: broader Settings redesign; cleaner General / Playback /
Library / Downloads / Updates / Integrations / Advanced groups; improved update notifications
if warranted; consistent progress/status UX. Retain the measured CI-overlap work and
quiet prepare-pr/full-log plans without implementing them here.

## Forward recovery policy

Development problems are corrected by a higher-version forward fix. An urgent bad Stable
may be held while that fix is prepared, then the corrected Development build is promoted.
A broken updater requires manual installation of a correctly signed higher-version APK.
There is no rollback, repoint, unhold, Development remediation or generic release-recovery
mechanism.

Stable: fix/revert on main -> higher-version Development -> validate -> manually promote
that exact signed build. If a catastrophic Stable regression prevents launch/updater use,
manually install a newer correctly signed Mosaic APK over the same package without clearing
data. Never mutate/re-version an old APK or force a downgrade. Preserve signing identity.
