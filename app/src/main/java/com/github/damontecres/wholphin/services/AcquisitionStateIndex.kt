package com.github.damontecres.wholphin.services

import com.github.damontecres.wholphin.data.model.MediaKey
import com.github.damontecres.wholphin.data.model.SeerrItemType
import com.github.damontecres.wholphin.data.model.SeerrRequestAcquisition
import com.github.damontecres.wholphin.data.model.TvSeasonTarget
import com.github.damontecres.wholphin.data.model.toCatalogMediaKey
import com.github.damontecres.wholphin.data.model.toTvSeasonTargets
import com.github.damontecres.wholphin.services.hilt.DefaultCoroutineScope
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import javax.inject.Inject
import javax.inject.Singleton

enum class AcquisitionIndexOrigin {
    AUTHORITATIVE,
    QUEUEING,
}

data class IndexedAcquisition(
    val request: SeerrRequestAcquisition,
    val seasonNumber: Int? = null,
    val tvSeasonTarget: TvSeasonTarget? = null,
    val origin: AcquisitionIndexOrigin,
)

data class AcquisitionIndexSnapshot(
    val byMediaKey: Map<MediaKey, List<IndexedAcquisition>> = emptyMap(),
    val unresolved: List<IndexedAcquisition> = emptyList(),
)

@Singleton
class AcquisitionStateIndex
    @Inject
    constructor(
        tracker: SeerrAcquisitionTracker,
        @param:DefaultCoroutineScope scope: CoroutineScope,
    ) {
        val state: StateFlow<AcquisitionIndexSnapshot> =
            tracker.state
                .map(SeerrAcquisitionTrackerState::toAcquisitionIndex)
                .stateIn(scope, SharingStarted.Eagerly, AcquisitionIndexSnapshot())
    }

internal fun SeerrAcquisitionTrackerState.toAcquisitionIndex(): AcquisitionIndexSnapshot {
    val indexed = linkedMapOf<MediaKey, MutableList<IndexedAcquisition>>()
    val unresolved = mutableListOf<IndexedAcquisition>()
    val entries =
        requests.map { IndexedAcquisition(it, origin = AcquisitionIndexOrigin.AUTHORITATIVE) } +
            queueingRequests.map { IndexedAcquisition(it, origin = AcquisitionIndexOrigin.QUEUEING) }

    entries.forEach { entry ->
        val catalog = entry.request.request.toCatalogMediaKey()
        when {
            catalog == null -> {
                unresolved += entry
            }

            entry.request.request.mediaType == SeerrItemType.MOVIE -> {
                indexed.getOrPut(catalog) { mutableListOf() } += entry
            }

            entry.request.request.mediaType == SeerrItemType.TV -> {
                val targets = entry.request.toTvSeasonTargets()
                if (targets.isEmpty()) {
                    unresolved += entry
                } else {
                    targets.forEach { target ->
                        val seasonEntry =
                            entry.copy(
                                seasonNumber = target.seasonNumber,
                                tvSeasonTarget = target,
                            )
                        indexed.getOrPut(MediaKey.Season(catalog, target.seasonNumber)) { mutableListOf() } += seasonEntry
                    }
                }
            }

            else -> {
                unresolved += entry
            }
        }
    }

    val ordering =
        compareBy<IndexedAcquisition>(
            { it.request.request.requestId },
            { it.request.request.is4k },
            { it.origin.ordinal },
        )
    return AcquisitionIndexSnapshot(
        byMediaKey = indexed.mapValues { (_, values) -> values.sortedWith(ordering) },
        unresolved = unresolved.sortedWith(ordering),
    )
}
