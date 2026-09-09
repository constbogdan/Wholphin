# Mosaic Release signing contract

Status: permanent Release signing identity ESTABLISHED; isolated signing exercise
IMPLEMENTED, awaiting first authorized live run after merge. The user reports the
`mosaic-release-signing` Environment restricted to main and all four Environment
secrets configured externally. Reviewer/bypass settings were not independently verified.
Real isolated CI signing remains untested. Updater routing and rolling develop/stable
publication remain disabled. No live signing was dispatched by Codex.

## Implemented manual hosted exercise

Workflow: [.github/workflows/mosaic-signing-exercise.yml](../.github/workflows/mosaic-signing-exercise.yml).
It accepts only workflow_dispatch in constbogdan/Wholphin on protected main, with
`expected_sha` exactly matching the dispatch SHA. No caller-supplied ref/artifact/run
can select a different build. This checkpoint supersedes future-only signing-job
statements in the original architecture below.

The build job runs offline acceptance, pre-commit, the existing Full Debug validation
graph plus defaultRelease unsigned assembly and its existing vital checks in one Gradle invocation.
Version allocation now also accepts explicitly SHA-authorized protected-main manual
exercises; ordinary PR/arbitrary-branch publication identities remain rejected.
No environment/signing credentials exist in the build job. This manual exercise
revalidates main rather than trying to promote an unrelated PR merge artifact.
Ordinary CI and its required check identity are unchanged. An exploratory full
Release lint run reported 252 errors/106 warnings, including generated Seerr API-level
usage; no baseline/suppression was added. Comprehensive lint remediation is separate
from this exercise. The workflow retains existing Full CI and assembly/vital checks.

The fresh signer job downloads only the successful build job's immutable artifact ID
from the same workflow run. Before secrets, it recomputes exact source/version identity,
checks unsigned APK hash/run/attempt, rejects prior signatures and checks alignment.
The secret-bearing step executes SDK apksigner only, without checkout, local scripts
or Gradle. Private tool diagnostics are suppressed; an EXIT trap removes the private
temporary directory. Secrets are step-scoped and no cache is used in the signing job.
After cleanup, public helpers compare all non-signature ZIP payload entries and run
verify_mosaic_apk.py for the pinned signer, Release package and allocated version.

Artifacts (7 days):

- `unsigned-mosaic-signing-exercise-1.0.N-<full-sha>-run-<run-id>-attempt-<attempt>`:
  exact universal unsigned defaultRelease APK and its source/run/hash provenance.
- `signed-mosaic-signing-exercise-1.0.N-<full-sha>-run-<run-id>-attempt-<attempt>`:
  `Mosaic-release.apk` and `verification.json` with source provenance, unsigned and
  signed SHA-256 hashes, package/version and certificate SHA-256.

The job summary links the signed artifact using the upload action's generated URL.
Download with `gh run download <run-id> --repo constbogdan/Wholphin --name <signed-artifact-name>`;
install the extracted Release APK with `adb install -r Mosaic-release.apk` for a
separately authorized device test. This is the permanent Mosaic Release identity,
not Debug; record any installed exercise version before later release testing.
Artifacts are temporary exercise evidence, not a durable accepted-release ledger.
Rebuilds may differ in bytes: do not treat a rerun as a published identity or promote
exercise APKs to a release. Durable no-replacement enforcement remains required before
publication. Rerun the entire workflow, not only failed signing jobs: provenance binds
the run attempt and deliberately rejects artifacts from an earlier attempt.

After this workflow reaches main, separately authorize a specific SHA and run:

```powershell
$exerciseSha = gh api repos/constbogdan/Wholphin/commits/main --jq .sha
$exerciseSha
# Review and authorize this exact SHA before dispatching:
gh workflow run mosaic-signing-exercise.yml --repo constbogdan/Wholphin --ref main -f "expected_sha=$exerciseSha"
```

If main moves between lookup and dispatch, the gate rejects the mismatch. Reassess the
new SHA before trying again. Apply any configured Environment approval; do not bypass
it. No tags, GitHub Releases, updater changes or Contents write are part of this run.

## Public custody checkpoint (2026-09-09)

The user reports successful permanent-key creation and recovery acceptance: two
independent encrypted backups exist; restore, file-hash comparison, certificate
verification and restored private-key-access verification all succeeded. This is
user-confirmed custody evidence, not a CI signing acceptance result. Only the public
certificate fingerprint is repository-visible; keystore/passwords/private material
remain user-controlled and must never be requested, read or handled by Codex.

Approved Release certificate SHA-256:

```text
63:75:61:83:D6:E7:7B:2A:5E:7C:D6:9B:40:95:32:EE:0B:3C:47:10:E1:3A:10:22:8D:FB:58:18:6F:55:6B:84
```

## Existing support and repository preparation

