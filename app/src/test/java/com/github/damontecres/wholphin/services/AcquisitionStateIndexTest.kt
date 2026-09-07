package com.github.damontecres.wholphin.services

import com.github.damontecres.wholphin.data.model.AcquisitionAggregate
import com.github.damontecres.wholphin.data.model.AcquisitionEntry
import com.github.damontecres.wholphin.data.model.AcquisitionEpisode
import com.github.damontecres.wholphin.data.model.AcquisitionProgress
import com.github.damontecres.wholphin.data.model.AcquisitionStatus
import com.github.damontecres.wholphin.data.model.CatalogMediaType
import com.github.damontecres.wholphin.data.model.JellyfinAcquisitionReadiness
import com.github.damontecres.wholphin.data.model.MediaKey
import com.github.damontecres.wholphin.data.model.RequestStatus
import com.github.damontecres.wholphin.data.model.SeasonAcquisition
import com.github.damontecres.wholphin.data.model.SeerrAcquisitionState
import com.github.damontecres.wholphin.data.model.SeerrAvailability
import com.github.damontecres.wholphin.data.model.SeerrItemType
import com.github.damontecres.wholphin.data.model.SeerrRequestAcquisition
import com.github.damontecres.wholphin.data.model.SeerrRequestState
import com.github.damontecres.wholphin.data.model.TvSeasonLifecycle
import com.github.damontecres.wholphin.data.model.toTvSeasonTargets
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.util.UUID

class AcquisitionStateIndexTest {
    @Test
    fun movieAcquisitionMapsToTypedCatalogIdentity() {
        val movie = request(1, 10, SeerrItemType.MOVIE)

        val index = SeerrAcquisitionTrackerState(requests = listOf(movie)).toAcquisitionIndex()

        assertEquals(listOf(1), index.byMediaKey[MediaKey.Catalog(CatalogMediaType.MOVIE, 10)]?.requestIds())
    }

    @Test
    fun tvSeasonsMapIndependentlyIncludingSpecials() {
        val tv = request(2, 20, SeerrItemType.TV, seasons = setOf(2, 0, 1))

        val index = SeerrAcquisitionTrackerState(requests = listOf(tv)).toAcquisitionIndex()
        val series = MediaKey.Catalog(CatalogMediaType.SERIES, 20)

        assertEquals(listOf(2), index.byMediaKey[MediaKey.Season(series, 0)]?.requestIds())
        assertEquals(listOf(2), index.byMediaKey[MediaKey.Season(series, 1)]?.requestIds())
        assertEquals(listOf(2), index.byMediaKey[MediaKey.Season(series, 2)]?.requestIds())
    }

    @Test
    fun representedSeasonIsIndexedEvenWhenRequestSeasonSetIsMissing() {
        val tv =
            request(
                requestId = 3,
                tmdbId = 30,
                type = SeerrItemType.TV,
                seasonEpisodeCounts = mapOf(4 to 4),
                acquisition =
                    tvAcquisition(
                        4,
                        listOf(entry(4, 1, "Show.S04E01", 4.0)),
                    ),
            )

        val index = SeerrAcquisitionTrackerState(requests = listOf(tv)).toAcquisitionIndex()
        val target = index.seasonTarget(30, 4)

        assertEquals(
            listOf(3),
            index.byMediaKey[MediaKey.Season(MediaKey.Catalog(CatalogMediaType.SERIES, 30), 4)]?.requestIds(),
        )
        assertEquals(4, target.seasonNumber)
        assertEquals(TvSeasonLifecycle.IN_PROGRESS, target.lifecycle)
        assertEquals(.24, target.acquisitionProjection.displayedFraction, .0001)
        assertTrue(target.hasCurrentAcquisitionWork)
    }

    @Test
    fun unassignedTvEvidenceDoesNotInventSeasonIdentity() {
        val tv =
            request(
                requestId = 4,
                tmdbId = 31,
                type = SeerrItemType.TV,
                acquisition =
                    SeerrAcquisitionState.Tv(
                        seasons = emptyList(),
                        unassignedEntries = listOf(entry(1, 1, "Unknown", 50.0).copy(episode = null)),
                    ),
            )

        val index = SeerrAcquisitionTrackerState(requests = listOf(tv)).toAcquisitionIndex()

        assertTrue(tv.toTvSeasonTargets().isEmpty())
        assertTrue(index.byMediaKey.isEmpty())
        assertEquals(listOf(4), index.unresolved.requestIds())
    }

