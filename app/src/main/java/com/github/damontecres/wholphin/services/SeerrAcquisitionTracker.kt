package com.github.damontecres.wholphin.services

import com.github.damontecres.wholphin.data.model.AcquisitionStatus
import com.github.damontecres.wholphin.data.model.SeerrAcquisitionState
import com.github.damontecres.wholphin.data.model.SeerrAvailability
import com.github.damontecres.wholphin.data.model.SeerrRequestAcquisition
import com.github.damontecres.wholphin.data.model.authoritativelyRepresentedSeasons
import com.github.damontecres.wholphin.data.model.hasAuthoritativeDownloadsRepresentation
import com.github.damontecres.wholphin.data.model.isWithinDownloadsCompletedWindow
import com.github.damontecres.wholphin.data.model.isWithinDownloadsWaitingGrace
import com.github.damontecres.wholphin.util.WholphinDispatchers
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.update
import java.util.concurrent.atomic.AtomicBoolean
import java.time.Instant
import java.time.OffsetDateTime
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withTimeoutOrNull
import timber.log.Timber
import javax.inject.Inject
import javax.inject.Singleton

data class SeerrAcquisitionTrackerState(
    val session: SeerrAcquisitionSession? = null,
    val requests: List<SeerrRequestAcquisition> = emptyList(),
    val queueingRequests: List<SeerrRequestAcquisition> = emptyList(),
    val isRunning: Boolean = false,
    val isRefreshing: Boolean = false,
    val consecutiveFailures: Int = 0,
    val lastSuccessfulRefreshEpochMillis: Long? = null,
    val lastError: String? = null,
) {
    val activeAcquisitionCount: Int
        get() = requests.count { it.isActiveAcquisition() }

    val problemCount: Int
        get() = requests.count { it.hasProblem() }
}

data class SeerrAcquisitionSession(
    val serverId: Int,
    val userId: Int,
)

