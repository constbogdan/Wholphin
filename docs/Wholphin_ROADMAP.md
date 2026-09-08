# Wholphin Roadmap

> Living roadmap for the Wholphin fork: completed work, current direction, and future backlog.

## Product Direction

The goal is to make Wholphin feel like one integrated media application rather than a Jellyfin client with isolated add-ons.

Jellyfin remains the source of truth for the local/playable library, while Seerr extends Wholphin with discovery, requests, watchlists, acquisition state, and unavailable-content awareness.

Longer term, features such as Discover, Watchlist, Collections, acquisition status, library availability, and external metadata should share a common product model and UI language. When the extended feature set is disabled, normal Wholphin/Jellyfin behavior should remain unaffected.

---

# What We've Done So Far

## Seerr / Acquisition Integration

- Added Seerr-backed acquisition tracking for movies, TV series, seasons, and episodes.
- Added acquisition/download lifecycle information to Wholphin.
- Added a Downloads page for active and recently completed acquisitions.
- Added Jellyfin readiness detection so an acquisition is not considered usable merely because Seerr reports it as available.
- Track playable Jellyfin episode IDs for TV acquisitions.
- Added Jellyfin season item IDs to TV readiness data.
- Implemented direct navigation from an Available TV season on Downloads to the corresponding Jellyfin season instead of only opening the series.
- Preserved normal failure warnings while cleaning up temporary acquisition tracing/debugging.
- Extracted TV acquisition calculations/projection logic from UI/service code into a dedicated data-model layer.
- Improved separation between Seerr acquisition state and Jellyfin playback readiness.

## Series / Season Availability Direction

The series experience is being expanded beyond the contents currently present in Jellyfin.

The intended model is:

- Available seasons appear normally.
- Missing/unavailable seasons can still be represented.
- Seerr supplies request/availability information for content that is not yet in Jellyfin.
- Partially available series can expose their missing seasons directly instead of forcing the user through a separate Discover flow.

## Development / Architecture

- Wholphin fork and Android/Kotlin development environment established.
- Feature work is being designed as one coherent optional product capability rather than permanently independent feature islands.
- Cross-feature state is expected to be reusable throughout Wholphin: library availability, watchlist state, acquisition state, collection membership, and similar metadata should eventually be available wherever a media item is rendered.

---

# Current Product Architecture Direction

## Unified Extended Experience

Eventually the Seerr/discovery-related work should be exposed through a single high-level feature toggle.

When enabled, Wholphin gains an extended media experience.

When disabled, the base Jellyfin experience should continue normally without dependencies on Seerr-specific functionality.

The extended layer should provide reusable state such as:

- In Jellyfin library
- Partially available
- Missing/incomplete
- Requested
- Pending
- Downloading
- Available but waiting for Jellyfin
- On watchlist
- Collection/franchise membership
- Upgrade available

This information should not belong exclusively to one screen.

### Enhanced-feature boundary and gating

The high-level toggle applies only to capabilities added by this fork on top of upstream Wholphin. It is not a Seerr enable/disable switch. Upstream Wholphin already provides Seerr-backed Discover, search results, request history, request submission/cancellation, Discover details, availability indicators, and similar-title/person enrichment; those remain governed by the existing Seerr configuration and reachability model.

The initial master switch controls the fork's Downloads/acquisition tracking, immediate local Queueing, acquisition progress and problem presentation, merged Jellyfin + Seerr season placeholders and request-more-seasons behavior on Jellyfin Series details, the added series availability header, and contextual incomplete-season diagnostics. Independent fixes such as numeric season ordering, exact-ID navigation, refresh corrections, and request-dialog focus/presentation improvements remain active when the master is off.

User intent is stored in protobuf DataStore and resolved through semantic capabilities rather than raw Boolean checks at every consumer. Initially all capabilities follow one master value; later Downloads, acquisition progress, missing seasons, integrity, and related capabilities may gain subordinate overrides without changing consumers. Seerr configuration, temporary reachability, and enhanced-feature enablement remain separate facts.

Disabling the feature family stops enhanced background work, hides Downloads, removes enhanced Series projections and presentation, and prevents acquisition-only request side effects without deleting server configuration or durable expectation caches. Re-enabling resumes eligible foreground work and enrichment. A future shared media-product-state coordinator should consume only enabled enhanced sources while keeping library/playability, request/availability, acquisition, integrity, watchlist, and quality as independent dimensions.

