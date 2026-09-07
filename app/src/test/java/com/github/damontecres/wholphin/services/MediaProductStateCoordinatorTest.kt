package com.github.damontecres.wholphin.services

import com.github.damontecres.wholphin.data.model.CatalogMediaType
import com.github.damontecres.wholphin.data.model.AcquisitionAggregate
import com.github.damontecres.wholphin.data.model.AcquisitionEntry
import com.github.damontecres.wholphin.data.model.AcquisitionEpisode
import com.github.damontecres.wholphin.data.model.AcquisitionProgress
import com.github.damontecres.wholphin.data.model.AcquisitionStatus
import com.github.damontecres.wholphin.data.model.LocalMediaType
import com.github.damontecres.wholphin.data.model.JellyfinAcquisitionReadiness
import com.github.damontecres.wholphin.data.model.MediaKey
import com.github.damontecres.wholphin.data.model.RequestStatus
import com.github.damontecres.wholphin.data.model.SeerrAcquisitionState
import com.github.damontecres.wholphin.data.model.SeerrAvailability
import com.github.damontecres.wholphin.data.model.SeerrItemType
import com.github.damontecres.wholphin.data.model.SeerrRequestAcquisition
import com.github.damontecres.wholphin.data.model.SeerrRequestState
import com.github.damontecres.wholphin.data.model.SeasonAcquisition
import com.github.damontecres.wholphin.data.model.toTvSeasonTargets
import com.github.damontecres.wholphin.ui.detail.series.seasonCardAcquisitionProgress
import com.github.damontecres.wholphin.ui.cards.ArtworkProgress
import com.github.damontecres.wholphin.ui.cards.ArtworkProgressSource
import com.github.damontecres.wholphin.ui.cards.CardAcquisitionState
import com.github.damontecres.wholphin.ui.cards.resolveArtworkProgress
import com.github.damontecres.wholphin.ui.detail.series.seasonCardPresentation
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.launch
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import java.util.UUID

class MediaProductStateCoordinatorTest {
    private val serverId = UUID.fromString("00000000-0000-0000-0000-000000000001")
    private val otherServerId = UUID.fromString("00000000-0000-0000-0000-000000000002")
    private val seriesId = UUID.fromString("00000000-0000-0000-0000-000000000003")
    private val localSeries = MediaKey.Local(serverId, seriesId, LocalMediaType.SERIES)
    private val catalogSeries = MediaKey.Catalog(CatalogMediaType.SERIES, 100)

    @Test
    fun localIntegrityAndCatalogAcquisitionJoinOnlyThroughExactSeasonAlias() = runTest {
        val localSeason1 = MediaKey.Season(localSeries, 1)
        val localSeason2 = MediaKey.Season(localSeries, 2)
        val catalogSeason1 = MediaKey.Season(catalogSeries, 1)
        val catalogSeason2 = MediaKey.Season(catalogSeries, 2)
        val acquisition = acquisition(1, seasonNumber = 1)
        val integrity1 = integrity(IntegrityAssessment.INCOMPLETE, 2)
        val integrity2 = integrity(IntegrityAssessment.COMPLETE, 0)
        val coordinator =
            coordinator(
                acquisitions = mapOf(catalogSeason1 to listOf(acquisition)),
                integrity = mapOf(localSeason1 to integrity1, localSeason2 to integrity2),
            )

        val result =
            coordinator.observe(
                keys = setOf(localSeason1, localSeason2),
                seasonAliases =
                    setOf(
                        SeasonMediaAlias(localSeason1, catalogSeason1),
                        SeasonMediaAlias(localSeason2, catalogSeason2),
                    ),
            ).first()

        assertEquals(listOf(1), result.getValue(localSeason1).acquisitions.requestIds())
        assertEquals(integrity1, result.getValue(localSeason1).integrity)
        assertTrue(result.getValue(localSeason2).acquisitions.isEmpty())
        assertEquals(integrity2, result.getValue(localSeason2).integrity)
    }

