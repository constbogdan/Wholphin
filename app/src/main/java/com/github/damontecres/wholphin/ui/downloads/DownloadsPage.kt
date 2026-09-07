package com.github.damontecres.wholphin.ui.downloads

import android.content.Context
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.snapshotFlow
import androidx.compose.runtime.withFrameNanos
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.focus.focusRestorer
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.hilt.lifecycle.viewmodel.compose.hiltViewModel
import androidx.lifecycle.ViewModel
import androidx.lifecycle.compose.LifecycleStartEffect
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.tv.material3.Icon
import androidx.tv.material3.ListItem
import androidx.tv.material3.MaterialTheme
import androidx.tv.material3.Text
import com.github.damontecres.wholphin.R
import com.github.damontecres.wholphin.data.model.AcquisitionAggregate
import com.github.damontecres.wholphin.data.model.AcquisitionStatus
import com.github.damontecres.wholphin.data.model.DiscoverItem
import com.github.damontecres.wholphin.data.model.RequestStatus
import com.github.damontecres.wholphin.data.model.SeerrAcquisitionState
import com.github.damontecres.wholphin.data.model.SeerrAvailability
import com.github.damontecres.wholphin.data.model.SeerrItemType
import com.github.damontecres.wholphin.data.model.SeerrRequestAcquisition
import com.github.damontecres.wholphin.data.model.TV_PROGRESS_GRACE_POLLS
import com.github.damontecres.wholphin.data.model.TvAcquisitionTiming
import com.github.damontecres.wholphin.data.model.TvSeasonLifecycle
import com.github.damontecres.wholphin.data.model.TvSeasonTarget
import com.github.damontecres.wholphin.data.model.activeTiming
import com.github.damontecres.wholphin.data.model.aggregateAcquisitionEntries
import com.github.damontecres.wholphin.data.model.hasActiveProgress
import com.github.damontecres.wholphin.data.model.isFinishing
import com.github.damontecres.wholphin.data.model.isWithinDownloadsCompletedWindow
import com.github.damontecres.wholphin.data.model.isWithinDownloadsWaitingGrace
import com.github.damontecres.wholphin.data.model.toTvSeasonTargets
import com.github.damontecres.wholphin.services.NavigationManager
import com.github.damontecres.wholphin.services.SeerrAcquisitionTracker
import com.github.damontecres.wholphin.ui.cards.CardAcquisitionState
import com.github.damontecres.wholphin.ui.cards.CardMediaPresentation
import com.github.damontecres.wholphin.ui.cards.movieCardPresentation
import com.github.damontecres.wholphin.ui.cards.tvSeasonCardPresentation
import com.github.damontecres.wholphin.ui.nav.Destination
import com.github.damontecres.wholphin.ui.nav.verifiedSeriesDestination
import com.github.damontecres.wholphin.ui.tryRequestFocus
import dagger.hilt.android.lifecycle.HiltViewModel
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.update
import org.jellyfin.sdk.model.api.BaseItemKind
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import javax.inject.Inject
import kotlin.math.roundToInt

@HiltViewModel
class DownloadsViewModel
    @Inject
    constructor(
        private val tracker: SeerrAcquisitionTracker,
        private val navigationManager: NavigationManager,
        @ApplicationContext private val context: Context,
    ) : ViewModel() {
        val state = tracker.state
        val pageVisit = MutableStateFlow(0)
        var focusedKey: String? = null
            private set
        var focusedItemIndex: Int = 0
            private set
        var firstVisibleItemIndex: Int = 0
            private set
        var firstVisibleItemScrollOffset: Int = 0
            private set
        var restoreTargetKey: String? = null
            private set
        var restoreTargetIndex: Int = 0
            private set
        var restoredVisit: Int = -1
        var focusRestoredVisit: Int = -1

        fun pageStarted() {
            restoreTargetKey = focusedKey
            restoreTargetIndex = focusedItemIndex
            pageVisit.update { it + 1 }
            tracker.setFastPolling(true)
            tracker.refreshNow()
        }

        fun pageStopped() = tracker.setFastPolling(false)

        fun open(item: DownloadDisplayItem) {
            val fallbackTitle =
                context.getString(
                    if (item.request.request.mediaType == SeerrItemType.TV) {
                        R.string.tv_series
                    } else {
                        R.string.movie
                    },
                )
            item.destination(fallbackTitle)?.let(navigationManager::navigateTo)
        }

        fun recordFocusedItem(
            key: String,
            index: Int,
        ) {
            focusedKey = key
            focusedItemIndex = index
        }

        fun recordScroll(
            index: Int,
            offset: Int,
        ) {
            firstVisibleItemIndex = index
            firstVisibleItemScrollOffset = offset
        }
    }

