# Baseline T0-1 operator UX, workflow, and presentation inventory

Status: **CP2 COMPLETE — OBSOLETE SURFACES REMOVED**
Next: **T0-1 CP3 — Low-risk names and summaries**

This is the authoritative execution ledger for T0-1. The inventory tables preserve the CP1
baseline; historical names in acceptance records are evidence, not active UX. CP2 removed only
the two obsolete inherited workflow surfaces and updated their ownership contract. It did not
rename a surviving surface, alter GitHub settings, or begin later presentation/performance work.

## CP2 implementation record

- Removed `.github/workflows/main.yml` (`Development build`). Its only job was restricted to the
  upstream repository, and Mosaic's `CI` already exclusively owns supported Development Build,
  Sign, and Publish delivery.
- Removed `.github/workflows/release.yml` (`Create release`). Its default APK role was superseded
  by Stable Promotion, and Baseline T0 explicitly does **not** own Appstore or Fire TV AAB
  distribution. If either store becomes a product requirement, it needs a deliberately supported
  pipeline rather than restoration of this secret-bearing inherited workflow.
- Both removed paths are explicit `DOWNSTREAM-OWNED` absences in
  `scripts/upstream_ownership_policy.json`. I06 still observes upstream changes and records their
  evidence, but preserves the downstream deletion instead of resurrecting either publisher.
- No helper became dead: both removed workflows were self-contained. Gradle's Appstore/Fire TV
  flavors remain application build capability, not a currently supported Mosaic distribution
  channel. Historical AAB behavior remains documented in the Item 6 audit.
- Focused local evidence: all 54 hosted-upstream fixtures and all 10 delivery/presentation tests
  pass. The former proves approved absence, REVIEW fallback, native candidate safety, retries and
  refusals; the latter proves the supported workflow file set is exactly the five workflows below.
- Classification after moving this durable ledger under `docs/`: the complete branch is
  `tooling-only / high`, selects Full validation because it changes security-sensitive workflow
  ownership, and correctly has `releaseRequired=false` because it changes no APK input.
- The supported Actions surface is now the five workflows listed below. Hosted confirmation that
  GitHub's sidebar has dropped the deleted workflow entries remains a post-merge observation, not
  a reason to retain executable dead files.

## Method and boundaries

The CP1 audit covered all seven files then under `.github/workflows`, both composite actions,
Python and PowerShell operator-output producers, PR templates/tooling, release helpers, validation
helpers, active tests that bind presentation, and documentation that identifies external/manual
contracts. It found **114 YAML workflow/action name declarations** (workflow, run, job, step, and
composite-action names) plus **31 generated presentation families** in scripts/templates: **145
human-visible labels or label families** in the CP1 baseline before ordinary Git/Gradle tool output.

Registry rows below consolidate repeated setup/checkout/upload labels only when they share one
producer, risk, and recommended treatment. `LOW`, `MEDIUM`, and `HIGH` refer to migration risk, not
quality. `HIGH` means the label or adjacent identity participates in a ruleset, lookup,
authentication, provenance, evidence reuse, or externally configured contract.

## Workflow registry

| Workflow | File | Trigger | Purpose | Current operator value | Recommendation |
|---|---|---|---|---|---|
| `CI` | `.github/workflows/ci.yml` | PR to `main`; push to `main`; manual | Risk-tiered PR validation, protected-main exact-tree reuse/fallback, Development Build → Sign → Publish | Essential; one run owns validation and Development delivery | **KEEP**; presentation cleanup only until coordinated `Full validation` migration |
| `Hold Release` | `.github/workflows/hold-release.yml` | Manual on protected `main` | Authenticate current Stable, await `release-hold`, stop advertising it | Essential emergency Stable containment | **KEEP** |
| `Mosaic — Stable Promotion` | `.github/workflows/mosaic-stable-promotion.yml` | Manual on protected `main` | Authenticate current Development, await `release-promote`, publish exact bytes as Stable | Essential normal Stable promotion | **RENAME** display to `Stable Promotion`; preserve file/API/provenance identities |
| `Mosaic — Signing Diagnostic` | `.github/workflows/mosaic-signing-exercise.yml` | Manual with exact-main SHA | Non-publishing signing credential/certificate diagnostic | Legitimate after key/secret/Environment changes, but expensive and asks the operator to repeat `github.sha` | **RENAME** to `Signing Diagnostic` and **SIMPLIFY** to authenticated zero-input current main in a later checkpoint |
| `Upstream — Synchronization` | `.github/workflows/upstream-sync.yml` | Fixed schedule and manual | Observe/classify upstream; create/reuse native normal/Draft candidate | Essential I06 operator surface | **RENAME** display to `Upstream Synchronization`; preserve workflow path, outcomes and evidence contracts |
| `Development build` | `.github/workflows/main.yml` | Push to `main` or `develop/*`; job restricted to `damontecres/Wholphin` | Inherited upstream rolling build/release | No downstream job could run; the row duplicated CI-owned Development delivery | **REMOVED IN CP2**; path remains an explicit downstream-owned absence |
| `Create release` | `.github/workflows/release.yml` | `v*` tag; job restricted to `damontecres/Wholphin` | Inherited upstream signed APK/AAB/mapping draft release | Could not run downstream; default APK/Stable responsibility was superseded and store/AAB distribution is outside Baseline T0 | **REMOVED IN CP2**; historical AAB evidence retained, path is downstream-owned absence |

### Removal evidence and CP2 decisions

- `main.yml` has no downstream execution path: its sole job requires
  `github.repository == 'damontecres/Wholphin'`. Current `.github/workflows/ci.yml` owns the only
  supported Development Build, Sign, and Publish chain. Repository search found only policy,
  fixtures, tests, and historical docs consuming its path/name; no runtime artifact consumer.