    @Test
    fun unresolvedAndConflictingAliasesDoNotGuess() = runTest {
        val localSeason = MediaKey.Season(localSeries, 1)
        val catalogSeason = MediaKey.Season(catalogSeries, 1)
        val conflictingCatalog =
            MediaKey.Season(MediaKey.Catalog(CatalogMediaType.SERIES, 101), 1)
        val localIntegrity = integrity(IntegrityAssessment.INCOMPLETE, 1)
        val coordinator =
            coordinator(
                acquisitions = mapOf(catalogSeason to listOf(acquisition(2, 1))),
                integrity = mapOf(localSeason to localIntegrity),
            )

        val unresolved = coordinator.observe(setOf(localSeason)).first().getValue(localSeason)
        val ambiguous =
            coordinator.observe(
                setOf(localSeason),
                setOf(
                    SeasonMediaAlias(localSeason, catalogSeason),
                    SeasonMediaAlias(localSeason, conflictingCatalog),
                ),
            ).first().getValue(localSeason)

        assertTrue(unresolved.acquisitions.isEmpty())
        assertEquals(localIntegrity, unresolved.integrity)
        assertTrue(ambiguous.acquisitions.isEmpty())
    }

    @Test
    fun mediaTypesAndJellyfinServersRemainDistinct() = runTest {
        val localSeason = MediaKey.Season(localSeries, 1)
        val otherLocalSeason =
            MediaKey.Season(MediaKey.Local(otherServerId, seriesId, LocalMediaType.SERIES), 1)
        val movie = MediaKey.Catalog(CatalogMediaType.MOVIE, 100)
        val catalogSeason = MediaKey.Season(catalogSeries, 1)
        val coordinator =
            coordinator(
                acquisitions =
                    mapOf(
                        movie to listOf(acquisition(3, null, SeerrItemType.MOVIE)),
                        catalogSeason to listOf(acquisition(4, 1)),
                    ),
                integrity = mapOf(localSeason to integrity(IntegrityAssessment.INCOMPLETE, 1)),
            )

        val result = coordinator.observe(setOf(movie, otherLocalSeason)).first()

        assertEquals(listOf(3), result.getValue(movie).acquisitions.requestIds())
        assertNull(result.getValue(movie).integrity)
        assertTrue(result.getValue(otherLocalSeason).acquisitions.isEmpty())
        assertNull(result.getValue(otherLocalSeason).integrity)
    }

    @Test
    fun acquisitionIntegrityBothAndNeitherRemainIndependentIncludingSeasonZero() = runTest {
        val season0 = MediaKey.Season(localSeries, 0)
        val season1 = MediaKey.Season(localSeries, 1)
        val season2 = MediaKey.Season(localSeries, 2)
        val season3 = MediaKey.Season(localSeries, 3)
        val catalog0 = MediaKey.Season(catalogSeries, 0)
        val catalog1 = MediaKey.Season(catalogSeries, 1)
        val catalog3 = MediaKey.Season(catalogSeries, 3)
        val coordinator =
            coordinator(
                acquisitions =
                    mapOf(
                        catalog0 to listOf(acquisition(5, 0)),
                        catalog1 to listOf(acquisition(6, 1)),
                        catalog3 to listOf(acquisition(7, 3)),
                    ),
                integrity =
                    mapOf(
                        season0 to integrity(IntegrityAssessment.COMPLETE, 0),
                        season1 to integrity(IntegrityAssessment.INCOMPLETE, 1),
                        season2 to integrity(IntegrityAssessment.COMPLETE, 0),
                    ),
            )
        val aliases =
            setOf(
                SeasonMediaAlias(season0, catalog0),
                SeasonMediaAlias(season1, catalog1),
                SeasonMediaAlias(season3, catalog3),
            )

        val result = coordinator.observe(setOf(season0, season1, season2, season3), aliases).first()

        assertEquals(listOf(5), result.getValue(season0).acquisitions.requestIds())
        assertEquals(IntegrityAssessment.COMPLETE, result.getValue(season0).integrity?.assessment)
        assertEquals(listOf(6), result.getValue(season1).acquisitions.requestIds())
        assertEquals(IntegrityAssessment.INCOMPLETE, result.getValue(season1).integrity?.assessment)
        assertTrue(result.getValue(season2).acquisitions.isEmpty())
        assertEquals(IntegrityAssessment.COMPLETE, result.getValue(season2).integrity?.assessment)
        assertEquals(listOf(7), result.getValue(season3).acquisitions.requestIds())
        assertNull(result.getValue(season3).integrity)
    }

