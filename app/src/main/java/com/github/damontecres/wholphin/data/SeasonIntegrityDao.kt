package com.github.damontecres.wholphin.data

import androidx.room.Dao
import androidx.room.Query
import androidx.room.Upsert
import com.github.damontecres.wholphin.data.model.SeasonIntegrityExpectationCache
import java.util.UUID

@Dao
interface SeasonIntegrityDao {
    @Query("SELECT * FROM season_integrity_expectations WHERE jellyfinUserRowId = :userId AND seriesItemId = :seriesItemId")
    suspend fun getSeries(userId: Int, seriesItemId: UUID): List<SeasonIntegrityExpectationCache>

    @Upsert
    suspend fun upsert(items: List<SeasonIntegrityExpectationCache>)
}
