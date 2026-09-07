package com.github.damontecres.wholphin.ui.main

import com.github.damontecres.wholphin.data.model.AcquisitionAggregate
import com.github.damontecres.wholphin.data.model.AcquisitionEntry
import com.github.damontecres.wholphin.data.model.AcquisitionEpisode
import com.github.damontecres.wholphin.data.model.AcquisitionProgress
import com.github.damontecres.wholphin.data.model.AcquisitionStatus
import com.github.damontecres.wholphin.data.model.CatalogMediaType
import com.github.damontecres.wholphin.data.model.DiscoverItem
import com.github.damontecres.wholphin.data.model.JellyfinAcquisitionReadiness
import com.github.damontecres.wholphin.data.model.MediaKey
import com.github.damontecres.wholphin.data.model.RequestStatus
import com.github.damontecres.wholphin.data.model.SeasonAcquisition
import com.github.damontecres.wholphin.data.model.SeerrAcquisitionState
import com.github.damontecres.wholphin.data.model.SeerrAvailability
import com.github.damontecres.wholphin.data.model.SeerrItemType
import com.github.damontecres.wholphin.data.model.SeerrRequestAcquisition
import com.github.damontecres.wholphin.data.model.SeerrRequestState
import com.github.damontecres.wholphin.services.AcquisitionIndexSnapshot
import com.github.damontecres.wholphin.services.SeerrAcquisitionTrackerState
import com.github.damontecres.wholphin.services.toAcquisitionIndex
import com.github.damontecres.wholphin.ui.cards.CardAcquisitionState
import com.github.damontecres.wholphin.ui.nav.Destination
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.jellyfin.sdk.model.api.BaseItemKind
import java.util.UUID

class HomeAcquiringSourceTest {
    @Test
    fun movieQueueingQueuedProgressAndFinishingAreIncluded() {
        val queueing = movie(1, 101, SeerrAcquisitionState.Queueing)
        val queued = movie(2, 102, movieState(entry(AcquisitionStatus.QUEUED)))
        val progress = movie(3, 103, movieState(entry(AcquisitionStatus.DOWNLOADING, 40.0, true)))
        val finishing =
            movie(
                4,
                104,
                movieState(
                    entry(
                        AcquisitionStatus.COMPLETED,
                        sizeLeft = 0.0,
                        observedProgress = true,
                        presentInQueue = false,
                        completed = true,
                    ),
                ),
            )

        val items = snapshot(queueing, queued, progress, finishing).toHomeAcquiringState().items.associateBy { it.key }

        assertEquals(CardAcquisitionState.QUEUEING, items.getValue(movieKey(101)).acquisitionPresentation?.acquisitionState)
        assertEquals(CardAcquisitionState.QUEUED, items.getValue(movieKey(102)).acquisitionPresentation?.acquisitionState)
        assertEquals(.6f, items.getValue(movieKey(103)).acquisitionPresentation?.acquisitionProgress)
        assertEquals(CardAcquisitionState.FINISHING, items.getValue(movieKey(104)).acquisitionPresentation?.acquisitionState)
    }

    @Test
    fun staleProcessingProblemAndHistoricalCompletionAreExcluded() {
        val processing = movie(5, 105, SeerrAcquisitionState.Processing)
        val problem = movie(6, 106, movieState(entry(AcquisitionStatus.PROBLEM)))
        val availabilityOnly =
            movie(
                25,
                125,
                SeerrAcquisitionState.None,
                availability = SeerrAvailability.AVAILABLE,
            )
        val historical =
            movie(
                7,
                107,
                movieState(
                    entry(
                        AcquisitionStatus.COMPLETED,
                        0.0,
                        true,
                        presentInQueue = false,
                        completed = true,
                    ),
                ),
                readiness = JellyfinAcquisitionReadiness(movieItemId = UUID.randomUUID()),
                availability = SeerrAvailability.AVAILABLE,
            )

        assertTrue(snapshot(processing, problem, availabilityOnly, historical).toHomeAcquiringState().items.isEmpty())
    }

