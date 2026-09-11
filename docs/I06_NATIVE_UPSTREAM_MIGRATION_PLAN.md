# I06 native upstream-integration migration plan

## Purpose and status

This tracks the remaining migration from synthetic I06 integration state to truthful native Git
ancestry. It does not authorize implementation, branch, workflow, PR, or GitHub-setting changes.

PR #38 resolved the feasibility question: Mosaic can retain its reviewed tree unchanged while the
accepted upstream commits become real ancestors. Future episodes should establish that ancestry
during integration rather than repairing it afterward.

## Standing design rules

1. Challenge the requirement before designing machinery for it.
2. Prefer native Git/GitHub behavior whenever it satisfies the validated requirement.
3. If native behavior appears insufficient, first challenge whether the extra requirement is needed.
4. If Git canonically represents a fact, do not duplicate it in durable I06 state without a
   demonstrated consumer.
5. Every custom mechanism must name the distinct property it protects.
6. Every validation pass must name the distinct evidence it provides.
7. Prove replacement behavior before removing the old path.
8. Uncertain identity, ancestry, scope, ownership, or provenance fails closed.

## Invariants

- Mosaic custom behavior and Enhanced-features isolation survive upstream integration.
- Classification covers the complete incoming upstream range.
- Semantic overlap is never resolved blindly with blanket ours or theirs behavior.
- Accepted upstream commits become real ancestors of final Mosaic main.
- The merge tree is the reviewed Mosaic resolution tree.
- No force-push, automatic semantic resolution, automatic Ready transition, or automatic merge.
- Human candidate changes and closed/rejected decisions remain authoritative.
- Normal operation remains quiet toward upstream GitHub surfaces.
- Required CI and established build/sign/publish provenance remain intact.

## 1 — Native ancestry model and proof

Status: **COMPLETE / LIVE VALIDATED**

- [x] Audit the complete upstream range through
      9c56965c82db934879fb94fb3c0f2576239d78ef.
- [x] Account for every changed path as adopted exactly, semantically resolved in PR #36, or
      deliberately preserved downstream.
- [x] Create a tree-preserving two-parent reconciliation commit.
- [x] Prove the commit has no content delta.
- [x] Pass required PR CI.
- [x] Merge with **Create a merge commit**, retaining the ancestry-bearing commit.
- [x] Verify the original upstream commits are ancestors of final Mosaic main.

### PR #38 evidence

| Property | Verified value |
|---|---|
| Reconciliation commit | a14f400750646c9178081d288a5fde9239089177 |
| First parent — Mosaic | c75f457d225c86ce1b8ddbc85623926b460ffe9d |
| Second parent — upstream | 9c56965c82db934879fb94fb3c0f2576239d78ef |
| Reconciliation tree | 62c857d60231254c6f3b477017e03cecdcc68858 |
| Changed files | 0 |
| Required PR CI | Passed |
| GitHub merge method | Create a merge commit |
| Before | 78 ahead / 3 behind |
| After | 80 ahead / 0 behind |

The original commits 4a567cb, 0b995b5, and 9c56965 are real ancestors of Mosaic main. No
application content changed to establish ancestry. Native Git ancestry is therefore viable for I06.

## Existing I06 mechanism decisions

