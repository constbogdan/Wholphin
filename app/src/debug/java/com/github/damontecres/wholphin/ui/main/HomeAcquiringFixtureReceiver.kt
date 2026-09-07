package com.github.damontecres.wholphin.ui.main

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.widget.Toast
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

@AndroidEntryPoint
internal class HomeAcquiringFixtureReceiver : BroadcastReceiver() {
    @Inject lateinit var controller: DebugHomeAcquiringController

    override fun onReceive(
        context: Context,
        intent: Intent,
    ) {
        val token = intent.getStringExtra(EXTRA_SCENARIO)?.lowercase()
        if (token == REAL_SCENARIO) {
            controller.useRealState()
            Toast.makeText(context, "Home Acquiring: real", Toast.LENGTH_SHORT).show()
            return
        }
        val scenario = HomeAcquiringFixtureScenario.fromToken(token)
        if (scenario == null) {
            Toast.makeText(context, "Unknown Home Acquiring fixture: $token", Toast.LENGTH_LONG).show()
            return
        }
        controller.useFixture(scenario)
        Toast.makeText(context, "Home Acquiring: ${scenario.token}", Toast.LENGTH_SHORT).show()
    }

    companion object {
        const val ACTION = "com.github.damontecres.wholphin.debug.ACQUISITION_FIXTURE"
        const val EXTRA_SCENARIO = "scenario"
        const val REAL_SCENARIO = "real"
    }
}
