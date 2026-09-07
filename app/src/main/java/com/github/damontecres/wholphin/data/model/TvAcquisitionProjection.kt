package com.github.damontecres.wholphin.data.model

import java.time.Instant
import java.time.OffsetDateTime

enum class TvSeasonLifecycle {
    QUEUED,
    IN_PROGRESS,
    FINISHING,
    AVAILABLE,
}

data class TvSeasonTarget(
    val request: SeerrRequestAcquisition,
    val seasonNumber: Int,
    val aggregate: AcquisitionAggregate?,
    val expectedEpisodeCount: Int?,
    val playableEpisodeCount: Int,
    val seerrAvailability: SeerrAvailability,
    val jellyfinReady: Boolean,
    val completedAtEpochMillis: Long?,
    val lifecycle: TvSeasonLifecycle,
    val acquisitionProjection: TvSeasonAcquisitionProjection,
    val hasCurrentAcquisitionWork: Boolean,
)

enum class TvAcquisitionScope {
    FULL_SEASON_ACQUISITION,
    EXPLICIT_EPISODES,
    AMBIGUOUS,
}

data class TvAcquisitionGroup(
    val downloadId: String?,
    val entries: List<AcquisitionEntry>,
    val scope: TvAcquisitionScope,
    val fraction: Double?,
    val representedEpisodes: Set<Int>,
    val current: Boolean,
)

data class TvSeasonAcquisitionProjection(
    val aggregate: AcquisitionAggregate,
    val groups: List<TvAcquisitionGroup>,
    val confirmedFraction: Double,
    val episodeNormalizedFraction: Double,
    val fullSeasonFraction: Double?,
    val displayedFraction: Double,
)

internal data class TvAcquisitionTiming(
    val remaining: String? = null,
    val etaEpochMillis: Long? = null,
)

internal fun SeerrRequestAcquisition.toTvSeasonTargets(): List<TvSeasonTarget> {
    if (request.mediaType != SeerrItemType.TV) return emptyList()
    val tv = acquisition as? SeerrAcquisitionState.Tv
    val assignedBySeason = tv?.seasons.orEmpty().associateBy { it.seasonNumber }
    val targetSeasonNumbers =
        (request.requestedSeasonNumbers + assignedBySeason.keys)
            .filter { it >= 0 }
            .distinct()
            .sorted()
    val unassignedAggregate =
        tv?.unassignedEntries
            ?.filter { it.episode?.seasonNumber == null }
            ?.takeIf {
                it.isNotEmpty() &&
                    request.requestedSeasonNumbers.size == 1 &&
                    assignedBySeason.isEmpty()
            }?.let(::aggregateAcquisitionEntries)

    return targetSeasonNumbers.map { seasonNumber ->
        val rawAggregate = assignedBySeason[seasonNumber]?.aggregate ?: unassignedAggregate
        val entries = rawAggregate?.entries.orEmpty()
        val expectedEpisodeCount = request.seasonEpisodeCounts[seasonNumber]
        val playableEpisodes = request.jellyfinReadiness.episodeItemIds[seasonNumber].orEmpty().keys
        val playableEpisodeCount = playableEpisodes.size
        val acquisitionProjection =
            (rawAggregate ?: AcquisitionAggregate(AcquisitionStatus.UNKNOWN, null, emptyList()))
                .analyzeTvSeasonAcquisition(seasonNumber, expectedEpisodeCount, playableEpisodes)
        val aggregate = acquisitionProjection.aggregate
        val jellyfinReady =
            request.jellyfinSeasonReadySinceEpochMillis.containsKey(seasonNumber) ||
                request.jellyfinReadiness.seasonReady(seasonNumber, expectedEpisodeCount)
        val seerrAvailability = request.seasonAvailability[seasonNumber] ?: SeerrAvailability.UNKNOWN
        val fullSeasonAcquisitionHasFinalEvidence =
            acquisitionProjection.groups.any { group ->
                group.scope == TvAcquisitionScope.FULL_SEASON_ACQUISITION &&
                    group.fraction == 1.0 &&
                    group.entries.any {
                        it.presentInQueue ||
                            it.absentPollCount <= TV_PROGRESS_GRACE_POLLS ||
                            it.observedSuccessfulTransferCompletion
                    }
            }
        val expectedEpisodesHaveFinalEvidence =
            expectedEpisodeCount != null &&
                expectedEpisodeCount > 0 &&
                (fullSeasonAcquisitionHasFinalEvidence ||
                    (1..expectedEpisodeCount).all { episodeNumber ->
                        episodeNumber in playableEpisodes ||
                            entries.any { entry ->
                                entry.episode?.episodeNumber == episodeNumber &&
                                    entry.status != AcquisitionStatus.PROBLEM &&
                                    entry.observedSuccessfulTransferCompletion
                            }
                    })
        val hasObservedActivity =
            entries.any { it.status != AcquisitionStatus.PROBLEM && it.hasObservedProgress } ||
                playableEpisodeCount > 0
        val lifecycle =
            when {
                jellyfinReady -> TvSeasonLifecycle.AVAILABLE
                seerrAvailability == SeerrAvailability.AVAILABLE -> TvSeasonLifecycle.FINISHING
                expectedEpisodesHaveFinalEvidence -> TvSeasonLifecycle.FINISHING
                hasObservedActivity -> TvSeasonLifecycle.IN_PROGRESS
                else -> TvSeasonLifecycle.QUEUED
            }
        val hasCurrentAcquisitionWork =
            acquisition == SeerrAcquisitionState.Queueing ||
                entries.any { entry ->
                    entry.status != AcquisitionStatus.PROBLEM &&
                        (entry.presentInQueue ||
                            (!entry.observedSuccessfulTransferCompletion &&
                                entry.absentPollCount <= TV_PROGRESS_GRACE_POLLS) ||
                            (entry.observedSuccessfulTransferCompletion && !jellyfinReady))
                }
        TvSeasonTarget(
            request = this,
            seasonNumber = seasonNumber,
            aggregate = aggregate,
            expectedEpisodeCount = expectedEpisodeCount,
            playableEpisodeCount = playableEpisodeCount,
            seerrAvailability = seerrAvailability,
            jellyfinReady = jellyfinReady,
            completedAtEpochMillis =
                request.jellyfinSeasonReadySinceEpochMillis[seasonNumber]
                    ?: request.seasonAvailableSinceEpochMillis[seasonNumber],
            lifecycle = lifecycle,
            acquisitionProjection = acquisitionProjection,
            hasCurrentAcquisitionWork = hasCurrentAcquisitionWork,
        )
    }
}

