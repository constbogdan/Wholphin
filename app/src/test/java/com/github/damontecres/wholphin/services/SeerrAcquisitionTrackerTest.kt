package com.github.damontecres.wholphin.services

import com.github.damontecres.wholphin.api.seerr.model.DownloadStatus
import com.github.damontecres.wholphin.api.seerr.model.DownloadStatusEpisode
import com.github.damontecres.wholphin.api.seerr.model.MediaInfo
import com.github.damontecres.wholphin.api.seerr.model.MediaRequest
import com.github.damontecres.wholphin.api.seerr.model.Season
import com.github.damontecres.wholphin.data.model.SeerrAcquisitionState
import com.github.damontecres.wholphin.data.model.SeerrAvailability
import com.github.damontecres.wholphin.data.model.SeerrRequestAcquisition
import com.github.damontecres.wholphin.data.model.JellyfinAcquisitionReadiness
import com.github.damontecres.wholphin.data.model.authoritativelyRepresentedSeasons
import com.github.damontecres.wholphin.data.model.toSeerrRequestAcquisition
import com.github.damontecres.wholphin.ui.downloads.destination
import com.github.damontecres.wholphin.ui.downloads.toDownloadSections
import com.github.damontecres.wholphin.ui.nav.Destination
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.advanceTimeBy
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.time.Instant
import java.util.UUID

@OptIn(ExperimentalCoroutinesApi::class)
class SeerrAcquisitionTrackerTest {
    @Test
    fun disabledTrackerRejectsForegroundAndQueueingSideEffects() =
        runTest {
            val tracker =
                tracker(
                    sessions = MutableStateFlow(SeerrAcquisitionSession(1, 1)),
                    acquisitionEnabled = { false },
                ) { emptyList() }

            tracker.startForeground()
            tracker.registerQueueing(movieRequest(899, size = null, sizeLeft = null))
            tracker.refreshNow()
            runCurrent()

            assertFalse(tracker.state.value.isRunning)
            assertTrue(tracker.state.value.queueingRequests.isEmpty())
            assertTrue(tracker.state.value.requests.isEmpty())
        }

    @Test
    fun deactivationClearsTransientSessionAndQueueingState() =
        runTest {
            val tracker = tracker(MutableStateFlow(SeerrAcquisitionSession(1, 1))) { emptyList() }

            tracker.startForeground()
            runCurrent()
            tracker.registerQueueing(movieRequest(900, size = null, sizeLeft = null))
            assertTrue(tracker.state.value.queueingRequests.isNotEmpty())

            tracker.deactivate()

            assertFalse(tracker.state.value.isRunning)
            assertEquals(null, tracker.state.value.session)
            assertTrue(tracker.state.value.requests.isEmpty())
            assertTrue(tracker.state.value.queueingRequests.isEmpty())
        }

    @Test
    fun requestPresenceAloneDoesNotRemoveQueueingWithoutAuthoritativeRow() =
        runTest {
            var current = emptyList<SeerrRequestAcquisition>()
            val tracker = tracker(MutableStateFlow(SeerrAcquisitionSession(1, 1))) { current }
            val submitted = movieRequest(901, size = null, sizeLeft = null)

            tracker.startForeground()
            runCurrent()
            tracker.registerQueueing(submitted)
            assertEquals(SeerrAcquisitionState.Queueing, tracker.state.value.queueingRequests.single().acquisition)

            current = listOf(submitted)
            tracker.refreshNow()
            runCurrent()

            assertEquals(SeerrAcquisitionState.Queueing, tracker.state.value.queueingRequests.single().acquisition)
            assertEquals(SeerrAcquisitionState.Processing, tracker.state.value.requests.single().acquisition)
            tracker.stopForeground()
        }

    @Test
    fun queueingReconcilesToAuthoritativeQueuedWhenTimestampIsEligible() =
        runTest {
            val submitted = movieRequest(905, size = null, sizeLeft = null)
            val queued = submitted.copy(request = submitted.request.copy(updatedAt = Instant.EPOCH.toString()))
            var current = emptyList<SeerrRequestAcquisition>()
            val tracker = tracker(MutableStateFlow(SeerrAcquisitionSession(1, 1))) { current }

            tracker.startForeground()
            runCurrent()
            tracker.registerQueueing(submitted)
            current = listOf(queued)
            tracker.refreshNow()
            runCurrent()

            assertTrue(tracker.state.value.queueingRequests.isEmpty())
            tracker.stopForeground()
        }