| Mechanism | Direction | Distinct property or reason |
|---|---|---|
| Scheduled/manual observation | **KEEP / SIMPLIFY** | Detect upstream movement without routine polling. |
| Exact ref, SHA, ancestry, and range checks | **KEEP** | Prevent integration against a different history. |
| Complete-range path inventory | **KEEP** | Proves every incoming change is accounted for. |
| FOLLOW / REVIEW / DOWNSTREAM-OWNED policy | **KEEP / SIMPLIFY** | Locates paths needing acceptance, inspection, or deliberate preservation. |
| Conservative unknown handling | **KEEP** | Fails closed when ownership is not established. |
| Isolated workspace | **KEEP** | Separates upstream content from credentials and developer work. |
| Mutation-only App token | **KEEP** | Enforces least privilege. |
| Normal PR for FOLLOW | **KEEP, use native merge** | Provides review and required CI. |
| Draft PR for REVIEW/conflict | **KEEP for now** | Enforces not-ready state while formal approvals remain zero. |
| Single-parent conflict candidate | **REPLACE WITH NATIVE** | It caused accepted history to remain absent from ancestry. |
| Blocked-context file | **SIMPLIFY / TEMPORARY** | Keep only if needed to bootstrap a conflict workspace. |
| Episode identity | **SIMPLIFY** | Keep only fields consumed by reuse and rejection decisions. |
| Risk / Debt / Age / Escalation arithmetic | **REMOVE unless a consumer is proven** | It does not enforce merge safety. |
| Journal Issue for every candidate | **REPLACE WITH PR where practical** | The PR already owns workspace, discussion, CI, and disposition. |
| Merged-Issue finalizer | **REPLACE WITH GITHUB NATIVE** | Necessary Issues can use a same-repository closing keyword. |
| Quiet conversation surfaces | **KEEP / SIMPLIFY** | Prevent upstream-visible references. |
| Machine observation artifact | **KEEP, minimize** | Retains exact provenance unavailable after ref/retention changes. |
| resolve-upstream discovery/checkout | **KEEP / SIMPLIFY** | Prevents guessed identity; it should lead into a real merge. |
| Generated Codex prompt | **SIMPLIFY** | Useful context, but not authoritative lifecycle state. |
| Focused semantic tests | **KEEP** | Prove behavior changed or preserved during resolution. |
| Local Standard | **KEEP** | Proves focused behavior and hygiene on the resolved workspace. |
| Mandatory local Full plus PR Full | **SIMPLIFY after proof** | Remove only validation that adds no independent evidence. |
| Required PR Full CI | **KEEP** | Validates the hosted merge candidate in a clean environment. |
| Protected-main build/release path | **KEEP** | Separate exact-main and Release-provenance boundary. |
| Non-force publication and human merge | **KEEP** | Protect human work and final acceptance authority. |

## 2 — Native clean and REVIEW candidates

Status: **COMPLETE — OFFLINE VALIDATED**

- [x] Add offline Git fixtures for native two-parent candidates.
- [x] Verify exact first parent, second parent, merge tree, and full-range classification.
- [x] Change only textually clean construction:
  - FOLLOW produces the existing normal PR backed by a native merge commit;
  - REVIEW produces the existing Draft PR backed by the same native merge commit.
- [x] Preserve downstream-owned bytes through explicit path resolution while keeping their upstream
      evolution observable.
- [x] Temporarily preserve existing journal, finalizer, resolver, and conflict behavior.
- [x] Preserve retries, human-change refusal, closed/rejected handling, quiet surfaces, App-token
      boundaries, no force-push, and required PR CI.
- [x] Prove accepted ancestry makes the next observation see no duplicate delta.
- [x] Prove unknown paths, rewrites, parent/tree mismatch, and concurrent main movement fail closed.

Completion criterion: clean FOLLOW and REVIEW fixtures produce reviewable native merge commits with
the exact expected parents and semantics; conflict behavior remains unchanged and existing security
and lifecycle tests pass.

This introduces the canonical representation on the lowest-risk path and supplies reusable
parent/tree verification for conflict resolution.

### Checkpoint 2 evidence

- `verify_complete_classification(...)` independently re-reads the complete merge-base-to-upstream
  Git diff and rejects missing, reordered, or unknown-ownership rows.
- `native_merge_candidate(...)` requires the checked-out downstream SHA, exact `MERGE_HEAD`, and
  reviewed index tree before constructing a commit. `verify_native_merge_candidate(...)` then
  requires exact parent order `[downstream, upstream]` and the exact committed tree.
- Clean FOLLOW and textually clean REVIEW fixtures both use that primitive. REVIEW remains Draft;
  FOLLOW remains a normal PR. Explicit downstream-owned restoration remains unchanged.