- `release.yml` was equally upstream-repository guarded. Its default APK release is superseded by
  zero-input Stable Promotion. It uniquely documented/built `bundleAppstoreRelease` and
  `bundleFiretvRelease` AABs, but Mosaic has no store publication contract or AAB consumer.
  Baseline T0 now explicitly defers those channels; removal does not imply AAB support moved.
- Neither inherited workflow should be consolidated into CI. They should disappear, not create a
  second publisher or release authority.

## Actions sidebar

### CP1 baseline sidebar

```text
CI
Create release
Development build
Hold Release
Mosaic — Signing Diagnostic
Mosaic — Stable Promotion
Upstream — Synchronization
```

### Supported sidebar after CP2

```text
CI
Hold Release
Mosaic — Signing Diagnostic
Mosaic — Stable Promotion
Upstream — Synchronization
```

### Proposed final sidebar after later presentation checkpoints

```text
CI
Hold Release
Signing Diagnostic
Stable Promotion
Upstream Synchronization
```

| Current | Final | Decision | Constraint |
|---|---|---|---|
| `CI` | `CI` | KEEP | Renaming changes `CI / Full validation`, a required and authenticated check contract |
| `Create release` | absent | REMOVED IN CP2 | Store/AAB distribution is deliberately unsupported in Baseline T0 |
| `Development build` | absent | REMOVED IN CP2 | Downstream CI already owns Development delivery |
| `Hold Release` | unchanged | KEEP | Already concise and operator-oriented |
| `Mosaic — Signing Diagnostic` | `Signing Diagnostic` | RENAME/SIMPLIFY | Tests/docs bind display; path/artifact/auth contracts remain |
| `Mosaic — Stable Promotion` | `Stable Promotion` | RENAME | Tests/docs bind display; file and release contracts remain |
| `Upstream — Synchronization` | `Upstream Synchronization` | RENAME | Tests/docs bind display; workflow path and evidence consumers remain |

Repository context makes the `Mosaic —` and `Upstream —` prefixes redundant. This is not permission
to rename `CI`, job IDs, workflow filenames, tags, artifacts, Environments, or classifier values.

## Presentation registry