    @Test
    fun movieGraceExpiresAndLiveUpgradeOnReadyMovieRemainsIncluded() {
        val withinGrace =
            movie(
                8,
                108,
                movieState(entry(AcquisitionStatus.DOWNLOADING, 50.0, true, false, absentPollCount = 2)),
            )
        val expired =
            movie(
                9,
                109,
                movieState(entry(AcquisitionStatus.DOWNLOADING, 50.0, true, false, absentPollCount = 3)),
            )
        val upgrade =
            movie(
                10,
                110,
                movieState(entry(AcquisitionStatus.DOWNLOADING, 25.0, true)),
                readiness = JellyfinAcquisitionReadiness(movieItemId = UUID.randomUUID()),
            )

        val keys = snapshot(withinGrace, expired, upgrade).toHomeAcquiringState().items.map { it.key }.toSet()

        assertEquals(setOf(movieKey(108), movieKey(110)), keys)
    }

    @Test
    fun activeSeriesSeasonsProduceIndependentCanonicalItems() {
        val seriesId = UUID.randomUUID()
        val seasonOne =
            series(
                11,
                111,
                1,
                tvState(1, entry(AcquisitionStatus.QUEUED, season = 1)),
                JellyfinAcquisitionReadiness(seriesItemId = seriesId),
            )
        val seasonTwo =
            series(
                12,
                111,
                2,
                tvState(2, entry(AcquisitionStatus.DOWNLOADING, 50.0, true, season = 2)),
            )

        val items = snapshot(seasonOne, seasonTwo).toHomeAcquiringState().items.associateBy { it.key }

        assertEquals(setOf(seasonKey(111, 1), seasonKey(111, 2)), items.keys)
        assertEquals(CardAcquisitionState.QUEUED, items.getValue(seasonKey(111, 1)).acquisitionPresentation?.acquisitionState)
        assertEquals(.5f, items.getValue(seasonKey(111, 2)).acquisitionPresentation?.acquisitionProgress)
        assertEquals(seriesId, items.getValue(seasonKey(111, 1)).verifiedJellyfinItemId)
    }

    @Test
    fun authoritativeSeasonWithoutRequestSeasonMetadataProducesExactItem() {
        val acquisition =
            series(
                34,
                134,
                3,
                tvState(3, entry(AcquisitionStatus.DOWNLOADING, 50.0, true, season = 3)),
            ).let { request ->
                request.copy(request = request.request.copy(requestedSeasonNumbers = emptySet()))
            }

        val items = snapshot(acquisition).toHomeAcquiringState().items

        assertEquals(listOf(seasonKey(134, 3)), items.map { it.key })
        assertEquals(3, items.single().seasonNumber)
        assertEquals(.5f, items.single().acquisitionPresentation?.acquisitionProgress)
    }

    @Test
    fun unassignedTvEvidenceDoesNotInventHomeSeasonItem() {
        val acquisition =
            series(
                35,
                135,
                3,
                SeerrAcquisitionState.Tv(
                    seasons = emptyList(),
                    unassignedEntries = listOf(entry(AcquisitionStatus.DOWNLOADING, 50.0, true)),
                ),
            ).let { request ->
                request.copy(
                    request =
                        request.request.copy(
                            requestedSeasonNumbers = emptySet(),
                            seasonEpisodeCounts = emptyMap(),
                        ),
                )
            }

        assertTrue(snapshot(acquisition).toHomeAcquiringState().items.isEmpty())
    }

