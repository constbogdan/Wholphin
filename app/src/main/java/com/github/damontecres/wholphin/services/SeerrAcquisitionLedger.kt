package com.github.damontecres.wholphin.services

import com.github.damontecres.wholphin.data.model.AcquisitionEntry
import com.github.damontecres.wholphin.data.model.AcquisitionStatus
import com.github.damontecres.wholphin.data.model.SeasonAcquisition
import com.github.damontecres.wholphin.data.model.SeerrAcquisitionState
import com.github.damontecres.wholphin.data.model.SeerrRequestAcquisition
import com.github.damontecres.wholphin.data.model.TV_PROGRESS_GRACE_POLLS
import com.github.damontecres.wholphin.data.model.aggregateAcquisitionEntries

internal class SeerrAcquisitionLedger {
    private val entries = mutableMapOf<LedgerEntryKey, LedgerEntry>()

    fun clear() = entries.clear()

    fun reconcile(requests: List<SeerrRequestAcquisition>): List<SeerrRequestAcquisition> {
        entries.replaceAll { _, value ->
            value.copy(
                entry =
                    value.entry.copy(
                        status = AcquisitionStatus.UNKNOWN,
                        presentInQueue = false,
                        absentPollCount =
                            if (value.entry.status == AcquisitionStatus.PROBLEM) {
                                TV_PROGRESS_GRACE_POLLS + 1
                            } else {
                                value.entry.absentPollCount + 1
                            },
                    ),
            )
        }

        requests.forEach { request ->
            val currentEntries = request.currentEntries()
            currentEntries.forEach { entry ->
                val key = request.entryKey(entry)
                if (request.request.mediaType == com.github.damontecres.wholphin.data.model.SeerrItemType.TV) {
                    entries.keys.removeAll { otherKey ->
                        otherKey.sameEpisodeAs(key) && otherKey.acquisitionIdentity != key.acquisitionIdentity
                    }
                }
                entries[key] =
                    entries[key]?.merge(
                        current = entry,
                        retainByteMaximums =
                            request.request.mediaType == com.github.damontecres.wholphin.data.model.SeerrItemType.MOVIE,
                    ) ?: LedgerEntry(entry)
            }
            removeAvailableTargets(request)
        }

        return requests.map { request -> request.withLedgerEntries() }
    }

    private fun removeAvailableTargets(request: SeerrRequestAcquisition) {
        val removed = mutableSetOf<LedgerEntryKey>()
        if (request.request.jellyfinReadiness.movieReady) {
            entries.keys.filterTo(removed) { it.matches(request) }
            entries.keys.removeAll(removed)
            return
        }
        request.request.requestedSeasonNumbers.forEach { seasonNumber ->
            val ready =
                request.request.jellyfinSeasonReadySinceEpochMillis.containsKey(seasonNumber) ||
                    request.request.jellyfinReadiness.seasonReady(
                        seasonNumber,
                        request.request.seasonEpisodeCounts[seasonNumber],
                    )
            if (ready) {
                entries.keys.filterTo(removed) { it.matches(request) && it.seasonNumber == seasonNumber }
            }
        }
        entries.keys.removeAll(removed)
    }

    private fun SeerrRequestAcquisition.withLedgerEntries(): SeerrRequestAcquisition {
        val matching =
            entries
                .filterKeys { it.matches(this) }
                .values
                .map { it.entry }
        val updated =
            when (val current = acquisition) {
                is SeerrAcquisitionState.Movie -> {
                    SeerrAcquisitionState.Movie(aggregateAcquisitionEntries(matching))
                }

                is SeerrAcquisitionState.Tv -> {
                    val assigned =
                        matching.filter { entry ->
                            val seasonNumber = entry.episode?.seasonNumber
                            seasonNumber != null &&
                                (
                                    request.requestedSeasonNumbers.isEmpty() ||
                                        seasonNumber in request.requestedSeasonNumbers
                                )
                        }
                    val seasons =
                        assigned
                            .groupBy { it.episode!!.seasonNumber }
                            .map { (seasonNumber, seasonEntries) ->
                                SeasonAcquisition(
                                    seasonNumber,
                                    aggregateAcquisitionEntries(seasonEntries),
                                )
                            }.sortedBy { it.seasonNumber }
                    current.copy(
                        seasons = seasons,
                        unassignedEntries = matching - assigned.toSet(),
                    )
                }

                SeerrAcquisitionState.Processing -> {
                    when {
                        matching.isEmpty() -> {
                            current
                        }

                        request.mediaType == com.github.damontecres.wholphin.data.model.SeerrItemType.TV -> {
                            SeerrAcquisitionState.Tv(
                                seasons =
                                    matching
                                        .filter { it.episode?.seasonNumber != null }
                                        .groupBy { it.episode!!.seasonNumber }
                                        .map { (seasonNumber, seasonEntries) ->
                                            SeasonAcquisition(
                                                seasonNumber,
                                                aggregateAcquisitionEntries(seasonEntries),
                                            )
                                        }.sortedBy { it.seasonNumber },
                                unassignedEntries = matching.filter { it.episode?.seasonNumber == null },
                            )
                        }

                        else -> {
                            SeerrAcquisitionState.Movie(aggregateAcquisitionEntries(matching))
                        }
                    }
                }

                SeerrAcquisitionState.None -> {
                    if (
                        matching.isNotEmpty() &&
                        request.mediaType == com.github.damontecres.wholphin.data.model.SeerrItemType.TV
                    ) {
                        SeerrAcquisitionState.Tv(
                            seasons =
                                matching
                                    .filter { it.episode?.seasonNumber != null }
                                    .groupBy { it.episode!!.seasonNumber }
                                    .map { (seasonNumber, seasonEntries) ->
                                        SeasonAcquisition(
                                            seasonNumber,
                                            aggregateAcquisitionEntries(seasonEntries),
                                        )
                                    }.sortedBy { it.seasonNumber },
                            unassignedEntries = matching.filter { it.episode?.seasonNumber == null },
                        )
                    } else {
                        current
                    }
                }

                SeerrAcquisitionState.Queueing -> {
                    current
                }
            }
        return copy(acquisition = updated)
    }

