package com.github.damontecres.wholphin.data.model

import org.jellyfin.sdk.model.api.BaseItemDto
import org.jellyfin.sdk.model.api.BaseItemKind
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertNull
import org.junit.Test
import java.util.UUID

class MediaKeyTest {
    private val serverId = UUID.randomUUID()

    @Test
    fun jellyfinMovieAndSeriesUseTypedTmdbCatalogIdentity() {
        val movie = item(BaseItemKind.MOVIE, tmdbId = "42")
        val series = item(BaseItemKind.SERIES, tmdbId = "42")

        assertEquals(MediaKey.Catalog(CatalogMediaType.MOVIE, 42), movie.toMediaKey(serverId))
        assertEquals(MediaKey.Catalog(CatalogMediaType.SERIES, 42), series.toMediaKey(serverId))
        assertNotEquals(movie.toMediaKey(serverId), series.toMediaKey(serverId))
    }

    @Test
    fun jellyfinSeasonAndEpisodeAreScopedUnderKnownSeries() {
        val series = MediaKey.Catalog(CatalogMediaType.SERIES, 100)
        val season = item(BaseItemKind.SEASON, indexNumber = 0)
        val episode = item(BaseItemKind.EPISODE, indexNumber = 3, parentIndexNumber = 0)

        assertEquals(MediaKey.Season(series, 0), season.toMediaKey(serverId, series))
        assertEquals(MediaKey.Episode(series, 0, 3), episode.toMediaKey(serverId, series))
    }

    @Test
    fun jellyfinItemWithoutCatalogIdentityRetainsServerScopedLocalIdentity() {
        val itemId = UUID.randomUUID()
        val movie = item(BaseItemKind.MOVIE, id = itemId)

        assertEquals(MediaKey.Local(serverId, itemId, LocalMediaType.MOVIE), movie.toMediaKey(serverId))
        assertNotEquals(movie.toMediaKey(serverId), movie.toMediaKey(UUID.randomUUID()))
    }

    @Test
    fun invalidProviderIdIsNotGuessedFromTitle() {
        val movie = item(BaseItemKind.MOVIE, tmdbId = "not-a-number")

        assertEquals(MediaKey.Local(serverId, movie.id, LocalMediaType.MOVIE), movie.toMediaKey(serverId))
    }

    @Test
    fun discoverMovieAndSeriesUseTypedCatalogIdentity() {
        val movie = discover(77, SeerrItemType.MOVIE)
        val series = discover(77, SeerrItemType.TV)

        assertEquals(MediaKey.Catalog(CatalogMediaType.MOVIE, 77), movie.toMediaKey())
        assertEquals(MediaKey.Catalog(CatalogMediaType.SERIES, 77), series.toMediaKey())
        assertNotEquals(movie.toMediaKey(), series.toMediaKey())
    }

    @Test
    fun discoverIdentityWithoutSafeMediaTypeOrIdIsUnresolved() {
        assertNull(discover(-1, SeerrItemType.MOVIE).toMediaKey())
        assertNull(discover(77, SeerrItemType.PERSON).toMediaKey())
        assertNull(discover(77, SeerrItemType.UNKNOWN).toMediaKey())
    }

    private fun item(
        type: BaseItemKind,
        id: UUID = UUID.randomUUID(),
        tmdbId: String? = null,
        indexNumber: Int? = null,
        parentIndexNumber: Int? = null,
    ) = BaseItem(
        BaseItemDto(
            id = id,
            type = type,
            name = "A title that is never used for identity",
            providerIds = tmdbId?.let { mapOf("Tmdb" to it) },
            indexNumber = indexNumber,
            parentIndexNumber = parentIndexNumber,
        ),
    )

    private fun discover(
        id: Int,
        type: SeerrItemType,
    ) = DiscoverItem(
        id = id,
        type = type,
        title = "Ignored title",
        subtitle = null,
        overview = null,
        availability = SeerrAvailability.UNKNOWN,
        releaseDate = null,
        posterUrl = null,
        backDropUrl = null,
        logoUrl = null,
        jellyfinItemId = null,
    )
}