    @Test
    fun tvSeasonLifecycleUsesCanonicalQueueingQueuedProgressAndFinishingPresentation() {
        val queueing = series(30, 130, 1, SeerrAcquisitionState.Queueing)
        val queued = series(31, 131, 2, tvState(2, entry(AcquisitionStatus.QUEUED, season = 2)))
        val progress = series(32, 132, 3, tvState(3, entry(AcquisitionStatus.DOWNLOADING, 60.0, true, season = 3)))
        val finishing =
            series(
                33,
                133,
                4,
                tvState(
                    4,
                    entry(
                        AcquisitionStatus.COMPLETED,
                        sizeLeft = 0.0,
                        observedProgress = true,
                        presentInQueue = false,
                        completed = true,
                        season = 4,
                    ),
                ),
            )

        val items = snapshot(queueing, queued, progress, finishing).toHomeAcquiringState().items.associateBy { it.key }

        assertEquals(CardAcquisitionState.QUEUEING, items.getValue(seasonKey(130, 1)).acquisitionPresentation?.acquisitionState)
        assertEquals(CardAcquisitionState.QUEUED, items.getValue(seasonKey(131, 2)).acquisitionPresentation?.acquisitionState)
        assertEquals(.4f, items.getValue(seasonKey(132, 3)).acquisitionPresentation?.acquisitionProgress)
        assertEquals(CardAcquisitionState.FINISHING, items.getValue(seasonKey(133, 4)).acquisitionPresentation?.acquisitionState)
    }

    @Test
    fun sameSeasonVariantsDeduplicateAndConflictingPresentationStaysCoarse() {
        val normal = series(34, 134, 3, tvState(3, entry(AcquisitionStatus.QUEUED, season = 3)))
        val fourK =
            series(
                35,
                134,
                3,
                tvState(3, entry(AcquisitionStatus.DOWNLOADING, 50.0, true, season = 3)),
                is4k = true,
            )

        val item = snapshot(normal, fourK).toHomeAcquiringState().items.single()

        assertEquals(seasonKey(134, 3), item.key)
        assertEquals(setOf(35, 34), item.requestIds)
        assertNull(item.acquisitionPresentation)
        assertEquals(CardAcquisitionState.ACQUIRING, item.cardPresentation().acquisitionState)
    }

    @Test
    fun sameRequestSeasonsRemainAdjacentAndNumericallyOrderedIncludingSpecials() {
        val base = series(36, 135, 3, SeerrAcquisitionState.Queueing, createdAt = "2026-09-05T12:00:00Z")
        val multi =
            base.copy(
                request =
                    base.request.copy(
                        requestedSeasonNumbers = setOf(5, 0, 4, 3),
                        seasonEpisodeCounts = mapOf(0 to 1, 3 to 1, 4 to 1, 5 to 1),
                        seasonAvailability =
                            mapOf(
                                0 to SeerrAvailability.PROCESSING,
                                3 to SeerrAvailability.PROCESSING,
                                4 to SeerrAvailability.PROCESSING,
                                5 to SeerrAvailability.PROCESSING,
                            ),
                    ),
            )

        val items = snapshot(multi).toHomeAcquiringState().items

        assertEquals(listOf(0, 3, 4, 5), items.map { it.seasonNumber })
        assertEquals(seasonKey(135, 0), items.first().key)
    }

    @Test
    fun tvSeasonOrderingUsesImmutableRequestTimeBeforeSeasonNumber() {
        val newer =
            series(37, 136, 4, SeerrAcquisitionState.Queueing, createdAt = "2026-09-05T12:00:00Z")
        val older =
            series(99, 136, 3, SeerrAcquisitionState.Queueing, createdAt = "2026-09-04T12:00:00Z")

        val keys = snapshot(older, newer).toHomeAcquiringState().items.map { it.key }

        assertEquals(listOf(seasonKey(136, 4), seasonKey(136, 3)), keys)
    }

    @Test
    fun movieVariantsDeduplicateAndConflictingPresentationBecomesCoarse() {
        val normal = movie(13, 112, movieState(entry(AcquisitionStatus.QUEUED)))
        val fourK =
            movie(
                14,
                112,
                movieState(entry(AcquisitionStatus.DOWNLOADING, 20.0, true)),
                is4k = true,
            )

        val item = snapshot(normal, fourK).toHomeAcquiringState().items.single()

        assertEquals(movieKey(112), item.key)
        assertEquals(setOf(14, 13), item.requestIds)
        assertEquals(CardAcquisitionState.ACQUIRING, item.acquisitionPresentation?.acquisitionState)
    }