- The textual-conflict fixture still produces the established deterministic single-parent blocked
  workspace and does not claim upstream ancestry.
- The complete hosted-sync suite passed: **59 tests**, including retry/rejection/human-edit,
  rewrite, concurrent-main, App-token, quiet-surface, journal/finalizer, required-CI, exact-parent,
  exact-tree, complete-range, and accepted-ancestry/no-delta coverage.
- No workflow, resolver, lifecycle, release, signing, or application code changed.

## 3 — Native textual-conflict completion

Status: **COMPLETE — OFFLINE VALIDATED**

- [x] Keep observation and Draft creation safe when Git cannot publish an unresolved index.
- [x] Retain the minimum blocked-context identities consumed to authenticate native continuation.
- [x] Make resolve-upstream authenticate and continue a real merge of the exact upstream tip into the
      exact downstream baseline.
- [x] Leave semantic choices to human/Codex resolution.
- [x] Require a two-parent merge commit whose tree equals the reviewed index and has no markers.
- [x] Preserve meaningful focused-test reporting and default-No publication authority.
- [x] Ensure prepare-pr preserves the merge commit and only fast-forwards the same Draft branch.
- [x] Refuse stale main, rewrites, incomplete range evidence, unrelated paths, unexpected parents, or
      ambiguous episode state.

Completion criterion: a conflict fixture moves from safe blocked context to a reviewed native merge
commit, and subsequent observation recognizes the upstream range as integrated.

### Checkpoint 3 evidence

- Hosted conflict observation and Draft creation remain unchanged: Git still publishes the safe,
  deterministic single-parent workspace because an unresolved Git index cannot be transported.
- On first local selection, `resolve-upstream` authenticates the SHA-pair branch, machine evidence,
  candidate tree, sole downstream-baseline parent, blocked context, upstream remote and current
  upstream ancestry before starting `git merge --no-ff --no-commit <exact-upstream-SHA>`.
- The final native merge uses the exact remote Draft head as first parent and the recorded upstream
  tip as second parent. The Draft head is itself proven to have the exact recorded Mosaic baseline
  as its sole parent; this extra transport commit is required for a non-force fast-forward update of
  the same Draft PR.
- The blocked-context file is removed from the resolved tree. Unmerged entries, conflict markers,
  whitespace errors, unexpected parents, or a committed tree different from the reviewed index fail
  closed.
- `prepare-pr -PreserveMergeCommit` runs the established focused Standard-then-Full policy, verifies
  exact parents/tree and the existing remote Draft head, skips replacement commit creation, permits
  only a fast-forward push, and requires exactly one same-branch Draft PR at the resulting head.
- All **35 resolver fixtures** pass for default-No authority, focused-filter propagation,
  stale/ambiguous state,
  incomplete evidence, upstream rewrite, unrelated scope, and exact same-Draft delegation. A
  disposable Git fixture proves the final two-parent commit, reviewed tree, removed context and
  marker refusal. The complete offline tooling suite passes **199 of 200 tests**, with the one
  existing Windows executable-bit portability skip.
- No Issue, finalizer, Risk/Debt/Age/Escalation, release, signing or application behavior changed.

## 4 — Live native-model acceptance

Status: **IN PROGRESS — hosted no-delta live validated; awaiting a genuine upstream delta.**

### Pre-live cleanup evidence

- [x] Accepted native ancestry is checked before historical candidate branches or journal anchors.
      The PR #38/#39 topology regression proves that an authenticated upstream tip already reachable
      from current Mosaic `main` returns quiet `no_delta`, even when an obsolete malformed candidate
      branch remains. Such branches are neither deleted nor overwritten; Git ancestry makes them
      irrelevant. Uncontained ranges retain all candidate, rewrite and fail-closed checks.
- [x] Hosted refusals now print their actionable sanitized reason to the Actions log as well as the
      machine artifact and step summary.
