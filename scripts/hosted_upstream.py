"""Hosted-only normal Git integration; no application code or build is executed.

The observe job has read permission. The publish job repeats the observation in
a fresh disposable repository and checks the first job's exact SHA pair.
"""

import argparse
import datetime
import hashlib
import html
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile


ORIGIN = "constbogdan/Wholphin"
UPSTREAM = "damontecres/Wholphin"
URLS = {"origin": f"https://github.com/{ORIGIN}.git",
        "upstream": f"https://github.com/{UPSTREAM}.git"}
# Reviewed, already integrated official upstream commit at implementation time.
INITIAL_ANCHOR = "1778bdb34caa699c0590232a7de709a889839765"
PREFIX = "chore/sync-upstream-"
BRANCH = re.compile(re.escape(PREFIX) + r"([0-9a-f]{40})-([0-9a-f]{40})$")
OBSERVATION = re.compile(r"<!-- wholphin-upstream-observed:([0-9a-f]{40}) -->")
ISSUE_PREFIX = "[upstream-sync blocked] "


class Blocked(RuntimeError):
    pass


class IdentityError(Blocked):
    pass


def upstream_summary(observation, *, publication=False, operation_error=False):
    outcome = observation['outcome']
    if operation_error or observation.get('record_failure'):
        heading = 'Publication error' if publication else 'Observation error'
    elif outcome == 'blocked':
        heading = 'Blocked · semantic conflicts' if observation.get('textual_conflicts') else 'Blocked · review required'
    else:
        heading = {'no_delta': 'No upstream delta', 'ready': 'Ready candidate',
                   'existing_pr': 'Existing candidate PR', 'pr_created': 'Published candidate PR'}.get(outcome, 'Upstream observation')
    # Retain full evidence and escape remote/user-controlled strings. Keep this in
    # the existing protected sync helper rather than adding an executable dependency.
    return '## ' + heading + '\n\n<pre>' + html.escape(json.dumps(observation, indent=2, ensure_ascii=True)) + '</pre>\n'


class OperationError(Blocked):
    """Same blocked outcome/exit policy, distinct human infrastructure diagnosis."""


def command(args, *, cwd=None, env=None, check=True, input=None):
    result = subprocess.run(args, cwd=cwd, env=env, input=input,
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace", timeout=180)
    if check and result.returncode:
        # Never echo credentials, untrusted command output, or workflow commands.
        operation = args[1:]
        while operation and operation[0] == "-c":
            operation = operation[2:]
        raise OperationError(f"{args[0]} {operation[0] if operation else 'operation'} failed (exit {result.returncode}); inspect permissions/connectivity and rerun.")
    return result


class Git:
    def __init__(self, path):
        self.path = Path(path)
        self.env = {k: v for k, v in os.environ.items()
                    if not k.startswith("GIT_") and k not in {"GH_TOKEN", "GITHUB_TOKEN", "SYNC_PUBLISH_TOKEN"}}
        self.env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                        GIT_TERMINAL_PROMPT="0", GIT_LFS_SKIP_SMUDGE="1")
        self.options = ["git", "-c", "core.hooksPath=" + os.devnull,
                        "-c", "core.autocrlf=false", "-c", "commit.gpgsign=false",
                        "-c", "maintenance.auto=false", "-c", "gc.auto=0",
                        "-c", "protocol.file.allow=never"]
        self.run("init", "--quiet")
        for name, url in URLS.items():
            self.run("remote", "add", name, url)

    def run(self, *args, check=True, input=None):
        return command(self.options + list(args), cwd=self.path, env=self.env,
                       check=check, input=input)

    def text(self, *args):
        return self.run(*args).stdout.strip()

    def identities(self):
        for name, expected in URLS.items():
            for option in ([], ["--push"]):
                actual = self.text("remote", "get-url", *option, "--all", name)
                if actual != expected:
                    raise IdentityError(f"Unexpected {name} identity; expected exactly {expected}.")

    def fetch(self, remote, source, destination):
        self.run("fetch", "--quiet", "--no-tags", remote, f"{source}:{destination}")

    def ancestor(self, older, newer):
        result = self.run("merge-base", "--is-ancestor", older, newer, check=False)
        if result.returncode not in (0, 1):
            raise Blocked("Cannot prove upstream ancestry; history is missing or rewritten.")
        return result.returncode == 0

    def push(self, branch, candidate):
        self.identities()
        env = dict(self.env, GH_TOKEN=os.environ["SYNC_PUBLISH_TOKEN"])
        # A fixed, trusted credential helper; never persisted in Git config.
        command(self.options + ["-c", "credential.helper=",
                "-c", "credential.helper=!gh auth git-credential", "push", "--porcelain",
                "origin", f"{candidate}:refs/heads/{branch}"], cwd=self.path, env=env)