    @Test
    fun futureAuthoritativeTimestampDoesNotCreateQueueingVisibilityGap() =
        runTest {
            val submitted = movieRequest(906, size = null, sizeLeft = null)
            val future = submitted.copy(request = submitted.request.copy(updatedAt = Instant.ofEpochSecond(3600).toString()))
            var current = emptyList<SeerrRequestAcquisition>()
            val tracker = tracker(MutableStateFlow(SeerrAcquisitionSession(1, 1))) { current }

            tracker.startForeground()
            runCurrent()
            tracker.registerQueueing(submitted)
            current = listOf(future)
            tracker.refreshNow()
            runCurrent()

            assertEquals(1, tracker.state.value.queueingRequests.size)
            tracker.stopForeground()
        }

    @Test
    fun multiSeasonQueueingReconcilesOnlyRepresentedSeason() =
        runTest {
            val submitted =
                tvRequest(907, emptyList()).copy(
                    request = tvRequest(907, emptyList()).request.copy(requestedSeasonNumbers = setOf(1, 2)),
                )
            val authoritative =
                tvRequest(907, listOf(episode("season-one", 1, 100.0, 50.0))).let {
                    it.copy(request = it.request.copy(requestedSeasonNumbers = setOf(1, 2)))
                }
            var current = emptyList<SeerrRequestAcquisition>()
            val tracker = tracker(MutableStateFlow(SeerrAcquisitionSession(1, 1))) { current }

            assertEquals(setOf(1), authoritative.authoritativelyRepresentedSeasons(testScheduler.currentTime))
            tracker.startForeground()
            runCurrent()
            tracker.registerQueueing(submitted)
            current = listOf(authoritative)
            tracker.refreshNow()
            runCurrent()

            assertEquals(setOf(2), tracker.state.value.queueingRequests.single().request.requestedSeasonNumbers)
            tracker.stopForeground()
        }

    @Test
    fun queueingCanReconcileDirectlyToActiveAcquisition() =
        runTest {
            val submitted = movieRequest(902, size = null, sizeLeft = null)
            val active = movieRequest(902, size = 100.0, sizeLeft = 40.0)
            var current = emptyList<SeerrRequestAcquisition>()
            val tracker = tracker(MutableStateFlow(SeerrAcquisitionSession(1, 1))) { current }

            tracker.startForeground()
            runCurrent()
            tracker.registerQueueing(submitted)
            current = listOf(active)
            tracker.refreshNow()
            runCurrent()

            assertTrue(tracker.state.value.queueingRequests.isEmpty())
            assertEquals(0.6, tracker.state.value.requests.single().movieProgress(), 0.0)
            tracker.stopForeground()
        }

    @Test
    fun queueingCanReconcileDirectlyToJellyfinAvailable() =
        runTest {
            val submitted = movieRequest(908, size = null, sizeLeft = null)
            val ready =
                submitted.copy(
                    request =
                        submitted.request.copy(
                            jellyfinReadiness = JellyfinAcquisitionReadiness(movieItemId = UUID.randomUUID()),
                        ),
                )
            var current = emptyList<SeerrRequestAcquisition>()
            val tracker = tracker(MutableStateFlow(SeerrAcquisitionSession(1, 1))) { current }

            tracker.startForeground()
            runCurrent()
            tracker.registerQueueing(submitted)
            current = listOf(ready)
            tracker.refreshNow()
            runCurrent()

            assertTrue(tracker.state.value.queueingRequests.isEmpty())
            assertTrue(tracker.state.value.requests.single().request.jellyfinReadiness.movieReady)
            tracker.stopForeground()
        }

    @Test
    fun tvPendingRequestUpdateQueuesEverySubmittedSeason() =
        runTest {
            val existing = tvRequest(903, emptyList())
            val tracker = tracker(MutableStateFlow(SeerrAcquisitionSession(1, 1))) { listOf(existing) }
            tracker.startForeground()
            runCurrent()
            val updated = existing.copy(request = existing.request.copy(requestedSeasonNumbers = setOf(1, 2)))

            tracker.registerQueueing(updated)

            assertEquals(setOf(1, 2), tracker.state.value.queueingRequests.single().request.requestedSeasonNumbers)
            tracker.stopForeground()
        }