- [x] Offline tooling tests run through an isolated buffered runner. It removes inherited
      `GITHUB_STEP_SUMMARY` and `GITHUB_OUTPUT` only from the test process, so synthetic summaries
      cannot alter the enclosing workflow; explicit fixture-local channels remain testable. Successful
      fixture transcripts are buffered, while stdout/stderr is retained when a test fails.
- [x] The isolation runner has explicit tooling-only/high-risk classification and focused offline-test
      selection; it does not imply APK relevance.

These fixes do not alter checkpoint 4's trust model or acceptance cases. They remove a false blocked
result after already-accepted ancestry and ensure upcoming live evidence is not mixed with fixture
presentation.

### First live evidence — contained upstream terminates quietly

- [x] Manual `workflow_dispatch` run `34603795016` completed successfully with `outcome: no_delta`.
- [x] The authenticated upstream tip was
      `9c56965c82db934879fb94fb3c0f2576239d78ef`; downstream `main` was
      `1998bdbb546395e7a3ff8a7f9728586662dc5996`; `ancestry_validated` was `true`.
- [x] `incoming_count` was `0`; `incoming_commits`, `changed_paths`, and `conflict_paths` were empty.
- [x] The Observe job succeeded. Candidate publication and journal-finalization jobs were skipped.
- [x] No branch, Issue, PR, comment, or other publication mutation occurred.
- [x] The Actions summary contained only the real **No upstream delta** result and no synthetic
      fixture, recovery, build, or resolver output.

This live-validates native Git reachability as the authoritative accepted-range fact: a contained
authenticated upstream tip stops before historical candidate or journal state can interfere.

### Remaining evidence-driven acceptance

- [ ] Take the next genuine upstream delta end-to-end through whichever native candidate path its
      real classification and merge result select. Verify parents/tree, required CI, human merge
      method, final ancestry, quiet surfaces, appropriate Development/release classification, and
      the following `no_delta` observation.
- [ ] If a natural FOLLOW candidate occurs, record its normal-PR evidence.
- [ ] If a natural textually clean REVIEW candidate occurs, record its native two-parent Draft
      evidence.
- [ ] If a genuine textual conflict occurs, record Draft → `resolve-upstream` → reviewed native
      two-parent merge evidence. Until then, retain all conflict-specific machinery.
- [ ] Opportunistically record DOWNSTREAM-OWNED overlap and retry/reuse evidence when those
      conditions naturally occur.

Do not manufacture FOLLOW, REVIEW, conflict, DOWNSTREAM-OWNED, retry, or concurrent-main episodes.
Deterministic offline fixtures remain the acceptance evidence for theoretical refusal/race paths.
Checkpoint 4's minimum remaining live gate is one genuine future upstream delta completed through
its naturally applicable native path. Outcome-specific machinery may be simplified only after that
specific path has genuine live evidence.

## 5 — Remove and simplify superseded machinery

Status: **DESIGNED / IMPLEMENTATION BLOCKED BY CHECKPOINT 4 EVIDENCE.**

### Proposed final pipeline

~~~text
scheduled/manual observation (read-only token)
  -> fetch authenticated upstream/main and Mosaic/main
  -> native containment: contained = quiet no_delta
  -> complete incoming-range ownership classification
  -> isolated native merge and explicit downstream-owned preservation
  -> normal PR for clean FOLLOW; Draft PR for semantic attention/conflict
  -> mutation job rechecks exact refs and uses repository-scoped App token only if needed
  -> human/Codex semantic work only where the Draft requires it
  -> one focused local Standard gate for changed semantics
  -> required hosted PR Full on the exact published tree
  -> human Ready/merge or reject
  -> protected-main Full and release handling remain unchanged
~~~

The PR becomes the authoritative lifecycle surface. Its branch/head, Draft state, checks, discussion,
closed/merged state and Git parents represent workspace identity, readiness, validation and final
disposition. No parallel Issue is required for facts already visible on the PR. A same-repository
Issue should exist only for a future demonstrated need distinct from an integration candidate; if
one does, native `Closes #N` should own merge closure.

