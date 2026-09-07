package com.github.damontecres.wholphin.services

import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class EnhancedFeatureControllerTest {
    @Test
    fun foregroundLifecycleStartsStopsAndDeactivatesTracking() =
        runTest {
            val enabled = MutableStateFlow(false)
            var starts = 0
            var stops = 0
            var deactivations = 0
            val controller =
                EnhancedFeatureController(
                    acquisitionTrackingEnabled = enabled,
                    startAcquisitionTracking = { starts++ },
                    stopAcquisitionTracking = { stops++ },
                    deactivateAcquisitionTracking = { deactivations++ },
                    scope = backgroundScope,
                )

            runCurrent()
            controller.startForeground()
            runCurrent()
            assertEquals(0, starts)

            enabled.value = true
            runCurrent()
            assertEquals(1, starts)

            controller.stopForeground()
            runCurrent()
            assertEquals(1, stops)

            controller.startForeground()
            runCurrent()
            assertEquals(2, starts)

            enabled.value = false
            runCurrent()
            assertEquals(2, deactivations)
        }
}