Release ID is `io.github.constbogdan.mosaic`; Debug adds `.debug`. Kotlin namespace
remains `com.github.damontecres.wholphin`. Gradle now explicitly leaves Release unsigned:
the inherited CI keystore decoding and local signing override were removed. Debug
keeps normal Android Debug signing. No Mosaic signing secret is passed to Gradle.
This intentionally replaces upstream's in-build SIGNING_KEY/KEY_ALIAS/KEY_PASSWORD/
KEY_STORE_PASSWORD mechanism. Inherited main.yml/release.yml retain upstream-only
guards; they remain disabled in our fork. Do not remove those guards to enable Mosaic.

Current Full CI builds universal and ABI defaultDebug APKs; only the universal PR APK
is retained for seven days. It is not a Release signing input. The manual main-only exercise
build adds defaultRelease assembly/release checks to the authoritative graph,
once, using `-PmosaicPublication=true` in a clean exact authorized main checkout.
Output selection must use the UNIVERSAL entry in
`app/build/outputs/apk/default/release/output-metadata.json`, not a wildcard that
could collect Debug/split/stale files. Only the explicit manual exercise retains main Release artifacts.

## Environment and credentials (externally configured by user)

Environment name: **mosaic-release-signing**. Select only protected `main` for signing;
exclude PRs, arbitrary branches and all tags initially. Stable later promotes already
signed main bytes rather than signing tag code. Require owner approval, prevent bypass
where supported, and prevent self-review if a separate reviewer is available. With
one owner, ensure the chosen review policy actually permits the intended manual
approval; audit GitHub plan/repository support before configuring it. Do not weaken
PR isolation to work around Environment limitations. Unattended signing requires a
separate explicit bounded standing authorization.

Environment secrets, entered manually by the user:

| Name | Meaning |
| --- | --- |
| MOSAIC_SIGNING_KEY | Base64-encoded PKCS12 keystore; encoding is not encryption. |
| MOSAIC_KEY_ALIAS | `mosaic-release` |
| MOSAIC_KEYSTORE_PASSWORD | Strong keystore password. |
| MOSAIC_KEY_PASSWORD | Key password; for the recommended PKCS12 setup, use the same password. |

No repository-level signing secrets and no fallback to upstream or Sync Bot names.
The expected public certificate SHA-256 belongs in reviewed
[mosaic-signing.json](../scripts/mosaic-signing.json), pinned to the established
certificate above in lowercase unseparated hex. A missing, malformed or different
fingerprint fails verification; there is no trust-on-first-use. Never paste the keystore, base64, passwords or private keys.

Validation/build: Contents read, no signing Environment or secrets. Signing: Contents
read and artifact access only, no release-writing token. A future independent publisher
may use GITHUB_TOKEN Contents write after verification, without the signing key.
Do not reuse Wholphin Sync Bot, add a PAT or create a release App without demonstrated
need. Only the manual exercise signer step consumes these Environment secrets.

## Original architecture and future publication requirements

The original preparation contract below is retained for context; the implemented
exercise above establishes artifact transport and isolated signing. Durable publication
records and release promotion remain future work. Any later implementation must bind canonical repository, successful trusted main CI,
exact source SHA, run ID/attempt, immutable artifact ID/hash and expected workflow
identity before requesting approval. A self-reported provenance JSON alone is not
proof of trusted CI. Avoid workflow_run unless all these checks are implemented.

1. Build/test unsigned Release without secrets. Record source/version metadata with
   `mosaic_version.py --publication --apk <unsigned-apk>`; its `apkSha256` is the
   unsigned input hash. Capture run/artifact identity, SDK/build-tool/dependency inputs
   and mapping files. Allocate before generating unignored worktree files.
2. In a fresh signer job, install pinned trusted SDK tools BEFORE secret injection.
   Do not execute checkout/candidate Gradle, hooks, local Actions or downloaded scripts
   with the keystore present. Trusted reviewed signing orchestration must be pinned
   independently of arbitrary artifact contents. Download only the exact validated APK
   and public provenance; check the input hash and unsigned status before any signing.
3. Check alignment before signing (`zipalign -c -P 16 4 <unsigned-apk>`). If alignment
   needs changing, produce an explicit aligned intermediate and record its hash;
   never silently replace the validated input. No compilation/rebuild is allowed.
4. Decode the Environment keystore into a unique private runner-temp directory with
   restrictive permissions, shell tracing disabled. Do not print decoded or encoded
   content; keep it out of caches/artifacts. Remove temp key material and secret env
   on every exit, including failure. Codex must not execute this private-material path.
5. Sign to a distinct output using SDK apksigner, with password ENV REFERENCES:

   ```text
   apksigner sign --ks <private-runner-temp-keystore> --ks-type PKCS12 --ks-key-alias <alias> --ks-pass env:MOSAIC_KEYSTORE_PASSWORD --key-pass env:MOSAIC_KEY_PASSWORD --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true --v4-signing-enabled false --out <signed-apk> <unsigned-apk>
   ```

   This is a future trusted-runner command, not a command executed by Codex. v4 is
   deliberately disabled until a separately specified idsig lifecycle is needed.
   Do not alter APK contents after signing. Compare non-signature payload entries
   before/after signing; only expected APK/JAR signature additions may differ.
