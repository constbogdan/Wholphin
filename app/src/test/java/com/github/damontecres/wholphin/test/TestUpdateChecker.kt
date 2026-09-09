package com.github.damontecres.wholphin.test

import com.github.damontecres.wholphin.preferences.AppPreferences
import com.github.damontecres.wholphin.preferences.AppPreferencesSerializer
import com.github.damontecres.wholphin.services.UpdateChecker
import com.github.damontecres.wholphin.services.UpdateSourceResolver
import com.github.damontecres.wholphin.services.getDownloadUrl
import com.github.damontecres.wholphin.util.Version
import io.mockk.mockk
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Protocol
import okhttp3.Response
import okhttp3.ResponseBody.Companion.toResponseBody
import org.junit.Assert
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.nio.file.Paths
import kotlin.io.path.readText

@RunWith(RobolectricTestRunner::class)
@Config(manifest = Config.NONE, sdk = [30])
class TestUpdateChecker {
    lateinit var releaseJson: JsonObject
    val assetsJson: JsonArray by lazy { releaseJson["assets"]!!.jsonArray }

    @Before
    fun setup() {
        val resource = javaClass.classLoader?.getResource("release_develop.json")
        Assert.assertNotNull(resource)
        val fileContents = Paths.get(resource!!.toURI()).readText()
        releaseJson = Json.parseToJsonElement(fileContents).jsonObject
    }

    @Test
    fun `Release chooses release`() {
        val url = getDownloadUrl(assetsJson, false, listOf())
        Assert.assertEquals("https://github.com/damontecres/Wholphin/releases/download/develop/Wholphin-release.apk", url)
    }

    @Test
    fun `Choose abi`() {
        val url = getDownloadUrl(assetsJson, false, listOf("arm64-v8a"))
        Assert.assertEquals("https://github.com/damontecres/Wholphin/releases/download/develop/Wholphin-release-arm64-v8a.apk", url)
    }

    @Test
    fun `Choose unknown abi`() {
        val url = getDownloadUrl(assetsJson, false, listOf("unknown"))
        Assert.assertEquals("https://github.com/damontecres/Wholphin/releases/download/develop/Wholphin-release.apk", url)
    }

    @Test
    fun `Debug chooses debug`() {
        val url = getDownloadUrl(assetsJson, true, listOf())
        Assert.assertEquals("https://github.com/damontecres/Wholphin/releases/download/develop/Wholphin-debug.apk", url)
    }

    @Test
    fun `Choose debug abi`() {
        val url = getDownloadUrl(assetsJson, true, listOf("arm64-v8a"))
        Assert.assertEquals("https://github.com/damontecres/Wholphin/releases/download/develop/Wholphin-debug-arm64-v8a.apk", url)
    }

    @Test
    fun `Mosaic defaults resolve stable and development metadata`() {
        Assert.assertEquals("https://github.com/constbogdan/Wholphin/releases/latest", AppPreferencesSerializer().defaultValue.updateUrl)
        Assert.assertEquals(
            "https://api.github.com/repos/constbogdan/Wholphin/releases/latest",
            UpdateSourceResolver.resolve("").metadataUrl.toString(),
        )
        Assert.assertEquals(
            "https://api.github.com/repos/constbogdan/Wholphin/releases/tags/develop",
            UpdateSourceResolver.resolve(UpdateSourceResolver.DEVELOPMENT_URL).metadataUrl.toString(),
        )
    }

    @Test
    fun `stored default migrates but custom endpoints and channel choice survive`() =
        runBlocking {
            val legacy = "https://api.github.com/repos/damontecres/Wholphin/releases/latest"
            val custom = "https://updates.example.test/mosaic.json?channel=testing"
            for (value in listOf(legacy, custom, UpdateSourceResolver.DEVELOPMENT_URL, legacy.replace("latest", "tags/develop"))) {
                val stored = AppPreferences.newBuilder().setUpdateUrl(value).build()
                val restored = AppPreferencesSerializer().readFrom(stored.toByteArray().inputStream())
                Assert.assertEquals(if (value == legacy) UpdateSourceResolver.STABLE_URL else value, restored.updateUrl)
            }
            Assert.assertEquals(custom, UpdateSourceResolver.resolve(custom).metadataUrl.toString())
        }

