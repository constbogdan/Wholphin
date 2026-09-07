package com.github.damontecres.wholphin.test

import androidx.room.testing.MigrationTestHelper
import androidx.room.Room
import androidx.room.util.useCursor
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.github.damontecres.wholphin.data.AppDatabase
import com.github.damontecres.wholphin.data.Migrations
import org.junit.Assert
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import java.io.IOException
import java.util.UUID

@RunWith(AndroidJUnit4::class)
class TestDbMigrations {
    private val testDbName = "migration-test"

    @get:Rule
    val helper: MigrationTestHelper =
        MigrationTestHelper(
            InstrumentationRegistry.getInstrumentation(),
            AppDatabase::class.java,
        )

    @Test
    fun migrate35To36CreatesSeasonExpectationCache() {
        helper.createDatabase(testDbName, 35).close()

        val database =
            Room.databaseBuilder(
                ApplicationProvider.getApplicationContext(),
                AppDatabase::class.java,
                testDbName,
            ).allowMainThreadQueries()
                .build()
        try {
            val sqlite = database.openHelper.writableDatabase
            sqlite
                .query("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'season_integrity_expectations'")
                .useCursor { cursor -> Assert.assertTrue(cursor.moveToFirst()) }
            sqlite.query("PRAGMA table_info(season_integrity_expectations)").useCursor { cursor ->
                val nameIndex = cursor.getColumnIndexOrThrow("name")
                val columns = buildSet {
                    while (cursor.moveToNext()) add(cursor.getString(nameIndex))
                }
                Assert.assertTrue("expectedEpisodeNumbers" in columns)
                Assert.assertTrue("lastUpdatedEpochMillis" in columns)
                Assert.assertFalse("playableEpisodeCount" in columns)
                Assert.assertFalse("missingEpisodeCount" in columns)
                Assert.assertFalse("incomplete" in columns)
            }
        } finally {
            database.close()
        }
    }

    @Test
    @Throws(IOException::class)
    fun migrate2To3() {
        val serverId = UUID.randomUUID()
        val userId = UUID.randomUUID()
        helper.createDatabase(testDbName, 2).apply {
            execSQL(
                "INSERT INTO servers VALUES (?, ?, ?)",
                arrayOf(
                    serverId.toString(),
                    "name",
                    "url",
                ),
            )
            execSQL(
                "INSERT INTO users (serverId, id, name, accessToken) VALUES (?, ?, ?, ?)",
                arrayOf(
                    serverId.toString(),
                    userId.toString(),
                    "username",
                    "token",
                ),
            )
            close()
        }

        val db =
            helper.runMigrationsAndValidate(
                testDbName,
                3,
                true,
                migrations = arrayOf(Migrations.Migrate2to3),
            )

        db.query("SELECT id FROM servers").useCursor { c ->
            c.moveToFirst()
            Assert.assertEquals(serverId.toString().replace("-", ""), c.getString(0))
        }
        db.query("SELECT serverId, id FROM users").useCursor { c ->
            c.moveToFirst()
            Assert.assertEquals(serverId.toString().replace("-", ""), c.getString(0))
            Assert.assertEquals(userId.toString().replace("-", ""), c.getString(1))
        }
    }

    @Test
    @Throws(IOException::class)
    fun migrate2To3_2() {
        val serverId = UUID.randomUUID()
        val userId = UUID.randomUUID()
        helper.createDatabase(testDbName, 2).apply {
            execSQL(
                "INSERT INTO servers VALUES (?, ?, ?)",
                arrayOf(
                    serverId.toString().replace("-", ""),
                    "name",
                    "url",
                ),
            )
            execSQL(
                "INSERT INTO users (serverId, id, name, accessToken) VALUES (?, ?, ?, ?)",
                arrayOf(
                    serverId.toString(),
                    userId.toString(),
                    "username",
                    "token",
                ),
            )
            close()
        }

        val db =
            helper.runMigrationsAndValidate(
                testDbName,
                3,
                true,
                migrations = arrayOf(Migrations.Migrate2to3),
            )

        db.query("SELECT id FROM servers").useCursor { c ->
            c.moveToFirst()
            Assert.assertEquals(serverId.toString().replace("-", ""), c.getString(0))
        }
        db.query("SELECT rowId, serverId, id FROM users").useCursor { c ->
            c.moveToFirst()
            Assert.assertTrue(c.getInt(0) > 0)
            Assert.assertEquals(serverId.toString().replace("-", ""), c.getString(1))
            Assert.assertEquals(userId.toString().replace("-", ""), c.getString(2))
        }
    }
}
