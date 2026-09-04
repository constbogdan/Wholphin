package com.github.damontecres.wholphin.services

import com.github.damontecres.wholphin.data.model.SeerrRequestAcquisition

internal data class SeerrRequestAcquisitionPage(
    val requests: List<SeerrRequestAcquisition>,
    val page: Int?,
    val pages: Int?,
    val totalResults: Int?,
)

internal suspend fun paginateSeerrRequestAcquisitions(
    pageSize: Int = 50,
    fetchPage: suspend (take: Int, skip: Int) -> SeerrRequestAcquisitionPage,
): List<SeerrRequestAcquisition> {
    val requests = linkedMapOf<Int, SeerrRequestAcquisition>()
    var skip = 0

    while (true) {
        val response = fetchPage(pageSize, skip)
        response.requests.forEach { requests[it.request.requestId] = it }
        skip += response.requests.size

        val hasMore =
            when {
                response.requests.isEmpty() -> false
                response.totalResults != null -> skip < response.totalResults
                response.page != null && response.pages != null -> response.page < response.pages
                else -> response.requests.size == pageSize
            }
        if (!hasMore) break
    }

    return requests.values.toList()
}
