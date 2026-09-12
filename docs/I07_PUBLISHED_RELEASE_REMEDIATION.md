# I07 — Published Release Remediation

## Status

**COMPLETE / LIVE VALIDATED.**

I07 has one exceptional purpose: a human can stop the Stable release currently
advertised by GitHub while a forward fix is prepared. It is not a rollback or general
release-management system.

## Permanent recovery policy

```text
Development problem → fix protected main → normal CI publishes N+1
Stable problem      → Hold Release if urgent → forward-fix and promote N+1
Broken updater      → manually install a correctly signed higher-version APK
```

Development withdrawal, repoint, rollback, and custom recovery are deliberately out of
scope. A bad Stable is never replaced with older bytes: ordinary recovery is a higher
Development build followed by normal exact-byte Stable Promotion. Clients already on a
bad version are not downgraded.

## Hold Release

The manually dispatched, zero-input [Hold Release workflow](../.github/workflows/hold-release.yml)
has one responsibility:

```text
Run workflow
    ↓
Prepare
    ↓
Hold
```

It resolves `GET /repos/constbogdan/Wholphin/releases/latest`; the operator does not
select a version, release, target, reason, or replacement.

### Prepare

The read-only job requires a manual run from exact protected `main` and authenticates
the current Stable by reusing the Stable Promotion trust model:

- exact numeric Release identity and `mosaic-v1.0.N` / `v1.0.N` relationship;
- annotated Stable tag containing the canonical manifest;
- equality with the immutable `downstream-build-N` Development provenance;
- exact APK and manifest asset identities, sizes, archive digests, and bytes;
- source SHA/tree and authenticated producing CI run;
- APK package, version, payload, SHA-256, and signing certificate.

The rolling/displayed `target_commitish` is not trusted. Missing, malformed, ambiguous,
foreign, conflicting, or unverifiable evidence refuses without mutation. The resulting
evidence, including the authenticated APK asset's exact API-provided download URL, is
transferred by exact artifact ID with archive-digest enforcement. Prepare links the
version directly to that authenticated APK URL in its compact summary.

### Hold

The write-capable job reauthenticates the evidence and remote Release, tag, and assets.
Immediately before mutation it proves that the same Release is still `/releases/latest`.
It shares the `mosaic-development-release` concurrency domain with publication and
Stable Promotion. The job alone is attached to the protected `release-hold`
Environment; Environment approval authorizes the human mutation decision but does not
replace any technical authentication.

The only mutation is:

```json
{
  "prerelease": true,
  "make_latest": "false"
}
```

The Release, tag, APK, manifest, immutable Development Release, and all provenance are
preserved. Assets are not deleted or replaced; tags are not moved; nothing is rebuilt
or resigned. Hold is not successful until it also proves that the held Release ID is no
longer returned by `/releases/latest`. It reports either the previous fully authenticated
eligible Stable linked to its exact API-provided APK URL, or `No release available`.
An invalid fallback or a still-advertised held Release fails Hold.

## Accidental-repeat guard

GitHub may make the preceding Stable current after N is held. A second zero-input run
must not blindly hold N-1. Before both authentication and mutation, Hold Release scans
the Release inventory and refuses when a higher-numbered, non-draft Stable prerelease
already exists. That is native durable evidence that a newer Stable was held and that
the operator must forward-fix instead.

This guard still permits a future N+1 to be held: the historical held N is lower than
the then-current version and therefore does not match. It introduces no unhold state or
custom remediation journal.

## Updater effects

Stable discovery remains GitHub `/releases/latest`, and the updater still offers an
update only when the available semantic version is greater than the installed version.

- Clients below held N may see the previous eligible Stable.
- Clients already on N do not downgrade and wait for N+1.
- If no prior eligible Stable exists, no Stable is advertised.
- If N broke updating, the recovery path is manual installation of a correctly signed
  higher-version APK.

No updater change is part of I07.

## Security boundaries

- Prepare is read-only and has no Environment; only Hold has `contents: write` and uses
  `release-hold`.
- No signing credentials, Gradle, version allocation, build, or Release-asset mutation
  is reachable.
- Protected-main identity, current CI trust, historical producer provenance, exact
  artifact identity, APK verification, and signer policy remain fail closed.
- Concurrency plus an immediate `/latest` recheck protects against Stable promotion
  races.
- There is intentionally no unhold, rollback, repoint, or mutable target selection.

## Validation evidence

Offline fixtures cover:

- valid current Stable authentication and the exact hold mutation;
- no current Stable, malformed identity, missing/ambiguous assets, and foreign or
  changed provenance;
- archive/APK digest and signer mismatch;
- `/latest` changing between Prepare and Hold;
- tag and asset preservation;
- Hold confirmation with a prior Stable, with no Stable, and with the held Release still
  current;
- accidental repeated execution and cascade refusal;
- zero-input workflow shape, narrow write permissions, digest-enforced evidence
  transfer, and absence of signing/build/tag-deletion behavior.

Hosted acceptance is complete:

- Hold Release run `34690727709` authenticated Stable v1.0.5 in read-only Prepare,
  exercised `release-hold` approval, changed only Stable eligibility, preserved release
  `385512947`, its `mosaic-v1.0.5` tag and exact APK/manifest assets, and confirmed that
  `/releases/latest` returned no eligible Stable.
- The forward fix produced Development v1.0.34 / `downstream-build-34` from source
  `b78fcaa65f61d5e2b77070e7845820c5e3aa393c`, with signed APK SHA-256
  `1d84dfb922765b28f75e422e25b7fbdc5123beb86fc0148d5e324f5547514e5d`.
- The first Sign attempt failed only because the newly renamed `release-sign`
  Environment had not yet received the existing four signing secrets. After those
  credentials and the main-only deployment restriction were configured, **Re-run
  failed jobs** retained successful validation and Build, reran Sign successfully, and
  completed Publish. This independently reconfirmed native Case A recovery after the
  Environment migration.
- Stable Promotion run `34694610864` authenticated `downstream-build-34`, exercised
  `release-promote` approval, and published Stable release `387569996`. Stable v1.0.34
  became `/releases/latest`; v1.0.5 remains the preserved held prerelease. Development
  and Stable APK assets have the same signed SHA-256 above.

Stable Promotion is now a zero-input **Prepare â†’ Release** workflow. Prepare resolves
the current rolling `develop` publication, proves its exact immutable Development
identity and bytes, and presents the candidate. Release reauthenticates protected main,
rolling `develop`, the immutable tag/release, provenance, and exact APK after
`release-promote` approval; any movement refuses rather than silently changing the
approved candidate.

## Rejected machinery

The original design considered Development withdrawal/repoint, Stable rollback,
operator-selected targets, resumable remediation state, and generic recovery workflows.
They were rejected because forward-fix is the only path that helps devices already on a
bad build, native failed-job reruns already cover delivery failures, downgrade is not a
normal updater behavior, and these mechanisms would add mutable authority without a
demonstrated consumer. Hold Release is retained only because immediately stopping new
Stable propagation protects a distinct incident-response requirement while N+1 is
prepared.
