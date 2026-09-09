"""Offline history fixtures; no monitored repository refs are changed."""

import os
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import mosaic_version as version


class VersionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        self.run_git("init", "-b", "main")
        self.run_git("config", "user.name", "Fixture")
        self.run_git("config", "user.email", "fixture@example.invalid")
        self.commit("epoch")
        self.epoch = self.run_git("rev-parse", "HEAD")

    def run_git(self, *args):
        return subprocess.check_output(["git", "-c", "core.hooksPath=" + os.devnull,
                                        "-c", "commit.gpgsign=false", *args],
                                       cwd=self.root, text=True, stderr=subprocess.PIPE).strip()

    def commit(self, message):
        self.run_git("commit", "--allow-empty", "-m", message)

    def allocate(self, publication=False):
        return version.allocate(self.root, publication, self.epoch)

    def runtime(self):
        return patch.dict(os.environ, GITHUB_ACTIONS="true", GITHUB_REPOSITORY="constbogdan/Wholphin",
                          GITHUB_REF="refs/heads/main", GITHUB_EVENT_NAME="push",
                          GITHUB_SHA=self.run_git("rev-parse", "HEAD"))

    def test_epoch_preview_not_publishable(self):
        self.assertEqual(self.allocate()["versionName"], "1.0.0")
        with self.runtime(), self.assertRaises(ValueError):
            self.allocate(True)

    def test_monotonic_and_repeatable(self):
        for n in range(1, 4):
            self.commit(str(n))
            with self.runtime():
                first = self.allocate(True)
                self.assertEqual(first, self.allocate(True))
            self.assertEqual(first["versionCode"], n)
            self.assertEqual(first["versionName"], f"1.0.{n}")
            self.assertEqual(first["buildTime"], int(self.run_git("show", "-s", "--format=%ct")) * 1000)

    def test_upstream_side_history_and_tags_do_not_allocate_versions(self):
        self.run_git("checkout", "-b", "upstream")
        self.commit("upstream 1")
        self.commit("upstream 2")
        self.run_git("tag", "v99.0.0")
        self.run_git("checkout", "main")
        self.run_git("merge", "--no-ff", "upstream", "-m", "sync")
        original = self.allocate()
        self.assertEqual(original["versionCode"], 1)
        self.run_git("tag", "p999")
        self.assertEqual(original, self.allocate())

    def test_missing_and_non_first_parent_epoch(self):
        with self.assertRaises(ValueError):
            version.allocate(self.root, epoch="f" * 40)
        self.run_git("checkout", "-b", "side")
        self.commit("side epoch")
        side = self.run_git("rev-parse", "HEAD")
        self.run_git("checkout", "main")
        self.run_git("merge", "--no-ff", "side", "-m", "merge")
        with self.assertRaises(ValueError):
            version.allocate(self.root, epoch=side)

    def test_shallow_clone_rejected(self):
        self.commit("next")
        clone = Path(self.temp.name) / "shallow"
        self.run_git("clone", "--depth=1", self.root.as_uri(), str(clone))
        with self.assertRaisesRegex(ValueError, "full Git history"):
            version.allocate(clone, epoch=self.epoch)

    def test_missing_parent_object_rejected(self):
        self.commit("next")
        object_path = self.root / ".git" / "objects" / self.epoch[:2] / self.epoch[2:]
        object_path.chmod(0o600)  # Git creates read-only loose objects on Windows.
        object_path.unlink()
        with self.assertRaisesRegex(ValueError, "complete Git history"):
            self.allocate()

    def test_inherited_git_directory_cannot_change_source(self):
        original = self.allocate()
        with patch.dict(os.environ, GIT_DIR="nonexistent-directory"):
            self.assertEqual(original, self.allocate())

    def test_publication_requires_exact_clean_main_event(self):
        self.commit("next")
        with self.runtime():
            for key, value in [("GITHUB_EVENT_NAME", "pull_request"), ("GITHUB_SHA", "0" * 40),
                               ("GITHUB_REF", "refs/heads/feature"), ("GITHUB_REPOSITORY", "other/repo")]:
                with patch.dict(os.environ, {key: value}), self.assertRaises(ValueError):
                    self.allocate(True)
            (self.root / "untracked").write_text("dirty")
            with self.assertRaises(ValueError):
                self.allocate(True)
            self.assertTrue(self.allocate()["dirty"])

    def test_published_bytes_cannot_change_under_same_identity(self):
        self.commit("next")
        with self.runtime():
            identity = self.allocate(True)
        apk = Path(self.temp.name) / "fixture.apk"
        apk.write_bytes(b"signed fixture one")
        published = version.artifact_record(identity, apk)
        version.verify_record(version.artifact_record(identity, apk), published)
        apk.write_bytes(b"signed fixture two")
        with self.assertRaises(ValueError):
            version.verify_record(version.artifact_record(identity, apk), published)
        with self.assertRaises(ValueError):
            version.artifact_record(self.allocate(), apk)

    def test_manual_exercise_requires_protected_main_and_exact_authorization(self):
        self.commit("next")
        with self.runtime(), patch.dict(os.environ, GITHUB_EVENT_NAME="workflow_dispatch",
                                       GITHUB_REF_PROTECTED="true",
                                       MOSAIC_EXERCISE_SHA=self.run_git("rev-parse", "HEAD")):
            self.assertTrue(self.allocate(True)["publication"])
            for key, value in (("GITHUB_REF_PROTECTED", "false"), ("MOSAIC_EXERCISE_SHA", "0" * 40),
                               ("GITHUB_REF", "refs/heads/feature"), ("GITHUB_EVENT_NAME", "pull_request")):
                with patch.dict(os.environ, {key: value}), self.assertRaises(ValueError):
                    self.allocate(True)

    def test_automatic_development_uses_same_version_only_for_guarded_ci_event(self):
        self.commit("next")
        sha = self.run_git("rev-parse", "HEAD")
        event = dict(action='completed', repository=dict(full_name='constbogdan/Wholphin'),
                     workflow_run=dict(id=1, run_attempt=1, workflow_id=42, head_sha=sha,
                                       head_branch='main', event='push', path='.github/workflows/ci.yml',
                                       head_repository=dict(full_name='constbogdan/Wholphin'),
                                       status='completed', conclusion='success'))
        path = Path(self.temp.name) / 'event.json'
        path.write_text(json.dumps(event))
        with self.runtime():
            expected = self.allocate(True)
            with patch.dict(os.environ, GITHUB_EVENT_NAME='workflow_run', GITHUB_EVENT_PATH=str(path),
                            GITHUB_REF_PROTECTED='true', MOSAIC_EXERCISE_SHA=sha,
                            GITHUB_WORKFLOW_REF='constbogdan/Wholphin/.github/workflows/mosaic-development-release.yml@refs/heads/main'):
                self.assertEqual(self.allocate(True), expected)
                event['workflow_run']['conclusion'] = 'failure'
                path.write_text(json.dumps(event))
                with self.assertRaises(ValueError):
                    self.allocate(True)


if __name__ == "__main__":
    unittest.main()
