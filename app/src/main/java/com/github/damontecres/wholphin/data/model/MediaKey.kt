package com.github.damontecres.wholphin.data.model

import org.jellyfin.sdk.model.api.BaseItemKind
import java.util.UUID

enum class CatalogMediaType {
    MOVIE,
    SERIES,
}

enum class LocalMediaType {
    MOVIE,
    SERIES,
    SEASON,
    EPISODE,
}

sealed interface MediaKey {
    data class Catalog(
        val mediaType: CatalogMediaType,
        val tmdbId: Int,
    ) : MediaKey {
        init {
            require(tmdbId > 0)
        }
    }

    data class Local(
        val serverId: UUID,
        val itemId: UUID,
        val mediaType: LocalMediaType,
    ) : MediaKey

    data class Season(
        val series: MediaKey,
        val seasonNumber: Int,
    ) : MediaKey {
        init {
            require(series.isSeriesIdentity())
            require(seasonNumber >= 0)
        }
    }

    data class Episode(
        val series: MediaKey,
        val seasonNumber: Int,
        val episodeNumber: Int,
    ) : MediaKey {
        init {
            require(series.isSeriesIdentity())
            require(seasonNumber >= 0)
            require(episodeNumber >= 0)
        }
    }
}

fun BaseItem.toMediaKey(
    serverId: UUID,
    seriesKey: MediaKey? = null,
): MediaKey? {
    val localType = type.toLocalMediaType() ?: return null
    val catalogType = type.toCatalogMediaType()
    val tmdbId =
        data.providerIds
            ?.get("Tmdb")
            ?.toIntOrNull()
            ?.takeIf { it > 0 }
    if (catalogType != null && tmdbId != null) return MediaKey.Catalog(catalogType, tmdbId)

    if (seriesKey?.isSeriesIdentity() == true) {
        when (type) {
            BaseItemKind.SEASON -> {
                indexNumber?.takeIf { it >= 0 }?.let {
                    return MediaKey.Season(seriesKey, it)
                }
            }

            BaseItemKind.EPISODE -> {
                val seasonNumber = data.parentIndexNumber?.takeIf { it >= 0 }
                val episodeNumber = indexNumber?.takeIf { it >= 0 }
                if (seasonNumber != null && episodeNumber != null) {
                    return MediaKey.Episode(seriesKey, seasonNumber, episodeNumber)
                }
            }

            else -> {
                Unit
            }
        }
    }
    return MediaKey.Local(serverId, id, localType)
}

fun DiscoverItem.toMediaKey(): MediaKey.Catalog? {
    val mediaType =
        when (type) {
            SeerrItemType.MOVIE -> CatalogMediaType.MOVIE

            SeerrItemType.TV -> CatalogMediaType.SERIES

            SeerrItemType.PERSON,
            SeerrItemType.UNKNOWN,
            -> return null
        }
    return id.takeIf { it > 0 }?.let { MediaKey.Catalog(mediaType, it) }
}

fun SeerrRequestState.toCatalogMediaKey(): MediaKey.Catalog? {
    val mediaType =
        when (mediaType) {
            SeerrItemType.MOVIE -> CatalogMediaType.MOVIE

            SeerrItemType.TV -> CatalogMediaType.SERIES

            SeerrItemType.PERSON,
            SeerrItemType.UNKNOWN,
            -> return null
        }
    return tmdbId?.takeIf { it > 0 }?.let { MediaKey.Catalog(mediaType, it) }
}

private fun MediaKey.isSeriesIdentity(): Boolean =
    when (this) {
        is MediaKey.Catalog -> mediaType == CatalogMediaType.SERIES

        is MediaKey.Local -> mediaType == LocalMediaType.SERIES

        is MediaKey.Season,
        is MediaKey.Episode,
        -> false
    }

private fun BaseItemKind?.toCatalogMediaType(): CatalogMediaType? =
    when (this) {
        BaseItemKind.MOVIE -> CatalogMediaType.MOVIE
        BaseItemKind.SERIES -> CatalogMediaType.SERIES
        else -> null
    }

private fun BaseItemKind?.toLocalMediaType(): LocalMediaType? =
    when (this) {
        BaseItemKind.MOVIE -> LocalMediaType.MOVIE
        BaseItemKind.SERIES -> LocalMediaType.SERIES
        BaseItemKind.SEASON -> LocalMediaType.SEASON
        BaseItemKind.EPISODE -> LocalMediaType.EPISODE
        else -> null
    }
