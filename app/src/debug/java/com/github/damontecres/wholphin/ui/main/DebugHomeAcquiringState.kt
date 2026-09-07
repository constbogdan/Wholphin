package com.github.damontecres.wholphin.ui.main

import com.github.damontecres.wholphin.services.hilt.DefaultCoroutineScope
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import javax.inject.Inject
import javax.inject.Singleton

internal enum class HomeAcquiringFixtureScenario(
    val token: String,
) {
    EMPTY("empty"),
    MOVIE_STATES("movie_states"),
    TV_MULTI_SEASON("tv_multi_season"),
    MIXED("mixed"),
    FOCUS_BEFORE("focus_before"),
    FOCUS_CARD_REMOVED("focus_card_removed"),
    FOCUS_ROW_REMOVED("focus_row_removed"),
    ;

    companion object {
        fun fromToken(token: String?): HomeAcquiringFixtureScenario? =
            entries.firstOrNull { it.token == token?.lowercase() }
    }
}

internal sealed interface DebugHomeAcquiringMode {
    data object Real : DebugHomeAcquiringMode

    data class Fixture(
        val scenario: HomeAcquiringFixtureScenario,
    ) : DebugHomeAcquiringMode
}

@Singleton
internal class DebugHomeAcquiringController
    @Inject
    constructor() {
        private val _mode = MutableStateFlow<DebugHomeAcquiringMode>(DebugHomeAcquiringMode.Real)
        val mode: StateFlow<DebugHomeAcquiringMode> = _mode

        fun useRealState() {
            _mode.value = DebugHomeAcquiringMode.Real
        }

        fun useFixture(scenario: HomeAcquiringFixtureScenario) {
            _mode.value = DebugHomeAcquiringMode.Fixture(scenario)
        }
    }

@Singleton
internal class DebugHomeAcquiringStateProvider
    @Inject
    constructor(
        realSource: HomeAcquiringSource,
        controller: DebugHomeAcquiringController,
        @DefaultCoroutineScope scope: CoroutineScope,
    ) : HomeAcquiringStateProvider {
        override val state: StateFlow<HomeAcquiringState> =
            combine(realSource.state, controller.mode) { realState, mode ->
                when (mode) {
                    DebugHomeAcquiringMode.Real -> realState
                    is DebugHomeAcquiringMode.Fixture -> HomeAcquiringFixtures.state(mode.scenario)
                }
            }.stateIn(scope, SharingStarted.Eagerly, realSource.state.value)
    }
