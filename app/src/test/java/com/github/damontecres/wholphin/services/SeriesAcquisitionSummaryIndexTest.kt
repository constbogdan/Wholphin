package com.github.damontecres.wholphin.services

import com.github.damontecres.wholphin.data.model.AcquisitionAggregate
import com.github.damontecres.wholphin.data.model.AcquisitionEntry
import com.github.damontecres.wholphin.data.model.AcquisitionEpisode
import com.github.damontecres.wholphin.data.model.AcquisitionProgress
import com.github.damontecres.wholphin.data.model.AcquisitionStatus
import com.github.damontecres.wholphin.data.model.BaseItem
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
import com.github.damontecres.wholphin.data.model.toMediaKey
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import org.jellyfin.sdk.model.api.BaseItemDto
import org.jellyfin.sdk.model.api.BaseItemKind
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.util.UUID

class SeriesAcquisitionSummaryIndexTest {
    @Test
    fun queueingQueuedInProgressAndFinishingAreActive() {
        val queueing = request(1, 101, acquisition = SeerrAcquisitionState.Queueing)
        val queued = request(2, 102, acquisition = tv(1, entry(AcquisitionStatus.QUEUED)))
        val inProgress = request(3, 103, acquisition = tv(1, entry(AcquisitionStatus.DOWNLOADING, 50.0, true)))
        val finishing =
            request(
                4,
                104,
                acquisition =
                    tv(
                        1,
                        entry(
                            status = AcquisitionStatus.COMPLETED,
                            sizeLeft = 0.0,
                            observedProgress = true,
                            presentInQueue = false,
                            completed = true,
                        ),
                    ),
            )

        val summaries = snapshot(queueing, queued, inProgress, finishing).toSeriesAcquisitionSummaries()

        assertEquals(setOf(series(101), series(102), series(103), series(104)), summaries.keys)
        assertTrue(summaries.values.all { it == SeriesAcquisitionSummary.ACTIVE })
    }

    @Test
    fun staleProcessingWholeSeriesAvailabilityAndProblemOnlyAreNone() {
        val processing = request(5, 105)
        val availabilityOnly = request(6, 106, availability = SeerrAvailability.AVAILABLE)
        val problem = request(7, 107, acquisition = tv(1, entry(AcquisitionStatus.PROBLEM)))

        val summaries = snapshot(processing, availabilityOnly, problem).toSeriesAcquisitionSummaries()

        assertTrue(summaries.isEmpty())
    }

    @Test
    fun boundedQueueAbsenceRemainsActiveThenClearsWithoutNewTimeoutPolicy() {
        val withinGrace =
            request(
                17,
                117,
                acquisition =
                    tv(
                        1,
                        entry(
                            status = AcquisitionStatus.DOWNLOADING,
                            sizeLeft = 50.0,
                            observedProgress = true,
                            presentInQueue = false,
                            absentPollCount = 2,
                        ),
                    ),
            )
        val beyondGrace =
            request(
                18,
                118,
                acquisition =
                    tv(
                        1,
                        entry(
                            status = AcquisitionStatus.DOWNLOADING,
                            sizeLeft = 50.0,
                            observedProgress = true,
                            presentInQueue = false,
                            absentPollCount = 3,
                        ),
                    ),
            )

        val summaries = snapshot(withinGrace, beyondGrace).toSeriesAcquisitionSummaries()

        assertEquals(SeriesAcquisitionSummary.ACTIVE, summaries[series(117)])
        assertFalse(series(118) in summaries)
    }

    @Test
    fun historicalAvailableCompletionIsNone() {
        val readyEpisode = UUID.randomUUID()
        val completed =
            request(
                8,
                108,
                availability = SeerrAvailability.AVAILABLE,
                readiness = JellyfinAcquisitionReadiness(episodeItemIds = mapOf(1 to mapOf(1 to readyEpisode))),
                acquisition =
                    tv(
                        1,
                        entry(
                            status = AcquisitionStatus.COMPLETED,
                            sizeLeft = 0.0,
                            observedProgress = true,
                            presentInQueue = false,
                            completed = true,
                        ),
                    ),
            )

        assertTrue(snapshot(completed).toSeriesAcquisitionSummaries().isEmpty())
    }