class GitHub:
    def environment(self, publish=False):
        env = {k: v for k, v in os.environ.items() if k != "SYNC_PUBLISH_TOKEN"}
        if publish:
            env["GH_TOKEN"] = os.environ["SYNC_PUBLISH_TOKEN"]
        return env

    def api(self, endpoint, payload=None, publish=False):
        args = ["gh", "api", "--hostname", "github.com", endpoint]
        if payload is not None:
            args += ["--method", "POST", "--input", "-"]
        env = self.environment(publish)
        return json.loads(command(args, env=env, input=json.dumps(payload) if payload else None).stdout)

    def pages(self, resource):
        output = command(["gh", "api", "--hostname", "github.com", "--paginate", "--slurp",
                          f"repos/{ORIGIN}/{resource}"], env=self.environment()).stdout
        return [item for page in json.loads(output) for item in page]

    def pulls(self):
        return self.pages("pulls?state=all&base=main&per_page=100")

    def issues(self):
        return [i for i in self.pages("issues?state=all&creator=github-actions%5Bbot%5D&per_page=100")
                if "pull_request" not in i and i["title"].startswith(ISSUE_PREFIX)]

    def create_pr(self, branch, body):
        return self.api(f"repos/{ORIGIN}/pulls", {
            "head": branch, "base": "main", "title": "chore: synchronize official upstream " + branch[len(PREFIX):12 + len(PREFIX)],
            "body": body, "maintainer_can_modify": False}, publish=True)["html_url"]

    def blocked_issue(self, observation):
        if self.api(f"repos/{ORIGIN}").get("has_issues") is not True:
            raise Blocked("Repository Issues are disabled; enable Issues externally to retain the required blocked-sync issue. No App credential change is indicated.")
        durable = dict(observation)
        # Exact identities and conflict evidence remain durable even when a huge
        # delta cannot fit a PR body. The complete JSON is supplemental only.
        for field in ("incoming_commits", "changed_paths", "conflict_paths", "protected_paths"):
            rows = durable.get(field, [])
            durable[field] = ([dict(row, subject=row["subject"][:300]) for row in rows[:10]]
                              if field == "incoming_commits" else [row[:500] for row in rows[:10]])
            if rows:
                durable["reason"] = durable.get("reason", "") + f" {field}: bounded preview of {len(rows)} records; reconstruct full evidence from the exact recorded SHAs."
        body = description(durable)
        key = hashlib.sha256(json.dumps({k: observation.get(k) for k in
            ("upstream_sha", "downstream_sha", "reason")}, sort_keys=True).encode()).hexdigest()
        marker = f"<!-- wholphin-upstream-blocked:{key} -->"
        for issue in self.issues():
            if marker in (issue.get("body") or ""):
                return issue["html_url"]
        return self.api(f"repos/{ORIGIN}/issues", {
            "title": ISSUE_PREFIX + observation.get("upstream_sha", "unknown")[:12],
            "body": marker + "\n" + body})["html_url"]


def sync_pulls(pulls):
    return [p for p in pulls if p["base"]["ref"] == "main"
            and p["base"]["repo"]["full_name"] == ORIGIN
            and p["head"].get("repo")
            and p["head"]["repo"]["full_name"] == ORIGIN
            and p["head"]["ref"].startswith(PREFIX)]


def branch_name(upstream, downstream):
    if not all(re.fullmatch(r"[0-9a-f]{40}", sha) for sha in (upstream, downstream)):
        raise Blocked("Invalid SHA identity.")
    return f"{PREFIX}{upstream}-{downstream}"


