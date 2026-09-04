package com.github.damontecres.wholphin.ui.detail.series

import com.github.damontecres.wholphin.api.seerr.model.Episode
import com.github.damontecres.wholphin.api.seerr.model.Season
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.time.LocalDate

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
}