@Composable
fun DownloadsPage(
    modifier: Modifier = Modifier,
    viewModel: DownloadsViewModel = hiltViewModel(),
) {
    val trackerState by viewModel.state.collectAsStateWithLifecycle()
    val pageVisit by viewModel.pageVisit.collectAsStateWithLifecycle()
    val sections = (trackerState.requests + trackerState.queueingRequests).toDownloadSections()
    val allItems = sections.active + sections.processing + sections.completed
    val sectionSignature =
        listOf(
            sections.active.map { it.key },
            sections.processing.map { it.key },
            sections.completed.map { it.key },
        )
    val focusRequesters = remember { mutableMapOf<String, FocusRequester>() }
    var previousSectionSignature by remember { mutableStateOf(sectionSignature) }
    val listState =
        rememberLazyListState(
            initialFirstVisibleItemIndex = viewModel.firstVisibleItemIndex,
            initialFirstVisibleItemScrollOffset = viewModel.firstVisibleItemScrollOffset,
        )

    LifecycleStartEffect(Unit) {
        viewModel.pageStarted()
        onStopOrDispose { viewModel.pageStopped() }
    }
    LaunchedEffect(listState) {
        snapshotFlow { listState.firstVisibleItemIndex to listState.firstVisibleItemScrollOffset }
            .collect { (index, offset) -> viewModel.recordScroll(index, offset) }
    }
    val restoreKey =
        viewModel.restoreTargetKey?.takeIf { key -> allItems.any { it.key == key } }
            ?: allItems
                .getOrNull(
                    viewModel.restoreTargetIndex.coerceIn(0, allItems.lastIndex.coerceAtLeast(0)),
                )?.key
    LaunchedEffect(pageVisit, allItems.isNotEmpty()) {
        if (pageVisit > 0 && allItems.isNotEmpty() && viewModel.restoredVisit != pageVisit) {
            viewModel.restoredVisit = pageVisit
            val targetIndex = restoreKey?.let(sections::lazyIndexOf)
            if (targetIndex != null) {
                withFrameNanos { }
                val visible = listState.layoutInfo.visibleItemsInfo.any { it.index == targetIndex }
                if (!visible) listState.scrollToItem(targetIndex)
            }
        }
    }
    LaunchedEffect(sectionSignature) {
        val sectionsChanged = previousSectionSignature != sectionSignature
        previousSectionSignature = sectionSignature
        if (
            sectionsChanged &&
            allItems.isNotEmpty() &&
            viewModel.focusedKey != null &&
            viewModel.restoredVisit == pageVisit
        ) {
            val target =
                refreshFocusTarget(
                    allItems,
                    viewModel.focusedKey,
                    viewModel.focusedItemIndex,
                )
            target?.let {
                val targetIndex = sections.lazyIndexOf(it.key)
                if (
                    targetIndex != null &&
                    listState.layoutInfo.visibleItemsInfo.none { visible -> visible.index == targetIndex }
                ) {
                    listState.scrollToItem(targetIndex)
                }
                withFrameNanos { }
                focusRequesters[it.key]?.tryRequestFocus()
            }
        }
        focusRequesters.keys.retainAll(allItems.mapTo(mutableSetOf()) { it.key })
    }

    Column(
        modifier = modifier.fillMaxSize().padding(horizontal = 28.dp, vertical = 20.dp),
    ) {
        Text(
            text = stringResource(R.string.downloads),
            style = MaterialTheme.typography.headlineLarge,
            modifier = Modifier.padding(bottom = 12.dp),
        )
        if (allItems.isEmpty()) {
            Text(
                text = stringResource(R.string.no_downloads),
                style = MaterialTheme.typography.bodyLarge,
            )
        } else {
            LazyColumn(
                state = listState,
                verticalArrangement = Arrangement.spacedBy(6.dp),
                modifier = Modifier.fillMaxSize().focusRestorer(),
            ) {
                downloadSection(
                    title = R.string.active_downloads,
                    items = sections.active,
                    restoreKey = restoreKey,
                    pageVisit = pageVisit,
                    focusRestoredVisit = viewModel.focusRestoredVisit,
                    onFocusRestored = { viewModel.focusRestoredVisit = pageVisit },
                    onFocused = viewModel::recordFocusedItem,
                    onClick = viewModel::open,
                    focusRequesterFor = { key -> focusRequesters.getOrPut(key) { FocusRequester() } },
                )
                downloadSection(
                    title = R.string.processing_downloads,
                    items = sections.processing,
                    restoreKey = restoreKey,
                    pageVisit = pageVisit,
                    focusRestoredVisit = viewModel.focusRestoredVisit,
                    onFocusRestored = { viewModel.focusRestoredVisit = pageVisit },
                    onFocused = viewModel::recordFocusedItem,
                    onClick = viewModel::open,
                    focusRequesterFor = { key -> focusRequesters.getOrPut(key) { FocusRequester() } },
                )
                downloadSection(
                    title = R.string.recently_completed_downloads,
                    items = sections.completed,
                    restoreKey = restoreKey,
                    pageVisit = pageVisit,
                    focusRestoredVisit = viewModel.focusRestoredVisit,
                    onFocusRestored = { viewModel.focusRestoredVisit = pageVisit },
                    onFocused = viewModel::recordFocusedItem,
                    onClick = viewModel::open,
                    focusRequesterFor = { key -> focusRequesters.getOrPut(key) { FocusRequester() } },
                )
            }
        }
    }
}

