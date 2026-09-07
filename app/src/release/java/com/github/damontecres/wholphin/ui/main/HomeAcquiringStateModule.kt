package com.github.damontecres.wholphin.ui.main

import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent

@Module
@InstallIn(SingletonComponent::class)
abstract class HomeAcquiringStateModule {
    @Binds
    abstract fun bindHomeAcquiringStateProvider(source: HomeAcquiringSource): HomeAcquiringStateProvider
}
