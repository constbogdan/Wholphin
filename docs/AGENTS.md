# AGENTS.md

## Wholphin Development Guidance

### Fresh-session bootstrap

A fresh Codex session must read the repository-local documents in this order:

1. `docs/AGENTS.md`
2. `docs/Wholphin_ROADMAP.md`
3. `docs/CODEX_HANDOFF.md`
4. `docs/UPSTREAM_SYNC.md`
5. `docs/PREPARE_PR.md` when preparing a commit or pull request

These repository-local copies are authoritative. Do not depend on sibling-workspace or other external copies. Before touching files, do not assume the current branch, worktree cleanliness, remotes, or merge state; inspect them from the repository root:

``` powershell
git status
git branch --show-current
git remote -v
git log -5 --oneline --decorate
```

`git status` must also be checked for an in-progress merge, rebase, cherry-pick, revert, or bisect. If its output is unclear, inspect the operation paths reported by `git rev-parse --git-path <name>` before proceeding.

For this repository, preserve these remote meanings:

``` ini
origin   = our maintained downstream fork
upstream = official Wholphin repository
```

Do not casually swap them. New product, fix, and maintenance work begins on a purpose-specific branch from the current validated `origin/main`. Manual upstream integration uses `chore/sync-upstream-YYYY-MM-DD`; hosted candidates use exact-SHA pair branches according to `docs/UPSTREAM_SYNC.md`.

Preserve all existing user and Codex work. Never reset, restore, clean, checkout over, or otherwise discard unrelated changes merely to make the workspace convenient. If the tree is dirty, first identify which changes belong to the current task and work around everything else.

Before implementing, modifying, or refactoring Wholphin ecosystem features, read:

-   `docs/Wholphin_ROADMAP.md`
-   `docs/CODEX_HANDOFF.md`

If `ECOSYSTEM.md` exists and is relevant to the task, read it as well.
Treat these documents as product, architecture, and development-continuity context, not merely as backlog/reference material.

The roadmap describes:

-   the intended long-term Wholphin product direction;
-   completed work that should not be accidentally duplicated or regressed;
-   current architectural decisions;
-   planned features and dependencies between them;
-   terminology and user-facing behavior we want to keep consistent.

## Product Principle

Wholphin should increasingly behave like one integrated media application rather than a Jellyfin client with disconnected feature add-ons.

Jellyfin remains the source of truth for the local/playable library.

Seerr extends the experience with concepts such as:

-   discovery;
-   requests;
-   acquisition state;
-   unavailable content;
-   watchlist state;
-   future cross-library metadata.

Where practical, these concepts should be modeled as reusable media state rather than implemented independently on individual screens.

For example, a media item may simultaneously be:

-   available in Jellyfin;
-   partially available;
-   incomplete;
-   requested;
-   downloading;
-   waiting for Jellyfin readiness;
-   on the watchlist;
-   part of a collection or franchise;
-   eligible for a quality upgrade.

Prefer designs that allow this state to be reused across Library, Series, Downloads, Discover, Watchlist, Collections, and Suggestions.

## Feature Isolation

The extended Seerr/discovery functionality is intended to become one coherent optional product capability.

Do not introduce dependencies that break or materially change normal Wholphin/Jellyfin behavior when the extended feature set is disabled or unavailable.

Prefer graceful degradation.

Base Jellyfin functionality should remain usable without Seerr.

When gating fork-added enhanced features, verify the boundary against `upstream/main`. Upstream Wholphin already includes Seerr-backed Discover, search, requests, availability indicators, details, and similar-content enrichment; do not disable those merely because their classes mention Seerr or Discover. Gate semantic fork-added capabilities at orchestration boundaries, and preserve independent bug fixes and UI/navigation/focus improvements when the enhanced family is off.

## Acquisition vs Contextual Library Diagnostics

Do not conflate acquisition lifecycle state with persistent library state.

Downloads/acquisition tracking answers questions such as:

-   Is this requested?
-   Is it downloading?
-   Is it waiting for import?
-   Has it recently become available?

Current library diagnostics answer a different question:

-   Is the content that should exist actually playable in Jellyfin?

For TV seasons, Wholphin may persist trusted released-episode expectations so a later visit can compare them with a fresh Jellyfin inventory even after acquisition history has expired or Seerr is unavailable.

Do not persist complete/incomplete conclusions, live Jellyfin counts, missing-episode results, or acquisition-adjusted status. Those values are ephemeral and must be calculated from persisted expectations, fresh Jellyfin playability, and current acquisition evidence.