@Singleton
class SeerrAcquisitionTracker internal constructor(
    private val loadRequests: suspend () -> List<SeerrRequestAcquisition>,
    private val enrichRequests: suspend (List<SeerrRequestAcquisition>) -> List<SeerrRequestAcquisition> = { it },
    private val resolveJellyfinReadiness: suspend (List<SeerrRequestAcquisition>) -> List<SeerrRequestAcquisition> = { it },
    private val sessions: Flow<SeerrAcquisitionSession?>,
    dispatcher: CoroutineDispatcher,
    private val pollIntervalMillis: Long,
    private val maxBackoffMillis: Long,
    private val currentTimeMillis: () -> Long,
) {
    @Inject
    constructor(
        seerrService: SeerrService,
        seerrServerRepository: SeerrServerRepository,
        jellyfinReadinessService: JellyfinAcquisitionReadinessService,
    ) : this(
        loadRequests = seerrService::getRequestAcquisitions,
        enrichRequests = seerrService::enrichRequestAcquisitions,
        resolveJellyfinReadiness = jellyfinReadinessService::enrich,
        sessions =
            seerrServerRepository.connection
                .map { connection ->
                    (connection as? SeerrConnectionStatus.Success)?.current?.let { current ->
                        SeerrAcquisitionSession(
                            serverId = current.server.id,
                            userId = current.config.id,
                        )
                    }
                }.distinctUntilChanged(),
        dispatcher = WholphinDispatchers.IO,
        pollIntervalMillis = DEFAULT_POLL_INTERVAL_MILLIS,
        maxBackoffMillis = MAX_BACKOFF_MILLIS,
        currentTimeMillis = System::currentTimeMillis,
    )

    private val scope = CoroutineScope(SupervisorJob() + dispatcher)
    private val refreshRequests = Channel<Unit>(Channel.CONFLATED)
    private val fastPolling = AtomicBoolean(false)
    private val ledger = SeerrAcquisitionLedger()
    private val queueingLock = Any()
    private val queueingRequests = linkedMapOf<QueueingKey, QueueingRequest>()
    private val _state = MutableStateFlow(SeerrAcquisitionTrackerState())
    val state: StateFlow<SeerrAcquisitionTrackerState> = _state

    private var foregroundJob: Job? = null

    @Synchronized
    fun startForeground() {
        if (foregroundJob?.isActive == true) return
        _state.update { it.copy(isRunning = true) }
        foregroundJob =
            scope.launch {
                sessions.collectLatest { session ->
                    if (session == null) {
                        resetSession(null)
                    } else {
                        if (_state.value.session != session) resetSession(session)
                        poll(session)
                    }
                }
            }
    }

    @Synchronized
    fun stopForeground() {
        foregroundJob?.cancel()
        foregroundJob = null
        _state.update { it.copy(isRunning = false, isRefreshing = false) }
    }

    fun refreshNow() {
        if (_state.value.isRunning) refreshRequests.trySend(Unit)
    }

    fun registerQueueing(submission: SeerrRequestAcquisition) {
        val now = currentTimeMillis()
        val queueingSubmission = submission.queueingTarget() ?: return
        synchronized(queueingLock) {
            pruneExpiredQueueing(now)
            val key = QueueingKey(queueingSubmission.request.requestId, queueingSubmission.request.is4k)
            val existing = queueingRequests[key]?.acquisition
            val combined =
                if (
                    existing != null &&
                    queueingSubmission.request.mediaType ==
                    com.github.damontecres.wholphin.data.model.SeerrItemType.TV
                ) {
                    val seasons =
                        existing.request.requestedSeasonNumbers +
                            queueingSubmission.request.requestedSeasonNumbers
                    queueingSubmission.copy(
                        request =
                            queueingSubmission.request.copy(
                                requestedSeasonNumbers = seasons,
                                seasonEpisodeCounts =
                                    existing.request.seasonEpisodeCounts +
                                        queueingSubmission.request.seasonEpisodeCounts,
                            ),
                    )
                } else {
                    queueingSubmission
                }
            queueingRequests[key] =
                QueueingRequest(
                    acquisition = combined.copy(acquisition = SeerrAcquisitionState.Queueing),
                    expiresAtEpochMillis = now + QUEUEING_TTL_MILLIS,
                )
            publishQueueing()
        }
    }

    /** Temporarily use the foreground-detail cadence without starting a second polling loop. */
    fun setFastPolling(enabled: Boolean) {
        if (fastPolling.getAndSet(enabled) != enabled) refreshNow()
    }

    private suspend fun poll(session: SeerrAcquisitionSession) {
        var failures = 0
        while (currentCoroutineContext().isActive) {
            try {
                _state.update { it.copy(isRefreshing = true) }
                val now = currentTimeMillis()
                val fetched = stampAvailabilityTransitions(loadRequests(), _state.value.requests, now)
                val withRetainedReadiness = retainJellyfinReadiness(fetched, _state.value.requests)
                val retained =
                    enrichRequests(
                        retainActiveAndRecent(withRetainedReadiness, _state.value.requests, now),
                    )
                val reconciled = ledger.reconcile(retained)
                val requests =
                    stampJellyfinReadinessTransitions(
                        resolveJellyfinReadiness(reconciled),
                        _state.value.requests,
                        now,
                    )
                val queueing = reconcileQueueing(requests, now)
                failures = 0
                _state.update {
                    it.copy(
                        session = session,
                        requests = requests,
                        queueingRequests = queueing,
                        isRefreshing = false,
                        consecutiveFailures = 0,
                        lastSuccessfulRefreshEpochMillis = currentTimeMillis(),
                        lastError = null,
                    )
                }
            } catch (ex: CancellationException) {
                throw ex
            } catch (ex: Exception) {
                failures++
                Timber.w(ex, "Unable to refresh Seerr acquisition state")
                val queueing = synchronized(queueingLock) {
                    pruneExpiredQueueing(currentTimeMillis())
                    queueingRequests.values.map { it.acquisition }
                }
                _state.update {
                    it.copy(
                        queueingRequests = queueing,
                        isRefreshing = false,
                        consecutiveFailures = failures,
                        lastError = ex.localizedMessage ?: ex::class.simpleName,
                    )
                }
            }

            val waitMillis = backoffMillis(failures)
            withTimeoutOrNull(waitMillis) { refreshRequests.receive() }
        }
    }

    private fun resetSession(session: SeerrAcquisitionSession?) {
        ledger.clear()
        synchronized(queueingLock) { queueingRequests.clear() }
        _state.update {
            SeerrAcquisitionTrackerState(
                session = session,
                isRunning = it.isRunning,
            )
        }
    }

    private fun backoffMillis(failures: Int): Long {
        val baseInterval = if (fastPolling.get()) FAST_POLL_INTERVAL_MILLIS else pollIntervalMillis
        if (failures <= 0) return baseInterval
        val multiplier = 1L shl (failures - 1).coerceAtMost(10)
        return (baseInterval * multiplier).coerceAtMost(maxBackoffMillis)
    }

    private fun reconcileQueueing(
        authoritative: List<SeerrRequestAcquisition>,
        nowEpochMillis: Long,
    ): List<SeerrRequestAcquisition> = synchronized(queueingLock) {
        pruneExpiredQueueing(nowEpochMillis)
        queueingRequests.entries.toList().forEach { (key, pending) ->
            val replacement = authoritative.firstOrNull { it.sameRequestAs(pending.acquisition) }
                ?: return@forEach
            val queued = pending.acquisition
            if (queued.request.mediaType != com.github.damontecres.wholphin.data.model.SeerrItemType.TV) {
                if (replacement.hasAuthoritativeDownloadsRepresentation(nowEpochMillis)) {
                    queueingRequests.remove(key)
                }
                return@forEach
            }

            val remainingSeasons =
                queued.request.requestedSeasonNumbers -
                    replacement.authoritativelyRepresentedSeasons(nowEpochMillis)
            if (remainingSeasons.isEmpty()) {
                queueingRequests.remove(key)
            } else if (remainingSeasons != queued.request.requestedSeasonNumbers) {
                queueingRequests[key] =
                    pending.copy(
                        acquisition =
                            queued.copy(
                                request =
                                    queued.request.copy(
                                        requestedSeasonNumbers = remainingSeasons,
                                        seasonAvailability = queued.request.seasonAvailability.filterKeys { it in remainingSeasons },
                                        seasonUpdatedAt = queued.request.seasonUpdatedAt.filterKeys { it in remainingSeasons },
                                        seasonEpisodeCounts = queued.request.seasonEpisodeCounts.filterKeys { it in remainingSeasons },
                                    ),
                            ),
                    )
            }
        }
        queueingRequests.values.map { it.acquisition }
    }

    private fun pruneExpiredQueueing(nowEpochMillis: Long) {
        queueingRequests.entries.removeAll { it.value.expiresAtEpochMillis <= nowEpochMillis }
    }

    private fun publishQueueing() {
        val queueing = queueingRequests.values.map { it.acquisition }
        _state.update { it.copy(queueingRequests = queueing) }
    }

    companion object {
        private const val RECENT_TERMINAL_REQUESTS = 25
        private const val DEFAULT_POLL_INTERVAL_MILLIS = 30_000L
        private const val FAST_POLL_INTERVAL_MILLIS = 8_000L
        private const val MAX_BACKOFF_MILLIS = 5 * 60_000L
        private const val QUEUEING_TTL_MILLIS = 15 * 60_000L

        private fun retainActiveAndRecent(
            requests: List<SeerrRequestAcquisition>,
            previous: List<SeerrRequestAcquisition>,
            nowEpochMillis: Long,
        ): List<SeerrRequestAcquisition> {
            val active = requests.filter { it.isActiveRequest(nowEpochMillis) }
            val completedWithinUiWindow =
                requests.filter { request ->
                    val completionTimes =
                        listOfNotNull(
                            request.request.jellyfinReadySinceEpochMillis,
                            request.request.availableSinceEpochMillis,
                        ) +
                            request.request.jellyfinSeasonReadySinceEpochMillis.values +
                            request.request.seasonAvailableSinceEpochMillis.values
                    completionTimes.any {
                        it.isWithinDownloadsCompletedWindow(nowEpochMillis)
                    }
                }
            val recent = requests.filterNot { it.isActiveRequest(nowEpochMillis) }.take(RECENT_TERMINAL_REQUESTS)
            val previouslyAcquiringIds =
                previous.filter { it.hasKnownAcquisitionEntries() }.mapTo(mutableSetOf()) { it.request.requestId }
            val retainedIds =
                (active + completedWithinUiWindow + recent).mapTo(mutableSetOf()) { it.request.requestId }
                    .apply { addAll(previouslyAcquiringIds) }
            return requests.filter { it.request.requestId in retainedIds }
        }
    }

    private data class QueueingKey(
        val requestId: Int,
        val is4k: Boolean,
    )

    private data class QueueingRequest(
        val acquisition: SeerrRequestAcquisition,
        val expiresAtEpochMillis: Long,
    )
}

