package com.github.damontecres.wholphin.services

import com.github.damontecres.wholphin.preferences.AppPreferences
import com.github.damontecres.wholphin.preferences.UpdateChannel
import com.github.damontecres.wholphin.util.Version
import okhttp3.HttpUrl
import okhttp3.HttpUrl.Companion.toHttpUrl

/** One source for update metadata, its APK assets, and installed-version notes. */
object UpdateSourceResolver {
    const val STABLE_URL = "https://github.com/constbogdan/Wholphin/releases/latest"
    const val DEVELOPMENT_URL = "https://github.com/constbogdan/Wholphin/releases/tags/develop"
    private const val LEGACY_DEFAULT = "https://api.github.com/repos/damontecres/Wholphin/releases/latest"

    // Stored preferences cannot distinguish the former bundled default from an explicit
    // choice of that identical value. All other custom endpoints remain untouched.
    fun migrateDefaultUrl(value: String): String = if (value.isBlank() || value == LEGACY_DEFAULT) STABLE_URL else value

    const val STABLE_API_URL = "https://api.github.com/repos/constbogdan/Wholphin/releases/latest"
    const val DEVELOPMENT_API_URL = "https://api.github.com/repos/constbogdan/Wholphin/releases/tags/develop"

    fun channel(preferences: AppPreferences): UpdateChannel =
        when (preferences.updateChannel) {
            UpdateChannel.UPDATE_CHANNEL_UNSPECIFIED, UpdateChannel.UNRECOGNIZED -> {
                when (migrateDefaultUrl(preferences.updateUrl)) {
                    STABLE_URL, STABLE_API_URL -> UpdateChannel.UPDATE_CHANNEL_STABLE
                    DEVELOPMENT_URL, DEVELOPMENT_API_URL -> UpdateChannel.UPDATE_CHANNEL_DEVELOPMENT
                    else -> UpdateChannel.UPDATE_CHANNEL_CUSTOM
                }
            }

            else -> {
                preferences.updateChannel
            }
        }

    fun migrate(preferences: AppPreferences): AppPreferences =
        if (preferences.updateChannel != UpdateChannel.UPDATE_CHANNEL_UNSPECIFIED &&
            preferences.updateChannel != UpdateChannel.UNRECOGNIZED
        ) {
            preferences
        } else {
            preferences
                .toBuilder()
                .setUpdateChannel(channel(preferences))
                .setUpdateUrl(migrateDefaultUrl(preferences.updateUrl))
                .build()
        }

    fun configuredUrl(preferences: AppPreferences): String =
        when (channel(preferences)) {
            UpdateChannel.UPDATE_CHANNEL_STABLE -> STABLE_API_URL
            UpdateChannel.UPDATE_CHANNEL_DEVELOPMENT -> DEVELOPMENT_API_URL
            else -> preferences.updateUrl
        }

    fun resolve(updateUrl: String): UpdateSource {
        val configured = updateUrl.toHttpUrl()
        val segments = configured.pathSegments
        val metadata =
            if (configured.host == "github.com" && segments.size >= 4 && segments[2] == "releases" &&
                (segments[3] == "latest" || segments[3] == "tags")
            ) {
                configured
                    .newBuilder()
                    .host("api.github.com")
                    .encodedPath("/repos${configured.encodedPath}")
                    .build()
            } else {
                configured
            }
        val apiSegments = metadata.pathSegments
        val releases =
            if (metadata.host == "api.github.com" && apiSegments.size >= 5 &&
                apiSegments[0] == "repos" && apiSegments[3] == "releases" &&
                (apiSegments[4] == "latest" || apiSegments[4] == "tags")
            ) {
                metadata.newBuilder().encodedPath("/" + metadata.encodedPathSegments.take(4).joinToString("/")).build()
            } else {
                null
            }
        return UpdateSource(metadata, releases)
    }
}

data class UpdateSource(
    val metadataUrl: HttpUrl,
    private val releasesUrl: HttpUrl?,
) {
    fun releaseNotesUrls(version: Version): List<HttpUrl> =
        buildList {
            // A rolling/custom endpoint can supply notes only for the matching installed version.
            add(metadataUrl)
            releasesUrl?.let {
                if (it.toString() == "https://api.github.com/repos/constbogdan/Wholphin/releases") {
                    add(
                        it
                            .newBuilder()
                            .addPathSegment("tags")
                            .addPathSegment("mosaic-$version")
                            .build(),
                    )
                }
                add(
                    it
                        .newBuilder()
                        .addPathSegment("tags")
                        .addPathSegment(version.toString())
                        .build(),
                )
                add(
                    it
                        .newBuilder()
                        .addPathSegment("tags")
                        .addPathSegment(version.toString().removePrefix("v"))
                        .build(),
                )
            }
        }.distinct()
}
