package com.github.damontecres.wholphin.services

import com.github.damontecres.wholphin.api.seerr.model.MediaInfo
import com.github.damontecres.wholphin.api.seerr.model.MediaRequest
import com.github.damontecres.wholphin.api.seerr.model.Season
import com.github.damontecres.wholphin.data.model.DiscoverItem
import com.github.damontecres.wholphin.data.model.SeerrAvailability
import com.github.damontecres.wholphin.data.model.SeerrItemType
import com.github.damontecres.wholphin.data.model.toSeerrRequestAcquisition
import com.github.damontecres.wholphin.ui.successQueryResult
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.jellyfin.sdk.api.client.ApiClient
import org.jellyfin.sdk.api.client.extensions.itemsApi
import org.jellyfin.sdk.api.operations.ItemsApi
import org.jellyfin.sdk.model.api.BaseItemDto
import org.jellyfin.sdk.model.api.BaseItemKind
import org.jellyfin.sdk.model.api.MediaSourceInfo
import org.jellyfin.sdk.model.api.request.GetItemsRequest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import java.util.UUID

class JellyfinAcquisitionReadinessServiceTest {
    private val api: ApiClient = mockk()
    private val itemsApi: ItemsApi = mockk()
    private val inventoryService: JellyfinSeriesInventoryService = mockk()
    private val service = JellyfinAcquisitionReadinessService(api, inventoryService)

    @Before
    fun setUp() {
        every { api.itemsApi } returns itemsApi
    }

    @Test
    fun coldStartMovieUsesExplicitJellyfinIdAndValidatesPlayability() =
        runTest {
            val movieId = UUID.randomUUID()
            val request = movieRequest(movieId)
            val item =
                BaseItemDto(
                    id = movieId,
                    type = BaseItemKind.MOVIE,
                    mediaSources = listOf(mockk<MediaSourceInfo>()),
                )
            coEvery { itemsApi.getItems(match<GetItemsRequest> { it.ids == listOf(movieId) }) } returns
                successQueryResult(listOf(item))

            val enriched = service.enrich(listOf(request)).single()

            assertEquals(movieId, enriched.request.jellyfinReadiness.movieItemId)
            assertTrue(enriched.request.jellyfinReadiness.movieReady)
        }

    @Test
    fun coldStartTvUsesExplicitJellyfinIdAndRestoresExactSeasonIdentity() =
        runTest {
            val seriesId = UUID.randomUUID()
            val seasonId = UUID.randomUUID()
            val episodeId = UUID.randomUUID()
            val request = tvRequest(seriesId)
            val item = BaseItemDto(id = seriesId, type = BaseItemKind.SERIES)
            coEvery { itemsApi.getItems(match<GetItemsRequest> { it.ids == listOf(seriesId) }) } returns
                successQueryResult(listOf(item))
            coEvery { inventoryService.get(seriesId) } returns
                JellyfinSeriesInventory(
                    seasonItemIds = mapOf(1 to seasonId),
                    playableEpisodeItemIds = mapOf(1 to mapOf(1 to episodeId)),
                )

            val enriched = service.enrich(listOf(request)).single()

            assertEquals(seriesId, enriched.request.jellyfinReadiness.seriesItemId)
            assertEquals(seasonId, enriched.request.jellyfinReadiness.seasonItemIds[1])
            assertEquals(episodeId, enriched.request.jellyfinReadiness.episodeItemIds[1]?.get(1))
            assertTrue(enriched.request.jellyfinReadiness.seasonReady(1, 1))
        }

    @Test
    fun unresolvedExplicitIdDoesNotFakeReadinessFromSeerrAvailability() =
        runTest {
            val movieId = UUID.randomUUID()
            val request = movieRequest(movieId)
            coEvery { itemsApi.getItems(any<GetItemsRequest>()) } returns successQueryResult()

            val enriched = service.enrich(listOf(request)).single()

            assertFalse(enriched.request.jellyfinReadiness.movieReady)
        }

