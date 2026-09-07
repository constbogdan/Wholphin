package com.github.damontecres.wholphin.ui.detail.series

import org.junit.Assert.assertEquals
import org.junit.Test
import java.util.UUID

class SeriesSeasonOrderingTest {
    @Test
    fun seasonsAreOrderedByNumberWithSpecialsFirst() {
        val seasons =
            listOf(
                TestSeason(number = 2, title = "Season Two"),
                TestSeason(number = 0, title = "Specials"),
                TestSeason(number = 3, title = "A title that would sort first"),
                TestSeason(number = 1, title = "Season One"),
            )

        val ordered = seasons.inSeasonNumberOrder { it.number }

        assertEquals(listOf(0, 1, 2, 3), ordered.map { it?.number })
    }

    @Test
    fun seasonsWithoutNumbersRemainLast() {
        val seasons =
            listOf(
                TestSeason(number = null, title = "Unknown"),
                TestSeason(number = 2, title = "Season Two"),
                TestSeason(number = 1, title = "Season One"),
            )

        val ordered = seasons.inSeasonNumberOrder { it.number }

        assertEquals(listOf(1, 2, null), ordered.map { it?.number })
    }

    @Test
    fun refreshReplacesSeasonCollectionAndPreservesSelectedSeasonById() {
        val season1 = TestSeason(UUID.randomUUID(), 1, "Season One")
        val season2 = TestSeason(UUID.randomUUID(), 2, "Season Two")
        val season3 = TestSeason(UUID.randomUUID(), 3, "Season Three")

        val refreshed =
            listOf(season3, season1, season2).asSeasonRefresh(
                selectedSeasonId = season2.id,
                itemId = { it.id },
                seasonNumber = { it.number },
            )

        assertEquals(listOf(1, 2, 3), refreshed.seasons.map { it?.number })
        assertEquals(season2.id, refreshed.seasons[refreshed.selectedIndex]?.id)
    }

    @Test
    fun refreshRemovesMissingSeasonAndFallsBackToFirstOrderedSeason() {
        val removedSeasonId = UUID.randomUUID()
        val season1 = TestSeason(UUID.randomUUID(), 1, "Season One")
        val season3 = TestSeason(UUID.randomUUID(), 3, "Season Three")

        val refreshed =
            listOf(season3, season1).asSeasonRefresh(
                selectedSeasonId = removedSeasonId,
                itemId = { it.id },
                seasonNumber = { it.number },
            )

        assertEquals(listOf(1, 3), refreshed.seasons.map { it?.number })
        assertEquals(0, refreshed.selectedIndex)
        assertEquals(season1.id, refreshed.seasons[refreshed.selectedIndex]?.id)
    }

    private data class TestSeason(
        val id: UUID = UUID.randomUUID(),
        val number: Int?,
        val title: String,
    )
}