For example:

- A Jellyfin library card can indicate that an item is on the watchlist.
- A Discover card can indicate that an item is already available locally.
- A Collection can contain available and unavailable movies.
- A Series page can show available and unavailable seasons together.
- Suggestions can expose availability/request state without navigating elsewhere first.

---

# Roadmap

## Phase 1 — Acquisition Foundation

**Status: implemented; remaining work is UX and extended real-world hardening**

Build the common acquisition model connecting Seerr state to Jellyfin readiness.

Includes:

- Seerr acquisition tracking
- Downloads page
- Movie/TV acquisition lifecycle
- Jellyfin readiness
- Episode readiness
- Season-aware navigation
- Recently completed acquisition history
- Seven-day rolling Recently Completed retention
- Cold-start Jellyfin readiness and navigation rehydration
- Shared TV acquisition projection/model

Remaining work in this phase mainly concerns extended real-world resilience testing and UI polish.

---

## Phase 2 — Complete Series Experience

Turn the Jellyfin series page into a complete representation of the show rather than only the seasons currently downloaded.

Planned experience:

- Show all known seasons.
- Render available Jellyfin seasons normally.
- Render unavailable seasons as placeholders/greyed cards.
- Allow unavailable seasons to be requested directly.
- Show series-level Seerr availability such as **Partially Available**.
- Show production status such as **Continuing** or **Ended**.
- Make partially available seasons actionable.
- Avoid unnecessary navigation through Discover simply to request another season.

### Enhanced Request Popup

Improve the existing request flow:

- Add/clean up **More Seasons** handling.
- Exclude fully available/non-actionable seasons.
- Keep partially available seasons when additional episodes are still requestable.
- Preserve pending/requested semantics.
- Keep the initially selected season visible separately.
- Do not duplicate the selected season under More Seasons.

---

## Phase 3 — Persistent Expectations and Live Integrity

**Status: implemented as contextual diagnostics**

Acquisition history and library integrity are different concepts.

A download disappearing from Downloads history must not cause Wholphin to forget trusted released-episode expectations.

Persist only the released-episode expectation needed for later evaluation. Calculate the current result from that expectation, a fresh Jellyfin playable-episode inventory, and current acquisition coverage.

Example:

> **Incomplete — 3 episodes missing**

Persist:

- Exact expected released episode numbers
- User, series, season, and TMDB identity
- Expectation update time

Do not persist live playable counts, missing numbers, or complete/incomplete conclusions. A season is shown as incomplete only when a live evaluation finds expected released episodes missing from Jellyfin and current acquisition evidence does not account for them.

### Contextual Live Evaluation

When a series is opened or explicitly refreshed, evaluate cached expectations against fresh Jellyfin state. Fetch detailed Seerr season metadata only when an expectation is absent or deliberately refreshed.

Supported triggers:

- Opening a series
- Explicitly refreshing the series

When missing episodes become playable, the next live evaluation clears the warning. Wholphin does not continuously crawl the library or repair backend state.

---

## Phase 4 — Acquisition UX

Make downloading feel native to Wholphin rather than like a remote request submitted to another application.

### Acquisition visibility outside the local library

Normal **Movies** and **Series** library grids remain Jellyfin-local: requested or acquiring catalog items must not be injected as synthetic library entries before Jellyfin discovers them. Active acquisition instead appears on separate transient surfaces:

- **Home — Acquiring:** the primary lightweight view of current Queueing, Queued, In progress, and Finishing items. The row should appear above existing Home content such as Recently Released and Recently Added, and disappear completely when empty so ordinary content shifts upward naturally.
- **Downloads:** the operational source for all active acquisition plus the existing rolling recent-history window, including detailed lifecycle, reliable progress, and timing.
- **Watchlist:** the future persistent catalog surface for items the user cares about, whether local or non-local.
- **Discover:** the exploration and request surface.
- **Movies / Series:** may later add their own distinct Acquiring rows if useful, but those rows must remain separate from the normal Jellyfin-local grids.

