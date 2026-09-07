package com.github.damontecres.wholphin.services

import com.github.damontecres.wholphin.data.model.CatalogMediaType
import com.github.damontecres.wholphin.data.model.LocalMediaType
import com.github.damontecres.wholphin.data.model.MediaKey
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.distinctUntilChanged
import javax.inject.Inject
import javax.inject.Singleton

data class MediaProductState(
    val acquisitions: List<IndexedAcquisition> = emptyList(),
    val integrity: IntegrityState? = null,
)

data class SeasonMediaAlias(
    val local: MediaKey.Season,
    val catalog: MediaKey.Season,
) {
    init {
        require((local.series as? MediaKey.Local)?.mediaType == LocalMediaType.SERIES)
        require((catalog.series as? MediaKey.Catalog)?.mediaType == CatalogMediaType.SERIES)
        require(local.seasonNumber == catalog.seasonNumber)
    }
}

@Singleton
class MediaProductStateCoordinator internal constructor(
    private val acquisitionSnapshots: Flow<AcquisitionIndexSnapshot>,
    private val observeIntegrity: (Set<MediaKey>) -> Flow<Map<MediaKey, IntegrityState>>,
) {
    @Inject
    constructor(
        acquisitionStateIndex: AcquisitionStateIndex,
        integrityStateSource: IntegrityStateSource,
    ) : this(acquisitionStateIndex.state, integrityStateSource::observe)

    fun observe(
        keys: Set<MediaKey>,
        seasonAliases: Set<SeasonMediaAlias> = emptySet(),
    ): Flow<Map<MediaKey, MediaProductState>> {
        val requestedKeys = keys.toSet()
        val aliases = SafeSeasonAliases(seasonAliases)
        val integrityKeys = requestedKeys + requestedKeys.mapNotNull(aliases::uniqueCounterpart)
        return combine(acquisitionSnapshots, observeIntegrity(integrityKeys)) { acquisition, integrity ->
            requestedKeys.associateWith { key ->
                val counterpart = aliases.uniqueCounterpart(key)
                val integrityState = integrity[key] ?: counterpart?.let(integrity::get)
                val acquisitionKeys =
                    buildSet {
                        add(key)
                        counterpart?.let(::add)
                        integrityState?.catalogSeasonAlias?.let(::add)
                    }
                val acquisitions =
                    if (acquisitionKeys.count { it != key } > 1) {
                        acquisition.byMediaKey[key].orEmpty()
                    } else {
                        acquisitionKeys.flatMap { acquisition.byMediaKey[it].orEmpty() }.distinct()
                    }
                MediaProductState(acquisitions = acquisitions, integrity = integrityState)
            }
        }.distinctUntilChanged()
    }
}

private class SafeSeasonAliases(
    aliases: Set<SeasonMediaAlias>,
) {
    private val counterparts: Map<MediaKey, Set<MediaKey>> =
        buildMap {
            aliases.forEach { alias ->
                put(alias.local, get(alias.local).orEmpty() + alias.catalog)
                put(alias.catalog, get(alias.catalog).orEmpty() + alias.local)
            }
        }

    fun uniqueCounterpart(key: MediaKey): MediaKey? = counterparts[key]?.singleOrNull()
}