    @Test
    fun multipleRequestsAndQualityVariantsArePreservedDeterministically() {
        val normal = request(8, 40, SeerrItemType.MOVIE, is4k = false)
        val fourK = request(8, 40, SeerrItemType.MOVIE, is4k = true)
        val later = request(9, 40, SeerrItemType.MOVIE, is4k = false)

        val index = SeerrAcquisitionTrackerState(requests = listOf(later, fourK, normal)).toAcquisitionIndex()
        val entries = index.byMediaKey.getValue(MediaKey.Catalog(CatalogMediaType.MOVIE, 40))

        assertEquals(listOf(8, 8, 9), entries.requestIds())
        assertEquals(listOf(false, true, false), entries.map { it.request.request.is4k })
    }

    @Test
    fun requestsForDifferentSeasonsDoNotContaminateOneAnother() {
        val seasonOne = request(11, 50, SeerrItemType.TV, seasons = setOf(1))
        val seasonTwo = request(12, 50, SeerrItemType.TV, seasons = setOf(2))
        val series = MediaKey.Catalog(CatalogMediaType.SERIES, 50)

        val index = SeerrAcquisitionTrackerState(requests = listOf(seasonTwo, seasonOne)).toAcquisitionIndex()

        assertEquals(listOf(11), index.byMediaKey[MediaKey.Season(series, 1)]?.requestIds())
        assertEquals(listOf(12), index.byMediaKey[MediaKey.Season(series, 2)]?.requestIds())
    }

    @Test
    fun tvSeasonIndexCarriesCanonicalPackAndEpisodeNormalizedProgress() {
        val pack =
            request(
                requestId = 15,
                tmdbId = 70,
                type = SeerrItemType.TV,
                seasons = setOf(2),
                seasonEpisodeCounts = mapOf(2 to 4),
                acquisition = tvAcquisition(2, listOf(entry(2, 1, "Show.S02", 60.0), entry(2, 2, "Show.S02", 60.0))),
            )
        val episode =
            request(
                requestId = 16,
                tmdbId = 80,
                type = SeerrItemType.TV,
                seasons = setOf(2),
                seasonEpisodeCounts = mapOf(2 to 4),
                acquisition = tvAcquisition(2, listOf(entry(2, 1, "Show.S02E01", 4.0))),
            )

        val index = SeerrAcquisitionTrackerState(requests = listOf(pack, episode)).toAcquisitionIndex()

        assertEquals(
            pack.toTvSeasonTargets().single().acquisitionProjection.displayedFraction,
            index.seasonTarget(70, 2).acquisitionProjection.displayedFraction,
            0.0001,
        )
        assertEquals(
            episode.toTvSeasonTargets().single().acquisitionProjection.displayedFraction,
            index.seasonTarget(80, 2).acquisitionProjection.displayedFraction,
            0.0001,
        )
        assertEquals(.4, index.seasonTarget(70, 2).acquisitionProjection.displayedFraction, 0.0001)
        assertEquals(.24, index.seasonTarget(80, 2).acquisitionProjection.displayedFraction, 0.0001)
        assertEquals(.96, (episode.acquisition as SeerrAcquisitionState.Tv).seasons.single().aggregate.progress!!.fraction, 0.0001)
    }

    @Test
    fun canonicalSeasonProgressIncludesJellyfinAndKeepsSeasonsIsolated() {
        val request =
            request(
                requestId = 17,
                tmdbId = 90,
                type = SeerrItemType.TV,
                seasons = setOf(1, 2),
                seasonEpisodeCounts = mapOf(1 to 4, 2 to 4),
                jellyfinReadiness =
                    JellyfinAcquisitionReadiness(
                        episodeItemIds =
                            mapOf(
                                1 to mapOf(1 to UUID.randomUUID(), 2 to UUID.randomUUID()),
                            ),
                    ),
            )

        val index = SeerrAcquisitionTrackerState(requests = listOf(request)).toAcquisitionIndex()

        assertEquals(
            request.toTvSeasonTargets().first { it.seasonNumber == 1 }.acquisitionProjection.displayedFraction,
            index.seasonTarget(90, 1).acquisitionProjection.displayedFraction,
            0.0001,
        )
        assertEquals(.5, index.seasonTarget(90, 1).acquisitionProjection.displayedFraction, 0.0001)
        assertEquals(0.0, index.seasonTarget(90, 2).acquisitionProjection.displayedFraction, 0.0001)
    }

