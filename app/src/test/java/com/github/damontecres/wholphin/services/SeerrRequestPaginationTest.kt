package com.github.damontecres.wholphin.services

import com.github.damontecres.wholphin.api.seerr.model.MediaInfo
import com.github.damontecres.wholphin.api.seerr.model.MediaRequest
import com.github.damontecres.wholphin.data.model.toSeerrRequestAcquisition
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

class SeerrRequestPaginationTest {
    @Test
    fun requestsEveryGlobalPageInOrder() =
        runTest {
            val calls = mutableListOf<Pair<Int, Int>>()
            val all = (1..5).map { request(it) }

            val result =
                paginateSeerrRequestAcquisitions(pageSize = 2) { take, skip ->
                    calls += take to skip
                    SeerrRequestAcquisitionPage(
                        requests = all.drop(skip).take(take),
                        page = skip / take + 1,
                        pages = 3,
                        totalResults = all.size,
                    )
                }

            assertEquals(listOf(1, 2, 3, 4, 5), result.map { it.request.requestId })
            assertEquals(
                listOf(2 to 0, 2 to 2, 2 to 4),
                calls,
            )
        }

    private fun request(id: Int) =
        MediaRequest(
            id = id,
            status = 5,
            type = "movie",
            media = MediaInfo(id = id, status = 5),
        ).toSeerrRequestAcquisition()
}