    @Test
    @OptIn(ExperimentalCoroutinesApi::class)
    fun multipleAcquisitionsAndSourceUpdatesPropagateWithoutStaleValues() = runTest {
        val localSeason = MediaKey.Season(localSeries, 1)
        val catalogSeason = MediaKey.Season(catalogSeries, 1)
        val acquisitionFlow =
            MutableStateFlow(
                AcquisitionIndexSnapshot(
                    byMediaKey = mapOf(catalogSeason to listOf(acquisition(8, 1), acquisition(9, 1))),
                ),
            )
        val integrityFlow =
            MutableStateFlow<Map<MediaKey, IntegrityState>>(
                mapOf(localSeason to integrity(IntegrityAssessment.INCOMPLETE, 1)),
            )
        val coordinator = coordinator(acquisitionFlow, integrityFlow)
        val states = mutableListOf<Map<MediaKey, MediaProductState>>()
        val collection =
            backgroundScope.launch(kotlinx.coroutines.test.UnconfinedTestDispatcher(testScheduler)) {
                coordinator.observe(
                    setOf(localSeason),
                    setOf(SeasonMediaAlias(localSeason, catalogSeason)),
                ).collect { states.add(it) }
            }

        assertEquals(listOf(8, 9), states.last().getValue(localSeason).acquisitions.requestIds())
        acquisitionFlow.value = AcquisitionIndexSnapshot()
        assertTrue(states.last().getValue(localSeason).acquisitions.isEmpty())
        integrityFlow.value = emptyMap()
        assertNull(states.last().getValue(localSeason).integrity)
        collection.cancel()
    }

    @Test
    fun determinateActiveSeasonAcquisitionProducesCardProgress() {
        val incomplete = integrity(IntegrityAssessment.INCOMPLETE, 1)
        val product =
            MediaProductState(
                acquisitions = listOf(acquisition(10, 1, state = activeTvState(1))),
                integrity = incomplete,
            )

        assertEquals(.5f, product.seasonCardAcquisitionProgress())
        assertEquals(.5f, product.seasonCardPresentation()?.acquisitionProgress)
        assertNull(product.seasonCardPresentation()?.acquisitionState)
        assertEquals(incomplete, product.integrity)
    }

    @Test
    fun queueingAndAuthoritativeQueuedMapToDistinctCardStates() {
        val queueing =
            MediaProductState(
                acquisitions = listOf(acquisition(16, 1, state = SeerrAcquisitionState.Queueing)),
            )
        val queued =
            MediaProductState(
                acquisitions =
                    listOf(
                        acquisition(
                            17,
                            1,
                            state = activeTvState(1, sizeLeft = 100.0),
                        ),
                    ),
            )

        assertEquals(CardAcquisitionState.QUEUEING, queueing.seasonCardPresentation()?.acquisitionState)
        assertNull(queueing.seasonCardPresentation()?.acquisitionProgress)
        assertEquals(CardAcquisitionState.QUEUED, queued.seasonCardPresentation()?.acquisitionState)
        assertNull(queued.seasonCardPresentation()?.acquisitionProgress)
    }