| ID | Surface/type | Current label(s) | Producer | Proposed human presentation | Contract? | Risk |
|---|---|---|---|---|---|---|
| P01 | Workflow/check | `CI` | `ci.yml:1` | Keep | GitHub ruleset/check prefix | HIGH |
| P02 | CI run | `PR #N · branch`; native push title; `Validate · branch` | `ci.yml:2-7` | Keep; already identifies context | Tests/docs | MEDIUM |
| P03 | CI job/check | `Full validation` | `ci.yml:33` | Deferred coordinated migration to `Prepare` | Ruleset, reuse, provenance, upstream selection | HIGH |
| P04 | CI validation steps | `Classify PR validation`; pre-commit; offline fixtures; full/targeted validation | `ci.yml:45-121` | `Plan validation`; `Check changed files`; `Run tooling tests`; `Validate application` | Tests and conditional structure | MEDIUM |
| P05 | PR APK steps | locate/record/upload/summarize PR test APK | `ci.yml:123-205` | `Prepare test APK`; one result statement, evidence collapsed | Artifact/evidence identity adjacent | HIGH |
| P06 | PR policy summary | `Mosaic PR validation`, `release relevance`, `validation risk`, `selected path` | `ci.yml:245-287` | `Validation plan/result`; translate to plain reason and release consequence | Classifier values remain machine contract | MEDIUM |
| P07 | Main reuse summary | `Protected-main validation`; executed/reused reason | `ci.yml:207-243` | `Full validation reused from PR #N` or `Full validation required — reason` | Reuse evidence fields | HIGH |
| P08 | Development jobs | `Build Development Release`; `Sign Development`; `Publish Development` | `ci.yml:301,384,454` | `Build`; `Sign`; `Publish` after tests/contracts migrate | Tests, provenance docs; job IDs remain stable | MEDIUM |
| P09 | Development classification | `Classify complete unpublished Development range` | `ci.yml:327`, `mosaic_development_release.py:368-413` | Early `Release plan`: build required/not required and why | Outputs drive jobs | HIGH |
| P10 | Release build steps | setup/build/prepare/upload authoritative unsigned Release | `ci.yml:332-352` | Concise verbs; hide “authoritative” from primary labels | Artifact ID/name/provenance remain | MEDIUM |
| P11 | Mapping steps/summary | retain/upload/summarize Release mapping diagnostic | `ci.yml:354-381` | `Save diagnostic mapping`; technical link collapsed | Artifact identity | MEDIUM |
| P12 | Sign steps | require ID, verify input, sign, verify payload | `ci.yml:408-452` | `Authenticate unsigned APK`; `Sign`; `Verify signed APK` | Security boundary | HIGH |
| P13 | Publish steps | require ID, validate manifest, publish bytes | `ci.yml:468-483` | `Authenticate signed APK`; `Publish Development` | Publication boundary | HIGH |
| P14 | Development artifacts | `unsigned-mosaic-main-ci-…`; `signed-mosaic-development-…`; `mapping-…` | `ci.yml`, signing/release helpers | Keep machine names; show `Development vX` outside details | Exact artifact auth | HIGH |
| P15 | Development Releases | tags `downstream-build-N`, `develop`; title/body `Mosaic vX — Development [Build N]` | `mosaic_delivery_output.py:17-36` | Human: `vX-N-gSHA — Development`; machine tags unchanged; deferred compatibility audit | Updater reads Release `name`; tags/manifests | HIGH |
| P16 | Development result | `Published · Mosaic vX` plus source/hash/run | `mosaic_delivery_output.py:39-57` | `Published Development vX`; main result visible, evidence collapsed | Tests/docs | MEDIUM |
| P17 | Stable workflow/run | `Mosaic — Stable Promotion`; `Stable Promotion` | `mosaic-stable-promotion.yml:1-2` | `Stable Promotion` | Tests/docs, not file identity | MEDIUM |
| P18 | Stable jobs | `Prepare`; `Release` | `mosaic-stable-promotion.yml:21,74` | Keep | Environment boundary/operator model | MEDIUM |
| P19 | Stable prepare steps | resolve/authenticate; certificate/package/version; manifest/hash | stable workflow lines 43-54 | `Authenticate Development candidate`; details collapsed | Security/provenance | HIGH |
| P20 | Stable summaries | `Ready to release`; `Promoted · Mosaic vX`; failed stage | stable workflow; `mosaic_delivery_output.py` | `Ready to release: vX`; `Released: vX`; explicit next action/refusal | Tests/docs | MEDIUM |
| P21 | Stable artifact | `stable-downstream-build-N-run-R-attempt-A` | stable workflow line 63 | Keep machine name; display `Stable vX evidence` | Exact handoff/auth | HIGH |
| P22 | Stable Release | tag `mosaic-vX`, name/version `vX`, exact Development bytes | `mosaic_stable.py`, delivery output | Human `vX — Stable`; retain machine tag/update compatibility | Updater/provenance | HIGH |
| P23 | Hold workflow/run/jobs | `Hold Release`; `Prepare`; `Hold` | `hold-release.yml` | Keep | Tests/docs and Environments | MEDIUM |
| P24 | Hold steps | `Get Release`; long authentication label; artifact requirement; `Hold` | hold workflow | `Find current Stable`; `Authenticate Stable`; `Hold Release` | Security sequence | MEDIUM |
| P25 | Hold summaries | `Ready to hold`; `Held: ✕ … → …`; `Refused` | hold workflow; `mosaic_hold_release.py` | Keep result; replace symbols with accessible words where useful | Tests/docs | MEDIUM |
| P26 | Hold artifact | `hold-release-ID-run-R-attempt-A` | hold workflow line 66 | Keep machine name; collapse exact identity | Exact handoff/auth | HIGH |
| P27 | Signing workflow/run | `Mosaic — Signing Diagnostic`; `Diagnose signing from SHA` | signing workflow lines 1-2 | `Signing Diagnostic`; run `Signing diagnostic · current main` | Tests/docs | MEDIUM |
| P28 | Signing input | required `expected_sha` | signing workflow lines 5-10 | Zero input; authenticate dispatched protected-main `github.sha` | Current authorization predicate | HIGH |
| P29 | Signing jobs/steps | long validate/build/sign/verify labels | signing workflow lines 28-142 | `Prepare diagnostic APK`; `Sign and verify`; concise substeps | Security boundaries/tests | MEDIUM |
| P30 | Signing artifacts | `unsigned/signed-mosaic-signing-exercise-…` | workflow and `mosaic_signing_exercise.py` | Preserve exact names; show signed diagnostic version prominently | Artifact validation | HIGH |
| P31 | Signing result | `Mosaic signing diagnostic verified`, artifact/source/retention | signing workflow line 133 | `Signing verified`; action/no-publication statement visible; details collapsed | Tests/docs | MEDIUM |
| P32 | Upstream workflow/run | `Upstream — Synchronization`; `Observe upstream · event` | upstream workflow lines 1-2 | `Upstream Synchronization`; `Upstream check · Scheduled/Manual` | Tests/docs | MEDIUM |
| P33 | Upstream jobs/steps | `Observe upstream integration`; read-only attempt; retain; publish/recheck | upstream workflow | `Observe`; `Publish candidate`; concise authentication verbs | Credential/condition structure | MEDIUM |
| P34 | Upstream outcomes | `No upstream delta`; `Ready candidate`; `Review required · Draft candidate`; etc. | `hosted_upstream.py:333-369` | Plain first-line counts/result/action; keep machine outcome in details | Tests and operational semantics | MEDIUM |
| P35 | Ownership classes | `FOLLOW`, `REVIEW`, `DOWNSTREAM-OWNED` | ownership policy/hosted summary | Keep machine tokens in evidence; explain as “integrate”, “review”, “preserve Mosaic” | Policy/classification | HIGH |
| P36 | Upstream PR titles | `chore: synchronize official upstream`; `chore: review upstream changes to …` | `hosted_upstream.py:323-330` | `Sync official upstream`; `Review upstream changes: area` | Tests/dedup uses branch/evidence, not title | MEDIUM |
| P37 | Upstream PR body | incoming/attention counts, filenames, run link, `<details>` evidence | `hosted_upstream.py:271-321,747-762` | `What changed / Why review / Validation / Next`; retain details collapsed | Episode marker/evidence embedded | HIGH |
| P38 | Upstream artifacts | `upstream-observation-A`; `upstream-outcome-A` | upstream workflow | Keep machine names; show operator result in summary | Resolver retrieval/auth | HIGH |
| P39 | Resolver CLI | candidate list, dependency states, publication plan, `Ready to PUSH?` | `resolve_upstream.py:604-843` | Sentence case; lead with action and next step; technical identities in prompt/log | Tests/operator contract | MEDIUM |
| P40 | Resolver prompt | Incoming, attention, CI, constraints, exact evidence | `resolve_upstream.py:692-809` | Keep bounded handoff; collapse/reference machine evidence where safe | Semantic safety contract | HIGH |
| P41 | Prepare-pr phases | uppercase `AUDIT/VALIDATE/STAGE/COMMIT/PUBLISH`, `[RUN/PASS/FAIL]` | `prepare-pr.ps1` | Title case lifecycle with one-line intent/result | Tests/log parsers | MEDIUM |
| P42 | Prepare-pr scope | `TOTAL COMPLETE PR SCOPE`; tracked/untracked/raw stats | `prepare-pr.ps1:387-479` | `PR scope: N files`; details collapsed/logged | Snapshot confirmation | HIGH |
| P43 | Prepare-pr title | Conventional title inferred from branch | `prepare-pr.ps1:600-627` | Keep concise conventional title; allow explicit human title | Commit/PR title, tests | MEDIUM |
| P44 | Generated PR body | Description/title; Confirmed paths; application/UI flags; Testing; review-sensitive; docs/screenshots/AI | `prepare-pr.ps1:665-719`, PR template | Default `What changed / Why / Validation / Next`; collapse paths/evidence | Template/tests/review process | MEDIUM |
| P45 | Prepare-pr completion | PR URL, `Required CI / Full validation pending`, `Review/merge in GitHub` | `prepare-pr.ps1:769-784` | Add auto-merge armed/not armed and direct next action | GitHub capability/settings | MEDIUM |
| P46 | Prepare-pr logs | `prepare-pr.log`, `.logs/prepare-pr/<run>` | `prepare-pr.ps1`, `.gitignore` | Keep machine-safe names; show one final location | Local compatibility | LOW |
| P47 | Local validation plan | `Wholphin validation`; requested level; relevance/risk/path | `validate-local.ps1:112-118` | `Validation plan`; plain reason and actual checks | Classifier values in log only | MEDIUM |
| P48 | Local validation progress | `[N/T] stage [RUN/PASS/FAIL] duration → log` | `mosaic_output.ps1` | Keep concise lifecycle; sentence-case stages | Tests/operators | MEDIUM |
| P49 | Local validation result/logs | final success/failure, `.logs/validation`, `validation.log` | output/validation scripts | Keep visible; technical excerpt and logs progressive | Compatibility log consumer | MEDIUM |
| P50 | Shared setup/action labels | `Setup`, SDK/tool setup, `Sign exact Mosaic APK` | `.github/actions/*/action.yml` | `Set up Android build`; `Sign APK`; keep internal action paths | Multiple workflows/tests | MEDIUM |
| P51 | Inherited Development labels | workflow/build/sign/checksum/delete release | `main.yml` | Removed with workflow in CP2 | Downstream-owned absence | LOW |
| P52 | Inherited tag-release labels | `Create release`, build/AAB/mapping/draft Release | `release.yml` | Removed in CP2 after AAB ownership decision | Downstream-owned absence | MEDIUM |