/**
 * TV progress is episode-normalized. Jellyfin is authoritative for playable episodes, while
 * current queue data (plus a bounded import grace) supplies provisional progress for the rest.
 */
internal fun AcquisitionAggregate.analyzeTvSeasonAcquisition(
    targetSeasonNumber: Int,
    expectedEpisodeCount: Int?,
    playableEpisodes: Set<Int>,
): TvSeasonAcquisitionProjection {
    if (expectedEpisodeCount == null || expectedEpisodeCount <= 0) {
        return TvSeasonAcquisitionProjection(
            aggregate = copy(progress = null),
            groups = emptyList(),
            confirmedFraction = 0.0,
            episodeNormalizedFraction = 0.0,
            fullSeasonFraction = null,
            displayedFraction = 0.0,
        )
    }

    val eligible =
        entries.filter { entry ->
            entry.status != AcquisitionStatus.PROBLEM &&
                (entry.presentInQueue ||
                    entry.absentPollCount <= TV_PROGRESS_GRACE_POLLS ||
                    entry.observedSuccessfulTransferCompletion) &&
                (entry.observedSuccessfulTransferCompletion ||
                    (entry.totalSize != null && entry.sizeLeft != null))
        }
    val groups =
        eligible
            .groupBy { entry ->
                entry.downloadId
                    ?: "episode:${entry.episode?.episodeNumber}:${entry.externalId}:${entry.title}"
            }.map { (_, groupEntries) ->
                groupEntries.toTvAcquisitionGroup(targetSeasonNumber)
            }
    val provisionalByEpisode = mutableMapOf<Int, Double>()
    groups
        .filter { it.scope != TvAcquisitionScope.FULL_SEASON_ACQUISITION }
        .forEach { group ->
            val fraction = group.fraction ?: return@forEach
            group.representedEpisodes.forEach { episodeNumber ->
                if (episodeNumber in 1..expectedEpisodeCount) {
                    provisionalByEpisode[episodeNumber] =
                        maxOf(provisionalByEpisode[episodeNumber] ?: 0.0, fraction)
                }
            }
        }

    val episodeNormalizedContribution =
        (1..expectedEpisodeCount).sumOf { episodeNumber ->
            if (episodeNumber in playableEpisodes) 1.0 else provisionalByEpisode[episodeNumber] ?: 0.0
        }
    val confirmedFraction =
        playableEpisodes.count { it in 1..expectedEpisodeCount }.toDouble() / expectedEpisodeCount
    val episodeNormalizedFraction = episodeNormalizedContribution / expectedEpisodeCount
    val fullSeasonFraction =
        groups
            .asSequence()
            .filter { it.scope == TvAcquisitionScope.FULL_SEASON_ACQUISITION }
            .mapNotNull { it.fraction }
            .maxOrNull()
    val displayedFraction =
        maxOf(confirmedFraction, episodeNormalizedFraction, fullSeasonFraction ?: 0.0)
            .coerceIn(0.0, 1.0)
    return TvSeasonAcquisitionProjection(
        aggregate =
            copy(
                progress =
                    AcquisitionProgress(
                        totalSize = expectedEpisodeCount.toDouble(),
                        sizeLeft = expectedEpisodeCount * (1.0 - displayedFraction),
                    ),
            ),
        groups = groups,
        confirmedFraction = confirmedFraction,
        episodeNormalizedFraction = episodeNormalizedFraction,
        fullSeasonFraction = fullSeasonFraction,
        displayedFraction = displayedFraction,
    )
}

