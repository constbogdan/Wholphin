#!/usr/bin/env python3
"""Safely prepare a local I06 candidate branch for semantic resolution."""

from __future__ import annotations

import argparse
from fnmatch import fnmatchcase
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import mosaic_validation_policy


REPOSITORY = "constbogdan/Wholphin"
BASE_BRANCH = "main"
BRANCH_PREFIX = "chore/sync-upstream-"
EPISODE = re.compile(r"<!-- wholphin-upstream-episode:([0-9a-f]{64}) -->")
JOURNAL = re.compile(r"<!-- wholphin-upstream-journal:(\{.*?\}) -->")
TECHNICAL = re.compile(r"<summary>Technical evidence</summary>\s*```json\s*(\{.*?\})\s*```", re.S)
RUN_ID = re.compile(r"/actions/runs/(\d+)")


class Refusal(RuntimeError):
    """A safety condition could not be proven."""


@dataclass
class Result:
    stdout: str
    stderr: str
    returncode: int


@dataclass
class Candidate:
    pr: dict
    issue: dict
    observation: dict
    ci: dict
    metrics: dict
    state: str = "Independent"
    predecessor: int | None = None
    overlaps: tuple[str, ...] = ()


class Runner:
    def run(self, args: list[str], *, cwd: Path, check: bool = True) -> Result:
        completed = subprocess.run(
            args, cwd=cwd, text=True, encoding="utf-8", errors="replace",
            capture_output=True, check=False,
        )
        result = Result(completed.stdout, completed.stderr, completed.returncode)
        if check and result.returncode:
            detail = (result.stderr or result.stdout).strip()
            raise Refusal(f"Command failed ({result.returncode}): {' '.join(args)}\n{detail}")
        return result


def slug(remote: str) -> str | None:
    match = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$", remote.strip())
    return match.group(1) if match else None


def json_output(runner: Runner, args: list[str], root: Path):
    result = runner.run(args, cwd=root)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise Refusal(f"Expected JSON from {' '.join(args)}: {error}") from error


def marker(body: str) -> str | None:
    match = EPISODE.search(body or "")
    return match.group(1) if match else None


def technical_evidence(body: str) -> dict:
    match = TECHNICAL.search(body or "")
    if not match:
        return {}
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return {}


def journal_record(body: str) -> dict:
    match = JOURNAL.search(body or "")
    if not match:
        return {}
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return {}


def flatten_pages(value) -> list[dict]:
    if not isinstance(value, list):
        return []
    if value and all(isinstance(page, list) for page in value):
        return [item for page in value for item in page if isinstance(item, dict)]
    return [item for item in value if isinstance(item, dict)]


def find_issue(runner: Runner, root: Path, episode: str) -> dict:
    pages = json_output(runner, [
        "gh", "api", "--paginate", "--slurp",
        f"repos/{REPOSITORY}/issues?state=all&per_page=100",
    ], root)
    matches = [issue for issue in flatten_pages(pages)
               if "pull_request" not in issue and marker(issue.get("body", "")) == episode]
    if len(matches) != 1:
        raise Refusal(f"Expected exactly one linked I06 journal Issue; found {len(matches)}.")
    if matches[0].get("state") != "open":
        raise Refusal(f"Linked journal Issue #{matches[0].get('number')} is not open; respect the recorded disposition.")
    return matches[0]


def validate_observation(observation: dict, pr: dict, episode: str, *, runner=None, root=None,
                         run_id=None, attempt=None) -> None:
    expected = {
        "episode_id": episode,
        "downstream_repo": REPOSITORY,
        "branch": pr["head"]["ref"],
    }
    if run_id is not None:
        expected["run_id"] = str(run_id)
    if attempt is not None:
        expected["run_attempt"] = str(attempt)
    for key, wanted in expected.items():
        actual = observation.get(key)
        if actual is not None and str(actual) != str(wanted):
            raise Refusal(f"Machine evidence mismatch for {key}: expected {wanted}, found {actual}.")
    anchor = observation.get("candidate_sha")
    head = pr["head"]["sha"]
    if anchor and anchor != head:
        if runner is None or root is None or not is_ancestor(runner, root, REPOSITORY, anchor, head):
            raise Refusal("PR head is not a proven descendant of the machine-evidence candidate SHA.")