Wholphin provides contextual diagnostics when the user visits or refreshes relevant content. It is not responsible for continuous whole-library auditing, backend repair, or policing historical consistency across Jellyfin, Seerr, and Servarr.

## Jellyfin Readiness

Do not treat Seerr availability as equivalent to Jellyfin playback readiness.

Content should only be considered ready for navigation/playback when the corresponding Jellyfin media is actually present and usable.

For TV content, preserve season-level and episode-level Jellyfin identity where needed for correct navigation and readiness.

## UI Terminology

Prefer user-facing wording that describes the actual condition.

Examples:

-   `Incomplete`
-   `3 episodes missing`
-   `Partially Available`
-   `Downloading`
-   `Requested`
-   `Available`

Avoid internal or misleading terminology such as `Stalled` when the real condition is simply that expected library content is missing.

## Existing Work

Before implementing a feature, inspect the existing code and roadmap to determine whether related infrastructure already exists.

Do not recreate existing acquisition/readiness logic in a new screen.

Reuse or extend shared models and projections where possible.

In particular, preserve the architectural direction of moving media-state calculations out of UI code and into shared domain/data layers.

## Knowledge Preservation / Handoff

`docs/CODEX_HANDOFF.md` is the persistent development handoff between Codex sessions.

Use the repository documents deliberately:

- `docs/AGENTS.md` holds permanent agent and development operating rules.
- `docs/UPSTREAM_SYNC.md` holds permanent branching and upstream-sync policy.
- `docs/Wholphin_ROADMAP.md` holds durable product and engineering direction.
- `docs/CODEX_HANDOFF.md` holds current and historical implementation continuity, non-obvious discoveries, rejected approaches, merge resolutions, and validation results.

During development, preserve information in this file whenever losing it
would make a future agent materially less effective or force it to
repeat significant investigation.

In particular, record:

-   subtle or non-obvious discoveries;
-   cross-repository behavior and dependencies;
-   API and lifecycle semantics;
-   important ID/correlation relationships;
-   architectural decisions and why they were made;
-   assumptions that investigation proved wrong;
-   approaches that were attempted and rejected, including why;
-   race conditions, timing behavior, and reconciliation requirements;
-   important invariants;
-   implementation constraints that are not obvious from the code;
-   unresolved questions and risks;
-   significant partial work that another session may inherit.

Preserve **reasoning and negative knowledge**, not only final
conclusions.

When useful, document discoveries as:

**Expected → Observed → Consequence**

so future agents understand both what was discovered and why it matters.

Do not turn the handoff into a chronological activity log. Routine
edits, commands, and facts readily apparent from the current code do not
need to be recorded.

Update `docs/CODEX_HANDOFF.md` **during the work**, when important
knowledge is discovered. Do not wait until the end of a task to
reconstruct subtle reasoning from memory.

Before completing a substantial task, ask:

**"What did I learn during this work that a future agent could not
safely or efficiently infer just by reading the resulting code?"**

Add that information to `docs/CODEX_HANDOFF.md`.

When information becomes a stable property of the ecosystem rather than
session-specific knowledge, promote it to the appropriate durable
documentation, such as `ECOSYSTEM.md`, architecture documentation, or
the roadmap. The handoff should not remain the only source of stable
architectural knowledge.

Never silently delete useful historical knowledge merely because the
current task is complete. Mark superseded conclusions clearly and point
to their replacement where appropriate.

## Implementation Approach

When asked to implement a task:

1. Read `docs/Wholphin_ROADMAP.md` and `docs/CODEX_HANDOFF.md` and `ECOSYSTEM.md` when present and relevant.
2. Inspect the relevant existing implementation before proposing changes.
3. Identify whether the task should extend an existing shared model instead of adding screen-specific logic.
4. Preserve existing Jellyfin behavior unless the task explicitly requires changing it.
5. Prefer the smallest coherent change that fits the long-term architecture.
6. Avoid speculative refactors unrelated to the requested task.
7. Call out any roadmap conflict or architectural tradeoff before implementing a conflicting design.
8. Update tests for changed behavior where practical.
9. Avoid leaving temporary tracing, debug UI, or dead branches behind.
10. If the implementation materially changes product direction or completes a roadmap item, update `docs/Wholphin_ROADMAP.md`.

## Refactoring Rules

Refactoring is welcome when it directly supports the requested feature or removes duplication exposed by that feature.

Avoid broad cleanup unrelated to the task.

Do not change behavior merely to make code stylistically cleaner.

Preserve working semantics unless the task explicitly changes them.

## Cross-Feature Thinking

When adding new state or behavior, consider whether other Wholphin surfaces will eventually need it.

Examples:

-   watchlist state should not belong only to a Watchlist page;
-   acquisition state should not belong only to Downloads;
-   collection membership should not belong only to Collections;
-   library availability should be reusable in Discover;
-   missing-season state should be reusable on series, season, collection, and suggestion surfaces.

This does not mean every task must implement all future consumers.

It means new domain concepts should be modeled so they can be reused later without major rework.

## Navigation

Prefer navigating to the most specific Jellyfin destination supported by the existing navigation model.

For example:

-   an available TV season should navigate to that season when its Jellyfin season ID is known;
-   avoid falling back to series-level navigation when a correct season-level destination is available.

## External Integrations

Future integrations such as Trakt, IMDb, TMDB lists, Sonarr/Radarr enhancements, or other metadata sources should remain optional.

Do not make the core Jellyfin experience dependent on them.

## Roadmap Discipline

`docs/Wholphin_ROADMAP.md` is a living document.

When a roadmap item is completed:

-   mark it completed;
-   move it into the completed/current-state section when appropriate;
-   document any significant architectural decision made during implementation.

When implementation reveals that a roadmap idea is no longer appropriate, update the roadmap rather than silently diverging from it.

## Repository and upstream workflow

`main` is the known-good integration baseline and receives changes through pull requests. Do not perform active feature, fix, or maintenance development directly on it.

Before synchronizing with the original project, read `docs/UPSTREAM_SYNC.md`. Never merge `upstream/main` directly into our `main`. Manual synchronization uses a dedicated `chore/sync-upstream-YYYY-MM-DD` branch, deliberate semantic conflict resolution, high-risk auto-merge review, Standard then Full local validation, and PR-only integration. The hosted v2 implementation instead prepares an ownership-aware normal or Draft `chore/sync-upstream-<upstream-SHA>-<downstream-SHA>` workspace in isolated GitHub jobs and relies on required PR Full CI without workstation validation. FOLLOW, REVIEW and DOWNSTREAM-OWNED policy never authorizes automatic semantic resolution or merge; conflicts remain blocked for human/Codex resolution in their Draft workspace. Activation status and credential prerequisites are recorded in the handoff and upstream policy.

For a hosted I06 attention candidate, use `.\scripts\resolve-upstream.ps1` to discover/select an actionable downstream PR, or pass `-Pr <N>` directly. This is the standard re-entrant checkout/evidence/prompt/publication entry point; do not reconstruct candidate identities or bypass dependency, clean-tree, scope, mapping and non-divergence refusals. First use exits after creating the Codex prompt. After semantic resolution, run it again: only an explicit default-No `Ready to PUSH?` approval may delegate exact derived filters to prepare-pr for ordinary fast-forward update of the same Draft. Draft readiness and merge/reject remain separate human decisions.

Pull requests targeting `main`, including upstream-sync pull requests, receive the required fork-owned `CI / Full validation` check. The job deterministically classifies the complete PR range: proven non-Android changes run changed-range pre-commit and offline workflow/Python checks; normal Android changes add mapped Kotlin/JVM coverage; unknown or sensitive build, release, signing, updater, persistence, identity, or CI boundaries retain Full default-debug validation. After a merge or push to protected `main`, the same job always runs repository-wide pre-commit and the complete default-debug compile/test/assembly graph before the I02 Release-artifact boundary. Manual upstream conflict recovery still requires local Standard with meaningful focused filters followed by Full. CI is not a replacement for semantic review or Android TV visual, focus, and integration testing.

CI validation is deliberately read-only, requires no backend, extension, or signing secrets, and must remain safe for fork pull requests. The inherited upstream development-release workflow is repository-gated and must not publish or replace releases in this fork during an ordinary `main` push. Tag-release behavior remains separate from validation.

The protected `main` ruleset requires pull requests and the `CI / Full validation` check, and blocks force pushes and branch deletion. The permanent integration flow is:

``` text
user explicitly authorizes publication
        -> autonomous audit / local validation / exact stage / commit / push / PR via gh
        -> GitHub takes over: required risk-tiered PR validation and mergeability
        -> user reviews completed PR and decides merge / reject
        -> Full validation on the merged main push
```

PR CI reports release relevance, validation risk, and the checks actually selected in the Actions summary. Protected-main and manual CI remain authoritative repository-wide pre-commit plus production compilation, the complete default-debug JVM suite, and default-debug APK assembly. CI does not replace Android TV visual, focus, navigation, or integration validation when the changed behavior requires those checks.

Codex does not decide independently that work should be published. Passing tests or completing implementation is not authority to stage for publication, commit, push, or create a PR. Publication begins only after an explicit user instruction such as “prepare the PR,” “publish this,” or an unambiguous equivalent.