private fun SeerrRequestAcquisition.queueingTarget(): SeerrRequestAcquisition? {
    if (request.mediaType != com.github.damontecres.wholphin.data.model.SeerrItemType.TV) return this
    val seasons = request.requestedSeasonNumbers
    if (seasons.isEmpty()) return null
    return copy(
        request =
            request.copy(
                requestedSeasonNumbers = seasons,
                seasonAvailability = request.seasonAvailability.filterKeys { it in seasons },
                seasonUpdatedAt = request.seasonUpdatedAt.filterKeys { it in seasons },
                seasonEpisodeCounts = request.seasonEpisodeCounts.filterKeys { it in seasons },
            ),
    )
}

private fun SeerrRequestAcquisition.sameRequestAs(queueing: SeerrRequestAcquisition): Boolean {
    if (
        request.requestId != queueing.request.requestId ||
        request.is4k != queueing.request.is4k ||
        request.mediaType != queueing.request.mediaType
    ) return false
    return true
}

internal fun retainJellyfinReadiness(
    current: List<SeerrRequestAcquisition>,
    previous: List<SeerrRequestAcquisition>,
): List<SeerrRequestAcquisition> {
    val previousById = previous.associateBy { it.request.requestId }
    return current.map { acquisition ->
        val old = previousById[acquisition.request.requestId]?.request ?: return@map acquisition
        val currentReadiness = acquisition.request.jellyfinReadiness
        val oldReadiness = old.jellyfinReadiness
        val episodeItemIds =
            (oldReadiness.episodeItemIds.keys + currentReadiness.episodeItemIds.keys).associateWith { seasonNumber ->
                oldReadiness.episodeItemIds[seasonNumber].orEmpty() +
                    currentReadiness.episodeItemIds[seasonNumber].orEmpty()
            }
        acquisition.copy(
            request =
                acquisition.request.copy(
                    jellyfinReadiness =
                        currentReadiness.copy(
                            movieItemId = currentReadiness.movieItemId ?: oldReadiness.movieItemId,
                            seriesItemId = currentReadiness.seriesItemId ?: oldReadiness.seriesItemId,
                            seasonItemIds = oldReadiness.seasonItemIds + currentReadiness.seasonItemIds,
                            episodeItemIds = episodeItemIds,
                        ),
                    jellyfinReadySinceEpochMillis =
                        acquisition.request.jellyfinReadySinceEpochMillis
                            ?: old.jellyfinReadySinceEpochMillis,
                    jellyfinSeasonReadySinceEpochMillis =
                        old.jellyfinSeasonReadySinceEpochMillis +
                            acquisition.request.jellyfinSeasonReadySinceEpochMillis,
                ),
        )
    }
}

