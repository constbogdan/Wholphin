package com.github.damontecres.wholphin.ui.main

import com.github.damontecres.wholphin.data.model.CatalogMediaType
import com.github.damontecres.wholphin.data.model.DiscoverItem
import com.github.damontecres.wholphin.data.model.MediaKey
import com.github.damontecres.wholphin.data.model.SeerrAvailability
import com.github.damontecres.wholphin.data.model.SeerrItemType
import com.github.damontecres.wholphin.ui.cards.CardAcquisitionState
import com.github.damontecres.wholphin.ui.cards.CardMediaPresentation

internal object HomeAcquiringFixtures {
    private const val SERIES_TMDB_ID = 1399

    private val movieStates =
        HomeAcquiringState(
            listOf(
                movie(550, "Fixture Movie — Queueing", CardAcquisitionState.QUEUEING, 101),
                movie(680, "Fixture Movie — Queued", CardAcquisitionState.QUEUED, 102),
                movie(155, "Fixture Movie — 35%", progress = .35f, requestId = 103),
                movie(27205, "Fixture Movie — Finishing", CardAcquisitionState.FINISHING, 104),
            ),
        )

    private val tvMultiSeason =
        HomeAcquiringState(
            listOf(
                season(SERIES_TMDB_ID, 3, "Fixture Series", progress = .42f, requestId = 201),
                season(SERIES_TMDB_ID, 4, "Fixture Series", CardAcquisitionState.QUEUED, 202),
                season(SERIES_TMDB_ID, 5, "Fixture Series", CardAcquisitionState.FINISHING, 203),
            ),
        )

    private val mixed =
        HomeAcquiringState(
            listOf(
                movie(603, "Mixed Movie — 20%", progress = .20f, requestId = 301),
                movie(157336, "Mixed Movie — Finishing", CardAcquisitionState.FINISHING, 302),
                season(66732, 2, "Mixed Series", CardAcquisitionState.QUEUED, 303),
                season(66732, 3, "Mixed Series", progress = .65f, requestId = 304),
            ),
        )

    private val focusBefore =
        HomeAcquiringState(
            listOf(
                movie(11, "Focus Survivor A", progress = .25f, requestId = 401),
                movie(22, "Focus Remove Me", CardAcquisitionState.QUEUED, 402),
                season(94997, 2, "Focus Survivor B", progress = .60f, requestId = 403),
            ),
        )

    private val focusCardRemoved =
        HomeAcquiringState(
            listOf(
                movie(11, "Focus Survivor A", progress = .25f, requestId = 401),
                season(94997, 2, "Focus Survivor B", progress = .60f, requestId = 403),
            ),
        )

    fun state(scenario: HomeAcquiringFixtureScenario): HomeAcquiringState =
        when (scenario) {
            HomeAcquiringFixtureScenario.EMPTY,
            HomeAcquiringFixtureScenario.FOCUS_ROW_REMOVED,
            -> HomeAcquiringState()
            HomeAcquiringFixtureScenario.MOVIE_STATES -> movieStates
            HomeAcquiringFixtureScenario.TV_MULTI_SEASON -> tvMultiSeason
            HomeAcquiringFixtureScenario.MIXED -> mixed
            HomeAcquiringFixtureScenario.FOCUS_BEFORE -> focusBefore
            HomeAcquiringFixtureScenario.FOCUS_CARD_REMOVED -> focusCardRemoved
        }

    private fun movie(
        tmdbId: Int,
        title: String,
        state: CardAcquisitionState? = null,
        requestId: Int,
        progress: Float? = null,
    ) = item(
        key = MediaKey.Catalog(CatalogMediaType.MOVIE, tmdbId),
        tmdbId = tmdbId,
        type = SeerrItemType.MOVIE,
        title = title,
        presentation = CardMediaPresentation(progress, state),
        requestId = requestId,
    )

    private fun season(
        tmdbId: Int,
        seasonNumber: Int,
        title: String,
        state: CardAcquisitionState? = null,
        requestId: Int,
        progress: Float? = null,
    ) = item(
        key =
            MediaKey.Season(
                MediaKey.Catalog(CatalogMediaType.SERIES, tmdbId),
                seasonNumber,
            ),
        tmdbId = tmdbId,
        type = SeerrItemType.TV,
        title = title,
        presentation = CardMediaPresentation(progress, state),
        requestId = requestId,
        seasonNumber = seasonNumber,
    )

    private fun item(
        key: MediaKey,
        tmdbId: Int,
        type: SeerrItemType,
        title: String,
        presentation: CardMediaPresentation,
        requestId: Int,
        seasonNumber: Int? = null,
    ) = HomeAcquiringItem(
        key = key,
        item =
            DiscoverItem(
                id = tmdbId,
                type = type,
                title = title,
                subtitle = "Debug acquisition fixture",
                overview = "Static debug-only data for Android TV acquisition UI validation.",
                availability = SeerrAvailability.PROCESSING,
                releaseDate = null,
                posterUrl = "https://picsum.photos/seed/wholphin-$tmdbId/500/750",
                backDropUrl = "https://picsum.photos/seed/wholphin-backdrop-$tmdbId/1280/720",
                logoUrl = null,
                jellyfinItemId = null,
            ),
        verifiedJellyfinItemId = null,
        verifiedJellyfinSeasonId = null,
        seasonNumber = seasonNumber,
        acquisitionPresentation = presentation,
        requestedAtEpochMillis = requestId.toLong(),
        requestIds = setOf(requestId),
    )
}