    @Test
    fun missingSeerrJellyfinIdFallsBackToIndependentJellyfinDiscovery() =
        runTest {
            val movieId = UUID.randomUUID()
            val request = movieRequest(jellyfinItemId = null, availability = SeerrAvailability.PROCESSING)
            val item = playableMovie(movieId)
            coEvery { itemsApi.getItems(match<GetItemsRequest> { it.searchTerm == "Movie" }) } returns
                successQueryResult(listOf(item))

            val enriched = service.enrich(listOf(request)).single()

            assertEquals(movieId, enriched.request.jellyfinReadiness.movieItemId)
            coVerify(exactly = 1) { itemsApi.getItems(match<GetItemsRequest> { it.searchTerm == "Movie" }) }
        }

    @Test
    fun staleSeerrJellyfinIdFallsBackToIndependentJellyfinDiscovery() =
        runTest {
            val staleId = UUID.randomUUID()
            val movieId = UUID.randomUUID()
            val request = movieRequest(jellyfinItemId = staleId, availability = SeerrAvailability.PROCESSING)
            coEvery { itemsApi.getItems(match<GetItemsRequest> { it.ids == listOf(staleId) }) } returns successQueryResult()
            coEvery { itemsApi.getItems(match<GetItemsRequest> { it.searchTerm == "Movie" }) } returns
                successQueryResult(listOf(playableMovie(movieId)))

            val enriched = service.enrich(listOf(request)).single()

            assertEquals(movieId, enriched.request.jellyfinReadiness.movieItemId)
            coVerify(exactly = 1) { itemsApi.getItems(match<GetItemsRequest> { it.ids == listOf(staleId) }) }
            coVerify(exactly = 1) { itemsApi.getItems(match<GetItemsRequest> { it.searchTerm == "Movie" }) }
        }

    private fun movieRequest(
        jellyfinItemId: UUID?,
        availability: SeerrAvailability = SeerrAvailability.AVAILABLE,
    ) =
        MediaRequest(
            id = 1,
            status = 5,
            type = "movie",
            media = MediaInfo(id = 1, tmdbId = 10, status = availability.status),
        ).toSeerrRequestAcquisition().withDiscoverItem(SeerrItemType.MOVIE, 10, "Movie", jellyfinItemId)

    private fun playableMovie(movieId: UUID) =
        BaseItemDto(
            id = movieId,
            type = BaseItemKind.MOVIE,
            providerIds = mapOf("Tmdb" to "10"),
            mediaSources = listOf(mockk<MediaSourceInfo>()),
        )

    private fun tvRequest(jellyfinItemId: UUID) =
        MediaRequest(
            id = 2,
            status = 5,
            type = "tv",
            seasons = listOf(Season(seasonNumber = 1, status = SeerrAvailability.AVAILABLE.status)),
            media = MediaInfo(id = 2, tmdbId = 20, status = SeerrAvailability.PARTIALLY_AVAILABLE.status),
        ).toSeerrRequestAcquisition().let { acquisition ->
            val withDiscoverItem = acquisition.withDiscoverItem(SeerrItemType.TV, 20, "Series", jellyfinItemId)
            withDiscoverItem.copy(
                request = withDiscoverItem.request.copy(seasonEpisodeCounts = mapOf(1 to 1)),
            )
        }

    private fun com.github.damontecres.wholphin.data.model.SeerrRequestAcquisition.withDiscoverItem(
        type: SeerrItemType,
        tmdbId: Int,
        title: String,
        jellyfinItemId: UUID?,
    ) = copy(
        request =
            request.copy(
                discoverItem =
                    DiscoverItem(
                        id = tmdbId,
                        type = type,
                        title = title,
                        subtitle = null,
                        overview = null,
                        availability = SeerrAvailability.AVAILABLE,
                        releaseDate = null,
                        posterUrl = null,
                        backDropUrl = null,
                        logoUrl = null,
                        jellyfinItemId = jellyfinItemId,
                    ),
                seasonEpisodeCounts = request.seasonEpisodeCounts,
            ),
    )
}
