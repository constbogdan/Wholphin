import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import mosaic_change_classification as classification
import mosaic_validation_reuse as reuse


MAIN = "c" * 40
BASE = "a" * 40
HEAD = "b" * 40
TESTED = "d" * 40
TREE = "e" * 40


class FakeGitHub:
    def __init__(self, *, full="success", runs=1, artifacts=1, tested_tree=TREE):
        self.full = full
        self.run_count = runs
        self.artifact_count = artifacts
        self.tested_tree = tested_tree

    def call(self, path):
        if path == "actions/workflows/ci.yml":
            return {"id": 42}
        if path == f"git/commits/{TESTED}":
            return {
                "tree": {"sha": self.tested_tree},
                "parents": [{"sha": BASE}, {"sha": HEAD}],
            }
        raise AssertionError(path)

    def pages(self, path, key=None):
        if path == f"commits/{MAIN}/pulls":
            return [
                {
                    "number": 7,
                    "merged_at": "2026-09-11T00:00:00Z",
                    "merge_commit_sha": MAIN,
                    "base": {"sha": BASE, "ref": "main", "repo": {"full_name": reuse.REPOSITORY}},
                    "head": {"sha": HEAD, "ref": "feature", "repo": {"full_name": reuse.REPOSITORY}},
                }
            ]
        if path.startswith("actions/workflows/ci.yml/runs?"):
            return [
                {
                    "id": 100 + index,
                    "run_attempt": 1,
                    "workflow_id": 42,
                    "path": reuse.WORKFLOW,
                    "event": "pull_request",
                    "head_sha": HEAD,
                    "head_branch": "feature",
                    "head_repository": {"full_name": reuse.REPOSITORY},
                    "status": "completed",
                    "conclusion": "success",
                }
                for index in range(self.run_count)
            ]
        match = reuse.re.fullmatch(r"actions/runs/([0-9]+)/attempts/1/jobs", path)
        if match:
            return [
                {
                    "name": reuse.JOB,
                    "status": "completed",
                    "conclusion": "success",
                    "head_sha": HEAD,
                    "steps": [
                        {"name": "Classify PR validation", "conclusion": "success"},
                        {"name": reuse.FULL_STEP, "conclusion": self.full},
                    ],
                }
            ]
        match = reuse.re.fullmatch(r"actions/runs/([0-9]+)/artifacts", path)
        if match:
            run = int(match[1])
            name = reuse.artifact_name(7, HEAD, TESTED, self.tested_tree, run, 1)
            return [
                {
                    "id": 500 + index,
                    "name": name,
                    "expired": False,
                    "digest": "sha256:" + "f" * 64,
                    "workflow_run": {
                        "id": run,
                        "head_sha": HEAD,
                        "head_branch": "feature",
                        "repository_id": 1,
                        "head_repository_id": 1,
                    },
                }
                for index in range(self.artifact_count)
            ]
        raise AssertionError(path)


def environment():
    return {
        "GITHUB_ACTIONS": "true",
        "GITHUB_REPOSITORY": reuse.REPOSITORY,
        "GITHUB_EVENT_NAME": "push",
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_REF_PROTECTED": "true",
        "GITHUB_SHA": MAIN,
    }


def git_values(_root, *args):
    if args == ("rev-parse", "HEAD"):
        return MAIN
    if args == ("rev-parse", "HEAD^{tree}"):
        return TREE
    if args == ("show", "-s", "--format=%P", "HEAD"):
        return f"{BASE} {HEAD}"
    raise AssertionError(args)


class ValidationReuseTests(unittest.TestCase):
    def decide(self, api=None, env=None, git_side_effect=git_values):
        with mock.patch.object(reuse, "git", side_effect=git_side_effect):
            return reuse.decide(ROOT, api or FakeGitHub(), env or environment())

    def test_exact_authenticated_pr_full_reuses_same_tree(self):
        result = self.decide()
        self.assertTrue(result["reuseFull"])
        self.assertEqual(result["testedTree"], TREE)
        self.assertEqual(result["mainTree"], TREE)
        self.assertEqual(result["runId"], "100")

    def test_different_tree_falls_back(self):
        result = self.decide(FakeGitHub(tested_tree="1" * 40))
        self.assertFalse(result["reuseFull"])
        self.assertIn("differs", result["reason"])

    def test_targeted_or_non_android_pr_falls_back(self):
        for conclusion in ("skipped", None):
            with self.subTest(conclusion=conclusion):
                result = self.decide(FakeGitHub(full=conclusion))
                self.assertFalse(result["reuseFull"])
                self.assertIn("missing or ambiguous", result["reason"])

    def test_missing_failed_or_cancelled_pr_full_falls_back(self):
        self.assertFalse(self.decide(FakeGitHub(runs=0))["reuseFull"])
        for conclusion in ("failure", "cancelled"):
            with self.subTest(conclusion=conclusion):
                self.assertFalse(self.decide(FakeGitHub(full=conclusion))["reuseFull"])

    def test_ambiguous_runs_or_artifacts_fall_back(self):
        self.assertFalse(self.decide(FakeGitHub(runs=2))["reuseFull"])
        self.assertFalse(self.decide(FakeGitHub(artifacts=2))["reuseFull"])

    def test_direct_main_or_non_pr_merge_falls_back(self):
        def one_parent(root, *args):
            if args == ("show", "-s", "--format=%P", "HEAD"):
                return BASE
            return git_values(root, *args)

        result = self.decide(git_side_effect=one_parent)
        self.assertFalse(result["reuseFull"])
        self.assertIn("two-parent", result["reason"])

    def test_api_uncertainty_falls_back_without_failing_delivery(self):
        api = mock.Mock()
        api.pages.side_effect = ValueError("transport unavailable")
        result = self.decide(api)
        self.assertFalse(result["reuseFull"])
        self.assertEqual(result["mainTree"], TREE)

    def test_record_binds_synthetic_merge_sha_and_tree(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "output"
            env = {
                "GITHUB_ACTIONS": "true",
                "GITHUB_REPOSITORY": reuse.REPOSITORY,
                "GITHUB_EVENT_NAME": "pull_request",
                "GITHUB_REF": "refs/pull/7/merge",
                "GITHUB_SHA": TESTED,
                "GITHUB_RUN_ID": "100",
                "GITHUB_RUN_ATTEMPT": "1",
                "GITHUB_OUTPUT": str(output),
                "PR_NUMBER": "7",
                "PR_HEAD_SHA": HEAD,
            }

            def pr_git(_root, *args):
                return TESTED if args == ("rev-parse", "HEAD") else TREE

            with mock.patch.object(reuse, "git", side_effect=pr_git):
                result = reuse.record(ROOT, env)
            self.assertEqual(result["testedSha"], TESTED)
            self.assertIn(f"tested-{TESTED}-tree-{TREE}", output.read_text())

    def test_release_assembly_and_non_apk_classification_are_unchanged(self):
        workflow = (ROOT / reuse.WORKFLOW).read_text(encoding="utf-8")
        self.assertIn("if: steps.release-classification.outputs.release_required == 'true'", workflow)
        self.assertIn(":app:assembleDefaultRelease -PmosaicPublication=true", workflow)
        self.assertEqual(
            classification.classify_paths(["docs/AGENTS.md"])["releaseRequired"], False
        )


if __name__ == "__main__":
    unittest.main()