internal fun TvSeasonAcquisitionProjection.activeTiming(nowEpochMillis: Long): TvAcquisitionTiming? {
    if (!aggregate.hasCurrentDownloadingProgress || aggregate.isFinishing) return null

    val selectedFullSeasonGroup =
        groups.firstOrNull {
            it.scope == TvAcquisitionScope.FULL_SEASON_ACQUISITION &&
                it.current &&
                it.fraction == fullSeasonFraction
        }
    if (selectedFullSeasonGroup != null) {
        return selectedFullSeasonGroup.entries
            .currentTimingCandidates(nowEpochMillis)
            .latestFinishingCandidate()
            ?.toTiming(nowEpochMillis)
    }

    return groups
        .filter { it.scope != TvAcquisitionScope.FULL_SEASON_ACQUISITION }
        .flatMap { it.entries }
        .currentTimingCandidates(nowEpochMillis)
        .latestFinishingCandidate()
        ?.toTiming(nowEpochMillis)
}

internal val AcquisitionAggregate.hasActiveProgress: Boolean
    get() =
        entries.any {
            it.presentInQueue &&
                it.hasObservedProgress &&
                it.sizeLeft != null &&
                it.sizeLeft > 0.0
        }

internal val AcquisitionAggregate.isFinishing: Boolean
    get() {
        val liveEntries = entries.filter { it.presentInQueue }
        return entries.isNotEmpty() &&
            ((liveEntries.isEmpty() && entries.any { it.hasObservedProgress }) ||
                (liveEntries.isNotEmpty() &&
                    liveEntries.all {
                        it.status == AcquisitionStatus.COMPLETED ||
                            it.sizeLeft == 0.0 ||
                            (it.status != AcquisitionStatus.QUEUED && it.timeLeft.isZeroDuration())
                    }))
    }

private fun List<AcquisitionEntry>.toTvAcquisitionGroup(
    targetSeasonNumber: Int,
): TvAcquisitionGroup {
    val representedEpisodes = mapNotNull { it.episode?.episodeNumber }.toSet()
    val totals = mapNotNull { it.totalSize }.distinct()
    val remaining = mapNotNull { it.sizeLeft }.distinct()
    val statuses = map { it.status }.distinct()
    val times = mapNotNull { it.timeLeft?.takeUnless(String::isBlank) }.distinct()
    val etas = mapNotNull { it.estimatedCompletionTime?.takeUnless(String::isBlank) }.distinct()
    val titles = mapNotNull { it.title?.trim()?.takeUnless(String::isBlank) }.distinct()
    val fraction =
        when {
            all { it.observedSuccessfulTransferCompletion } -> 1.0
            totals.size == 1 && remaining.size == 1 && totals.single() > 0.0 ->
                (1.0 - remaining.single() / totals.single()).coerceIn(0.0, 1.0)
            else -> null
        }
    val releaseScope = titles.singleOrNull()?.parseTvReleaseScope(targetSeasonNumber)
    val sharedDownload = first().downloadId?.takeUnless(String::isBlank)
    val coherentState =
        totals.size == 1 && remaining.size == 1 && statuses.size == 1 && times.size <= 1 && etas.size <= 1
    val allEntriesBelongToTargetSeason = all { it.episode?.seasonNumber == targetSeasonNumber }
    val scope =
        when {
            releaseScope == TvReleaseScope.EXPLICIT_EPISODES -> TvAcquisitionScope.EXPLICIT_EPISODES
            releaseScope == TvReleaseScope.PARTIAL_SEASON -> TvAcquisitionScope.AMBIGUOUS
            sharedDownload == null -> TvAcquisitionScope.AMBIGUOUS
            representedEpisodes.size < 2 -> TvAcquisitionScope.AMBIGUOUS
            !allEntriesBelongToTargetSeason -> TvAcquisitionScope.AMBIGUOUS
            titles.size != 1 -> TvAcquisitionScope.AMBIGUOUS
            !coherentState -> TvAcquisitionScope.AMBIGUOUS
            releaseScope == TvReleaseScope.SEASON_ONLY -> TvAcquisitionScope.FULL_SEASON_ACQUISITION
            else -> TvAcquisitionScope.AMBIGUOUS
        }
    return TvAcquisitionGroup(
        downloadId = sharedDownload,
        entries = this,
        scope = scope,
        fraction = fraction,
        representedEpisodes = representedEpisodes,
        current = any { it.presentInQueue },
    )
}