    private fun checker(
        requests: MutableList<String>,
        response: (String) -> Pair<Int, String>,
    ): UpdateChecker {
        val client =
            OkHttpClient
                .Builder()
                .addInterceptor { chain ->
                    val url = chain.request().url.toString()
                    requests.add(url)
                    val (code, body) = response(url)
                    Response
                        .Builder()
                        .request(chain.request())
                        .protocol(Protocol.HTTP_1_1)
                        .code(code)
                        .message("fixture")
                        .body(body.toResponseBody("application/json".toMediaType()))
                        .build()
                }.build()
        return UpdateChecker(mockk(), client)
    }

    private fun metadata(version: String): String =
        """
        {"name":"$version","body":"notes",
        "assets":[{"name":"Wholphin-debug.apk",
        "browser_download_url":"https://github.com/constbogdan/Wholphin/releases/download/develop/Wholphin-debug.apk"}]}
        """.trimIndent()

    @Test
    fun `checks APK selection and installed notes share the chosen source`() =
        runBlocking {
            for (source in listOf(
                UpdateSourceResolver.STABLE_URL,
                UpdateSourceResolver.DEVELOPMENT_URL,
                "https://custom.example.test/update.json",
            )) {
                val requests = mutableListOf<String>()
                val checker = checker(requests) { 200 to metadata("v1.0.3") }
                val release = checker.getLatestRelease(source)
                Assert.assertEquals(Version.fromString("1.0.3"), release?.version)
                Assert.assertEquals(
                    "https://github.com/constbogdan/Wholphin/releases/download/develop/Wholphin-debug.apk",
                    release?.downloadUrl,
                )
                Assert.assertNotNull(checker.getRelease(Version.fromString("1.0.3"), source))
                Assert.assertEquals(List(2) { UpdateSourceResolver.resolve(source).metadataUrl.toString() }, requests)
            }
        }

    @Test
    fun `installed notes use selected repository tags and never newer rolling notes`() =
        runBlocking {
            val requests = mutableListOf<String>()
            val checker =
                checker(requests) { url ->
                    when {
                        url.endsWith("/tags/1.0.3") -> 200 to metadata("1.0.3")
                        url.endsWith("/tags/v1.0.3") -> 404 to "{}"
                        else -> 200 to metadata("v1.0.4")
                    }
                }
            Assert.assertEquals(
                Version.fromString("1.0.3"),
                checker.getRelease(Version.fromString("1.0.3"), "https://github.com/example/custom/releases/tags/develop")?.version,
            )
            Assert.assertEquals(
                listOf("develop", "v1.0.3", "1.0.3").map { "https://api.github.com/repos/example/custom/releases/tags/$it" },
                requests,
            )
            val customRequests = mutableListOf<String>()
            Assert.assertNull(
                checker(customRequests) {
                    200 to metadata("1.0.4")
                }.getRelease(Version.fromString("1.0.3"), "https://custom.example.test/release.json"),
            )
            Assert.assertEquals(1, customRequests.size)
        }

    @Test
    fun `downstream aliases win over fallback and versioned artifacts`() {
        val json =
            """
            [{"name":"Wholphin.apk",
            "browser_download_url":"fallback"},
            {"name":"Wholphin-release-1.0.3.apk",
            "browser_download_url":"versioned"},
            {"name":"Wholphin-release.apk",
            "browser_download_url":"release"},
            {"name":"Wholphin-debug.apk",
            "browser_download_url":"debug"},
            {"name":"Wholphin-release-arm64-v8a.apk",
            "browser_download_url":"release-arm64"},
            {"name":"Wholphin-debug-arm64-v8a.apk",
            "browser_download_url":"debug-arm64"}]
            """.trimIndent()
        val assets = Json.parseToJsonElement(json).jsonArray
        Assert.assertEquals("release", getDownloadUrl(assets, false, emptyList()))
        Assert.assertEquals("debug", getDownloadUrl(assets, true, emptyList()))
        Assert.assertEquals("release-arm64", getDownloadUrl(assets, false, listOf("arm64-v8a")))
        Assert.assertEquals("debug-arm64", getDownloadUrl(assets, true, listOf("arm64-v8a")))
    }
}
