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

Status: **READY — hosted mutation requires explicit user authorization.**

- [ ] Natural FOLLOW: parents/tree, CI, merge method, final ancestry, and next no-delta observation.
- [ ] Natural REVIEW: Draft safety, semantic edits, Ready decision, merge, and ancestry.
- [ ] Natural conflict: resolver, resolution, focused tests, two-parent merge, CI, merge, and ancestry.
- [ ] DOWNSTREAM-OWNED overlap: preserve Mosaic bytes with complete upstream evidence and ancestry.
- [ ] Retry/concurrent-main movement: deterministic reuse or safe refusal without force-push.
- [ ] Quiet-upstream audit: no upstream cross-reference, mention, comment, or notification.
- [ ] Confirm Development classification and the I02 artifact pipeline remain unchanged.

Completion criterion: every real outcome class demonstrates truthful ancestry, preserved Mosaic
behavior, required CI, safe retries, quiet operation, and unchanged release behavior.

## 5 — Remove and simplify superseded machinery

Status: Blocked by checkpoint 4. Replacement must be live-proven before removal.

- [ ] Reassess whether an Issue serves any consumer not served by the PR.
- [ ] Where an Issue remains necessary, use GitHub-native Closes #N and verify merge closure.
- [ ] Remove the custom finalizer only after native closure is proven.
- [ ] Remove Risk/Debt/Age/Escalation calculations that drive no required decision or gate.
- [ ] Reduce episode markers and artifacts to identities/provenance with actual consumers.
- [ ] Remove single-parent conflict handling after open candidates are migrated or closed.
- [ ] Collapse resolver/prepare-pr checks only where no time-of-check/time-of-use boundary is lost.
- [ ] Record the unique evidence from every validation pass; remove mandatory local Full only if
      required PR Full covers the same resolved tree.
- [ ] Reconcile documentation and fixtures without deleting coverage of surviving invariants.

Completion criterion: Git/GitHub own ancestry, PR state, merge authority, and Issue closure wherever
native behavior suffices; each remaining custom mechanism and validation pass protects one stated,
non-duplicated property.

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
| 2 — Native clean/REVIEW | Offline implementation and fixtures | **Ready — next** |
| 3 — Native conflict completion | Reuses checkpoint 2 parent/tree primitives | Blocked by 2 |
| 4 — Live acceptance | Genuine episodes and explicit hosted authorization | Blocked by 2–3 |
| 5 — Simplification/removal | Replacement must be accepted first | Blocked by 4 |

## Outside this plan

- I07 Development/Stable withdrawal and recovery.
- Application, UI, Enhanced-feature, Jellyfin, or Seerr changes.
- Pre-merge Release-artifact reuse based on tree equivalence.
- Signing, updater, release-channel, or Stable redesign.
- Merge queues without demonstrated concurrency need.
- Automatic semantic resolution, Ready transition, merge, or force-push.

## Recommended next branch

~~~text
chore/i06-native-clean-review-candidates
~~~

Limit it to offline native-merge primitives and migration of textually clean FOLLOW/REVIEW candidate
construction. Do not migrate conflict resolution or remove lifecycle machinery in that branch.
