package com.github.damontecres.wholphin.services

import com.github.damontecres.wholphin.data.SeasonIntegrityDao
import com.github.damontecres.wholphin.data.ServerRepository
import com.github.damontecres.wholphin.data.model.AcquisitionStatus
import com.github.damontecres.wholphin.data.model.SeasonAcquisitionCoverage
import com.github.damontecres.wholphin.data.model.SeasonIntegrity
import com.github.damontecres.wholphin.data.model.SeasonIntegrityExpectation
import com.github.damontecres.wholphin.data.model.SeasonIntegrityExpectationCache
import com.github.damontecres.wholphin.data.model.SeerrAcquisitionState
import com.github.damontecres.wholphin.data.model.SeerrItemType
import com.github.damontecres.wholphin.data.model.calculateSeasonIntegrity
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SeasonIntegrityService
    @Inject
    constructor(
        private val dao: SeasonIntegrityDao,
        private val serverRepository: ServerRepository,
        private val acquisitionTracker: SeerrAcquisitionTracker,
        private val seriesInventoryService: JellyfinSeriesInventoryService,
        private val observationStore: IntegrityObservationStore,
    ) {
        suspend fun cachedSeasonNumbers(seriesItemId: UUID): Set<Int> {
            val userId = serverRepository.currentUser?.rowId ?: return emptySet()
            return dao.getSeries(userId, seriesItemId).mapTo(mutableSetOf()) { it.seasonNumber }
        }

        suspend fun evaluate(
            seriesItemId: UUID,
            tmdbId: Int?,
            refreshedExpectations: List<SeasonIntegrityExpectation> = emptyList(),
        ): List<SeasonIntegrity> {
            val user = serverRepository.currentUser ?: return emptyList()
            val userId = user.rowId
            val now = System.currentTimeMillis()
            if (refreshedExpectations.isNotEmpty()) {
                dao.upsert(
                    refreshedExpectations.map { expectation ->
                        SeasonIntegrityExpectationCache(
                            jellyfinUserRowId = userId,
                            seriesItemId = seriesItemId,
                            seasonNumber = expectation.seasonNumber,
                            tmdbId = tmdbId,
                            expectedEpisodeNumbers = expectation.expectedEpisodeNumbers,
                            lastUpdatedEpochMillis = now,
                        )
                    },
                )
            }

            val cached = dao.getSeries(userId, seriesItemId)
            val session = IntegritySession(user.serverId, userId)
            if (cached.isEmpty()) {
                observationStore.replaceSeries(session, seriesItemId, tmdbId, emptyList())
                return emptyList()
            }
            val inventory = seriesInventoryService.get(seriesItemId)
            val resolvedTmdbId = tmdbId ?: cached.firstNotNullOfOrNull { it.tmdbId }
            val coverage = acquisitionCoverage(resolvedTmdbId)
            val result =
                cached.mapNotNull { expectation ->
                    calculateSeasonIntegrity(
                        expectation =
                            SeasonIntegrityExpectation(
                                seasonNumber = expectation.seasonNumber,
                                expectedEpisodeNumbers = expectation.expectedEpisodeNumbers,
                            ),
                        seasonItemId = inventory.seasonItemIds[expectation.seasonNumber],
                        playableEpisodeNumbers = inventory.playableEpisodeNumbers[expectation.seasonNumber].orEmpty(),
                        acquisitionCoverage = coverage[expectation.seasonNumber] ?: SeasonAcquisitionCoverage(),
                    )
                }
            observationStore.replaceSeries(session, seriesItemId, resolvedTmdbId, result)
            return result
        }

        private fun acquisitionCoverage(tmdbId: Int?): Map<Int, SeasonAcquisitionCoverage> {
            if (tmdbId == null) return emptyMap()
            val requests =
                acquisitionTracker.state.value
                    .let { it.requests + it.queueingRequests }
                    .filter { it.request.tmdbId == tmdbId && it.request.mediaType == SeerrItemType.TV }
            return requests
                .flatMap { acquisition ->
                    val requestedSeasons = acquisition.request.requestedSeasonNumbers
                    when (val state = acquisition.acquisition) {
                        SeerrAcquisitionState.Queueing -> {
                            requestedSeasons.map { it to SeasonAcquisitionCoverage(coversWholeSeason = true) }
                        }

                        // Processing can remain stale long after real acquisition activity stops.
                        SeerrAcquisitionState.Processing -> {
                            emptyList()
                        }

                        is SeerrAcquisitionState.Tv -> {
                            val assigned =
                                state.seasons.map { season ->
                                    val episodes =
                                        season.aggregate.entries
                                            .filter { it.presentInQueue && it.status != AcquisitionStatus.PROBLEM }
                                            .mapNotNull { it.episode?.episodeNumber }
                                            .toSet()
                                    season.seasonNumber to SeasonAcquisitionCoverage(episodeNumbers = episodes)
                                }
                            val unassignedActive =
                                state.unassignedEntries.any { it.presentInQueue && it.status != AcquisitionStatus.PROBLEM }
                            if (unassignedActive && requestedSeasons.size == 1) {
                                assigned + (requestedSeasons.single() to SeasonAcquisitionCoverage(coversWholeSeason = true))
                            } else {
                                assigned
                            }
                        }

                        else -> {
                            emptyList()
                        }
                    }
                }.groupBy({ it.first }, { it.second })
                .mapValues { (_, values) ->
                    SeasonAcquisitionCoverage(
                        episodeNumbers = values.flatMap { it.episodeNumbers }.toSet(),
                        coversWholeSeason = values.any { it.coversWholeSeason },
                    )
                }
        }
    }
