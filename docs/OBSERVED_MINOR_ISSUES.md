# Observed Minor Issues

Small, non-blocking issues observed during development or manual validation.

These items should be preserved for later review but should not interrupt the current implementation unless they become functionally significant. When an issue is fixed, record the resolution before removing or marking it resolved.

## Open

### Series Details — Incomplete badge briefly flickers during initial load

**Observed:** When navigating to a series page containing an incomplete season, the `Incomplete` badge can briefly appear, disappear, and then appear again as the page state and integrity reconciliation settle.

**Final state:** Correct. The appropriate `Incomplete` badge is displayed after loading/reconciliation completes.

**Impact:** Minor visual flicker only. No incorrect persistent state or functional issue has been observed.

**Decision:** Deferred. Do not interrupt the current shared media-state architecture work to investigate this.

**Possible area to inspect later:** Intermediate Series details/integrity projections emitted while persisted state, Seerr enrichment, Jellyfin inventory, and reconciliation are being assembled.

### Discover Search — active movie acquisition progress not shown

Observed: A movie actively downloading shows the shared acquisition progress rail on Discover → Requests, but the same movie returned through Discover → Search does not currently show progress.

Reason: Discover Search has not yet been migrated to consume the shared MediaProductState / CardMediaPresentation acquisition state.

Future work: Extend shared acquisition presentation to Discover Search movie results using typed TMDB identity. Define safe ambiguity handling when multiple acquisitions/quality variants exist and no exact request identity is available.

Scope: Movie results first. Do not infer a single progress value for TV series until series/multi-season aggregation semantics are explicitly defined.

Decision: Deferred as part of the broader cross-surface shared-state rollout.

### Series Details — acquisition progress may remain until the tracker publishes completion

Observed: While remaining on a Series Details page, a season card's acquisition progress rail updates correctly during active downloading. After the season download completes, the rail can remain visible at its last known progress position instead of disappearing.

Expected: The card rail represents active determinate acquisition progress only. Once the acquisition is no longer actively progressing, the presentation value should become null and the rail should disappear.

Impact: Minor stale UI state; underlying download/acquisition completion is not known to be incorrect.

The presentation-policy defect has been resolved: retained terminal targets now require `hasCurrentAcquisitionWork` before producing any ordinary-card acquisition presentation. `SeriesViewModel` already replaces presentation with null when the shared source removes it.

Remaining possibility: a rail can still reflect the last successfully published live queue snapshot until polling publishes queue disappearance or Jellyfin readiness. Retain this narrower runtime observation until it is reproduced or ruled out; do not delete tracker history to mask it.

## Resolved

### Home Acquiring — final-row removal shift

**Observed:** A visible focus/scroll shift could occur when the focused final Acquiring card disappeared and the entire leading row was removed.

**Resolution:** Lazy-item placement animation was restored while retaining the one-shot nearby-card and configured-row fallback rules. Deterministic Android TV validation with `focus_before` → `focus_card_removed` → `focus_row_removed` passed, including card removal, whole-row removal, focus fallback, and stable restoration.

### Home / Downloads — contradictory TV acquisition lifecycle

**Observed:** For the same real season, Home could show `Queued` while Downloads showed `In progress · 50%` because the two surfaces interpreted retained acquisition evidence differently.

**Resolution:** Downloads now uses the shared current-work card projection for operational exact-season lifecycle and determinate progress. On the same authoritative snapshot, both surfaces classify Queueing, Queued, In progress, and Finishing consistently. Only In progress carries a determinate fraction; Downloads may still provide richer timing and navigation. Normal asynchronous polling/publication lag remains possible and is not a semantic disagreement.

### Discover Requests — Queued movie acquisition rail

**Observed:** Downloads could describe a movie as `Queued · 0%` while its Requests card rendered a small determinate rail from a tiny non-zero aggregate fraction.

**Resolution:** Home and Discover Requests now share one current-work-qualified movie card projector. Only a genuinely downloading aggregate with live observed progress produces a rail; Queueing, Queued, and Finishing produce their state presentation without a rail. Request ID and normal/4K isolation remain exact, while conflicting catalog variants become coarse `Acquiring` rather than selecting or averaging them.

### Series Details — retained terminal acquisition presentation

**Observed:** Retained TV acquisition history could remain indexed after current work ended, while the card projector did not explicitly enforce the target's current-work result.

**Resolution:** `tvSeasonCardPresentation()` now returns no presentation when `TvSeasonTarget.hasCurrentAcquisitionWork` is false. Useful tracker/index history is preserved. Any separate delay caused by the tracker not yet publishing a new snapshot remains recorded as the narrower open polling-lag observation above.

### Home Acquiring — excessive vertical separation

**Observed:** The Acquiring row felt more isolated than normal Home rows and delayed visibility of the following row header.

**Correction:** The first attempted resolution removed the Acquiring wrapper's 8dp bottom padding, but full-path comparison showed that native configured rows retain that same wrapper padding. The result was an 8dp Acquiring gap versus the native 16dp effective gap (8dp LazyRow bottom content padding plus 8dp row-wrapper padding).

**Resolution:** Acquiring and configured rows now use the same shared 8dp Home-row wrapper padding, restoring the same 16dp effective distance from card/caption bottom to the next header. Title/card spacing, LazyRow padding, card dimensions, placement animation, and focus behavior are unchanged.

**Further correction:** Equal padding did not eliminate the remaining mismatch because Acquiring still used captioned movie and season cards while native poster rows were poster-only. Home Acquiring now uses the same 172dp poster-only footprint for movies and TV seasons; seasons carry an upper-right `S#` marker instead of a caption. The shared native 8dp wrapper padding was retained.

**Final structural correction:** The separately implemented Acquiring `LazyRow` also inherited Home's outer `ScrollToTopBringIntoViewSpec`, whereas every configured row restores the default nested bring-into-view policy around its `ItemRow`. Acquiring now uses that same native policy boundary. No spacing constant or card geometry was changed.

**Native-mechanics follow-up:** Matching the nested policy was insufficient because Acquiring still maintained a parallel `LazyRow` without native `ItemRow` entry/restoration mechanics. Acquiring now renders through generic `ItemRow` with its existing stable Bundle-safe item keys and custom poster cards. No spacing constant or card geometry changed.

**Status:** Resolved. The native `ItemRow` migration and Android TV validation passed with `tv_multi_season`, `mixed`, and the focus-removal sequence.
