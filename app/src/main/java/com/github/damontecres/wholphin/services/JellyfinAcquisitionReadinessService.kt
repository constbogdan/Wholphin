package com.github.damontecres.wholphin.services

import com.github.damontecres.wholphin.data.model.JellyfinAcquisitionReadiness
import com.github.damontecres.wholphin.data.model.SeerrItemType
import com.github.damontecres.wholphin.data.model.SeerrRequestAcquisition
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import org.jellyfin.sdk.api.client.ApiClient
import org.jellyfin.sdk.api.client.extensions.itemsApi
import org.jellyfin.sdk.model.api.BaseItemKind
import org.jellyfin.sdk.model.api.ItemFields
import org.jellyfin.sdk.model.api.request.GetItemsRequest
import timber.log.Timber
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class JellyfinAcquisitionReadinessService
    @Inject
    constructor(
        private val api: ApiClient,
        private val seriesInventoryService: JellyfinSeriesInventoryService,
    ) {
        suspend fun enrich(requests: List<SeerrRequestAcquisition>): List<SeerrRequestAcquisition> =
            coroutineScope {
                val semaphore = Semaphore(3)
                requests
                    .map { acquisition ->
                        async {
                            if (!acquisition.needsJellyfinReadinessCheck()) return@async acquisition
                            semaphore.withPermit {
                                runCatching { acquisition.withJellyfinReadiness() }
                                    .onFailure {
                                        Timber.w(it, "Unable to resolve Jellyfin readiness for request %s", acquisition.request.requestId)
                                    }.getOrDefault(acquisition)
                            }
                        }
                    }.awaitAll()
            }

        private suspend fun SeerrRequestAcquisition.withJellyfinReadiness(): SeerrRequestAcquisition {
            val kind =
                when (request.mediaType) {
                    SeerrItemType.MOVIE -> BaseItemKind.MOVIE
                    SeerrItemType.TV -> BaseItemKind.SERIES
                    else -> return this
                }
            val item = findJellyfinItem(kind) ?: return this

            val readiness =
                if (request.mediaType == SeerrItemType.MOVIE) {
                    JellyfinAcquisitionReadiness(movieItemId = item.id.takeIf { item.mediaSources.orEmpty().isNotEmpty() })
                } else {
                    val inventory = seriesInventoryService.get(item.id)
                    JellyfinAcquisitionReadiness(
                        seriesItemId = item.id,
                        seasonItemIds = inventory.seasonItemIds,
                        episodeItemIds = inventory.playableEpisodeItemIds,
                    )
                }
            return copy(request = request.copy(jellyfinReadiness = readiness))
        }

        private suspend fun SeerrRequestAcquisition.findJellyfinItem(kind: BaseItemKind) =
            request.discoverItem
                ?.jellyfinItemId
                ?.let { jellyfinItemId ->
                    api.itemsApi
                        .getItems(
                            GetItemsRequest(
                                ids = listOf(jellyfinItemId),
                                includeItemTypes = listOf(kind),
                                fields = listOf(ItemFields.PROVIDER_IDS, ItemFields.MEDIA_SOURCES),
                                limit = 1,
                                enableTotalRecordCount = false,
                            ),
                        ).content.items
                        .firstOrNull { it.id == jellyfinItemId && it.type == kind }
                }
                ?: findJellyfinItemByTmdb(kind)

        private suspend fun SeerrRequestAcquisition.findJellyfinItemByTmdb(kind: BaseItemKind) =
            request.tmdbId?.let { tmdbId ->
                val title = request.discoverItem?.title ?: return@let null
                api.itemsApi
                    .getItems(
                        GetItemsRequest(
                            searchTerm = title,
                            recursive = true,
                            includeItemTypes = listOf(kind),
                            fields = listOf(ItemFields.PROVIDER_IDS, ItemFields.MEDIA_SOURCES),
                            limit = 20,
                            enableTotalRecordCount = false,
                        ),
                    ).content.items
                    .firstOrNull { it.providerIds?.get("Tmdb") == tmdbId.toString() }
            }
    }

internal fun SeerrRequestAcquisition.needsJellyfinReadinessCheck(): Boolean =
    when (request.mediaType) {
        SeerrItemType.MOVIE -> {
            !request.jellyfinReadiness.movieReady
        }

        SeerrItemType.TV -> {
            request.requestedSeasonNumbers.any { season ->
                !request.jellyfinReadiness.seasonReady(season, request.seasonEpisodeCounts[season])
            }
        }

        else -> {
            false
        }
    }