### Mechanism disposition

| Current mechanism | Decision | Distinct surviving property or replacement |
|---|---|---|
| Scheduled/manual observation | **KEEP** | This exists because it detects upstream movement without workstation polling; removing it would make discovery manual. |
| Native containment, merge-base and complete-range detection | **KEEP** | This exists because it proves the exact unaccepted upstream range; removing it would permit omission or replay. |
| FOLLOW / REVIEW / DOWNSTREAM-OWNED classification | **KEEP / SIMPLIFY** | This exists because it selects exact adoption, semantic review, or deliberate Mosaic-byte preservation per path; removing it would expose downstream-owned behavior to blind replacement. |
| Conservative unknown ownership | **KEEP** | This exists because it prevents unreviewed automation/security paths from silently integrating; removing it would turn missing policy into approval. |
| Isolated candidate construction and native two-parent verification | **KEEP** | This exists because it proves exact parents and reviewed tree without touching developer state; removing it would weaken ancestry/content identity. |
| Normal FOLLOW PR and Draft attention PR | **KEEP** | This exists because Draft is the only current hard not-ready gate under the zero-approval ruleset; removing it would expose unresolved semantic work to accidental merge. |
| Read-only observe job followed by mutation-only App-token job | **KEEP** | This exists because it separates inspection from write authority and rechecks ref freshness; merging the jobs would expose routine observations to unnecessary credentials. |
| Exact non-force ref checks and human-change/rejection preservation | **KEEP / REPLACE WITH NATIVE** | Keep time-of-check/time-of-use checks; let branch fast-forward rules and PR open/Draft/closed state represent reuse and disposition instead of parallel episode state. |
| Journal Issue for every candidate | **REMOVE AFTER REPRESENTATIVE CANDIDATE** | The PR already owns attention, discussion, checks and disposition; the Issue supplies no independent decision or recovery boundary. |
| Episode hash, journal observation counter and first/latest timestamps | **REMOVE AFTER REPRESENTATIVE CANDIDATE** | Exact SHA-pair branch plus the one-open-candidate rule identify current work; GitHub already records creation/update history. |
| Risk / Debt / Age / Escalation arithmetic and managed Issue labels | **REMOVE AFTER REPRESENTATIVE CANDIDATE** | No value changes validation, readiness, reviewer assignment, notification or merge policy; it is decorative duplicated state. |
| Custom merged-Issue finalizer workflow job | **REMOVE AFTER REPRESENTATIVE CANDIDATE** | PR merge/close is already canonical terminal state; after legacy journals are drained there is nothing distinct to finalize. |
| `observed_excluded` for an all-DOWNSTREAM-OWNED range | **REPLACE WITH NATIVE** | Ownership may preserve Mosaic bytes but must not suppress upstream ancestry; construct a reviewed ancestry-bearing candidate instead. |
| Machine observation/outcome artifacts | **SIMPLIFY** | This exists because short-lived runs need inspectable path-classification and refusal evidence; remove parents, tree, merge base, containment and accepted-range fields derivable from retained Git objects. |
| Actions summary | **KEEP / SIMPLIFY** | This exists because operators need a concise current result and rich navigation; removing it would force artifact inspection for routine operation. |
| Quiet Issue/PR rendering | **KEEP for PR / REMOVE for Issues** | This exists because downstream operation must not create upstream-visible references; retain sanitization in PR text while deleting Issue-specific rendering. |
| `resolve-upstream` | **SIMPLIFY AFTER REPRESENTATIVE CANDIDATE; conflict core blocked** | This exists because conflict resolution must authenticate and start the exact merge; remove Issue lookup, priority parsing, artifact-first episode recovery and multi-episode dependency calculation. |
| Generated Codex handoff | **KEEP / SIMPLIFY** | This exists because semantic resolution needs bounded path/commit/test context; derive it from authenticated PR/Git/classification evidence instead of journal state. |
| Blocked single-parent transport commit/context | **SIMPLIFY ONLY AFTER LIVE CONFLICT** | An unresolved index cannot be pushed; retain the safe transport until a genuine conflict proves exact native continuation, then derive everything possible from branch/parents/replayed merge and minimize or remove the context file. |
| Focused-test derivation | **KEEP** | This exists because it connects the semantic decision to the narrow behavior proof; removing it would make local review purely syntactic. |
| `prepare-pr` merge preservation and safe publication | **KEEP / SIMPLIFY** | This exists because it verifies/publishes the reviewed merge without replacing it; remove I06-only lifecycle assumptions but retain exact parent/tree and non-force checks. |
| Local Standard then local Full | **SIMPLIFY AFTER REPRESENTATIVE CANDIDATE** | Retain focused Standard; local Full duplicates hosted PR Full for the same published tree and should become optional diagnostics rather than mandatory publication work. |
| Required PR Full | **KEEP** | This exists because it validates the exact remote candidate in a clean trusted runner before merge; removing it would leave only workstation evidence. |
| Protected-main Full/release path | **KEEP / OUT OF I06** | This exists because it validates and releases the actual protected-main result; changing it belongs to release architecture, not upstream simplification. |
| Manual `sync-upstream.ps1` path | **KEEP AS BREAK-GLASS / DOCUMENT** | This exists because hosted automation may be unavailable; it must remain explicit manual recovery, not a second routine lifecycle. |
| Legacy synthetic candidates/journals | **REMOVE AFTER DRAIN/MIGRATION** | Compatibility exists only for already-open state; creating new legacy state after native acceptance would prolong two lifecycle models. |

