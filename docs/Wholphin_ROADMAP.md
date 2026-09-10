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

### Completed foundations

- [x] Protect `main` with pull-request-only integration, a required `CI / Full validation` check, and blocked force pushes/deletion.
- [x] Establish purpose-specific branches, dedicated upstream-sync branches, repository-specific Fast/Standard/Full validation, and local-to-CI parity.
- [x] Establish fork-owned, read-only PR CI and guard inherited upstream development and stable-release publishers from running in the downstream fork.
- [x] Establish safe manual upstream synchronization with deliberate semantic conflict resolution.
- [x] Maintain authoritative repository-local agent, handoff, roadmap, upstream-sync, and PR-preparation documentation.
- [x] Implement and dogfood the guarded Wholphin `prepare-pr` v1 workflow, including complete PR-scope review, Git-native snapshot/tree verification, validation, exact staging, commit verification, safe push/PR creation, and persistent diagnostics.

### Target operating architecture

Wholphin defines the safety/workflow contract: one appropriate protected integration branch with equivalent guarantees. It does not mandate `main`, PowerShell, Gradle, identical CI, or identical release mechanics across downstream repositories.

| Owner | Responsibilities |
| --- | --- |
| Local / Codex | Implementation, fast/high-value feedback, downstream workspace safety, minimum useful pre-publication validation, autonomous publication after explicit user authorization. |
| GitHub | CURRENT: authoritative CI, formatting/lint, compile/tests/build, mergeability/policy and durable PR state, operational hosted upstream detection, live-validated PR Debug artifacts, and live-validated manual Mosaic Release signing/artifacts. CURRENT: automatic Mosaic Development delivery and manual Stable promotion are live validated. FUTURE: repair sync publication binding, live sync-PR validation, security/dependency checks and measured CI optimization. |
| Human | Publication authorization, semantic/product judgment, exceptional conflicts, Android TV/manual runtime validation where required, completed-PR merge/reject and release approval. |

Prefer deterministic GitHub/tooling for objective checks. Evaluate established tools before building custom alternatives; future agents assist fuzzy/semantic analysis and never replace deterministic validation. The two normal decisions are explicit readiness to publish, followed by review of the completed PR and merge/reject; [PREPARE_PR.md](PREPARE_PR.md) owns the detailed workflow.

### P0 - immediate publication handoff

- [x] Complete, validate and integrate Autonomous PR handoff v2 through PR #9; it is CURRENT on `main`.
- [x] Establish authenticated `gh` as the standard GitHub publication interface and dogfood successful PR creation.
- Keep prepare-pr thin and autonomous after explicit publication authorization. Preserve scope/tree checks, required validation, PR-only integration and inherited publisher guards as ongoing invariants.

### P1 - approved next: move toil off the workstation

Current Mosaic release sequence:

1. **Permanent signing identity - COMPLETE / LIVE VALIDATED.**
2. **Updater routing - COMPLETE / LIVE VALIDATED.**
3. **Rolling development release - COMPLETE / LIVE VALIDATED.**
4. **Live device in-place update acceptance - COMPLETE / LIVE VALIDATED.**
5. **Stable promotion + channel UX - COMPLETE / LIVE VALIDATED.**
6. **Automatic Development delivery - COMPLETE / LIVE VALIDATED.**

Next plumbing: Upstream Sync publication credential binding. The historical Item 6
optimization/refactor/cleanup workstream follows; it is distinct from release milestone 6.