def inspect(git, github, observation, anchor=INITIAL_ANCHOR):
    git.identities()
    git.fetch("origin", "refs/heads/main", "refs/remotes/origin/main")
    git.fetch("upstream", "refs/heads/main", "refs/remotes/upstream/main")
    down = git.text("rev-parse", "refs/remotes/origin/main")
    up = git.text("rev-parse", "refs/remotes/upstream/main")
    observation.update(upstream_sha=up, downstream_sha=down, branch=branch_name(up, down))
    if not git.ancestor(anchor, down):
        raise Blocked("Downstream no longer contains the reviewed initial upstream anchor; inspect main history.")
    pulls = sync_pulls(github.pulls())
    anchors = {anchor}
    # Also retain an attempted branch if a runner died after push but before PR.
    refs = git.text("ls-remote", "--refs", "origin", "refs/heads/" + PREFIX + "*")
    for row in refs.splitlines():
        _, ref = row.split()
        match = BRANCH.fullmatch(ref.removeprefix("refs/heads/"))
        if match:
            destination = "refs/attempts/" + match[1] + "-" + match[2]
            git.fetch("origin", ref, destination)
            if not git.ancestor(match[1], destination) or not git.ancestor(match[2], destination):
                raise Blocked("Existing sync branch does not contain its named input pair; inspect different work without overwriting it.")
            anchors.add(match[1])
    # PR head refs survive branch deletion. Closed PRs remain decision records.
    for pr in pulls:
        match = BRANCH.fullmatch(pr["head"]["ref"])
        if match:
            git.fetch("origin", f"refs/pull/{int(pr['number'])}/head", f"refs/review/{int(pr['number'])}")
            anchors.add(match[1])
    for issue in github.issues():
        anchors.update(OBSERVATION.findall(issue.get("body") or ""))
    for previous in sorted(anchors):
        if git.run("cat-file", "-e", previous + "^{commit}", check=False).returncode:
            git.fetch("upstream", previous, "refs/observations/" + previous)
        if not git.ancestor(previous, up):
            raise Blocked(f"Upstream is not a descendant of recorded observation {previous}; human rewrite review required.")
    observation["ancestry_validated"] = True
    if git.ancestor(up, down):
        observation.update(outcome="no_delta", comparison_baseline=up, upstream_base_sha=up,
                           incoming_count=0, incoming_commits=[], changed_paths=[], conflict_paths=[])
        return
    bases = git.text("merge-base", "--all", down, up).splitlines()
    if len(bases) != 1:
        raise Blocked("Expected one common comparison baseline; inspect unrelated/criss-cross history.")
    base = bases[0]
    observation.update(comparison_baseline=base, upstream_base_sha=base)
    commits = git.text("rev-list", "--reverse", f"{down}..{up}").splitlines()
    observation["incoming_commits"] = [{"sha": sha, "subject": git.text("show", "-s", "--format=%s", sha)} for sha in commits]
    observation["changed_paths"] = git.run("diff", "--name-only", "-z", "--no-ext-diff", "--no-textconv", base, up, "--").stdout.rstrip("\0").split("\0")
    observation["incoming_count"] = len(commits)
    same = [p for p in pulls if p["head"]["ref"] == observation["branch"]]
    others = [p for p in pulls if p["state"] == "open" and p not in same]
    if others:
        observation["existing_pr_url"] = others[0]["html_url"]
        raise Blocked("Another sync PR is open; review/merge or deliberately close it before a new proposal. History was not overwritten.")
    if len(same) > 1 or (same and same[0]["state"] != "open"):
        raise Blocked("This exact SHA pair has a closed or ambiguous PR decision; do not automatically reopen or recreate it.")
    # Merge occurs only in this process-owned temporary checkout. No hooks,
    # filters, application scripts, local actions, or builds are invoked.
    git.run("checkout", "--quiet", "--detach", down)
    git.env.update(GIT_AUTHOR_NAME="github-actions[bot]", GIT_COMMITTER_NAME="github-actions[bot]",
                   GIT_AUTHOR_EMAIL="41898282+github-actions[bot]@users.noreply.github.com",
                   GIT_COMMITTER_EMAIL="41898282+github-actions[bot]@users.noreply.github.com")
    merge = git.run("merge", "--no-ff", "--no-commit", up, check=False)
    conflicts = git.run("diff", "--name-only", "--diff-filter=U", "-z").stdout.rstrip("\0")
    observation["conflict_paths"] = conflicts.split("\0") if conflicts else []
    observation["textual_conflicts"] = bool(conflicts)
    if merge.returncode:
        raise Blocked("Textual conflicts require human semantic resolution." if conflicts else "Normal integration failed before publication.")
    git.run("diff", "--cached", "--check")
    tree = git.text("write-tree")
    protected = git.run("diff", "--name-only", "--no-ext-diff", "--no-textconv", down, tree,
                        "--", ".github", "scripts/hosted_upstream.py").stdout.strip()
    if protected:
        observation["protected_paths"] = protected.splitlines()
        raise Blocked("Integration changes hosted automation/publisher guards; review these changes manually before publication.")
    timestamp = max(int(git.text("show", "-s", "--format=%ct", s)) for s in (up, down))
    git.env.update(GIT_AUTHOR_DATE=f"{timestamp} +0000", GIT_COMMITTER_DATE=f"{timestamp} +0000")
    message = f"Merge official upstream {up} into downstream {down}\n\nWholphin-Upstream: {up}\nWholphin-Downstream: {down}\n"
    candidate = git.run("commit-tree", tree, "-p", down, "-p", up, input=message).stdout.strip()
    if not git.ancestor(up, candidate) or not git.ancestor(down, candidate):
        raise Blocked("Candidate does not contain both exact input commits.")
    observation.update(candidate_sha=candidate, candidate_tree=tree, outcome="ready")
    description(observation)  # Check durable PR metadata fits before any push.
    if same:
        if same[0]["head"]["sha"] != candidate:
            raise Blocked("Existing PR head differs from the deterministic candidate; preserve human changes.")
        observation.update(outcome="existing_pr", pr_url=same[0]["html_url"])