### Native facts versus retained custom evidence

Git/GitHub canonically replace persisted candidate parents, candidate tree, merge base, upstream
containment, accepted range, branch/head identity, PR readiness, CI state, creation/update timestamps,
merge/rejection disposition and retry identity. These should be derived with `rev-parse`, `merge-base`,
`rev-list`, the PR head/base/Draft/state and required checks.

The minimized machine artifact should retain only facts with a consumer across the observe/publish
boundary or after a refusal: schema/policy version, repository/ref identities, observed upstream and
downstream SHAs, run identity/time, outcome/refusal, and complete per-path ownership/reason evidence.
Exact upstream/downstream inputs remain custom evidence because the mutation job must reject ref
movement. Per-path classification remains because Git stores changed bytes, not Mosaic ownership
intent. Rich URLs and subjects can be reconstructed from repository, SHA and path rather than stored.

For a textual conflict, the temporary transport needs only enough non-Git evidence to bind the
trusted policy/classification used when it was created. Branch name plus its sole downstream parent
already encode the SHA pair; replaying the exact merge derives conflicts. Remove the blocked-context
file only after live conflict proof shows those derivations cover every resolver consumer.

### Resolver's minimum long-term responsibility

~~~text
discover one open authenticated I06 Draft PR
  -> verify downstream repository/base/head/Draft and exact branch SHA pair
  -> fetch and checkout the exact PR head without overwriting local work
  -> authenticate upstream tip and candidate parent shape
  -> start or continue the exact native merge
  -> render bounded Git/classification/Codex context and meaningful focused tests
  -> verify clean reviewed index, allowed scope, no markers, exact parents/tree
  -> delegate non-force publication of the preserved merge to prepare-pr
~~~

Issue enumeration, journal parsing, Risk/Debt/Age display, artifact-first episode recovery,
observation counters, same-area episode hashes, and multi-candidate dependency graphs become
unnecessary. The hosted publisher already serializes candidates and refuses another open sync PR;
the resolver therefore does not need to solve a parallel-work scheduler. Expired artifacts should
not block resolution when PR/Git plus bounded durable classification evidence can authenticate the
same facts; uncertainty still refuses.

### Validation evidence before and after