internal fun refreshFocusTarget(
    items: List<DownloadDisplayItem>,
    focusedKey: String?,
    previousIndex: Int,
): DownloadDisplayItem? {
    if (items.isEmpty() || focusedKey == null) return null
    return items.firstOrNull { it.key == focusedKey }
        ?: items[previousIndex.coerceIn(0, items.lastIndex)]
}

private fun androidx.compose.foundation.lazy.LazyListScope.downloadSection(
    title: Int,
    items: List<DownloadDisplayItem>,
    restoreKey: String?,
    pageVisit: Int,
    focusRestoredVisit: Int,
    onFocusRestored: () -> Unit,
    onFocused: (String, Int) -> Unit,
    onClick: (DownloadDisplayItem) -> Unit,
    focusRequesterFor: (String) -> FocusRequester,
) {
    if (items.isEmpty()) return
    item(key = "header_$title") {
        Text(
            text = stringResource(title),
            style = MaterialTheme.typography.titleMedium,
            modifier = Modifier.padding(top = 10.dp, bottom = 2.dp),
        )
    }
    items(items, key = { it.key }) { item ->
        val focusRequester = focusRequesterFor(item.key)
        LaunchedEffect(pageVisit) {
            if (item.key == restoreKey && focusRestoredVisit != pageVisit) {
                if (focusRequester.tryRequestFocus()) onFocusRestored()
            }
        }
        DownloadRow(
            item = item,
            onClick = { onClick(item) },
            modifier =
                Modifier
                    .focusRequester(focusRequester)
                    .onFocusChanged {
                        if (it.isFocused) onFocused(item.key, item.flatIndex)
                    },
        )
    }
}

@Composable
private fun DownloadRow(
    item: DownloadDisplayItem,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val fallbackTitle =
        stringResource(
            if (item.request.request.mediaType == SeerrItemType.TV) R.string.tv_series else R.string.movie,
        )
    val title = item.title ?: fallbackTitle
    val displayTitle =
        item.seasonNumber?.let { stringResource(R.string.download_season_title, title, it) } ?: title
    val timing = item.timing?.displayText()
    ListItem(
        selected = false,
        onClick = onClick,
        headlineContent = { Text(displayTitle, maxLines = 1) },
        supportingContent = {
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                Text(stringResource(item.status.stringResource))
                timing?.let { Text(it) }
            }
        },
        trailingContent = {
            if (item.completed) {
                Icon(Icons.Default.CheckCircle, contentDescription = null)
            } else {
                item.progress?.let { progress ->
                    Column {
                        Text("${(progress * 100).roundToInt()}%")
                        LinearProgressIndicator(
                            progress = { progress },
                            modifier = Modifier.width(150.dp),
                        )
                    }
                }
            }
        },
        modifier = modifier.fillMaxWidth(),
    )
}