Presentation registry: **52 grouped rows** — **2 LOW**, **30 MEDIUM**, **20 HIGH**. The most
important non-cosmetic labels are `CI`, `Full validation`, artifact names, tags/Release names,
Environment names, ownership tokens, embedded PR evidence markers, and exact SHA/run/tree fields.

## PR presentation audit

There are two automated PR producers:

1. `scripts/prepare-pr.ps1` generates a Conventional Commit title from the task branch (or explicit
   `-Title`) and a large body with Description, Confirmed paths, application/UI flags, Testing,
   Review-sensitive paths, Documentation, Screenshots, and AI/LLM usage. The default view repeats
   raw paths already available in GitHub Files changed and leaves “why”/“what next” partly implicit.
2. `scripts/hosted_upstream.py` creates a normal FOLLOW title or area-based REVIEW/conflict title.
   Its body correctly keeps exact technical evidence collapsed, but should foreground why human
   attention is or is not needed, validation state, and the next semantic action.

`.github/pull_request_template.md` supplies the manual fallback structure; no other active
maintenance workflow creates PRs. Recommended default body order is **What changed → Why →
Validation/result → What happens next**, followed by collapsed Confirmed Paths, review-sensitive
paths, provenance/authentication, and raw inventories. Never collapse the refusal, required operator
action, validation result, or Draft/ready state.

Prepare-pr currently creates/reuses the PR but neither enables nor arms auto-merge. It can invoke
`gh pr merge --auto --merge` after exact PR/head authentication for ordinary non-Draft PRs, but only
after repository auto-merge is enabled and the policy explicitly excludes upstream Drafts. That is
a process checkpoint with mocked/offline tests and hosted acceptance, not a cosmetic edit.

## Release and artifact presentation

| Channel | Human presentation today | Machine identity | Proposed later presentation |
|---|---|---|---|
| Development rolling | Release body `Mosaic vX — Development`; Release API name/version remains `vX`; result `Published · Mosaic vX` | tag `develop`; immutable `downstream-build-N`; manifest; exact signed artifact | `vStable-N-gSHA — Development`, Compare Changes from current Stable, primary install link; identities collapsed |
| Development immutable | `Mosaic vX — Development Build N` | tag/identity `downstream-build-N` | Treat as provenance/archive, not primary human release |
| Stable | name/title `vX`; body `Mosaic vX — Stable`; result `Promoted · Mosaic vX` | tag `mosaic-vX`; exact immutable source; manifest/APK digest | `vX — Stable`, Compare Changes from previous Stable, concise release result |

`UpdateChecker` compatibility makes Release `name`, tag, versionCode, filenames and manifest fields
HIGH-risk. The future Development version format is presentation work only after a dedicated
updater/versionCode/provenance audit. `Wholphin-release.apk` also remains a compatibility filename.

Operator-visible authenticated artifacts include PR Full Debug APK evidence, unsigned/signed main
Release handoffs, mappings, Stable verification evidence, Hold evidence, signing diagnostic
inputs/results, upstream observation/outcome, and failure diagnostics. Their long names are exact
machine identity and should not be prettified. Summaries should show `Development vX`, `Stable vX`,
`PR #N test APK`, or `Signing diagnostic vX`, with artifact IDs/names under Technical details.

Compare Changes belongs in Development bodies/summaries from current Stable source to Development
source, and in Stable bodies/summaries from previous Stable source to promoted source. Immutable
archive pages may retain exact source links without becoming the primary comparison surface.

## Output registry