private fun SeerrRequestAcquisition.hasKnownAcquisitionEntries(): Boolean =
    when (val state = acquisition) {
        is SeerrAcquisitionState.Movie -> state.aggregate.entries.isNotEmpty()
        is SeerrAcquisitionState.Tv -> state.seasons.any { it.aggregate.entries.isNotEmpty() } || state.unassignedEntries.isNotEmpty()
        SeerrAcquisitionState.Queueing,
        SeerrAcquisitionState.None,
        SeerrAcquisitionState.Processing,
        -> false
    }

internal fun stampAvailabilityTransitions(
    current: List<SeerrRequestAcquisition>,
    previous: List<SeerrRequestAcquisition>,
    nowEpochMillis: Long,
): List<SeerrRequestAcquisition> {
    val previousById = previous.associateBy { it.request.requestId }
    return current.map { acquisition ->
        val request = acquisition.request
        val old = previousById[request.requestId]?.request
        val initialFallback = request.updatedAt?.toEpochMillis()
        val availableSince =
            when {
                request.availability != SeerrAvailability.AVAILABLE -> null
                old?.availability == SeerrAvailability.AVAILABLE -> old.availableSinceEpochMillis
                old != null -> nowEpochMillis
                else -> initialFallback
            }
        val seasonAvailableSince =
            request.requestedSeasonNumbers.mapNotNull { seasonNumber ->
                if (request.seasonAvailability[seasonNumber] != SeerrAvailability.AVAILABLE) {
                    null
                } else {
                    val oldTime = old?.seasonAvailableSinceEpochMillis?.get(seasonNumber)
                    val becameAvailable = old != null && old.seasonAvailability[seasonNumber] != SeerrAvailability.AVAILABLE
                    val seasonFallback = request.seasonUpdatedAt[seasonNumber]?.toEpochMillis()
                    seasonNumber to
                        (oldTime
                            ?: if (becameAvailable) nowEpochMillis else seasonFallback ?: initialFallback
                            ?: return@mapNotNull null)
                }
            }.toMap()
        acquisition.copy(
            request =
                request.copy(
                    availableSinceEpochMillis = availableSince,
                    seasonAvailableSinceEpochMillis = seasonAvailableSince,
                ),
        )
    }
}