def load_observation(runner: Runner, root: Path, issue: dict, pr: dict, episode: str) -> tuple[dict, str | None]:
    record = journal_record(issue.get("body", ""))
    run_url = record.get("latestRunUrl")
    match = RUN_ID.search(run_url or "")
    if not match:
        fallback = technical_evidence(pr.get("body", ""))
        validate_observation(fallback, pr, episode, runner=runner, root=root)
        return fallback, run_url
    run_id = match.group(1)
    run = json_output(runner, ["gh", "api", f"repos/{REPOSITORY}/actions/runs/{run_id}"], root)
    attempt = int(run.get("run_attempt") or 0)
    if not attempt:
        raise Refusal("Latest Upstream Sync run did not expose a valid attempt number.")
    with tempfile.TemporaryDirectory(prefix="wholphin-upstream-evidence-") as directory:
        destination = Path(directory)
        artifact_name = f"upstream-outcome-{attempt}"
        downloaded = runner.run([
            "gh", "run", "download", run_id, "--repo", REPOSITORY,
            "--name", artifact_name, "--dir", str(destination),
        ], cwd=root, check=False)
        if downloaded.returncode:
            artifact_name = f"upstream-observation-{attempt}"
            downloaded = runner.run([
                "gh", "run", "download", run_id, "--repo", REPOSITORY,
                "--name", artifact_name, "--dir", str(destination),
            ], cwd=root, check=False)
        evidence_file = next(destination.rglob("*.json"), None) if downloaded.returncode == 0 else None
        if not evidence_file:
            fallback = technical_evidence(pr.get("body", ""))
            fallback["evidence_warning"] = "Machine observation artifact was unavailable or expired."
            validate_observation(fallback, pr, episode, runner=runner, root=root)
            return fallback, run_url
        observation = json.loads(evidence_file.read_text(encoding="utf-8"))
    validate_observation(observation, pr, episode, runner=runner, root=root,
                         run_id=run_id, attempt=attempt)
    return observation, run_url


def checks(runner: Runner, root: Path, number: int) -> dict:
    result = runner.run([
        "gh", "pr", "checks", str(number), "--repo", REPOSITORY,
        "--json", "name,state,link,bucket,workflow",
    ], cwd=root, check=False)
    if result.returncode and not result.stdout.strip():
        return {"status": "UNKNOWN", "name": None, "url": None}
    try:
        rows = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        return {"status": "UNKNOWN", "name": None, "url": None}
    preferred = next((row for row in rows if row.get("name") == "Full validation"), None)
    row = preferred or next((row for row in rows if row.get("bucket") in ("fail", "pending")), None)
    row = row or (rows[0] if rows else {})
    buckets = {item.get("bucket") for item in rows}
    status = ("FAILED" if buckets & {"fail", "cancel"} else
              "PENDING" if "pending" in buckets else "PASSED" if rows else "UNKNOWN")
    name = " / ".join(value for value in (row.get("workflow"), row.get("name")) if value)
    return {"status": status, "name": name or None, "url": row.get("link")}


def priority(issue: dict, observation: dict) -> dict:
    values = dict(observation.get("priority") or {})
    body = issue.get("body", "")
    patterns = {
        "risk": r"Risk:\s*\*\*(.*?)\*\*",
        "debt": r"Integration debt:\s*\*\*(.*?)\*\*",
        "age": r"Age:\s*\*\*(.*?)\*\*",
        "escalation": r"Escalation:\s*\*\*(.*?)\*\*",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, body)
        if match:
            values[key] = match.group(1)
    return {key: str(values.get(key) or "Unknown").title() if key != "age" else str(values.get(key) or "Unknown")
            for key in patterns}