    @Test
    fun movieAndSeriesWithSameTmdbIdRemainDistinct() {
        val movie = movie(15, 113, SeerrAcquisitionState.Queueing)
        val series = series(16, 113, 1, SeerrAcquisitionState.Queueing)

        val keys = snapshot(movie, series).toHomeAcquiringState().items.map { it.key }.toSet()

        assertEquals(setOf(movieKey(113), seasonKey(113, 1)), keys)
    }

    @Test
    fun orderingUsesCreatedTimeThenRequestIdAndTypedIdentity() {
        val newest = movie(17, 114, SeerrAcquisitionState.Queueing, createdAt = "2026-09-05T12:00:00Z")
        val older = movie(99, 115, SeerrAcquisitionState.Queueing, createdAt = "2026-09-04T12:00:00Z")
        val fallbackHigher = movie(20, 116, SeerrAcquisitionState.Queueing)
        val fallbackLower = movie(19, 117, SeerrAcquisitionState.Queueing)

        val keys = snapshot(fallbackLower, older, fallbackHigher, newest).toHomeAcquiringState().items.map { it.key }

        assertEquals(listOf(movieKey(114), movieKey(115), movieKey(116), movieKey(117)), keys)
    }

    @Test
    fun missingMetadataAndUnresolvedIdentityAreOmitted() {
        val noMetadata = movie(21, 118, SeerrAcquisitionState.Queueing, metadata = null)
        val unresolved = movie(22, null, SeerrAcquisitionState.Queueing)

        assertTrue(snapshot(noMetadata, unresolved).toHomeAcquiringState().items.isEmpty())
    }

    @Test
    fun verifiedReadinessIdAppearsWithoutChangingCatalogIdentity() {
        val localId = UUID.randomUUID()
        val nonLocal = movie(23, 119, SeerrAcquisitionState.Queueing)
        val localUpgrade =
            movie(
                23,
                119,
                movieState(entry(AcquisitionStatus.DOWNLOADING, 80.0, true)),
                readiness = JellyfinAcquisitionReadiness(movieItemId = localId),
            )

        val before = snapshot(nonLocal).toHomeAcquiringState().items.single()
        val after = snapshot(localUpgrade).toHomeAcquiringState().items.single()

        assertEquals(before.key, after.key)
        assertNull(before.verifiedJellyfinItemId)
        assertEquals(localId, after.verifiedJellyfinItemId)
    }

    @Test
    fun homeCardPresentationPreservesCanonicalMovieAndSeasonProgress() {
        val movie =
            snapshot(movie(26, 126, movieState(entry(AcquisitionStatus.DOWNLOADING, 24.0, true))))
                .toHomeAcquiringState().items.single()
        val series =
            snapshot(series(27, 127, 2, tvState(2, entry(AcquisitionStatus.DOWNLOADING, 24.0, true, season = 2))))
                .toHomeAcquiringState().items.single()

        assertEquals(.76f, movie.cardPresentation().acquisitionProgress)
        assertNull(movie.cardPresentation().acquisitionState)
        assertEquals(.76f, series.cardPresentation().acquisitionProgress)
        assertNull(series.cardPresentation().acquisitionState)
    }

    @Test
    fun homeArtworkPresentationIsCaptionlessAndUsesCompactSeasonBadges() {
        val movie =
            snapshot(movie(40, 140, movieState(entry(AcquisitionStatus.DOWNLOADING, 24.0, true))))
                .toHomeAcquiringState().items.single()
        val seasonThree =
            snapshot(series(41, 141, 3, tvState(3, entry(AcquisitionStatus.DOWNLOADING, 24.0, true, season = 3))))
                .toHomeAcquiringState().items.single()
        val specials =
            snapshot(series(42, 142, 0, tvState(0, entry(AcquisitionStatus.QUEUED, season = 0))))
                .toHomeAcquiringState().items.single()

        assertNull(movie.artworkPresentation().seasonBadge)
        assertEquals("S3", seasonThree.artworkPresentation().seasonBadge)
        assertEquals("S0", specials.artworkPresentation().seasonBadge)
        assertEquals(movie.cardPresentation(), movie.artworkPresentation().mediaPresentation)
        assertEquals(seasonThree.cardPresentation(), seasonThree.artworkPresentation().mediaPresentation)
        assertEquals(specials.cardPresentation(), specials.artworkPresentation().mediaPresentation)
    }

