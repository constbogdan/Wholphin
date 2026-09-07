package com.github.damontecres.wholphin.services

import com.github.damontecres.wholphin.preferences.AppPreferencesSerializer
import com.github.damontecres.wholphin.preferences.EnhancedFeaturesSetting
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class EnhancedFeatureGateTest {
    @Test
    fun freshInstallDefaultsEnhancedFeaturesOff() {
        val setting = AppPreferencesSerializer().defaultValue.enhancedFeaturesPreferences.masterSetting

        assertEquals(EnhancedFeaturesSetting.ENHANCED_FEATURES_DISABLED, setting)
    }

    @Test
    fun unspecifiedMigratedPreferencePreservesEnabledBehavior() {
        val state = EnhancedFeatureResolver.resolve(EnhancedFeaturesSetting.ENHANCED_FEATURES_UNSPECIFIED)

        assertTrue(state.masterEnabled)
        EnhancedCapability.entries.forEach { assertTrue(state.isEnabled(it)) }
    }

    @Test
    fun explicitEnabledPreferenceEnablesEveryInitialCapability() {
        val state = EnhancedFeatureResolver.resolve(EnhancedFeaturesSetting.ENHANCED_FEATURES_ENABLED)

        assertTrue(state.masterEnabled)
        EnhancedCapability.entries.forEach { assertTrue(state.isEnabled(it)) }
    }

    @Test
    fun explicitDisabledPreferenceDisablesEveryInitialCapability() {
        val state = EnhancedFeatureResolver.resolve(EnhancedFeaturesSetting.ENHANCED_FEATURES_DISABLED)

        assertFalse(state.masterEnabled)
        EnhancedCapability.entries.forEach { assertFalse(state.isEnabled(it)) }
    }

    @Test
    fun dependentCapabilitiesAreDisabledWhenAcquisitionTrackingIsOverriddenOff() {
        val state =
            EnhancedFeatureResolver.resolve(
                EnhancedFeaturesSetting.ENHANCED_FEATURES_ENABLED,
                mapOf(EnhancedCapability.ACQUISITION_TRACKING to false),
            )

        assertFalse(state.isEnabled(EnhancedCapability.ACQUISITION_TRACKING))
        assertFalse(state.isEnabled(EnhancedCapability.ACQUISITION_PROGRESS))
        assertFalse(state.isEnabled(EnhancedCapability.DOWNLOADS))
        assertTrue(state.isEnabled(EnhancedCapability.MISSING_SEASONS))
    }
}
