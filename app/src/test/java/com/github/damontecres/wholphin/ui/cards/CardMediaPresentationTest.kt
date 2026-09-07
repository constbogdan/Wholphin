package com.github.damontecres.wholphin.ui.cards

import com.github.damontecres.wholphin.data.model.AcquisitionAggregate
import com.github.damontecres.wholphin.data.model.AcquisitionEntry
import com.github.damontecres.wholphin.data.model.AcquisitionEpisode
import com.github.damontecres.wholphin.data.model.AcquisitionProgress
import com.github.damontecres.wholphin.data.model.AcquisitionStatus
import com.github.damontecres.wholphin.data.model.JellyfinAcquisitionReadiness
import com.github.damontecres.wholphin.data.model.RequestStatus
import com.github.damontecres.wholphin.data.model.SeasonAcquisition
import com.github.damontecres.wholphin.data.model.SeerrAcquisitionState
import com.github.damontecres.wholphin.data.model.SeerrAvailability
import com.github.damontecres.wholphin.data.model.SeerrItemType
import com.github.damontecres.wholphin.data.model.SeerrRequestAcquisition
import com.github.damontecres.wholphin.data.model.SeerrRequestState
import com.github.damontecres.wholphin.data.model.toTvSeasonTargets
import com.github.damontecres.wholphin.services.AcquisitionIndexOrigin
import com.github.damontecres.wholphin.services.IndexedAcquisition
import com.github.damontecres.wholphin.services.MediaProductState
import java.util.UUID
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class CardMediaPresentationTest {
    @Test
    fun visiblePlaybackProgressSuppressesAcquisitionProgress() {
        val result =
            resolveArtworkProgress(
                showPlaybackOverlay = true,
                watchedPercent = 25.0,
                acquisitionProgress = .75f,
            )

        assertEquals(ArtworkProgress(.25f, ArtworkProgressSource.PLAYBACK), result)
    }

    @Test
    fun acquisitionProgressRendersWithoutPlaybackIncludingWhenOverlayIsDisabled() {
        val withoutPlayback = resolveArtworkProgress(true, null, .4f)
        val withoutOverlay = resolveArtworkProgress(false, 25.0, .4f)

        assertEquals(ArtworkProgress(.4f, ArtworkProgressSource.ACQUISITION), withoutPlayback)
        assertEquals(ArtworkProgress(.4f, ArtworkProgressSource.ACQUISITION), withoutOverlay)
    }

    @Test
    fun invalidOrAbsentProgressProducesNoArtworkRail() {
        assertNull(resolveArtworkProgress(true, null, null))
        assertNull(resolveArtworkProgress(true, Double.NaN, Float.NaN))
        assertNull(resolveArtworkProgress(true, 100.0, 1f))
        assertNull(resolveArtworkProgress(true, 0.0, 0f))
    }

    @Test
    fun movieRequestPresentationMatchesExactRequestAndQualityVariant() {
        val normal = movieAcquisition(requestId = 10, is4k = false, fraction = .25)
        val fourK = movieAcquisition(requestId = 10, is4k = true, fraction = .75)
        val queued =
            movieAcquisition(
                requestId = 11,
                is4k = false,
                fraction = .001,
                status = AcquisitionStatus.QUEUED,
            )
        val product = MediaProductState(acquisitions = listOf(normal, fourK, queued))

        assertEquals(.25f, product.movieRequestCardPresentation(10, false)?.acquisitionProgress)
        assertEquals(.75f, product.movieRequestCardPresentation(10, true)?.acquisitionProgress)
        assertEquals(CardAcquisitionState.QUEUED, product.movieRequestCardPresentation(11, false)?.acquisitionState)
        assertNull(product.movieRequestCardPresentation(11, false)?.acquisitionProgress)
    }

    @Test
    fun unrelatedRequestOrQualityAndEmptyEnhancedStateDoNotAttach() {
        val product = MediaProductState(acquisitions = listOf(movieAcquisition(11, false, .5)))

        assertNull(product.movieRequestCardPresentation(12, false))
        assertNull(product.movieRequestCardPresentation(11, true))
        assertNull(MediaProductState().movieRequestCardPresentation(11, false))
    }

    @Test
    fun movieLifecycleUsesCurrentWorkAndCanonicalActivitySemantics() {
        val queueing = indexedMovie(20, false, SeerrAcquisitionState.Queueing)
        val queued = movieAcquisition(21, false, .001, AcquisitionStatus.QUEUED)
        val progress = movieAcquisition(22, false, .4)
        val finishing =
            movieAcquisition(
                requestId = 23,
                is4k = false,
                fraction = 1.0,
                status = AcquisitionStatus.COMPLETED,
                presentInQueue = false,
                successful = true,
            )

        assertEquals(CardAcquisitionState.QUEUEING, queueing.movieCardPresentation()?.acquisitionState)
        assertEquals(CardAcquisitionState.QUEUED, queued.movieCardPresentation()?.acquisitionState)
        assertNull(queued.movieCardPresentation()?.acquisitionProgress)
        assertEquals(.4f, progress.movieCardPresentation()?.acquisitionProgress)
        assertEquals(CardAcquisitionState.FINISHING, finishing.movieCardPresentation()?.acquisitionState)
        assertNull(finishing.movieCardPresentation()?.acquisitionProgress)
    }

    @Test
    fun terminalAndProblemOnlyMoviesHaveNoCardPresentation() {
        val terminal =
            movieAcquisition(
                requestId = 30,
                is4k = false,
                fraction = 1.0,
                status = AcquisitionStatus.COMPLETED,
                presentInQueue = false,
                successful = true,
                readiness = JellyfinAcquisitionReadiness(movieItemId = UUID.randomUUID()),
            )
        val expired =
            movieAcquisition(
                requestId = 31,
                is4k = false,
                fraction = .5,
                presentInQueue = false,
                absentPollCount = 3,
            )
        val problem = movieAcquisition(32, false, .1, AcquisitionStatus.PROBLEM)

        assertNull(terminal.movieCardPresentation())
        assertNull(expired.movieCardPresentation())
        assertNull(problem.movieCardPresentation())
    }

    @Test
    fun catalogMovieProjectionPreservesAgreementAndMakesConflictsCoarse() {
        val queued = movieAcquisition(40, false, 0.0, AcquisitionStatus.QUEUED)
        val sameQueued = movieAcquisition(41, true, 0.0, AcquisitionStatus.QUEUED)
        val progress = movieAcquisition(42, true, .5)
        val differentProgress = movieAcquisition(43, true, .75)

        assertEquals(
            CardAcquisitionState.QUEUED,
            listOf(queued, sameQueued).movieCatalogCardPresentation()?.acquisitionState,
        )
        assertEquals(
            CardAcquisitionState.ACQUIRING,
            listOf(queued, progress).movieCatalogCardPresentation()?.acquisitionState,
        )
        assertEquals(
            CardAcquisitionState.ACQUIRING,
            listOf(progress, differentProgress).movieCatalogCardPresentation()?.acquisitionState,
        )
    }

    @Test
    fun catalogMovieProjectionIgnoresHistoryWhenCurrentWorkExists() {
        val historical =
            movieAcquisition(
                requestId = 50,
                is4k = false,
                fraction = .8,
                presentInQueue = false,
                absentPollCount = 3,
            )
        val current = movieAcquisition(51, true, .25)

        assertEquals(.25f, listOf(historical, current).movieCatalogCardPresentation()?.acquisitionProgress)
        assertNull(listOf(historical).movieCatalogCardPresentation())
    }

    @Test
    fun retainedTvTargetWithoutCurrentWorkHasNoPresentation() {
        val retained = tvAcquisition(presentInQueue = false, absentPollCount = 3)
        val current = tvAcquisition(presentInQueue = true, absentPollCount = 0)

        assertNull(retained.tvSeasonCardPresentation())
        assertEquals(.5f, current.tvSeasonCardPresentation()?.acquisitionProgress)
    }

    private fun movieAcquisition(
        requestId: Int,
        is4k: Boolean,
        fraction: Double,
        status: AcquisitionStatus = AcquisitionStatus.DOWNLOADING,
        presentInQueue: Boolean = true,
        successful: Boolean = false,
        absentPollCount: Int = 0,
        readiness: JellyfinAcquisitionReadiness = JellyfinAcquisitionReadiness(),
    ): IndexedAcquisition {
        val aggregate =
            AcquisitionAggregate(
                status = status,
                progress = AcquisitionProgress(totalSize = 100.0, sizeLeft = 100.0 * (1.0 - fraction)),
                entries =
                    listOf(
                        AcquisitionEntry(
                            externalId = null,
                            downloadId = "download-$requestId-$is4k",
                            mediaType = "movie",
                            title = "Movie",
                            status = status,
                            rawStatus = null,
                            totalSize = 100.0,
                            sizeLeft = 100.0 * (1.0 - fraction),
                            estimatedCompletionTime = null,
                            timeLeft = null,
                            episode = null,
                            hasObservedProgress = true,
                            presentInQueue = presentInQueue,
                            observedSuccessfulTransferCompletion = successful,
                            absentPollCount = absentPollCount,
                        ),
                    ),
            )
        return IndexedAcquisition(
            request =
                SeerrRequestAcquisition(
                    request =
                        SeerrRequestState(
                            requestId = requestId,
                            mediaId = null,
                            tmdbId = 100,
                            requestedById = null,
                            requestedByName = null,
                            status = RequestStatus.APPROVED,
                            mediaType = SeerrItemType.MOVIE,
                            is4k = is4k,
                            availability = SeerrAvailability.PROCESSING,
                            seasonAvailability = emptyMap(),
                            seasonUpdatedAt = emptyMap(),
                            requestedSeasonNumbers = emptySet(),
                            createdAt = null,
                            updatedAt = null,
                            jellyfinReadiness = readiness,
                        ),
                    acquisition = SeerrAcquisitionState.Movie(aggregate),
                ),
            origin = AcquisitionIndexOrigin.AUTHORITATIVE,
        )
    }

    private fun indexedMovie(
        requestId: Int,
        is4k: Boolean,
        acquisition: SeerrAcquisitionState,
    ) = IndexedAcquisition(
        request = requestState(requestId, is4k, SeerrItemType.MOVIE, acquisition),
        origin = AcquisitionIndexOrigin.AUTHORITATIVE,
    )

    private fun tvAcquisition(
        presentInQueue: Boolean,
        absentPollCount: Int,
    ): IndexedAcquisition {
        val entry =
            AcquisitionEntry(
                externalId = null,
                downloadId = "tv-download",
                mediaType = "tv",
                title = "Series.S01E01",
                status = AcquisitionStatus.DOWNLOADING,
                rawStatus = null,
                totalSize = 100.0,
                sizeLeft = 50.0,
                estimatedCompletionTime = null,
                timeLeft = null,
                episode = AcquisitionEpisode(null, 1, 1, null, false),
                presentInQueue = presentInQueue,
                hasObservedProgress = true,
                absentPollCount = absentPollCount,
            )
        val aggregate =
            AcquisitionAggregate(
                AcquisitionStatus.DOWNLOADING,
                AcquisitionProgress(100.0, 50.0),
                listOf(entry),
            )
        val request =
            requestState(
                60,
                false,
                SeerrItemType.TV,
                SeerrAcquisitionState.Tv(listOf(SeasonAcquisition(1, aggregate)), emptyList()),
                requestedSeasons = setOf(1),
            )
        return IndexedAcquisition(
            request = request,
            seasonNumber = 1,
            tvSeasonTarget = request.toTvSeasonTargets().single(),
            origin = AcquisitionIndexOrigin.AUTHORITATIVE,
        )
    }

    private fun requestState(
        requestId: Int,
        is4k: Boolean,
        mediaType: SeerrItemType,
        acquisition: SeerrAcquisitionState,
        requestedSeasons: Set<Int> = emptySet(),
    ) = SeerrRequestAcquisition(
        request =
            SeerrRequestState(
                requestId = requestId,
                mediaId = null,
                tmdbId = 100,
                requestedById = null,
                requestedByName = null,
                status = RequestStatus.APPROVED,
                mediaType = mediaType,
                is4k = is4k,
                availability = SeerrAvailability.PROCESSING,
                seasonAvailability = requestedSeasons.associateWith { SeerrAvailability.PROCESSING },
                seasonUpdatedAt = emptyMap(),
                requestedSeasonNumbers = requestedSeasons,
                seasonEpisodeCounts = requestedSeasons.associateWith { 1 },
                createdAt = null,
                updatedAt = null,
            ),
        acquisition = acquisition,
    )
}