Movie cards may expose exact lifecycle or reliable progress. Home Acquiring represents TV as one logical card per active season, using canonical season progress without aggregating across seasons. Other series-poster surfaces may use only the coarse `SeriesAcquisitionSummary`; Series Details and Downloads retain richer exact per-season state.

The intended transition is **Discover / Watchlist → Acquiring → Jellyfin discovery → Recently Added / normal library**. Once Jellyfin discovers an item, it joins the local library naturally while shared media identity/state continues following the same logical item. The transient rows require no new persistence and remain hidden when enhanced acquisition tracking is disabled or no acquisition is active.

### Download Progress

- Show acquisition/download progress in Wholphin.
- Add a compact progress bubble/overlay.
- Display percentage where reliable progress information is available.
- Allow the user to inspect active downloads.

### Completion Feedback

- In-app notification when requested content becomes available.
- Clearly distinguish:
  - Requested
  - Pending
  - Downloading
  - Importing/processing
  - Available in Seerr
  - Ready to play in Jellyfin

### Disk Space Awareness

Before requesting/downloading content:

- Detect available storage where possible.
- Warn when free space is low.
- Potentially estimate whether the requested content is likely to fit.
- Avoid blocking requests unnecessarily when size cannot be estimated reliably.

---

## Phase 5 — Watchlist

Add a dedicated Seerr/Jellyseerr watchlist experience.

Planned features:

- Dedicated navigation destination
- Movie/Series filtering
- Sort by date added
- Sort by release year
- Genre grouping/filtering
- Collection/franchise grouping
- Persist preferred view locally, or server-side where supported

Watchlist membership should become reusable metadata throughout Wholphin.

Examples:

- Show a watchlist indicator on Jellyfin library cards.
- Show watchlist state in Collections.
- Show watchlist state in Discover and suggestions.

---

## Phase 6 — Collections & Franchises

Create a richer collection experience that includes content outside the current Jellyfin library.

### Movie Collections

Show:

- Available collection items
- Unavailable collection items
- Request state
- Download state

Optionally include completely unavailable collections when at least one item or related title is on the user's watchlist.

Jellyfin and Seerr/TMDB collection identifiers can be used to correlate collection membership where appropriate.

### Franchise Relationships

Go beyond strict TMDB box sets.

Examples:

- Alien → Aliens → Predator → AVP → Prometheus
- Iron Man → Avengers → wider MCU
- Batman/Superman → Justice League → wider DC universe

This introduces the concept of related media universes rather than relying only on formal movie collections.

---

## Phase 7 — Discover

Build a richer Discover landing page.

Proposed primary sections/tabs:

- Movies
- Series
- Animation / Anime
- Franchises

### Fresh

**Status: configurable application-managed backend, Discovery Sources settings, Discover row, and opt-in card indicator implemented locally in Seerr; Wholphin consumption deferred.**

Fresh is the transient intersection of recent Seerr Discover movies/series and retained releases belonging to a selected autobrr filter. It signals that recent media appeared in the user's chosen release feed; it does not imply Watchlist intent, a request, acquisition, playback readiness, permanent availability, or a particular quality level.

A shared rebuildable in-memory projection uses typed TMDB identity and supports an authenticated ordered media API plus cheap membership indicators. Autobrr owns release policy/history; Seerr owns recent candidate selection. No permanent release-observation or tracker-availability database is introduced. Current matching is conservative title/alias matching with movie year discrimination over a rolling 90-day window. Ordering uses the earliest retained qualifying observation within that window.

Seerr now persists write-only-token configuration, runs one non-overlapping scheduled coordinator, retains the last good snapshot as stale during transient failures, and exposes admin status/test/refresh controls plus `/api/v1/fresh`. The fixed Discover Fresh row consumes that API with normal movie/series cards and preserves backend ordering. A shared typed frontend membership index also supplies an opt-in Fresh indicator to ordinary Discover media sliders without per-card requests. Administrators can configure the autobrr connection/filter and normalized rolling movie/TV Discover candidate policies under Discovery Sources. Remaining work is Wholphin consumption. Fresh stays optional; ordinary Discover works when its source is disabled or unavailable.

### Browse By

Possible discovery dimensions:

- Genre
- Decade
- Year range
- Popularity
- Recently released
- Highly rated
- Franchise
- Collection
- Studio
- Network
- Streaming origin
- Country
- Language

