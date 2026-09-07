package com.github.damontecres.wholphin.ui.detail.series

import com.github.damontecres.wholphin.api.seerr.model.Episode
import com.github.damontecres.wholphin.api.seerr.model.Season
import com.github.damontecres.wholphin.data.model.LocalMediaType
import com.github.damontecres.wholphin.data.model.MediaKey
import com.github.damontecres.wholphin.services.IntegrityAssessment
import com.github.damontecres.wholphin.services.IntegrityState
import com.github.damontecres.wholphin.services.MediaProductState
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import java.time.LocalDate
import java.util.UUID

class SeasonIntegrityExpectationTest {
    @Test
    fun derivesOnlyReleasedDatedEpisodes() {
        val season =
            Season(
                seasonNumber = 1,
                episodeCount = 4,
                episodes =
                    listOf(
                        Episode(episodeNumber = 1, airDate = "2026-08-31"),
                        Episode(episodeNumber = 2, airDate = "2026-09-04"),
                        Episode(episodeNumber = 3, airDate = "2026-09-05"),
                        Episode(episodeNumber = 4, airDate = null),
                    ),
            )

        val result = season.toReleasedIntegrityExpectation(LocalDate.parse("2026-09-04"))!!

        assertEquals(setOf(1, 2), result.expectedEpisodeNumbers)
    }

    @Test
    fun omitsSpecialsAndUnsafeCountOnlyFallbacks() {
        val specials = Season(seasonNumber = 0, episodes = listOf(Episode(episodeNumber = 1, airDate = "2020-01-01")))
        val countOnly = Season(seasonNumber = 1, episodeCount = 10, episodes = null)

        assertTrue(specials.toReleasedIntegrityExpectation(LocalDate.parse("2026-09-04")) == null)
        assertTrue(countOnly.toReleasedIntegrityExpectation(LocalDate.parse("2026-09-04")) == null)
    }

    @Test
    fun incompleteStateProjectsThroughCombinedProductState() {
        val fixture = productProjectionFixture()
        val incomplete = integrityState(IntegrityAssessment.INCOMPLETE, missingCount = 2)

        val projected =
            fixture.seasons.withProductState(
                mapOf(fixture.seasonKey to MediaProductState(integrity = incomplete)),
                fixture.seriesKey,
            )

        assertTrue(projected.single().integrity?.incomplete == true)
        assertEquals(2, projected.single().integrity?.missingEpisodeCount)
        assertNull(projected.single().mediaPresentation)
    }

    @Test
    fun completeStateProjectsWithoutIncompleteIndicatorCondition() {
        val fixture = productProjectionFixture()
        val complete = integrityState(IntegrityAssessment.COMPLETE, missingCount = 0)

        val projected =
            fixture.seasons.withProductState(
                mapOf(fixture.seasonKey to MediaProductState(integrity = complete)),
                fixture.seriesKey,
            )

        assertFalse(projected.single().integrity?.incomplete ?: true)
        assertNull(projected.single().mediaPresentation)
    }

    @Test
    fun absentEnhancedStatePreservesBaseSeasonPresentation() {
        val fixture = productProjectionFixture()

        val projected = fixture.seasons.withProductState(emptyMap(), fixture.seriesKey)

        assertEquals(fixture.seasons.single().seasonNumber, projected.single().seasonNumber)
        assertEquals(fixture.seasons.single().jellyfinItem, projected.single().jellyfinItem)
        assertEquals(fixture.seasons.single().seerrSeason, projected.single().seerrSeason)
        assertEquals(fixture.seasons.single().imageUrl, projected.single().imageUrl)
        assertNull(projected.single().integrity)
        assertNull(projected.single().mediaPresentation)
    }

    private fun productProjectionFixture(): ProductProjectionFixture {
        val serverId = UUID.fromString("00000000-0000-0000-0000-000000000010")
        val seriesId = UUID.fromString("00000000-0000-0000-0000-000000000011")
        val seriesKey = MediaKey.Local(serverId, seriesId, LocalMediaType.SERIES)
        return ProductProjectionFixture(
            seriesKey = seriesKey,
            seasonKey = MediaKey.Season(seriesKey, 1),
            seasons = listOf(SeriesDetailsSeason(1, null, null, "poster")),
        )
    }

    private fun integrityState(assessment: IntegrityAssessment, missingCount: Int) =
        IntegrityState(
            assessment = assessment,
            missingEpisodeCount = missingCount,
            missingEpisodeNumbers = if (missingCount == 0) emptySet() else (1..missingCount).toSet(),
            expectedEpisodeNumbers = null,
            playableEpisodeNumbers = null,
            physicallyMissingEpisodeNumbers = null,
            activelyCoveredEpisodeNumbers = null,
        )

    private data class ProductProjectionFixture(
        val seriesKey: MediaKey.Local,
        val seasonKey: MediaKey.Season,
        val seasons: List<SeriesDetailsSeason>,
    )
}
