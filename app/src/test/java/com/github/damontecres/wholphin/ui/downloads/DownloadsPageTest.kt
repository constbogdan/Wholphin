package com.github.damontecres.wholphin.ui.downloads

import com.github.damontecres.wholphin.api.seerr.model.DownloadStatus
import com.github.damontecres.wholphin.api.seerr.model.DownloadStatusEpisode
import com.github.damontecres.wholphin.api.seerr.model.MediaInfo
import com.github.damontecres.wholphin.api.seerr.model.MediaRequest
import com.github.damontecres.wholphin.api.seerr.model.Season
import com.github.damontecres.wholphin.api.seerr.model.RequestUser
import com.github.damontecres.wholphin.data.model.SeerrAvailability
import com.github.damontecres.wholphin.data.model.SeerrAcquisitionState
import com.github.damontecres.wholphin.data.model.SeerrRequestAcquisition
import com.github.damontecres.wholphin.data.model.TV_PROGRESS_GRACE_POLLS
import com.github.damontecres.wholphin.data.model.TvSeasonLifecycle
import com.github.damontecres.wholphin.data.model.JellyfinAcquisitionReadiness
import com.github.damontecres.wholphin.data.model.toSeerrRequestAcquisition
import com.github.damontecres.wholphin.data.model.toTvSeasonTargets
import com.github.damontecres.wholphin.ui.cards.CardAcquisitionState
import com.github.damontecres.wholphin.ui.cards.tvSeasonCardPresentation
import com.github.damontecres.wholphin.ui.nav.Destination
import com.github.damontecres.wholphin.services.SeerrAcquisitionLedger
import org.jellyfin.sdk.model.api.BaseItemKind
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.UUID

class DownloadsPageTest {
    private val now = Instant.parse("2026-08-31T12:00:00Z")

    @Test
    fun queueingMovieAndTvSeasonRenderImmediatelyWithoutProgress() {
        val movie = request(900, updatedAt = now.toString()).copy(acquisition = SeerrAcquisitionState.Queueing)
        val tv = tvSeasonRequest(901, emptyList(), expectedEpisodeCount = 22)
            .copy(acquisition = SeerrAcquisitionState.Queueing)

        val sections = listOf(movie, tv).toDownloadSections(now.toEpochMilli())

        assertEquals(listOf(DownloadStatusLabel.QUEUEING, DownloadStatusLabel.QUEUEING), sections.processing.map { it.status })
        assertEquals(listOf("900_movie", "901_season_1"), sections.processing.map { it.key })
        assertTrue(sections.processing.all { it.progress == null && it.timing == null })
    }

    @Test
    fun staleProcessingWithoutQueueIsExcluded() {
        val request = request(1, updatedAt = now.minusSeconds(16 * 60).toString())

        val sections = listOf(request).toDownloadSections(now.toEpochMilli())

        assertTrue(sections.active.isEmpty())
        assertTrue(sections.processing.isEmpty())
    }

    @Test
    fun recentProcessingWithoutQueueUsesGraceWindow() {
        val request = request(1, updatedAt = now.minusSeconds(14 * 60).toString())

        val sections = listOf(request).toDownloadSections(now.toEpochMilli())

        assertEquals(1, sections.processing.size)
    }

    @Test
    fun liveQueueEntryIsActiveRegardlessOfRequestAge() {
        val request =
            request(
                1,
                updatedAt = now.minusSeconds(30 * 24 * 60 * 60).toString(),
                queue = listOf(DownloadStatus(status = "downloading", propertySize = 100.0, sizeLeft = 50.0)),
            )

        val sections = listOf(request).toDownloadSections(now.toEpochMilli())

        assertEquals(1, sections.active.size)
        assertEquals(.5f, sections.active.single().progress!!, 0f)
        assertEquals(DownloadStatusLabel.IN_PROGRESS, sections.active.single().status)
    }

    @Test
    fun queuedItemDoesNotExposeStaleTiming() {
        val queued =
            request(
                1,
                updatedAt = now.toString(),
                queue =
                    listOf(
                        DownloadStatus(
                            status = "queued",
                            propertySize = 100.0,
                            sizeLeft = 100.0,
                            timeLeft = "00:00:00",
                            estimatedCompletionTime = now.plusSeconds(3600).toString(),
                        ),
                    ),
            )

        val item = listOf(queued).toDownloadSections(now.toEpochMilli()).processing.single()

        assertEquals(DownloadStatusLabel.QUEUED, item.status)
        assertEquals(null, item.timing)
        assertEquals(null, item.progress)
    }

    @Test
    fun readyMovieWithCurrentUpgradeStaysOperationalBeforeHistory() {
        val completedAt = now.minusSeconds(24 * 60 * 60).toEpochMilli()
        fun readyUpgrade(status: String, sizeLeft: Double) =
            request(
                id = 910,
                updatedAt = now.toString(),
                queue = listOf(DownloadStatus(status = status, propertySize = 100.0, sizeLeft = sizeLeft)),
            ).let { acquisition ->
                acquisition.copy(
                    request =
                        acquisition.request.copy(
                            jellyfinReadiness = JellyfinAcquisitionReadiness(movieItemId = UUID.randomUUID()),
                            jellyfinReadySinceEpochMillis = completedAt,
                        ),
                )
            }

        val queued = listOf(readyUpgrade("queued", 99.9)).toDownloadSections(now.toEpochMilli())
        val progressing = listOf(readyUpgrade("downloading", 50.0)).toDownloadSections(now.toEpochMilli())
        val finishing = listOf(readyUpgrade("completed", 0.0)).toDownloadSections(now.toEpochMilli())

        assertEquals(DownloadStatusLabel.QUEUED, queued.processing.single().status)
        assertEquals(null, queued.processing.single().progress)
        assertEquals(DownloadStatusLabel.IN_PROGRESS, progressing.active.single().status)
        assertEquals(.5f, progressing.active.single().progress!!, 0f)
        assertEquals(DownloadStatusLabel.FINISHING, finishing.processing.single().status)
        assertEquals(null, finishing.processing.single().progress)
        assertTrue((queued.completed + progressing.completed + finishing.completed).isEmpty())
        assertEquals(1, queued.processing.size)
        assertEquals(1, progressing.active.size)
        assertEquals(1, finishing.processing.size)
    }

    @Test
    fun seerrAvailableMovieWaitsInFinishingUntilJellyfinReady() {
        val request =
            MediaRequest(
                id = 911,
                status = 5,
                type = "movie",
                media =
                    MediaInfo(
                        id = 911,
                        tmdbId = 911,
                        status = SeerrAvailability.AVAILABLE.status,
                        downloadStatus =
                            listOf(
                                DownloadStatus(
                                    status = "completed",
                                    propertySize = 100.0,
                                    sizeLeft = 0.0,
                                ),
                            ),
                    ),
            ).toSeerrRequestAcquisition()

        val sections = listOf(request).toDownloadSections(now.toEpochMilli())

        assertEquals(DownloadStatusLabel.FINISHING, sections.processing.single().status)
        assertEquals(null, sections.processing.single().progress)
        assertTrue(sections.completed.isEmpty())
    }

    @Test
    fun readySeasonWithCurrentReplacementUsesTheSameLifecycleAsSharedCards() {
        fun readyReplacement(status: String, sizeLeft: Double) =
            tvSeasonRequest(
                id = 912,
                queue = listOf(tvEpisode(1, 100.0, sizeLeft).copy(status = status)),
                expectedEpisodeCount = 1,
            ).let { acquisition ->
                acquisition.copy(
                    request =
                        acquisition.request.copy(
                            seasonAvailableSinceEpochMillis = mapOf(1 to now.minusSeconds(60).toEpochMilli()),
                            jellyfinReadiness =
                                JellyfinAcquisitionReadiness(
                                    seriesItemId = UUID.randomUUID(),
                                    episodeItemIds = mapOf(1 to mapOf(1 to UUID.randomUUID())),
                                ),
                            jellyfinSeasonReadySinceEpochMillis = mapOf(1 to now.minusSeconds(60).toEpochMilli()),
                        ),
                )
            }

        val queued = readyReplacement("queued", 99.9)
        val progressing = readyReplacement("downloading", 50.0)
        val finishing = readyReplacement("completed", 0.0)

        listOf(
            queued to DownloadStatusLabel.QUEUED,
            progressing to DownloadStatusLabel.IN_PROGRESS,
            finishing to DownloadStatusLabel.FINISHING,
        ).forEach { (request, expectedStatus) ->
            val targetPresentation = request.toTvSeasonTargets().single().tvSeasonCardPresentation()
            val sections = listOf(request).toDownloadSections(now.toEpochMilli())
            val row = (sections.active + sections.processing).single()

            assertEquals(expectedStatus, row.status)
            assertTrue(sections.completed.isEmpty())
            when (targetPresentation?.acquisitionState) {
                CardAcquisitionState.QUEUED -> assertEquals(DownloadStatusLabel.QUEUED, row.status)
                CardAcquisitionState.FINISHING -> assertEquals(DownloadStatusLabel.FINISHING, row.status)
                null -> assertEquals(targetPresentation?.acquisitionProgress, row.progress)
                else -> throw AssertionError("Unexpected shared TV card state: ${targetPresentation.acquisitionState}")
            }
        }
    }