    @Test
    fun seasonCardUsesCanonicalEpisodeNormalizedProgressFromSharedStateInsteadOfRawAggregate() = runTest {
        val indexed = acquisition(15, 1, state = activeTvState(1, sizeLeft = 4.0), expectedEpisodeCount = 4)
        val raw =
            (indexed.request.acquisition as SeerrAcquisitionState.Tv)
                .seasons.single().aggregate.progress!!.fraction
        val product =
            coordinator(
                acquisitions =
                    mapOf(
                        MediaKey.Season(catalogSeries, 1) to listOf(indexed),
                    ),
            ).observe(
                keys = setOf(MediaKey.Season(localSeries, 1)),
                seasonAliases =
                    setOf(
                        SeasonMediaAlias(
                            MediaKey.Season(localSeries, 1),
                            MediaKey.Season(catalogSeries, 1),
                        ),
                    ),
            ).first().getValue(MediaKey.Season(localSeries, 1))

        assertEquals(.96, raw, 0.0001)
        val cardProgress = product.seasonCardAcquisitionProgress()
        assertEquals(.24f, cardProgress)
        assertEquals(
            ArtworkProgress(.24f, ArtworkProgressSource.ACQUISITION),
            resolveArtworkProgress(false, null, cardProgress),
        )
    }

    @Test
    fun absentDisabledOrIndeterminateAcquisitionProducesNoCardProgress() {
        val indeterminate = MediaProductState(acquisitions = listOf(acquisition(11, 1)))

        assertNull(MediaProductState().seasonCardAcquisitionProgress())
        assertNull(MediaProductState().seasonCardPresentation())
        assertNull(indeterminate.seasonCardAcquisitionProgress())
        assertNull(indeterminate.seasonCardPresentation())
    }

    @Test
    fun finishingOrMultipleAcquisitionsProduceNoCardProgress() {
        val finishing =
            MediaProductState(acquisitions = listOf(acquisition(12, 1, state = finishingTvState(1))))
        val multiple =
            MediaProductState(
                acquisitions =
                    listOf(
                        acquisition(13, 1, state = activeTvState(1)),
                        acquisition(14, 1, state = activeTvState(1)),
                    ),
            )

        assertNull(finishing.seasonCardAcquisitionProgress())
        assertEquals(CardAcquisitionState.FINISHING, finishing.seasonCardPresentation()?.acquisitionState)
        assertNull(multiple.seasonCardAcquisitionProgress())
        assertNull(multiple.seasonCardPresentation())
    }

    @Test
    fun jellyfinReadyTerminalSeasonProducesNoAcquisitionPresentation() {
        val indexed = acquisition(18, 1)
        val readyRequest =
            indexed.request.copy(
                request =
                    indexed.request.request.copy(
                        jellyfinReadiness =
                            JellyfinAcquisitionReadiness(
                                episodeItemIds = mapOf(1 to mapOf(1 to UUID.randomUUID())),
                            ),
                    ),
            )
        val ready =
            indexed.copy(
                request = readyRequest,
                tvSeasonTarget = readyRequest.toTvSeasonTargets().single(),
            )

        assertNull(MediaProductState(acquisitions = listOf(ready)).seasonCardPresentation())
    }

    private fun coordinator(
        acquisitions: Map<MediaKey, List<IndexedAcquisition>> = emptyMap(),
        integrity: Map<MediaKey, IntegrityState> = emptyMap(),
    ) = coordinator(MutableStateFlow(AcquisitionIndexSnapshot(byMediaKey = acquisitions)), MutableStateFlow(integrity))

    private fun coordinator(
        acquisitions: MutableStateFlow<AcquisitionIndexSnapshot>,
        integrity: MutableStateFlow<Map<MediaKey, IntegrityState>>,
    ) = MediaProductStateCoordinator(
        acquisitionSnapshots = acquisitions,
        observeIntegrity = { keys -> integrity.map { values -> values.filterKeys(keys::contains) } },
    )