6. After key cleanup, run public verification (no keystore argument):

   ```text
   python scripts/verify_mosaic_apk.py --apk <signed-apk> --provenance <unsigned-provenance.json> --apksigner <sdk-apksigner> --aapt <sdk-aapt> --output <new-public-record.json>
   ```

   The prepared verifier requires SDK signature verification success, one matching
   signer, non-debuggable Mosaic package, exact positive 1.0.N/code N, clean publication
   provenance and unsigned input hash. It records signer, input provenance and final
   APK SHA-256; output creation is exclusive to prevent overwriting accepted records.
   It does not authenticate workflow provenance or prove input/output payload equality;
   those remain signer-job responsibilities above. It never reads a keystore.
7. Before any future upload, compare against existing immutable accepted identity
   records and fail on different bytes/provenance for an existing N. Persist signed
   APK, fingerprint/hash/provenance record, input identity and mapping for the support
   lifetime in approved durable storage, with backup. Seven-day PR artifacts and logs
   are insufficient. Storage/publisher wiring is future work, not implemented here.

Reference: [Android apksigner](https://developer.android.com/tools/apksigner).

## Historical creation procedure: completed, do not regenerate

The permanent key already exists. Retain these commands as historical reference,
not a next action or authorization to replace it.

Use a private terminal outside the repository and outside Codex/shell transcription.
Choose a secured directory outside source trees, cloud-sync and build caches. The
following example uses `D:\Mosaic-Key-Custody`; create/select a suitable private
directory yourself. If the target file already exists, STOP: do not replace an
existing permanent identity. Passwords are prompted, never put on command lines.

```powershell
keytool -genkeypair -keystore "D:\Mosaic-Key-Custody\mosaic-release.p12" -storetype PKCS12 -alias mosaic-release -keyalg RSA -keysize 4096 -sigalg SHA256withRSA -validity 10000
keytool -list -v -keystore "D:\Mosaic-Key-Custody\mosaic-release.p12" -storetype PKCS12 -alias mosaic-release
```

The second command displays the public certificate SHA256 fingerprint. Send only the
SHA256 hex value, optionally colon-separated; do not send full terminal transcripts.
Record alias, creation/expiry dates, certificate fingerprint and custody locations in
your password manager/offline custody record. DN fields become public certificate
metadata: use truthful values you are comfortable making public. No signing key has
been created by this task. [keytool reference](https://docs.oracle.com/en/java/javase/21/docs/specs/man/keytool.html).

## Backup and recovery procedure (initial acceptance completed)

Maintain one permanent key with at least TWO encrypted backups stored independently,
for example separate encrypted offline media/locations. Keep recovery passwords
available independently; neither GitHub nor one machine is the sole backup. Never
commit keystores/private keys or upload them as Actions artifacts. Ignore patterns
are accidental-commit protection, not permission to place private material in Git.

Before first Release, restore a backup to another secured directory without overwriting
the working copy. Compare original/restored file SHA256 locally, then verify readability:

```powershell
Get-FileHash "D:\Mosaic-Key-Custody\mosaic-release.p12" -Algorithm SHA256
Get-FileHash "E:\Mosaic-Restore-Test\mosaic-release.p12" -Algorithm SHA256
keytool -list -v -keystore "E:\Mosaic-Restore-Test\mosaic-release.p12" -storetype PKCS12 -alias mosaic-release
```

Confirm matching file hashes, alias, PrivateKeyEntry, certificate SHA256 and validity.
Listing proves the store can be read; additionally prove restored private-key use with
a local throwaway CSR (not sent to any CA), using only the restored keystore:

```powershell
keytool -certreq -keystore "E:\Mosaic-Restore-Test\mosaic-release.p12" -storetype PKCS12 -alias mosaic-release -file "E:\Mosaic-Restore-Test\restore-check.csr"
keytool -printcertreq -file "E:\Mosaic-Restore-Test\restore-check.csr"
```

Record successful restore/read/private-key-use verification privately. Securely manage
the restored copy and disposable CSR yourself; Codex must not inspect them. No APK
or permanent private key is generated by the restore test. Losing the key without
recovery ends compatible sideload updates; a replacement key generally means a new
installation/migration. Rotation requires a separately validated supported lineage,
not simply replacing the keystore. Debug key reset is not Release key recovery.

## Next authorization boundary

External Environment/secret configuration is user-confirmed complete; no further
settings changes are requested by this task. Review and merge the implementation
separately, then authorize the exact protected-main dispatch described above. The
first successful live run must verify the public record and artifact; device runtime
acceptance is separate. Updater migration and rolling/stable publication remain disabled.