    @Test
    fun queueingExpiresEvenWhenReconciliationKeepsFailing() =
        runTest {
            val tracker = tracker(MutableStateFlow(SeerrAcquisitionSession(1, 1))) { error("offline") }
            tracker.startForeground()
            runCurrent()
            tracker.registerQueueing(movieRequest(904, size = null, sizeLeft = null))
            advanceTimeBy(15 * 60_000L)

            tracker.refreshNow()
            runCurrent()

            assertTrue(tracker.state.value.queueingRequests.isEmpty())
            tracker.stopForeground()
        }

    @Test
    fun initialAvailableTimestampUsesRequestUpdateNotMutableMediaUpdate() {
        val requestUpdated = Instant.parse("2026-08-01T00:00:00Z")
        val mediaUpdated = Instant.parse("2026-08-31T00:00:00Z")
        val available =
            MediaRequest(
                id = 1,
                status = 2,
                type = "movie",
                updatedAt = requestUpdated.toString(),
                media =
                    MediaInfo(
                        id = 1,
                        status = SeerrAvailability.AVAILABLE.status,
                        updatedAt = mediaUpdated.toString(),
                    ),
            ).toSeerrRequestAcquisition()

        val stamped = stampAvailabilityTransitions(listOf(available), emptyList(), mediaUpdated.toEpochMilli())

        assertEquals(requestUpdated.toEpochMilli(), stamped.single().request.availableSinceEpochMillis)
    }

    @Test
    fun observedAvailabilityTransitionUsesObservationTime() {
        val processing = movieRequest(1, size = null, sizeLeft = null)
        val available =
            processing.copy(
                request = processing.request.copy(availability = SeerrAvailability.AVAILABLE),
            )

        val stamped = stampAvailabilityTransitions(listOf(available), listOf(processing), 1234L)

        assertEquals(1234L, stamped.single().request.availableSinceEpochMillis)
    }

    @Test
    fun initialTvSeasonCompletionUsesRequestedSeasonUpdateTime() {
        val completedAt = Instant.parse("2026-09-01T07:38:08Z")
        val completed =
            MediaRequest(
                id = 2,
                status = 5,
                type = "tv",
                updatedAt = "2026-09-01T07:40:00Z",
                seasons =
                    listOf(
                        Season(
                            seasonNumber = 1,
                            status = SeerrAvailability.AVAILABLE.status,
                            updatedAt = completedAt.toString(),
                        ),
                    ),
                media =
                    MediaInfo(
                        id = 20,
                        status = SeerrAvailability.PARTIALLY_AVAILABLE.status,
                    ),
            ).toSeerrRequestAcquisition()

        val stamped = stampAvailabilityTransitions(listOf(completed), emptyList(), completedAt.plusSeconds(60).toEpochMilli())

        assertEquals(completedAt.toEpochMilli(), stamped.single().request.seasonAvailableSinceEpochMillis[1])
    }