Example decade/year-range presentation:

- 1970–1979
- 1980–1989
- 1990–1999
- 2000–2009
- 2010–2019
- 2020–present

### Viewing Order

Franchises can expose alternative viewing orders:

- Release order
- Chronological order

This is especially useful for franchises such as Star Wars and large cinematic universes.

---

## Phase 8 — Smart Suggestions

Use the combined Jellyfin + Seerr + watchlist + collection model to make suggestions more useful.

Potential examples:

- Continue a franchise
- Next unavailable movie in a collection
- Next season of a series
- Related franchise
- Movies connected to something recently watched
- Watchlisted titles that have recently become available
- Missing entries between already-owned franchise titles

Suggestions should understand whether content is:

- Playable now
- Missing
- Requested
- Downloading
- On the watchlist

---

## Phase 9 — Automatic Next-Season Acquisition

Optional automation for users who want Wholphin to keep a currently watched series ready.

Potential behavior:

1. User approaches the end of the current season.
2. Wholphin determines that a later season exists.
3. The next season is not locally available.
4. Wholphin optionally requests it through Seerr.

Needs safeguards:

- Explicit opt-in
- Configurable completion threshold
- Never duplicate an existing request
- Respect pending/downloading state
- Do not request specials accidentally
- Handle continuing versus ended series
- Allow per-series disable/override

---

## Phase 10 — Quality Upgrades

Allow users to request a better version of content they already own when Seerr/Sonarr/Radarr supports a higher quality profile.

Examples:

- 720p → 1080p
- 1080p → 4K

Potential UI:

> **Upgrade available**

The action should clearly distinguish upgrading an existing item from requesting missing content.

---

## Phase 11 — External Player Improvements

Continue validating external-player integration, particularly for devices such as the Zidoo Z9X 8K.

Observed behavior already indicates that playback/resume position can return to Jellyfin even though Jellyfin may not display an active playback session in the dashboard.

Future work:

- Verify resume reporting consistently.
- Verify watched/completed state.
- Investigate richer playback progress reporting where the external player permits it.
- Investigate chapter information/thumbnails exposed through Jellyfin APIs.
- Preserve compatibility with native/external player choices.

---

## Phase 12 — External Lists & Metadata

Investigate optional list integration with services such as:

- Trakt
- IMDb
- TMDB
- Other compatible list providers

Potential uses:

- Import a list into Watchlist
- Browse external lists in Discover
- Turn lists into request queues
- Use curated lists as recommendation sources
- Cross-reference library availability

Integrations should remain optional and should not become requirements for normal Wholphin operation.

---

# TODO

## Acquisition / Downloads

- [x] Implement Seerr acquisition model.
- [x] Implement Downloads page.
- [x] Track Jellyfin readiness separately from Seerr availability.
- [x] Track playable Jellyfin episodes for TV acquisitions.
- [x] Retain Jellyfin season IDs in TV readiness data.
- [x] Navigate Available TV season Downloads entries directly to the Jellyfin season.
- [x] Extract shared TV acquisition projection logic.
- [x] Preserve acquisition/readiness orthogonality in Downloads: active upgrade/replacement work wins over recent-ready history, Seerr availability alone does not prove readiness, and operational lifecycle/progress matches the shared card projection.
  - [x] External Standard validation passed for the Downloads lifecycle checkpoint (targeted JVM tests, production Kotlin compile, acquisition model/tracker, Seerr pagination, Downloads page, and whitespace checks; `00:04:53.6766272`).
- [x] Remove temporary acquisition tracing/debug surface.
- [ ] Review acquisition lifecycle edge cases after extended real-world testing.
- [ ] Add in-app download/acquisition progress indicator.
  - [x] Manually evaluate the provisional Series season-card bottom-edge progress rail; Android TV lifecycle validation passed across Queueing, Queued, In progress, temporary queue absence, resumed progress, Finishing, simultaneous seasons, and placeholder-to-Jellyfin transition.
