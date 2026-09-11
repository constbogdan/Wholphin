import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name("resolve_upstream.py")
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("resolve_upstream", MODULE_PATH)
resolve = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = resolve
SPEC.loader.exec_module(resolve)


EPISODE = "e" * 64
UPSTREAM = "a" * 40
DOWNSTREAM = "b" * 40
CANDIDATE = "c" * 40
BRANCH = f"chore/sync-upstream-{UPSTREAM}-{DOWNSTREAM}"


class FakeRunner:
    def __init__(self, *, dirty=False, origin="https://github.com/constbogdan/Wholphin.git",
                 state="open", candidate=True, local=False, local_sha=CANDIDATE,
                 tracking=None, artifact=True, ci_bucket="fail", current_branch="chore/test",
                 upstream_rewritten=False):
        self.dirty = dirty
        self.origin = origin
        self.state = state
        self.candidate = candidate
        self.local = local
        self.local_sha = local_sha
        self.tracking = tracking
        self.artifact = artifact
        self.ci_bucket = ci_bucket
        self.current_branch = current_branch
        self.upstream_rewritten = upstream_rewritten
        self.main_sha = DOWNSTREAM
        self.compare_map = {}
        self.calls = []
        self.root = None

    def pr(self):
        body = f"<!-- wholphin-upstream-episode:{EPISODE} -->" if self.candidate else "ordinary"
        return {"number": 33, "state": self.state, "draft": True, "body": body,
                "html_url": "https://github.com/constbogdan/Wholphin/pull/33",
                "head": {"ref": BRANCH if self.candidate else "feature/ordinary", "sha": CANDIDATE,
                         "repo": {"full_name": resolve.REPOSITORY}},
                "base": {"ref": "main", "repo": {"full_name": resolve.REPOSITORY}}}

    def issue(self):
        record = {"schemaVersion": 1, "episodeId": EPISODE,
                  "firstObserved": "2026-09-10T00:00:00+00:00",
                  "latestObserved": "2026-09-10T01:00:00+00:00",
                  "observationCount": 2,
                  "latestRunUrl": "https://github.com/constbogdan/Wholphin/actions/runs/456"}
        body = ("Risk: **Medium**\nIntegration debt: **High**\nAge: **1h**\n"
                "Escalation: **Attention**\n"
                f"<!-- wholphin-upstream-episode:{EPISODE} -->\n"
                f"<!-- wholphin-upstream-journal:{json.dumps(record, separators=(',', ':'))} -->")
        return {"number": 32, "state": "open", "body": body,
                "html_url": "https://github.com/constbogdan/Wholphin/issues/32"}

    def observation(self):
        return {"schema_version": 2, "episode_id": EPISODE,
                "downstream_repo": resolve.REPOSITORY, "branch": BRANCH,
                "run_id": "456", "run_attempt": "1", "candidate_sha": CANDIDATE,
                "upstream_sha": UPSTREAM, "downstream_sha": DOWNSTREAM,
                "candidate_tree": "f" * 40, "ownership_policy_version": 1,
                "comparison_baseline": "9" * 40, "classification_range_count": 1,
                "automation_changes": [{"path": "app/SeriesViewModel.kt", "ownership": "REVIEW"}],
                "review_paths": ["app/SeriesViewModel.kt", "app/ContextMenu.kt"],
                "conflict_paths": ["app/SeriesViewModel.kt"], "clean_path_count": 10,
                "priority": {"risk": "medium", "debt": "high", "age": "1h",
                             "escalation": "Attention"},
                "incoming_commits": [{"sha": "d" * 40,
                                      "subject": "Fix duplicates (#1946)",
                                      "url": "https://github.com/damontecres/Wholphin/commit/" + "d" * 40}]}

    def run(self, args, *, cwd, check=True):
        self.calls.append(list(args))
        self.root = Path(cwd)
        result = self._result(args)
        if check and result.returncode:
            raise resolve.Refusal(result.stderr or "fixture failure")
        return result

    def _result(self, args):
        joined = " ".join(args)
        if args[:3] == ["git", "rev-parse", "--show-toplevel"]:
            return resolve.Result(str(self.root), "", 0)
        if args[:4] == ["git", "remote", "get-url", "origin"]:
            return resolve.Result(self.origin + "\n", "", 0)
        if args[:4] == ["git", "remote", "get-url", "upstream"]:
            return resolve.Result("https://github.com/damontecres/Wholphin.git\n", "", 0)
        if args[:3] == ["git", "status", "--porcelain=v1"]:
            return resolve.Result("?? local.txt\n" if self.dirty else "", "", 0)
        if args[:3] == ["git", "branch", "--show-current"]:
            return resolve.Result(self.current_branch + "\n", "", 0)
        if args[:3] == ["gh", "auth", "status"]:
            return resolve.Result("authenticated", "", 0)
        if args[:3] == ["gh", "api", f"repos/{resolve.REPOSITORY}/pulls/33"]:
            return resolve.Result(json.dumps(self.pr()), "", 0)
        if args[:3] == ["gh", "api", "--paginate"]:
            return resolve.Result(json.dumps([[self.pr()]] if "pulls?" in args[-1] else [[self.issue()]]), "", 0)
        if args[:3] == ["gh", "api", f"repos/{resolve.REPOSITORY}/git/ref/heads/main"]:
            return resolve.Result(json.dumps({"object": {"sha": self.main_sha}}), "", 0)
        if args[:2] == ["gh", "api"] and "/compare/" in args[2]:
            comparison = args[2].split("/compare/", 1)[1]
            return resolve.Result(json.dumps({"status": self.compare_map.get(comparison, "diverged")}), "", 0)
        if args[:3] == ["gh", "api", f"repos/{resolve.REPOSITORY}/actions/runs/456"]:
            return resolve.Result(json.dumps({"run_attempt": 1}), "", 0)
        if args[:3] == ["gh", "run", "download"]:
            if not self.artifact:
                return resolve.Result("", "expired", 1)
            destination = Path(args[args.index("--dir") + 1])
            (destination / "observation.json").write_text(json.dumps(self.observation()), encoding="utf-8")
            return resolve.Result("", "", 0)
        if args[:3] == ["gh", "pr", "checks"]:
            row = {"name": "Full validation", "workflow": "CI", "bucket": self.ci_bucket,
                   "state": "FAILURE" if self.ci_bucket == "fail" else "SUCCESS",
                   "link": "https://github.com/constbogdan/Wholphin/actions/runs/789"}
            return resolve.Result(json.dumps([row]), "", 1 if self.ci_bucket == "fail" else 0)
        if args[:3] == ["git", "check-ref-format", "--branch"]:
            return resolve.Result(BRANCH, "", 0)
        if args[:2] == ["git", "fetch"]:
            return resolve.Result("", "", 0)
        if args[:3] == ["git", "rev-parse", f"refs/remotes/origin/{BRANCH}"]:
            return resolve.Result(CANDIDATE + "\n", "", 0)
        if args[:4] == ["git", "show-ref", "--verify", "--quiet"]:
            return resolve.Result("", "", 0 if self.local else 1)
        if args[:3] == ["git", "rev-parse", f"refs/heads/{BRANCH}"]:
            return resolve.Result(self.local_sha + "\n", "", 0)
        if args[:2] == ["git", "for-each-ref"]:
            return resolve.Result((self.tracking or "") + "\n", "", 0)
        if args[:2] in (["git", "switch"], ["git", "branch"]):
            return resolve.Result("", "", 0)
        if args[:5] == ["git", "show", "-s", "--format=%P", CANDIDATE]:
            return resolve.Result(DOWNSTREAM + "\n", "", 0)
        if args[:3] == ["git", "rev-parse", CANDIDATE + "^{tree}"]:
            return resolve.Result("f" * 40 + "\n", "", 0)
        if args[:3] == ["git", "show", CANDIDATE + ":.upstream-sync/blocked-context.json"]:
            context = {"schemaVersion": 1, "upstream": UPSTREAM, "downstream": DOWNSTREAM,
                       "policyVersion": 1, "conflicts": ["app/SeriesViewModel.kt"]}
            return resolve.Result(json.dumps(context), "", 0)
        if args[:3] == ["git", "rev-parse", "HEAD"]:
            return resolve.Result(CANDIDATE + "\n", "", 0)
        if args[:2] == ["git", "cat-file"]:
            return resolve.Result("", "", 0)
        if args[:3] == ["git", "merge-base", "--is-ancestor"]:
            return resolve.Result("", "rewritten" if self.upstream_rewritten else "",
                                  1 if self.upstream_rewritten else 0)
        if args[:2] == ["git", "merge"]:
            return resolve.Result("", "fixture conflict", 1)
        if args[:3] == ["git", "rev-parse", "MERGE_HEAD"]:
            return resolve.Result(UPSTREAM + "\n", "", 0)
        if args[:2] == ["git", "rm"]:
            return resolve.Result("", "", 0)
        raise AssertionError(f"Unexpected fixture command: {joined}")