def publish(git, github, observation, expected_up, expected_down):
    if (observation.get("upstream_sha"), observation.get("downstream_sha")) != (expected_up, expected_down):
        raise Blocked("Refs changed between read and publish jobs; rerun to observe current inputs.")
    if observation["outcome"] in {"no_delta", "existing_pr"}:
        return
    if observation["outcome"] != "ready":
        raise Blocked("Observation is not a publishable candidate.")
    token_present = bool(os.environ.get("SYNC_PUBLISH_TOKEN", "").strip())
    print("SYNC_PUBLISH_TOKEN: " + ("present" if token_present else "missing"))
    if not token_present:
        raise OperationError("Publication App token unavailable. Check SYNC_BOT_CLIENT_ID and SYNC_BOT_PRIVATE_KEY for the approved repository-scoped App and rerun; no branch was pushed.")
    git.identities()
    for remote, expected in (("origin", expected_down), ("upstream", expected_up)):
        actual = git.text("ls-remote", "--refs", remote, "refs/heads/main").split()
        if not actual or actual[0] != expected:
            raise Blocked("Main ref moved immediately before publication; rerun without overwriting history.")
    branch, candidate = observation["branch"], observation["candidate_sha"]
    current = git.text("ls-remote", "--refs", "origin", "refs/heads/" + branch).split()
    if current and current[0] != candidate:
        raise Blocked("Sync branch already contains different work; no force push is permitted.")
    # Recheck PR decisions just before publication, including partially completed retries.
    pulls = sync_pulls(github.pulls())
    matching = [p for p in pulls if p["head"]["ref"] == branch]
    if matching:
        if len(matching) == 1 and matching[0]["state"] == "open" and matching[0]["head"]["sha"] == candidate:
            observation.update(outcome="existing_pr", pr_url=matching[0]["html_url"])
            return
        raise Blocked("PR decision changed before publication; human review required.")
    if any(p["state"] == "open" for p in pulls):
        raise Blocked("Another sync PR appeared before publication; rerun after review.")
    if not current:
        git.push(branch, candidate)
    published = git.text("ls-remote", "--refs", "origin", "refs/heads/" + branch).split()
    if not published or published[0] != candidate:
        raise Blocked("Published branch identity could not be verified; preserve it and inspect the remote.")
    observation["pr_url"] = github.create_pr(branch, description(observation))
    observation["outcome"] = "pr_created"