    @Test
    fun verifiedIdentityChangesDestinationWithoutChangingCatalogIdentity() {
        val localId = UUID.randomUUID()
        val localSeriesId = UUID.randomUUID()
        val localSeasonId = UUID.randomUUID()
        val remote = snapshot(movie(28, 128, SeerrAcquisitionState.Queueing)).toHomeAcquiringState().items.single()
        val local =
            snapshot(
                movie(
                    28,
                    128,
                    movieState(entry(AcquisitionStatus.DOWNLOADING, 50.0, true)),
                    readiness = JellyfinAcquisitionReadiness(movieItemId = localId),
                ),
            ).toHomeAcquiringState().items.single()

        assertEquals(remote.key, local.key)
        assertTrue(remote.destination() is Destination.DiscoveredItem)
        assertEquals(
            Destination.MediaItem(
                localId,
                BaseItemKind.MOVIE,
            ),
            local.destination(),
        )
        val remoteSeries =
            snapshot(series(29, 129, 2, SeerrAcquisitionState.Queueing))
                .toHomeAcquiringState().items.single()
        val seriesOnly =
            snapshot(
                series(
                    29,
                    129,
                    2,
                    tvState(2, entry(AcquisitionStatus.QUEUED, season = 2)),
                    readiness = JellyfinAcquisitionReadiness(seriesItemId = localSeriesId),
                ),
            ).toHomeAcquiringState().items.single()
        val series =
            snapshot(
                series(
                    29,
                    129,
                    2,
                    tvState(2, entry(AcquisitionStatus.QUEUED, season = 2)),
                    readiness =
                        JellyfinAcquisitionReadiness(
                            seriesItemId = localSeriesId,
                            seasonItemIds = mapOf(2 to localSeasonId),
                        ),
                ),
            ).toHomeAcquiringState().items.single()
        assertEquals(remoteSeries.key, seriesOnly.key)
        assertEquals(seriesOnly.key, series.key)
        assertTrue(remoteSeries.destination() is Destination.DiscoveredItem)
        assertEquals(Destination.MediaItem(localSeriesId, BaseItemKind.SERIES), seriesOnly.destination())
        assertEquals(
            Destination.SeriesOverview(
                localSeriesId,
                BaseItemKind.SERIES,
                com.github.damontecres.wholphin.ui.detail.series.SeasonEpisodeIds(localSeasonId, 2, null, null),
            ),
            series.destination(),
        )
    }

    @Test
    fun configuredRowsKeepStableKeysWhenAcquiringRowAppearsOrDisappears() {
        val configured = (0..2).map(::configuredHomeRowKey)
        val withAcquiring = listOf("acquiring") + (0..2).map(::configuredHomeRowKey)

        assertEquals(listOf("configured:0", "configured:1", "configured:2"), configured)
        assertEquals(configured, withAcquiring.drop(1))
        assertEquals(configured, (0..2).map(::configuredHomeRowKey))
    }

    @Test
    fun acquiringComposeKeyIsStableSaveableAndMediaTypeSpecific() {
        val movie = movieKey(3476)
        val series = seasonKey(3476, 3)

        assertEquals("acquiring:MOVIE:3476", movie.composeSaveableKey())
        assertEquals("acquiring:SERIES:3476:season:3", series.composeSaveableKey())
        assertEquals(movie.composeSaveableKey(), movieKey(3476).composeSaveableKey())
        assertTrue(movie.composeSaveableKey() != series.composeSaveableKey())
    }

