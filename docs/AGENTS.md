# AGENTS.md

## Wholphin Development Guidance

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

Before synchronizing with the original project, read `docs/UPSTREAM_SYNC.md`. Never merge `upstream/main` directly into our `main`: use a dedicated `chore/sync-upstream-YYYY-MM-DD` branch created from current validated `main`, stop for deliberate semantic resolution if conflicts occur, inspect high-risk auto-merges, run Standard and then Full validation, and merge the sync branch through a pull request.

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

-   Prefer targeted validation for the code changed; do not automatically run the full Gradle test suite after every change.
-   Do not spend agent time waiting on long-running Gradle validation unless required for diagnosis.
-   Maintain `scripts/validate-local.ps1` with the validation commands appropriate for the current work.
-   `Fast` and `Standard` require an explicit `-TestFilter` identifying the focused test class or classes appropriate to the current task.
-   `Full` does not require a test filter because it runs the complete suite.
-   Order validation from cheapest/most targeted to broader regression checks.
-   The script should fail fast, preserve failure exit codes, identify each step, and write output to `validation.log`.
-   Do not run long validation commands yourself. Tell the user when the validation script is ready so they can run it separately.
-   When validation results are provided, analyze them and fix any failures attributable to the change.
-   Before considering a larger feature/batch ready to merge, include the appropriate broader/full-suite validation.

### Validation Handoff in Responses

When implementation reaches a point where the changed code is ready for user-run validation, continue responding normally with the implementation summary, important decisions, remaining caveats, and anything else that would ordinarily be reported.

Then end the response with a clearly identified **Run this** action containing the exact validation command the user should execute from the repository root.

Use a fenced PowerShell command block so supported Codex/VS Code interfaces can expose it as an executable/run action.

Choose the validation level based on the state of the work:

-   `Fast` --- during iteration when focused validation is sufficient. Requires `-TestFilter`.
-   `Standard` --- the normal validation handoff when an implementation task is believed ready for meaningful regression testing. Requires `-TestFilter`.
-   `Full` --- larger checkpoints, pre-merge validation, substantial cross-cutting changes, or when the complete suite is specifically warranted. No test filter is required.

Prefer `Standard` when a feature implementation is considered complete unless there is a concrete reason to choose `Fast` or `Full`.

Examples:

**Run this**

``` powershell
.\scripts\validate-local.ps1 -Level Standard -TestFilter '*SeriesSeasonOrderingTest*'
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
.\scripts\validate-local.ps1 -Level Fast -TestFilter '*RelevantExistingOrChangedTest*'
```

Do not make the user reconstruct or infer the appropriate validation command from prose.

Do not run long `Standard` or `Full` validation merely to avoid presenting the handoff command. The user will run it separately and provide the result or `validation.log`.

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
