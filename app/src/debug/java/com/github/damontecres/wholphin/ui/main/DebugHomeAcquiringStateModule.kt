package com.github.damontecres.wholphin.ui.main

import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent

@Module
@InstallIn(SingletonComponent::class)
internal abstract class DebugHomeAcquiringStateModule {
    @Binds
    abstract fun bindHomeAcquiringStateProvider(
        source: DebugHomeAcquiringStateProvider,
    ): HomeAcquiringStateProvider
}