- [x] Add a transient Home **Acquiring** row above existing Home content.
  - [x] Add the reusable Home acquisition projection/source without migrating Home UI.
  - [x] Checkpoint 1 passed external Standard validation (targeted JVM tests, production Kotlin compile, acquisition model/tracker, Seerr pagination, Downloads page, and whitespace checks; `00:06:27.2001194`).
  - [x] Integrate the transient row as a separately keyed leading Home item without changing configured Home rows or settings.
  - [x] Migrate Home TV acquisition from coarse series posters to exact season-scoped cards without additional network work.
  - [x] Complete Android TV focus, lifecycle, and navigation validation; mixed/movie/TV and focus-removal fixture scenarios passed.
  - [x] Keep normal Movies and Series grids Jellyfin-local; do not inject synthetic catalog entries.
  - [x] Hide the row completely when no qualifying acquisition is active or enhanced acquisition is disabled.
  - [x] Use exact lifecycle/progress for movies where safe and exact canonical season lifecycle/progress for TV without cross-season aggregation.
  - [x] Append a stable end-of-row arrow that opens the existing Downloads operational surface; navigation and return-to-Home behavior passed Android TV validation.
  - [x] Consolidated acquisition/Home foundation passed external Full validation on 2026-09-07: production Kotlin compile, complete default-debug JVM unit suite, default-debug APK assembly, and Git whitespace check (`00:01:21.5762407`).
- [ ] Consider separate Movies / Series **Acquiring** rows after evaluating the Home surface.
- [ ] Add completion notification.
- [ ] Investigate disk-space warning before acquisition.

## Library Integrity

- [x] Persist released-episode expectations independently of Downloads history.
- [x] Read current playable episode inventory from Jellyfin during contextual evaluation.
- [x] Calculate missing episode numbers ephemerally rather than persisting a conclusion.
- [x] Exclude episodes covered by current authoritative acquisition evidence.
- [x] Evaluate integrity when a series is opened or explicitly refreshed.
- [x] Clear the warning naturally when a later contextual evaluation finds all expected episodes playable.
- [x] Reject persistent complete/incomplete snapshots and continuous whole-library auditing; they become stale without an authoritative event stream.

## Series

- [x] Show all known seasons on the series page.
- [x] Add unavailable/placeholder season cards.
- [x] Request a missing season directly from its placeholder.
- [x] Add **Partially Available** series badge.
- [x] Order season tabs deterministically by numeric Jellyfin season number.
- [x] Refresh the materialized Jellyfin season list while preserving exact-ID selection when possible.
- [ ] Add **Continuing / Ended** production-status badge.
- [ ] Improve More Seasons request popup.
- [ ] Exclude fully available/non-actionable seasons from More Seasons.
- [ ] Preserve actionable partially available seasons.
- [ ] Avoid duplicate selected season in More Seasons.

## Watchlist

- [ ] Add dedicated watchlist navigation destination.
- [ ] Add Movie/Series filter.
- [ ] Sort by date added.
- [ ] Sort by year.
- [ ] Add genre filtering/grouping.
- [ ] Add collection/franchise grouping.
- [ ] Persist preferred view configuration.
- [ ] Expose watchlist state on media cards outside the Watchlist page.

## Collections / Franchises

- [ ] Add dedicated movie Collections page.
- [ ] Combine available and unavailable collection items.
- [ ] Add option to surface unavailable collections related to watchlisted content.
- [ ] Reuse TMDB collection IDs where appropriate.
- [ ] Design broader franchise/universe relationship model.
- [ ] Add release-order browsing.
- [ ] Add chronological-order browsing.

## Discover

- [ ] Design new Discover landing page.
- [ ] Add Movies tab.
- [ ] Add Series tab.
- [ ] Add Animation/Anime tab.
- [ ] Add Franchises tab.
- [ ] Add Browse by Genre.
- [ ] Add Browse by Decade/year range.
- [ ] Explore studio/network/country/language browsing.
- [ ] Show local availability directly on Discover cards.
- [ ] Show request/download state directly on Discover cards.

## Smart Features

- [ ] Design unified media-state model reusable across screens.
- [ ] Add collection/franchise-aware suggestions.
- [ ] Add availability-aware suggestions.
- [ ] Add watchlist-aware suggestions.
- [ ] Design automatic next-season acquisition.
- [ ] Add opt-in and safeguards for automatic requests.
- [ ] Investigate quality-upgrade actions.
- [ ] Detect available higher quality profiles.