| Pass | Current distinct evidence | Final role |
|---|---|---|
| Focused tests during semantic work | Fast feedback for the exact changed/preserved behavior | **KEEP**, direct/manual as needed. |
| Local Standard | Changed-scope hygiene, production compile where selected, and meaningful focused JVM behavior on the reviewed workspace | **KEEP as the one required local semantic gate.** |
| Local Full | Repository-wide hygiene plus complete default-debug graph on the same workstation tree | **OPTIONAL after live proof**; useful for debugging/reproduction, but redundant as a mandatory publication gate. |
| Required PR Full | Clean hosted validation of the exact published candidate tree | **KEEP and ensure the upstream candidate path actually selects the complete hosted graph before removing mandatory local Full.** |
| Protected-main Full | Validation of the actual merged protected-main SHA and release boundary | **KEEP unchanged; outside I06 cleanup.** |

The intended attention publication path becomes:

~~~text
semantic/focused iteration
  -> prepare-pr: one focused Standard local gate
  -> required hosted PR Full
  -> human merge/reject
~~~

`validate-local.ps1 -Level Fast|Standard|Full` remains available unchanged for manual debugging,
reproduction and explicitly requested local assurance. The simplification removes only the mandatory
second local Full invocation from I06 publication. This is safe only after a representative native
candidate proves required hosted Full runs against the exact preserved merge tree; a merely named
`CI / Full validation` check that selected a narrower risk path is not equivalent evidence.

### Material simplification target

Approximate counts intentionally describe concepts rather than lines of code:

| Measure | Current I06 | Proposed final I06 |
|---|---:|---:|
| Custom outcome/resolver lifecycle labels | about 17, plus four priority dimensions | about 4 tool results (`no_delta`, `candidate`, `refused`, `error`); PR/Git owns open, Draft, closed and merged state |
| Durable/top-level custom state fields | more than 35 plus nested journal/priority evidence | about 10–12 plus complete per-path ownership evidence; temporary conflict policy binding only where needed |
| Workflow jobs | 3 (observe, publish, Issue finalizer) | 2 (observe, publish) |
| Files/helpers with direct I06 lifecycle responsibility | about 6, with Issue/episode logic spread through hosted and resolver scripts | about 4 focused responsibilities: hosted observer/publisher, ownership policy, resolver plus thin launcher; generic prepare-pr remains shared |
| Routine attention-path human steps | resolver discovery, semantic edit, second resolver approval, local Standard, local Full, PR Ready/review, merge | semantic resolve, one publication authorization/Standard gate, PR review/Ready/merge |
| Expensive validation passes before/through merge | local Standard + local Full + hosted PR Full + protected-main Full | local Standard + hosted PR Full + protected-main Full |

### Evidence gates and implementation order

**Safe after the completed hosted `no_delta` proof:**

1. Preserve the early native-containment path and stop adding historical candidate/journal work to
   `no_delta`. No further custom no-delta lifecycle state is justified.
2. Prepare fixture/document migrations for the smaller outcome vocabulary, but do not remove
   candidate consumers before representative live proof.

**Blocked until one genuine native candidate completes end-to-end:**

1. Make the PR the sole new lifecycle surface; stop creating journal Issues.
2. Drain or explicitly preserve any legacy open journals, then remove the finalizer job.
3. Remove episode identity/history and Risk/Debt/Age/Escalation/Issue-label machinery.
4. Simplify retry/rejection to exact branch/ref plus native PR state.
5. Remove resolver Issue lookup, priority presentation, multi-episode dependency graph and
   artifact-first recovery; retain exact Git/classification authentication.
6. Require actual hosted PR Full for upstream candidates, then reduce mandatory local publication
   validation to focused Standard.
7. Replace `observed_excluded` with an ancestry-bearing candidate whose tree preserves explicitly
   DOWNSTREAM-OWNED Mosaic bytes. Unknown ownership continues to fail closed.
8. Minimize artifacts only after every removed field has no remaining reader.

**Blocked until a genuine textual-conflict episode completes:**

1. Prove the safe transport Draft → resolver merge → reviewed two-parent commit → same-PR
   fast-forward path live.