def description(o):
    lines = ["## Hosted upstream synchronization", "",
             "Required **CI / Full validation is pending** for a new candidate. The scoped App token triggers the normal PR CI path. Existing PR check state must be inspected on GitHub.", "",
             "Human semantic review and merge/reject remain required. A textual merge is not behavioral validation. Review Series/Home/Downloads, navigation, Discover requests, preferences/protobuf, resources, acquisition/integrity, and Enhanced Wholphin OFF behavior.", "",
             "No local workstation validation is required for this hosted path. No automatic conflict resolution or merge is performed.", ""]
    for key in ("outcome", "upstream_repo", "upstream_ref", "upstream_base_sha", "upstream_sha", "downstream_repo", "downstream_ref", "downstream_sha", "comparison_baseline", "candidate_sha", "branch", "incoming_count", "textual_conflicts", "protected_paths", "observed_at", "run_url", "reason", "existing_pr_url"):
        value = html.escape(str(o.get(key, 'not available'))).replace("@", "&#64;")
        lines.append(f"- {key}: {value}")
    for title, rows in (("Incoming commits", [c["sha"] + " " + c["subject"] for c in o.get("incoming_commits", [])]),
                        ("Changed paths (common base to upstream)", o.get("changed_paths", [])),
                        ("Conflict paths", o.get("conflict_paths", []))):
        lines += ["", "### " + title, ""]
        lines += ["- " + html.escape(str(row)).replace("@", "&#64;") for row in rows] or ["None recorded."]
    body = "\n".join(lines)
    # Keep every critical SHA/path in the durable issue/PR, rather than silently
    # truncating it into an expiring artifact. Oversized proposals fail closed.
    if len(body.encode("utf-8")) > 55000:
        raise Blocked("Evidence exceeds one durable GitHub body; split/review this integration manually.")
    if o.get("upstream_sha") and o.get("ancestry_validated"):
        body += "\n\n<!-- wholphin-upstream-observed:" + o["upstream_sha"] + " -->"
    return body + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--expected-upstream", default="")
    parser.add_argument("--expected-downstream", default="")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    o = {"schema_version": 1, "upstream_repo": UPSTREAM, "upstream_ref": "refs/heads/main",
         "downstream_repo": ORIGIN, "downstream_ref": "refs/heads/main",
         "observed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
         "workflow": os.environ.get("GITHUB_WORKFLOW"), "run_id": os.environ.get("GITHUB_RUN_ID"),
         "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
         "run_url": f"https://github.com/{ORIGIN}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}",
         "outcome": "blocked", "textual_conflicts": None}
    github = GitHub()
    identity_valid = False
    operation_error = False
    try:
        if (os.environ.get("GITHUB_ACTIONS") != "true" or os.environ.get("GITHUB_REPOSITORY") != ORIGIN
                or os.environ.get("GITHUB_REF") != "refs/heads/main"
                or os.environ.get("GITHUB_EVENT_NAME") not in {"schedule", "workflow_dispatch"}):
            raise IdentityError("Hosted execution requires the canonical downstream, main, and schedule/workflow_dispatch.")
        with tempfile.TemporaryDirectory(prefix="wholphin-sync-", dir=os.environ["RUNNER_TEMP"]) as work:
            git = Git(work)
            git.identities()
            identity_valid = True
            inspect(git, github, o)
            if args.publish:
                publish(git, github, o, args.expected_upstream, args.expected_downstream)
    except (Blocked, OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        operation_error = isinstance(exc, OperationError) or not isinstance(exc, Blocked)
        o.update(outcome="blocked", reason=str(exc) if isinstance(exc, Blocked) else f"{type(exc).__name__}: hosted operation failed; inspect permissions/input and rerun.")
        if args.publish and identity_valid and not isinstance(exc, IdentityError):
            try:
                o["blocked_issue_url"] = github.blocked_issue(o)
            except (Blocked, OSError, ValueError, subprocess.TimeoutExpired) as record_error:
                o["record_failure"] = "Durable issue creation failed. This run must remain failed; manually preserve its exact SHA pair and diagnostics in a GitHub issue before retrying."
                if isinstance(record_error, Blocked):
                    o["record_failure"] += " " + str(record_error)
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(o, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as stream:
                for key in ("outcome", "upstream_sha", "downstream_sha"):
                    stream.write(f"{key}={o.get(key, '')}\n")
        if os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as stream:
                stream.write(upstream_summary(o, publication=args.publish, operation_error=operation_error))
    return 1 if args.publish and o["outcome"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