    @Test
    fun authoritativeAndQueueingCollisionsAreBothPreserved() {
        val authoritative = request(13, 60, SeerrItemType.MOVIE)
        val queueing = authoritative.copy(acquisition = SeerrAcquisitionState.Queueing)

        val index =
            SeerrAcquisitionTrackerState(
                requests = listOf(authoritative),
                queueingRequests = listOf(queueing),
            ).toAcquisitionIndex()
        val entries = index.byMediaKey.getValue(MediaKey.Catalog(CatalogMediaType.MOVIE, 60))

        assertEquals(listOf(AcquisitionIndexOrigin.AUTHORITATIVE, AcquisitionIndexOrigin.QUEUEING), entries.map { it.origin })
    }

    @Test
    fun unresolvedAcquisitionIsSurfacedWithoutInventedIdentity() {
        val unresolved = request(14, null, SeerrItemType.MOVIE)

        val index = SeerrAcquisitionTrackerState(requests = listOf(unresolved)).toAcquisitionIndex()

        assertTrue(index.byMediaKey.isEmpty())
        assertEquals(listOf(14), index.unresolved.requestIds())
    }

    @Test
    fun emptyOrClearedTrackerStateProducesEmptyIndex() {
        val index = SeerrAcquisitionTrackerState().toAcquisitionIndex()

        assertTrue(index.byMediaKey.isEmpty())
        assertTrue(index.unresolved.isEmpty())
    }

    private fun request(
        requestId: Int,
        tmdbId: Int?,
        type: SeerrItemType,
        seasons: Set<Int> = emptySet(),
        seasonEpisodeCounts: Map<Int, Int> = emptyMap(),
        jellyfinReadiness: JellyfinAcquisitionReadiness = JellyfinAcquisitionReadiness(),
        is4k: Boolean = false,
        acquisition: SeerrAcquisitionState = SeerrAcquisitionState.Processing,
    ) = SeerrRequestAcquisition(
        request =
            SeerrRequestState(
                requestId = requestId,
                mediaId = null,
                tmdbId = tmdbId,
                requestedById = null,
                requestedByName = null,
                status = RequestStatus.APPROVED,
                mediaType = type,
                is4k = is4k,
                availability = SeerrAvailability.PROCESSING,
                seasonAvailability = emptyMap(),
                seasonUpdatedAt = emptyMap(),
                seasonEpisodeCounts = seasonEpisodeCounts,
                requestedSeasonNumbers = seasons,
                createdAt = null,
                updatedAt = null,
                jellyfinReadiness = jellyfinReadiness,
            ),
        acquisition = acquisition,
    )

    private fun aggregate() = AcquisitionAggregate(AcquisitionStatus.QUEUED, null, emptyList())

    private fun tvAcquisition(seasonNumber: Int, entries: List<AcquisitionEntry>) =
        SeerrAcquisitionState.Tv(
            seasons =
                listOf(
                    SeasonAcquisition(
                        seasonNumber,
                        AcquisitionAggregate(
                            AcquisitionStatus.DOWNLOADING,
                            AcquisitionProgress(
                                totalSize = entries.sumOf { it.totalSize!! },
                                sizeLeft = entries.sumOf { it.sizeLeft!! },
                            ),
                            entries,
                        ),
                    ),
                ),
            unassignedEntries = emptyList(),
        )

    private fun entry(seasonNumber: Int, episodeNumber: Int, title: String, sizeLeft: Double) =
        AcquisitionEntry(
            externalId = episodeNumber,
            downloadId = "download",
            mediaType = "tv",
            title = title,
            status = AcquisitionStatus.DOWNLOADING,
            rawStatus = null,
            totalSize = 100.0,
            sizeLeft = sizeLeft,
            estimatedCompletionTime = null,
            timeLeft = null,
            episode = AcquisitionEpisode(null, seasonNumber, episodeNumber, null, false),
            hasObservedProgress = true,
        )

    private fun AcquisitionIndexSnapshot.seasonTarget(tmdbId: Int, seasonNumber: Int) =
        byMediaKey
            .getValue(MediaKey.Season(MediaKey.Catalog(CatalogMediaType.SERIES, tmdbId), seasonNumber))
            .single()
            .tvSeasonTarget!!

    private fun List<IndexedAcquisition>.requestIds() = map { it.request.request.requestId }
}
