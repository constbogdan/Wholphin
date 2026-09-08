"""Offline integration tests: disposable Git repositories and an in-memory GitHub.

Run: python -B -m unittest discover -s scripts -p 'test_hosted_upstream.py' -v
No test contacts GitHub or mutates the application checkout.
"""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import hosted_upstream as sync


class GitHubFake:
    def __init__(self):
        self.records = []
        self.issue_records = []
        self.created = []
        self.fail_pr = False

    def pulls(self):
        return self.records

    def issues(self):
        return self.issue_records

    def create_pr(self, branch, body):
        if self.fail_pr:
            raise sync.Blocked("PR creation failed")
        self.created.append((branch, body))
        return "https://github.com/constbogdan/Wholphin/pull/123"


class LocalGit(sync.Git):
    def __init__(self, path, remotes):
        self.remotes = remotes
        self.pushes = []
        super().__init__(path)
        # Explicit fixture-only local transport. Production forbids file URLs.
        self.options += ["-c", "protocol.file.allow=always"]

    def fetch(self, remote, source, destination):
        self.run("fetch", "--quiet", "--no-tags", str(self.remotes[remote]), f"{source}:{destination}")

    def text(self, *args):
        if args[0] == "ls-remote":
            args = tuple(str(self.remotes.get(a, a)) for a in args)
        return super().text(*args)

    def push(self, branch, candidate):
        self.identities()
        args = ("push", "--porcelain", str(self.remotes["origin"]), f"{candidate}:refs/heads/{branch}")
        self.pushes.append(args)
        self.run(*args)


