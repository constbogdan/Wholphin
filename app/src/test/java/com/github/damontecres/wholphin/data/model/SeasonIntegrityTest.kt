package com.github.damontecres.wholphin.data.model

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class SeasonIntegrityTest {
    @Test
    fun allExpectedEpisodesPlayableIsComplete() {
        val result = calculate(expected = setOf(1, 2, 3), playable = setOf(1, 2, 3))!!

        assertFalse(result.incomplete)
        assertEquals(emptySet<Int>(), result.physicallyMissingEpisodeNumbers)
    }

    @Test
    fun exactExpectedAndPlayableEpisodesProducePhysicalMissingSet() {
        val result = calculate(expected = setOf(1, 2, 3), playable = setOf(1))!!

        assertEquals(setOf(2, 3), result.physicallyMissingEpisodeNumbers)
        assertEquals(setOf(2, 3), result.unattendedMissingEpisodeNumbers)
    }

    @Test
    fun activeReacquisitionDoesNotRewritePhysicalMissingState() {
        val result =
            calculate(
                expected = setOf(1, 2, 3),
                playable = setOf(1),
                coverage = SeasonAcquisitionCoverage(episodeNumbers = setOf(2, 99)),
            )!!

        assertEquals(setOf(2, 3), result.physicallyMissingEpisodeNumbers)
        assertEquals(setOf(2), result.activelyCoveredEpisodeNumbers)
        assertEquals(setOf(3), result.unattendedMissingEpisodeNumbers)
    }

    @Test
    fun wholeSeasonCoverageOnlySuppressesTheWarning() {
        val result =
            calculate(
                expected = setOf(1, 2),
                playable = setOf(1),
                coverage = SeasonAcquisitionCoverage(coversWholeSeason = true),
            )!!

        assertEquals(setOf(2), result.physicallyMissingEpisodeNumbers)
        assertFalse(result.incomplete)
    }

    @Test
    fun restoredEpisodeCannotRemainInAStaleMissingResult() {
        val before = calculate(setOf(1, 2), setOf(1))!!
        val after = calculate(setOf(1, 2), setOf(1, 2))!!

        assertTrue(before.incomplete)
        assertFalse(after.incomplete)
    }

    @Test
    fun specialsAndUnknownExpectationsProduceNoClaim() {
        assertNull(calculate(setOf(1), seasonNumber = 0))
        assertNull(calculate(emptySet()))
    }

    private fun calculate(
        expected: Set<Int>,
        playable: Set<Int> = emptySet(),
        coverage: SeasonAcquisitionCoverage = SeasonAcquisitionCoverage(),
        seasonNumber: Int = 1,
    ) = calculateSeasonIntegrity(
        expectation = SeasonIntegrityExpectation(seasonNumber, expected),
        seasonItemId = null,
        playableEpisodeNumbers = playable,
        acquisitionCoverage = coverage,
    )
}
