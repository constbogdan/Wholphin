package com.github.damontecres.wholphin.data.model

import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import java.util.UUID

@Entity(
    tableName = "season_integrity_expectations",
    foreignKeys = [
        ForeignKey(
            entity = JellyfinUser::class,
            parentColumns = ["rowId"],
            childColumns = ["jellyfinUserRowId"],
            onDelete = ForeignKey.CASCADE,
            onUpdate = ForeignKey.CASCADE,
        ),
    ],
    indices = [Index("jellyfinUserRowId"), Index("seriesItemId")],
    primaryKeys = ["jellyfinUserRowId", "seriesItemId", "seasonNumber"],
)
data class SeasonIntegrityExpectationCache(
    val jellyfinUserRowId: Int,
    val seriesItemId: UUID,
    val seasonNumber: Int,
    val tmdbId: Int?,
    val expectedEpisodeNumbers: Set<Int>,
    val lastUpdatedEpochMillis: Long,
)

data class SeasonIntegrityExpectation(
    val seasonNumber: Int,
    val expectedEpisodeNumbers: Set<Int>,
)

/** A current, in-memory comparison. None of these live Jellyfin/acquisition values are persisted. */
data class SeasonIntegrity(
    val seasonNumber: Int,
    val seasonItemId: UUID?,
    val expectedEpisodeNumbers: Set<Int>,
    val playableEpisodeNumbers: Set<Int>,
    val physicallyMissingEpisodeNumbers: Set<Int>,
    val activelyCoveredEpisodeNumbers: Set<Int>,
    val unattendedMissingEpisodeNumbers: Set<Int>,
) {
    val missingEpisodeCount: Int = unattendedMissingEpisodeNumbers.size
    val incomplete: Boolean = unattendedMissingEpisodeNumbers.isNotEmpty()
}

internal data class SeasonAcquisitionCoverage(
    val episodeNumbers: Set<Int> = emptySet(),
    val coversWholeSeason: Boolean = false,
)

internal fun calculateSeasonIntegrity(
    expectation: SeasonIntegrityExpectation,
    seasonItemId: UUID?,
    playableEpisodeNumbers: Set<Int>,
    acquisitionCoverage: SeasonAcquisitionCoverage,
): SeasonIntegrity? {
    if (expectation.seasonNumber == 0) return null
    val expectedNumbers = expectation.expectedEpisodeNumbers.filter { it > 0 }.toSet()
    if (expectedNumbers.isEmpty()) return null

    val playableExpectedNumbers = expectedNumbers.intersect(playableEpisodeNumbers)
    val physicallyMissing = expectedNumbers - playableExpectedNumbers
    val activelyCovered =
        if (acquisitionCoverage.coversWholeSeason) physicallyMissing
        else physicallyMissing.intersect(acquisitionCoverage.episodeNumbers)

    return SeasonIntegrity(
        seasonNumber = expectation.seasonNumber,
        seasonItemId = seasonItemId,
        expectedEpisodeNumbers = expectedNumbers,
        playableEpisodeNumbers = playableExpectedNumbers,
        physicallyMissingEpisodeNumbers = physicallyMissing,
        activelyCoveredEpisodeNumbers = activelyCovered,
        unattendedMissingEpisodeNumbers = physicallyMissing - activelyCovered,
    )
}