| ID | Surface | Producer | Purpose / typical size | Default now | Available / shown | Recommendation |
|---|---|---|---|---|---|---|
| O01 | PR validation policy | `ci.yml` inline Python | decision + 2–4 checks, ~10 lines | visible | classification in seconds / end of validation job | REDESIGN SUMMARY |
| O02 | PR test APK | `ci.yml` inline Python | download + 8 identity fields/instructions, ~20 lines | visible | after Full / after Full | COLLAPSE |
| O03 | Main validation reuse | `ci.yml` inline Python | main result + tree/run evidence, 5–7 lines | visible | before Full / summary step after Full or skip | REDESIGN SUMMARY |
| O04 | Development eligibility | `mosaic_development_release.record_eligibility` | decision, SHAs, policy, full path list, variable | visible | start of Build job / after classification | REDESIGN SUMMARY |
| O05 | Release mapping | `ci.yml` printf | artifact URL/retention, 5 lines | visible | after Build / after upload | COLLAPSE |
| O06 | Development publication | `publication_summary` | release result + source/hash/build/run, ~10 lines | visible | after publish / after publish | REDESIGN SUMMARY |
| O07 | Stable prepare | stable workflow printf | ready version/link, 3 lines | visible | after authentication / after authentication | KEEP VISIBLE |
| O08 | Stable release/failure | `publication_summary`, workflow printf | result or failed stage, 5–10 lines | visible | after action / after action | REDESIGN SUMMARY |
| O09 | Hold prepare | hold workflow printf | ready version/link, 3 lines | visible | after authentication / after authentication | KEEP VISIBLE |
| O10 | Hold result/refusal | hold workflow/helper | held/fallback or refusal, 3–6 lines | visible | after recheck/mutation / immediately then | KEEP VISIBLE |
| O11 | Signing diagnostic | workflow printf | artifact/link/source/retention/no-publication, ~10 lines | visible | after sign / after sign | REDESIGN SUMMARY |
| O12 | Upstream Actions summary | `upstream_summary` | decision, policy counts, per-path lists, navigation, full JSON; tens/hundreds lines | visible | observation in seconds / at observation end | COLLAPSE |
| O13 | Upstream PR body | `candidate_body` | commits, attention, run, JSON, variable | evidence partly collapsed | at candidate creation / creation | REDESIGN SUMMARY |
| O14 | Resolver prompt | `codex_prompt` file | exact semantic task/evidence, large | file/log | after selection / immediately | MOVE TO ARTIFACT |
| O15 | Resolver CLI transcript | resolver print functions | candidates, dependencies, scope, filters, prompts, variable | visible | progressively / progressively | KEEP VISIBLE |
| O16 | Prepare-pr audit/transcript | `prepare-pr.ps1` | commits, every path/stat/risk/snapshot/commands, large | concise mode partly suppresses lists | early / progressively | MOVE TO LOG |
| O17 | Generated PR Confirmed Paths | `New-PullRequestBody` | complete raw path list, potentially large | visible | before PR / PR creation | COLLAPSE |
| O18 | Validation terminal | `validate-local.ps1`, `mosaic_output.ps1` | plan, one line/stage, concise result/log, bounded failure | visible | progressively / progressively | KEEP VISIBLE |
| O19 | Release bodies | `release_body` | purpose/version/build/source/hash/install/provenance, ~15 lines | visible | publication / publication | REDESIGN SUMMARY |
| O20 | Raw evidence JSON | upstream PR/details and retained artifacts | complete authentication/provenance, unbounded | PR details plus artifact | observation / PR and artifact | REMOVE DUPLICATE from PR when artifact + minimum embedded resolver evidence suffice; keep artifact authoritative |

Output recommendations: **KEEP VISIBLE 5; COLLAPSE 4; MOVE TO LOG 1; MOVE TO ARTIFACT 1;
REDESIGN SUMMARY 8; REMOVE DUPLICATE 1**. “Move to artifact” for the resolver means retain its
existing ignored prompt file; it does not mean upload to GitHub.

## Progressive disclosure rules

Use `<details><summary>Technical details</summary>` for Confirmed Paths, raw paths/commits,
tree/SHA/run/attempt provenance, artifact inventories and IDs, authentication checks, APK hashes,
classifier tokens, and verbose diagnostics. Keep visible the main decision/result, affected
version/build/PR, failure or refusal reason, operator action, approval wait, and next stage.

Target:

```markdown
Full validation reused — this exact tree passed on PR #55.

<details><summary>Technical details</summary>
tested tree, run, attempt, artifact identity
</details>
```

## Information timing registry

| Workflow/process | Information | Available when | Shown now | Avoidable delay | Recommended mechanism |
|---|---|---|---|---|---|
| PR CI | change class, validation path, release relevance | classification, usually seconds | summary after validation job | targeted/full duration: ~3–11 min | append an early plan summary, then final result update/second section |
| Main CI | exact-tree reuse decision | before Gradle | summary step after Full executes/skips | up to observed ~5m25s | early summary line immediately after reuse inspection |
| Main CI Development | whether unpublished range needs an APK | only after validation in separate Build job | Build-job eligibility summary | validation duration, ~5m when not reused | keep release authority after validation, but expose anticipated PR release relevance earlier and clearly say final range check follows |
| Signing | approval requirement | graph creation | Environment waiting UI; no custom summary beforehand | immediate UI is native | improve job/display wording; do not add a Plan job |
| Stable Promotion | candidate version | after authenticated prepare | immediately after prepare | authentication time only, necessary | keep; run name cannot safely claim version before authentication |
| Hold Release | current Stable | after authenticated prepare | immediately after prepare | authentication time only, necessary | keep |
| Upstream Sync | no-delta/counts/candidate need | observe completes, seconds | same job summary | negligible | simplify first line; no Plan job |
| Signing Diagnostic | current source and no-publication intent | dispatch | SHA-heavy run name; result after 9–11 min build/sign | intent unclear for entire run | zero-input run title + immediate purpose summary |
| prepare-pr | complete scope/classification/validation path | audit/classification | terminal progressively; PR body only at end | no major delay | keep early terminal plan; collapse/log detail |
| local validation | selected work and reason | classifier, seconds | immediately | none | translate jargon while retaining raw values in log |