internal fun stampJellyfinReadinessTransitions(
    current: List<SeerrRequestAcquisition>,
    previous: List<SeerrRequestAcquisition>,
    nowEpochMillis: Long,
): List<SeerrRequestAcquisition> {
    val previousById = previous.associateBy { it.request.requestId }
    return current.map { acquisition ->
        val request = acquisition.request
        val old = previousById[request.requestId]?.request
        val movieReadySince =
            when {
                !request.jellyfinReadiness.movieReady -> null
                old?.jellyfinReadiness?.movieReady == true -> old.jellyfinReadySinceEpochMillis
                old != null -> nowEpochMillis
                else -> request.jellyfinReadySinceEpochMillis
            }
        val seasonReadySince =
            request.requestedSeasonNumbers.mapNotNull { seasonNumber ->
                val expected = request.seasonEpisodeCounts[seasonNumber]
                if (!request.jellyfinReadiness.seasonReady(seasonNumber, expected)) {
                    null
                } else {
                    val oldExpected = old?.seasonEpisodeCounts?.get(seasonNumber)
                    val wasReady =
                        old != null &&
                            (old.jellyfinSeasonReadySinceEpochMillis.containsKey(seasonNumber) ||
                                old.jellyfinReadiness.seasonReady(seasonNumber, oldExpected))
                    val readySince =
                        when {
                            wasReady -> old?.jellyfinSeasonReadySinceEpochMillis?.get(seasonNumber)
                            old != null -> nowEpochMillis
                            else -> request.jellyfinSeasonReadySinceEpochMillis[seasonNumber]
                        }
                    readySince?.let { seasonNumber to it }
                }
            }.toMap()
        acquisition.copy(
            request =
                request.copy(
                    jellyfinReadySinceEpochMillis = movieReadySince,
                    jellyfinSeasonReadySinceEpochMillis = seasonReadySince,
                ),
        )
    }
}

private fun SeerrRequestAcquisition.isActiveRequest(nowEpochMillis: Long): Boolean =
    if (
        request.availability == SeerrAvailability.AVAILABLE ||
        request.availability == SeerrAvailability.BLOCKLISTED ||
        request.availability == SeerrAvailability.DELETED
    ) {
        false
    } else {
        hasLiveQueueEntry() ||
            request.isWithinDownloadsWaitingGrace(nowEpochMillis)
    }

private fun SeerrRequestAcquisition.isActiveAcquisition(): Boolean =
    if (request.availability == SeerrAvailability.AVAILABLE) {
        false
    } else {
        when (acquisition) {
            SeerrAcquisitionState.None -> false
            SeerrAcquisitionState.Processing -> false
            SeerrAcquisitionState.Queueing -> false
            is SeerrAcquisitionState.Movie -> acquisition.aggregate.entries.any { it.isActivelyProgressing() }
            is SeerrAcquisitionState.Tv ->
                acquisition.seasons.any { season -> season.aggregate.entries.any { it.isActivelyProgressing() } } ||
                    acquisition.unassignedEntries.any { it.isActivelyProgressing() }
        }
    }

private fun SeerrRequestAcquisition.hasProblem(): Boolean =
    when (acquisition) {
            SeerrAcquisitionState.None,
            SeerrAcquisitionState.Processing,
            SeerrAcquisitionState.Queueing,
            -> false
            is SeerrAcquisitionState.Movie -> acquisition.aggregate.status == AcquisitionStatus.PROBLEM
            is SeerrAcquisitionState.Tv ->
                acquisition.seasons.any { it.aggregate.status == AcquisitionStatus.PROBLEM } ||
                    acquisition.unassignedEntries.any { it.status == AcquisitionStatus.PROBLEM }
    }

private fun SeerrRequestAcquisition.hasLiveQueueEntry(): Boolean =
    when (val state = acquisition) {
        SeerrAcquisitionState.None,
        SeerrAcquisitionState.Processing,
        SeerrAcquisitionState.Queueing,
        -> false
        is SeerrAcquisitionState.Movie -> state.aggregate.entries.any { it.presentInQueue }
        is SeerrAcquisitionState.Tv ->
            state.seasons.any { season -> season.aggregate.entries.any { it.presentInQueue } } ||
                state.unassignedEntries.any { it.presentInQueue }
    }

private fun com.github.damontecres.wholphin.data.model.AcquisitionEntry.isActivelyProgressing(): Boolean =
    presentInQueue && hasObservedProgress && sizeLeft?.let { it > 0.0 } == true

private fun String.toEpochMillis(): Long? =
    runCatching { Instant.parse(this).toEpochMilli() }
        .recoverCatching { OffsetDateTime.parse(this).toInstant().toEpochMilli() }
        .getOrNull()
