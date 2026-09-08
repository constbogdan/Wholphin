package com.github.damontecres.wholphin.data.model

internal val SeerrRequestAcquisition.hasCurrentMovieAcquisitionWork: Boolean
    get() {
        if (request.mediaType != SeerrItemType.MOVIE) return false
        if (acquisition == SeerrAcquisitionState.Queueing) return true
        val movie = acquisition as? SeerrAcquisitionState.Movie ?: return false
        return movie.aggregate.entries.any { entry ->
            entry.status != AcquisitionStatus.PROBLEM &&
                (
                    entry.presentInQueue ||
                        (
                            !entry.observedSuccessfulTransferCompletion &&
                                entry.absentPollCount <= TV_PROGRESS_GRACE_POLLS
                        ) ||
                        (entry.observedSuccessfulTransferCompletion && !request.jellyfinReadiness.movieReady)
                )
        }
    }
