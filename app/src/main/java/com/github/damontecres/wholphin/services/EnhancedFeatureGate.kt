package com.github.damontecres.wholphin.services

import androidx.datastore.core.DataStore
import com.github.damontecres.wholphin.preferences.AppPreferences
import com.github.damontecres.wholphin.preferences.EnhancedFeaturesSetting
import com.github.damontecres.wholphin.services.hilt.DefaultCoroutineScope
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import javax.inject.Inject
import javax.inject.Singleton

enum class EnhancedCapability {
    DOWNLOADS,
    ACQUISITION_TRACKING,
    ACQUISITION_PROGRESS,
    MISSING_SEASONS,
    SERIES_REQUEST_ENHANCEMENTS,
    SEASON_INTEGRITY,
}

data class EnhancedFeatureState(
    val isLoaded: Boolean = false,
    val masterEnabled: Boolean = false,
    val enabledCapabilities: Set<EnhancedCapability> = emptySet(),
) {
    fun isEnabled(capability: EnhancedCapability): Boolean = capability in enabledCapabilities
}

internal object EnhancedFeatureResolver {
    private val masterCapabilities = EnhancedCapability.entries.toSet()
    private val dependencies =
        mapOf(
            EnhancedCapability.DOWNLOADS to setOf(EnhancedCapability.ACQUISITION_TRACKING),
            EnhancedCapability.ACQUISITION_PROGRESS to setOf(EnhancedCapability.ACQUISITION_TRACKING),
        )

    fun resolve(
        setting: EnhancedFeaturesSetting,
        overrides: Map<EnhancedCapability, Boolean> = emptyMap(),
    ): EnhancedFeatureState {
        // UNSPECIFIED identifies preferences written before the setting existed.
        val enabled = setting != EnhancedFeaturesSetting.ENHANCED_FEATURES_DISABLED
        val requested =
            if (enabled) {
                masterCapabilities.filterTo(mutableSetOf()) { overrides[it] != false }
            } else {
                emptySet()
            }
        val effective =
            requested.filterTo(mutableSetOf()) { capability ->
                dependencies[capability].orEmpty().all { it in requested }
            }
        return EnhancedFeatureState(
            isLoaded = true,
            masterEnabled = enabled,
            enabledCapabilities = effective,
        )
    }
}

fun AppPreferences.isEnhancedCapabilityEnabled(capability: EnhancedCapability): Boolean =
    EnhancedFeatureResolver.resolve(enhancedFeaturesPreferences.masterSetting).isEnabled(capability)

@Singleton
class EnhancedFeatureGate
    @Inject
    constructor(
        preferences: DataStore<AppPreferences>,
        @param:DefaultCoroutineScope scope: CoroutineScope,
    ) {
        val state: StateFlow<EnhancedFeatureState> =
            preferences.data
                .map { EnhancedFeatureResolver.resolve(it.enhancedFeaturesPreferences.masterSetting) }
                .distinctUntilChanged()
                .stateIn(scope, SharingStarted.Eagerly, EnhancedFeatureState())

        fun isEnabled(capability: EnhancedCapability): Boolean = state.value.isEnabled(capability)

        fun observe(capability: EnhancedCapability): Flow<Boolean> = state.map { it.isEnabled(capability) }.distinctUntilChanged()
    }