def assert_preflight(runner: Runner, root: Path, *, allow_dirty=False) -> tuple[str, str]:
    if not shutil.which("git"):
        raise Refusal("Git is required and was not found on PATH.")
    if not shutil.which("gh"):
        raise Refusal("GitHub CLI is required. Install gh, then run 'gh auth login'.")
    top = runner.run(["git", "rev-parse", "--show-toplevel"], cwd=root).stdout.strip()
    if Path(top).resolve() != root.resolve():
        raise Refusal(f"Expected repository root {root}, but Git reported {top}.")
    origin = runner.run(["git", "remote", "get-url", "origin"], cwd=root).stdout.strip()
    if slug(origin) != REPOSITORY:
        raise Refusal(f"Expected origin {REPOSITORY}; found {slug(origin) or origin}.")
    dirty = runner.run(["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=root).stdout.strip()
    branch = runner.run(["git", "branch", "--show-current"], cwd=root).stdout.strip()
    if dirty and not allow_dirty:
        raise Refusal("Working tree is not clean. Commit or preserve local work separately; nothing was stashed or discarded.")
    auth = runner.run(["gh", "auth", "status", "--hostname", "github.com"], cwd=root, check=False)
    if auth.returncode:
        raise Refusal("GitHub CLI is not authenticated. Run 'gh auth login' and retry.")
    return branch, dirty


def validate_pr(pr: dict, number: int) -> str:
    if int(pr.get("number") or 0) != number:
        raise Refusal("GitHub returned metadata for a different PR.")
    if pr.get("base", {}).get("repo", {}).get("full_name") != REPOSITORY:
        raise Refusal(f"PR #{number} does not belong to {REPOSITORY}.")
    if pr.get("base", {}).get("ref") != BASE_BRANCH:
        raise Refusal(f"PR #{number} does not target {BASE_BRANCH}.")
    if pr.get("state") != "open":
        raise Refusal(f"PR #{number} is {pr.get('state', 'not open')}; closed decisions are not reopened.")
    branch = pr.get("head", {}).get("ref") or ""
    if pr.get("head", {}).get("repo", {}).get("full_name") != REPOSITORY:
        raise Refusal("PR head is not the maintained downstream repository.")
    episode = marker(pr.get("body", ""))
    if not episode or not branch.startswith(BRANCH_PREFIX):
        raise Refusal(f"PR #{number} is not a durable I06 Upstream Sync candidate.")
    return episode


def open_candidates(runner: Runner, root: Path) -> list[Candidate]:
    pulls = flatten_pages(json_output(runner, [
        "gh", "api", "--paginate", "--slurp",
        f"repos/{REPOSITORY}/pulls?state=open&base={BASE_BRANCH}&per_page=100",
    ], root))
    issues = flatten_pages(json_output(runner, [
        "gh", "api", "--paginate", "--slurp",
        f"repos/{REPOSITORY}/issues?state=all&per_page=100",
    ], root))
    candidates = []
    for pr in pulls:
        episode = marker(pr.get("body", ""))
        if (not episode or pr.get("head", {}).get("repo", {}).get("full_name") != REPOSITORY
                or not str(pr.get("head", {}).get("ref") or "").startswith(BRANCH_PREFIX)):
            continue
        linked = [issue for issue in issues if "pull_request" not in issue
                  and marker(issue.get("body", "")) == episode]
        if len(linked) != 1:
            raise Refusal(f"PR #{pr.get('number')} has {len(linked)} matching journal Issues; dependency state is ambiguous.")
        issue = linked[0]
        if issue.get("state") != "open":
            observation = technical_evidence(pr.get("body", ""))
            candidates.append(Candidate(pr, issue, observation, checks(runner, root, int(pr["number"])),
                                        priority(issue, observation), state="Superseded"))
            continue
        observation, _ = load_observation(runner, root, issue, pr, episode)
        candidates.append(Candidate(pr, issue, observation, checks(runner, root, int(pr["number"])),
                                    priority(issue, observation)))
    return sorted(candidates, key=lambda candidate: int(candidate.pr["number"]))


def semantic_paths(candidate: Candidate) -> set[str]:
    observation = candidate.observation
    paths = set(observation.get("review_paths") or []) | set(observation.get("conflict_paths") or [])
    for change in observation.get("automation_changes") or []:
        path = str(change.get("path") or "")
        production = (path.startswith("app/src/main/") or path.startswith(".github/")
                      or path.startswith("scripts/") or path.endswith((".gradle", ".gradle.kts")))
        ownership = change.get("ownership") in {"REVIEW", "DOWNSTREAM-OWNED"}
        if path and (production or ownership):
            paths.add(path)
    return {path for path in paths if not path.startswith("docs/") and not path.endswith(".md")}


def compare_status(runner: Runner, root: Path, repository: str, base: str, head: str) -> str:
    if base == head:
        return "identical"
    result = json_output(runner, ["gh", "api", f"repos/{repository}/compare/{base}...{head}"], root)
    return str(result.get("status") or "unknown")


def is_ancestor(runner: Runner, root: Path, repository: str, older: str, newer: str) -> bool:
    return compare_status(runner, root, repository, older, newer) in {"ahead", "identical"}


def classify_dependencies(runner: Runner, root: Path, candidates: list[Candidate]) -> list[Candidate]:
    main = json_output(runner, ["gh", "api", f"repos/{REPOSITORY}/git/ref/heads/{BASE_BRANCH}"], root)
    main_sha = main.get("object", {}).get("sha")
    if not main_sha:
        raise Refusal("Could not determine authoritative downstream main SHA.")
    active = [candidate for candidate in candidates if candidate.state != "Superseded"]
    for candidate in active:
        if is_ancestor(runner, root, REPOSITORY, candidate.pr["head"]["sha"], main_sha):
            candidate.state = "Superseded"
            continue
        observed_main = candidate.observation.get("downstream_sha")
        if observed_main != main_sha:
            candidate.state = "Dependency ambiguous"
    active = [candidate for candidate in active if candidate.state not in {"Superseded", "Dependency ambiguous"}]
    edges: dict[int, set[int]] = {int(candidate.pr["number"]): set() for candidate in active}
    for index, left in enumerate(active):
        for right in active[index + 1:]:
            overlap = sorted(semantic_paths(left) & semantic_paths(right))
            if not overlap:
                continue
            left_up = left.observation.get("upstream_sha")
            right_up = right.observation.get("upstream_sha")
            left_down = left.observation.get("downstream_sha")
            right_down = right.observation.get("downstream_sha")
            if not all((left_up, right_up, left_down, right_down)):
                left.state = right.state = "Dependency ambiguous"
                left.overlaps = right.overlaps = tuple(overlap)
                continue
            left_first = (is_ancestor(runner, root, "damontecres/Wholphin", left_up, right_up)
                          and is_ancestor(runner, root, REPOSITORY, left_down, right_down))
            right_first = (is_ancestor(runner, root, "damontecres/Wholphin", right_up, left_up)
                           and is_ancestor(runner, root, REPOSITORY, right_down, left_down))
            if left_first == right_first:
                left.state = right.state = "Dependency ambiguous"
                left.overlaps = right.overlaps = tuple(overlap)
            elif left_first:
                edges[int(right.pr["number"])].add(int(left.pr["number"]))
                right.overlaps = tuple(overlap)
            else:
                edges[int(left.pr["number"])].add(int(right.pr["number"]))
                left.overlaps = tuple(overlap)
    for candidate in active:
        number = int(candidate.pr["number"])
        if candidate.state == "Dependency ambiguous":
            continue
        predecessors = sorted(edges[number])
        if predecessors:
            candidate.state = f"Waiting on PR #{predecessors[0]}"
            candidate.predecessor = predecessors[0]
        elif len(active) == 1 or any(edges.values()):
            candidate.state = "Ready for resolution"
        else:
            candidate.state = "Independent"
    return candidates


def render_candidates(candidates: list[Candidate]) -> str:
    lines = ["Open upstream candidates", ""]
    for index, candidate in enumerate(candidates, 1):
        paths = sorted(set(candidate.observation.get("review_paths") or []) |
                       set(candidate.observation.get("conflict_paths") or []))
        metrics = candidate.metrics
        lines += [f"[{index}] PR #{candidate.pr['number']} - Issue #{candidate.issue['number']}",
                  f"    {metrics['risk']} risk - {metrics['debt']} debt - {metrics['age']}"
                  + (" - Attention" if metrics["escalation"] == "Attention" else ""),
                  f"    {len(paths)} requiring attention", f"    CI: {candidate.ci['status']}",
                  f"    {candidate.state}"]
        if candidate.overlaps:
            lines.append("    Overlap: " + ", ".join(Path(path).name for path in candidate.overlaps))
        lines.append("")
    return "\n".join(lines).rstrip()


def checkout(runner: Runner, root: Path, branch: str, remote_sha: str) -> None:
    valid = runner.run(["git", "check-ref-format", "--branch", branch], cwd=root, check=False)
    if valid.returncode:
        raise Refusal("GitHub supplied an invalid candidate branch name.")
    runner.run(["git", "fetch", "--no-tags", "origin", f"refs/heads/{branch}:refs/remotes/origin/{branch}"], cwd=root)
    fetched = runner.run(["git", "rev-parse", f"refs/remotes/origin/{branch}"], cwd=root).stdout.strip()
    if fetched != remote_sha:
        raise Refusal("Fetched candidate branch does not match the current PR head SHA.")
    local = runner.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], cwd=root, check=False)
    if local.returncode == 0:
        local_sha = runner.run(["git", "rev-parse", f"refs/heads/{branch}"], cwd=root).stdout.strip()
        if local_sha != fetched:
            raise Refusal(f"Local branch '{branch}' differs from the PR head; refusing to overwrite or reset it.")
        tracking = runner.run(["git", "for-each-ref", "--format=%(upstream:short)", f"refs/heads/{branch}"], cwd=root).stdout.strip()
        if tracking and tracking != f"origin/{branch}":
            raise Refusal(f"Local branch '{branch}' tracks unexpected ref '{tracking}'.")
        runner.run(["git", "switch", branch], cwd=root)
        if not tracking:
            runner.run(["git", "branch", "--set-upstream-to", f"origin/{branch}", branch], cwd=root)
    else:
        runner.run(["git", "switch", "--track", "-c", branch, f"origin/{branch}"], cwd=root)


