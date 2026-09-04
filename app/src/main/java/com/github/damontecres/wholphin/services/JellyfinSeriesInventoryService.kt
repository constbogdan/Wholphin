package com.github.damontecres.wholphin.services

import org.jellyfin.sdk.api.client.ApiClient
import org.jellyfin.sdk.api.client.extensions.itemsApi
import org.jellyfin.sdk.model.api.BaseItemKind
import org.jellyfin.sdk.model.api.ItemFields
import org.jellyfin.sdk.model.api.request.GetItemsRequest
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

data class JellyfinSeriesInventory(
    val seasonItemIds: Map<Int, UUID>,
    val playableEpisodeItemIds: Map<Int, Map<Int, UUID>>,
) {
    val playableEpisodeNumbers: Map<Int, Set<Int>> =
        playableEpisodeItemIds.mapValues { (_, episodes) -> episodes.keys }
}

@Singleton
class JellyfinSeriesInventoryService
    @Inject
    constructor(
        private val api: ApiClient,
    ) {
        suspend fun get(seriesItemId: UUID): JellyfinSeriesInventory {
            val items =
                api.itemsApi.getItems(
                    GetItemsRequest(
                        parentId = seriesItemId,
                        recursive = true,
                        includeItemTypes = listOf(BaseItemKind.SEASON, BaseItemKind.EPISODE),
                        fields = listOf(ItemFields.MEDIA_SOURCES),
                        enableTotalRecordCount = false,
                    ),
                ).content.items
            val seasons =
                items.filter { it.type == BaseItemKind.SEASON }
                    .mapNotNull { season -> season.indexNumber?.let { it to season.id } }
                    .toMap()
            val episodes =
                items.filter { it.type == BaseItemKind.EPISODE && it.mediaSources.orEmpty().isNotEmpty() }
                    .mapNotNull { episode ->
                        val season = episode.parentIndexNumber ?: return@mapNotNull null
                        val number = episode.indexNumber ?: return@mapNotNull null
                        Triple(season, number, episode.id)
                    }.groupBy { it.first }
                    .mapValues { (_, values) -> values.associate { it.second to it.third } }
            return JellyfinSeriesInventory(seasons, episodes)
        }
    }
