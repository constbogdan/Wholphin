package com.github.damontecres.wholphin.ui.cards

import com.github.damontecres.wholphin.data.model.AcquisitionStatus
import com.github.damontecres.wholphin.data.model.SeerrAcquisitionState
import com.github.damontecres.wholphin.data.model.SeerrItemType
import com.github.damontecres.wholphin.data.model.SeerrRequestAcquisition
import com.github.damontecres.wholphin.data.model.TvSeasonLifecycle
import com.github.damontecres.wholphin.data.model.TvSeasonTarget
import com.github.damontecres.wholphin.data.model.aggregateAcquisitionEntries
import com.github.damontecres.wholphin.data.model.analyzeTvSeasonAcquisition
import com.github.damontecres.wholphin.data.model.hasActiveProgress
import com.github.damontecres.wholphin.data.model.hasCurrentMovieAcquisitionWork
import com.github.damontecres.wholphin.data.model.isFinishing
import com.github.damontecres.wholphin.services.IndexedAcquisition
import com.github.damontecres.wholphin.services.MediaProductState

data class CardMediaPresentation(
    val acquisitionProgress: Float? = null,
    val acquisitionState: CardAcquisitionState? = null,
)

enum class CardAcquisitionState {
    ACQUIRING,
    QUEUEING,
    QUEUED,
    FINISHING,
}

internal enum class ArtworkProgressSource {
    PLAYBACK,
    ACQUISITION,
}

internal data class ArtworkProgress(
    val fraction: Float,
    val source: ArtworkProgressSource,
)

internal fun resolveArtworkProgress(
    showPlaybackOverlay: Boolean,
    watchedPercent: Double?,
    acquisitionProgress: Float?,
): ArtworkProgress? {
    val playback =
        watchedPercent
            ?.takeIf { showPlaybackOverlay && it.isFinite() && it > 0.0 && it < 100.0 }
            ?.let { ArtworkProgress((it / 100.0).toFloat(), ArtworkProgressSource.PLAYBACK) }
    return playback
        ?: acquisitionProgress
            ?.takeIf { it.isFinite() && it > 0f && it < 1f }
            ?.let { ArtworkProgress(it, ArtworkProgressSource.ACQUISITION) }
}

internal fun MediaProductState.movieRequestCardPresentation(
    requestId: Int,
    is4k: Boolean,
): CardMediaPresentation? =
    acquisitions
        .filter { indexed ->
            indexed.request.request.requestId == requestId &&
                indexed.request.request.is4k == is4k &&
                indexed.request.request.mediaType == SeerrItemType.MOVIE
        }.movieCatalogCardPresentation()

internal fun List<IndexedAcquisition>.movieCatalogCardPresentation(): CardMediaPresentation? {
    val presentations = mapNotNull(IndexedAcquisition::movieCardPresentation).distinct()
    return when (presentations.size) {
        0 -> null
        1 -> presentations.single()
        else -> CardMediaPresentation(acquisitionState = CardAcquisitionState.ACQUIRING)
    }
}

internal fun IndexedAcquisition.movieCardPresentation(): CardMediaPresentation? = request.movieCardPresentation()

internal fun SeerrRequestAcquisition.movieCardPresentation(): CardMediaPresentation? {
    if (!hasCurrentMovieAcquisitionWork) return null
    return when (val acquisition = acquisition) {
        SeerrAcquisitionState.Queueing -> {
            CardMediaPresentation(acquisitionState = CardAcquisitionState.QUEUEING)
        }

        is SeerrAcquisitionState.Movie -> {
            val aggregate = acquisition.aggregate
            when {
                aggregate.isFinishing -> {
                    CardMediaPresentation(acquisitionState = CardAcquisitionState.FINISHING)
                }

                aggregate.status == AcquisitionStatus.DOWNLOADING &&
                    aggregate.hasActiveProgress -> {
                    val progress =
                        aggregate.progress
                            ?.fraction
                            ?.takeIf { it.isFinite() && it > 0.0 && it < 1.0 }
                            ?.toFloat()
                    progress?.let { CardMediaPresentation(acquisitionProgress = it) }
                        ?: CardMediaPresentation(acquisitionState = CardAcquisitionState.QUEUED)
                }

                else -> {
                    CardMediaPresentation(acquisitionState = CardAcquisitionState.QUEUED)
                }
            }
        }

        else -> {
            null
        }
    }
}

internal fun IndexedAcquisition.tvSeasonCardPresentation(): CardMediaPresentation? {
    if (request.acquisition == SeerrAcquisitionState.Queueing) {
        return CardMediaPresentation(acquisitionState = CardAcquisitionState.QUEUEING)
    }
    val target = tvSeasonTarget ?: return null
    return target.tvSeasonCardPresentation()
}

internal fun TvSeasonTarget.tvSeasonCardPresentation(): CardMediaPresentation? {
    if (!hasCurrentAcquisitionWork) return null
    val operationalAggregate =
        aggregate
            ?.let { canonical ->
                if (jellyfinReady) {
                    aggregateAcquisitionEntries(canonical.entries)
                        .analyzeTvSeasonAcquisition(seasonNumber, expectedEpisodeCount, emptySet())
                        .aggregate
                } else {
                    canonical
                }
            }
            ?: return CardMediaPresentation(acquisitionState = CardAcquisitionState.QUEUED)
    when (lifecycle) {
        TvSeasonLifecycle.QUEUED -> {
            return CardMediaPresentation(acquisitionState = CardAcquisitionState.QUEUED)
        }

        TvSeasonLifecycle.FINISHING -> {
            return CardMediaPresentation(acquisitionState = CardAcquisitionState.FINISHING)
        }

        TvSeasonLifecycle.AVAILABLE -> {
            if (operationalAggregate.isFinishing) {
                return CardMediaPresentation(acquisitionState = CardAcquisitionState.FINISHING)
            }
        }

        TvSeasonLifecycle.IN_PROGRESS -> {
            Unit
        }
    }
    val progress =
        operationalAggregate.progress
            ?.fraction
            ?.takeIf { it.isFinite() && it > 0.0 && it < 1.0 }
            ?.toFloat()
    return if (
        operationalAggregate.status == AcquisitionStatus.DOWNLOADING &&
        operationalAggregate.hasActiveProgress &&
        progress != null
    ) {
        CardMediaPresentation(acquisitionProgress = progress)
    } else {
        CardMediaPresentation(acquisitionState = CardAcquisitionState.QUEUED)
    }
}