    private fun SeerrRequestAcquisition.currentEntries(): List<AcquisitionEntry> =
        when (val state = acquisition) {
            is SeerrAcquisitionState.Movie -> {
                state.aggregate.entries
            }

            is SeerrAcquisitionState.Tv -> {
                state.seasons.flatMap { it.aggregate.entries } + state.unassignedEntries
            }

            SeerrAcquisitionState.None,
            SeerrAcquisitionState.Processing,
            SeerrAcquisitionState.Queueing,
            -> {
                emptyList()
            }
        }

    private fun SeerrRequestAcquisition.entryKey(entry: AcquisitionEntry): LedgerEntryKey =
        LedgerEntryKey(
            mediaId = request.mediaId ?: -request.requestId,
            requestId =
                request.requestId.takeIf {
                    request.mediaType == com.github.damontecres.wholphin.data.model.SeerrItemType.TV
                },
            is4k = request.is4k,
            seasonNumber = entry.episode?.seasonNumber,
            episodeIdentity =
                if (request.mediaType == com.github.damontecres.wholphin.data.model.SeerrItemType.MOVIE) {
                    "media"
                } else {
                    entry.episode?.episodeNumber?.toString()
                        ?: entry.downloadId
                        ?: entry.title
                        ?: "media"
                },
            acquisitionIdentity =
                if (request.mediaType == com.github.damontecres.wholphin.data.model.SeerrItemType.MOVIE) {
                    "media"
                } else {
                    entry.downloadId
                        ?: listOfNotNull(entry.externalId, entry.title, entry.episode?.episodeNumber)
                            .joinToString(":")
                            .ifBlank { "unknown" }
                },
        )

    private data class LedgerEntryKey(
        val mediaId: Int,
        /** TV requests sharing one series media row must retain independent acquisition history. */
        val requestId: Int?,
        val is4k: Boolean,
        val seasonNumber: Int?,
        val episodeIdentity: String,
        val acquisitionIdentity: String,
    ) {
        fun matches(request: SeerrRequestAcquisition): Boolean =
            mediaId == (request.request.mediaId ?: -request.request.requestId) &&
                requestId ==
                request.request.requestId.takeIf {
                    request.request.mediaType == com.github.damontecres.wholphin.data.model.SeerrItemType.TV
                } &&
                is4k == request.request.is4k

        fun sameEpisodeAs(other: LedgerEntryKey): Boolean =
            mediaId == other.mediaId &&
                requestId == other.requestId &&
                is4k == other.is4k &&
                seasonNumber == other.seasonNumber &&
                episodeIdentity == other.episodeIdentity
    }

    private data class LedgerEntry(
        val entry: AcquisitionEntry,
    ) {
        fun merge(
            current: AcquisitionEntry,
            retainByteMaximums: Boolean,
        ): LedgerEntry {
            val decreasedSinceLastPoll =
                entry.sizeLeft != null && current.sizeLeft != null && current.sizeLeft < entry.sizeLeft
            val total = if (retainByteMaximums) maxOfNullable(entry.totalSize, current.totalSize) else current.totalSize
            val completed =
                if (retainByteMaximums) {
                    maxOfNullable(entry.completedSize(), current.completedSize())
                } else {
                    current.completedSize()
                }
            val remaining =
                if (total != null && completed != null) {
                    (total - completed).coerceIn(0.0, total)
                } else {
                    current.sizeLeft
                }
            return LedgerEntry(
                current.copy(
                    totalSize = total,
                    sizeLeft = remaining,
                    presentInQueue = true,
                    absentPollCount = 0,
                    hasObservedProgress =
                        entry.hasObservedProgress || current.hasObservedProgress || decreasedSinceLastPoll,
                    observedSuccessfulTransferCompletion =
                        current.status != AcquisitionStatus.PROBLEM &&
                            (
                                entry.observedSuccessfulTransferCompletion ||
                                    current.observedSuccessfulTransferCompletion
                            ),
                ),
            )
        }
    }
}

private fun AcquisitionEntry.completedSize(): Double? = if (totalSize != null && sizeLeft != null) totalSize - sizeLeft else null

private fun maxOfNullable(
    first: Double?,
    second: Double?,
): Double? = listOfNotNull(first, second).maxOrNull()