    private fun acquisition(
        requestId: Int,
        seasonNumber: Int?,
        mediaType: SeerrItemType = SeerrItemType.TV,
        state: SeerrAcquisitionState = SeerrAcquisitionState.Processing,
        expectedEpisodeCount: Int = 1,
    ): IndexedAcquisition {
        val request =
            SeerrRequestAcquisition(
                request =
                    SeerrRequestState(
                        requestId = requestId,
                        mediaId = null,
                        tmdbId = 100,
                        requestedById = null,
                        requestedByName = null,
                        status = RequestStatus.APPROVED,
                        mediaType = mediaType,
                        is4k = false,
                        availability = SeerrAvailability.PROCESSING,
                        seasonAvailability = emptyMap(),
                        seasonUpdatedAt = emptyMap(),
                        seasonEpisodeCounts = seasonNumber?.let { mapOf(it to expectedEpisodeCount) }.orEmpty(),
                        requestedSeasonNumbers = seasonNumber?.let(::setOf).orEmpty(),
                        createdAt = null,
                        updatedAt = null,
                    ),
                acquisition = state,
            )
        return IndexedAcquisition(
            request = request,
            seasonNumber = seasonNumber,
            tvSeasonTarget = request.toTvSeasonTargets().singleOrNull { it.seasonNumber == seasonNumber },
            origin = AcquisitionIndexOrigin.AUTHORITATIVE,
        )
    }

    private fun activeTvState(seasonNumber: Int, sizeLeft: Double = 50.0) =
        SeerrAcquisitionState.Tv(
            seasons =
                listOf(
                    SeasonAcquisition(
                        seasonNumber,
                        AcquisitionAggregate(
                            status = AcquisitionStatus.DOWNLOADING,
                            progress = AcquisitionProgress(totalSize = 100.0, sizeLeft = sizeLeft),
                            entries =
                                listOf(
                                    entry(
                                        AcquisitionStatus.DOWNLOADING,
                                        sizeLeft = sizeLeft,
                                        seasonNumber = seasonNumber,
                                    ),
                                ),
                        ),
                    ),
                ),
            unassignedEntries = emptyList(),
        )

    private fun finishingTvState(seasonNumber: Int) =
        SeerrAcquisitionState.Tv(
            seasons =
                listOf(
                    SeasonAcquisition(
                        seasonNumber,
                        AcquisitionAggregate(
                            status = AcquisitionStatus.COMPLETED,
                            progress = AcquisitionProgress(totalSize = 100.0, sizeLeft = 0.0),
                            entries =
                                listOf(
                                    entry(
                                        AcquisitionStatus.COMPLETED,
                                        sizeLeft = 0.0,
                                        seasonNumber = seasonNumber,
                                    ),
                                ),
                        ),
                    ),
                ),
            unassignedEntries = emptyList(),
        )

    private fun entry(status: AcquisitionStatus, sizeLeft: Double, seasonNumber: Int) =
        AcquisitionEntry(
            externalId = null,
            downloadId = "download",
            mediaType = "tv",
            title = "Show.S%02dE01".format(seasonNumber),
            status = status,
            rawStatus = null,
            totalSize = 100.0,
            sizeLeft = sizeLeft,
            estimatedCompletionTime = null,
            timeLeft = null,
            episode = AcquisitionEpisode(null, seasonNumber, 1, null, false),
            presentInQueue = true,
            hasObservedProgress = true,
            observedSuccessfulTransferCompletion = status == AcquisitionStatus.COMPLETED,
        )

    private fun integrity(assessment: IntegrityAssessment, missingCount: Int) =
        IntegrityState(
            assessment = assessment,
            missingEpisodeCount = missingCount,
            missingEpisodeNumbers = if (missingCount == 0) emptySet() else (1..missingCount).toSet(),
            expectedEpisodeNumbers = null,
            playableEpisodeNumbers = null,
            physicallyMissingEpisodeNumbers = null,
            activelyCoveredEpisodeNumbers = null,
        )

    private fun List<IndexedAcquisition>.requestIds() = map { it.request.request.requestId }
}