[Automatic acceptance](MOSAIC_DEVELOPMENT_RELEASE.md#automatic-development-and-channel-migration-acceptance)
records PR #20, automatic release #2, v1.0.8/build-8 and in-app 1.0.5 -> 1.0.8 with preserved
settings and Development migration. Stable build-5 promotion is live validated and remains
manual; Development is continuous after authoritative main CI. See the follow-up phase below.
Completed evidence and remaining work:

- [x] Merge hosted upstream detection/candidate preparation on `main`, with isolated normal merges, exact-SHA deduplication, durable blocked issues, and offline safety tests.
- [x] Establish **Detection: OPERATIONAL**. First manual smoke [run 34281315948](https://github.com/constbogdan/Wholphin/actions/runs/34281315948) succeeded with `no_delta`, zero incoming commits and successful ancestry validation. Exact SHAs and external App setup are recorded in [UPSTREAM_SYNC](UPSTREAM_SYNC.md#hosted-upstream-synchronization-v1).
- [ ] **Hosted sync candidate/PR publication: IMPLEMENTED + OFFLINE TESTED; BLOCKED on scheduled credential binding.** Run 34346400694 observed successfully (artifact 10101863873) but publication failed with empty SYNC_PUBLISH_TOKEN (outcome artifact 10101871740). Fix the narrow separate credential binding next; never simply broaden GITHUB_TOKEN. The initial smoke remains historical evidence: No branch/PR was needed in the smoke run. Verify App-token publication and required PR Full CI with a genuine delta. Hosted candidates require no workstation validation; GitHub PR CI remains authoritative, with semantic review and human merge/reject mandatory.
- [x] Implement PR-only universal defaultDebug artifacts from successful Full CI, reusing its existing APK with seven-day retention, head/tested/base SHA metadata and a job-summary download link. OPERATIONAL + LIVE VALIDATED through PR #12 / run 34284819578: the exact artifact was downloaded, installed and run on the emulator after removing an old Debug installation. See [retrieval and install instructions](CODEX_HANDOFF.md#pr-debug-apk-artifacts-2026-09-09).
- [x] Implement approved Mosaic technical identity (`io.github.constbogdan.mosaic`, Debug `.debug`, upstream Kotlin namespace retained) and frozen-epoch first-parent versions (`1.0.N`). Signing is live-validated below; updater routing and rolling development delivery are live validated; stable promotion is live validated; visual branding remains pending. See [implementation boundaries](CODEX_HANDOFF.md#mosaic-technical-identity-and-versions-implemented-2026-09-09).
- [x] Persist the [downstream Release identity proposal](CODEX_HANDOFF.md#downstream-release-identity-contract-proposal-2026-09-09): separate app ID, owned Release key, anchored first-parent version sequence, common updater source and exact-artifact promotion. Identity/version allocation is approved and implemented; signing is live-validated; manual development publication is live validated through unsigned recovery; automatic Development after exact-main CI is live validated; Stable stays manual.
- [x] Prepare [Mosaic signing infrastructure](MOSAIC_SIGNING.md): explicitly unsigned Gradle Release builds, public fingerprint policy/verifier and user-only custody/restore instructions. The manual exercise remains available; normal Development now uses the isolated signer after successful main CI. Identity/versioning is operational on main.
- [x] Permanent Mosaic Release signing identity established: user confirms two independent encrypted backups and successful restore/hash/certificate/private-key-access verification. Only the public SHA256 is recorded in the pinned signing policy.
- [x] User confirms main-restricted `mosaic-release-signing` Environment/secrets configured. Implement manual exact-SHA protected-main validation, unsigned artifact transport, isolated signing and public verification with seven-day exercise artifacts.
- [x] **Permanent signing / first signing acceptance COMPLETE + OPERATIONAL:** run 34323962085, source `055dde77b00c9b6e814d1115422bc60f8fd334b3`, Mosaic 1.0.3/code 3. Hosted signing, independent certificate/package/provenance verification and emulator installation succeeded. Build ~16m43s, signing job ~34s. See [acceptance evidence](MOSAIC_SIGNING.md#first-permanent-release-signing-acceptance). That exercise published no GitHub Release. Its preserved 1.0.3 installation has since been updated in place to 1.0.5 through Mosaic; see delivery acceptance above.
- [x] Implement shared Mosaic updater source routing for checks, APK metadata and installed-version notes, with custom URL overrides and legacy-default migration. [Contract and compatibility](MOSAIC_SIGNING.md#updater-routing-contract). Downstream discovery, notes/source metadata, alias download and in-place update are COMPLETE / LIVE VALIDATED.
- [x] Implement the [Mosaic rolling development publication mechanism](MOSAIC_DEVELOPMENT_RELEASE.md), reusing successful exact-main CI and the shared isolated signer. Manual exact-SHA authorization only; unsigned artifact 10099950969 was recovered using tooling 7d55b98b22e2d440599dfef7288f2ac066a0f8b1 and published as downstream-build-5/develop. Publication and in-place device acceptance are COMPLETE / LIVE VALIDATED.
- [ ] Consider main Debug artifact retention separately; its existing build output could be retained without another build. Main rolling development Release and updater routing are live validated; stable promotion and channel UX are implemented, with first live Stable publication pending. Application identity and source version allocation are implemented. PR Debug test signing is not that future Release identity.
- [ ] **I03 implemented/offline validated; hosted acceptance pending:** classifier-selected local/PR tiers, mapped JVM fallback, concise stage output, per-stage logs, valid native VS Code tasks, and PR summaries are implemented. Protected main remains authoritative Full plus conditional I02 Release ownership; Development remains zero Gradle. Accept with real non-Android, normal targeted-Android, and high-risk Full PR runs and record timing savings against the former ~5–7 minute unconditional PR Full path.
- [ ] Formalize simple rollback/recovery: fail closed before publication, corrective commits or revert PRs afterward, no destructive reset of shared dirty work. Define device recovery considerations before release automation.

### P2 - future established security, dependency and review tooling

- [ ] Evaluate/adopt GitHub-native security and dependency capabilities, CodeQL, dependency review, secret scanning/push protection, and Renovate or Dependabot before custom alternatives. Audit actual settings/eligibility; choose one low-noise dependency-update owner per ecosystem.
- [ ] Evaluate Codex PR review, CodeRabbit and Copilot review where appropriate; trial one advisory reviewer and measure signal, noise, latency, access and actual cost/eligibility before adoption.
- [ ] After I03 hosted acceptance, profile classifier-selected PR timings and tune mappings only from evidence; preserve broad fallback and protected-main authority.
- [ ] Prefer GitHub checks, issues and native notifications for operational status; add other notifications only for a demonstrated need.

### P3 - future downstream releases and broader portability

- [ ] Define downstream release ownership, versioning, signing, RC/stable promotion, provenance, SBOMs, retention and release approval before enabling publishers.
- [ ] Port the proven contract to Seerr only after deliberately reconciling `origin/develop` versus `upstream/develop` divergence and auditing inherited container/chart/Pages/tag/release/issue/PR mutation workflows.
- [ ] Preserve Seerr's appropriate `develop` integration branch, pnpm/Node/Docker validation and repository-specific release lifecycle; adapt the contract to the other pending downstream repositories with their own toolchains and policies.

### Later - future semantic assistance

- [ ] Evaluate specialized agents for upstream-delta analysis, semantic conflict assistance, CI diagnosis, release readiness and cross-repository compatibility. Agents must not replace objective checks or autonomously resolve/publish semantic conflicts.
- [ ] Consider review apps only for services with a real web preview boundary, and self-hosted runners only if measured constraints justify the maintenance cost.

### Pre-main validation model

Wholphin does not currently need a permanent staging/develop branch. The preferred model is:

``` text
feature/fix branch
  -> PR
  -> required CI
  -> downloadable PR Debug APK (operational/live validated, seven-day retention)
  -> optional Android TV/device validation where needed
  -> main
  -> short-lived main debug artifact (P1, not yet retained)
  -> eventual RC/stable release process (P3)
```

Seerr is different: upstream `develop` genuinely participates in its integration and development-container lifecycle. Portability preserves that distinction rather than adding a staging branch to Wholphin or renaming every downstream integration branch.

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

### Stable channel implementation and future Settings UX

[Stable promotion/channel contract](MOSAIC_STABLE.md) is implemented: exact existing
signed build promotion with no rebuild/re-sign, explicit manual authorization, latest
routing and Stable/Development/Custom migration. Stable promotion of downstream-build-5, selector/device migration and automatic Development
after successful main CI are COMPLETE / LIVE VALIDATED. Stable promotion remains manual. Broader Settings
redesign, General/Playback/Library/Downloads/Updates/Integrations/Advanced grouping,
notification improvements where warranted and consistent progress/status UX are future
work, separate from this Updates-only change and from pending CI optimization.


### Post-delivery optimization and product follow-ups

**Next plumbing:** repair Upstream Sync publisher credential binding while preserving
read-only observation and narrowly scoped separate publication authority. No change to
keys, settings, workflow behavior or CI gates is authorized by this documentation checkpoint.

**Historical Item 6: measured optimization + refactor + cleanup (PENDING).** Begin with
representative local prepare-pr and GitHub Actions logs; construct a task/timing/overlap
matrix before redesigning. This workstream retains its historical Item 6 name even though
release milestone 6 (automatic delivery) is now complete.

| Existing evidence | Implication to investigate |
| --- | --- |
| Expensive PR Debug validation, repeated on merged main | Quantify overlap and risk-aware placement |
| Main CI roughly 5-7 minutes; earlier examples 6-7 minutes | Use actual representative task logs |
| Automatic Development: Release build 9m55s, sign 37s, publish 18s; total 11m02s | Separate Release compilation dominates delivery |
| Earlier exercise: build ~16m43s, signing ~34s | Preserve memory/validation context when comparing |
| Stable verify 38s, publish 20s, total ~1m05s | Artifact-only delivery can be short |
| Recovery performs zero Gradle work after build | Preserve unsigned/signed retry checkpoints |

Target to investigate, **not the current gate policy**:

```text
PR -> fast/change-aware checks -> targeted tests -> risk classification -> merge
protected main -> authoritative heavy validation ONCE -> Release APK ONCE
               -> immutable artifact -> sign -> verify -> publish Development
```

Higher-risk PRs may still require Full validation before merge. Failed post-merge Full
validation must make main red and block publication. Keep current required Full CI until a
separately approved redesign establishes the replacement. Preserve fast PR feedback versus
Full merge gates, merge queue, change-aware validation, artifact reuse and zero-build signing/
publishing as measured options, not completed optimizations.

Audit all Actions workflows together: dead/redundant workflow code, obsolete compatibility
branches, unused scripts/helpers, duplicate GitHub API/provenance requests, unnecessary
checkouts/transfers, slow Python helpers, caching and unnecessary Gradle tasks. Determine
whether skipped inherited Development build workflows are obsolete before removing them.
Then standardize workflow/job/step/artifact names, summaries, outputs, scripts and tests.
Misleading real-publication labels include `Mosaic signing exercise verified` and
`signed-mosaic-signing-exercise-...`. Candidate lifecycle names after the audit:
CI ? Pull Request; CI ? Main; Mosaic ? Development Release; Mosaic ? Development Recovery;
Mosaic ? Stable Promotion; Upstream ? Synchronization. Renaming must preserve provenance/
recovery and required-check compatibility. Improve GITHUB_STEP_SUMMARY, progress/status and
slim/quiet prepare-pr.ps1 output while retaining complete diagnostic logs.

**Update and Settings UX (PENDING):** automatic discovery worked but proactive notification
was absent during normal use, re-entry and force-stop/reopen; Settings/About showed the
available update. Investigate a non-blocking Mosaic vX available banner/toast/notification
with de-duplication. Audit/consolidate Install update appearing in two Settings/About
surfaces. Improve states: Up to date / Update available / Downloading / Ready to install.
Retain broader Settings redesign, clearer General / Playback / Library / Downloads / Updates /
Integrations / Advanced groups, consistent status/progress and improved channel-selector
presentation. Keep Custom URL advanced, not normal configuration.

**Fluid download progress / water-meter effect (INVESTIGATE TELEMETRY FIRST):** inspect
Sonarr/Radarr/Seerr byte/progress telemetry before implementation. If trustworthy samples
exist, explore a flowing byte counter/progress bar using recent measured throughput and a
bounded/adaptive smoothing buffer. Interpolation is UI-only: never mutate authoritative
acquisition state, move displayed progress backward or simulate motion indefinitely after
fresh evidence stops. Converge to authoritative samples and exact completion. No smoothing
implementation is approved until telemetry is understood.

**Recovery policy:** Development bad build -> optionally repoint develop to last known-good
bytes -> fix/revert -> higher-version forward recovery. Repoint tooling/authorization is
future work; current publisher rollback rejection remains intact. Stable regression ->
fix/revert on main -> higher-version Development -> validate -> manually promote exact bytes.
If Stable cannot launch its updater, manually install a newer correctly signed Mosaic APK
over the existing package without clearing data. Never mutate/re-version an old APK to
force downgrade. See [recovery boundaries](MOSAIC_STABLE.md#forward-recovery-policy-and-pending-rollback-tooling).

**Post-plumbing repository organization (PENDING):** rewrite README around what Mosaic is,
why it exists and how Stable/Development work. Describe a personal experimentation and
integration downstream, not an official Wholphin replacement. Credit Wholphin and other
upstreams; explicitly encourage adoption of Mosaic features/fixes/designs/ideas by Wholphin
and relevant open-source projects rather than treating them as exclusive. Add useful workflow/
version badges, a compact label taxonomy and historical PR label backfill. Backfill meaningful
completed Issues linked to PRs and create actionable roadmap Issues. Establish one Mosaic
GitHub Project, meaningful product/release milestones (not every iteration), and useful
Issue ? PR ? Project automation. Rename Wholphin-release.apk to Mosaic-release.apk only
atomically with updater compatibility; retain the legacy alias temporarily for older Mosaic
versions if required. No README, assets, labels, Issues, Project or GitHub changes occur here.


### Upstream publication blocker correction

Live run/artifact audit corrected the earlier credential-binding hypothesis: read-only
observation found SeriesOverview.kt / SeriesViewModel.kt conflicts; the ready-only App
mint step correctly skipped. Durable issue recording failed and repository Issues are
currently disabled. See [diagnosis](CODEX_HANDOFF.md#upstream-publication-diagnosis-conflict-and-disabled-issues).
Next: separately enable Issues, validate durable blocked reporting, and resolve semantic
conflicts through the approved sync process. A ready delta must still live-validate App
branch/PR publication. Safe presence/disabled-Issues diagnostics and regression tests are
implemented; no App credential or permission expansion is indicated. Earlier binding-task
labels above are historical hypotheses superseded here. Item 6 remains deferred.