    @Test
    fun acquiringMoreUsesStableNonMediaKeyAndExistingDownloadsDestination() {
        val movie = movieKey(3476).composeSaveableKey()
        val season = seasonKey(3476, 3).composeSaveableKey()

        assertEquals("acquiring:more", HOME_ACQUIRING_MORE_KEY)
        assertTrue(HOME_ACQUIRING_MORE_KEY != movie)
        assertTrue(HOME_ACQUIRING_MORE_KEY != season)
        assertEquals(Destination.Downloads, homeAcquiringMoreDestination())
    }

    @Test
    fun acquiringFocusRetainsIdentityMovesNearbyAndFallsBackOnce() {
        val first = movieKey(130)
        val focused = movieKey(131)
        val last = movieKey(132)

        assertEquals(
            AcquiringFocusResolution.Unchanged,
            resolveAcquiringFocus(true, listOf(first, focused), listOf(last, first, focused), focused),
        )
        assertEquals(
            AcquiringFocusResolution.Card(last),
            resolveAcquiringFocus(true, listOf(first, focused, last), listOf(first, last), focused),
        )
        assertEquals(
            AcquiringFocusResolution.ConfiguredFallback,
            resolveAcquiringFocus(true, listOf(focused), emptyList(), focused),
        )
        assertEquals(
            AcquiringFocusResolution.Unchanged,
            resolveAcquiringFocus(true, emptyList(), listOf(first), null),
        )
        assertEquals(
            AcquiringFocusResolution.Unchanged,
            resolveAcquiringFocus(false, listOf(focused), emptyList(), focused),
        )
    }

    @Test
    @OptIn(ExperimentalCoroutinesApi::class)
    fun emptyAcquisitionIndexProducesAndRepublishesEmptySharedState() = runTest {
        val snapshots = MutableStateFlow(AcquisitionIndexSnapshot())
        val source = HomeAcquiringSource(snapshots, backgroundScope)
        runCurrent()
        assertTrue(source.state.value.items.isEmpty())

        snapshots.value = snapshot(movie(24, 120, SeerrAcquisitionState.Queueing))
        runCurrent()
        assertEquals(movieKey(120), source.state.value.items.single().key)

        snapshots.value = AcquisitionIndexSnapshot()
        runCurrent()
        assertTrue(source.state.value.items.isEmpty())
    }

    private fun snapshot(vararg acquisitions: SeerrRequestAcquisition): AcquisitionIndexSnapshot =
        SeerrAcquisitionTrackerState(
            requests = acquisitions.filterNot { it.acquisition == SeerrAcquisitionState.Queueing },
            queueingRequests = acquisitions.filter { it.acquisition == SeerrAcquisitionState.Queueing },
        ).toAcquisitionIndex()

    private fun movie(
        requestId: Int,
        tmdbId: Int?,
        acquisition: SeerrAcquisitionState,
        readiness: JellyfinAcquisitionReadiness = JellyfinAcquisitionReadiness(),
        availability: SeerrAvailability = SeerrAvailability.PROCESSING,
        is4k: Boolean = false,
        createdAt: String? = null,
        metadata: DiscoverItem? = discover(tmdbId ?: 1, SeerrItemType.MOVIE),
    ) = request(
        requestId,
        tmdbId,
        SeerrItemType.MOVIE,
        acquisition,
        readiness,
        availability,
        is4k,
        createdAt,
        metadata,
    )

    private fun series(
        requestId: Int,
        tmdbId: Int,
        season: Int,
        acquisition: SeerrAcquisitionState,
        readiness: JellyfinAcquisitionReadiness = JellyfinAcquisitionReadiness(),
        is4k: Boolean = false,
        createdAt: String? = null,
    ) = request(
        requestId,
        tmdbId,
        SeerrItemType.TV,
        acquisition,
        readiness,
        is4k = is4k,
        createdAt = createdAt,
        season = season,
        metadata = discover(tmdbId, SeerrItemType.TV),
    )