After that authorization, `scripts/prepare-pr.ps1` is the normal autonomous publication path. It audits the complete scope, applies the same deterministic classifier used by CI (while honoring explicit meaningful JVM filters), validates without drift, stages exactly, generates the title, commits, verifies tree identity, safely pushes, and uses authenticated `gh` to locate or create the PR without routine intermediate prompts. Upstream-sync branches still require Standard with meaningful focused patterns followed by Full. The user then reviews the completed GitHub PR and decides whether to merge. Read `docs/PREPARE_PR.md` for stop conditions and advanced diagnostic phases.

Prepare-pr never makes ownership assumptions about a dirty tree. Normal use automatically selects one coherent non-ignored change set in the dedicated task worktree. If unrelated work is mixed in, use an explicit advanced scope only after review or preserve the work in a separate worktree; any remaining out-of-scope dirty path is refused because it would validate a different tree from the intended commit. Never bypass the script with a broad `git add .` merely for convenience.

The normal human boundaries are “ready to publish” before prepare-pr starts and “ready to merge” after the GitHub PR exists. Prepare-pr never force-pushes, merges, waits for CI, or deletes branches/worktrees. After publication, required `CI / Full validation` and manual merge remain the repository gates.

Wholphin does not currently need a permanent staging/develop branch. Use PR CI and, once implemented, short-lived PR debug APKs for pre-main device testing; the target sequence and artifact status are in [the roadmap](Wholphin_ROADMAP.md#downstream-repository-maintenance-standardization).

### Automation design principles

Use GitHub as the preferred control plane for unattended schedules, pull-request state, required checks, review, merge, artifacts, security alerts, and notifications. Keep local scripts deterministic, thin, repository-specific, and useful before publication; do not recreate durable hosted workflow state locally.

Preserve both normal human decision boundaries: explicit publication authorization, then completed-PR review and merge/reject. An agent may complete mechanical local preparation and, when the task explicitly authorizes external publication, push and open a pull request from an isolated task worktree. Objective checks belong in deterministic tooling; AI review and agent analysis are advisory unless a later policy explicitly establishes a narrower guarded role.

Standardize maintained downstream repositories by safety contract rather than by branch name or identical scripts. The invariant is one appropriate protected integration branch; neither `main`, PowerShell, Gradle, identical CI, nor identical release mechanics are mandatory. Each repository chooses its own integration branch, validation graph, package manager, artifacts, upstream identity, and release implementation while preserving PR-only integration, local/CI parity, semantic upstream conflict handling, minimal permissions, and guarded publishers.

## When Requirements Are Ambiguous

Use the roadmap and existing product behavior to infer the intended direction.

Prefer consistency with the unified Wholphin product model.

If multiple implementations are technically valid, favor the one that:

-   preserves base Jellyfin behavior;
-   centralizes reusable state;
-   minimizes duplicate logic;
-   works cleanly with future roadmap features;
-   produces the clearest user-facing behavior.

## Validation workflow

The repository-supported commands are:

``` powershell
.\scripts\validate-local.ps1 -Level Fast
.\scripts\validate-local.ps1 -Level Standard
.\scripts\validate-local.ps1 -Level Full
```

Fast is very quick relevant feedback, Standard is the normal completed-task handoff, and Full is explicit comprehensive validation for high-risk or substantial checkpoints. Fast and Standard derive changed paths from `origin/main` through `HEAD` plus the current working tree and select focused tests deterministically; an explicit `-TestFilter '*RelevantTest*'` remains available. Python and `pre-commit` are local prerequisites. The script resolves Java and exposes its `bin` directory to child processes for that validation process only; validation tooling must never silently install dependencies or mutate global developer tooling.

-   Prefer targeted validation for the code changed; do not automatically run the full Gradle test suite after every change.
-   During ordinary implementation, prefer fast, high-value feedback. Explicit publication authorization includes running the validation required by prepare-pr without another user handoff.
-   Maintain `scripts/validate-local.ps1` with the validation commands appropriate for the current work.
-   Fast and Standard use the source-controlled validation policy and canonical change classifier. Explicit `-TestFilter` values override derived focused patterns; never invent a filter.
-   Unknown or sensitive inputs escalate to Full. An unmapped production path receives the broad all-JVM fallback rather than no tests.
-   Fast runs the smallest selected feedback path; Standard adds changed-scope pre-commit, offline tooling tests, and production compilation for targeted Android changes; Full runs repository-wide pre-commit, all offline tests, and one combined complete default-debug Gradle graph.
-   Pre-commit includes autofix hooks and may modify files before returning non-zero. If it fails, inspect the working-tree diff before rerunning validation; the script stops before Gradle rather than validating an unreviewed rewrite.
-   Local Standard/Full use `pre-commit` from `PATH` when available, then fall back to `python -m pre_commit`. If neither works, install it once with `python -m pip install pre-commit`; validation never mutates permanent developer tooling or `PATH`.
-   Order validation from cheapest/most targeted to broader regression checks.
-   The script fails fast, preserves exit codes, prints truthful start/pass/fail stages without fabricated percentages, and retains complete per-stage logs under `.logs/validation/<run>/`. The repository-root `validation.log` remains a replace-on-run compatibility snapshot, assembled and copied once after validation finishes so live command output has only one writer. Failures show only a bounded useful excerpt plus the absolute full-log path.
-   During ordinary implementation, hand off long validation to the user unless already authorized. During explicitly authorized publication, run the required validation autonomously.
-   When validation results are provided, analyze them and fix any failures attributable to the change.
-   Before considering a larger feature/batch ready to merge, include the appropriate broader/full-suite validation.

### Validation Handoff in Responses

For ordinary implementation, when the changed code is ready for user-run validation, continue responding normally with the implementation summary, important decisions, remaining caveats, and anything else that would ordinarily be reported.

Then end the response with a clearly identified **Run this** action containing the exact validation command the user should execute from the repository root.

Use a fenced PowerShell command block so supported Codex/VS Code interfaces can expose it as an executable/run action.

Choose the validation level based on the state of the work:

-   `Fast` --- very quick classifier-selected feedback during iteration. It can run without a filter; use `-TestFilter` when a narrower real JVM seam is known.
-   `Standard` --- normal completed-task developer handoff. It works without a filter by deriving mapped coverage and adds the appropriate hygiene/tooling/compile evidence.
-   `Full` --- high-risk, substantial, explicit comprehensive, upstream-sync, or checkpoint validation. It always runs the complete local graph.

Unknown/sensitive scope escalates conservatively even when Fast or Standard was requested. Explicit real filters remain supported; never invent one merely to change the tier.

Examples:

**Run this**

``` powershell
.\scripts\validate-local.ps1 -Level Standard
```

Or, when full validation is warranted:

**Run this**

``` powershell
.\scripts\validate-local.ps1 -Level Full
```

The test filter must reference the actual focused test class(es) changed or created for the task. Do not invent a test name merely for the handoff.

For focused iterative validation:

**Run this**

``` powershell
.\scripts\validate-local.ps1 -Level Fast
```

Do not make the user reconstruct or infer the appropriate validation command from prose.

This user-run handoff applies to ordinary implementation. Once publication is explicitly authorized, prepare-pr runs Standard/Full itself; do not insert a routine validation confirmation or return the work to the user before the PR exists.

If validation has already been run externally and the supplied results are sufficient, analyze those results normally rather than asking for the same validation again.

If a validation failure requires another code change, make the fix and then provide a new **Run this** action for the smallest validation level that meaningfully verifies the fix.

The **Run this** action supplements the normal completion response; it does not replace the implementation summary.

Testing / Validation

Before creating a new test file, inspect the existing focused tests around the changed code.

Prefer extending the most appropriate existing test class when the behavior naturally belongs there.

Create a new test class only when:

no suitable existing test seam exists;
the new behavior represents a distinct domain/component concern;
or a separate class materially improves clarity and maintainability.

Do not create a new test class merely because the task introduced a new bugfix or because an example test name was mentioned in a prompt.

The focused validation filter handed back to the user should reference the actual test class(es) changed or created for the task.

## Debug Home acquisition fixtures

For Android TV Home acquisition UI iteration, the debug build provides an in-memory fixture source selected by an ADB broadcast. Prefer it for deterministic card/focus presentation work; it does not validate Seerr, Servarr, download-client, Jellyfin, tracker, or persistence integration. Fixture mode replaces only Home's acquiring projection, never merges with real state, and resets to `real` after process death.

From the repository root, select a scenario with:

``` powershell
adb shell am broadcast -n com.github.damontecres.wholphin.debug/com.github.damontecres.wholphin.ui.main.HomeAcquiringFixtureReceiver -a com.github.damontecres.wholphin.debug.ACQUISITION_FIXTURE --es scenario <token>
```

Supported tokens are `real`, `empty`, `movie_states`, `tv_multi_season`, `mixed`, `focus_before`, `focus_card_removed`, and `focus_row_removed`. Use consecutive focus scenarios while Home remains visible to exercise card and whole-row removal.