class ResolveUpstreamTests(unittest.TestCase):
    def root(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / ".gitignore").write_text(".logs/\n", encoding="utf-8")
        return root

    def execute(self, runner):
        root = self.root()
        with patch.object(resolve.shutil, "which", return_value="fixture"):
            summary, output = resolve.execute(33, root, runner)
        return root, summary, output

    def candidate(self, number, path, upstream, downstream=DOWNSTREAM, head=None):
        episode = f"{number:064x}"
        branch = f"chore/sync-upstream-{upstream}-{downstream}"
        head = head or f"{number:040x}"
        pr = {"number": number, "state": "open", "draft": True,
              "body": f"<!-- wholphin-upstream-episode:{episode} -->",
              "head": {"ref": branch, "sha": head, "repo": {"full_name": resolve.REPOSITORY}},
              "base": {"ref": "main", "repo": {"full_name": resolve.REPOSITORY}}}
        issue = {"number": number - 1, "state": "open", "body":
                 f"Risk: **Medium**\nIntegration debt: **Low**\nAge: **1h**\nEscalation: **None**\n"
                 f"<!-- wholphin-upstream-episode:{episode} -->"}
        observation = {"episode_id": episode, "upstream_sha": upstream,
                       "downstream_sha": downstream, "candidate_sha": head,
                       "review_paths": [path], "conflict_paths": [path], "clean_path_count": 1}
        return resolve.Candidate(pr, issue, observation,
                                 {"status": "FAILED", "name": "CI / Full validation", "url": "run"},
                                 resolve.priority(issue, observation))

    def test_native_conflict_resolution_produces_exact_two_parent_reviewed_tree(self):
        root = self.root()
        env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")

        def git(*args, check=True):
            result = subprocess.run(
                ["git", "-c", "core.autocrlf=false", *args], cwd=root, env=env,
                capture_output=True, text=True, encoding="utf-8",
            )
            if check:
                self.assertEqual(0, result.returncode, result.stderr)
            return result

        git("init", "-b", "main")
        git("config", "user.name", "Fixture")
        git("config", "user.email", "fixture@example.invalid")
        (root / "source.kt").write_text("base\n", encoding="utf-8", newline="\n")
        git("add", "source.kt")
        git("commit", "-m", "Base")
        downstream = git("rev-parse", "HEAD").stdout.strip()
        (root / "source.kt").write_text("upstream\n", encoding="utf-8", newline="\n")
        git("commit", "-am", "Upstream")
        upstream = git("rev-parse", "HEAD").stdout.strip()
        upstream_bare = root.parent / (root.name + "-upstream.git")
        self.addCleanup(lambda: shutil.rmtree(upstream_bare, ignore_errors=True))
        subprocess.run(["git", "init", "--bare", str(upstream_bare)], check=True,
                       capture_output=True, text=True)
        git("push", str(upstream_bare), f"{upstream}:refs/heads/main")
        git("checkout", "--detach", downstream)
        context = {"schemaVersion": 1, "upstream": upstream, "downstream": downstream,
                   "policyVersion": 1, "conflicts": ["source.kt"]}
        context_path = root / ".upstream-sync" / "blocked-context.json"
        context_path.parent.mkdir()
        context_path.write_text(json.dumps(context), encoding="utf-8", newline="\n")
        git("add", ".upstream-sync/blocked-context.json")
        git("commit", "-m", "Blocked workspace")
        candidate_sha = git("rev-parse", "HEAD").stdout.strip()
        branch = f"chore/sync-upstream-{upstream}-{downstream}"
        git("switch", "-c", branch)
        git("remote", "add", "upstream", str(upstream_bare))
        observation = {"candidate_sha": candidate_sha, "candidate_tree": git(
            "rev-parse", "HEAD^{tree}").stdout.strip(), "upstream_sha": upstream,
            "downstream_sha": downstream, "ownership_policy_version": 1,
            "conflict_paths": ["source.kt"]}
        pr = {"number": 33, "head": {"ref": branch, "sha": candidate_sha}}
        candidate = resolve.Candidate(pr, {}, observation, {}, {})
        runner = resolve.Runner()

        resolve.begin_native_resolution(runner, root, candidate)
        self.assertEqual(upstream, git("rev-parse", "MERGE_HEAD").stdout.strip())
        (root / "source.kt").write_text(
            "<<<<<<< downstream\nleft\n=======\nright\n>>>>>>> upstream\n",
            encoding="utf-8", newline="\n",
        )
        git("add", "source.kt")
        with self.assertRaisesRegex(resolve.Refusal, "conflict markers"):
            resolve.assert_resolved_native_merge(runner, root, candidate)
        (root / "source.kt").write_text(
            "resolved downstream + upstream\n", encoding="utf-8", newline="\n"
        )
        commit, reviewed_tree = resolve.commit_native_resolution(
            runner, root, candidate, ["source.kt", ".upstream-sync/blocked-context.json"]
        )
        self.assertEqual(
            [candidate_sha, upstream],
            git("show", "-s", "--format=%P", commit).stdout.split(),
        )
        self.assertEqual(reviewed_tree, git("rev-parse", commit + "^{tree}").stdout.strip())
        self.assertEqual(0, git("merge-base", "--is-ancestor", upstream, commit, check=False).returncode)
        self.assertNotEqual(0, git("cat-file", "-e", commit + ":.upstream-sync/blocked-context.json",
                                  check=False).returncode)
        self.assertEqual("resolved downstream + upstream", git("show", commit + ":source.kt").stdout.strip())

    def test_upstream_rewrite_and_incomplete_context_fail_before_merge(self):
        with self.assertRaisesRegex(resolve.Refusal, "no longer belongs"):
            self.execute(FakeRunner(upstream_rewritten=True))

        class MismatchedPolicy(FakeRunner):
            def observation(self):
                value = super().observation()
                value["ownership_policy_version"] = 2
                return value

        with self.assertRaisesRegex(resolve.Refusal, "context does not match"):
            self.execute(MismatchedPolicy())

    def run_wrapper(self, arguments, input_text=""):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        scripts = root / "scripts"
        scripts.mkdir()
        wrapper = MODULE_PATH.with_name("resolve-upstream.ps1")
        (scripts / wrapper.name).write_text(wrapper.read_text(encoding="utf-8"), encoding="utf-8")
        capture = root / "python-args.txt"
        (scripts / "resolve_upstream.py").write_text(
            "import os, pathlib, sys\n"
            "pathlib.Path(os.environ['RESOLVE_CAPTURE']).write_text(' '.join(sys.argv[1:]))\n",
            encoding="utf-8",
        )
        environment = os.environ.copy()
        environment["RESOLVE_CAPTURE"] = str(capture)
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if not shell:
            self.skipTest("PowerShell is unavailable")
        completed = subprocess.run(
            [shell, "-NoProfile", "-ExecutionPolicy", "Bypass",
             "-File", str(scripts / wrapper.name), *arguments],
            cwd=root, input=input_text, text=True, capture_output=True, env=environment, check=False)
        return completed, capture.read_text(encoding="utf-8").strip() if capture.exists() else ""

    def test_explicit_pr_is_the_only_direct_operator_input(self):
        wrapper = MODULE_PATH.with_name("resolve-upstream.ps1").read_text(encoding="utf-8")
        self.assertRegex(wrapper, r"\[string\]\$Pr")
        self.assertNotIn("$Branch", wrapper)
        completed, captured = self.run_wrapper(["-Pr", "33"])
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertRegex(captured, r"--pr 33$")

    def test_interactive_invocation_reprompts_until_positive_integer(self):
        completed, captured = self.run_wrapper([])
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertNotIn("--pr", captured)

    def test_invalid_explicit_pr_fails_clearly(self):
        completed, captured = self.run_wrapper(["-Pr", "0"])
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("-Pr must be a positive integer", completed.stderr)
        self.assertEqual("", captured)

    def test_wrong_repository_refuses_before_checkout(self):
        runner = FakeRunner(origin="https://github.com/example/wrong.git")
        with self.assertRaisesRegex(resolve.Refusal, "Expected origin"):
            self.execute(runner)
        self.assertFalse(any(call[:2] == ["git", "switch"] for call in runner.calls))

    def test_dirty_tree_including_untracked_refuses_before_github_query(self):
        runner = FakeRunner(dirty=True)
        with self.assertRaisesRegex(resolve.Refusal, "not clean"):
            self.execute(runner)
        self.assertFalse(any("pulls/33" in " ".join(call) for call in runner.calls))

    def test_pr_not_found_surfaces_github_error(self):
        class Missing(FakeRunner):
            def _result(self, args):
                if args[:3] == ["gh", "api", f"repos/{resolve.REPOSITORY}/pulls/33"]:
                    return resolve.Result("", "HTTP 404: Not Found", 1)
                return super()._result(args)
        with self.assertRaisesRegex(resolve.Refusal, "HTTP 404"):
            self.execute(Missing())

    def test_non_candidate_and_closed_pr_refuse(self):
        for runner, message in ((FakeRunner(candidate=False), "not a durable I06"),
                                (FakeRunner(state="closed"), "closed")):
            with self.subTest(message=message), self.assertRaisesRegex(resolve.Refusal, message):
                self.execute(runner)

    def test_fresh_checkout_uses_exact_pr_branch_and_creates_prompt(self):
        runner = FakeRunner()
        root, summary, output = self.execute(runner)
        self.assertIn(["git", "fetch", "--no-tags", "origin",
                       f"refs/heads/{BRANCH}:refs/remotes/origin/{BRANCH}"], runner.calls)
        self.assertIn(["git", "switch", "--track", "-c", BRANCH, f"origin/{BRANCH}"], runner.calls)
        self.assertTrue(output.is_file())
        self.assertEqual(output, root / ".logs/upstream-resolution/pr-33/codex-prompt.md")
        self.assertIn("PR:          #33", summary)
        self.assertIn("Issue:       #32", summary)
        self.assertIn("State:       Draft - attention required", summary)
        self.assertIn("Risk:        Medium", summary)
        self.assertIn("Debt:        High", summary)
        self.assertIn("CI: FAILED", summary)
        self.assertIn(
            "Read `.logs/upstream-resolution/pr-33/codex-prompt.md` and carry out the instructions exactly.",
            summary,
        )
        self.assertNotIn("# Resolve Upstream Sync PR #33", summary)

    def test_existing_exact_tracking_branch_is_safe(self):
        runner = FakeRunner(local=True, tracking=f"origin/{BRANCH}")
        self.execute(runner)
        self.assertIn(["git", "switch", BRANCH], runner.calls)
        self.assertFalse(any("--track" in call for call in runner.calls))

    def test_existing_local_divergence_refuses_without_switch(self):
        runner = FakeRunner(local=True, local_sha="f" * 40)
        with self.assertRaisesRegex(resolve.Refusal, "differs from the PR head"):
            self.execute(runner)
        self.assertFalse(any(call[:2] == ["git", "switch"] for call in runner.calls))

    def test_issue_evidence_attention_ci_and_actual_values_reach_prompt(self):
        runner = FakeRunner()
        _, _, output = self.execute(runner)
        text = output.read_text(encoding="utf-8")
        self.assertIn("Linked journal: #32", text)
        self.assertIn("Candidate state: Draft - attention required", text)
        self.assertIn("Risk: Medium", text)
        self.assertIn("Integration debt: High", text)
        self.assertIn("app/SeriesViewModel.kt", text)
        self.assertIn("Fix duplicates (#1946)", text)
        self.assertIn("FAILED - CI / Full validation", text)
        self.assertIn("actions/runs/789", text)
        self.assertIn(UPSTREAM, text)
        self.assertIn(DOWNSTREAM, text)
        self.assertIn("exact meaningful JVM test filter values", text)
        self.assertIn("identify the test that must be added", text)

    def test_mismatched_machine_evidence_refuses(self):
        class Mismatched(FakeRunner):
            def observation(self):
                value = super().observation()
                value["candidate_sha"] = "9" * 40
                return value
        with self.assertRaisesRegex(resolve.Refusal, "machine-evidence candidate SHA"):
            self.execute(Mismatched())

    def test_human_edited_draft_head_is_accepted_only_as_proven_descendant(self):
        runner = FakeRunner()
        pr = runner.pr()
        pr["head"]["sha"] = "8" * 40
        observation = runner.observation()
        runner.compare_map[f"{CANDIDATE}...{'8' * 40}"] = "ahead"
        resolve.validate_observation(observation, pr, EPISODE, runner=runner, root=self.root())

    def test_closed_linked_journal_refuses(self):
        class ClosedJournal(FakeRunner):
            def issue(self):
                value = super().issue()
                value["state"] = "closed"
                return value
        with self.assertRaisesRegex(resolve.Refusal, "journal Issue #32 is not open"):
            self.execute(ClosedJournal())

    def test_ci_success_renders(self):
        _, summary, _ = self.execute(FakeRunner(ci_bucket="pass"))
        self.assertIn("CI: PASSED", summary)

    def test_expired_artifact_without_complete_native_evidence_fails_closed(self):
        runner = FakeRunner(artifact=False)
        with self.assertRaisesRegex(resolve.Refusal, "Machine evidence is incomplete"):
            self.execute(runner)

    def test_logs_are_ignored_and_no_mutating_github_or_destructive_git_commands_exist(self):
        root, _, _ = self.execute(FakeRunner())
        self.assertIn(".logs/", (root / ".gitignore").read_text(encoding="utf-8"))
        source = MODULE_PATH.read_text(encoding="utf-8")
        for forbidden in ("gh pr comment", "gh issue", "git reset", "git stash", "git clean",
                          "--force", "git push", "git pull"):
            self.assertNotIn(forbidden, source)

    def test_vscode_interactive_task_preserves_existing_tasks(self):
        tasks = json.loads((MODULE_PATH.parent.parent / ".vscode/tasks.json").read_text(encoding="utf-8"))
        commands = {task["label"]: task["command"] for task in tasks["tasks"]}
        self.assertEqual(r".\scripts\resolve-upstream.ps1", commands["Mosaic: Resolve Upstream"])
        self.assertEqual(r".\scripts\prepare-pr.ps1", commands["Mosaic: Prepare PR"])
        for level in ("Fast", "Standard", "Full"):
            self.assertEqual(fr".\scripts\validate-local.ps1 -Level {level}",
                             commands[f"Mosaic: Validate {level}"])

    def test_selector_handles_zero_one_multiple_and_cancellation(self):
        with patch("builtins.print") as output:
            self.assertIsNone(resolve.select_candidate([], None, lambda _: ""))
            self.assertIn("No open", output.call_args.args[0])
        one = self.candidate(33, "app/src/main/SeriesViewModel.kt", "1" * 40)
        one.state = "Ready for resolution"
        self.assertIs(one, resolve.select_candidate([one], None, lambda _: ""))
        two = self.candidate(37, "app/src/main/Other.kt", "2" * 40)
        two.state = "Independent"
        self.assertIsNone(resolve.select_candidate([one, two], None, lambda _: "q"))
        self.assertIs(two, resolve.select_candidate([one, two], None, lambda _: "2"))

    def test_independent_candidates_remain_parallel(self):
        runner = FakeRunner()
        first = self.candidate(33, "app/src/main/SeriesViewModel.kt", "1" * 40)
        second = self.candidate(37, "app/src/main/ContextMenu.kt", "2" * 40)
        result = resolve.classify_dependencies(runner, self.root(), [first, second])
        self.assertEqual(["Independent", "Independent"], [candidate.state for candidate in result])

    def test_exact_attention_overlap_uses_upstream_ancestry_order(self):
        runner = FakeRunner()
        older, newer = "1" * 40, "2" * 40
        runner.compare_map[f"{older}...{newer}"] = "ahead"
        first = self.candidate(33, "app/src/main/SeriesViewModel.kt", older)
        second = self.candidate(37, "app/src/main/SeriesViewModel.kt", newer)
        result = resolve.classify_dependencies(runner, self.root(), [first, second])
        self.assertEqual("Ready for resolution", result[0].state)
        self.assertEqual("Waiting on PR #33", result[1].state)
        self.assertEqual(("app/src/main/SeriesViewModel.kt",), result[1].overlaps)

    def test_ambiguous_overlap_refuses_selection(self):
        runner = FakeRunner()
        first = self.candidate(33, "app/src/main/SeriesViewModel.kt", "1" * 40)
        second = self.candidate(37, "app/src/main/SeriesViewModel.kt", "2" * 40)
        result = resolve.classify_dependencies(runner, self.root(), [first, second])
        self.assertEqual("Dependency ambiguous", result[0].state)
        with self.assertRaisesRegex(resolve.Refusal, "refusing to guess"):
            resolve.select_candidate(result, 33)

    def test_predecessor_merge_supersedes_it_and_requires_fresh_successor_observation(self):
        runner = FakeRunner()
        merged_head, current = "3" * 40, "4" * 40
        runner.main_sha = current
        runner.compare_map[f"{merged_head}...{current}"] = "ahead"
        first = self.candidate(33, "app/src/main/SeriesViewModel.kt", "1" * 40,
                               downstream=DOWNSTREAM, head=merged_head)
        second = self.candidate(37, "app/src/main/SeriesViewModel.kt", "2" * 40,
                                downstream=current)
        result = resolve.classify_dependencies(runner, self.root(), [first, second])
        self.assertEqual("Superseded", result[0].state)
        self.assertEqual("Ready for resolution", result[1].state)

    def test_stale_downstream_baseline_is_ambiguous_until_reobserved(self):
        runner = FakeRunner()
        runner.main_sha = "4" * 40
        candidate = self.candidate(33, "app/src/main/SeriesViewModel.kt", "1" * 40)
        self.assertEqual("Dependency ambiguous",
                         resolve.classify_dependencies(runner, self.root(), [candidate])[0].state)

    def test_filter_derivation_uses_i03_mapping_and_changed_tests(self):
        filters = resolve.derive_filters([
            "app/src/main/java/com/github/damontecres/wholphin/ui/detail/series/SeriesViewModel.kt",
            "app/src/test/java/com/github/damontecres/wholphin/ui/detail/series/SeriesViewModelTest.kt",
        ], ["app/src/main/java/com/github/damontecres/wholphin/ui/detail/series/SeriesViewModel.kt"])
        self.assertIn("com.github.damontecres.wholphin.ui.detail.series.*", filters)
        self.assertIn("*SeriesViewModelTest", filters)

    def test_missing_or_unmapped_filters_refuse(self):
        with self.assertRaisesRegex(resolve.Refusal, "No semantic-resolution changes"):
            resolve.derive_filters([], [])
        with self.assertRaisesRegex(resolve.Refusal, "ambiguous"):
            resolve.derive_filters(["app/src/main/java/com/github/damontecres/wholphin/unknown/Foo.kt"], [])

    def test_supplemental_scope_allows_related_tests_and_refuses_unrelated_behavior(self):
        attention = ["app/src/main/java/com/github/damontecres/wholphin/ui/detail/series/SeriesViewModel.kt"]
        resolve.validate_resolution_scope([
            attention[0],
            "app/src/main/java/com/github/damontecres/wholphin/ui/detail/series/SeriesDetails.kt",
            "app/src/test/java/com/github/damontecres/wholphin/ui/detail/series/SeriesViewModelTest.kt",
            ".upstream-sync/blocked-context.json",
        ], attention)
        with self.assertRaisesRegex(resolve.Refusal, "outside"):
            resolve.validate_resolution_scope([
                attention[0],
                "app/src/main/java/com/github/damontecres/wholphin/ui/downloads/DownloadsPage.kt",
            ], attention)

    def test_changed_test_supplies_supplemental_filter_for_unmapped_resource_attention(self):
        filters = resolve.derive_filters([
            "app/src/main/res/values/strings.xml",
            "app/src/test/java/com/github/damontecres/wholphin/ui/detail/series/SeriesViewModelTest.kt",
        ], ["app/src/main/res/values/strings.xml"])
        self.assertEqual(["*SeriesViewModelTest"], filters)

    def test_default_no_publication_never_invokes_prepare_pr(self):
        candidate = self.candidate(
            33, "app/src/main/java/com/github/damontecres/wholphin/ui/detail/series/SeriesViewModel.kt",
            "1" * 40)
        runner = FakeRunner()
        with (patch.object(resolve, "verify_local_descendant"),
              patch.object(resolve, "assert_native_merge_identity"),
              patch.object(resolve, "resolution_paths", return_value=[
                  "app/src/main/java/com/github/damontecres/wholphin/ui/detail/series/SeriesViewModel.kt"]),
              patch.object(resolve, "validate_filter_targets")):
            resolve.publication_phase(self.root(), runner, candidate, lambda _: "")
        self.assertFalse(any(call and call[0] == "powershell" for call in runner.calls))

    def test_explicit_yes_rechecks_and_delegates_exact_filters_to_prepare_pr(self):
        candidate = self.candidate(
            33, "app/src/main/java/com/github/damontecres/wholphin/ui/detail/series/SeriesViewModel.kt",
            "1" * 40)
        candidate.state = "Ready for resolution"

        class PublishRunner(FakeRunner):
            def _result(self, args):
                if args and args[0] == "powershell":
                    return resolve.Result("prepared", "", 0)
                return super()._result(args)

        runner = PublishRunner()
        paths = ["app/src/main/java/com/github/damontecres/wholphin/ui/detail/series/SeriesViewModel.kt"]
        with (patch.object(resolve, "verify_local_descendant"),
              patch.object(resolve, "assert_native_merge_identity"),
              patch.object(resolve, "resolution_paths", return_value=paths),
              patch.object(resolve, "validate_filter_targets"),
              patch.object(resolve, "open_candidates", return_value=[candidate]),
              patch.object(resolve, "classify_dependencies", return_value=[candidate]),
              patch.object(resolve, "commit_native_resolution", return_value=("d" * 40, "f" * 40))):
            resolve.publication_phase(self.root(), runner, candidate, lambda _: "y")
        command = next(call for call in runner.calls if call and call[0] == "powershell")
        self.assertEqual("-Command", command[-2])
        self.assertIn("prepare-pr.ps1", command[-1])
        self.assertIn("-TestFilter @('com.github.damontecres.wholphin.ui.detail.series.*')", command[-1])
        self.assertIn("-PreserveMergeCommit", command[-1])
        self.assertIn(f"-ExpectedMergeFirstParent '{candidate.pr['head']['sha']}'", command[-1])
        self.assertIn(f"-ExpectedMergeSecondParent '{candidate.observation['upstream_sha']}'", command[-1])

    def test_clean_review_candidate_keeps_existing_non_conflict_publication_path(self):
        candidate = self.candidate(
            33, "app/src/main/java/com/github/damontecres/wholphin/ui/detail/series/SeriesViewModel.kt",
            "1" * 40,
        )
        candidate.observation["conflict_paths"] = []
        candidate.state = "Ready for resolution"

        class PublishRunner(FakeRunner):
            def _result(self, args):
                if args and args[0] == "powershell":
                    return resolve.Result("prepared", "", 0)
                return super()._result(args)

        runner = PublishRunner()
        paths = ["app/src/main/java/com/github/damontecres/wholphin/ui/detail/series/SeriesViewModel.kt"]
        with (patch.object(resolve, "verify_local_descendant"),
              patch.object(resolve, "assert_native_merge_identity") as native,
              patch.object(resolve, "resolution_paths", return_value=paths),
              patch.object(resolve, "validate_filter_targets"),
              patch.object(resolve, "open_candidates", return_value=[candidate]),
              patch.object(resolve, "classify_dependencies", return_value=[candidate])):
            resolve.publication_phase(self.root(), runner, candidate, lambda _: "y")
        native.assert_not_called()
        command = next(call for call in runner.calls if call and call[0] == "powershell")
        self.assertNotIn("-PreserveMergeCommit", command[-1])

    def test_waiting_candidate_refuses_direct_selection(self):
        candidate = self.candidate(37, "app/src/main/SeriesViewModel.kt", "2" * 40)
        candidate.state = "Waiting on PR #33"
        with self.assertRaisesRegex(resolve.Refusal, "Resolve its predecessor"):
            resolve.select_candidate([candidate], 37)

    def test_prepare_pr_contract_reuses_same_head_without_ready_or_force(self):
        source = (MODULE_PATH.parent / "prepare-pr.ps1").read_text(encoding="utf-8")
        self.assertIn("pr list --repo $slug --base $config.BaseBranch --head $branch --state open", source)
        self.assertIn("Remote branch is divergent or ahead; publication would require a force push", source)
        self.assertIn("[switch]$PreserveMergeCommit", source)
        self.assertIn("Expected exactly one existing Draft PR for the preserved upstream merge", source)
        self.assertIn("Expected exactly one existing Draft PR before preserved merge publication", source)
        self.assertIn("Existing Draft PR moved before publication; no push occurred", source)
        self.assertIn("HEAD is not the exact reviewed native upstream-resolution merge commit", source)
        self.assertIn("Existing Draft PR head does not match the reviewed upstream merge commit", source)
        self.assertNotIn("pr ready", source)
        self.assertNotIn("--force", source)


if __name__ == "__main__":
    unittest.main()