    private fun request(
        requestId: Int,
        tmdbId: Int?,
        type: SeerrItemType,
        acquisition: SeerrAcquisitionState,
        readiness: JellyfinAcquisitionReadiness = JellyfinAcquisitionReadiness(),
        availability: SeerrAvailability = SeerrAvailability.PROCESSING,
        is4k: Boolean = false,
        createdAt: String? = null,
        metadata: DiscoverItem? = null,
        season: Int = 1,
    ) = SeerrRequestAcquisition(
        request =
            SeerrRequestState(
                requestId = requestId,
                mediaId = null,
                tmdbId = tmdbId,
                discoverItem = metadata,
                requestedById = null,
                requestedByName = null,
                status = RequestStatus.APPROVED,
                mediaType = type,
                is4k = is4k,
                availability = availability,
                seasonAvailability = if (type == SeerrItemType.TV) mapOf(season to availability) else emptyMap(),
                seasonUpdatedAt = emptyMap(),
                seasonEpisodeCounts = if (type == SeerrItemType.TV) mapOf(season to 1) else emptyMap(),
                requestedSeasonNumbers = if (type == SeerrItemType.TV) setOf(season) else emptySet(),
                createdAt = createdAt,
                updatedAt = null,
                jellyfinReadiness = readiness,
            ),
        acquisition = acquisition,
    )

    private fun movieState(entry: AcquisitionEntry) =
        SeerrAcquisitionState.Movie(
            AcquisitionAggregate(
                status = entry.status,
                progress = entry.sizeLeft?.let { AcquisitionProgress(100.0, it) },
                entries = listOf(entry),
            ),
        )

    private fun tvState(season: Int, entry: AcquisitionEntry) =
        SeerrAcquisitionState.Tv(
            seasons =
                listOf(
                    SeasonAcquisition(
                        season,
                        AcquisitionAggregate(
                            status = entry.status,
                            progress = entry.sizeLeft?.let { AcquisitionProgress(100.0, it) },
                            entries = listOf(entry),
                        ),
                    ),
                ),
            unassignedEntries = emptyList(),
        )

    private fun entry(
        status: AcquisitionStatus,
        sizeLeft: Double? = null,
        observedProgress: Boolean = false,
        presentInQueue: Boolean = true,
        completed: Boolean = false,
        absentPollCount: Int = 0,
        season: Int? = null,
    ) = AcquisitionEntry(
        externalId = 1,
        downloadId = "download",
        mediaType = if (season == null) "movie" else "tv",
        title = if (season == null) "Movie" else "Series.S%02dE01".format(season),
        status = status,
        rawStatus = null,
        totalSize = sizeLeft?.let { 100.0 },
        sizeLeft = sizeLeft,
        estimatedCompletionTime = null,
        timeLeft = null,
        episode = season?.let { AcquisitionEpisode(null, it, 1, null, false) },
        presentInQueue = presentInQueue,
        hasObservedProgress = observedProgress,
        observedSuccessfulTransferCompletion = completed,
        absentPollCount = absentPollCount,
    )

    private fun discover(id: Int, type: SeerrItemType) =
        DiscoverItem(
            id = id,
            type = type,
            title = "Item $id",
            subtitle = null,
            overview = "Overview",
            availability = SeerrAvailability.PROCESSING,
            releaseDate = null,
            posterUrl = "poster/$id",
            backDropUrl = "backdrop/$id",
            logoUrl = null,
            jellyfinItemId = null,
        )

    private fun movieKey(tmdbId: Int) = MediaKey.Catalog(CatalogMediaType.MOVIE, tmdbId)

    private fun seriesKey(tmdbId: Int) = MediaKey.Catalog(CatalogMediaType.SERIES, tmdbId)

    private fun seasonKey(tmdbId: Int, seasonNumber: Int) = MediaKey.Season(seriesKey(tmdbId), seasonNumber)
}
