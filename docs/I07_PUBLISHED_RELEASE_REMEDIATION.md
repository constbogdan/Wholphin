# I07 — Published Release Remediation

## Status

**Simplified design implemented and offline validated; hosted live acceptance remains.**

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

The manually dispatched, zero-input [Hold Release workflow](../.github/workflows/mosaic-hold-release.yml)
has one responsibility:

```text
Run workflow
    ↓
Get Release
    ↓
Hold
    ↓
Confirm
```

It resolves `GET /repos/constbogdan/Wholphin/releases/latest`; the operator does not
select a version, release, target, reason, or replacement.

### Get Release

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
evidence is transferred by exact artifact ID with archive-digest enforcement.

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
or resigned.

### Confirm

Confirmation proves that the held Release is a published prerelease and that its exact
Release ID is no longer returned by `/releases/latest`. It reports either the previous
eligible Stable selected by GitHub or `none`. An invalid fallback or a still-advertised
held Release fails the workflow.

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

- Get Release is read-only; only Hold has `contents: write`.
- Get Release and Confirm have no Environment; only Hold uses `release-hold`.
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
- `/latest` changing between Get Release and Hold;
- tag and asset preservation;
- Confirm with a prior Stable, with no Stable, and with the held Release still current;
- accidental repeated execution and cascade refusal;
- zero-input workflow shape, narrow write permissions, digest-enforced evidence
  transfer, and absence of signing/build/tag-deletion behavior.

Repository validation and hosted mutation acceptance remain required before this is an
operational capability.

## Live acceptance remaining

With explicit authorization, dispatch Hold Release only against a deliberately selected
current Stable incident/test release and record:

1. Get Release authenticates the exact current Stable without mutation.
2. Hold changes only `prerelease` and latest eligibility.
3. The tag, APK, manifest, digests, and provenance are unchanged.
4. Confirm observes the held ID absent from `/latest` and reports the correct fallback
   or `none`.
5. An immediate second dispatch refuses before mutation rather than cascading.
6. Normal forward-fix and Stable Promotion of N+1 restore the advertised channel.

After that acceptance, I07 is complete. No additional rollback/repoint framework or
Development remediation remains planned.

## Rejected machinery

The original design considered Development withdrawal/repoint, Stable rollback,
operator-selected targets, resumable remediation state, and generic recovery workflows.
They were rejected because forward-fix is the only path that helps devices already on a
bad build, native failed-job reruns already cover delivery failures, downgrade is not a
normal updater behavior, and these mechanisms would add mutable authority without a
demonstrated consumer. Hold Release is retained only because immediately stopping new
Stable propagation protects a distinct incident-response requirement while N+1 is
prepared.
