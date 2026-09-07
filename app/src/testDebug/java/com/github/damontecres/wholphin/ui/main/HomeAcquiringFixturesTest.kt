package com.github.damontecres.wholphin.ui.main

import com.github.damontecres.wholphin.data.model.MediaKey
import com.github.damontecres.wholphin.services.AcquisitionIndexSnapshot
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class HomeAcquiringFixturesTest {
    @Test
    fun scenariosHaveUniqueTypedKeysAndValidProgress() {
        HomeAcquiringFixtureScenario.entries.forEach { scenario ->
            val items = HomeAcquiringFixtures.state(scenario).items
            assertEquals(scenario.token, items.size, items.map { it.key }.distinct().size)
            assertEquals(scenario.token, items.size, items.map { it.key.composeSaveableKey() }.distinct().size)
            items.mapNotNull { it.acquisitionPresentation?.acquisitionProgress }.forEach { progress ->
                assertTrue(scenario.token, progress > 0f && progress < 1f)
            }
        }

        val movie: MediaKey =
            MediaKey.Catalog(com.github.damontecres.wholphin.data.model.CatalogMediaType.MOVIE, 1399)
        val season: MediaKey =
            MediaKey.Season(
                MediaKey.Catalog(com.github.damontecres.wholphin.data.model.CatalogMediaType.SERIES, 1399),
                3,
            )
        assertFalse(movie == season)
        assertFalse(movie.composeSaveableKey() == season.composeSaveableKey())
    }

    @Test
    fun focusRemovalPreservesSurvivorKeysAndRowRemovalIsEmpty() {
        val before = HomeAcquiringFixtures.state(HomeAcquiringFixtureScenario.FOCUS_BEFORE).items.map { it.key }
        val after = HomeAcquiringFixtures.state(HomeAcquiringFixtureScenario.FOCUS_CARD_REMOVED).items.map { it.key }

        assertTrue(before.containsAll(after))
        assertEquals(1, before.size - after.size)
        assertTrue(HomeAcquiringFixtures.state(HomeAcquiringFixtureScenario.FOCUS_ROW_REMOVED).items.isEmpty())
    }

    @Test
    fun debugProviderDefaultsToRealAndSwitchingDoesNotMutateRealSource() =
        runTest {
            val snapshots = MutableStateFlow(AcquisitionIndexSnapshot())
            val realSource = HomeAcquiringSource(snapshots, backgroundScope)
            val initialRealState = realSource.state.value
            val controller = DebugHomeAcquiringController()
            val provider = DebugHomeAcquiringStateProvider(realSource, controller, backgroundScope)

            assertEquals(DebugHomeAcquiringMode.Real, controller.mode.value)
            assertEquals(initialRealState, provider.state.first { it == initialRealState })

            val mixed = HomeAcquiringFixtures.state(HomeAcquiringFixtureScenario.MIXED)
            controller.useFixture(HomeAcquiringFixtureScenario.MIXED)

            assertEquals(mixed, provider.state.first { it == mixed })
            assertEquals(initialRealState, realSource.state.value)

            controller.useRealState()
            assertEquals(initialRealState, provider.state.first { it == initialRealState })
        }
}
