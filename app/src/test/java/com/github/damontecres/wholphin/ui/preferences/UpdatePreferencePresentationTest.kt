package com.github.damontecres.wholphin.ui.preferences

import com.github.damontecres.wholphin.R
import com.github.damontecres.wholphin.preferences.AppPreference
import com.github.damontecres.wholphin.preferences.AppPreferences
import com.github.damontecres.wholphin.preferences.UpdateChannel
import com.github.damontecres.wholphin.preferences.advancedPreferences
import com.github.damontecres.wholphin.preferences.basicPreferences
import com.github.damontecres.wholphin.util.LoadingState
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class UpdatePreferencePresentationTest {
    @Test
    fun `update action truthfully represents each state`() {
        assertEquals(
            UpdatePreferencePresentation.Check,
            updatePreferencePresentation(LoadingState.Pending, updateAvailable = false),
        )
        assertEquals(
            UpdatePreferencePresentation.Checking,
            updatePreferencePresentation(LoadingState.Loading, updateAvailable = false),
        )
        assertEquals(
            UpdatePreferencePresentation.UpToDate,
            updatePreferencePresentation(LoadingState.Success, updateAvailable = false),
        )
        assertEquals(
            UpdatePreferencePresentation.Retry,
            updatePreferencePresentation(LoadingState.Error("network"), updateAvailable = false),
        )
        assertEquals(
            UpdatePreferencePresentation.Install,
            updatePreferencePresentation(LoadingState.Success, updateAvailable = true),
        )
        assertEquals(
            UpdatePreferencePresentation.Checking,
            updatePreferencePresentation(LoadingState.Loading, updateAvailable = true),
        )
        assertEquals(
            UpdatePreferencePresentation.Retry,
            updatePreferencePresentation(LoadingState.Error("network"), updateAvailable = true),
        )
    }

    @Test
    fun `about is the canonical ordered update preference group`() {
        val about = basicPreferences.single { it.title == R.string.about }
        assertEquals(
            listOf(
                AppPreference.InstalledVersion,
                AppPreference.Update,
                AppPreference.UpdateChannelPreference,
            ),
            about.preferences,
        )

        val customPreferences =
            visiblePreferences(
                about,
                AppPreferences
                    .newBuilder()
                    .setUpdateChannel(UpdateChannel.UPDATE_CHANNEL_CUSTOM)
                    .build(),
            )
        assertEquals(
            listOf(
                AppPreference.InstalledVersion,
                AppPreference.Update,
                AppPreference.UpdateChannelPreference,
                AppPreference.UpdateUrl,
                AppPreference.AutoCheckForUpdates,
            ),
            customPreferences,
        )

        val stablePreferences =
            visiblePreferences(
                about,
                AppPreferences
                    .newBuilder()
                    .setUpdateChannel(UpdateChannel.UPDATE_CHANNEL_STABLE)
                    .build(),
            )
        assertEquals(
            listOf(
                AppPreference.InstalledVersion,
                AppPreference.Update,
                AppPreference.UpdateChannelPreference,
                AppPreference.AutoCheckForUpdates,
            ),
            stablePreferences,
        )
        val advancedUpdatePreferences =
            advancedPreferences
                .flatMap { group ->
                    group.preferences + group.conditionalPreferences.flatMap { it.preferences }
                }.filter {
                    it in
                        setOf(
                            AppPreference.Update,
                            AppPreference.UpdateChannelPreference,
                            AppPreference.UpdateUrl,
                            AppPreference.AutoCheckForUpdates,
                        )
                }
        assertTrue(advancedUpdatePreferences.isEmpty())
    }

    private fun visiblePreferences(
        group: PreferenceGroup<AppPreferences>,
        preferences: AppPreferences,
    ) = group.preferences +
        group.conditionalPreferences
            .filter { it.condition(preferences) }
            .flatMap { it.preferences }
}
