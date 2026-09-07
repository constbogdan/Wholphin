package com.github.damontecres.wholphin.services

import com.github.damontecres.wholphin.data.ServerRepository
import com.github.damontecres.wholphin.data.model.CatalogMediaType
import com.github.damontecres.wholphin.data.model.LocalMediaType
import com.github.damontecres.wholphin.data.model.MediaKey
import com.github.damontecres.wholphin.data.model.SeasonIntegrity
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.flow.update
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

enum class IntegrityAssessment {
    COMPLETE,
    INCOMPLETE,
}

data class IntegrityState(
    val assessment: IntegrityAssessment,
    val missingEpisodeCount: Int,
    val missingEpisodeNumbers: Set<Int>?,
    val expectedEpisodeNumbers: Set<Int>?,
    val playableEpisodeNumbers: Set<Int>?,
    val physicallyMissingEpisodeNumbers: Set<Int>?,
    val activelyCoveredEpisodeNumbers: Set<Int>?,
    val catalogSeasonAlias: MediaKey.Season? = null,
) {
    val incomplete: Boolean get() = assessment == IntegrityAssessment.INCOMPLETE
}

internal data class IntegritySession(
    val serverId: UUID,
    val jellyfinUserRowId: Int,
)

internal data class SeasonIntegrityObservation(
    val session: IntegritySession,
    val seriesItemId: UUID,
    val seasonNumber: Int,
    val state: IntegrityState,
)

@Singleton
class IntegrityObservationStore
    @Inject
    constructor() {
        private val mutableObservations = MutableStateFlow<List<SeasonIntegrityObservation>>(emptyList())
        internal val observations: Flow<List<SeasonIntegrityObservation>> = mutableObservations

        internal fun replaceSeries(
            session: IntegritySession,
            seriesItemId: UUID,
            tmdbId: Int?,
            integrity: List<SeasonIntegrity>,
        ) {
            val replacement = integrity.map { it.toObservation(session, seriesItemId, tmdbId) }
            mutableObservations.update { current ->
                current.filterNot { it.session == session && it.seriesItemId == seriesItemId } + replacement
            }
        }
    }

@Singleton
class IntegrityStateSource
    @Inject
    internal constructor(
        observationStore: IntegrityObservationStore,
        serverRepository: ServerRepository,
        enhancedFeatureGate: EnhancedFeatureGate,
    ) {
        private val observations = observationStore.observations
        private val currentUser = serverRepository.current
        private val enabled = enhancedFeatureGate.observe(EnhancedCapability.SEASON_INTEGRITY)

        fun observe(keys: Set<MediaKey>): Flow<Map<MediaKey, IntegrityState>> {
            if (keys.isEmpty()) return flowOf(emptyMap())
            val requestedKeys = keys.toSet()
            return combine(observations, currentUser, enabled) { observations, current, enabled ->
                val session = current?.user?.let { IntegritySession(it.serverId, it.rowId) }
                observations.toKeyedIntegrityState(session, enabled, requestedKeys)
            }.distinctUntilChanged()
        }
    }

internal fun List<SeasonIntegrityObservation>.toKeyedIntegrityState(
    activeSession: IntegritySession?,
    enabled: Boolean,
    requestedKeys: Set<MediaKey>,
): Map<MediaKey, IntegrityState> {
    if (!enabled || activeSession == null || requestedKeys.isEmpty()) return emptyMap()
    return asSequence()
        .filter { it.session == activeSession && it.seasonNumber >= 0 }
        .map { observation ->
            val seriesKey = MediaKey.Local(activeSession.serverId, observation.seriesItemId, LocalMediaType.SERIES)
            MediaKey.Season(seriesKey, observation.seasonNumber) to observation.state
        }.filter { (key, _) -> key in requestedKeys }
        .toMap()
}

internal fun SeasonIntegrity.toObservation(
    session: IntegritySession,
    seriesItemId: UUID,
    tmdbId: Int?,
): SeasonIntegrityObservation {
    val catalogAlias =
        tmdbId?.takeIf { it > 0 }?.let {
            MediaKey.Season(MediaKey.Catalog(CatalogMediaType.SERIES, it), seasonNumber)
        }
    return SeasonIntegrityObservation(
        session = session,
        seriesItemId = seriesItemId,
        seasonNumber = seasonNumber,
        state =
            IntegrityState(
                assessment = if (incomplete) IntegrityAssessment.INCOMPLETE else IntegrityAssessment.COMPLETE,
                missingEpisodeCount = missingEpisodeCount,
                missingEpisodeNumbers = unattendedMissingEpisodeNumbers.toSet(),
                expectedEpisodeNumbers = expectedEpisodeNumbers.toSet(),
                playableEpisodeNumbers = playableEpisodeNumbers.toSet(),
                physicallyMissingEpisodeNumbers = physicallyMissingEpisodeNumbers.toSet(),
                activelyCoveredEpisodeNumbers = activelyCoveredEpisodeNumbers.toSet(),
                catalogSeasonAlias = catalogAlias,
            ),
    )
}