def resolution_paths(runner: Runner, root: Path, remote_sha: str) -> list[str]:
    paths = set()
    commands = (
        ["git", "diff", "--no-renames", "--name-only", remote_sha, "HEAD", "--"],
        ["git", "diff", "--no-renames", "--name-only", "HEAD", "--"],
        ["git", "diff", "--cached", "--no-renames", "--name-only", "HEAD", "--"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    )
    for command in commands:
        paths.update(line.strip().replace("\\", "/") for line in runner.run(command, cwd=root).stdout.splitlines()
                     if line.strip())
    return sorted(paths)


def derive_filters(paths: list[str], attention: list[str]) -> list[str]:
    if not paths:
        raise Refusal("No semantic-resolution changes exist; publication is not needed.")
    production = sorted(set(path for path in paths + attention if path.startswith("app/src/main/")))
    changed_tests = sorted(set(path for path in paths
                               if path.startswith(("app/src/test/", "app/src/testDebug/"))))
    production_filters, fallback = mosaic_validation_policy.focused_tests(production)
    test_filters, _ = mosaic_validation_policy.focused_tests(changed_tests)
    if fallback and not test_filters:
        raise Refusal("Focused coverage is ambiguous and no supplemental changed test proves intent for: " +
                      ", ".join(fallback))
    filters = sorted((set(production_filters) - {mosaic_validation_policy.ALL_JVM_TESTS}) |
                     set(test_filters))
    if not filters:
        raise Refusal("No meaningful focused JVM filters can be derived from the resolution scope.")
    return filters


def validate_resolution_scope(paths: list[str], attention: list[str]) -> None:
    attention_set = set(attention)
    attention_filters, attention_fallback = mosaic_validation_policy.focused_tests(attention)
    changed_tests = [path for path in paths if path.startswith(("app/src/test/", "app/src/testDebug/"))]
    if attention_fallback and not changed_tests:
        raise Refusal("Attention scope has no deterministic focused-test mapping: " +
                      ", ".join(attention_fallback))
    unrelated = []
    for path in paths:
        if path in attention_set or path == ".upstream-sync/blocked-context.json":
            continue
        if path.startswith(("app/src/test/", "app/src/testDebug/")):
            continue
        if path.startswith("app/src/main/"):
            mapped, fallback = mosaic_validation_policy.focused_tests([path])
            if not fallback and set(mapped) & set(attention_filters):
                continue
        unrelated.append(path)
    if unrelated:
        raise Refusal("Resolution contains paths outside the deterministic attention/test scope: " +
                      ", ".join(unrelated))


def validate_filter_targets(root: Path, filters: list[str]) -> None:
    classes = set()
    for source_root in (root / "app" / "src").glob("test*"):
        if not source_root.is_dir():
            continue
        for source in list(source_root.rglob("*.kt")) + list(source_root.rglob("*.java")):
            text = source.read_text(encoding="utf-8", errors="replace")
            package = re.search(r"^\s*package\s+([\w.]+)", text, re.M)
            if not package:
                continue
            for name in re.findall(r"^\s*(?:public\s+)?(?:class|object)\s+(\w+)", text, re.M):
                classes.add(f"{package.group(1)}.{name}")
    unmatched = [test_filter for test_filter in filters
                 if not any(fnmatchcase(name, test_filter) or fnmatchcase(name.split(".")[-1], test_filter)
                            for name in classes)]
    if unmatched:
        raise Refusal("Focused JVM filters do not match source-controlled tests: " + ", ".join(unmatched))


def verify_local_descendant(runner: Runner, root: Path, candidate: Candidate) -> None:
    branch = candidate.pr["head"]["ref"]
    remote_sha = candidate.pr["head"]["sha"]
    current = runner.run(["git", "branch", "--show-current"], cwd=root).stdout.strip()
    if current != branch:
        raise Refusal(f"Expected candidate branch '{branch}', found '{current or 'detached HEAD'}'.")
    runner.run(["git", "fetch", "--no-tags", "origin",
                f"refs/heads/{branch}:refs/remotes/origin/{branch}"], cwd=root)
    fetched = runner.run(["git", "rev-parse", f"refs/remotes/origin/{branch}"], cwd=root).stdout.strip()
    if fetched != remote_sha:
        raise Refusal("Remote candidate head moved after evidence refresh; rerun without overwriting it.")
    ancestry = runner.run(["git", "merge-base", "--is-ancestor", remote_sha, "HEAD"], cwd=root, check=False)
    if ancestry.returncode:
        raise Refusal("Local candidate branch is not a normal descendant of the remote PR head.")


def prepare_command(root: Path, filters: list[str]) -> list[str]:
    def quote(value):
        return "'" + str(value).replace("'", "''") + "'"
    script = quote(root / "scripts" / "prepare-pr.ps1")
    filter_array = "@(" + ",".join(quote(value) for value in filters) + ")"
    return ["powershell", "-NoProfile", "-Command", f"& {script} -TestFilter {filter_array}"]


def select_candidate(candidates: list[Candidate], requested: int | None, input_fn=input) -> Candidate | None:
    if not candidates:
        print("No open Upstream Sync attention candidates.")
        return None
    print(render_candidates(candidates))
    selectable = [candidate for candidate in candidates
                  if candidate.state in {"Ready for resolution", "Independent"}]
    if requested is not None:
        matches = [candidate for candidate in candidates if int(candidate.pr["number"]) == requested]
        if len(matches) != 1:
            raise Refusal(f"Open I06 candidate PR #{requested} was not found.")
        chosen = matches[0]
    else:
        default_index = candidates.index(selectable[0]) + 1 if len(selectable) == 1 else None
        try:
            answer = input_fn("\nSelect candidate" + (f" [{default_index}]" if default_index else "") + ": ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSelection cancelled; no branch was changed.")
            return None
        if not answer and default_index:
            chosen = selectable[0]
        elif answer.isdigit() and 1 <= int(answer) <= len(candidates):
            chosen = candidates[int(answer) - 1]
        else:
            print("Selection cancelled; no branch was changed.")
            return None
    if chosen.state.startswith("Waiting on"):
        raise Refusal(f"PR #{chosen.pr['number']} is {chosen.state}. Resolve its predecessor first.")
    if chosen.state in {"Superseded", "Dependency ambiguous"}:
        raise Refusal(f"PR #{chosen.pr['number']} is {chosen.state}; refusing to guess an integration order.")
    return chosen


def publication_phase(root: Path, runner: Runner, candidate: Candidate, input_fn=input) -> None:
    if candidate.state.startswith("Waiting on") or candidate.state in {"Superseded", "Dependency ambiguous"}:
        raise Refusal(f"Candidate is {candidate.state}; semantic publication is not currently actionable.")
    verify_local_descendant(runner, root, candidate)
    paths = resolution_paths(runner, root, candidate.pr["head"]["sha"])
    attention = sorted(set(candidate.observation.get("review_paths") or []) |
                       set(candidate.observation.get("conflict_paths") or []))
    validate_resolution_scope(paths, attention)
    filters = derive_filters(paths, attention)
    validate_filter_targets(root, filters)
    print("\nPublication plan")
    print(f"PR: #{candidate.pr['number']} (same Draft)")
    print("Changes:")
    for path in paths:
        print(f"- {path}")
    print("Validation:\n  Focused tests:")
    for test_filter in filters:
        print(f"  - {test_filter}")
    try:
        approved = input_fn("\nReady to PUSH? [y/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        approved = ""
    if approved != "y":
        print("Publication cancelled; nothing was committed or pushed.")
        return

    refreshed = classify_dependencies(runner, root, open_candidates(runner, root))
    matches = [item for item in refreshed if int(item.pr["number"]) == int(candidate.pr["number"])]
    if len(matches) != 1 or marker(matches[0].pr.get("body", "")) != marker(candidate.pr.get("body", "")):
        raise Refusal("Candidate PR/episode changed immediately before publication.")
    current = matches[0]
    if current.state.startswith("Waiting on") or current.state in {"Superseded", "Dependency ambiguous"}:
        raise Refusal(f"Candidate is now {current.state}; prepare-pr was not invoked.")
    if current.pr["head"]["sha"] != candidate.pr["head"]["sha"]:
        raise Refusal("Remote candidate head changed immediately before publication.")
    verify_local_descendant(runner, root, current)
    current_paths = resolution_paths(runner, root, current.pr["head"]["sha"])
    validate_resolution_scope(current_paths, attention)
    current_filters = derive_filters(current_paths, attention)
    validate_filter_targets(root, current_filters)
    if current_paths != paths or current_filters != filters:
        raise Refusal("Resolution scope or focused-test plan changed after approval; rerun and review it.")
    runner.run(prepare_command(root, filters), cwd=root)


def prompt(number: int, pr: dict, issue: dict, observation: dict, metrics: dict, ci: dict,
           dependency="Ready for resolution") -> str:
    commits = observation.get("incoming_commits") or []
    paths = sorted(set(observation.get("review_paths") or []) | set(observation.get("conflict_paths") or []))
    commit_lines = []
    for commit in commits:
        sha = str(commit.get("sha") or "")
        subject = " ".join(str(commit.get("subject") or "Untitled upstream commit").split())
        url = commit.get("url")
        commit_lines.append(f"- {sha[:7]} - {subject}" + (f"\n  {url}" if url else ""))
    if not commit_lines:
        commit_lines = ["- Exact incoming commit details were unavailable; inspect the linked Actions run and Git history."]
    path_lines = [f"- {path}" for path in paths] or ["- No attention paths were recovered; inspect the linked run before editing."]
    ci_lines = [f"{ci['status']}" + (f" - {ci['name']}" if ci.get("name") else "")]
    if ci.get("url"):
        ci_lines.append(ci["url"])
    return f"""# Resolve Upstream Sync PR #{number}

Resolve the currently checked-out Upstream Sync candidate for PR #{number}.

This branch was created by I06. The candidate intentionally preserves current
Mosaic/downstream bytes for unresolved attention paths while integrating safe
non-conflicting upstream changes.

Do not interpret the absence of Git conflict markers as proof that the semantic
integration is complete.

Linked journal: #{issue['number']}
Candidate state: {'Draft - attention required' if pr.get('draft') else 'Normal PR - verify attention disposition'}
Dependency state: {dependency}
Risk: {metrics['risk']}
Integration debt: {metrics['debt']}
Age: {metrics['age']}
Escalation: {metrics['escalation']}
Episode ID: {marker(pr.get('body', ''))}
Upstream SHA: {observation.get('upstream_sha', 'unavailable')}
Downstream baseline SHA: {observation.get('downstream_sha', 'unavailable')}

## Incoming upstream changes

{chr(10).join(commit_lines)}

## Attention paths

{chr(10).join(path_lines)}

Cleanly integrated paths: {int(observation.get('clean_path_count') or 0)}

## Current CI

{chr(10).join(ci_lines)}

For every attention path:

1. Reconstruct the exact upstream intent from the recorded evidence and Git history.
2. Inspect current Mosaic behavior.
3. Preserve both where compatible.
4. Never blindly choose ours or theirs.
5. Preserve already-integrated clean upstream changes.
6. Preserve Enhanced Wholphin OFF behavior.
7. Preserve Mosaic acquisition, Series, and Downloads behavior where applicable.
8. Add or update tests where behavior changes.

Start with compile/runtime blockers exposed by CI, then resolve the remaining
attention paths semantically. Inspect the linked run when bounded failure evidence
is unavailable. Run focused validation as you work.

Do not push, merge, mark the PR Ready, rewrite candidate history, or force-update
the branch.

Report the semantic decisions made, tests changed, and validation needed before
this Draft can become Ready.
"""


def selected_output(number: int, root: Path, candidate: Candidate, runner: Runner) -> tuple[str, Path]:
    pr, issue, observation = candidate.pr, candidate.issue, candidate.observation
    run_url = journal_record(issue.get("body", "")).get("latestRunUrl")
    metrics, ci = candidate.metrics, candidate.ci
    checkout(runner, root, pr["head"]["ref"], pr["head"]["sha"])
    content = prompt(number, pr, issue, observation, metrics, ci, candidate.state)
    output = root / ".logs" / "upstream-resolution" / f"pr-{number}" / "codex-prompt.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8", newline="\n")
    paths = sorted(set(observation.get("review_paths") or []) | set(observation.get("conflict_paths") or []))
    clean = int(observation.get("clean_path_count") or 0)
    summary = [
        "Upstream resolution", "",
        f"PR:          #{number}",
        f"Issue:       #{issue['number']}",
        f"State:       {'Draft - attention required' if pr.get('draft') else 'Normal - verify attention disposition'}",
        f"Risk:        {metrics['risk']}",
        f"Debt:        {metrics['debt']}",
        f"Age:         {metrics['age']}",
        f"Escalation:  {metrics['escalation']}",
        f"Dependency:  {candidate.state}", "",
        "Branch:", pr["head"]["ref"], "",
        f"{len(paths)} requiring attention",
        *[f"- {path}" for path in paths], "",
        f"{clean} additional file{'s' if clean != 1 else ''} integrate cleanly.", "",
        f"CI: {ci['status']}",
    ]
    if ci.get("name"):
        summary.append(f"Check: {ci['name']}")
    if ci.get("url"):
        summary.append(f"Run: {ci['url']}")
    elif run_url:
        summary.append(f"Latest sync: {run_url}")
    summary += ["", "Checked out candidate branch successfully.", "", content.rstrip(), "",
                "Ready for semantic resolution.", "", "Next:",
                "1. Paste the generated prompt into Codex.",
                "2. Let Codex resolve and run focused checks.",
                "3. Run the appropriate local validation.",
                "4. Use prepare-pr to update the SAME existing PR.",
                "5. Mark Ready only after semantic resolution and CI are satisfactory.", "",
                f"Prompt: {output.relative_to(root).as_posix()}"]
    return "\n".join(summary), output


def execute(number: int, root: Path, runner: Runner) -> tuple[str, Path]:
    assert_preflight(runner, root)
    pr = json_output(runner, ["gh", "api", f"repos/{REPOSITORY}/pulls/{number}"], root)
    episode = validate_pr(pr, number)
    issue = find_issue(runner, root, episode)
    observation, _ = load_observation(runner, root, issue, pr, episode)
    candidate = Candidate(pr, issue, observation, checks(runner, root, number), priority(issue, observation),
                          state="Ready for resolution")
    return selected_output(number, root, candidate, runner)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr", type=int)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    try:
        runner = Runner()
        branch, dirty = assert_preflight(runner, root, allow_dirty=True)
        candidates = classify_dependencies(runner, root, open_candidates(runner, root))
        current = [candidate for candidate in candidates if candidate.pr["head"]["ref"] == branch]
        if current:
            if args.pr is not None and int(current[0].pr["number"]) != args.pr:
                raise Refusal(f"Current candidate branch belongs to PR #{current[0].pr['number']}, not PR #{args.pr}.")
            publication_phase(root, runner, current[0])
            return 0
        if dirty:
            raise Refusal("Working tree is not clean. Preserve local work separately before selecting another candidate.")
        chosen = select_candidate(candidates, args.pr)
        if chosen is None:
            return 0
        summary, _ = selected_output(int(chosen.pr["number"]), root, chosen, runner)
        print(summary)
        return 0
    except Refusal as error:
        print(f"resolve-upstream: REFUSED\n{error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