data class DownloadSections(
    val active: List<DownloadDisplayItem>,
    val processing: List<DownloadDisplayItem>,
    val completed: List<DownloadDisplayItem>,
)

data class DownloadDisplayItem(
    val key: String,
    val title: String?,
    val status: DownloadStatusLabel,
    val progress: Float?,
    val timing: DownloadTiming?,
    val completed: Boolean,
    val request: SeerrRequestAcquisition,
    val seasonNumber: Int? = null,
    val flatIndex: Int = 0,
)

enum class DownloadStatusLabel(
    val stringResource: Int,
) {
    QUEUEING(R.string.download_status_queueing),
    QUEUED(R.string.download_status_queued),
    IN_PROGRESS(R.string.download_status_in_progress),
    FINISHING(R.string.download_status_finishing),
    AVAILABLE(R.string.download_status_available),
    PROBLEM(R.string.download_status_problem),
}

data class DownloadTiming(
    val remaining: String? = null,
    val eta: String? = null,
)

@Composable
private fun DownloadTiming.displayText(): String? =
    when {
        remaining != null && eta != null -> {
            stringResource(
                R.string.download_timing_remaining_eta,
                remaining,
                eta,
            )
        }

        remaining != null -> {
            stringResource(R.string.download_timing_remaining, remaining)
        }

        eta != null -> {
            stringResource(R.string.download_timing_eta, eta)
        }

        else -> {
            null
        }
    }