Do not add lightweight Plan jobs by default. Early summary writes inside existing cheap
classification/prepare steps are enough for CI, upstream, and local flows. Stable/Hold must not
announce an unauthenticated version early.

## Conditional path and explanation registry

| Surface | Current condition | Current explanation | Desired immediate explanation |
|---|---|---|---|
| PR validation | non-Android / targeted / Full | classifier tokens shown at end | `Application validation not required`, `Focused Android checks selected`, or `Full validation required — <plain reason>` |
| Main Full | exact-tree evidence reuse or fallback | accurate but late/technical | `Full validation reused — exact tree passed on PR #N` or `Full validation required — evidence missing/different/ambiguous` |
| Development Build | complete unpublished range release relevance | `Skipped · tooling-only` plus internals | `No build required — these changes do not affect the application` |
| Development Sign/Publish | Build required and dependencies succeeded | native skipped/waiting only | Build summary says what follows; job title/UI says `Waiting for approval — signing authorization required` |
| Stable Promotion | authenticated candidate then Environment | native wait + prepare line | `Ready to release: vX`; `Waiting for approval — Stable publication authorization required` |
| Hold Release | authenticated Stable then Environment/recheck | good prepare/result; refusals technical | `Ready to hold: vX`; `Release refused — prepared Stable changed; nothing modified` |
| Upstream publish | no delta vs ready/review/conflict | detailed outcome with policy vocabulary | `No upstream changes`; `Candidate ready`; or `Review required — N files need semantic decisions` |
| Signing Diagnostic | exact SHA guard/build/sign | skipped job may not explain invalid input | after zero-input migration: `Diagnostic will build and sign current protected main; nothing will be published` |
| prepare-pr | scope drift/autofix/validation/PR reuse | safe but verbose | retain refusal reason and “nothing staged/pushed”; state next action and auto-merge state |

Failures and refusals must never be collapsed away. A skipped job caused by a failed prerequisite
should point to that prerequisite rather than appear as a successful policy skip.

## Prepare-pr and validation process

Current possible Full chain is:

```text
operator manually runs Full
→ guided prepare-pr classifies and may run Full again
→ PR CI runs Full for high-risk/release-sensitive paths
→ protected main reuses exact PR Full only when all predicates match; otherwise Full runs again
```

Prepare-pr does not know or authenticate a prior local `validation.log` as reusable evidence, so an
operator-run Full immediately before guided publication is duplicate work. PR Full evidence reuse
already works on main when the required run/artifact/tested tree and final main tree match. The
minimum target is:

- focused/Standard local checks during implementation;
- prepare-pr performs only the still-required local gate and never repeats an authenticated
  unchanged local snapshot without a deliberately designed evidence format;
- required PR CI is the authoritative Full for high-risk and every `releaseRequired=true` APK path;
- protected main reuses PR Full on exact-tree equality and otherwise fails safely to Full.

Removing local Full from upstream resolution, changing which PRs run Full, or renaming the check is
a HIGH-risk process migration. It requires classifier tests, prepare-pr acceptance fixtures,
PR/main evidence-reuse tests, ruleset coordination where names change, and live exact-tree/fallback
acceptance. Do not solve duplication by trusting `validation.log` or weakening main fallback.

Auto-merge is technically feasible through authenticated `gh` after PR creation/reuse. The design
must authenticate the same head, require non-Draft status, use normal merge (especially for native
upstream ancestry), preserve required CI, refuse ambiguity, and report whether auto-merge was armed.
It also requires the repository’s native auto-merge setting to be enabled manually. Human approval
of publication would arm merge; protected rules/checks would still decide when merge occurs.

## Performance inventory

Known evidence: local Full is approximately **9–11 minutes**; one observed offline tooling phase
was **6m38s**; Android Full was **3m16s**; protected-main Release Build is commonly **10+ minutes**
(I02 measured 9m12s). The hosted upstream fixture suite alone creates many real disposable Git
topologies and was recently ~4m35s, making it the first offline profiling suspect. Other Python
suites, process startup, serial execution and repeated fixture setup need measurement rather than
assumption. Release assembly runs in a fresh job/workspace after Debug validation, so cross-job
Gradle/cache misses are the first Build hypothesis.

T0-1 CP7 must capture per-suite/per-test and Gradle task/cache/configuration timings before changing
parallelism, fixtures, task graphs or caches. Preserve deterministic isolation and provenance;
performance is not permission to merge security fixtures or build/sign jobs.

## Signing Diagnostic conclusion

**KEEP AND SIMPLIFY.** Its distinct operator purpose is to verify key custody, Environment secret
wiring, signer certificate, package/version and payload integrity without publishing a Release. It
is useful after signing-key restoration/rotation or Environment migration. The manual
`expected_sha` adds no independent authorization: workflow dispatch is already on protected main,
the guard requires the input equal `github.sha`, and `release-sign` controls access to credentials.
Resolve/authenticate current protected main automatically, show the version/source and
“diagnostic only; nothing published” before expensive work, and retain the Environment boundary.
Whether it can consume an already authenticated unsigned artifact instead of rebuilding belongs to
the performance/process checkpoint and must preserve diagnostic independence.

## T0-1 implementation ledger

Every row states the problem/current source, target UX, coupling/risk, required validation,
external action, and owner checkpoint.

### REMOVE (3)

