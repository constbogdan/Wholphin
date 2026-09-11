"""Offline integration tests: disposable Git repositories and an in-memory GitHub.

Run: python -B -m unittest discover -s scripts -p 'test_hosted_upstream.py' -v
No test contacts GitHub or mutates the application checkout.
"""

import json
import io
from contextlib import redirect_stdout
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
        self.journals = []
        self.fail_pr = False
        self.available_labels = set(sync.MANAGED_LABELS)

    def pulls(self):
        return self.records

    def issues(self):
        return self.issue_records

    def labels(self):
        return set(self.available_labels)

    def create_pr(self, branch, body, *, draft=False, title=None):
        if self.fail_pr:
            raise sync.Blocked("PR creation failed")
        self.created.append((branch, body, draft, title))
        return "https://github.com/constbogdan/Wholphin/pull/123"

    def journal_issue(self, observation):
        marker = sync.journal_state_marker(observation)
        issue = next((record for record in self.issue_records if marker in record["body"]), None)
        sync.update_observation_history(observation, issue)
        labels = sync.issue_labels(issue, observation, self.available_labels)
        if issue is None:
            issue = {"number": len(self.issue_records) + 1, "state": "open", "labels": labels,
                     "html_url": f"https://github.com/constbogdan/Wholphin/issues/{len(self.issue_records) + 1}"}
            self.issue_records.append(issue)
        issue.update(title=sync.priority_title(observation["priority"]),
                     body=sync.issue_body(observation), labels=labels)
        self.journals.append((issue, observation["outcome"]))
        return issue

    def update_journal(self, issue, observation, *, close=False):
        issue.update(title=sync.priority_title(observation["priority"]),
                     body=sync.issue_body(observation),
                     labels=sync.issue_labels(issue, observation, self.available_labels))
        if close:
            issue["state"] = "closed"
        self.journals.append((issue, observation["outcome"], close))
        return issue


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

    def observe(self, git=None, **values):
        git = git or self.instance()
        o = {"upstream_repo": sync.UPSTREAM, "downstream_repo": sync.ORIGIN}
        o.update(values)
        sync.inspect(git, self.github, o, self.anchor)
        return git, o

    def pr(self, o, state="open", head=None, draft=False, body=None):
        return {"number": 123, "state": state, "html_url": "https://github.com/constbogdan/Wholphin/pull/123",
                "draft": draft, "body": body if body is not None else sync.description(o),
                "base": {"ref": "main", "repo": {"full_name": sync.ORIGIN}},
                "head": {"ref": o["branch"], "sha": head or o["candidate_sha"], "repo": {"full_name": sync.ORIGIN}}}

    def retain_pr(self, git, o, state="open", head=None, draft=False, body=None):
        git.run("push", str(self.remotes["origin"]), f"{o['candidate_sha']}:refs/pull/123/head")
        self.github.records = [self.pr(o, state, head, draft=draft, body=body)]

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
        for text in (up, self.anchor, "Human review", "upstream.txt", "1 additional file integrates cleanly"):
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

    def test_textual_conflict_creates_deterministic_blocked_workspace(self):
        self.upstream("base.txt", "upstream\n")
        self.g("checkout", "--detach", self.anchor)
        self.commit("base.txt", "downstream\n")
        self.g("push", str(self.remotes["origin"]), "HEAD:refs/heads/main")
        git, o = self.instance(), {}
        sync.inspect(git, self.github, o, self.anchor)
        self.assertEqual(o["outcome"], "semantic_conflict")
        self.assertEqual(o["conflict_paths"], ["base.txt"])
        self.assertTrue(o["textual_conflicts"])
        self.assertFalse(git.ancestor(o["upstream_sha"], o["candidate_sha"]))
        sync.publish(git, self.github, o, o["upstream_sha"], o["downstream_sha"])
        self.assertEqual(o["outcome"], "blocked")
        self.assertTrue(self.github.created[0][2])
        self.assertFalse(self.github.journals[-1][2])
        self.assertEqual(1, len(git.pushes))
        self.assertNotIn("--force", git.pushes[0])

        git.run("push", str(self.remotes["origin"]),
                f"{o['candidate_sha']}:refs/pull/123/head")
        self.github.records = [self.pr(o, draft=True)]
        retry, existing = self.observe()
        self.assertEqual("existing_draft_pr", existing["outcome"])
        sync.publish(retry, self.github, existing, existing["upstream_sha"], existing["downstream_sha"])
        self.assertFalse(retry.pushes)
        self.assertEqual("open", self.github.issue_records[0]["state"])

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

    def test_draft_pr_appearing_during_publish_remains_blocked_and_open(self):
        self.upstream(".github/workflows/release.yml", "review\n")
        git, observation = self.observe()
        self.assertEqual("review_required", observation["outcome"])
        self.github.records = [self.pr(observation, draft=True)]
        sync.publish(git, self.github, observation, observation["upstream_sha"], observation["downstream_sha"])
        self.assertEqual("existing_draft_pr", observation["outcome"])
        self.assertFalse(git.pushes or self.github.created)
        self.assertFalse(self.github.journals[-1][2])

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
        output = io.StringIO()
        with patch.dict(os.environ, {"SYNC_PUBLISH_TOKEN": ""}), redirect_stdout(output):
            with self.assertRaisesRegex(sync.Blocked, "App token unavailable"):
                sync.publish(git, self.github, o, o["upstream_sha"], o["downstream_sha"])
        self.assertFalse(git.pushes or self.github.created)
        self.assertEqual(output.getvalue(), "SYNC_PUBLISH_TOKEN: missing\n")

    def test_token_presence_does_not_log_value(self):
        self.upstream()
        git, o = self.observe()
        output = io.StringIO()
        with redirect_stdout(output):
            sync.publish(git, self.github, o, o['upstream_sha'], o['downstream_sha'])
        self.assertEqual(output.getvalue(), 'SYNC_PUBLISH_TOKEN: present\n')
        self.assertNotIn('fixture-only-never-sent', output.getvalue())

    def test_disabled_issues_fail_without_creation_or_app_credential(self):
        github = sync.GitHub()
        with patch.object(github, 'api', return_value={'has_issues': False}) as api:
            with self.assertRaisesRegex(sync.Blocked, 'Issues are disabled'):
                github.blocked_issue({'reason': 'conflict'})
        api.assert_called_once_with('repos/' + sync.ORIGIN)

    def test_workflow_app_output_and_permission_boundaries(self):
        workflow = (Path(__file__).resolve().parent.parent / '.github/workflows/upstream-sync.yml').read_text()
        observe, publish = workflow.split('\n  publish:\n')
        self.assertNotIn('secrets.', observe)
        self.assertNotIn('SYNC_PUBLISH_TOKEN', observe)
        self.assertNotIn(': write', observe)
        self.assertNotIn('contents: write', publish.split('    steps:')[0])
        self.assertNotIn('pull-requests: write', publish.split('    steps:')[0])
        self.assertIn('issues: write', publish)
        for part in (observe, publish):
            self.assertIn("github.repository == 'constbogdan/Wholphin' && github.ref == 'refs/heads/main'", part)
        self.assertIn("needs.observe.outputs.outcome != 'no_delta'", publish)
        mint, execution = publish.split('      - name: Recheck exact inputs', 1)
        self.assertIn('contains(fromJSON', mint)
        for outcome in ('ready', 'review_required', 'semantic_conflict'):
            self.assertIn(outcome, mint)
        self.assertIn('id: publication', mint)
        self.assertIn('uses: actions/create-github-app-token@', mint)
        for expected in ('client-id: ${{ vars.SYNC_BOT_CLIENT_ID }}', 'private-key: ${{ secrets.SYNC_BOT_PRIVATE_KEY }}',
                         'owner: constbogdan', 'repositories: Wholphin', 'permission-contents: write',
                         'permission-pull-requests: write'):
            self.assertIn(expected, mint)
        self.assertIn('SYNC_PUBLISH_TOKEN: ${{ steps.publication.outputs.token }}', execution)
        self.assertIn('GH_TOKEN: ${{ github.token }}', execution)
        self.assertIn('EXPECTED_UPSTREAM: ${{ needs.observe.outputs.upstream }}', execution)
        self.assertIn('EXPECTED_DOWNSTREAM: ${{ needs.observe.outputs.downstream }}', execution)
        self.assertIn('if: always()', execution)
        self.assertNotIn('MOSAIC_', workflow)

        finalize = workflow.split('\n  finalize-merged-episode:\n', 1)[1]
        self.assertIn("github.event.pull_request.merged == true", finalize)
        self.assertIn("startsWith(github.event.pull_request.head.ref, 'chore/sync-upstream-')", finalize)
        self.assertIn("--finalize-merged-pr", finalize)
        self.assertIn("issues: write", finalize)
        self.assertIn("pull-requests: read", finalize)
        self.assertNotIn("contents: write", finalize)
        self.assertNotIn("create-github-app-token", finalize)

    def test_merged_candidate_closes_exact_linked_journal_idempotently(self):
        episode = "e" * 64
        merge_sha = "c" * 40
        pr = {
            "number": 36,
            "state": "closed",
            "merged_at": "2026-09-11T01:00:00Z",
            "merge_commit_sha": merge_sha,
            "body": f"<!-- wholphin-upstream-episode:{episode} -->",
            "base": {"ref": "main", "repo": {"full_name": sync.ORIGIN}},
            "head": {
                "ref": sync.branch_name("a" * 40, "b" * 40),
                "repo": {"full_name": sync.ORIGIN},
            },
        }
        issue = {
            "number": 35,
            "state": "open",
            "body": f"Attention history\n<!-- wholphin-upstream-episode:{episode} -->",
            "labels": ["risk: medium", "debt: high", "attention", "human-review"],
        }

        class FinalizeFake:
            def __init__(self):
                self.patches = []

            def api(self, endpoint, payload=None, **kwargs):
                if payload is None:
                    return pr
                self.patches.append((endpoint, payload, kwargs))
                issue.update(payload)
                return issue

            def issues(self):
                return [issue]

        github = FinalizeFake()
        result = sync.finalize_merged_episode(github, 36)
        self.assertEqual("journal_closed_merged", result["outcome"])
        self.assertEqual("closed", issue["state"])
        self.assertEqual("completed", issue["state_reason"])
        self.assertEqual(["human-review"], issue["labels"])
        self.assertIn("Resolved upstream integration", issue["body"])
        self.assertIn("https://github.com/constbogdan/Wholphin/pull/36", issue["body"])
        self.assertNotIn("github.com/damontecres", issue["body"])
        self.assertEqual("PATCH", github.patches[0][2]["method"])

        repeated = sync.finalize_merged_episode(github, 36)
        self.assertEqual("journal_already_closed", repeated["outcome"])
        self.assertEqual(1, len(github.patches))

    def test_merged_journal_finalization_rejects_unlinked_or_unmerged_pr(self):
        episode = "e" * 64
        base_pr = {
            "number": 36,
            "state": "closed",
            "merged_at": "2026-09-11T01:00:00Z",
            "merge_commit_sha": "c" * 40,
            "body": f"<!-- wholphin-upstream-episode:{episode} -->",
            "base": {"ref": "main", "repo": {"full_name": sync.ORIGIN}},
            "head": {
                "ref": sync.branch_name("a" * 40, "b" * 40),
                "repo": {"full_name": sync.ORIGIN},
            },
        }

        class RefusalFake:
            def __init__(self, pr, issues):
                self.pr = pr
                self.issue_records = issues

            def api(self, endpoint, payload=None, **kwargs):
                if payload is not None:
                    raise AssertionError("refusal must occur before mutation")
                return self.pr

            def issues(self):
                return self.issue_records

        unmerged = dict(base_pr, merged_at=None)
        with self.assertRaisesRegex(sync.Blocked, "does not authenticate"):
            sync.finalize_merged_episode(RefusalFake(unmerged, []), 36)
        unrelated = [{"number": 35, "state": "open", "body": "different episode"}]
        with self.assertRaisesRegex(sync.Blocked, "exactly one journal"):
            sync.finalize_merged_episode(RefusalFake(base_pr, unrelated), 36)

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

    def test_downstream_owned_automation_is_observed_and_excluded(self):
        self.upstream(".github/workflows/main.yml", "unreviewed publisher\n")
        git, observation = self.observe()
        self.assertEqual("observed_excluded", observation["outcome"])
        self.assertEqual("DOWNSTREAM-OWNED", observation["automation_changes"][0]["ownership"])
        self.assertFalse(git.pushes)
        sync.publish(git, self.github, observation, observation["upstream_sha"], observation["downstream_sha"])
        self.assertFalse(self.github.journals)

    def test_owned_deletion_preserves_downstream_file_and_is_excluded(self):
        self.commit(".github/workflows/main.yml", "owned\n")
        self.anchor = self.g("rev-parse", "HEAD")
        for remote in self.remotes.values():
            self.g("push", str(remote), "HEAD:refs/heads/main")
        self.g("rm", ".github/workflows/main.yml")
        self.g("commit", "-m", "Delete owned workflow")
        self.g("push", str(self.remotes["upstream"]), "HEAD:refs/heads/main")
        _, observation = self.observe()
        self.assertEqual("observed_excluded", observation["outcome"])
        self.assertEqual("D", observation["automation_changes"][0]["status"])

    def test_owned_rename_restores_both_downstream_path_states_in_mixed_candidate(self):
        old = ".github/workflows/mosaic-development-release.yml"
        new = ".github/workflows/mosaic-development-resume.yml"
        self.commit(old, "downstream release\n")
        self.anchor = self.g("rev-parse", "HEAD")
        for remote in self.remotes.values():
            self.g("push", str(remote), "HEAD:refs/heads/main")
        self.g("mv", old, new)
        self.commit("app/example.kt", "follow\n")
        self.g("push", str(self.remotes["upstream"]), "HEAD:refs/heads/main")
        git, observation = self.observe()
        self.assertEqual("ready", observation["outcome"])
        self.assertEqual("downstream release", git.text("show", observation["candidate_sha"] + ":" + old))
        self.assertNotEqual(0, git.run("cat-file", "-e", observation["candidate_sha"] + ":" + new,
                                       check=False).returncode)
        self.assertEqual("follow", git.text("show", observation["candidate_sha"] + ":app/example.kt"))

    def test_explicit_follow_and_review_policy_have_distinct_outcomes(self):
        self.upstream(".github/actions/setup/action.yml", "follow setup\n")
        follow_git, follow = self.observe()
        self.assertEqual("ready", follow["outcome"])
        self.assertEqual("FOLLOW", follow["automation_changes"][0]["ownership"])
        self.assertEqual("follow setup", follow_git.text(
            "show", follow["candidate_sha"] + ":.github/actions/setup/action.yml"))

        self.upstream(".github/workflows/release.yml", "review release\n")
        _, review = self.observe()
        self.assertEqual("review_required", review["outcome"])
        release = next(change for change in review["automation_changes"]
                       if change["path"] == ".github/workflows/release.yml")
        self.assertEqual("REVIEW", release["ownership"])
        self.assertIn("semantic review", release["reason"])

    def test_later_owned_change_produces_new_observed_state(self):
        first = self.upstream(".github/workflows/main.yml", "one\n")
        _, a = self.observe()
        second = self.upstream(".github/workflows/main.yml", "two\n")
        _, b = self.observe()
        self.assertEqual("observed_excluded", a["outcome"])
        self.assertEqual("observed_excluded", b["outcome"])
        self.assertEqual((first, second), (a["upstream_sha"], b["upstream_sha"]))
        self.assertNotEqual(a["automation_changes"][0]["new_blob"], b["automation_changes"][0]["new_blob"])

    def test_unknown_automation_defaults_to_review_and_creates_draft(self):
        self.upstream(".github/workflows/future.yml", "future\n")
        git, observation = self.observe()
        self.assertEqual("review_required", observation["outcome"])
        self.assertEqual("REVIEW", observation["automation_changes"][0]["ownership"])
        sync.publish(git, self.github, observation, observation["upstream_sha"], observation["downstream_sha"])
        self.assertEqual("review_pr_created", observation["outcome"])
        self.assertTrue(self.github.created[0][2])
        self.assertEqual("chore: review upstream changes to future.yml", self.github.created[0][3])
        self.assertIn(observation["journal_issue_url"], self.github.created[0][1])
        self.assertIn(observation["pr_url"], self.github.issue_records[0]["body"])
        self.assertFalse(self.github.journals[-1][2])

    def test_rename_crossing_ownership_boundary_requires_review(self):
        self.commit(".github/actions/setup/action.yml", "setup\n")
        self.anchor = self.g("rev-parse", "HEAD")
        for remote in self.remotes.values():
            self.g("push", str(remote), "HEAD:refs/heads/main")
        (self.seed / ".github/workflows").mkdir(parents=True, exist_ok=True)
        self.g("mv", ".github/actions/setup/action.yml", ".github/workflows/main.yml")
        self.g("commit", "-m", "Cross ownership boundary")
        self.g("push", str(self.remotes["upstream"]), "HEAD:refs/heads/main")
        _, observation = self.observe()
        change = observation["automation_changes"][0]
        self.assertTrue(change["status"].startswith("R"))
        self.assertEqual("REVIEW", change["ownership"])
        self.assertIn("crosses ownership", change["reason"])

    def test_mixed_changes_keep_all_ownership_evidence(self):
        self.upstream("app/example.kt", "app\n")
        self.upstream(".github/actions/setup/action.yml", "setup\n")
        self.upstream(".github/workflows/future.yml", "review\n")
        self.upstream(".github/workflows/main.yml", "owned\n")
        _, observation = self.observe()
        self.assertEqual("review_required", observation["outcome"])
        self.assertEqual({"FOLLOW": 2, "REVIEW": 1, "DOWNSTREAM-OWNED": 1}, observation["ownership_counts"])
        self.assertEqual(4, len(observation["automation_changes"]))

    def test_trusted_policy_and_schedule_contract(self):
        policy = sync.load_policy()
        self.assertEqual(1, policy["schemaVersion"])
        self.assertEqual("REVIEW", policy["defaultAutomationOwnership"])
        self.assertEqual("DOWNSTREAM-OWNED", policy["paths"][".github/workflows/main.yml"])
        self.assertEqual("FOLLOW", policy["paths"][".github/actions/setup/action.yml"])
        workflow = (Path(__file__).resolve().parent.parent / ".github/workflows/upstream-sync.yml").read_text()
        self.assertIn("cron: '0 6,15,21 * * *'", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("cancel-in-progress: false", workflow)

    def test_issue_failure_does_not_discard_valid_candidate(self):
        self.upstream()
        git, observation = self.observe()
        with patch.object(self.github, "journal_issue", side_effect=sync.OperationError("issue unavailable")):
            sync.publish(git, self.github, observation, observation["upstream_sha"], observation["downstream_sha"])
        self.assertEqual("pr_created", observation["outcome"])
        self.assertIn("journal_warning", observation)

    def test_series_conflict_fixture_keeps_nonconflicting_context(self):
        series = "app/src/main/java/com/github/damontecres/wholphin/ui/detail/series/SeriesViewModel.kt"
        rtl = "app/src/main/java/com/github/damontecres/wholphin/ui/player/RtlControls.kt"
        self.commit(series, "base\n")
        self.anchor = self.g("rev-parse", "HEAD")
        for remote in self.remotes.values():
            self.g("push", str(remote), "HEAD:refs/heads/main")
        self.commit(series, "upstream duplicate search fix\n")
        self.commit(rtl, "upstream rtl\n")
        self.g("push", str(self.remotes["upstream"]), "HEAD:refs/heads/main")
        self.g("checkout", "--detach", self.anchor)
        self.commit(series, "downstream acquisition behavior\n")
        self.g("push", str(self.remotes["origin"]), "HEAD:refs/heads/main")
        git, observation = self.observe()
        self.assertEqual("semantic_conflict", observation["outcome"])
        self.assertEqual([series], observation["conflict_paths"])
        self.assertEqual("upstream rtl", git.text("show", observation["candidate_sha"] + ":" + rtl))
        self.assertFalse(git.ancestor(observation["upstream_sha"], observation["candidate_sha"]))

    def test_three_observations_reuse_one_issue_and_one_draft_pr(self):
        self.upstream(".github/workflows/future.yml", "review\n")
        first_git, first = self.observe(observed_at="2026-09-10T00:00:00+00:00",
                                       run_url="https://github.com/constbogdan/Wholphin/actions/runs/1")
        sync.publish(first_git, self.github, first, first["upstream_sha"], first["downstream_sha"])
        self.retain_pr(first_git, first, draft=True, body=self.github.created[0][1])
        for hour, run in ((6, 2), (12, 3)):
            retry, observation = self.observe(
                observed_at=f"2026-09-10T{hour:02}:00:00+00:00",
                run_url=f"https://github.com/constbogdan/Wholphin/actions/runs/{run}")
            self.assertEqual("existing_draft_pr", observation["outcome"])
            sync.publish(retry, self.github, observation,
                         observation["upstream_sha"], observation["downstream_sha"])
            self.assertFalse(retry.pushes)
        self.assertEqual(1, len(self.github.created))
        self.assertEqual(1, len(self.github.issue_records))
        journal = sync.journal_metadata(self.github.issue_records[0])
        self.assertEqual("2026-09-10T00:00:00+00:00", journal["firstObserved"])
        self.assertEqual("2026-09-10T12:00:00+00:00", journal["latestObserved"])
        self.assertEqual(3, journal["observationCount"])
        self.assertEqual("https://github.com/constbogdan/Wholphin/actions/runs/3", journal["latestRunUrl"])
        self.assertEqual("High risk · Low debt · 12h", self.github.issue_records[0]["title"])
        self.assertEqual(["debt: low", "risk: high"], self.github.issue_records[0]["labels"])
        self.assertIn("https://github.com/constbogdan/Wholphin/pull/123",
                      self.github.issue_records[0]["body"])

    def test_unrelated_downstream_movement_reuses_attention_episode(self):
        self.upstream(".github/workflows/future.yml", "review\n")
        first_git, first = self.observe(observed_at="2026-09-10T00:00:00+00:00")
        sync.publish(first_git, self.github, first, first["upstream_sha"], first["downstream_sha"])
        self.retain_pr(first_git, first, draft=True, body=self.github.created[0][1])
        first_episode, first_branch = first["episode_id"], first["branch"]

        self.g("checkout", "--detach", self.anchor)
        self.commit("unrelated.txt", "downstream movement\n")
        self.g("push", str(self.remotes["origin"]), "HEAD:refs/heads/main")
        retry, observation = self.observe(observed_at="2026-09-10T06:00:00+00:00")
        self.assertNotEqual(first_branch, observation["branch"])
        self.assertEqual(first_episode, observation["episode_id"])
        self.assertEqual("existing_draft_pr", observation["outcome"])
        self.assertEqual(first_branch, observation["existing_branch"])
        sync.publish(retry, self.github, observation,
                     observation["upstream_sha"], observation["downstream_sha"])
        self.assertEqual(1, len(self.github.created))
        self.assertEqual(1, len(self.github.issue_records))

    def test_new_upstream_same_area_updates_episode_evidence_without_duplicate(self):
        self.upstream(".github/workflows/future.yml", "review one\n")
        first_git, first = self.observe(observed_at="2026-09-10T00:00:00+00:00")
        sync.publish(first_git, self.github, first, first["upstream_sha"], first["downstream_sha"])
        self.retain_pr(first_git, first, draft=True, body=self.github.created[0][1])
        first_upstream = first["upstream_sha"]

        self.upstream(".github/workflows/future.yml", "review two\n")
        retry, observation = self.observe(observed_at="2026-09-10T06:00:00+00:00")
        self.assertNotEqual(first_upstream, observation["upstream_sha"])
        self.assertEqual(first["episode_id"], observation["episode_id"])
        self.assertEqual(2, observation["attention_change_count"])
        self.assertEqual("existing_draft_pr", observation["outcome"])
        sync.publish(retry, self.github, observation,
                     observation["upstream_sha"], observation["downstream_sha"])
        self.assertEqual(1, len(self.github.created))
        self.assertEqual(1, len(self.github.issue_records))
        self.assertIn(observation["upstream_sha"], self.github.issue_records[0]["body"])

    def test_risk_debt_age_and_escalation_are_independent_and_explainable(self):
        observation = {"review_paths": ["app/SeriesViewModel.kt"],
                       "attention_change_count": 1, "clean_path_count": 0,
                       "observed_at": "2026-09-01T00:00:00+00:00"}
        day_one = sync.priority_metrics(observation, "2026-09-01T00:00:00+00:00",
                                        "2026-09-02T00:00:00+00:00")
        day_seven = sync.priority_metrics(observation, "2026-09-01T00:00:00+00:00",
                                          "2026-09-08T00:00:00+00:00")
        self.assertEqual(("medium", "low", "1d", "None"),
                         (day_one["risk"], day_one["debt"], day_one["age"], day_one["escalation"]))
        self.assertEqual(("medium", "high", "7d", "Attention"),
                         (day_seven["risk"], day_seven["debt"], day_seven["age"], day_seven["escalation"]))
        churn = sync.priority_metrics({**observation, "attention_change_count": 5})
        self.assertEqual("high", churn["risk"])
        self.assertEqual("high", churn["debt"])
        sensitive = sync.priority_metrics({**observation, "review_paths": [".github/workflows/release.yml"]})
        self.assertEqual("high", sensitive["risk"])
        critical = sync.priority_metrics({**observation, "review_paths": [".github/actions/mosaic-sign-apk/action.yml"]})
        self.assertEqual(("critical", "Attention"), (critical["risk"], critical["escalation"]))

    def test_issue_title_labels_and_episode_identity_are_independent(self):
        base = {"ownership_policy_version": 1, "review_paths": ["source.kt"],
                "conflict_paths": [], "automation_changes": [{"path": "source.kt", "ownership": "REVIEW",
                "downstream_blob": "a" * 40}], "attention_change_count": 1}
        episode = sync.attention_episode(base)
        later = {**base, "priority": {"risk": "high", "debt": "high", "escalation": "Attention"}}
        labels = sync.issue_labels({"labels": [{"name": "risk: low"}, {"name": "debt: low"},
                                                {"name": "human-review"}]}, later, sync.MANAGED_LABELS)
        self.assertEqual(episode, sync.attention_episode(later))
        self.assertIn("risk: high", labels)
        self.assertIn("debt: high", labels)
        self.assertIn("attention", labels)
        self.assertIn("human-review", labels)
        self.assertFalse(any(label.startswith("age:") for label in labels))
        later["priority"] = {"risk": "medium", "debt": "low", "escalation": "None", "age": "6h"}
        self.assertEqual("Medium risk · Low debt · 6h", sync.priority_title(later["priority"]))

    def test_missing_labels_are_reported_without_creation_or_permission_broadening(self):
        observation = {"priority": {"risk": "high", "debt": "high", "escalation": "Attention"}}
        labels = sync.issue_labels({}, observation, {"risk: high"})
        self.assertEqual(["risk: high"], labels)
        self.assertEqual(["attention", "debt: high"], observation["missing_labels"])
        workflow = (Path(__file__).resolve().parent.parent / ".github/workflows/upstream-sync.yml").read_text()
        self.assertNotIn("permission-issues", workflow)
        self.assertNotIn("permissions: write-all", workflow)

    def test_quiet_issue_and_rich_summary_split_operator_navigation_from_provenance(self):
        path = "app/src/SeriesViewModel.kt"
        clean_path = "app/src/RtlControls.kt"
        observation = {"episode_id": "a" * 64, "outcome": "review_required",
                       "upstream_sha": "b" * 40,
                       "downstream_sha": "c" * 40, "pr_url": "https://github.com/constbogdan/Wholphin/pull/31",
                       "pr_number": 31, "run_url": "https://github.com/constbogdan/Wholphin/actions/runs/9",
                       "incoming_commits": [{"sha": "d" * 40, "subject": "Fix duplicates (#1946)",
                                             "url": "https://github.com/damontecres/Wholphin/commit/" + "d" * 40,
                                             "pull_request_numbers": ["1946"],
                                             "pull_request_urls": ["https://github.com/damontecres/Wholphin/pull/1946"]}],
                       "review_paths": [path], "conflict_paths": [path], "clean_path_count": 1,
                       "automation_changes": [{"path": path, "new_blob": "e" * 40,
                                                "downstream_blob": "f" * 40, "ownership": "REVIEW",
                                                "upstream_url": "https://github.com/damontecres/Wholphin/blob/" + "b" * 40 + "/" + path,
                                                "downstream_url": "https://github.com/constbogdan/Wholphin/blob/" + "c" * 40 + "/" + path},
                                               {"path": clean_path, "new_blob": "1" * 40,
                                                "downstream_blob": None, "ownership": "FOLLOW"}],
                       "journal": {"firstObserved": "2026-09-10T00:00:00+00:00",
                                   "latestObserved": "2026-09-10T06:00:00+00:00",
                                   "observationCount": 2, "latestRunUrl": "https://example/run"},
                       "priority": {"risk": "medium", "debt": "low", "age": "6h",
                                    "escalation": "None"}}
        body = sync.issue_body(observation)
        self.assertIn("Draft PR: [#31](https://github.com/constbogdan/Wholphin/pull/31)", body)
        self.assertIn("PR 1946", body)
        self.assertIn("<code>ddddddd</code>", body)
        self.assertIn("<code>SeriesViewModel.kt</code>", body)
        self.assertNotIn("github.com/damontecres", body)
        self.assertNotIn("damontecres/Wholphin#", body)
        self.assertIn("1 additional file integrates cleanly.", body)
        self.assertNotIn(clean_path, body)
        self.assertNotIn("existing_pr_url: not available", body)
        self.assertIn("Latest observation:", body)
        self.assertIn(clean_path, json.dumps(observation))

        summary = sync.upstream_summary(observation)
        self.assertIn("[PR 1946](https://github.com/damontecres/Wholphin/pull/1946)", summary)
        self.assertIn("https://github.com/damontecres/Wholphin/commit/" + "d" * 40, summary)
        self.assertIn("https://github.com/damontecres/Wholphin/blob/" + "b" * 40 + "/" + path, summary)
        self.assertIn("https://github.com/constbogdan/Wholphin/blob/" + "c" * 40 + "/" + path, summary)

    def test_clean_follow_journal_closes_after_pr_handoff_and_remains_history(self):
        self.upstream("app/example.kt", "clean\n")
        git, observation = self.observe(observed_at="2026-09-10T00:00:00+00:00")
        sync.publish(git, self.github, observation,
                     observation["upstream_sha"], observation["downstream_sha"])
        self.assertEqual("pr_created", observation["outcome"])
        self.assertEqual(1, len(self.github.issue_records))
        self.assertEqual("closed", self.github.issue_records[0]["state"])
        self.assertIn(observation["pr_url"], self.github.issue_records[0]["body"])
        self.assertNotIn("github.com/damontecres", self.github.issue_records[0]["body"])
        self.assertNotIn("github.com/damontecres", self.github.created[0][1])
        self.assertNotIn(observation["upstream_sha"][:12], self.github.issue_records[0]["title"])
        self.assertNotIn(observation["upstream_sha"][:12], self.github.created[0][3])

    def test_machine_artifact_retains_exact_upstream_navigation_urls(self):
        self.upstream(".github/workflows/future.yml", "review\n")
        _, observation = self.observe()
        commit = observation["incoming_commits"][0]
        change = observation["automation_changes"][0]
        self.assertEqual("https://github.com/damontecres/Wholphin/commit/" + commit["sha"],
                         commit["url"])
        self.assertEqual("https://github.com/damontecres/Wholphin/blob/" +
                         observation["upstream_sha"] + "/.github/workflows/future.yml",
                         change["upstream_url"])
        self.assertIn(commit["url"], json.dumps(observation))
        self.assertIn(change["upstream_url"], json.dumps(observation))

    def test_body_escapes_external_markup_and_mentions(self):
        unsafe = "line-one#1946@team\n## injected"
        subject = ("Fixes damontecres/Wholphin#1946 and #1947 "
                   "https://github.com/damontecres/Wholphin/pull/1948 <script>@everyone</script>")
        body = sync.description({"incoming_commits": [{"sha": "a" * 40, "subject": subject}],
                                 "review_paths": [unsafe],
                                 "automation_changes": [{"path": unsafe, "new_blob": "a" * 40,
                                                         "downstream_blob": None}],
                                 "upstream_sha": "a" * 40})
        self.assertNotIn("<script>", body)
        self.assertNotIn("@everyone", body)
        self.assertNotIn("\n## injected", body)
        self.assertNotIn("github.com/damontecres", body)
        self.assertNotIn("damontecres/Wholphin#", body)
        self.assertNotIn("#1947", body)
        for number in ("1946", "1947", "1948"):
            self.assertIn("PR " + number, body)
        self.assertIn("line-one#1946&#64;team\\n## injected", body)
        title = sync.candidate_title({"review_paths": ["unsafe#1946@team.yml"]}, True)
        self.assertNotIn("#1946", title)
        self.assertNotIn("@team", title)

        summary = sync.upstream_summary({"outcome": "review_required",
            "ownership_counts": {"FOLLOW": 0, "REVIEW": 1, "DOWNSTREAM-OWNED": 0},
            "automation_changes": [{"ownership": "REVIEW", "path": "`\n## injected",
                                     "reason": "<review>@team"}]})
        self.assertNotIn("\n## injected", summary)
        self.assertNotIn("<review>", summary)
        self.assertIn("&lt;review&gt;&#64;team", summary)

    def test_blocked_issue_deduplication_including_closed_issue(self):
        github = sync.GitHub()
        created = []
        def create(endpoint, payload=None, **kwargs):
            if payload is None:
                return {'has_issues': True}
            if endpoint.endswith("/issues"):
                created.append({**payload, "number": 5, "state": "open",
                                "html_url": "https://github.com/constbogdan/Wholphin/issues/5"})
            else:
                created[0].update(payload)
            return created[-1]
        o = {"upstream_sha": "a" * 40, "downstream_sha": "b" * 40,
             "episode_id": "c" * 64, "observed_at": "2026-09-10T00:00:00+00:00",
             "review_paths": ["source.kt"], "automation_changes": [], "outcome": "blocked"}
        with patch.object(github, "issues", side_effect=lambda: created), \
                patch.object(github, "labels", return_value=set(sync.MANAGED_LABELS)), \
                patch.object(github, "api", side_effect=create):
            first = github.blocked_issue(o)
            created[0]["state"] = "closed"
            self.assertEqual(first, github.blocked_issue(dict(o)))
            self.assertEqual(len(created), 1)

    def test_new_observation_closes_prior_open_journal_as_superseded(self):
        github = sync.GitHub()
        prior = {"number": 4, "state": "open", "title": "Medium risk · Low debt · 1h",
                 "html_url": "https://github.com/constbogdan/Wholphin/issues/4",
                 "body": "<!-- wholphin-upstream-episode:" + "d" * 64 + " -->\nold", "labels": []}
        calls = []
        def api(endpoint, payload=None, **kwargs):
            calls.append((endpoint, payload, kwargs))
            if payload is None:
                return {"has_issues": True}
            if endpoint.endswith("/issues"):
                return {"number": 5, "state": "open", "title": payload["title"], "labels": payload["labels"],
                        "html_url": "https://github.com/constbogdan/Wholphin/issues/5", "body": payload["body"]}
            return prior
        observation = {"upstream_sha": "a" * 40, "downstream_sha": "b" * 40,
                       "ownership_policy_version": 1, "episode_id": "e" * 64,
                       "observed_at": "2026-09-10T00:00:00+00:00", "review_paths": ["source.kt"],
                       "automation_changes": [], "outcome": "review_required"}
        with patch.object(github, "issues", return_value=[prior]), \
                patch.object(github, "labels", return_value=set(sync.MANAGED_LABELS)), \
                patch.object(github, "api", side_effect=api):
            created = github.journal_issue(observation)
        self.assertEqual(5, created["number"])
        self.assertTrue(any(payload and payload.get("state") == "closed" and kwargs.get("method") == "PATCH"
                            for _, payload, kwargs in calls))

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

    def test_long_opaque_app_token_is_transport_only_and_redacted(self):
        token = "ghs_future." + ("opaque-Part_with-punctuation." * 20)
        github = sync.GitHub()
        with patch.dict(os.environ, {"GH_TOKEN": "read-only", "SYNC_PUBLISH_TOKEN": token}), \
                patch.object(sync, "command") as run:
            run.return_value.stdout = '{"html_url":"https://github.com/constbogdan/Wholphin/pull/1"}'
            github.create_pr(sync.branch_name("a" * 40, "b" * 40), "fixture")
            self.assertEqual(run.call_args.kwargs["env"]["GH_TOKEN"], token)
            self.assertNotIn("SYNC_PUBLISH_TOKEN", run.call_args.kwargs["env"])
            self.assertNotIn(token, " ".join(run.call_args.args[0]))
        failed = subprocess.CompletedProcess(["gh", "api"], 1, "", token)
        with patch.object(sync.subprocess, "run", return_value=failed), self.assertRaises(sync.Blocked) as error:
            sync.command(["gh", "api"], env={"GH_TOKEN": token})
        self.assertNotIn(token, str(error.exception))

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

    def test_failed_cli_records_durable_issue_and_publication_error_outcome(self):
        output = self.root / "blocked.json"
        runtime = {"GITHUB_ACTIONS": "true", "GITHUB_REPOSITORY": sync.ORIGIN,
                   "GITHUB_REF": "refs/heads/main", "GITHUB_EVENT_NAME": "workflow_dispatch",
                   "RUNNER_TEMP": str(self.root), "GITHUB_STEP_SUMMARY": str(self.root / "summary.md"),
                   "GITHUB_OUTPUT": str(self.root / "outputs")}
        def conflict(git, gh, observation):
            observation.update(upstream_sha="a" * 40, downstream_sha="b" * 40,
                               conflict_paths=["source.kt"], textual_conflicts=True)
            raise sync.OperationError("permission_denied: fixture publication failed.")
        with patch.dict(os.environ, runtime), patch("sys.argv", ["hosted_upstream", "--publish", "--output", str(output)]), patch.object(sync, "inspect", side_effect=conflict), patch.object(sync.GitHub, "blocked_issue", return_value="https://github.com/constbogdan/Wholphin/issues/1") as issue:
            self.assertEqual(sync.main(), 1)
        self.assertTrue(issue.called)
        result = json.loads(output.read_text())
        self.assertTrue(result["textual_conflicts"])
        self.assertEqual(result["conflict_paths"], ["source.kt"])
        self.assertIn("blocked_issue_url", result)
        self.assertIn("outcome=publication_error", (self.root / "outputs").read_text())

    def test_upstream_contained_after_accepted_merge_no_new_pr(self):
        self.upstream()
        git, o = self.observe()
        git.run("push", str(self.remotes["origin"]), o["candidate_sha"] + ":refs/heads/main")
        _, result = self.observe()
        self.assertEqual(result["outcome"], "no_delta")


if __name__ == "__main__":
    unittest.main()
