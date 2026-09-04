package com.github.damontecres.wholphin.data.model

import com.github.damontecres.wholphin.api.seerr.model.DownloadStatus
import com.github.damontecres.wholphin.api.seerr.model.DownloadStatusEpisode
import com.github.damontecres.wholphin.api.seerr.model.MediaInfo
import com.github.damontecres.wholphin.api.seerr.model.MediaRequest
import com.github.damontecres.wholphin.api.seerr.model.Season
import com.github.damontecres.wholphin.api.seerr.infrastructure.Serializer
import kotlinx.serialization.decodeFromString
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class SeerrAcquisitionTest {
    @Test
    fun calculatesMovieProgressFromAllValidQueueEntries() {
        val result =
            movieRequest(
                normal =
                    listOf(
                        download(size = 1_000.5, sizeLeft = 250.25, status = "downloading"),
                        download(size = 499.5, sizeLeft = 0.0, status = "queued"),
                    ),
            ).toSeerrRequestAcquisition()

        val movie = result.acquisition as SeerrAcquisitionState.Movie
        assertEquals(AcquisitionStatus.DOWNLOADING, movie.aggregate.status)
        assertEquals(1_500.0, movie.aggregate.progress!!.totalSize, 0.0)
        assertEquals(250.25, movie.aggregate.progress.sizeLeft, 0.0)
        assertEquals(1_249.75 / 1_500.0, movie.aggregate.progress.fraction, 0.000_001)
    }

    @Test
    fun processingWithoutQueueDataIsIndeterminate() {
        val result = movieRequest(mediaStatus = SeerrAvailability.PROCESSING.status).toSeerrRequestAcquisition()

        assertEquals(RequestStatus.APPROVED, result.request.status)
        assertEquals(SeerrAvailability.PROCESSING, result.request.availability)
        assertEquals(SeerrAcquisitionState.Processing, result.acquisition)
    }

    @Test
    fun emptyQueuePlaceholderIsIgnored() {
        val result =
            movieRequest(
                mediaStatus = SeerrAvailability.PROCESSING.status,
                normal = listOf(DownloadStatus()),
            ).toSeerrRequestAcquisition()

        assertEquals(SeerrAcquisitionState.Processing, result.acquisition)
    }

    @Test
    fun requestedTvSeasonSuppliesAvailabilityAndCompletionTimestamp() {
        val result =
            MediaRequest(
                id = 2,
                status = RequestStatus.COMPLETED.status,
                type = "tv",
                seasons =
                    listOf(
                        Season(
                            seasonNumber = 1,
                            status = SeerrAvailability.AVAILABLE.status,
                            updatedAt = "2026-09-01T07:38:08Z",
                        ),
                    ),
                media =
                    MediaInfo(
                        id = 20,
                        status = SeerrAvailability.PARTIALLY_AVAILABLE.status,
                    ),
            ).toSeerrRequestAcquisition()

        assertEquals(SeerrAvailability.PARTIALLY_AVAILABLE, result.request.availability)
        assertEquals(SeerrAvailability.AVAILABLE, result.request.seasonAvailability[1])
        assertEquals("2026-09-01T07:38:08Z", result.request.seasonUpdatedAt[1])
    }

    @Test
    fun emptyRequestActorsDeserializeWithoutLosingValidIdentity() {
        val empty =
            Serializer.kotlinxSerializationJson.decodeFromString<MediaRequest>(
                """{"id":1,"status":2,"requestedBy":{},"modifiedBy":{}}""",
            )
        val valid =
            Serializer.kotlinxSerializationJson.decodeFromString<MediaRequest>(
                """{"id":2,"status":2,"requestedBy":{"id":42,"username":"alex"}}""",
            )

        assertNull(empty.requestedBy?.id)
        assertNull(empty.modifiedBy?.id)
        assertEquals(42, valid.requestedBy?.id)
        assertEquals("alex", valid.requestedBy?.username)
    }

    @Test
    fun fourKRequestUsesOnlyFourKQueue() {
        val request =
            movieRequest(
                is4k = true,
                normal = listOf(download(size = 100.0, sizeLeft = 90.0, status = "downloading")),
                fourK = listOf(download(size = 200.0, sizeLeft = 50.0, status = "queued")),
            )

        val movie = request.toSeerrRequestAcquisition().acquisition as SeerrAcquisitionState.Movie
        assertEquals(AcquisitionStatus.QUEUED, movie.aggregate.status)
        assertEquals(0.75, movie.aggregate.progress!!.fraction, 0.0)
        assertEquals(200.0, movie.aggregate.progress.totalSize, 0.0)
    }

    @Test
    fun groupsTvProgressBySeasonAndRetainsEpisodeIdentity() {
        val request =
            tvRequest(
                requestedSeasons = setOf(1, 2),
                queue =
                    listOf(
                        episodeDownload(1, 1, 100.0, 25.0, "downloading", "s1e1"),
                        episodeDownload(1, 2, 300.0, 150.0, "queued", "s1e2"),
                        episodeDownload(2, 1, 500.0, 400.0, "paused", "s2e1"),
                    ),
            )

        val tv = request.toSeerrRequestAcquisition().acquisition as SeerrAcquisitionState.Tv
        val seasonOneProgress = tv.seasons[0].aggregate.progress!!
        assertEquals(listOf(1, 2), tv.seasons.map { it.seasonNumber })
        assertEquals(400.0, seasonOneProgress.totalSize, 0.0)
        assertEquals(175.0, seasonOneProgress.sizeLeft, 0.0)
        assertEquals(AcquisitionStatus.DOWNLOADING, tv.seasons[0].aggregate.status)
        assertEquals(2, tv.seasons[0].aggregate.entries[1].episode!!.episodeNumber)
        assertEquals("Episode 2", tv.seasons[0].aggregate.entries[1].episode!!.title)
        assertEquals("s1e2", tv.seasons[0].aggregate.entries[1].downloadId)
        assertEquals(0.2, tv.seasons[1].aggregate.progress!!.fraction, 0.000_001)
    }

    @Test
    fun invalidOrMissingSizesDoNotCreateOrCorruptProgress() {
        val result =
            movieRequest(
                normal =
                    listOf(
                        download(size = null, sizeLeft = null, status = "downloading"),
                        download(size = -1.0, sizeLeft = 0.0, status = "queued"),
                        download(size = 100.0, sizeLeft = 110.0, status = "queued"),
                    ),
            ).toSeerrRequestAcquisition()

        val movie = result.acquisition as SeerrAcquisitionState.Movie
        assertEquals(AcquisitionStatus.DOWNLOADING, movie.aggregate.status)
        assertNull(movie.aggregate.progress)
        assertEquals(3, movie.aggregate.entries.size)
    }

    @Test
    fun processingDoesNotMeanDownloadingWithoutDownloadingQueueStatus() {
        val result =
            movieRequest(
                mediaStatus = SeerrAvailability.PROCESSING.status,
                normal = listOf(download(size = 100.0, sizeLeft = 50.0, status = "queued")),
            ).toSeerrRequestAcquisition()

        val movie = result.acquisition as SeerrAcquisitionState.Movie
        assertEquals(AcquisitionStatus.QUEUED, movie.aggregate.status)
        assertTrue(movie.aggregate.entries.none { it.status == AcquisitionStatus.DOWNLOADING })
    }

    private fun movieRequest(
        is4k: Boolean = false,
        mediaStatus: Int = SeerrAvailability.PROCESSING.status,
        normal: List<DownloadStatus>? = null,
        fourK: List<DownloadStatus>? = null,
    ) = MediaRequest(
        id = 1,
        status = RequestStatus.APPROVED.status,
        type = "movie",
        is4k = is4k,
        media =
            MediaInfo(
                id = 10,
                status = mediaStatus,
                downloadStatus = normal,
                downloadStatus4k = fourK,
            ),
    )

    private fun tvRequest(
        requestedSeasons: Set<Int>,
        queue: List<DownloadStatus>,
    ) = MediaRequest(
        id = 2,
        status = RequestStatus.APPROVED.status,
        type = "tv",
        seasons = requestedSeasons.map { Season(seasonNumber = it) },
        media =
            MediaInfo(
                id = 20,
                status = SeerrAvailability.PROCESSING.status,
                downloadStatus = queue,
            ),
    )

    private fun download(
        size: Double?,
        sizeLeft: Double?,
        status: String,
    ) = DownloadStatus(
        externalId = 10,
        propertySize = size,
        sizeLeft = sizeLeft,
        status = status,
    )

    private fun episodeDownload(
        seasonNumber: Int,
        episodeNumber: Int,
        size: Double,
        sizeLeft: Double,
        status: String,
        downloadId: String,
    ) = DownloadStatus(
        externalId = 20,
        propertySize = size,
        sizeLeft = sizeLeft,
        status = status,
        downloadId = downloadId,
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