| ID | Source / current problem | Target and dependency/risk | Validation / external action | CP |
|---|---|---|---|---|
| R01 — COMPLETE | `.github/workflows/main.yml`; dead guarded `Development build` polluted sidebar | Deleted; ownership policy, fixtures and current docs preserve its intended absence. Current CI is sole owner | Focused policy/workflow tests; hosted sidebar observation after merge; no settings | CP2 |
| R02 — COMPLETE | `.github/workflows/release.yml`; dead guarded `Create release`, but unique AAB knowledge | Baseline T0 declines store/AAB ownership; deleted and marked downstream-owned absence; capability retained in historical audit | Focused ownership/release tests; hosted sidebar observation after merge | CP2 |
| R03 — COMPLETE FOR REMOVED SURFACES | Active docs presented deleted/obsolete workflow surfaces | Current docs point to CI/Stable/Hold; historical evidence is explicitly labeled historical | Link/pre-commit checks; no GitHub change | CP2; final consistency sweep CP8 |

### LOW-RISK PRESENTATION (4)

| ID | Source / current problem | Target and dependency/risk | Validation / external action | CP |
|---|---|---|---|---|
| L01 | Stable workflow display repeats repository prefix | `Stable Promotion`; tests/docs only, file unchanged | Focused presentation tests + hosted display acceptance | CP3 |
| L02 | Upstream workflow display repeats prefix and run exposes raw `workflow_dispatch` | `Upstream Synchronization`; `Upstream check · Manual/Scheduled` | Hosted/presentation tests; natural/manual read-only acceptance | CP3 |
| L03 | Signing Diagnostic repeats prefix | `Signing Diagnostic`; artifacts/file unchanged | Signing presentation tests | CP3 |
| L04 | Setup/composite and safe step labels are inconsistent (`Setup`, `Get Release`) | Natural verb/object labels without changing action paths or job IDs | YAML/static tests | CP3 |

### SUMMARY / COLLAPSE (6)

| ID | Source / current problem | Target and dependency/risk | Validation / external action | CP |
|---|---|---|---|---|
| S01 | `ci.yml` PR policy summary is late and classifier-centric | Early plain-language plan + final result; raw policy in details | Summary fixtures for every path; hosted PR cases | CP3 |
| S02 | PR APK/main reuse summaries expose all identities equally | Main result/link visible; SHA/tree/run/artifact in `<details>` | Exact evidence assertions + hosted reuse/fallback | CP3 |
| S03 | `mosaic_development_release.record_eligibility` emits full paths/default | One build/no-build sentence; paths and policy evidence collapsed | Release classifier/output tests; live non-APK/APK | CP3 |
| S04 | `hosted_upstream.upstream_summary` exposes policy tables and full JSON | Counts/attention/action first; lists/navigation/details collapsed; artifact remains complete | Hostile input, quiet-surface, outcome tests; natural run | CP3 |
| S05 | prepare-pr console and PR body repeat raw scope | `PR scope: N files`; paths/stats in logs and collapsed PR details | Disposable prepare-pr tests; no snapshot weakening | CP6 |
| S06 | failure summaries name `$GITHUB_JOB` but not always action/remedy | Plain refusal/failure, mutation status, retry/forward-fix action visible | Failure fixtures; no secret/stderr regression | CP3/CP8 |

### PROCESS SIMPLIFICATION (5)

| ID | Source / current problem | Target and dependency/risk | Validation / external action | CP |
|---|---|---|---|---|
| P01 | Operator Full can precede prepare-pr Full | Document/use one publication entry point; design authenticated snapshot evidence only if reuse is needed | Disposable drift/autofix/snapshot tests | CP4 |
| P02 | prepare-pr + PR Full duplicate local/hosted assurance | For ordinary high-risk/APK work, local focused/Standard then authoritative PR Full; retain fail-closed main fallback | Classifier/prepare-pr/CI fixtures and live PR/main reuse | CP4 |
| P03 | Upstream candidates require local Standard then Full plus PR Full | Remove duplicate local Full only after required upstream PR Full and exact merge evidence fully cover it | Native merge/filter/evidence tests; live natural candidate | CP4 |
| P04 | prepare-pr stops after PR creation and manual auto-merge click | Authenticate same non-Draft head and arm native auto-merge; never arm upstream Draft | Mocked `gh`, branch/rules tests; enable GitHub auto-merge manually; hosted acceptance | CP4 |
| P05 | Signing Diagnostic requires repeated SHA | Zero-input authenticated protected-main source; keep Environment approval and no publication | Signing auth/refusal tests + manual hosted diagnostic | CP4 |

### HIGH-RISK CONTRACT MIGRATION (5)

| ID | Source / current problem | Target and dependency/risk | Validation / external action | CP |
|---|---|---|---|---|
| H01 | `Full validation` is desired as `Prepare` but is ruleset/reuse/provenance input | Coordinated rename across workflow, ruleset, API consumers, tests/docs with no interval lacking required protection | Old/new check migration tests and hosted PR/main acceptance; manual ruleset update | CP5 |
| H02 | Development job names are verbose and test-bound | `Build`, `Sign`, `Publish` only after proving names are not external API/provenance selectors; job IDs unchanged | Release/security tests + hosted APK delivery/rerun | CP5 |
| H03 | Artifact names are ugly but authenticated | Do not rename by default; improve surrounding display. Any change needs dual-reader/migration proof | Complete artifact/provenance/Stable/Hold tests | CP5 or reject |
| H04 | Release names/tags/installer filenames mix human/machine identity | Keep updater contracts; isolate human title changes from machine identity | Updater/version/manifest/device update acceptance | CP5/CP6 |
| H05 | Ownership path state for removed inherited workflows | Explicit downstream-owned absence so upstream sync cannot resurrect publishers | I06 classification/native candidate fixtures + natural observation | CP2/CP5 |

### PERFORMANCE (3)