class HostedSyncTests(unittest.TestCase):
    def setUp(self):
        token = patch.dict(os.environ, {"SYNC_PUBLISH_TOKEN": "fixture-only-never-sent"})
        token.start()
        self.addCleanup(token.stop)
        self.temp = tempfile.TemporaryDirectory(prefix="wholphin-sync-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.seed = self.root / "seed"
        self.seed.mkdir()
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
                        GIT_AUTHOR_NAME="Fixture", GIT_COMMITTER_NAME="Fixture",
                        GIT_AUTHOR_EMAIL="fixture@example.invalid", GIT_COMMITTER_EMAIL="fixture@example.invalid")
        self.g("init", "-b", "main")
        self.commit("base.txt", "base\n")
        self.anchor = self.g("rev-parse", "HEAD")
        self.remotes = {name: self.root / (name + ".git") for name in ("origin", "upstream")}
        for remote in self.remotes.values():
            self.g("clone", "--bare", str(self.seed), str(remote))
        self.github = GitHubFake()

    def g(self, *args):
        result = subprocess.run(["git", "-c", "core.autocrlf=false", "-c", "core.hooksPath=" + os.devnull,
                                 *args], cwd=self.seed, env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def commit(self, name, content):
        path = self.seed / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        self.g("add", "--", name)
        self.g("commit", "-m", "Update " + name)
        return self.g("rev-parse", "HEAD")

    def upstream(self, name="upstream.txt", content="incoming\n"):
        sha = self.commit(name, content)
        self.g("push", str(self.remotes["upstream"]), "HEAD:refs/heads/main")
        return sha

    def instance(self):
        path = self.root / ("work-" + str(len(list(self.root.glob("work-*")))))
        path.mkdir()
        return LocalGit(path, self.remotes)

    def observe(self, git=None):
        git = git or self.instance()
        o = {"upstream_repo": sync.UPSTREAM, "downstream_repo": sync.ORIGIN}
        sync.inspect(git, self.github, o, self.anchor)
        return git, o

    def pr(self, o, state="open", head=None):
        return {"number": 123, "state": state, "html_url": "https://github.com/constbogdan/Wholphin/pull/123",
                "base": {"ref": "main", "repo": {"full_name": sync.ORIGIN}},
                "head": {"ref": o["branch"], "sha": head or o["candidate_sha"], "repo": {"full_name": sync.ORIGIN}}}

    def retain_pr(self, git, o, state="open", head=None):
        git.run("push", str(self.remotes["origin"]), f"{o['candidate_sha']}:refs/pull/123/head")
        self.github.records = [self.pr(o, state, head)]

    def test_no_delta_and_no_remote_mutation(self):
        git, o = self.observe()
        self.assertEqual(o["outcome"], "no_delta")
        sync.publish(git, self.github, o, o["upstream_sha"], o["downstream_sha"])
        self.assertFalse(git.pushes or self.github.created)

    def test_upstream_ahead_normal_merge_exact_parents_and_metadata(self):
        up = self.upstream()
        git, o = self.observe()
        self.assertEqual(o["outcome"], "ready")
        self.assertEqual(git.text("show", "-s", "--format=%P", o["candidate_sha"]), self.anchor + " " + up)
        self.assertEqual(o["incoming_count"], 1)
        self.assertEqual(o["changed_paths"], ["upstream.txt"])
        body = sync.description(o)
        for text in (up, self.anchor, "Full validation", "pending", "Human semantic review", "upstream.txt", "textual_conflicts: False"):
            self.assertIn(text, body)

    def test_divergent_downstream_preserved(self):
        up = self.upstream()
        self.g("checkout", "--detach", self.anchor)
        down = self.commit("custom.txt", "downstream\n")
        self.g("push", str(self.remotes["origin"]), "HEAD:refs/heads/main")
        git, o = self.observe()
        self.assertEqual(o["downstream_sha"], down)
        self.assertTrue(git.ancestor(up, o["candidate_sha"]))
        self.assertEqual(git.text("show", o["candidate_sha"] + ":custom.txt"), "downstream")

    def test_textual_conflict_stops_before_push(self):
        self.upstream("base.txt", "upstream\n")
        self.g("checkout", "--detach", self.anchor)
        self.commit("base.txt", "downstream\n")
        self.g("push", str(self.remotes["origin"]), "HEAD:refs/heads/main")
        git, o = self.instance(), {}
        with self.assertRaisesRegex(sync.Blocked, "Textual conflicts"):
            sync.inspect(git, self.github, o, self.anchor)
        self.assertEqual(o["conflict_paths"], ["base.txt"])
        self.assertTrue(o["textual_conflicts"])
        self.assertFalse(git.pushes)

    def test_invalid_fetch_or_push_identity(self):
        for push in (False, True):
            git = self.instance()
            git.run("remote", "set-url", *(["--push"] if push else []), "origin", "https://github.com/other/repo.git")
            with self.assertRaisesRegex(sync.Blocked, "Unexpected origin"):
                self.observe(git)
            self.assertFalse(git.pushes)

    def test_initial_anchor_rewrite_refused(self):
        self.upstream()
        git = self.instance()
        with self.assertRaises(sync.Blocked):
            sync.inspect(git, self.github, {}, "f" * 40)

    def test_recorded_upstream_rewrite_refused(self):
        first = self.upstream()
        git, old = self.observe()
        self.retain_pr(git, old, "closed")
        self.g("checkout", "--detach", self.anchor)
        self.commit("replacement.txt", "rewritten\n")
        # Fixture-only rewrite simulates an upstream event; executor never does this.
        self.g("push", "--force", str(self.remotes["upstream"]), "HEAD:refs/heads/main")
        with self.assertRaisesRegex(sync.Blocked, "not a descendant.*" + first):
            self.observe()

    def test_conflict_observation_is_rewrite_anchor(self):
        old = self.upstream()
        self.github.issue_records = [{"body": f"<!-- wholphin-upstream-observed:{old} -->"}]
        self.g("checkout", "--detach", self.anchor)
        self.commit("other.txt", "different\n")
        self.g("push", "--force", str(self.remotes["upstream"]), "HEAD:refs/heads/main")
        with self.assertRaisesRegex(sync.Blocked, "not a descendant"):
            self.observe()

    def test_orphan_published_branch_is_rewrite_anchor(self):
        self.upstream()
        git, o = self.observe()
        git.push(o["branch"], o["candidate_sha"])
        self.g("checkout", "--detach", self.anchor)
        self.commit("replacement.txt", "rewrite after interrupted publication\n")
        self.g("push", "--force", str(self.remotes["upstream"]), "HEAD:refs/heads/main")
        with self.assertRaisesRegex(sync.Blocked, "not a descendant"):
            self.observe()

    def test_deterministic_branch_and_commit_across_retries(self):
        self.upstream()
        _, a = self.observe()
        _, b = self.observe()
        self.assertEqual(a["branch"], b["branch"])
        self.assertEqual(a["candidate_sha"], b["candidate_sha"])
        self.assertEqual(sync.BRANCH.fullmatch(a["branch"]).groups(), (a["upstream_sha"], a["downstream_sha"]))
        self.assertNotEqual(a["branch"], sync.branch_name(a["upstream_sha"], "a" * 40))
        with self.assertRaises(sync.Blocked):
            sync.branch_name("--unsafe", a["downstream_sha"])

    def test_existing_open_pr_reused_without_writes(self):
        self.upstream()
        git, o = self.observe()
        self.retain_pr(git, o)
        retry, result = self.observe()
        self.assertEqual(result["outcome"], "existing_pr")
        sync.publish(retry, self.github, result, result["upstream_sha"], result["downstream_sha"])
        self.assertFalse(retry.pushes or self.github.created)

    def test_closed_pr_not_reopened(self):
        self.upstream()
        git, o = self.observe()
        self.retain_pr(git, o, "closed")
        with self.assertRaisesRegex(sync.Blocked, "closed or ambiguous"):
            self.observe()

    def test_new_upstream_preserves_older_open_pr(self):
        self.upstream()
        git, o = self.observe()
        self.retain_pr(git, o)
        self.upstream("newer.txt")
        with self.assertRaisesRegex(sync.Blocked, "Another sync PR is open"):
            self.observe()

    def test_human_changes_to_pr_head_preserved(self):
        self.upstream()
        git, o = self.observe()
        self.retain_pr(git, o, head="b" * 40)
        with self.assertRaisesRegex(sync.Blocked, "preserve human changes"):
            self.observe()

    def test_publish_only_candidate_branch_without_force(self):
        self.upstream()
        git, o = self.observe()
        sync.publish(git, self.github, o, o["upstream_sha"], o["downstream_sha"])
        self.assertEqual(o["outcome"], "pr_created")
        self.assertEqual(len(git.pushes), 1)
        self.assertNotIn("--force", git.pushes[0])
        self.assertNotIn("+", git.pushes[0][-1])
        self.assertTrue(git.pushes[0][-1].endswith(o["branch"]))
        self.assertEqual(git.text("ls-remote", "--refs", "origin", "refs/heads/main").split()[0], self.anchor)

    def test_pr_failure_retry_reuses_published_branch(self):
        self.upstream()
        git, o = self.observe()
        self.github.fail_pr = True
        with self.assertRaisesRegex(sync.Blocked, "PR creation failed"):
            sync.publish(git, self.github, o, o["upstream_sha"], o["downstream_sha"])
        retry, result = self.observe()
        self.github.fail_pr = False
        sync.publish(retry, self.github, result, result["upstream_sha"], result["downstream_sha"])
        self.assertFalse(retry.pushes)
        self.assertEqual(result["outcome"], "pr_created")

    def test_push_failure_never_creates_pr(self):
        self.upstream()
        git, o = self.observe()
        with patch.object(git, "push", side_effect=sync.Blocked("push failed")):
            with self.assertRaises(sync.Blocked):
                sync.publish(git, self.github, o, o["upstream_sha"], o["downstream_sha"])
        self.assertFalse(self.github.created)

    def test_missing_app_token_stops_before_push(self):
        self.upstream()
        git, o = self.observe()
        with patch.dict(os.environ, {"SYNC_PUBLISH_TOKEN": ""}):
            with self.assertRaisesRegex(sync.Blocked, "App token unavailable"):
                sync.publish(git, self.github, o, o["upstream_sha"], o["downstream_sha"])
        self.assertFalse(git.pushes or self.github.created)

    def test_changed_job_inputs_and_late_ref_drift_block(self):
        self.upstream()
        git, o = self.observe()
        with self.assertRaisesRegex(sync.Blocked, "between read and publish"):
            sync.publish(git, self.github, o, "c" * 40, o["downstream_sha"])
        self.upstream("later.txt")
        with self.assertRaisesRegex(sync.Blocked, "moved immediately"):
            sync.publish(git, self.github, o, o["upstream_sha"], o["downstream_sha"])
        self.assertFalse(git.pushes or self.github.created)

    def test_existing_different_branch_never_overwritten(self):
        self.upstream()
        git, o = self.observe()
        git.run("push", str(self.remotes["origin"]), f"{self.anchor}:refs/heads/{o['branch']}")
        with self.assertRaisesRegex(sync.Blocked, "different work"):
            sync.publish(git, self.github, o, o["upstream_sha"], o["downstream_sha"])

    def test_automation_changes_fail_closed(self):
        self.upstream(".github/workflows/main.yml", "unreviewed publisher\n")
        with self.assertRaisesRegex(sync.Blocked, "publisher guards"):
            self.observe()

    def test_body_escapes_external_markup_and_mentions(self):
        body = sync.description({"incoming_commits": [{"sha": "a" * 40, "subject": "<script>@everyone</script>"}]})
        self.assertNotIn("<script>", body)
        self.assertNotIn("@everyone", body)

    def test_blocked_issue_deduplication_including_closed_issue(self):
        github = sync.GitHub()
        created = []
        def create(endpoint, payload):
            created.append({**payload, "html_url": "https://github.com/constbogdan/Wholphin/issues/5"})
            return created[-1]
        with patch.object(github, "issues", side_effect=lambda: created), patch.object(github, "api", side_effect=create):
            o = {"upstream_sha": "a" * 40, "downstream_sha": "b" * 40, "reason": "conflict"}
            self.assertEqual(github.blocked_issue(o), github.blocked_issue(o))
            self.assertEqual(len(created), 1)

    def test_non_hosted_cli_cannot_mutate(self):
        output = self.root / "out.json"
        runtime = {"GITHUB_ACTIONS": "false", "GITHUB_OUTPUT": str(self.root / "outputs"),
                   "GITHUB_STEP_SUMMARY": str(self.root / "summary.md")}
        with patch.dict(os.environ, runtime), patch("sys.argv", ["hosted_upstream", "--publish", "--output", str(output)]), patch.object(sync.GitHub, "blocked_issue") as issue:
            self.assertEqual(sync.main(), 1)
        self.assertFalse(issue.called)
        self.assertEqual(json.loads(output.read_text())["outcome"], "blocked")

    def test_github_subprocess_credentials_are_operation_scoped(self):
        github = sync.GitHub()
        with patch.dict(os.environ, {"GH_TOKEN": "read-only-repository-token"}), patch.object(sync, "command") as run:
            run.return_value.stdout = "[]"
            github.pulls()
            github.api("repos/constbogdan/Wholphin/issues", {"title": "blocked"})
            for call in run.call_args_list:
                self.assertEqual(call.kwargs["env"]["GH_TOKEN"], "read-only-repository-token")
                self.assertNotIn("SYNC_PUBLISH_TOKEN", call.kwargs["env"])
            run.return_value.stdout = '{"html_url": "https://github.com/constbogdan/Wholphin/pull/1"}'
            github.create_pr(sync.branch_name("a" * 40, "b" * 40), "fixture")
            self.assertEqual(run.call_args.kwargs["env"]["GH_TOKEN"], "fixture-only-never-sent")
            self.assertNotIn("SYNC_PUBLISH_TOKEN", run.call_args.kwargs["env"])
            self.assertNotIn("fixture-only-never-sent", str(run.call_args.args))

    def test_production_push_refspec_and_credential_isolation(self):
        git = self.instance()
        self.assertNotIn("SYNC_PUBLISH_TOKEN", git.env)
        self.assertNotIn("GH_TOKEN", git.env)
        branch = sync.branch_name("a" * 40, "b" * 40)
        with patch.object(sync, "command") as run:
            # Invoke the production implementation, not the fixture transport.
            with patch.object(git, "identities"):
                sync.Git.push(git, branch, "c" * 40)
        args = run.call_args.args[0]
        self.assertEqual(args[-2:], ["origin", "c" * 40 + ":refs/heads/" + branch])
        self.assertFalse(any(arg.startswith(("--force", "+")) for arg in args))
        self.assertNotIn("fixture-only-never-sent", " ".join(args))
        self.assertEqual(run.call_args.kwargs["env"]["GH_TOKEN"], "fixture-only-never-sent")

    def test_failed_cli_records_durable_issue_and_machine_outcome(self):
        output = self.root / "blocked.json"
        runtime = {"GITHUB_ACTIONS": "true", "GITHUB_REPOSITORY": sync.ORIGIN,
                   "GITHUB_REF": "refs/heads/main", "GITHUB_EVENT_NAME": "workflow_dispatch",
                   "RUNNER_TEMP": str(self.root), "GITHUB_STEP_SUMMARY": str(self.root / "summary.md"),
                   "GITHUB_OUTPUT": str(self.root / "outputs")}
        def conflict(git, gh, observation):
            observation.update(upstream_sha="a" * 40, downstream_sha="b" * 40,
                               conflict_paths=["source.kt"], textual_conflicts=True)
            raise sync.Blocked("Textual conflicts require review.")
        with patch.dict(os.environ, runtime), patch("sys.argv", ["hosted_upstream", "--publish", "--output", str(output)]), patch.object(sync, "inspect", side_effect=conflict), patch.object(sync.GitHub, "blocked_issue", return_value="https://github.com/constbogdan/Wholphin/issues/1") as issue:
            self.assertEqual(sync.main(), 1)
        self.assertTrue(issue.called)
        result = json.loads(output.read_text())
        self.assertTrue(result["textual_conflicts"])
        self.assertEqual(result["conflict_paths"], ["source.kt"])
        self.assertIn("blocked_issue_url", result)
        self.assertIn("outcome=blocked", (self.root / "outputs").read_text())

    def test_upstream_contained_after_accepted_merge_no_new_pr(self):
        self.upstream()
        git, o = self.observe()
        git.run("push", str(self.remotes["origin"]), o["candidate_sha"] + ":refs/heads/main")
        _, result = self.observe()
        self.assertEqual(result["outcome"], "no_delta")


if __name__ == "__main__":
    unittest.main()
