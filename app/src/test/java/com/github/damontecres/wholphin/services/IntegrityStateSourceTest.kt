package com.github.damontecres.wholphin.services

import com.github.damontecres.wholphin.data.model.CatalogMediaType
import com.github.damontecres.wholphin.data.model.LocalMediaType
import com.github.damontecres.wholphin.data.model.MediaKey
import com.github.damontecres.wholphin.data.model.SeasonIntegrity
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import java.util.UUID

class IntegrityStateSourceTest {
    private val serverId = UUID.fromString("00000000-0000-0000-0000-000000000001")
    private val seriesId = UUID.fromString("00000000-0000-0000-0000-000000000002")
    private val session = IntegritySession(serverId, jellyfinUserRowId = 10)

    @Test
    fun knownJellyfinSeriesAndSeasonsMapToExactLocalMediaKeys() {
        val season1State = integrityState(IntegrityAssessment.COMPLETE, 0, emptySet())
        val season2State = integrityState(IntegrityAssessment.INCOMPLETE, 1, setOf(4))
        val observations = listOf(observation(1, state = season1State), observation(2, state = season2State))
        val season1 = seasonKey(serverId, seriesId, 1)
        val season2 = seasonKey(serverId, seriesId, 2)

        val result =
            observations.toKeyedIntegrityState(
                activeSession = session,
                enabled = true,
                requestedKeys = setOf(season2, season1),
            )

        assertEquals(setOf(season1, season2), result.keys)
        assertEquals(IntegrityAssessment.COMPLETE, result.getValue(season1).assessment)
        assertEquals(setOf(4), result.getValue(season2).missingEpisodeNumbers)
    }

    @Test
    fun serverAndActiveUserSessionsDoNotExposeEachOthersObservations() {
        val otherServer = UUID.fromString("00000000-0000-0000-0000-000000000003")
        val otherServerSession = IntegritySession(otherServer, jellyfinUserRowId = 10)
        val otherUserSession = IntegritySession(serverId, jellyfinUserRowId = 11)
        val requested = setOf(seasonKey(serverId, seriesId, 1), seasonKey(otherServer, seriesId, 1))
        val observations =
            listOf(
                observation(1),
                observation(1, session = otherServerSession),
                observation(1, session = otherUserSession),
            )

        val result = observations.toKeyedIntegrityState(session, enabled = true, requested)

        assertEquals(setOf(seasonKey(serverId, seriesId, 1)), result.keys)
    }

    @Test
    fun incompleteStateAndExactMissingNumbersArePreserved() {
        val observation =
            SeasonIntegrity(
                seasonNumber = 4,
                seasonItemId = UUID.fromString("00000000-0000-0000-0000-000000000005"),
                expectedEpisodeNumbers = setOf(1, 2, 3, 4, 5),
                playableEpisodeNumbers = setOf(1, 2),
                physicallyMissingEpisodeNumbers = setOf(3, 4, 5),
                activelyCoveredEpisodeNumbers = setOf(4),
                unattendedMissingEpisodeNumbers = setOf(3, 5),
            )
                .toObservation(session, seriesId, tmdbId = 100)
        val key = seasonKey(serverId, seriesId, 4)

        val result =
            listOf(observation)
                .toKeyedIntegrityState(session, true, setOf(key))
                .getValue(key)

        assertEquals(IntegrityAssessment.INCOMPLETE, result.assessment)
        assertEquals(2, result.missingEpisodeCount)
        assertEquals(setOf(3, 5), result.missingEpisodeNumbers)
        assertEquals(setOf(1, 2, 3, 4, 5), result.expectedEpisodeNumbers)
        assertEquals(setOf(1, 2), result.playableEpisodeNumbers)
        assertEquals(setOf(3, 4, 5), result.physicallyMissingEpisodeNumbers)
        assertEquals(setOf(4), result.activelyCoveredEpisodeNumbers)
        assertEquals(
            MediaKey.Season(MediaKey.Catalog(CatalogMediaType.SERIES, 100), 4),
            result.catalogSeasonAlias,
        )
    }

    @Test
    fun completeStateIsPreserved() {
        val key = seasonKey(serverId, seriesId, 1)
        val state = integrityState(IntegrityAssessment.COMPLETE, missingCount = 0, missingNumbers = emptySet())

        val result =
            listOf(observation(1, state = state))
                .toKeyedIntegrityState(session, true, setOf(key))
                .getValue(key)

        assertEquals(IntegrityAssessment.COMPLETE, result.assessment)
        assertEquals(0, result.missingEpisodeCount)
        assertEquals(emptySet<Int>(), result.missingEpisodeNumbers)
    }

    @Test
    fun countOnlyMissingStateDoesNotInventEpisodeNumbers() {
        val key = seasonKey(serverId, seriesId, 3)
        val state = integrityState(IntegrityAssessment.INCOMPLETE, missingCount = 2, missingNumbers = null)

        val result =
            listOf(observation(3, state = state))
                .toKeyedIntegrityState(session, true, setOf(key))
                .getValue(key)

        assertEquals(2, result.missingEpisodeCount)
        assertNull(result.missingEpisodeNumbers)
    }

    @Test
    fun seasonZeroIdentityRemainsRepresentable() {
        val key = seasonKey(serverId, seriesId, 0)

        val result = listOf(observation(0)).toKeyedIntegrityState(session, true, setOf(key))

        assertTrue(key in result)
    }

    @Test
    fun unsafeOrUnrequestedIdentityIsNotGuessed() {
        val requested = seasonKey(serverId, seriesId, 1)
        val differentSeries = UUID.fromString("00000000-0000-0000-0000-000000000004")
        val observations = listOf(observation(-1), observation(1, seriesItemId = differentSeries))

        val result = observations.toKeyedIntegrityState(session, enabled = true, setOf(requested))

        assertTrue(result.isEmpty())
    }

    @Test
    fun emptyInactiveAndDisabledSourcesExposeNoState() {
        val key = seasonKey(serverId, seriesId, 1)
        val observations = listOf(observation(1))

        assertTrue(
            emptyList<SeasonIntegrityObservation>()
                .toKeyedIntegrityState(session, true, setOf(key))
                .isEmpty(),
        )
        assertTrue(observations.toKeyedIntegrityState(null, true, setOf(key)).isEmpty())
        assertTrue(observations.toKeyedIntegrityState(session, false, setOf(key)).isEmpty())
        assertTrue(observations.toKeyedIntegrityState(session, true, emptySet()).isEmpty())
    }

    private fun observation(
        seasonNumber: Int,
        session: IntegritySession = this.session,
        seriesItemId: UUID = this.seriesId,
        state: IntegrityState = integrityState(IntegrityAssessment.COMPLETE, 0, emptySet()),
    ) = SeasonIntegrityObservation(
        session = session,
        seriesItemId = seriesItemId,
        seasonNumber = seasonNumber,
        state = state,
    )

    private fun seasonKey(serverId: UUID, seriesId: UUID, seasonNumber: Int): MediaKey.Season =
        MediaKey.Season(MediaKey.Local(serverId, seriesId, LocalMediaType.SERIES), seasonNumber)

    private fun integrityState(
        assessment: IntegrityAssessment,
        missingCount: Int,
        missingNumbers: Set<Int>?,
    ) = IntegrityState(
        assessment = assessment,
        missingEpisodeCount = missingCount,
        missingEpisodeNumbers = missingNumbers,
        expectedEpisodeNumbers = null,
        playableEpisodeNumbers = null,
        physicallyMissingEpisodeNumbers = null,
        activelyCoveredEpisodeNumbers = null,
    )
}