/** Queue data is authoritative; queue-less requests receive only a short 15-minute grace period. */
internal fun List<SeerrRequestAcquisition>.toDownloadSections(nowEpochMillis: Long = System.currentTimeMillis()): DownloadSections {
    val active = mutableListOf<DownloadDisplayItem>()
    val processing = mutableListOf<DownloadDisplayItem>()
    val completed = mutableListOf<DownloadDisplayItem>()
    forEach { request ->
        val title = request.displayTitle()
        val tvTargets = request.toTvSeasonTargets()
        if (request.acquisition == SeerrAcquisitionState.Queueing) {
            if (request.request.mediaType == SeerrItemType.TV && tvTargets.isNotEmpty()) {
                tvTargets.forEach { target ->
                    processing +=
                        request.queueingRow(
                            key = "${request.request.requestId}_season_${target.seasonNumber}",
                            title = title,
                            seasonNumber = target.seasonNumber,
                        )
                }
            } else {
                val suffix = if (request.request.mediaType == SeerrItemType.MOVIE) "movie" else "tv"
                processing += request.queueingRow("${request.request.requestId}_$suffix", title)
            }
            return@forEach
        }

        if (request.request.mediaType == SeerrItemType.TV && tvTargets.isNotEmpty()) {
            tvTargets.forEach { target ->
                val row = target.toRow(title, nowEpochMillis) ?: return@forEach
                when (row.status) {
                    DownloadStatusLabel.IN_PROGRESS -> active += row

                    DownloadStatusLabel.AVAILABLE -> completed += row

                    DownloadStatusLabel.QUEUEING,
                    DownloadStatusLabel.QUEUED,
                    DownloadStatusLabel.FINISHING,
                    DownloadStatusLabel.PROBLEM,
                    -> processing += row
                }
            }
            return@forEach
        }

        if (request.request.mediaType == SeerrItemType.TV) {
            val unassignedEntries =
                (request.acquisition as? SeerrAcquisitionState.Tv)
                    ?.unassignedEntries
                    .orEmpty()
                    .filter { entry ->
                        entry.status != AcquisitionStatus.PROBLEM &&
                            (
                                entry.presentInQueue ||
                                    (
                                        !entry.observedSuccessfulTransferCompletion &&
                                            entry.absentPollCount <= TV_PROGRESS_GRACE_POLLS
                                    ) ||
                                    entry.observedSuccessfulTransferCompletion
                            )
                    }
            if (unassignedEntries.isNotEmpty()) {
                val aggregate = aggregateAcquisitionEntries(unassignedEntries)
                val row =
                    request.row(
                        key = "${request.request.requestId}_tv",
                        title = title,
                        aggregate = aggregate,
                        completed = false,
                        nowEpochMillis = nowEpochMillis,
                    )
                if (aggregate.hasActiveProgress && !aggregate.isFinishing) {
                    active += row
                } else {
                    processing += row
                }
            } else if (request.request.isWithinDownloadsWaitingGrace(nowEpochMillis)) {
                processing += request.row("${request.request.requestId}_tv", title, null, false, nowEpochMillis)
            }
            return@forEach
        }

        val moviePresentation = request.movieCardPresentation()
        if (request.request.mediaType == SeerrItemType.MOVIE && moviePresentation != null) {
            val aggregate = (request.acquisition as? SeerrAcquisitionState.Movie)?.aggregate
            val row =
                request.row(
                    key = "${request.request.requestId}_movie",
                    title = title,
                    aggregate = aggregate,
                    completed = false,
                    nowEpochMillis = nowEpochMillis,
                    mediaPresentation = moviePresentation,
                )
            if (moviePresentation.acquisitionProgress != null) {
                active += row
            } else {
                processing += row
            }
            return@forEach
        }

        val completedAt = request.request.jellyfinReadySinceEpochMillis ?: request.request.availableSinceEpochMillis
        if (
            request.request.mediaType == SeerrItemType.MOVIE &&
            request.request.jellyfinReadiness.movieReady &&
            completedAt.isWithinDownloadsCompletedWindow(nowEpochMillis)
        ) {
            completed += request.row("${request.request.requestId}_movie", title, null, true, nowEpochMillis)
        }
        if (
            request.request.availability == SeerrAvailability.AVAILABLE ||
            request.request.jellyfinReadiness.movieReady
        ) {
            return@forEach
        }

        if (request.request.isWithinDownloadsWaitingGrace(nowEpochMillis)) {
            processing += request.row("${request.request.requestId}_movie", title, null, false, nowEpochMillis)
        }
    }

    val completedByKey = completed.associateBy { it.key }
    val activeByKey = active.filterNot { it.key in completedByKey }.associateBy { it.key }
    val processingByKey =
        processing
            .filterNot { it.key in completedByKey || it.key in activeByKey }
            .associateBy { it.key }
    val exclusiveActive = activeByKey.values.toList()
    val exclusiveProcessing = processingByKey.values.toList()
    val exclusiveCompleted = completedByKey.values.toList()
    val indices =
        (exclusiveActive + exclusiveProcessing + exclusiveCompleted)
            .mapIndexed { index, item -> item.key to index }
            .toMap()
    return DownloadSections(
        exclusiveActive.map { it.copy(flatIndex = indices.getValue(it.key)) },
        exclusiveProcessing.map { it.copy(flatIndex = indices.getValue(it.key)) },
        exclusiveCompleted.map { it.copy(flatIndex = indices.getValue(it.key)) },
    )
}

