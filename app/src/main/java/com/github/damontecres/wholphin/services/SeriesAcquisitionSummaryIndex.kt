package com.github.damontecres.wholphin.services

import com.github.damontecres.wholphin.data.model.CatalogMediaType
import com.github.damontecres.wholphin.data.model.MediaKey
import com.github.damontecres.wholphin.services.hilt.DefaultCoroutineScope
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import javax.inject.Inject
import javax.inject.Singleton

enum class SeriesAcquisitionSummary {
    NONE,
    ACTIVE,
}

@Singleton
class SeriesAcquisitionSummaryIndex internal constructor(
    acquisitionSnapshots: Flow<AcquisitionIndexSnapshot>,
    scope: CoroutineScope,
) {
    @Inject
    constructor(
        acquisitionStateIndex: AcquisitionStateIndex,
        @DefaultCoroutineScope scope: CoroutineScope,
    ) : this(acquisitionStateIndex.state, scope)

    val state: StateFlow<Map<MediaKey.Catalog, SeriesAcquisitionSummary>> =
        acquisitionSnapshots
            .map(AcquisitionIndexSnapshot::toSeriesAcquisitionSummaries)
            .distinctUntilChanged()
            .stateIn(scope, SharingStarted.Eagerly, emptyMap())

    fun observe(keys: Set<MediaKey.Catalog>): Flow<Map<MediaKey.Catalog, SeriesAcquisitionSummary>> {
        val requestedKeys = keys.filterTo(mutableSetOf()) { it.mediaType == CatalogMediaType.SERIES }
        return state
            .map { summaries -> summaries.filterKeys(requestedKeys::contains) }
            .distinctUntilChanged()
    }
}

internal fun AcquisitionIndexSnapshot.toSeriesAcquisitionSummaries():
    Map<MediaKey.Catalog, SeriesAcquisitionSummary> =
    buildMap {
        byMediaKey.forEach { (key, acquisitions) ->
            val seriesKey = (key as? MediaKey.Season)?.series as? MediaKey.Catalog ?: return@forEach
            if (seriesKey.mediaType != CatalogMediaType.SERIES) return@forEach
            if (acquisitions.any { it.tvSeasonTarget?.hasCurrentAcquisitionWork == true }) {
                put(seriesKey, SeriesAcquisitionSummary.ACTIVE)
            }
        }
    }