    @Test
    fun observedTvSeasonCompletionUsesObservationTime() {
        val processing =
            MediaRequest(
                id = 2,
                status = 2,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.PROCESSING.status)),
                media = MediaInfo(id = 20, status = SeerrAvailability.PARTIALLY_AVAILABLE.status),
            ).toSeerrRequestAcquisition()
        val completed =
            MediaRequest(
                id = 2,
                status = 5,
                type = "tv",
                seasons =
                    listOf(
                        Season(
                            seasonNumber = 1,
                            status = SeerrAvailability.AVAILABLE.status,
                            updatedAt = "2026-09-01T07:38:08Z",
                        ),
                    ),
                media = MediaInfo(id = 20, status = SeerrAvailability.PARTIALLY_AVAILABLE.status),
            ).toSeerrRequestAcquisition()

        val stamped = stampAvailabilityTransitions(listOf(completed), listOf(processing), 1234L)

        assertEquals(1234L, stamped.single().request.seasonAvailableSinceEpochMillis[1])
    }

    @Test
    fun observedJellyfinMovieReadinessUsesObservationTime() {
        val processing = movieRequest(1, size = null, sizeLeft = null)
        val ready =
            processing.copy(
                request =
                    processing.request.copy(
                        jellyfinReadiness = JellyfinAcquisitionReadiness(movieItemId = UUID.randomUUID()),
                    ),
            )

        val stamped = stampJellyfinReadinessTransitions(listOf(ready), listOf(processing), 1234L)

        assertEquals(1234L, stamped.single().request.jellyfinReadySinceEpochMillis)
    }

    @Test
    fun initialJellyfinMovieReadinessDoesNotInventCompletionTime() {
        val request = movieRequest(1, size = null, sizeLeft = null)
        val ready =
            request.copy(
                request =
                    request.request.copy(
                        jellyfinReadiness = JellyfinAcquisitionReadiness(movieItemId = UUID.randomUUID()),
                    ),
            )

        val stamped = stampJellyfinReadinessTransitions(listOf(ready), emptyList(), 1234L)

        assertEquals(null, stamped.single().request.jellyfinReadySinceEpochMillis)
    }

    @Test
    fun alreadyReadyJellyfinMovieRetainsOriginalCompletionTime() {
        val request = movieRequest(1, size = null, sizeLeft = null)
        val ready =
            request.copy(
                request =
                    request.request.copy(
                        jellyfinReadiness = JellyfinAcquisitionReadiness(movieItemId = UUID.randomUUID()),
                        jellyfinReadySinceEpochMillis = 1234L,
                    ),
            )

        val stamped = stampJellyfinReadinessTransitions(listOf(ready), listOf(ready), 5678L)

        assertEquals(1234L, stamped.single().request.jellyfinReadySinceEpochMillis)
    }

    @Test
    fun initialJellyfinSeasonReadinessDoesNotInventCompletionTime() {
        val ready =
            tvRequest(1, emptyList()).let { acquisition ->
                acquisition.copy(
                    request =
                        acquisition.request.copy(
                            seasonEpisodeCounts = mapOf(1 to 1),
                            jellyfinReadiness =
                                JellyfinAcquisitionReadiness(
                                    episodeItemIds = mapOf(1 to mapOf(1 to UUID.randomUUID())),
                                ),
                        ),
                )
            }

        val stamped = stampJellyfinReadinessTransitions(listOf(ready), emptyList(), 1234L)

        assertTrue(stamped.single().request.jellyfinSeasonReadySinceEpochMillis.isEmpty())
    }

    @Test
    fun coldStartPublishesRecentMovieAfterReadinessRehydration() =
        runTest {
            val movieId = UUID.randomUUID()
            val loaded =
                movieRequest(3, size = null, sizeLeft = null).let { acquisition ->
                    acquisition.copy(
                        request =
                            acquisition.request.copy(
                                availability = SeerrAvailability.AVAILABLE,
                                updatedAt = Instant.EPOCH.toString(),
                            ),
                    )
                }
            val tracker =
                tracker(
                    sessions = MutableStateFlow(SeerrAcquisitionSession(1, 1)),
                    resolveReadiness = { requests ->
                        requests.map { acquisition ->
                            acquisition.copy(
                                request =
                                    acquisition.request.copy(
                                        jellyfinReadiness = JellyfinAcquisitionReadiness(movieItemId = movieId),
                                    ),
                            )
                        }
                    },
                ) { listOf(loaded) }

            tracker.startForeground()
            runCurrent()

            val published = tracker.state.value.requests.single()
            assertEquals(movieId, published.request.jellyfinReadiness.movieItemId)
            val item = listOf(published).toDownloadSections(testScheduler.currentTime).completed.single()
            val destination = item.destination("Movie") as Destination.MediaItem
            assertEquals(movieId, destination.itemId)
            tracker.stopForeground()
        }

    @Test
    fun jellyfinSeasonRequiresExpectedEpisodeCount() {
        val processing = tvRequest(1, emptyList())
        val episodeIds = mapOf(1 to mapOf(1 to UUID.randomUUID(), 2 to UUID.randomUUID()))
        val partial =
            processing.copy(
                request =
                    processing.request.copy(
                        seasonEpisodeCounts = mapOf(1 to 3),
                        jellyfinReadiness = JellyfinAcquisitionReadiness(episodeItemIds = episodeIds),
                    ),
            )
        val complete =
            partial.copy(
                request =
                    partial.request.copy(
                        jellyfinReadiness =
                            JellyfinAcquisitionReadiness(
                                episodeItemIds =
                                    mapOf(
                                        1 to
                                            mapOf(
                                                1 to UUID.randomUUID(),
                                                2 to UUID.randomUUID(),
                                                3 to UUID.randomUUID(),
                                            ),
                                    ),
                            ),
                    ),
            )

        assertTrue(stampJellyfinReadinessTransitions(listOf(partial), emptyList(), 1234L).single().request.jellyfinSeasonReadySinceEpochMillis.isEmpty())
        assertEquals(1234L, stampJellyfinReadinessTransitions(listOf(complete), listOf(partial), 1234L).single().request.jellyfinSeasonReadySinceEpochMillis[1])
    }

    @Test
    fun previouslyResolvedJellyfinIdentitySurvivesFreshSeerrSnapshot() {
        val movieId = UUID.randomUUID()
        val seriesId = UUID.randomUUID()
        val seasonId = UUID.randomUUID()
        val episodeId = UUID.randomUUID()
        val previous =
            tvRequest(70, emptyList()).let { acquisition ->
                acquisition.copy(
                    request =
                        acquisition.request.copy(
                            jellyfinReadiness =
                                JellyfinAcquisitionReadiness(
                                    movieItemId = movieId,
                                    seriesItemId = seriesId,
                                    seasonItemIds = mapOf(1 to seasonId),
                                    episodeItemIds = mapOf(1 to mapOf(1 to episodeId)),
                                ),
                            jellyfinSeasonReadySinceEpochMillis = mapOf(1 to 1234L),
                        ),
                )
            }
        val fresh = tvRequest(70, emptyList())

        val retained = retainJellyfinReadiness(listOf(fresh), listOf(previous)).single().request

        assertEquals(movieId, retained.jellyfinReadiness.movieItemId)
        assertEquals(seriesId, retained.jellyfinReadiness.seriesItemId)
        assertEquals(seasonId, retained.jellyfinReadiness.seasonItemIds[1])
        assertEquals(episodeId, retained.jellyfinReadiness.episodeItemIds[1]?.get(1))
        assertEquals(1234L, retained.jellyfinSeasonReadySinceEpochMillis[1])
    }

    @Test
    fun seerrCompletedTargetsStillRequireJellyfinIdentityResolution() {
        val completedMovie =
            MediaRequest(
                id = 71,
                status = 5,
                type = "movie",
                media = MediaInfo(id = 71, status = SeerrAvailability.AVAILABLE.status),
            ).toSeerrRequestAcquisition()
        val completedSeason =
            MediaRequest(
                id = 72,
                status = 5,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.AVAILABLE.status)),
                media = MediaInfo(id = 72, status = SeerrAvailability.PARTIALLY_AVAILABLE.status),
            ).toSeerrRequestAcquisition().let { acquisition ->
                acquisition.copy(
                    request = acquisition.request.copy(seasonEpisodeCounts = mapOf(1 to 1)),
                )
            }

        assertTrue(completedMovie.needsJellyfinReadinessCheck())
        assertTrue(completedSeason.needsJellyfinReadinessCheck())
    }

    @Test
    fun ledgerRetainsHistoryUntilJellyfinReadinessIsTerminal() {
        val ledger = SeerrAcquisitionLedger()
        val active = partialTvRequest(listOf(episode("episode-1", 1, 100.0, 25.0)))
        ledger.reconcile(listOf(active))
        val seerrComplete =
            partialTvRequest(emptyList()).let { acquisition ->
                acquisition.copy(
                    request =
                        acquisition.request.copy(
                            seasonAvailability = mapOf(1 to SeerrAvailability.AVAILABLE),
                            seasonEpisodeCounts = mapOf(1 to 1),
                        ),
                )
            }

        val retained = ledger.reconcile(listOf(seerrComplete)).single().acquisition as SeerrAcquisitionState.Tv
        assertEquals(1, retained.seasons.single().aggregate.entries.size)

        val jellyfinReady =
            seerrComplete.copy(
                request =
                    seerrComplete.request.copy(
                        jellyfinReadiness =
                            JellyfinAcquisitionReadiness(
                                seriesItemId = UUID.randomUUID(),
                                episodeItemIds = mapOf(1 to mapOf(1 to UUID.randomUUID())),
                            ),
                    ),
            )
        val terminal = ledger.reconcile(listOf(jellyfinReady)).single().acquisition

        assertFalse(terminal is SeerrAcquisitionState.Tv)
    }

    @Test
    fun initialPollPopulatesGlobalState() =
        runTest {
            val sessions = MutableStateFlow<SeerrAcquisitionSession?>(SeerrAcquisitionSession(1, 42))
            var loads = 0
            val tracker =
                tracker(sessions) {
                    loads++
                    listOf(movieRequest(1, size = 100.0, sizeLeft = 25.0))
                }

            tracker.startForeground()
            runCurrent()

            assertEquals(1, loads)
            assertEquals(1, tracker.state.value.requests.size)
            assertEquals(1, tracker.state.value.activeAcquisitionCount)
            assertEquals(SeerrAcquisitionSession(1, 42), tracker.state.value.session)
            tracker.stopForeground()
        }

    @Test
    fun disappearingQueueItemRetainsProgressWithoutRemainingDownloading() =
        runTest {
            var current = listOf(movieRequest(1, size = 100.0, sizeLeft = 40.0))
            val tracker = tracker(MutableStateFlow(SeerrAcquisitionSession(1, 1))) { current }
            tracker.startForeground()
            runCurrent()

            current = listOf(movieRequest(1, size = null, sizeLeft = null))
            tracker.refreshNow()
            runCurrent()

            val movie = tracker.state.value.requests.single().acquisition as SeerrAcquisitionState.Movie
            assertEquals(0.6, movie.aggregate.progress!!.fraction, 0.0)
            assertFalse(movie.aggregate.entries.single().presentInQueue)
            assertFalse(movie.aggregate.entries.single().status.name == "DOWNLOADING")
            tracker.stopForeground()
        }

    @Test
    fun downloadingStatusDoesNotBecomeActiveUntilSizeMoves() =
        runTest {
            var current = listOf(movieRequest(1, size = 100.0, sizeLeft = 100.0))
            val tracker = tracker(MutableStateFlow(SeerrAcquisitionSession(1, 1))) { current }
            tracker.startForeground()
            runCurrent()

            val queuedEntry =
                (tracker.state.value.requests.single().acquisition as SeerrAcquisitionState.Movie)
                    .aggregate.entries.single()
            assertFalse(queuedEntry.hasObservedProgress)
            assertEquals(0, tracker.state.value.activeAcquisitionCount)

            current = listOf(movieRequest(1, size = 100.0, sizeLeft = 90.0))
            tracker.refreshNow()
            runCurrent()

            val movingEntry =
                (tracker.state.value.requests.single().acquisition as SeerrAcquisitionState.Movie)
                    .aggregate.entries.single()
            assertTrue(movingEntry.hasObservedProgress)
            assertEquals(1, tracker.state.value.activeAcquisitionCount)
            tracker.stopForeground()
        }

    @Test
    fun episodeRetryWithNewDownloadIdDoesNotDoubleCount() =
        runTest {
            var current = listOf(tvRequest(1, "old", 100.0, 50.0))
            val tracker = tracker(MutableStateFlow(SeerrAcquisitionSession(1, 1))) { current }
            tracker.startForeground()
            runCurrent()

            current = listOf(tvRequest(1, "retry", 100.0, 25.0))
            tracker.refreshNow()
            runCurrent()

            val tv = tracker.state.value.requests.single().acquisition as SeerrAcquisitionState.Tv
            val aggregate = tv.seasons.single().aggregate
            assertEquals(1, aggregate.entries.size)
            assertEquals("retry", aggregate.entries.single().downloadId)
            assertEquals(100.0, aggregate.progress!!.totalSize, 0.0)
            assertEquals(0.75, aggregate.progress.fraction, 0.0)
            tracker.stopForeground()
        }

    @Test
    fun newEpisodeIncreasesSeasonDenominator() =
        runTest {
            var current = listOf(tvRequest(1, "one", 100.0, 0.0))
            val tracker = tracker(MutableStateFlow(SeerrAcquisitionSession(1, 1))) { current }
            tracker.startForeground()
            runCurrent()

            current =
                listOf(
                    tvRequest(
                        requestId = 1,
                        entries =
                            listOf(
                                episode("one", 1, 100.0, 0.0),
                                episode("two", 2, 300.0, 300.0),
                            ),
                    ),
                )
            tracker.refreshNow()
            runCurrent()

            val tv = tracker.state.value.requests.single().acquisition as SeerrAcquisitionState.Tv
            assertEquals(400.0, tv.seasons.single().aggregate.progress!!.totalSize, 0.0)
            assertEquals(0.25, tv.seasons.single().aggregate.progress!!.fraction, 0.0)
            tracker.stopForeground()
        }

    @Test
    fun tvEpisodeEntriesDisappearIndependentlyWithoutResettingSeasonProgress() =
        runTest {
            var current =
                listOf(
                    partialTvRequest(
                        listOf(
                            episode("one", 1, 100.0, 50.0),
                            episode("two", 2, 100.0, 100.0),
                        ),
                    ),
                )
            val tracker = tracker(MutableStateFlow(SeerrAcquisitionSession(1, 1))) { current }
            tracker.startForeground()
            runCurrent()

            current = listOf(partialTvRequest(listOf(episode("two", 2, 100.0, 50.0))))
            tracker.refreshNow()
            runCurrent()

            var season =
                (tracker.state.value.requests.single().acquisition as SeerrAcquisitionState.Tv)
                    .seasons.single()
            assertEquals(2, season.aggregate.entries.size)
            assertEquals(0.5, season.aggregate.progress!!.fraction, 0.0)
            assertEquals(1, season.aggregate.entries.count { it.presentInQueue })

            current = listOf(partialTvRequest(emptyList()))
            tracker.refreshNow()
            runCurrent()

            season =
                (tracker.state.value.requests.single().acquisition as SeerrAcquisitionState.Tv)
                    .seasons.single()
            assertEquals(2, season.aggregate.entries.size)
            assertEquals(0.5, season.aggregate.progress!!.fraction, 0.0)
            assertTrue(season.aggregate.entries.none { it.presentInQueue })
            tracker.stopForeground()
        }

    @Test
    fun normalAndFourKLedgersRemainIsolated() =
        runTest {
            var current =
                listOf(
                    movieRequest(1, size = 100.0, sizeLeft = 50.0, is4k = false),
                    movieRequest(2, size = 400.0, sizeLeft = 100.0, is4k = true),
                )
            val tracker = tracker(MutableStateFlow(SeerrAcquisitionSession(1, 1))) { current }
            tracker.startForeground()
            runCurrent()

            current =
                listOf(
                    movieRequest(1, size = null, sizeLeft = null, is4k = false),
                    movieRequest(2, size = 400.0, sizeLeft = 0.0, is4k = true),
                )
            tracker.refreshNow()
            runCurrent()

            val normal = tracker.state.value.requests.first { !it.request.is4k }.movieProgress()
            val fourK = tracker.state.value.requests.first { it.request.is4k }.movieProgress()
            assertEquals(0.5, normal, 0.0)
            assertEquals(1.0, fourK, 0.0)
            tracker.stopForeground()
        }

    @Test
    fun serverOrUserSwitchResetsStateAndLedger() =
        runTest {
            val sessions = MutableStateFlow<SeerrAcquisitionSession?>(SeerrAcquisitionSession(1, 1))
            val tracker =
                tracker(sessions) {
                    if (sessions.value?.userId == 1) {
                        listOf(movieRequest(1, size = 100.0, sizeLeft = 50.0))
                    } else {
                        listOf(movieRequest(2, size = null, sizeLeft = null))
                    }
                }
            tracker.startForeground()
            runCurrent()

            sessions.value = SeerrAcquisitionSession(2, 2)
            runCurrent()

            assertEquals(SeerrAcquisitionSession(2, 2), tracker.state.value.session)
            assertEquals(2, tracker.state.value.requests.single().request.requestId)
            assertEquals(SeerrAcquisitionState.Processing, tracker.state.value.requests.single().acquisition)
            tracker.stopForeground()
        }

    @Test
    fun networkFailureRetainsLastGoodSnapshot() =
        runTest {
            var fail = false
            val tracker =
                tracker(MutableStateFlow(SeerrAcquisitionSession(1, 1))) {
                    if (fail) error("offline")
                    listOf(movieRequest(1, size = 100.0, sizeLeft = 50.0))
                }
            tracker.startForeground()
            runCurrent()
            val good = tracker.state.value.requests

            fail = true
            tracker.refreshNow()
            runCurrent()

            assertEquals(good, tracker.state.value.requests)
            assertEquals(1, tracker.state.value.consecutiveFailures)
            assertEquals("offline", tracker.state.value.lastError)
            tracker.stopForeground()
        }

    private fun kotlinx.coroutines.test.TestScope.tracker(
        sessions: MutableStateFlow<SeerrAcquisitionSession?>,
        resolveReadiness: suspend (List<SeerrRequestAcquisition>) -> List<SeerrRequestAcquisition> = { it },
        acquisitionEnabled: () -> Boolean = { true },
        loader: suspend () -> List<SeerrRequestAcquisition>,
    ): SeerrAcquisitionTracker {
        val tracker =
            SeerrAcquisitionTracker(
                loadRequests = loader,
                resolveJellyfinReadiness = resolveReadiness,
                sessions = sessions,
                dispatcher = StandardTestDispatcher(testScheduler),
                pollIntervalMillis = 30_000L,
                maxBackoffMillis = 300_000L,
                currentTimeMillis = { testScheduler.currentTime },
                acquisitionEnabled = acquisitionEnabled,
            )
        backgroundScope.coroutineContext[Job]?.invokeOnCompletion { tracker.stopForeground() }
        return tracker
    }

    private fun movieRequest(
        requestId: Int,
        size: Double?,
        sizeLeft: Double?,
        is4k: Boolean = false,
    ): SeerrRequestAcquisition {
        val entry = size?.let { download("movie-$requestId", it, sizeLeft ?: 0.0) }
        return MediaRequest(
            id = requestId,
            status = 2,
            type = "movie",
            is4k = is4k,
            media =
                MediaInfo(
                    id = 10,
                    status = SeerrAvailability.PROCESSING.status,
                    downloadStatus = if (is4k) null else listOfNotNull(entry),
                    downloadStatus4k = if (is4k) listOfNotNull(entry) else null,
                ),
        ).toSeerrRequestAcquisition()
    }

    private fun tvRequest(
        requestId: Int,
        downloadId: String,
        size: Double,
        sizeLeft: Double,
    ) = tvRequest(requestId, listOf(episode(downloadId, 1, size, sizeLeft)))

    private fun tvRequest(
        requestId: Int,
        entries: List<DownloadStatus>,
    ) = MediaRequest(
        id = requestId,
        status = 2,
        type = "tv",
        seasons = listOf(Season(seasonNumber = 1)),
        media =
            MediaInfo(
                id = 20,
                status = SeerrAvailability.PROCESSING.status,
                downloadStatus = entries,
            ),
    ).toSeerrRequestAcquisition()

    private fun partialTvRequest(entries: List<DownloadStatus>) =
        MediaRequest(
            id = 1,
            status = 2,
            type = "tv",
            seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.PROCESSING.status)),
            media =
                MediaInfo(
                    id = 20,
                    status = SeerrAvailability.PARTIALLY_AVAILABLE.status,
                    downloadStatus = entries,
                ),
        ).toSeerrRequestAcquisition()

    private fun episode(
        downloadId: String,
        episodeNumber: Int,
        size: Double,
        sizeLeft: Double,
    ) = download(downloadId, size, sizeLeft).copy(
        episode =
            DownloadStatusEpisode(
                seriesId = 20,
                seasonNumber = 1,
                episodeNumber = episodeNumber,
                title = "Episode $episodeNumber",
                hasFile = false,
            ),
    )

    private fun download(
        downloadId: String,
        size: Double,
        sizeLeft: Double,
    ) = DownloadStatus(
        externalId = 20,
        downloadId = downloadId,
        propertySize = size,
        sizeLeft = sizeLeft,
        status = "downloading",
    )

    private fun SeerrRequestAcquisition.movieProgress(): Double =
        (acquisition as SeerrAcquisitionState.Movie).aggregate.progress!!.fraction
}