private fun TvSeasonTarget.toRow(
    seriesTitle: String?,
    nowEpochMillis: Long,
): DownloadDisplayItem? {
    val mediaPresentation = tvSeasonCardPresentation()
    if (mediaPresentation != null) {
        return DownloadDisplayItem(
            key = "${request.request.requestId}_season_$seasonNumber",
            title = seriesTitle,
            status = mediaPresentation.downloadStatus(),
            progress = mediaPresentation.acquisitionProgress,
            timing =
                mediaPresentation.acquisitionProgress?.let {
                    acquisitionProjection.activeTiming(nowEpochMillis)?.toDownloadTiming()
                },
            completed = false,
            request = request,
            seasonNumber = seasonNumber,
        )
    }
    val hasAcquisitionEvidence = aggregate?.entries.orEmpty().isNotEmpty()
    val shouldDisplay =
        when (lifecycle) {
            TvSeasonLifecycle.AVAILABLE -> {
                completedAtEpochMillis.isWithinDownloadsCompletedWindow(nowEpochMillis)
            }

            TvSeasonLifecycle.FINISHING -> {
                if (seerrAvailability == SeerrAvailability.AVAILABLE) {
                    completedAtEpochMillis.isWithinDownloadsCompletedWindow(nowEpochMillis)
                } else {
                    true
                }
            }

            TvSeasonLifecycle.IN_PROGRESS -> {
                true
            }

            TvSeasonLifecycle.QUEUED -> {
                hasAcquisitionEvidence || request.request.isWithinDownloadsWaitingGrace(nowEpochMillis)
            }
        }
    if (!shouldDisplay) return null
    val timing = acquisitionProjection.activeTiming(nowEpochMillis)
    return DownloadDisplayItem(
        key = "${request.request.requestId}_season_$seasonNumber",
        title = seriesTitle,
        status =
            when (lifecycle) {
                TvSeasonLifecycle.QUEUED -> DownloadStatusLabel.QUEUED
                TvSeasonLifecycle.IN_PROGRESS -> DownloadStatusLabel.IN_PROGRESS
                TvSeasonLifecycle.FINISHING -> DownloadStatusLabel.FINISHING
                TvSeasonLifecycle.AVAILABLE -> DownloadStatusLabel.AVAILABLE
            },
        progress =
            if (lifecycle == TvSeasonLifecycle.IN_PROGRESS) {
                aggregate
                    ?.progress
                    ?.fraction
                    ?.toFloat()
                    ?.takeIf { it.isFinite() && it > 0f && it < 1f }
            } else {
                null
            },
        timing =
            if (lifecycle == TvSeasonLifecycle.IN_PROGRESS) {
                timing?.toDownloadTiming()
            } else {
                null
            },
        completed = lifecycle == TvSeasonLifecycle.AVAILABLE,
        request = request,
        seasonNumber = seasonNumber,
    )
}

private fun DownloadSections.lazyIndexOf(key: String): Int? {
    var lazyIndex = 0
    for (section in listOf(active, processing, completed)) {
        if (section.isEmpty()) continue
        lazyIndex++
        section.forEach { item ->
            if (item.key == key) return lazyIndex
            lazyIndex++
        }
    }
    return null
}

private fun SeerrRequestAcquisition.row(
    key: String,
    title: String?,
    aggregate: AcquisitionAggregate?,
    completed: Boolean,
    nowEpochMillis: Long,
    seasonNumber: Int? = null,
    mediaPresentation: CardMediaPresentation? = null,
): DownloadDisplayItem =
    DownloadDisplayItem(
        key = key,
        title = title,
        status =
            mediaPresentation?.downloadStatus() ?: when {
                completed -> DownloadStatusLabel.AVAILABLE
                request.status == RequestStatus.FAILURE -> DownloadStatusLabel.PROBLEM
                aggregate == null -> DownloadStatusLabel.QUEUED
                aggregate.isFinishing -> DownloadStatusLabel.FINISHING
                aggregate.hasActiveProgress -> DownloadStatusLabel.IN_PROGRESS
                else -> DownloadStatusLabel.QUEUED
            },
        // ARR may report 100% before import; reserve 100%/Available for Jellyfin readiness.
        progress =
            if (mediaPresentation != null) {
                mediaPresentation.acquisitionProgress
            } else if (aggregate?.hasActiveProgress == true && !aggregate.isFinishing) {
                aggregate.progress
                    ?.fraction
                    ?.toFloat()
                    ?.takeIf { it.isFinite() && it > 0f && it < 1f }
            } else {
                null
            },
        timing =
            if (mediaPresentation != null) {
                mediaPresentation.acquisitionProgress?.let { aggregate?.activeTiming(nowEpochMillis) }
            } else {
                aggregate?.activeTiming(nowEpochMillis)
            },
        completed = completed,
        request = this,
        seasonNumber = seasonNumber,
    )

private fun CardMediaPresentation.downloadStatus(): DownloadStatusLabel =
    when {
        acquisitionProgress != null -> DownloadStatusLabel.IN_PROGRESS
        acquisitionState == CardAcquisitionState.QUEUEING -> DownloadStatusLabel.QUEUEING
        acquisitionState == CardAcquisitionState.FINISHING -> DownloadStatusLabel.FINISHING
        else -> DownloadStatusLabel.QUEUED
    }