    @Test
    fun liveQualityUpgradeOnPlayableSeasonIsActive() {
        val upgrade =
            request(
                9,
                109,
                readiness = JellyfinAcquisitionReadiness(episodeItemIds = mapOf(1 to mapOf(1 to UUID.randomUUID()))),
                acquisition = tv(1, entry(AcquisitionStatus.DOWNLOADING, 40.0, true)),
            )

        assertEquals(
            SeriesAcquisitionSummary.ACTIVE,
            snapshot(upgrade).toSeriesAcquisitionSummaries()[series(109)],
        )
    }

    @Test
    fun multipleSeasonsAndQualityVariantsCollapseWithoutChoosingWinner() {
        val seasonOne = request(10, 110, acquisition = tv(1, entry(AcquisitionStatus.QUEUED)))
        val seasonTwo4k =
            request(
                11,
                110,
                season = 2,
                is4k = true,
                acquisition = tv(2, entry(AcquisitionStatus.DOWNLOADING, season = 2)),
            )

        val summaries = snapshot(seasonOne, seasonTwo4k).toSeriesAcquisitionSummaries()

        assertEquals(mapOf(series(110) to SeriesAcquisitionSummary.ACTIVE), summaries)
    }

    @Test
    fun authoritativeSeasonWithoutRequestSeasonMetadataIsActive() {
        val acquisition =
            request(
                19,
                119,
                season = 3,
                acquisition = tv(3, entry(AcquisitionStatus.DOWNLOADING, 50.0, true, season = 3)),
            ).let { request ->
                request.copy(request = request.request.copy(requestedSeasonNumbers = emptySet()))
            }

        assertEquals(
            SeriesAcquisitionSummary.ACTIVE,
            snapshot(acquisition).toSeriesAcquisitionSummaries()[series(119)],
        )
    }

