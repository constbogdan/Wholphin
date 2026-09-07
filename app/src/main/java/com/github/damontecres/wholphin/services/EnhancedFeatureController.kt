package com.github.damontecres.wholphin.services

import com.github.damontecres.wholphin.services.hilt.DefaultCoroutineScope
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class EnhancedFeatureController internal constructor(
    acquisitionTrackingEnabled: Flow<Boolean>,
    private val startAcquisitionTracking: () -> Unit,
    private val stopAcquisitionTracking: () -> Unit,
    private val deactivateAcquisitionTracking: () -> Unit,
    scope: CoroutineScope,
) {
    @Inject
    constructor(
        gate: EnhancedFeatureGate,
        tracker: SeerrAcquisitionTracker,
        @DefaultCoroutineScope scope: CoroutineScope,
    ) : this(
        acquisitionTrackingEnabled = gate.observe(EnhancedCapability.ACQUISITION_TRACKING),
        startAcquisitionTracking = tracker::startForeground,
        stopAcquisitionTracking = tracker::stopForeground,
        deactivateAcquisitionTracking = tracker::deactivate,
        scope = scope,
    )

    private val foreground = MutableStateFlow(false)

    init {
        combine(
            foreground,
            acquisitionTrackingEnabled,
        ) { isForeground, enabled ->
            when {
                !enabled -> LifecycleAction.DEACTIVATE
                isForeground -> LifecycleAction.START
                else -> LifecycleAction.STOP
            }
        }.distinctUntilChanged()
            .onEach { action ->
                when (action) {
                    LifecycleAction.START -> startAcquisitionTracking()
                    LifecycleAction.STOP -> stopAcquisitionTracking()
                    LifecycleAction.DEACTIVATE -> deactivateAcquisitionTracking()
                }
            }.launchIn(scope)
    }

    fun startForeground() {
        foreground.value = true
    }

    fun stopForeground() {
        foreground.value = false
    }

    private enum class LifecycleAction {
        START,
        STOP,
        DEACTIVATE,
    }
}