    @Test
    fun zeroRemainingQueueItemIsFinishingNotComplete() {
        val finishing =
            request(
                1,
                updatedAt = now.toString(),
                queue =
                    listOf(
                        DownloadStatus(
                            status = "completed",
                            propertySize = 100.0,
                            sizeLeft = 0.0,
                            timeLeft = "00:00:00",
                        ),
                    ),
            )

        val item = listOf(finishing).toDownloadSections(now.toEpochMilli()).processing.single()

        assertEquals(DownloadStatusLabel.FINISHING, item.status)
        assertTrue(!item.completed)
        assertEquals(null, item.progress)
        assertEquals(null, item.timing)
    }

    @Test
    fun disappearedKnownQueueItemRemainsFinishingOutsideWaitingGrace() {
        val historical =
            request(
                1,
                updatedAt = now.minusSeconds(60 * 60).toString(),
                queue = listOf(DownloadStatus(status = "downloading", propertySize = 100.0, sizeLeft = 5.0)),
            ).let { acquisition ->
                val movie = acquisition.acquisition as SeerrAcquisitionState.Movie
                acquisition.copy(
                    acquisition =
                        SeerrAcquisitionState.Movie(
                            movie.aggregate.copy(
                                entries = movie.aggregate.entries.map { it.copy(presentInQueue = false) },
                            ),
                        ),
                )
            }

        val sections = listOf(historical).toDownloadSections(now.toEpochMilli())

        assertTrue(sections.active.isEmpty())
        assertEquals(DownloadStatusLabel.FINISHING, sections.processing.single().status)
    }

    @Test
    fun staleEtaIsHiddenWhilePositiveRemainingTimeIsKept() {
        val moving =
            request(
                1,
                updatedAt = now.toString(),
                queue =
                    listOf(
                        DownloadStatus(
                            status = "downloading",
                            propertySize = 100.0,
                            sizeLeft = 50.0,
                            timeLeft = "00:10:00",
                            estimatedCompletionTime = now.minusSeconds(1).toString(),
                        ),
                    ),
            )

        val item = listOf(moving).toDownloadSections(now.toEpochMilli()).active.single()

        assertEquals("00:10:00", item.timing?.remaining)
        assertEquals(null, item.timing?.eta)
    }

    @Test
    fun jellyfinReadyMovieMovesSectionsWithStableKey() {
        val finishing =
            request(
                1,
                updatedAt = now.toString(),
                queue = listOf(DownloadStatus(status = "completed", propertySize = 100.0, sizeLeft = 0.0)),
            )
        val ready =
            finishing.copy(
                request =
                    finishing.request.copy(
                        jellyfinReadiness = JellyfinAcquisitionReadiness(movieItemId = UUID.randomUUID()),
                        jellyfinReadySinceEpochMillis = now.toEpochMilli(),
                    ),
                acquisition =
                    (finishing.acquisition as SeerrAcquisitionState.Movie).let { movie ->
                        movie.copy(
                            aggregate =
                                movie.aggregate.copy(
                                    entries = movie.aggregate.entries.map { it.copy(presentInQueue = false) },
                                ),
                        )
                    },
            )

        val finishingItem = listOf(finishing).toDownloadSections(now.toEpochMilli()).processing.single()
        val completedItem = listOf(ready).toDownloadSections(now.toEpochMilli()).completed.single()

        assertEquals(finishingItem.key, completedItem.key)
        assertEquals(DownloadStatusLabel.AVAILABLE, completedItem.status)
        val destination = completedItem.destination("Movie") as Destination.MediaItem
        assertEquals(ready.request.jellyfinReadiness.movieItemId, destination.itemId)
        assertEquals(BaseItemKind.MOVIE, destination.type)
    }

    @Test
    fun nonReadyItemAlwaysUsesDiscoverDestination() {
        val item =
            listOf(request(1, updatedAt = now.toString()))
                .toDownloadSections(now.toEpochMilli()).processing.single()

        assertTrue(item.destination("Movie") is Destination.DiscoveredItem)
    }