    @Test
    fun unassignedTvEvidenceDoesNotInventSeriesSummary() {
        val acquisition =
            request(
                20,
                120,
                season = 3,
                acquisition =
                    SeerrAcquisitionState.Tv(
                        seasons = emptyList(),
                        unassignedEntries =
                            listOf(entry(AcquisitionStatus.DOWNLOADING, 50.0, true).copy(episode = null)),
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

        assertTrue(snapshot(acquisition).toSeriesAcquisitionSummaries().isEmpty())
    }

    @Test
    fun separateSeriesRemainIsolatedAndUnresolvedIdentityIsOmitted() {
        val first = request(12, 111, acquisition = SeerrAcquisitionState.Queueing)
        val second = request(13, 112, acquisition = tv(1, entry(AcquisitionStatus.QUEUED)))
        val unresolved = request(14, null, acquisition = SeerrAcquisitionState.Queueing)

        val index = tracker(first, second, unresolved).toAcquisitionIndex()
        val summaries = index.toSeriesAcquisitionSummaries()

        assertEquals(setOf(series(111), series(112)), summaries.keys)
        assertEquals(1, index.unresolved.size)
    }

    @Test
    @OptIn(ExperimentalCoroutinesApi::class)
    fun emptySourceAndFilteredObservationExposeNoSummary() = runTest {
        val snapshots = MutableStateFlow(AcquisitionIndexSnapshot())
        val index = SeriesAcquisitionSummaryIndex(snapshots, backgroundScope)
        runCurrent()

        assertTrue(index.state.value.isEmpty())
        snapshots.value = snapshot(request(15, 113, acquisition = SeerrAcquisitionState.Queueing))
        runCurrent()

        assertEquals(
            mapOf(series(113) to SeriesAcquisitionSummary.ACTIVE),
            index.observe(setOf(series(113), series(999))).first(),
        )
        assertTrue(index.observe(setOf(MediaKey.Catalog(CatalogMediaType.MOVIE, 113))).first().isEmpty())
    }

    @Test
    fun placeholderAndJellyfinLocalIdentityUseSameCatalogSummary() {
        val summary = snapshot(request(16, 114, acquisition = SeerrAcquisitionState.Queueing)).toSeriesAcquisitionSummaries()
        val placeholder =
            DiscoverItem(
                id = 114,
                type = SeerrItemType.TV,
                title = "Series",
                subtitle = null,
                overview = null,
                availability = SeerrAvailability.UNKNOWN,
                releaseDate = null,
                posterUrl = null,
                backDropUrl = null,
                logoUrl = null,
                jellyfinItemId = null,
            )
        val local =
            BaseItem(
                BaseItemDto(
                    id = UUID.randomUUID(),
                    type = BaseItemKind.SERIES,
                    name = "Series",
                    providerIds = mapOf("Tmdb" to "114"),
                ),
            )
        val serverId = UUID.randomUUID()

        assertEquals(series(114), placeholder.toMediaKey())
        assertEquals(series(114), local.toMediaKey(serverId))
        assertEquals(SeriesAcquisitionSummary.ACTIVE, summary[placeholder.toMediaKey()])
        assertEquals(SeriesAcquisitionSummary.ACTIVE, summary[local.toMediaKey(serverId)])
    }

    private fun snapshot(vararg requests: SeerrRequestAcquisition): AcquisitionIndexSnapshot =
        tracker(*requests).toAcquisitionIndex()

    private fun tracker(vararg requests: SeerrRequestAcquisition) =
        SeerrAcquisitionTrackerState(
            requests = requests.filterNot { it.acquisition == SeerrAcquisitionState.Queueing },
            queueingRequests = requests.filter { it.acquisition == SeerrAcquisitionState.Queueing },
        )

    private fun request(
        requestId: Int,
        tmdbId: Int?,
        season: Int = 1,
        is4k: Boolean = false,
        availability: SeerrAvailability = SeerrAvailability.PROCESSING,
        readiness: JellyfinAcquisitionReadiness = JellyfinAcquisitionReadiness(),
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
                mediaType = SeerrItemType.TV,
                is4k = is4k,
                availability = availability,
                seasonAvailability = mapOf(season to availability),
                seasonUpdatedAt = emptyMap(),
                seasonEpisodeCounts = mapOf(season to 1),
                requestedSeasonNumbers = setOf(season),
                createdAt = null,
                updatedAt = null,
                jellyfinReadiness = readiness,
            ),
        acquisition = acquisition,
    )

    private fun tv(season: Int, vararg entries: AcquisitionEntry) =
        SeerrAcquisitionState.Tv(
            seasons =
                listOf(
                    SeasonAcquisition(
                        season,
                        AcquisitionAggregate(
                            status = entries.first().status,
                            progress =
                                entries.first().sizeLeft?.let {
                                    AcquisitionProgress(totalSize = 100.0, sizeLeft = it)
                                },
                            entries = entries.toList(),
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
        season: Int = 1,
        absentPollCount: Int = 0,
    ) = AcquisitionEntry(
        externalId = 1,
        downloadId = "download",
        mediaType = "tv",
        title = "Series.S01E01",
        status = status,
        rawStatus = null,
        totalSize = sizeLeft?.let { 100.0 },
        sizeLeft = sizeLeft,
        estimatedCompletionTime = null,
        timeLeft = null,
        episode = AcquisitionEpisode(null, season, 1, null, false),
        presentInQueue = presentInQueue,
        hasObservedProgress = observedProgress,
        observedSuccessfulTransferCompletion = completed,
        absentPollCount = absentPollCount,
    )

    private fun series(tmdbId: Int) = MediaKey.Catalog(CatalogMediaType.SERIES, tmdbId)
}