| ID | Source / current problem | Target and dependency/risk | Validation / external action | CP |
|---|---|---|---|---|
| F01 | Offline tooling ~6m38s; hosted Git fixtures likely dominate | Per-suite/test profile; share only immutable setup proven isolation-safe; assess process parallelism | Repeated timing + full offline equivalence | CP7 |
| F02 | Android Full ~3m16s and repeated across paths | Measure Gradle task/cache overlap before changing authoritative validation model | Task graph/cache evidence + complete validation | CP7 after CP4 |
| F03 | Release Build ~10m+, fresh job after Debug | Profile configuration/task/cache/download time; assess safe cache/artifact reuse without crossing build/sign authority | Hosted timing and provenance/security regression | CP7 |

### RELEASE PRESENTATION (4)

| ID | Source / current problem | Target and dependency/risk | Validation / external action | CP |
|---|---|---|---|---|
| V01 | Development primary title lacks distance from Stable | After compatibility audit, `vStable-distance-gSHA — Development`; machine `downstream-build-N` unchanged | VersionCode/updater/provenance tests + device acceptance | CP6 |
| V02 | Stable/Development bodies lack prominent comparison | Compare Stable→Development and prior Stable→new Stable | Source-baseline/ref authentication tests + live releases | CP6 |
| V03 | Immutable archive looks like another human release | Mark archive/provenance role; rolling channel is primary | Release body/updater tests | CP6 |
| V04 | Artifact identities dominate summaries | Human version/channel first; exact artifact in details | Artifact authentication unchanged; summary tests | CP6 |

### DEFER TO T0-2 (4)

| ID | Finding | Why deferred | T0-2 evidence needed |
|---|---|---|---|
| D01 | Whether every current provenance field has a distinct consumer | Correctness/security architecture, not presentation | Producer/consumer and threat-model audit |
| D02 | Whether ruleset, Environment and permission configuration exactly matches documented assumptions | External assurance beyond repository UX | Read-only settings inventory and drift checks |
| D03 | Previously unknown races/idempotency/security gaps discovered during cleanup | Must not expand T0-1 speculatively | Whole-system adversarial audit and categorization |
| D04 | Application architecture/test adequacy for resumed features | Product engineering boundary, not operator cleanup | T0-2 architecture and coverage audit |

Ledger totals: **REMOVE 3; LOW-RISK PRESENTATION 4; SUMMARY/COLLAPSE 6; PROCESS
SIMPLIFICATION 5; HIGH-RISK CONTRACT MIGRATION 5; PERFORMANCE 3; RELEASE PRESENTATION 4;
DEFER TO T0-2 4** — **34 finite items**.

## Recommended T0-1 checkpoint sequence

1. **CP1 — Inventory (complete):** this document; no behavior change.
2. **CP2 — Remove obsolete surfaces (complete):** deleted `main.yml` and `release.yml`, explicitly
   deferred AAB/store distribution, and updated ownership/tests/docs atomically. Hosted sidebar
   observation remains post-merge evidence.
3. **CP3 — Low-risk names and summaries:** remove redundant prefixes, translate primary decisions,
   add early summary lines, collapse detail. Do not touch `CI / Full validation`.
4. **CP4 — Process simplification:** eliminate redundant validation paths, simplify Signing
   Diagnostic input, and arm native auto-merge. This depends on CP3’s clear explanations and
   requires GitHub auto-merge enablement plus hosted exact-tree/fallback acceptance.
5. **CP5 — High-risk contracts:** only if still valuable, coordinate `Full validation → Prepare`
   and Development job presentation with ruleset and every authenticated consumer. Manual GitHub
   ruleset change and hosted old/new transition acceptance are mandatory.
6. **CP6 — PR and Release presentation:** restructure PR default view, add Compare Changes, and
   implement human Development versioning only after updater/version/provenance proof. Device and
   live release acceptance required for version/title changes.
7. **CP7 — Performance:** profile first, then optimize offline fixtures, Android validation and
   Release Build independently. Depends on CP4 so obsolete duplicate work is not optimized.
8. **CP8 — Final consistency sweep:** compare every surviving Actions/PR/Release/CLI surface to this
   registry, reconcile docs, and prove no machine contract was cosmetically renamed.

Cosmetic CP3 is deliberately separated from CP5 machine-contract migration. CP2 should not wait for
cosmetic work because dead workflows distort the inventory operators see. CP7 follows CP4 because
removing duplication is higher leverage than accelerating duplicate work.

## Future “Learn more” integration

| Surface | Future handbook topic |
|---|---|
| CI PR/main summaries | Validation and Evidence Reuse |
| PR test APK | Pull Requests and Test APKs |
| Build/Sign/Publish | Development Delivery |
| Signing wait/diagnostic | Signing and Environment Authorization |
| Stable Prepare/Release | Stable Release |
| Hold Prepare/Hold | Hold Release and Forward Recovery |
| Upstream summary/PR | Upstream Synchronization; FOLLOW, REVIEW, and Conflicts |
| Release bodies/settings | Development vs Stable Channels; Versioning and Provenance |
| Refusal/rerun guidance | Failed-job Recovery |

Do not hardcode wiki URLs during T0-1. Use centrally managed stable destinations during T0-3.
Every surface must remain understandable without following a link.

## CP2 completion statement

The two obsolete surfaces and their executable definitions are removed without transferring their
authority or changing a surviving workflow. Current CI remains the sole Development delivery owner;
Stable Promotion and Hold Release retain their exact responsibilities. Appstore/Fire TV AAB
distribution is explicitly deferred. The ownership policy and regression fixtures make both
deletions intentional downstream state.

CP3 may begin on a separate branch after CP2 is merged. Hosted confirmation of the five-workflow
sidebar is useful natural acceptance evidence but does not block the next bounded checkpoint. CP3
must still avoid the coordinated `CI / Full validation` machine-contract migration reserved for a
later checkpoint.
