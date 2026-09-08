package com.github.damontecres.wholphin.ui.main

import com.github.damontecres.wholphin.data.model.CatalogMediaType
import com.github.damontecres.wholphin.data.model.DiscoverItem
import com.github.damontecres.wholphin.data.model.MediaKey
import com.github.damontecres.wholphin.data.model.hasCurrentMovieAcquisitionWork
import com.github.damontecres.wholphin.services.AcquisitionIndexSnapshot
import com.github.damontecres.wholphin.services.AcquisitionStateIndex
import com.github.damontecres.wholphin.services.IndexedAcquisition
import com.github.damontecres.wholphin.services.hilt.DefaultCoroutineScope
import com.github.damontecres.wholphin.ui.cards.CardAcquisitionState
import com.github.damontecres.wholphin.ui.cards.CardMediaPresentation
import com.github.damontecres.wholphin.ui.cards.movieCatalogCardPresentation
import com.github.damontecres.wholphin.ui.cards.tvSeasonCardPresentation
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import java.time.Instant
import java.time.OffsetDateTime
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

data class HomeAcquiringItem(
    val key: MediaKey,
    val item: DiscoverItem,
    val verifiedJellyfinItemId: UUID?,
    val verifiedJellyfinSeasonId: UUID? = null,
    val seasonNumber: Int? = null,
    val acquisitionPresentation: CardMediaPresentation?,
    val requestedAtEpochMillis: Long?,
    val requestIds: Set<Int>,
)

data class HomeAcquiringState(
    val items: List<HomeAcquiringItem> = emptyList(),
)

interface HomeAcquiringStateProvider {
    val state: StateFlow<HomeAcquiringState>
}

@Singleton
class HomeAcquiringSource internal constructor(
    acquisitionSnapshots: Flow<AcquisitionIndexSnapshot>,
    scope: CoroutineScope,
) : HomeAcquiringStateProvider {
    @Inject
    constructor(
        acquisitionStateIndex: AcquisitionStateIndex,
        @DefaultCoroutineScope scope: CoroutineScope,
    ) : this(acquisitionStateIndex.state, scope)

    override val state: StateFlow<HomeAcquiringState> =
        acquisitionSnapshots
            .map(AcquisitionIndexSnapshot::toHomeAcquiringState)
            .distinctUntilChanged()
            .stateIn(scope, SharingStarted.Eagerly, HomeAcquiringState())
}

internal fun AcquisitionIndexSnapshot.toHomeAcquiringState(): HomeAcquiringState {
    val acquisitionsByKey = linkedMapOf<MediaKey, MutableList<IndexedAcquisition>>()
    byMediaKey.forEach { (mediaKey, acquisitions) ->
        val supported =
            (mediaKey is MediaKey.Catalog && mediaKey.mediaType == CatalogMediaType.MOVIE) ||
                (
                    mediaKey is MediaKey.Season &&
                        (mediaKey.series as? MediaKey.Catalog)?.mediaType == CatalogMediaType.SERIES
                )
        if (supported) acquisitionsByKey.getOrPut(mediaKey) { mutableListOf() }.addAll(acquisitions)
    }

    val items =
        acquisitionsByKey
            .mapNotNull { (key, indexed) ->
                val active =
                    when (key.mediaType) {
                        CatalogMediaType.MOVIE -> indexed.filter { it.request.hasCurrentMovieAcquisitionWork }
                        CatalogMediaType.SERIES -> indexed.filter { it.tvSeasonTarget?.hasCurrentAcquisitionWork == true }
                    }
                if (active.isEmpty()) return@mapNotNull null
                val requests = active.distinctBy { it.requestIdentity() }
                val orderedRequests = requests.sortedWith(acquisitionRequestOrdering)
                val discoverItem =
                    orderedRequests.firstNotNullOfOrNull { it.request.request.discoverItem }
                        ?: return@mapNotNull null
                val jellyfinIds =
                    requests
                        .mapNotNull { acquisition ->
                            when (key.mediaType) {
                                CatalogMediaType.MOVIE -> acquisition.request.request.jellyfinReadiness.movieItemId
                                CatalogMediaType.SERIES -> acquisition.request.request.jellyfinReadiness.seriesItemId
                            }
                        }.distinct()
                HomeAcquiringItem(
                    key = key,
                    item = discoverItem,
                    verifiedJellyfinItemId = jellyfinIds.singleOrNull(),
                    verifiedJellyfinSeasonId =
                        (key as? MediaKey.Season)?.seasonNumber?.let { seasonNumber ->
                            requests
                                .mapNotNull {
                                    it.request.request.jellyfinReadiness.seasonItemIds[seasonNumber]
                                }.distinct()
                                .singleOrNull()
                        },
                    seasonNumber = (key as? MediaKey.Season)?.seasonNumber,
                    acquisitionPresentation =
                        if (key.mediaType == CatalogMediaType.MOVIE) {
                            requests.movieCatalogCardPresentation()
                        } else {
                            requests.mapNotNull(IndexedAcquisition::tvSeasonCardPresentation).distinct().singleOrNull()
                        },
                    requestedAtEpochMillis =
                        requests
                            .mapNotNull {
                                it.request.request.createdAt
                                    .toEpochMillis()
                            }.maxOrNull(),
                    requestIds = orderedRequests.mapTo(linkedSetOf()) { it.request.request.requestId },
                )
            }.sortedWith(
                compareByDescending<HomeAcquiringItem> { it.requestedAtEpochMillis != null }
                    .thenByDescending { it.requestedAtEpochMillis ?: Long.MIN_VALUE }
                    .thenByDescending { item -> item.requestIds.maxOrNull() ?: Int.MIN_VALUE }
                    .thenBy { it.key.mediaType.ordinal }
                    .thenBy { it.key.tmdbId }
                    .thenBy { it.seasonNumber ?: -1 },
            )
    return HomeAcquiringState(items)
}

private val acquisitionRequestOrdering =
    compareByDescending<IndexedAcquisition> {
        it.request.request.createdAt
            .toEpochMillis() != null
    }.thenByDescending {
        it.request.request.createdAt
            .toEpochMillis() ?: Long.MIN_VALUE
    }.thenByDescending { it.request.request.requestId }
        .thenBy { it.request.request.is4k }

private fun IndexedAcquisition.requestIdentity() = Triple(request.request.requestId, request.request.is4k, origin)

private val MediaKey.mediaType: CatalogMediaType
    get() =
        when (this) {
            is MediaKey.Catalog -> mediaType
            is MediaKey.Season -> (series as MediaKey.Catalog).mediaType
            else -> error("Unsupported Home acquisition key: $this")
        }

private val MediaKey.tmdbId: Int
    get() =
        when (this) {
            is MediaKey.Catalog -> tmdbId
            is MediaKey.Season -> (series as MediaKey.Catalog).tmdbId
            else -> error("Unsupported Home acquisition key: $this")
        }

private fun String?.toEpochMillis(): Long? =
    this?.let { value ->
        runCatching { Instant.parse(value).toEpochMilli() }
            .recoverCatching { OffsetDateTime.parse(value).toInstant().toEpochMilli() }
            .getOrNull()
    }