private enum class TvReleaseScope {
    SEASON_ONLY,
    EXPLICIT_EPISODES,
    PARTIAL_SEASON,
    UNKNOWN,
}

private fun String.parseTvReleaseScope(targetSeasonNumber: Int): TvReleaseScope {
    val separator = "[\\s._-]"
    val episodeToken =
        Regex(
            "(?i)(?:s\\d{1,3}${separator}*e\\d{1,4}|(?:^|$separator)\\d{1,3}x\\d{1,4}(?:$|$separator)|" +
                "(?:^|$separator)e(?:p(?:isode)?)?${separator}*\\d{1,4}|" +
                "e\\d{1,4}${separator}*(?:-|to)${separator}*e?\\d{1,4})",
        )
    if (episodeToken.containsMatchIn(this)) return TvReleaseScope.EXPLICIT_EPISODES

    val partialSeason =
        Regex("(?i)(?:^|$separator)(?:part|pt|vol(?:ume)?|disc|disk|cour)${separator}*\\d+(?:$|$separator)")
    if (partialSeason.containsMatchIn(this)) return TvReleaseScope.PARTIAL_SEASON

    val seasonToken =
        Regex(
            "(?i)(?:^|$separator)(?:s0*$targetSeasonNumber|season${separator}*0*$targetSeasonNumber)(?:$|$separator)",
        )
    return if (seasonToken.containsMatchIn(this)) TvReleaseScope.SEASON_ONLY else TvReleaseScope.UNKNOWN
}

private data class TvTimingCandidate(
    val entry: AcquisitionEntry,
    val etaEpochMillis: Long?,
    val remainingSeconds: Long?,
)

private val AcquisitionAggregate.hasCurrentDownloadingProgress: Boolean
    get() =
        entries.any {
            it.presentInQueue &&
                it.status == AcquisitionStatus.DOWNLOADING &&
                it.hasObservedProgress &&
                it.sizeLeft?.let { left -> left > 0.0 } == true
        }

private fun List<AcquisitionEntry>.currentTimingCandidates(nowEpochMillis: Long): List<TvTimingCandidate> =
    asSequence()
        .filter {
            it.presentInQueue &&
                it.status != AcquisitionStatus.PROBLEM &&
                it.sizeLeft?.let { left -> left > 0.0 } == true
        }.mapNotNull { entry ->
            val eta = entry.estimatedCompletionTime?.toFutureEpochMillis(nowEpochMillis)
            val remaining = entry.timeLeft.toPositiveDurationSeconds()
            if (eta == null && remaining == null) null else TvTimingCandidate(entry, eta, remaining)
        }.toList()

private fun List<TvTimingCandidate>.latestFinishingCandidate(): TvTimingCandidate? =
    filter { it.remainingSeconds != null }.maxByOrNull { it.remainingSeconds!! }
        ?: filter { it.etaEpochMillis != null }.maxByOrNull { it.etaEpochMillis!! }

private fun TvTimingCandidate.toTiming(nowEpochMillis: Long): TvAcquisitionTiming =
    TvAcquisitionTiming(
        remaining = entry.timeLeft?.takeIf { remainingSeconds != null },
        etaEpochMillis = remainingSeconds?.let { nowEpochMillis + it * 1_000L } ?: etaEpochMillis,
    )

private fun String?.toPositiveDurationSeconds(): Long? {
    val parts = this?.trim()?.split(':') ?: return null
    if (parts.size != 3) return null
    val hours = parts[0].toLongOrNull() ?: return null
    val minutes = parts[1].toLongOrNull() ?: return null
    val seconds = parts[2].toLongOrNull() ?: return null
    if (hours < 0 || minutes !in 0..59 || seconds !in 0..59) return null
    return (hours * 3600 + minutes * 60 + seconds).takeIf { it > 0 }
}

private fun String.toFutureEpochMillis(nowEpochMillis: Long): Long? =
    runCatching { Instant.parse(this).toEpochMilli() }
        .recoverCatching { OffsetDateTime.parse(this).toInstant().toEpochMilli() }
        .getOrNull()
        ?.takeIf { it > nowEpochMillis }

private fun String?.isZeroDuration(): Boolean =
    this?.trim() in setOf("00:00:00", "0:00:00", "00:00")