2. Remove legacy final-single-parent assumptions and expired-artifact compatibility for that path.
3. Minimize or remove blocked-context storage only after branch/parent/replayed-merge derivation is
   proven to authenticate every required fact.
4. Simplify conflict prompt/scope checks without removing exact parent/tree, marker, dirty-path,
   upstream-rewrite, stale-main or default-No refusals.

Replacement must be proven before old readers/writers disappear. Each step should first add native
derivation beside the old value, prove equality in fixtures and available live evidence, switch the
consumer, and only then remove the duplicated field or mechanism.

### Requirements rejected or corrected

- A journal Issue for every candidate is unnecessary; it duplicates the PR and created a custom
  finalization problem.
- Risk/Debt/Age/Escalation is unjustified without a consumer that changes notification, assignment,
  validation or merge policy.
- `observed_excluded` is unsound under truthful ancestry: DOWNSTREAM-OWNED means preserve Mosaic
  content in the merge tree, not leave accepted upstream commits perpetually outside ancestry.
- Multiple simultaneous episode scheduling is unnecessary while hosted publication deliberately
  permits only one open sync PR.
- Persisting Git parents/tree/base/containment is unnecessary when retained Git objects and PR refs
  are the canonical source; cross-job input SHAs and non-Git ownership intent are the exceptions.
- Mandatory local Full plus required hosted Full is duplicate assurance for the same candidate tree.
  Removing local Full is conditional on proving the hosted check executes the complete graph.
- Removing the conflict transport commit immediately would be unsound: Git cannot publish an
  unresolved index. The transport may be minimized only after genuine conflict acceptance.

Completion criterion: Git/GitHub own ancestry, PR state, merge authority, validation state and
disposition; each remaining custom mechanism protects one named gap, no accepted ownership class
suppresses native ancestry, and conflict compatibility remains until its native replacement is
live-proven.

## Safety and rollback

- Keep the current I06 path until replacement passes offline and live acceptance.
- Roll back defects through reviewed revert PRs; never rewrite protected main.
- Failed candidates remain Draft and unmerged; nothing is force-updated or automatically deleted.
- If parent/tree/range proof is uncertain, retain the current manual semantic path.
- Reverting integrated content does not remove ancestry; use a reviewed mainline-parent revert and
  document the intentionally reverted behavior.
- Build, signing, Development recovery, Stable promotion, and updater rollback remain outside I06.

## Progress ledger

| Checkpoint | Evidence | State |
|---|---|---|
| 1 — Native model/proof | PR #38; a14f4007; 0 files; CI passed; 80 ahead / 0 behind | **Complete / live validated** |
| 2 — Native clean/REVIEW | Offline implementation and fixtures | **Complete / offline validated** |
| 3 — Native conflict completion | Exact candidate continuation, parents/tree and same-Draft preservation | **Complete / offline validated** |
| 4 — Live acceptance | Run 34603795016 proves hosted quiet no-delta; one genuine native candidate remains | **In progress / awaiting upstream** |
| 5 — Simplification/removal | Replacement must be accepted first | Blocked by 4 |

## Outside this plan

- I07 Development/Stable withdrawal and recovery.
- Application, UI, Enhanced-feature, Jellyfin, or Seerr changes.
- Pre-merge Release-artifact reuse based on tree equivalence.
- Signing, updater, release-channel, or Stable redesign.
- Merge queues without demonstrated concurrency need.
- Automatic semantic resolution, Ready transition, merge, or force-push.

## Recommended next action

~~~text
Wait for damontecres/Wholphin to advance beyond 9c56965c82db934879fb94fb3c0f2576239d78ef.
~~~

A scheduled Upstream — Synchronization run may produce the representative candidate naturally.
Resume I06 when the authenticated `upstream/main` tip is no longer an ancestor of Mosaic `main`.
Checkpoint 4 is operational acceptance, not another implementation redesign. Publication still
requires the established authority boundaries; checkpoint 5 remains blocked until the surviving
replacement path has sufficient live proof.
