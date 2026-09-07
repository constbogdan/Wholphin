package com.github.damontecres.wholphin.data.model

import java.time.Instant
import java.time.OffsetDateTime

internal const val DOWNLOADS_WAITING_GRACE_MILLIS = 15 * 60_000L
internal const val DOWNLOADS_COMPLETED_WINDOW_MILLIS = 7 * 24 * 60 * 60_000L

internal fun SeerrRequestState.isWithinDownloadsWaitingGrace(nowEpochMillis: Long): Boolean =
    (updatedAt ?: createdAt)?.toDownloadsEpochMillis()?.let {
        nowEpochMillis - it in 0..DOWNLOADS_WAITING_GRACE_MILLIS
    } == true

internal fun Long?.isWithinDownloadsCompletedWindow(nowEpochMillis: Long): Boolean =
    this?.let { nowEpochMillis - it in 0..DOWNLOADS_COMPLETED_WINDOW_MILLIS } == true

internal fun SeerrRequestAcquisition.hasAuthoritativeDownloadsRepresentation(
    nowEpochMillis: Long,
): Boolean =
    request.jellyfinReadiness.movieReady ||
        (request.availability !in TERMINAL_AVAILABILITY &&
            ((acquisition as? SeerrAcquisitionState.Movie)?.aggregate?.entries?.isNotEmpty() == true ||
                request.isWithinDownloadsWaitingGrace(nowEpochMillis)))

internal fun SeerrRequestAcquisition.authoritativelyRepresentedSeasons(
    nowEpochMillis: Long,
): Set<Int> {
    val requested = request.requestedSeasonNumbers
    if (requested.isEmpty()) return emptySet()
    val tv = acquisition as? SeerrAcquisitionState.Tv
    val assigned = tv?.seasons.orEmpty().associateBy { it.seasonNumber }
    val unassignedCanRepresentSoleSeason =
        requested.size == 1 && assigned.isEmpty() && tv?.unassignedEntries.orEmpty().isNotEmpty()
    val waiting = request.isWithinDownloadsWaitingGrace(nowEpochMillis)
    return requested.filterTo(mutableSetOf()) { seasonNumber ->
        request.jellyfinSeasonReadySinceEpochMillis.containsKey(seasonNumber) ||
            request.jellyfinReadiness.seasonReady(seasonNumber, request.seasonEpisodeCounts[seasonNumber]) ||
            request.jellyfinReadiness.episodeItemIds[seasonNumber].orEmpty().isNotEmpty() ||
            assigned[seasonNumber]?.aggregate?.entries?.isNotEmpty() == true ||
            unassignedCanRepresentSoleSeason ||
            (request.seasonAvailability[seasonNumber] == SeerrAvailability.AVAILABLE &&
                request.seasonAvailableSinceEpochMillis[seasonNumber]
                    .isWithinDownloadsCompletedWindow(nowEpochMillis)) ||
            waiting
    }
}

private fun String.toDownloadsEpochMillis(): Long? =
    runCatching { Instant.parse(this).toEpochMilli() }
        .recoverCatching { OffsetDateTime.parse(this).toInstant().toEpochMilli() }
        .getOrNull()

private val TERMINAL_AVAILABILITY =
    setOf(
        SeerrAvailability.AVAILABLE,
        SeerrAvailability.BLOCKLISTED,
        SeerrAvailability.DELETED,
    )