private fun SeerrRequestAcquisition.queueingRow(
    key: String,
    title: String?,
    seasonNumber: Int? = null,
): DownloadDisplayItem =
    DownloadDisplayItem(
        key = key,
        title = title,
        status = DownloadStatusLabel.QUEUEING,
        progress = null,
        timing = null,
        completed = false,
        request = this,
        seasonNumber = seasonNumber,
    )

internal fun DownloadDisplayItem.destination(fallbackTitle: String): Destination? {
    val state = request.request
    if (completed) {
        if (state.mediaType == SeerrItemType.MOVIE) {
            state.jellyfinReadiness.movieItemId?.let { id ->
                return Destination.MediaItem(id, BaseItemKind.MOVIE)
            }
        } else if (
            state.mediaType == SeerrItemType.TV &&
            seasonNumber != null &&
            state.jellyfinReadiness.seasonReady(
                seasonNumber,
                state.seasonEpisodeCounts[seasonNumber],
            )
        ) {
            state.jellyfinReadiness.seriesItemId?.let { id ->
                val seasonId = state.jellyfinReadiness.seasonItemIds[seasonNumber]
                return verifiedSeriesDestination(id, seasonId, seasonNumber)
            }
        }
    }
    val discoverItem = state.discoverItem ?: request.toDiscoverItem(title ?: fallbackTitle)
    return discoverItem?.let { Destination.DiscoveredItem(it) }
}

private fun SeerrRequestAcquisition.displayTitle(): String? =
    request.discoverItem?.title ?: when (val state = acquisition) {
        SeerrAcquisitionState.Queueing -> {
            null
        }

        is SeerrAcquisitionState.Movie -> {
            state.aggregate.entries.firstNotNullOfOrNull { it.title }
        }

        is SeerrAcquisitionState.Tv -> {
            state.seasons
                .asSequence()
                .flatMap { it.aggregate.entries.asSequence() }
                .plus(state.unassignedEntries.asSequence())
                .firstNotNullOfOrNull { it.title }
        }

        else -> {
            null
        }
    }

private fun SeerrRequestAcquisition.toDiscoverItem(title: String): DiscoverItem? =
    request.tmdbId?.let { tmdbId ->
        DiscoverItem(
            id = tmdbId,
            type = request.mediaType,
            title = title,
            subtitle = null,
            overview = null,
            availability = request.availability,
            releaseDate = null,
            posterUrl = null,
            backDropUrl = null,
            logoUrl = null,
            jellyfinItemId = null,
        )
    }

private fun AcquisitionAggregate.activeTiming(nowEpochMillis: Long): DownloadTiming? {
    if (!hasActiveProgress || isFinishing) return null
    val entry =
        entries.firstOrNull {
            it.presentInQueue &&
                it.status == AcquisitionStatus.DOWNLOADING &&
                it.hasObservedProgress &&
                it.sizeLeft?.let { left -> left > 0.0 } == true
        } ?: return null
    val remaining = entry.timeLeft?.takeUnless { it.isZeroDuration() || it.isBlank() }
    val eta = entry.estimatedCompletionTime?.toLocalEta(nowEpochMillis)
    return DownloadTiming(remaining = remaining, eta = eta)
}

private fun TvAcquisitionTiming.toDownloadTiming(): DownloadTiming =
    DownloadTiming(
        remaining = remaining,
        eta =
            etaEpochMillis?.let {
                Instant
                    .ofEpochMilli(it)
                    .atZone(ZoneId.systemDefault())
                    .format(DateTimeFormatter.ofPattern("HH:mm"))
            },
    )

private fun String.toLocalEta(nowEpochMillis: Long): String? {
    val instant =
        runCatching { Instant.parse(this) }
            .recoverCatching { OffsetDateTime.parse(this).toInstant() }
            .getOrNull()
            ?: return null
    return instant
        .takeIf { it.toEpochMilli() > nowEpochMillis }
        ?.atZone(ZoneId.systemDefault())
        ?.format(DateTimeFormatter.ofPattern("HH:mm"))
}

private fun String?.isZeroDuration(): Boolean = this?.trim() in setOf("00:00:00", "0:00:00", "00:00")