    @Test
    fun jellyfinReadySeasonUsesResolvedSeasonDestinationButSeerrOnlyCompletionDoesNot() {
        val seriesId = UUID.randomUUID()
        val seasonId = UUID.randomUUID()
        val base =
            MediaRequest(
                id = 23,
                status = 5,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.AVAILABLE.status)),
                media = MediaInfo(id = 23, tmdbId = 23, status = SeerrAvailability.PARTIALLY_AVAILABLE.status),
            ).toSeerrRequestAcquisition()
        val seerrOnly =
            base.copy(
                request = base.request.copy(seasonAvailableSinceEpochMillis = mapOf(1 to now.toEpochMilli())),
            )
        val jellyfinReady =
            seerrOnly.copy(
                request =
                    seerrOnly.request.copy(
                        seasonEpisodeCounts = mapOf(1 to 1),
                        jellyfinReadiness =
                            JellyfinAcquisitionReadiness(
                                seriesItemId = seriesId,
                                seasonItemIds = mapOf(1 to seasonId),
                                episodeItemIds = mapOf(1 to mapOf(1 to UUID.randomUUID())),
                            ),
                        jellyfinSeasonReadySinceEpochMillis = mapOf(1 to now.toEpochMilli()),
                    ),
            )

        val seerrOnlySections = listOf(seerrOnly).toDownloadSections(now.toEpochMilli())
        assertTrue(seerrOnlySections.completed.isEmpty())
        assertTrue(seerrOnlySections.processing.single().destination("TV Series") is Destination.DiscoveredItem)
        val completedItem = listOf(jellyfinReady).toDownloadSections(now.toEpochMilli()).completed.single()
        val destination = completedItem.destination("TV Series") as Destination.SeriesOverview
        assertEquals(seriesId, destination.itemId)
        assertEquals(BaseItemKind.SERIES, destination.type)
        assertEquals(seasonId, destination.seasonEpisode?.seasonId)
        assertEquals(1, destination.seasonEpisode?.seasonNumber)

        val unresolvedSeason =
            completedItem.copy(
                request =
                    jellyfinReady.copy(
                        request =
                            jellyfinReady.request.copy(
                                jellyfinReadiness =
                                    jellyfinReady.request.jellyfinReadiness.copy(seasonItemIds = emptyMap()),
                            ),
                    ),
            )
        val fallback = unresolvedSeason.destination("TV Series") as Destination.MediaItem
        assertEquals(seriesId, fallback.itemId)
        assertEquals(BaseItemKind.SERIES, fallback.type)
    }

    @Test
    fun coldStartReadySeasonUsesExactDestinationWithoutInventedReadinessTimestamp() {
        val seriesId = UUID.randomUUID()
        val seasonId = UUID.randomUUID()
        val episodeIds = mapOf(1 to UUID.randomUUID(), 2 to UUID.randomUUID())
        val loaded =
            MediaRequest(
                id = 25,
                status = 5,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.AVAILABLE.status)),
                media = MediaInfo(id = 25, tmdbId = 25, status = SeerrAvailability.PARTIALLY_AVAILABLE.status),
            ).toSeerrRequestAcquisition().let { acquisition ->
                acquisition.copy(
                    request =
                        acquisition.request.copy(
                            seasonEpisodeCounts = mapOf(1 to 2),
                            seasonAvailableSinceEpochMillis = mapOf(1 to now.minusSeconds(2 * 24 * 60 * 60).toEpochMilli()),
                            jellyfinReadiness =
                                JellyfinAcquisitionReadiness(
                                    seriesItemId = seriesId,
                                    seasonItemIds = mapOf(1 to seasonId),
                                    episodeItemIds = mapOf(1 to episodeIds),
                                ),
                            jellyfinSeasonReadySinceEpochMillis = emptyMap(),
                        ),
                )
            }

        val item = listOf(loaded).toDownloadSections(now.toEpochMilli()).completed.single()
        val destination = item.destination("TV Series") as Destination.SeriesOverview

        assertEquals(seriesId, destination.itemId)
        assertEquals(BaseItemKind.SERIES, destination.type)
        assertEquals(seasonId, destination.seasonEpisode?.seasonId)
        assertEquals(1, destination.seasonEpisode?.seasonNumber)
    }

    @Test
    fun jellyfinReadySpecialsUsesSeasonZeroDestination() {
        val seriesId = UUID.randomUUID()
        val seasonId = UUID.randomUUID()
        val base =
            MediaRequest(
                id = 24,
                status = 5,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 0, status = SeerrAvailability.AVAILABLE.status)),
                media = MediaInfo(id = 24, tmdbId = 24, status = SeerrAvailability.PARTIALLY_AVAILABLE.status),
            ).toSeerrRequestAcquisition()
        val ready =
            base.copy(
                request =
                    base.request.copy(
                        seasonEpisodeCounts = mapOf(0 to 1),
                        jellyfinReadiness =
                            JellyfinAcquisitionReadiness(
                                seriesItemId = seriesId,
                                seasonItemIds = mapOf(0 to seasonId),
                                episodeItemIds = mapOf(0 to mapOf(1 to UUID.randomUUID())),
                            ),
                        jellyfinSeasonReadySinceEpochMillis = mapOf(0 to now.toEpochMilli()),
                    ),
            )
        val item =
            DownloadDisplayItem(
                key = "24_season_0",
                title = "TV Series",
                status = DownloadStatusLabel.AVAILABLE,
                progress = 1f,
                timing = null,
                completed = true,
                request = ready,
                seasonNumber = 0,
            )

        val destination = item.destination("TV Series") as Destination.SeriesOverview
        assertEquals(seriesId, destination.itemId)
        assertEquals(seasonId, destination.seasonEpisode?.seasonId)
        assertEquals(0, destination.seasonEpisode?.seasonNumber)
    }

    @Test
    fun timingIsClearedWhenCurrentQueueStatusStopsProgressing() {
        val paused =
            request(
                1,
                updatedAt = now.toString(),
                queue =
                    listOf(
                        DownloadStatus(
                            status = "paused",
                            propertySize = 100.0,
                            sizeLeft = 50.0,
                            timeLeft = "00:10:00",
                            estimatedCompletionTime = now.plusSeconds(600).toString(),
                        ),
                    ),
            )

        val item = listOf(paused).toDownloadSections(now.toEpochMilli()).processing.single()

        assertEquals(DownloadStatusLabel.QUEUED, item.status)
        assertEquals(null, item.timing)
        assertEquals(null, item.progress)
    }

    @Test
    fun completedUsesRollingSevenDaysWithoutCountCap() {
        val recent = (1..30).map { request(it, availableAt = now.minusSeconds(6 * 24 * 60 * 60).toString()) }
        val boundary = request(98, availableAt = now.minusSeconds(7 * 24 * 60 * 60).toString())
        val expired = request(99, availableAt = now.minusSeconds(7 * 24 * 60 * 60 + 1).toString())

        val sections = (recent + boundary + expired).toDownloadSections(now.toEpochMilli())

        assertEquals(31, sections.completed.size)
        assertTrue(sections.completed.none { it.request.request.requestId == 99 })
    }

    @Test
    fun tvCompletionUsesTheSameRollingBoundary() {
        val recent = tvRequest(1, now.minusSeconds(7 * 24 * 60 * 60).toEpochMilli())
        val expired = tvRequest(2, now.minusSeconds(7 * 24 * 60 * 60 + 1).toEpochMilli())

        val sections = listOf(recent, expired).toDownloadSections(now.toEpochMilli())

        assertEquals(listOf(1), sections.completed.map { it.request.request.requestId })
        assertEquals(null, sections.completed.single().title)
        assertEquals(1, sections.completed.single().seasonNumber)
    }

    @Test
    fun futureCompletionTimestampIsNotRecentlyCompleted() {
        val future = request(100, availableAt = now.plusSeconds(60).toString())

        val sections = listOf(future).toDownloadSections(now.toEpochMilli())

        assertTrue(sections.completed.isEmpty())
    }

    @Test
    fun seerrSeasonCompletionWhileWholeSeriesRemainsPartialIsFinishing() {
        val request =
            MediaRequest(
                id = 20,
                status = 5,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.AVAILABLE.status)),
                media = MediaInfo(id = 20, tmdbId = 20, status = SeerrAvailability.PARTIALLY_AVAILABLE.status),
            ).toSeerrRequestAcquisition().let { acquisition ->
                acquisition.copy(
                    request = acquisition.request.copy(seasonAvailableSinceEpochMillis = mapOf(1 to now.toEpochMilli())),
                )
            }

        val sections = listOf(request).toDownloadSections(now.toEpochMilli())

        assertEquals(SeerrAvailability.PARTIALLY_AVAILABLE, request.request.availability)
        assertEquals(DownloadStatusLabel.FINISHING, sections.processing.single().status)
        assertTrue(sections.completed.isEmpty())
        assertTrue(sections.active.isEmpty())
    }

    @Test
    fun partialJellyfinEpisodeReadinessIsFinishingNotQueued() {
        val request =
            MediaRequest(
                id = 21,
                status = 2,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.PROCESSING.status)),
                media = MediaInfo(id = 21, tmdbId = 21, status = SeerrAvailability.PARTIALLY_AVAILABLE.status),
            ).toSeerrRequestAcquisition().let { acquisition ->
                acquisition.copy(
                    request =
                        acquisition.request.copy(
                            seasonEpisodeCounts = mapOf(1 to 2),
                            jellyfinReadiness =
                                JellyfinAcquisitionReadiness(
                                    seriesItemId = UUID.randomUUID(),
                                    episodeItemIds = mapOf(1 to mapOf(1 to UUID.randomUUID())),
                                ),
                        ),
                )
            }

        val item = listOf(request).toDownloadSections(now.toEpochMilli()).active.single()

        assertEquals(DownloadStatusLabel.IN_PROGRESS, item.status)
        assertEquals("21_season_1", item.key)
    }

    @Test
    fun disappearedTvEpisodeEntriesRemainQueuedDuringBoundedGrace() {
        val request =
            MediaRequest(
                id = 22,
                status = 2,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.PROCESSING.status)),
                media =
                    MediaInfo(
                        id = 22,
                        status = SeerrAvailability.PARTIALLY_AVAILABLE.status,
                        downloadStatus =
                            listOf(
                                tvEpisode(1, 100.0, 0.0),
                                tvEpisode(2, 300.0, 150.0),
                            ),
                    ),
            ).toSeerrRequestAcquisition().let { acquisition ->
                val tv = acquisition.acquisition as SeerrAcquisitionState.Tv
                acquisition.copy(
                    request = acquisition.request.copy(seasonEpisodeCounts = mapOf(1 to 2)),
                    acquisition =
                        tv.copy(
                            seasons =
                                tv.seasons.map { season ->
                                    season.copy(
                                        aggregate =
                                            season.aggregate.copy(
                                                entries = season.aggregate.entries.map { it.copy(presentInQueue = false) },
                                            ),
                                    )
                                },
                        ),
                )
            }

        val item = listOf(request).toDownloadSections(now.toEpochMilli()).processing.single()

        assertEquals(DownloadStatusLabel.QUEUED, item.status)
        assertEquals(null, item.progress)
    }

    @Test
    fun jellyfinPlayableEpisodesNormalizeSeasonProgressEvenWhenNeverQueued() {
        val playable = (1..12).associateWith { UUID.randomUUID() }
        val request =
            MediaRequest(
                id = 580,
                status = 2,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.PROCESSING.status)),
                media = MediaInfo(id = 580, tmdbId = 1104, status = SeerrAvailability.PARTIALLY_AVAILABLE.status),
            ).toSeerrRequestAcquisition().let { acquisition ->
                acquisition.copy(
                    request =
                        acquisition.request.copy(
                            seasonEpisodeCounts = mapOf(1 to 13),
                            jellyfinReadiness =
                                JellyfinAcquisitionReadiness(
                                    seriesItemId = UUID.randomUUID(),
                                    episodeItemIds = mapOf(1 to playable),
                                ),
                        ),
                )
            }

        val item = listOf(request).toDownloadSections(now.toEpochMilli()).active.single()

        assertEquals(12f / 13f, item.progress!!, .00001f)
    }

    @Test
    fun seasonSixShapedFullSeasonAcquisitionUsesUnderlyingByteFraction() {
        val packEntries =
            (1..10).map { episodeNumber ->
                tvEpisode(episodeNumber, 1_000.0, 500.0).copy(
                    downloadId = "shared-season-pack",
                    title = "The.Good.Wife.S01.1080p.WEB-DL-playWEB",
                )
            }
        val request =
            MediaRequest(
                id = 581,
                status = 2,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.PROCESSING.status)),
                media = MediaInfo(id = 581, status = SeerrAvailability.PROCESSING.status, downloadStatus = packEntries),
            ).toSeerrRequestAcquisition().let { acquisition ->
                acquisition.copy(request = acquisition.request.copy(seasonEpisodeCounts = mapOf(1 to 22)))
            }

        val item = listOf(request).toDownloadSections(now.toEpochMilli()).active.single()

        assertEquals(.5f, item.progress!!, .00001f)
    }

    @Test
    fun episodeRangeAndPartialOrAmbiguousTitlesRemainEpisodeNormalized() {
        val titles =
            listOf(
                "The.Good.Wife.S01E01-E10.1080p.WEB-DL",
                "The.Good.Wife.S01.Part.1.1080p.WEB-DL",
                "The.Good.Wife.S02.1080p.WEB-DL",
                null,
            )

        titles.forEachIndexed { index, title ->
            val entries =
                (1..10).map { episodeNumber ->
                    tvEpisode(episodeNumber, 1_000.0, 500.0).copy(
                        downloadId = "shared-$index",
                        title = title,
                    )
                }
            val item = tvSeasonRequest(600 + index, entries, expectedEpisodeCount = 22)
                .let(::listOf)
                .toDownloadSections(now.toEpochMilli())
                .active
                .single()

            assertEquals((10.0 * .5 / 22.0).toFloat(), item.progress!!, .00001f)
        }
    }

    @Test
    fun fullSeasonProgressAndJellyfinReadinessAreMergedWithoutDoubleCounting() {
        val entries =
            (1..10).map { episodeNumber ->
                tvEpisode(episodeNumber, 1_000.0, 660.0).copy(
                    downloadId = "season-pack",
                    title = "The.Good.Wife.S01.1080p.WEB-DL",
                )
            }
        val fivePlayable = (1..5).associateWith { UUID.randomUUID() }
        val tenPlayable = (1..10).associateWith { UUID.randomUUID() }
        val base = tvSeasonRequest(605, entries, expectedEpisodeCount = 22)

        val packDominates = base.withPlayableEpisodes(1, fivePlayable)
            .let(::listOf).toDownloadSections(now.toEpochMilli()).active.single()
        val jellyfinDominates = base.withPlayableEpisodes(1, tenPlayable)
            .let(::listOf).toDownloadSections(now.toEpochMilli()).active.single()

        assertEquals(.34f, packDominates.progress!!, .00001f)
        assertEquals(10f / 22f, jellyfinDominates.progress!!, .00001f)
    }

    @Test
    fun completedFullSeasonAcquisitionFinishesUntilJellyfinIsReady() {
        val ledger = SeerrAcquisitionLedger()
        val entries =
            (1..10).map { episodeNumber ->
                tvEpisode(episodeNumber, 1_000.0, 0.0).copy(
                    downloadId = "completed-pack",
                    title = "The.Good.Wife.S01.1080p.WEB-DL",
                    status = "completed",
                    timeLeft = "00:00:00",
                )
            }
        ledger.reconcile(listOf(tvSeasonRequest(606, entries, expectedEpisodeCount = 22)))
        repeat(TV_PROGRESS_GRACE_POLLS + 2) {
            ledger.reconcile(listOf(tvSeasonRequest(606, emptyList(), expectedEpisodeCount = 22)))
        }
        val retained =
            ledger.reconcile(listOf(tvSeasonRequest(606, emptyList(), expectedEpisodeCount = 22))).single()
        val item = listOf(retained).toDownloadSections(now.toEpochMilli()).processing.single()

        assertEquals(DownloadStatusLabel.FINISHING, item.status)
        assertEquals(null, item.progress)
        assertTrue(!item.completed)
    }

    @Test
    fun fullSeasonGraceCanRegressToJellyfinConfirmedFloor() {
        val ledger = SeerrAcquisitionLedger()
        fun snapshot(queue: List<DownloadStatus>) = tvSeasonRequest(607, queue, expectedEpisodeCount = 22)
        val entries =
            (1..10).map { episodeNumber ->
                tvEpisode(episodeNumber, 1_000.0, 100.0).copy(
                    downloadId = "grace-pack",
                    title = "The.Good.Wife.S01.1080p.WEB-DL",
                )
            }
        ledger.reconcile(listOf(snapshot(entries)))
        val firstGap = ledger.reconcile(listOf(snapshot(emptyList()))).single()
        ledger.reconcile(listOf(snapshot(emptyList())))
        val expired = ledger.reconcile(listOf(snapshot(emptyList()))).single()
        val playable = (1..11).associateWith { UUID.randomUUID() }

        val gapItem = listOf(firstGap).toDownloadSections(now.toEpochMilli()).processing.single()
        assertEquals(DownloadStatusLabel.QUEUED, gapItem.status)
        assertEquals(null, gapItem.progress)
        assertEquals(
            .5f,
            listOf(expired.withPlayableEpisodes(1, playable)).toDownloadSections(now.toEpochMilli()).active.single().progress!!,
            .00001f,
        )
    }

    @Test
    fun fullSeasonTimingIsDeduplicatedFromSharedProjection() {
        val entries =
            (1..10).map { episodeNumber ->
                tvEpisode(episodeNumber, 1_000.0, 500.0).copy(
                    downloadId = "timed-pack",
                    title = "The.Good.Wife.S01.1080p.WEB-DL",
                    timeLeft = "00:20:00",
                    estimatedCompletionTime = now.plusSeconds(1_200).toString(),
                )
            }
        val item = tvSeasonRequest(608, entries, expectedEpisodeCount = 22)
            .let(::listOf).toDownloadSections(now.toEpochMilli()).active.single()

        assertEquals("00:20:00", item.timing?.remaining)
        assertTrue(item.timing?.eta != null)
    }

    @Test
    fun independentEpisodeTimingUsesLatestSeasonEstimate() {
        val entries =
            listOf(
                tvEpisode(1, 1_000.0, 500.0).copy(
                    timeLeft = "00:05:00",
                    estimatedCompletionTime = now.plusSeconds(30_000).toString(),
                    title = "The.Good.Wife.S01E01.1080p.WEB-DL",
                ),
                tvEpisode(2, 1_000.0, 1_000.0).copy(
                    timeLeft = "00:15:00",
                    estimatedCompletionTime = now.plusSeconds(20_000).toString(),
                    title = "The.Good.Wife.S01E02.1080p.WEB-DL",
                ),
            )
        val item = tvSeasonRequest(609, entries, expectedEpisodeCount = 2)
            .let(::listOf).toDownloadSections(now.toEpochMilli()).active.single()

        assertEquals("00:15:00", item.timing?.remaining)
        assertTrue(item.timing?.eta != null)
    }

    @Test
    fun conflictingRawEtaIsReplacedByDeviceTimePlusDuration() {
        val rawEta = now.plusSeconds(30_000)
        val entry =
            tvEpisode(1, 1_000.0, 500.0).copy(
                timeLeft = "00:13:24",
                estimatedCompletionTime = rawEta.toString(),
                title = "The.Good.Wife.S01E01.1080p.WEB-DL",
            )
        val item = tvSeasonRequest(610, listOf(entry), expectedEpisodeCount = 1)
            .let(::listOf).toDownloadSections(now.toEpochMilli()).active.single()
        val derivedEta =
            now.plusSeconds(13 * 60 + 24)
                .atZone(ZoneId.systemDefault())
                .format(DateTimeFormatter.ofPattern("HH:mm"))

        assertEquals("00:13:24", item.timing?.remaining)
        assertEquals(derivedEta, item.timing?.eta)
    }

    @Test
    fun rawEtaIsUsedOnlyWhenNoPositiveTvDurationExists() {
        val rawEta = now.plusSeconds(1_800)
        val entry =
            tvEpisode(1, 1_000.0, 500.0).copy(
                timeLeft = null,
                estimatedCompletionTime = rawEta.toString(),
                title = "The.Good.Wife.S01E01.1080p.WEB-DL",
            )
        val item = tvSeasonRequest(611, listOf(entry), expectedEpisodeCount = 1)
            .let(::listOf).toDownloadSections(now.toEpochMilli()).active.single()
        val expected = rawEta.atZone(ZoneId.systemDefault()).format(DateTimeFormatter.ofPattern("HH:mm"))

        assertEquals(null, item.timing?.remaining)
        assertEquals(expected, item.timing?.eta)
    }

    @Test
    fun failedZeroRemainingEntryContributesNoTvProgress() {
        val request =
            MediaRequest(
                id = 582,
                status = 2,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.PROCESSING.status)),
                media =
                    MediaInfo(
                        id = 582,
                        status = SeerrAvailability.PROCESSING.status,
                        downloadStatus = listOf(tvEpisode(1, 100.0, 0.0).copy(status = "failed")),
                    ),
            ).toSeerrRequestAcquisition().let { acquisition ->
                acquisition.copy(request = acquisition.request.copy(seasonEpisodeCounts = mapOf(1 to 1)))
            }

        val item = listOf(request).toDownloadSections(now.toEpochMilli()).processing.single()

        assertEquals(null, item.progress)
        assertEquals(DownloadStatusLabel.QUEUED, item.status)
    }

    @Test
    fun missingExpectedEpisodeCountProducesIndeterminateTvProgress() {
        val request =
            MediaRequest(
                id = 583,
                status = 2,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.PROCESSING.status)),
                media =
                    MediaInfo(
                        id = 583,
                        status = SeerrAvailability.PROCESSING.status,
                        downloadStatus = listOf(tvEpisode(1, 100.0, 50.0)),
                    ),
            ).toSeerrRequestAcquisition()

        val item = listOf(request).toDownloadSections(now.toEpochMilli()).processing.single()

        assertEquals(DownloadStatusLabel.QUEUED, item.status)
        assertEquals(null, item.progress)
    }

    @Test
    fun tvProvisionalProgressExpiresAfterBoundedImportGrace() {
        val ledger = SeerrAcquisitionLedger()
        fun snapshot(queue: List<DownloadStatus>) =
            MediaRequest(
                id = 584,
                status = 2,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.PROCESSING.status)),
                media = MediaInfo(id = 584, status = SeerrAvailability.PROCESSING.status, downloadStatus = queue),
            ).toSeerrRequestAcquisition().let { acquisition ->
                acquisition.copy(request = acquisition.request.copy(seasonEpisodeCounts = mapOf(1 to 1)))
            }

        ledger.reconcile(listOf(snapshot(listOf(tvEpisode(1, 100.0, 25.0)))))
        val firstGap = ledger.reconcile(listOf(snapshot(emptyList()))).single()
        val secondGap = ledger.reconcile(listOf(snapshot(emptyList()))).single()
        val expired = ledger.reconcile(listOf(snapshot(emptyList()))).single()

        assertEquals(
            DownloadStatusLabel.QUEUED,
            listOf(firstGap).toDownloadSections(now.toEpochMilli()).processing.single().status,
        )
        assertEquals(
            DownloadStatusLabel.QUEUED,
            listOf(secondGap).toDownloadSections(now.toEpochMilli()).processing.single().status,
        )
        assertEquals(null, listOf(expired).toDownloadSections(now.toEpochMilli()).active.single().progress)
    }

    @Test
    fun explicitlyCompletedEpisodeSurvivesImportGrace() {
        val ledger = SeerrAcquisitionLedger()
        fun snapshot(queue: List<DownloadStatus>) = tvSeasonRequest(1584, queue, expectedEpisodeCount = 2)

        ledger.reconcile(listOf(snapshot(listOf(tvEpisode(1, 100.0, 0.0)))))
        repeat(TV_PROGRESS_GRACE_POLLS + 2) { ledger.reconcile(listOf(snapshot(emptyList()))) }
        val retained = ledger.reconcile(listOf(snapshot(emptyList()))).single()
        val item = listOf(retained).toDownloadSections(now.toEpochMilli()).processing.single()

        assertEquals(DownloadStatusLabel.QUEUED, item.status)
        assertEquals(null, item.progress)
        val entry = (retained.acquisition as SeerrAcquisitionState.Tv).seasons.single().aggregate.entries.single()
        assertTrue(entry.observedSuccessfulTransferCompletion)
    }

    @Test
    fun allExplicitlyCompletedEpisodesRemainFinishingUntilJellyfinReady() {
        val ledger = SeerrAcquisitionLedger()
        fun snapshot(queue: List<DownloadStatus>) = tvSeasonRequest(1585, queue, expectedEpisodeCount = 2)

        ledger.reconcile(
            listOf(snapshot(listOf(tvEpisode(1, 100.0, 0.0), tvEpisode(2, 100.0, 0.0)))),
        )
        repeat(TV_PROGRESS_GRACE_POLLS + 2) { ledger.reconcile(listOf(snapshot(emptyList()))) }
        val retained = ledger.reconcile(listOf(snapshot(emptyList()))).single()
        val item = listOf(retained).toDownloadSections(now.toEpochMilli()).processing.single()

        assertEquals(DownloadStatusLabel.FINISHING, item.status)
        assertEquals(null, item.progress)
    }

    @Test
    fun jellyfinPlayableEpisodeSupersedesOnlyItsCompletedProgressContribution() {
        val ledger = SeerrAcquisitionLedger()
        val initial = tvSeasonRequest(
            1586,
            listOf(tvEpisode(1, 100.0, 0.0), tvEpisode(2, 100.0, 0.0)),
            expectedEpisodeCount = 3,
        )
        ledger.reconcile(listOf(initial))
        val withOnePlayable =
            tvSeasonRequest(1586, emptyList(), expectedEpisodeCount = 3)
                .withPlayableEpisodes(1, mapOf(1 to UUID.randomUUID()))

        val reconciled = ledger.reconcile(listOf(withOnePlayable)).single()
        val item = listOf(reconciled).toDownloadSections(now.toEpochMilli()).processing.single()
        val entries = (reconciled.acquisition as SeerrAcquisitionState.Tv).seasons.single().aggregate.entries

        assertEquals(DownloadStatusLabel.QUEUED, item.status)
        assertEquals(null, item.progress)
        assertEquals(listOf(1, 2), entries.mapNotNull { it.episode?.episodeNumber }.sorted())
        assertTrue(entries.all { it.observedSuccessfulTransferCompletion })
    }

    @Test
    fun replacementDownloadCanLegitimatelyLowerTvProgress() {
        val ledger = SeerrAcquisitionLedger()
        fun snapshot(downloadId: String, sizeLeft: Double) =
            MediaRequest(
                id = 585,
                status = 2,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.PROCESSING.status)),
                media =
                    MediaInfo(
                        id = 585,
                        status = SeerrAvailability.PROCESSING.status,
                        downloadStatus = listOf(tvEpisode(1, 100.0, sizeLeft).copy(downloadId = downloadId)),
                    ),
            ).toSeerrRequestAcquisition().let { acquisition ->
                acquisition.copy(request = acquisition.request.copy(seasonEpisodeCounts = mapOf(1 to 1)))
            }

        val original = ledger.reconcile(listOf(snapshot("original", 10.0))).single()
        val replacement = ledger.reconcile(listOf(snapshot("replacement", 90.0))).single()

        assertEquals(.9f, listOf(original).toDownloadSections(now.toEpochMilli()).active.single().progress!!, .00001f)
        assertEquals(.1f, listOf(replacement).toDownloadSections(now.toEpochMilli()).active.single().progress!!, .00001f)
        val entries = (replacement.acquisition as SeerrAcquisitionState.Tv).seasons.single().aggregate.entries
        assertEquals(listOf("replacement"), entries.map { it.downloadId })
    }

    @Test
    fun jellyfinReadinessOverridesProvisionalProgressDuringImportGrace() {
        val ledger = SeerrAcquisitionLedger()
        fun snapshot(queue: List<DownloadStatus>) =
            MediaRequest(
                id = 586,
                status = 2,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.PROCESSING.status)),
                media = MediaInfo(id = 586, status = SeerrAvailability.PROCESSING.status, downloadStatus = queue),
            ).toSeerrRequestAcquisition().let { acquisition ->
                acquisition.copy(request = acquisition.request.copy(seasonEpisodeCounts = mapOf(1 to 2)))
            }

        ledger.reconcile(listOf(snapshot(listOf(tvEpisode(1, 100.0, 50.0)))))
        val gap = ledger.reconcile(listOf(snapshot(emptyList()))).single()
        val readyEpisode =
            gap.copy(
                request =
                    gap.request.copy(
                        jellyfinReadiness =
                            JellyfinAcquisitionReadiness(
                                seriesItemId = UUID.randomUUID(),
                                episodeItemIds = mapOf(1 to mapOf(1 to UUID.randomUUID())),
                            ),
                    ),
            )

        val item = listOf(readyEpisode).toDownloadSections(now.toEpochMilli()).processing.single()
        assertEquals(DownloadStatusLabel.QUEUED, item.status)
        assertEquals(null, item.progress)
    }

    @Test
    fun sameSeriesRequestsKeepSeasonFourQueueAndTimingOutOfSeasonThree() {
        val ledger = SeerrAcquisitionLedger()
        val seasonFourEntry =
            tvEpisode(1, 100.0, 50.0, seasonNumber = 4).copy(
                downloadId = "season-four",
                timeLeft = "00:10:00",
                estimatedCompletionTime = now.plusSeconds(600).toString(),
            )
        fun requestForSeason(
            requestId: Int,
            seasonNumber: Int,
            queue: List<DownloadStatus>,
        ) = MediaRequest(
            id = requestId,
            status = 2,
            type = "tv",
            createdAt = now.toString(),
            updatedAt = now.toString(),
            seasons = listOf(Season(seasonNumber = seasonNumber, status = SeerrAvailability.PROCESSING.status)),
            media =
                MediaInfo(
                    id = 1435,
                    tmdbId = 1435,
                    status = SeerrAvailability.PARTIALLY_AVAILABLE.status,
                    downloadStatus = queue,
                ),
        ).toSeerrRequestAcquisition().let { acquisition ->
            acquisition.copy(request = acquisition.request.copy(seasonEpisodeCounts = mapOf(seasonNumber to 22)))
        }

        val reconciled =
            ledger.reconcile(
                listOf(
                    requestForSeason(581, 4, listOf(seasonFourEntry)),
                    // Seerr repeats the same series-level queue on historical requests.
                    requestForSeason(579, 3, listOf(seasonFourEntry)),
                ),
            )
        val sections = reconciled.toDownloadSections(now.toEpochMilli())
        val seasonFour = sections.active.single { it.key == "581_season_4" }
        val seasonThree = sections.processing.single { it.key == "579_season_3" }

        assertEquals(.5f / 22f, seasonFour.progress!!, .00001f)
        assertEquals("00:10:00", seasonFour.timing?.remaining)
        assertTrue(seasonFour.timing?.eta != null)
        assertEquals(DownloadStatusLabel.IN_PROGRESS, seasonFour.status)
        assertEquals(null, seasonThree.progress)
        assertEquals(null, seasonThree.timing)
        assertEquals(DownloadStatusLabel.QUEUED, seasonThree.status)

        val retained =
            ledger.reconcile(
                listOf(
                    requestForSeason(581, 4, emptyList()),
                    requestForSeason(579, 3, emptyList()),
                ),
            )
        val seasonFourTarget = retained.single { it.request.requestId == 581 }.toTvSeasonTargets().single()
        val seasonThreeTarget = retained.single { it.request.requestId == 579 }.toTvSeasonTargets().single()
        assertEquals(listOf("season-four"), seasonFourTarget.aggregate?.entries?.map { it.downloadId })
        assertTrue(seasonFourTarget.aggregate?.entries?.single()?.presentInQueue == false)
        assertTrue(seasonThreeTarget.aggregate?.entries.orEmpty().isEmpty())
    }

    @Test
    fun knownOtherSeasonEntryCannotUseSingleSeasonUnassignedFallback() {
        val mapped =
            MediaRequest(
                id = 587,
                status = 2,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 3, status = SeerrAvailability.PROCESSING.status)),
                media =
                    MediaInfo(
                        id = 587,
                        status = SeerrAvailability.PROCESSING.status,
                        downloadStatus = listOf(tvEpisode(1, 100.0, 50.0, seasonNumber = 4)),
                    ),
            ).toSeerrRequestAcquisition()
        val seasonFourEntry =
            MediaRequest(
                id = 588,
                status = 2,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 4)),
                media = MediaInfo(id = 588, downloadStatus = listOf(tvEpisode(1, 100.0, 50.0, seasonNumber = 4))),
            ).toSeerrRequestAcquisition().let {
                (it.acquisition as SeerrAcquisitionState.Tv).seasons.single().aggregate.entries.single()
            }
        val contaminated =
            mapped.copy(
                request = mapped.request.copy(seasonEpisodeCounts = mapOf(3 to 22)),
                acquisition =
                    SeerrAcquisitionState.Tv(
                        seasons = emptyList(),
                        unassignedEntries = listOf(seasonFourEntry),
                    ),
            )

        val target = contaminated.toTvSeasonTargets().single()

        assertTrue(target.aggregate?.entries.orEmpty().isEmpty())
        assertEquals(0.0, target.aggregate?.progress?.fraction ?: -1.0, 0.0)
        assertEquals(TvSeasonLifecycle.QUEUED, target.lifecycle)
    }

    @Test
    fun genuinelySeasonlessEntryStillUsesUnambiguousSingleSeasonFallback() {
        val request =
            MediaRequest(
                id = 589,
                status = 2,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 3, status = SeerrAvailability.PROCESSING.status)),
                media =
                    MediaInfo(
                        id = 589,
                        status = SeerrAvailability.PROCESSING.status,
                        downloadStatus =
                            listOf(
                                DownloadStatus(
                                    downloadId = "seasonless",
                                    status = "downloading",
                                    propertySize = 100.0,
                                    sizeLeft = 50.0,
                                    timeLeft = "00:05:00",
                                    estimatedCompletionTime = now.plusSeconds(300).toString(),
                                ),
                            ),
                    ),
            ).toSeerrRequestAcquisition().let { acquisition ->
                acquisition.copy(request = acquisition.request.copy(seasonEpisodeCounts = mapOf(3 to 22)))
            }

        val target = request.toTvSeasonTargets().single()

        assertEquals(listOf("seasonless"), target.aggregate?.entries?.map { it.downloadId })
        assertEquals(TvSeasonLifecycle.IN_PROGRESS, target.lifecycle)
    }

    @Test
    fun authoritativeSeasonWithoutRequestSeasonMetadataUsesExactTvRow() {
        val request =
            tvSeasonRequest(
                id = 590,
                queue = listOf(tvEpisode(1, 100.0, 50.0, seasonNumber = 3)),
                expectedEpisodeCount = 1,
                seasonNumber = 3,
            ).let { acquisition ->
                acquisition.copy(request = acquisition.request.copy(requestedSeasonNumbers = emptySet()))
            }

        val target = request.toTvSeasonTargets().single()
        val sections = listOf(request).toDownloadSections(now.toEpochMilli())

        assertEquals(3, target.seasonNumber)
        assertEquals(TvSeasonLifecycle.IN_PROGRESS, target.lifecycle)
        assertEquals(.5, target.acquisitionProjection.displayedFraction, .0001)
        assertEquals(listOf("590_season_3"), sections.active.map { it.key })
        assertTrue((sections.active + sections.processing + sections.completed).none { it.key == "590_movie" })
    }

    @Test
    fun trulyUnassignedTvEvidenceUsesGenericTvFallbackUntilSeasonIsAssigned() {
        val assigned =
            tvSeasonRequest(
                id = 591,
                queue = listOf(tvEpisode(1, 100.0, 50.0, seasonNumber = 3)),
                expectedEpisodeCount = 1,
                seasonNumber = 3,
            ).let { acquisition ->
                acquisition.copy(request = acquisition.request.copy(requestedSeasonNumbers = emptySet()))
            }
        val assignedState = assigned.acquisition as SeerrAcquisitionState.Tv
        val unassigned =
            assigned.copy(
                request =
                    assigned.request.copy(
                        requestedSeasonNumbers = emptySet(),
                        seasonEpisodeCounts = emptyMap(),
                    ),
                acquisition =
                    SeerrAcquisitionState.Tv(
                        seasons = emptyList(),
                        unassignedEntries =
                            assignedState.seasons.single().aggregate.entries.map { it.copy(episode = null) },
                    ),
            )

        val unresolvedSections = listOf(unassigned).toDownloadSections(now.toEpochMilli())
        val resolvedSections = listOf(assigned).toDownloadSections(now.toEpochMilli())

        assertTrue(unassigned.toTvSeasonTargets().isEmpty())
        assertEquals(listOf("591_tv"), unresolvedSections.active.map { it.key })
        assertTrue((unresolvedSections.active + unresolvedSections.processing).none { it.key == "591_movie" })
        assertEquals(listOf("591_season_3"), resolvedSections.active.map { it.key })
        assertTrue((resolvedSections.active + resolvedSections.processing).none { it.key == "591_tv" })
    }

    @Test
    fun tvRequestWithOneSeasonProducesOnlyOneSeasonRow() {
        val request =
            MediaRequest(
                id = 30,
                status = 2,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 2, status = SeerrAvailability.PROCESSING.status)),
                media =
                    MediaInfo(
                        id = 30,
                        tmdbId = 30,
                        status = SeerrAvailability.PARTIALLY_AVAILABLE.status,
                        downloadStatus =
                            listOf(
                                tvEpisode(1, 100.0, 50.0, seasonNumber = 2),
                                DownloadStatus(
                                    externalId = 30,
                                    downloadId = "series-level",
                                    status = "downloading",
                                    propertySize = 100.0,
                                    sizeLeft = 50.0,
                                ),
                            ),
                    ),
            ).toSeerrRequestAcquisition()

        val sections = listOf(request).toDownloadSections(now.toEpochMilli())
        val rows = sections.active + sections.processing + sections.completed

        assertEquals(listOf("30_season_2"), rows.map { it.key })
        assertEquals(2, rows.single().seasonNumber)
    }

    @Test
    fun tvRequestWithMultipleSeasonsProducesEachSeasonOnce() {
        val request =
            MediaRequest(
                id = 31,
                status = 2,
                type = "tv",
                seasons =
                    listOf(
                        Season(seasonNumber = 1, status = SeerrAvailability.PROCESSING.status),
                        Season(seasonNumber = 2, status = SeerrAvailability.PROCESSING.status),
                    ),
                media =
                    MediaInfo(
                        id = 31,
                        tmdbId = 31,
                        status = SeerrAvailability.PARTIALLY_AVAILABLE.status,
                        downloadStatus =
                            listOf(
                                tvEpisode(1, 100.0, 50.0, seasonNumber = 1),
                                tvEpisode(1, 200.0, 100.0, seasonNumber = 2),
                                DownloadStatus(
                                    externalId = 31,
                                    downloadId = "series-level",
                                    status = "downloading",
                                    propertySize = 100.0,
                                    sizeLeft = 50.0,
                                ),
                            ),
                    ),
            ).toSeerrRequestAcquisition()

        val sections = listOf(request).toDownloadSections(now.toEpochMilli())
        val rows = sections.active + sections.processing + sections.completed

        assertEquals(listOf("31_season_1", "31_season_2"), rows.map { it.key }.sorted())
        assertEquals(listOf(1, 2), rows.mapNotNull { it.seasonNumber }.sorted())
    }

    @Test
    fun readyTvSeasonWithCurrentFinishingWorkStaysOperational() {
        val request =
            MediaRequest(
                id = 572,
                status = 5,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.AVAILABLE.status)),
                media =
                    MediaInfo(
                        id = 572,
                        tmdbId = 572,
                        status = SeerrAvailability.PARTIALLY_AVAILABLE.status,
                        downloadStatus = listOf(tvEpisode(1, 100.0, 0.0)),
                    ),
            ).toSeerrRequestAcquisition().let { acquisition ->
                acquisition.copy(
                    request =
                        acquisition.request.copy(
                            seasonAvailableSinceEpochMillis = mapOf(1 to now.toEpochMilli()),
                            jellyfinReadiness =
                                JellyfinAcquisitionReadiness(
                                    seriesItemId = UUID.randomUUID(),
                                    episodeItemIds = mapOf(1 to mapOf(1 to UUID.randomUUID())),
                                ),
                            jellyfinSeasonReadySinceEpochMillis = mapOf(1 to now.toEpochMilli()),
                        ),
                )
            }

        val sections = listOf(request).toDownloadSections(now.toEpochMilli())
        val rows = sections.active + sections.processing + sections.completed

        assertTrue(sections.active.isEmpty())
        assertEquals(DownloadStatusLabel.FINISHING, sections.processing.single().status)
        assertEquals(null, sections.processing.single().progress)
        assertEquals(listOf("572_season_1"), rows.map { it.key })
    }

    @Test
    fun tvSeasonTransitionsBetweenSectionsWithOneStableKey() {
        val seriesId = UUID.randomUUID()
        val active =
            MediaRequest(
                id = 573,
                status = 2,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.PROCESSING.status)),
                media =
                    MediaInfo(
                        id = 573,
                        tmdbId = 573,
                        status = SeerrAvailability.PARTIALLY_AVAILABLE.status,
                        downloadStatus = listOf(tvEpisode(1, 100.0, 50.0)),
                    ),
            ).toSeerrRequestAcquisition()
                .let { acquisition ->
                    acquisition.copy(
                        request = acquisition.request.copy(seasonEpisodeCounts = mapOf(1 to 1)),
                    )
                }
        val finishing =
            active.copy(
                acquisition =
                    (active.acquisition as SeerrAcquisitionState.Tv).let { tv ->
                        tv.copy(
                            seasons =
                                tv.seasons.map { season ->
                                    season.copy(
                                        aggregate =
                                            season.aggregate.copy(
                                                entries = season.aggregate.entries.map { it.copy(presentInQueue = false) },
                                            ),
                                    )
                                },
                        )
                    },
            )
        val completed =
            finishing.copy(
                request =
                    finishing.request.copy(
                        jellyfinReadiness =
                            JellyfinAcquisitionReadiness(
                                seriesItemId = seriesId,
                                episodeItemIds = mapOf(1 to mapOf(1 to UUID.randomUUID())),
                            ),
                        jellyfinSeasonReadySinceEpochMillis = mapOf(1 to now.toEpochMilli()),
                    ),
                acquisition =
                    (finishing.acquisition as SeerrAcquisitionState.Tv).let { tv ->
                        tv.copy(
                            seasons =
                                tv.seasons.map { season ->
                                    season.copy(
                                        aggregate =
                                            season.aggregate.copy(
                                                entries = season.aggregate.entries.map {
                                                    it.copy(absentPollCount = TV_PROGRESS_GRACE_POLLS + 1)
                                                },
                                            ),
                                    )
                                },
                        )
                    },
            )

        val activeSections = listOf(active).toDownloadSections(now.toEpochMilli())
        val finishingSections = listOf(finishing).toDownloadSections(now.toEpochMilli())
        val completedSections = listOf(completed).toDownloadSections(now.toEpochMilli())

        assertEquals(listOf("573_season_1"), activeSections.active.map { it.key })
        assertEquals(listOf("573_season_1"), finishingSections.processing.map { it.key })
        assertEquals(DownloadStatusLabel.QUEUED, finishingSections.processing.single().status)
        assertEquals(listOf("573_season_1"), completedSections.completed.map { it.key })
        assertTrue(finishingSections.processing.single().destination("TV Series") is Destination.DiscoveredItem)
        val completedDestination =
            completedSections.completed.single().destination("TV Series") as Destination.MediaItem
        assertEquals(seriesId, completedDestination.itemId)
        assertEquals(BaseItemKind.SERIES, completedDestination.type)
        assertEquals(1, activeSections.active.size + activeSections.processing.size + activeSections.completed.size)
        assertEquals(1, finishingSections.active.size + finishingSections.processing.size + finishingSections.completed.size)
        assertEquals(1, completedSections.active.size + completedSections.processing.size + completedSections.completed.size)
        assertTrue(completedSections.active.isEmpty())
        assertTrue(completedSections.processing.isEmpty())
    }

    @Test
    fun sequentialEpisodeChurnRemainsInProgressAndProgressCanIncrease() {
        fun snapshot(secondEpisodeSizeLeft: Double): SeerrRequestAcquisition {
            val acquisition =
                MediaRequest(
                    id = 577,
                    status = 2,
                    type = "tv",
                    seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.PROCESSING.status)),
                    media =
                        MediaInfo(
                            id = 577,
                            status = SeerrAvailability.PARTIALLY_AVAILABLE.status,
                            downloadStatus =
                                listOf(
                                    tvEpisode(1, 100.0, 0.0),
                                    tvEpisode(2, 100.0, secondEpisodeSizeLeft),
                                ),
                        ),
                ).toSeerrRequestAcquisition()
            val tv = acquisition.acquisition as SeerrAcquisitionState.Tv
            return acquisition.copy(
                request = acquisition.request.copy(seasonEpisodeCounts = mapOf(1 to 3)),
                acquisition =
                    tv.copy(
                        seasons =
                            tv.seasons.map { season ->
                                season.copy(
                                    aggregate =
                                        season.aggregate.copy(
                                            entries =
                                                season.aggregate.entries.map { entry ->
                                                    if (entry.episode?.episodeNumber == 1) {
                                                        entry.copy(presentInQueue = false)
                                                    } else {
                                                        entry
                                                    }
                                                },
                                        ),
                                )
                            },
                    ),
            )
        }

        val earlier = listOf(snapshot(98.0)).toDownloadSections(now.toEpochMilli()).active.single()
        val later = listOf(snapshot(12.0)).toDownloadSections(now.toEpochMilli()).active.single()

        assertEquals(DownloadStatusLabel.IN_PROGRESS, earlier.status)
        assertEquals(DownloadStatusLabel.IN_PROGRESS, later.status)
        assertTrue(later.progress!! > earlier.progress!!)
    }

    @Test
    fun temporaryEmptyQueueAfterActivityIsInProgressUntilExpectedEpisodesAreCovered() {
        val request =
            MediaRequest(
                id = 578,
                status = 2,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.PROCESSING.status)),
                media =
                    MediaInfo(
                        id = 578,
                        status = SeerrAvailability.PARTIALLY_AVAILABLE.status,
                        downloadStatus = listOf(tvEpisode(1, 100.0, 0.0)),
                    ),
            ).toSeerrRequestAcquisition().let { acquisition ->
                val tv = acquisition.acquisition as SeerrAcquisitionState.Tv
                acquisition.copy(
                    request = acquisition.request.copy(seasonEpisodeCounts = mapOf(1 to 2)),
                    acquisition =
                        tv.copy(
                            seasons =
                                tv.seasons.map { season ->
                                    season.copy(
                                        aggregate =
                                            season.aggregate.copy(
                                                entries = season.aggregate.entries.map { it.copy(presentInQueue = false) },
                                            ),
                                    )
                                },
                        ),
                )
            }

        val sections = listOf(request).toDownloadSections(now.toEpochMilli())

        assertEquals(DownloadStatusLabel.QUEUED, sections.processing.single().status)
        assertEquals(null, sections.processing.single().progress)
        assertTrue(sections.active.isEmpty())
    }

    @Test
    fun allExpectedEpisodeEvidenceCanEnterFinishingAfterQueueClears() {
        val request =
            MediaRequest(
                id = 579,
                status = 2,
                type = "tv",
                seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.PROCESSING.status)),
                media =
                    MediaInfo(
                        id = 579,
                        status = SeerrAvailability.PARTIALLY_AVAILABLE.status,
                        downloadStatus =
                            listOf(
                                tvEpisode(1, 100.0, 0.0),
                                tvEpisode(2, 100.0, 0.0),
                            ),
                    ),
            ).toSeerrRequestAcquisition().let { acquisition ->
                val tv = acquisition.acquisition as SeerrAcquisitionState.Tv
                acquisition.copy(
                    request = acquisition.request.copy(seasonEpisodeCounts = mapOf(1 to 2)),
                    acquisition =
                        tv.copy(
                            seasons =
                                tv.seasons.map { season ->
                                    season.copy(
                                        aggregate =
                                            season.aggregate.copy(
                                                entries = season.aggregate.entries.map { it.copy(presentInQueue = false) },
                                            ),
                                    )
                                },
                        ),
                )
            }

        val sections = listOf(request).toDownloadSections(now.toEpochMilli())

        assertEquals(DownloadStatusLabel.FINISHING, sections.processing.single().status)
        assertTrue(sections.active.isEmpty())
    }

    @Test
    fun refreshFocusKeepsStableItemWhenItMovesSections() {
        val finishing =
            listOf(
                MediaRequest(
                    id = 574,
                    status = 2,
                    type = "tv",
                    seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.PROCESSING.status)),
                    media =
                        MediaInfo(
                            id = 574,
                            status = SeerrAvailability.PARTIALLY_AVAILABLE.status,
                            downloadStatus = listOf(tvEpisode(1, 100.0, 0.0)),
                        ),
                ).toSeerrRequestAcquisition(),
            ).toDownloadSections(now.toEpochMilli()).processing.single()
        val completed = finishing.copy(status = DownloadStatusLabel.AVAILABLE, completed = true)

        assertEquals(completed, refreshFocusTarget(listOf(completed), finishing.key, 0))
    }

    @Test
    fun refreshFocusChoosesNearestRowWhenFocusedItemDisappears() {
        val requests =
            listOf(
                request(575, updatedAt = now.toString()),
                request(576, updatedAt = now.toString()),
            ).toDownloadSections(now.toEpochMilli()).processing

        assertEquals(requests[1], refreshFocusTarget(listOf(requests[1]), requests[0].key, 1))
        assertEquals(null, refreshFocusTarget(emptyList(), requests[0].key, 0))
    }

    @Test
    fun requesterIdentityIsPreserved() {
        val request = request(1, updatedAt = now.toString())

        assertEquals(42, request.request.requestedById)
        assertEquals("alex", request.request.requestedByName)
    }

    private fun request(
        id: Int,
        updatedAt: String? = null,
        availableAt: String? = null,
        queue: List<DownloadStatus>? = null,
    ) = MediaRequest(
        id = id,
        status = 2,
        type = "movie",
        createdAt = updatedAt,
        updatedAt = updatedAt,
        requestedBy = RequestUser(id = 42, username = "alex"),
        media =
            MediaInfo(
                id = id,
                tmdbId = id,
                status = if (availableAt == null) SeerrAvailability.PROCESSING.status else SeerrAvailability.AVAILABLE.status,
                updatedAt = availableAt,
                downloadStatus = queue,
            ),
    ).toSeerrRequestAcquisition().let { acquisition ->
        acquisition.copy(
            request =
                acquisition.request.copy(
                    availableSinceEpochMillis = availableAt?.let(Instant::parse)?.toEpochMilli(),
                    jellyfinReadiness =
                        JellyfinAcquisitionReadiness(
                            movieItemId = availableAt?.let { UUID.randomUUID() },
                        ),
                    jellyfinReadySinceEpochMillis = availableAt?.let(Instant::parse)?.toEpochMilli(),
                ),
        )
    }

    private fun tvRequest(
        id: Int,
        completedAt: Long,
    ) = MediaRequest(
        id = id,
        status = 2,
        type = "tv",
        seasons = listOf(Season(seasonNumber = 1)),
        media =
            MediaInfo(
                id = id,
                tmdbId = id,
                status = SeerrAvailability.PARTIALLY_AVAILABLE.status,
                seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.AVAILABLE.status)),
            ),
    ).toSeerrRequestAcquisition().let { acquisition ->
        acquisition.copy(
            request =
                acquisition.request.copy(
                    seasonEpisodeCounts = mapOf(1 to 1),
                    seasonAvailableSinceEpochMillis = mapOf(1 to completedAt),
                    jellyfinReadiness =
                        JellyfinAcquisitionReadiness(
                            seriesItemId = UUID.randomUUID(),
                            episodeItemIds = mapOf(1 to mapOf(1 to UUID.randomUUID())),
                        ),
                    jellyfinSeasonReadySinceEpochMillis = mapOf(1 to completedAt),
                ),
        )
    }

    private fun tvSeasonRequest(
        id: Int,
        queue: List<DownloadStatus>,
        expectedEpisodeCount: Int,
        seasonNumber: Int = 1,
    ) = MediaRequest(
        id = id,
        status = 2,
        type = "tv",
        seasons = listOf(Season(seasonNumber = seasonNumber, status = SeerrAvailability.PROCESSING.status)),
        media =
            MediaInfo(
                id = id,
                tmdbId = id,
                status = SeerrAvailability.PROCESSING.status,
                downloadStatus = queue,
            ),
    ).toSeerrRequestAcquisition().let { acquisition ->
        acquisition.copy(
            request =
                acquisition.request.copy(
                    seasonEpisodeCounts = mapOf(seasonNumber to expectedEpisodeCount),
                ),
        )
    }

    private fun SeerrRequestAcquisition.withPlayableEpisodes(
        seasonNumber: Int,
        episodes: Map<Int, UUID>,
    ): SeerrRequestAcquisition =
        copy(
            request =
                request.copy(
                    jellyfinReadiness =
                        JellyfinAcquisitionReadiness(
                            seriesItemId = UUID.randomUUID(),
                            episodeItemIds = mapOf(seasonNumber to episodes),
                        ),
                ),
        )

    private fun tvEpisode(
        episodeNumber: Int,
        size: Double,
        sizeLeft: Double,
        seasonNumber: Int = 1,
    ) = DownloadStatus(
        externalId = 20,
        downloadId = "episode-$episodeNumber",
        status = "downloading",
        propertySize = size,
        sizeLeft = sizeLeft,
        episode =
            DownloadStatusEpisode(
                seriesId = 20,
                seasonNumber = seasonNumber,
                episodeNumber = episodeNumber,
                title = "Episode $episodeNumber",
                hasFile = false,
            ),
    )
}