## Playback

- [ ] Validate external-player resume behavior across more scenarios.
- [ ] Validate watched/completed reporting.
- [ ] Investigate external-player progress reporting.
- [ ] Investigate Jellyfin chapter thumbnail availability to external players.

## External Integrations

- [ ] Investigate Trakt list integration.
- [ ] Investigate IMDb list integration.
- [ ] Investigate TMDB list integration.
- [ ] Define import versus live-sync behavior.
- [ ] Ensure external integrations remain optional.

## Architecture / Product

- [x] Define the upstream/base boundary and semantic capability-gate architecture.
  - [x] Implement and validate the documented high-level capability gate for fork-added enhanced features.
  - [x] Confirm at runtime that disabling it preserves upstream/base Wholphin surfaces and behavior.
  - [x] Add and validate an incremental shared media-identity foundation and read-only acquisition index.
  - [x] Add and validate an incremental read-only integrity source keyed by shared media identity.
  - [x] Add and validate a read-only acquisition + integrity product-state coordinator and migrate one Series season-card projection.
  - [x] Add an indexed coarse series-acquisition summary foundation without migrating a card or page.
- [ ] Centralize library/request/acquisition/watchlist state.
- [ ] Make shared media state available to cards across Library, Discover, Watchlist, Collections, and Suggestions.
  - [ ] Avoid feature-specific duplicate implementations of the same media-state logic.

## Downstream repository maintenance standardization

Wholphin is the reference implementation for a shared maintained-downstream operating model that will later extend to Seerr, the three currently pending repository activities, and future modified services.

- [x] Establish protected `main` with pull-request-only integration and blocked force pushes/deletion.
- [x] Establish feature/fix/chore naming and dedicated upstream-sync branches.
- [x] Establish repository-specific Fast/Standard/Full local validation and local-to-required-CI parity.
- [x] Establish fork-owned GitHub Actions validation and protection from inherited upstream development-release automation.
- [x] Establish safe manual upstream synchronization and semantic conflict-resolution policy.
- [x] Maintain authoritative repository-local agent, handoff, roadmap, and upstream-policy documentation.
- [ ] Add a shared, guarded `prepare-pr` workflow for status/diff auditing, validation, staging, commit preparation, push, and PR creation.
  - [x] Implement the Wholphin v1 guided workflow with explicit scope, snapshot-bound validation, staged review, separate commit/publication approvals, safe push behavior, and GitHub CLI fallback.
  - [ ] Complete external Full validation and Android-independent workflow acceptance before marking the milestone complete.
- [ ] Add automated upstream-change detection and conflict-safe sync-PR preparation.
- [ ] Adapt the model to Seerr after deliberately establishing its downstream baseline and auditing inherited workflows.
- [ ] Adapt the model to the other pending repositories and future modified services.
- [ ] Standardize downstream build/release ownership and automation where appropriate.

Portability means the same workflow and safety guarantees with a repository-specific implementation. Do not blindly copy Wholphin details: every repository must derive its own build toolchain, validation commands, runtimes, formatting/lint tools, CI runner, secrets, artifacts, releases, upstream tag/versioning behavior, and high-risk merge surfaces.

The shared identity/index work is a compatibility seam, not a mandatory model migration. Existing `BaseItem`, `DiscoverItem`, pagers, destinations, ViewModels, and cards remain usable directly; new consumers may adopt identity-indexed sources one at a time. Combined product state remains ephemeral and must not require a database migration.

External Standard validation completed successfully for this checkpoint in `00:08:19.0908900`, covering its focused identity/index tests, production Kotlin compilation, established acquisition/tracker/pagination/Downloads regressions, and the Git whitespace check.

---

# Longer-Term Vision

Wholphin should be able to answer the important questions about a title without making the user think about which backend owns the information:

- **Can I watch it?**
- **Do I own part of it?**
- **What am I missing?**
- **Is it already being downloaded?**
- **Can I request it?**
- **Is it on my watchlist?**
- **Is there a better-quality version available?**
- **What comes next?**
- **What is this connected to?**

The distinction between Jellyfin, Seerr, Sonarr/Radarr, and external metadata providers should remain an implementation detail wherever possible.

The user should experience one media library.
