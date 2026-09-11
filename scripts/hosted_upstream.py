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
import sys
import tempfile
from urllib.parse import quote


ORIGIN = "constbogdan/Wholphin"
UPSTREAM = "damontecres/Wholphin"
URLS = {"origin": f"https://github.com/{ORIGIN}.git",
        "upstream": f"https://github.com/{UPSTREAM}.git"}
# Reviewed, already integrated official upstream commit at implementation time.
INITIAL_ANCHOR = "1778bdb34caa699c0590232a7de709a889839765"
PREFIX = "chore/sync-upstream-"
BRANCH = re.compile(re.escape(PREFIX) + r"([0-9a-f]{40})-([0-9a-f]{40})$")
OBSERVATION = re.compile(r"<!-- wholphin-upstream-observed:([0-9a-f]{40}) -->")
ISSUE_PREFIX = "[upstream-sync] "
LEGACY_ISSUE_PREFIX = "[upstream-sync blocked] "
POLICY_PATH = Path(__file__).with_name("upstream_ownership_policy.json")
OWNERSHIP = {"FOLLOW", "REVIEW", "DOWNSTREAM-OWNED"}
EPISODE_MARKER = re.compile(r"<!-- wholphin-upstream-episode:([0-9a-f]{64}) -->")
JOURNAL_MARKER = re.compile(r"<!-- wholphin-upstream-journal:(\{.*?\}) -->")
TERMINAL_MARKER = re.compile(r"<!-- wholphin-upstream-terminal:(\{.*?\}) -->")
RISK_LABELS = {f"risk: {level}" for level in ("low", "medium", "high", "critical")}
DEBT_LABELS = {f"debt: {level}" for level in ("low", "medium", "high", "critical")}
MANAGED_LABELS = RISK_LABELS | DEBT_LABELS | {"attention"}


class Blocked(RuntimeError):
    pass


class IdentityError(Blocked):
    pass


def load_policy(path=POLICY_PATH):
    policy = json.loads(Path(path).read_text(encoding="utf-8"))
    if policy.get("schemaVersion") != 1 or policy.get("defaultAutomationOwnership") != "REVIEW":
        raise IdentityError("Unsupported upstream ownership policy.")
    if not set(policy.get("paths", {}).values()) <= OWNERSHIP:
        raise IdentityError("Unknown upstream ownership classification.")
    return policy


def ownership(path, policy):
    if path in policy["paths"]:
        return policy["paths"][path]
    return "REVIEW" if path.startswith(".github/") else "FOLLOW"


def classify_changes(git, base, up, policy, downstream=None):
    raw = git.run("diff", "--name-status", "-z", "--find-renames", base, up, "--").stdout
    fields = raw.rstrip("\0").split("\0") if raw else []
    result, index = [], 0
    while index < len(fields):
        status = fields[index]
        index += 1
        old = fields[index]
        index += 1
        new = old
        if status.startswith(("R", "C")):
            new = fields[index]
            index += 1
        old_owner, new_owner = ownership(old, policy), ownership(new, policy)
        classification = "REVIEW" if old != new and old_owner != new_owner else new_owner
        if old != new and old_owner != new_owner:
            reason = "rename crosses ownership boundary"
        elif classification == "DOWNSTREAM-OWNED":
            reason = "trusted downstream policy preserves this exact path"
        elif classification == "REVIEW":
            reason = ("trusted downstream policy requires semantic review" if new in policy["paths"]
                      else "unmapped automation path defaults to REVIEW")
        elif new in policy["paths"]:
            reason = "trusted downstream policy follows upstream"
        else:
            reason = "non-automation path follows upstream by default"
        def blob(commit, path):
            value = git.run("rev-parse", f"{commit}:{path}", check=False)
            return value.stdout.strip() if value.returncode == 0 else None
        result.append({"status": status, "old_path": old, "path": new,
                       "old_blob": blob(base, old), "new_blob": blob(up, new),
                       "downstream_blob": blob(downstream or base, new),
                       "downstream_old_blob": blob(downstream or base, old),
                       "old_ownership": old_owner, "new_ownership": new_owner,
                       "ownership": classification,
                       "counterpart": old if old != new else None,
                       "reason": reason,
                       "affects_candidate": classification != "DOWNSTREAM-OWNED"})
    return result


def verify_complete_classification(git, base, upstream, changes):
    """Prove that classification accounts for the complete native upstream range."""
    expected = git.run(
        "diff", "--name-status", "-z", "--find-renames", base, upstream, "--"
    ).stdout
    fields = expected.rstrip("\0").split("\0") if expected else []
    range_rows, index = [], 0
    while index < len(fields):
        status = fields[index]
        index += 1
        old_path = fields[index]
        index += 1
        path = old_path
        if status.startswith(("R", "C")):
            path = fields[index]
            index += 1
        range_rows.append((status, old_path, path))
    classified_rows = [
        (row.get("status"), row.get("old_path"), row.get("path")) for row in changes
    ]
    if classified_rows != range_rows:
        raise Blocked("Complete upstream range classification does not match the Git diff.")
    if any(row.get("ownership") not in OWNERSHIP for row in changes):
        raise Blocked("Complete upstream range contains an unknown ownership classification.")
    return range_rows


def verify_native_merge_candidate(git, candidate, downstream, upstream, tree=None):
    """Authenticate exact native merge parents and, when supplied, its reviewed tree."""
    parents = git.text("show", "-s", "--format=%P", candidate).split()
    candidate_tree = git.text("rev-parse", candidate + "^{tree}")
    if parents != [downstream, upstream]:
        raise Blocked("Native merge candidate does not have the exact trusted parent order.")
    if tree is not None and candidate_tree != tree:
        raise Blocked("Native merge candidate tree differs from the reviewed merge tree.")
    return candidate_tree


def native_merge_candidate(git, downstream, upstream, tree, message):
    """Create and authenticate a deterministic native two-parent merge commit."""
    if git.text("rev-parse", "HEAD") != downstream:
        raise Blocked("Native merge first-parent checkout moved during candidate construction.")
    merge_heads = git.text("rev-parse", "MERGE_HEAD").splitlines()
    if merge_heads != [upstream]:
        raise Blocked("Native merge second parent does not match the trusted upstream tip.")
    if git.text("write-tree") != tree:
        raise Blocked("Native merge index tree changed before candidate construction.")
    candidate = git.run(
        "commit-tree", tree, "-p", downstream, "-p", upstream, input=message
    ).stdout.strip()
    verify_native_merge_candidate(git, candidate, downstream, upstream, tree)
    return candidate


def preserve_downstream_owned(git, downstream, changes):
    for change in changes:
        if change["ownership"] != "DOWNSTREAM-OWNED":
            continue
        # A same-owner rename changes two path states. Restore both the old and
        # new path exactly as downstream records them rather than accepting half
        # of the upstream rename while excluding the other half.
        for path in sorted({change["old_path"], change["path"]}):
            exists = git.run("cat-file", "-e", f"{downstream}:{path}", check=False).returncode == 0
            if exists:
                git.run("checkout", downstream, "--", path)
                git.run("add", "--", path)
            else:
                git.run("rm", "-f", "--ignore-unmatch", "--", path)


def display_text(value):
    return html.escape(str(value)).replace("\r", "\\r").replace("\n", "\\n").replace("@", "&#64;")


def display_markdown_text(value):
    return display_text(value).translate(str.maketrans({
        "[": "&#91;", "]": "&#93;", "(": "&#40;", ")": "&#41;", "`": "&#96;"}))


def parse_time(value):
    if not value:
        return datetime.datetime.now(datetime.timezone.utc)
    parsed = datetime.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=datetime.timezone.utc)


def attention_paths(observation):
    return sorted(set(observation.get("review_paths", [])) | set(observation.get("conflict_paths", [])))


def attention_episode(observation):
    paths = set(attention_paths(observation))
    rows = []
    for change in observation.get("automation_changes", []):
        if change.get("path") in paths:
            rows.append({"path": change.get("path"),
                         "counterpart": change.get("counterpart"),
                         "status": change.get("status"),
                         "ownership": change.get("ownership"),
                         "downstream_blob": change.get("downstream_blob"),
                         "downstream_old_blob": change.get("downstream_old_blob"),
                         "textual_conflict": change.get("path") in observation.get("conflict_paths", [])})
    payload = {"schemaVersion": 1,
               "policyVersion": observation.get("ownership_policy_version"),
               "attention": sorted(rows, key=lambda row: (row["path"] or "", row["ownership"] or ""))}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def observation_identity(observation):
    payload = {key: observation.get(key) for key in
               ("upstream_sha", "downstream_sha", "run_id", "run_attempt", "observed_at")}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def priority_metrics(observation, first_observed=None, latest_observed=None):
    paths = attention_paths(observation)
    first = parse_time(first_observed or observation.get("observed_at"))
    latest = parse_time(latest_observed or observation.get("observed_at"))
    age_seconds = max(0, int((latest - first).total_seconds()))
    age_days = age_seconds / 86400
    churn = max(1, int(observation.get("attention_change_count") or 1)) if paths else 0

    risk_rank = 0 if not paths else 1
    critical_tokens = ("keystore", "signing", "credential", "mosaic-sign-apk")
    high_tokens = (".github/workflows/", "build.gradle", ".proto", "/schemas/", "appdatabase")
    lowered = [path.lower() for path in paths]
    if any(token in path for path in lowered for token in critical_tokens):
        risk_rank = 3
    elif any(token in path for path in lowered for token in high_tokens):
        risk_rank = 2
    if len(paths) >= 5 or churn >= 5:
        risk_rank = min(3, risk_rank + 1)

    debt_points = 0
    if paths:
        clean_count = int(observation.get("clean_path_count") or 0)
        debt_points = 1 + max(0, len(paths) - 1) + max(0, churn - 1) + clean_count // 10
        if age_days >= 3:
            debt_points += 2
        if age_days >= 7:
            debt_points += 3
        if age_days >= 21:
            debt_points += 3
    debt_rank = 0 if debt_points <= 2 else 1 if debt_points <= 4 else 2 if debt_points <= 7 else 3
    levels = ("low", "medium", "high", "critical")
    escalation = ("Attention" if risk_rank == 3 or debt_rank >= 2
                  or (risk_rank >= 2 and age_days >= 3)
                  or (risk_rank >= 1 and age_days >= 7) else "None")
    hours = age_seconds // 3600
    age = f"{max(1, hours)}h" if hours < 24 else f"{int(age_days)}d"
    return {"risk": levels[risk_rank], "debt": levels[debt_rank], "age": age,
            "age_seconds": age_seconds, "escalation": escalation,
            "risk_evidence": {"attentionPaths": len(paths), "attentionCommits": churn,
                              "sensitivePaths": [path for path in paths if any(token in path.lower()
                                                  for token in critical_tokens + high_tokens)]},
            "debt_evidence": {"points": debt_points, "attentionPaths": len(paths),
                              "attentionCommits": churn,
                              "cleanPaths": int(observation.get("clean_path_count") or 0)}}


def priority_title(metrics):
    title = (f"{metrics['risk'].title()} risk \N{MIDDLE DOT} {metrics['debt'].title()} debt \N{MIDDLE DOT} "
             f"{metrics['age']}")
    return title + (" \N{MIDDLE DOT} Attention" if metrics["escalation"] == "Attention" else "")


def finalize_attention(git, observation, base, upstream):
    paths = attention_paths(observation)
    observation["attention_change_count"] = (int(git.text(
        "rev-list", "--count", f"{base}..{upstream}", "--", *paths)) if paths else 0)
    observation["clean_path_count"] = sum(
        change.get("affects_candidate") and change.get("path") not in paths
        for change in observation.get("automation_changes", []))
    if paths:
        observation["episode_id"] = attention_episode(observation)
        observation["priority"] = priority_metrics(observation)


def episode_marker(observation):
    episode = observation.get("episode_id")
    return f"<!-- wholphin-upstream-episode:{episode} -->" if episode else ""


def journal_state_marker(observation):
    if observation.get("episode_id"):
        return episode_marker(observation)
    key = hashlib.sha256(json.dumps({key: observation.get(key) for key in
        ("upstream_sha", "downstream_sha", "ownership_policy_version")}, sort_keys=True).encode()).hexdigest()
    return f"<!-- wholphin-upstream-state:{key} -->"


def pull_episode(pull):
    match = EPISODE_MARKER.search(pull.get("body") or "")
    return match.group(1) if match else None


def is_sync_issue(issue):
    body = issue.get("body") or ""
    return bool(EPISODE_MARKER.search(body) or "<!-- wholphin-upstream-state:" in body
                or issue.get("title", "").startswith((ISSUE_PREFIX, LEGACY_ISSUE_PREFIX)))


def blob_url(repository, sha, path):
    if not sha or not path:
        return None
    return f"https://github.com/{repository}/blob/{sha}/{quote(path, safe='/')}"


def pull_reference_numbers(subject):
    patterns = (
        rf"https?://github\.com/{re.escape(UPSTREAM)}/(?:pull|issues)/(\d+)",
        rf"(?<![\w/]){re.escape(UPSTREAM)}#(\d+)",
        r"(?<![\w/])#(\d+)",
    )
    return list(dict.fromkeys(number for pattern in patterns
                              for number in re.findall(pattern, subject, flags=re.IGNORECASE)))


def quiet_subject(value):
    """Render upstream-controlled text without live URLs, mentions, or issue references."""
    text = str(value or "Untitled upstream commit")
    text = re.sub(r"https?://[^\s<>()]+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(?<![\w/])[\w.-]+/[\w.-]+#\d+", "", text)
    text = re.sub(r"\(?\s*#\d+\s*\)?", "", text)
    text = " ".join(text.split()).strip(" -\N{EM DASH}\N{MIDDLE DOT}()")
    return display_markdown_text(text or "Untitled upstream commit")


def commit_presentation(commit, *, rich_upstream=False):
    sha = commit.get("sha") or ""
    raw_subject = commit.get("subject") or "Untitled upstream commit"
    numbers = commit.get("pull_request_numbers") or pull_reference_numbers(raw_subject)
    short = display_text(sha[:7] or "unknown")
    if rich_upstream:
        subject = display_markdown_text(re.sub(r"\s*\(#\d+\)\s*$", "", raw_subject))
        commit_url = commit.get("url") or (f"https://github.com/{UPSTREAM}/commit/{sha}" if sha else None)
        commit_text = f"[`{short}`]({commit_url})" if commit_url else f"`{short}`"
        references = [f"[PR {number}](https://github.com/{UPSTREAM}/pull/{number})" for number in numbers]
    else:
        subject = quiet_subject(raw_subject)
        commit_text = f"<code>{short}</code>"
        references = [f"PR {display_text(number)}" for number in numbers]
    reference_text = (" ".join(references) + " \N{EM DASH} ") if references else ""
    return f"{reference_text}{subject} \N{MIDDLE DOT} {commit_text}"


def technical_evidence(observation):
    return json.dumps({
        key: observation.get(key) for key in (
            "schema_version", "ownership_policy_version", "episode_id", "upstream_repo",
            "upstream_base_sha", "upstream_sha", "downstream_repo", "downstream_sha",
            "comparison_baseline", "candidate_sha", "candidate_tree", "branch", "outcome",
            "candidate_parents", "classification_range_count", "ownership_counts", "review_paths",
            "conflict_paths", "attention_change_count", "clean_path_count", "priority",
            "configured_schedule_utc", "observed_at", "run_url")
        if observation.get(key) is not None
    }, indent=2, ensure_ascii=True)


def human_evidence(observation, *, issue=False, rich_upstream=False, include_technical=True):
    lines = []
    if issue and observation.get("pr_url"):
        number = observation.get("pr_number", str(observation["pr_url"]).rstrip("/").split("/")[-1])
        lines += [f"Draft PR: [#{number}]({observation['pr_url']})", ""]
    commits = observation.get("incoming_commits", [])
    lines += [f"{len(commits)} incoming", ""]
    lines += [f"- {commit_presentation(commit, rich_upstream=rich_upstream)}"
              for commit in commits[:10]] or ["- None"]
    if len(commits) > 10:
        lines.append(f"- {len(commits) - 10} additional incoming commits are retained in the observation artifact.")
    paths = attention_paths(observation)
    lines += ["", f"{len(paths)} requiring attention", ""]
    changes = {change.get("path"): change for change in observation.get("automation_changes", [])}
    for path in paths:
        change = changes.get(path, {})
        if rich_upstream:
            upstream_side = (f"[Upstream file]({change.get('upstream_url') or blob_url(UPSTREAM, observation.get('upstream_sha'), path)})"
                             if change.get("new_blob") else "upstream absent")
            if change.get("downstream_blob"):
                downstream_side = f"[Mosaic file]({change.get('downstream_url') or blob_url(ORIGIN, observation.get('downstream_sha'), path)})"
            elif change.get("downstream_old_blob") and change.get("counterpart"):
                counterpart = change["counterpart"]
                prior_url = change.get("downstream_old_url") or blob_url(
                    ORIGIN, observation.get("downstream_sha"), counterpart)
                downstream_side = (f"[Mosaic prior path]({prior_url}) "
                                   f"<code>{display_text(counterpart)}</code>")
            else:
                downstream_side = "Mosaic absent"
            lines.append(f"- <code>{display_text(path)}</code> \N{MIDDLE DOT} {upstream_side} | {downstream_side}")
        else:
            lines.append(f"- <code>{display_text(Path(path).name)}</code>")
    if not paths:
        lines.append("- None")
    clean = int(observation.get("clean_path_count") or 0)
    if clean:
        verb = "integrates" if clean == 1 else "integrate"
        lines += ["", f"{clean} additional file{'s' if clean != 1 else ''} {verb} cleanly."]
    if observation.get("run_url"):
        lines += ["", f"Latest observation: [{display_text(observation['run_url'])}]({observation['run_url']})"]
    if observation.get("journal_issue_url") and not issue:
        lines += ["", f"Tracking issue: [{display_text(observation['journal_issue_url'])}]({observation['journal_issue_url']})"]
    if include_technical:
        lines += ["", "<details>", "<summary>Technical evidence</summary>", "", "```json",
                  technical_evidence(observation), "```", "", "</details>"]
        marker = journal_state_marker(observation)
        if marker:
            lines += ["", marker]
        if observation.get("upstream_sha") and observation.get("ancestry_validated"):
            lines += ["", f"<!-- wholphin-upstream-observed:{observation['upstream_sha']} -->"]
    return "\n".join(lines) + "\n"


def journal_metadata(issue):
    match = JOURNAL_MARKER.search((issue or {}).get("body") or "")
    if not match:
        return {}
    try:
        return json.loads(match.group(1))
    except (TypeError, ValueError):
        return {}


def update_observation_history(observation, issue=None):
    prior = journal_metadata(issue)
    observed = observation.get("observed_at") or datetime.datetime.now(datetime.timezone.utc).isoformat()
    identity = observation_identity(observation)
    count = int(prior.get("observationCount") or 0)
    if prior.get("latestObservationId") != identity:
        count += 1
    record = {
        "schemaVersion": 1,
        "episodeId": observation.get("episode_id"),
        "firstObserved": prior.get("firstObserved") or observed,
        "latestObserved": observed,
        "observationCount": count,
        "latestRunUrl": observation.get("run_url"),
        "latestObservationId": identity,
    }
    observation["journal"] = record
    observation["priority"] = priority_metrics(
        observation, record["firstObserved"], record["latestObserved"])
    return record


def issue_body(observation):
    record = observation["journal"]
    metrics = observation["priority"]
    lines = [
        f"Risk: **{metrics['risk'].title()}**",
        f"Integration debt: **{metrics['debt'].title()}**",
        f"Age: **{metrics['age']}**",
        f"Escalation: **{metrics['escalation']}**",
        "",
        f"First observed: `{record['firstObserved']}`",
        f"Latest observed: `{record['latestObserved']}`",
        f"Observations: **{record['observationCount']}**",
    ]
    if observation.get("missing_labels"):
        lines += ["", "Repository labels requiring one-time external creation: " +
                  ", ".join(f"`{display_text(label)}`" for label in observation["missing_labels"])]
    lines += [
        "", human_evidence(observation, issue=True).rstrip(), "",
        f"<!-- wholphin-upstream-journal:{json.dumps(record, sort_keys=True, separators=(',', ':'))} -->",
    ]
    return "\n".join(lines) + "\n"


def issue_labels(issue, observation, available):
    current = {
        label.get("name") if isinstance(label, dict) else label
        for label in (issue or {}).get("labels", [])
    }
    desired = {f"risk: {observation['priority']['risk']}",
               f"debt: {observation['priority']['debt']}"}
    if observation["priority"]["escalation"] == "Attention":
        desired.add("attention")
    observation["missing_labels"] = sorted(desired - available)
    return sorted((current - MANAGED_LABELS) | (desired & available))


def candidate_title(observation, draft):
    if draft:
        names = [quiet_subject(Path(path).name) for path in attention_paths(observation)]
        scope = ", ".join(names[:2])
        if len(names) > 2:
            scope += f" and {len(names) - 2} more"
        return "chore: review upstream changes" + (f" to {scope}" if scope else "")
    return "chore: synchronize official upstream"


def upstream_summary(observation, *, publication=False, operation_error=False):
    outcome = observation['outcome']
    if operation_error or observation.get('record_failure'):
        heading = 'Publication error' if publication else 'Observation error'
    elif outcome in {'blocked', 'semantic_conflict'}:
        heading = 'Blocked · semantic conflicts' if observation.get('textual_conflicts') else 'Blocked · review required'
    else:
        heading = {'no_delta': 'No upstream delta', 'observed_excluded': 'Observed · downstream-owned changes excluded',
                   'ready': 'Ready candidate', 'review_required': 'Review required · Draft candidate',
                   'existing_pr': 'Existing candidate PR', 'existing_draft_pr': 'Existing Draft candidate PR',
                   'pr_created': 'Published candidate PR',
                   'review_pr_created': 'Draft candidate PR created'}.get(outcome, 'Upstream observation')
    # Retain full evidence and escape remote/user-controlled strings. Keep this in
    # the existing protected sync helper rather than adding an executable dependency.
    counts = observation.get('ownership_counts') or {}
    count_text = ''
    if counts:
        count_text = (f"\nUpstream changes: {len(observation.get('automation_changes', []))}\n\n"
                      f"- FOLLOW: {counts.get('FOLLOW', 0)} — normal candidate integration\n"
                      f"- REVIEW: {counts.get('REVIEW', 0)} — semantic/manual review required\n"
                      f"- DOWNSTREAM-OWNED: {counts.get('DOWNSTREAM-OWNED', 0)} — observed, intentionally preserved downstream\n")
        for category in ("FOLLOW", "REVIEW", "DOWNSTREAM-OWNED"):
            rows = [change for change in observation.get("automation_changes", [])
                    if change.get("ownership") == category]
            if rows:
                count_text += f"\n### {category}\n\n"
                for change in rows:
                    path = display_text(change.get("path", "unknown"))
                    reason = display_text(change.get("reason", ""))
                    count_text += f"- <code>{path}</code> — {reason}\n"
        count_text += ("\nConfigured schedule: <code>" + display_text(observation.get("configured_schedule_utc", "unknown")) +
                       "</code>; observed start: <code>" + display_text(observation.get("observed_at", "unknown")) + "</code>.\n")
    navigation = human_evidence(observation, rich_upstream=True, include_technical=False)
    return ('## ' + heading + '\n' + count_text + '\n## Operator navigation\n\n' + navigation +
            '\n## Complete machine evidence\n\n<pre>' +
            html.escape(json.dumps(observation, indent=2, ensure_ascii=True)) + '</pre>\n')


class OperationError(Blocked):
    """Operational failure reported separately from expected blocked states."""


def command(args, *, cwd=None, env=None, check=True, input=None):
    result = subprocess.run(args, cwd=cwd, env=env, input=input,
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace", timeout=180)
    if check and result.returncode:
        # Never echo credentials, untrusted command output, or workflow commands.
        operation = args[1:]
        while operation and operation[0] == "-c":
            operation = operation[2:]
        diagnostic = result.stderr.lower() if isinstance(result.stderr, str) else ""
        category = ("permission_denied" if "403" in diagnostic or "permission" in diagnostic
                    else "rate_limited" if "rate limit" in diagnostic or "429" in diagnostic
                    else "not_found" if "404" in diagnostic or "not found" in diagnostic
                    else "transient_network" if any(value in diagnostic for value in ("timeout", "timed out", "502", "503", "504"))
                    else "operation_failed")
        raise OperationError(f"{category}: {args[0]} {operation[0] if operation else 'operation'} failed (exit {result.returncode}); inspect permissions/connectivity and rerun.")
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

    def api(self, endpoint, payload=None, publish=False, method="POST"):
        args = ["gh", "api", "--hostname", "github.com", endpoint]
        if payload is not None:
            args += ["--method", method, "--input", "-"]
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
                if "pull_request" not in i and is_sync_issue(i)]

    def labels(self):
        return {label["name"] for label in self.pages("labels?per_page=100")}

    def create_pr(self, branch, body, *, draft=False, title=None):
        return self.api(f"repos/{ORIGIN}/pulls", {
            "head": branch, "base": "main", "title": title or "chore: synchronize official upstream",
            "body": body, "maintainer_can_modify": False, "draft": draft}, publish=True)["html_url"]

    def journal_issue(self, observation):
        if self.api(f"repos/{ORIGIN}").get("has_issues") is not True:
            raise Blocked("Repository Issues are disabled; enable Issues externally to retain the required blocked-sync issue. No App credential change is indicated.")
        marker = journal_state_marker(observation)
        issues = self.issues()
        existing = None
        for issue in issues:
            if marker in (issue.get("body") or ""):
                existing = issue
                break
        if existing and existing.get("state") != "open":
            observation["journal_closed"] = True
            if observation.get("episode_id"):
                observation["human_disposition"] = f"Issue #{existing['number']} is closed and will not be reopened automatically."
            return existing
        update_observation_history(observation, existing)
        available = self.labels()
        labels = issue_labels(existing, observation, available)
        title = (priority_title(observation["priority"])
                 if observation.get("episode_id")
                 else "Upstream integration journal")
        body = issue_body(observation)
        if existing:
            return self.api(f"repos/{ORIGIN}/issues/{int(existing['number'])}",
                            {"title": title, "body": body, "labels": labels}, method="PATCH")
        for issue in issues:
            if issue.get("state") == "open" and is_sync_issue(issue):
                prior = issue.get("body") or ""
                note = f"\n\nSuperseded by upstream state `{observation.get('upstream_sha')}` under policy v{observation.get('ownership_policy_version')}.\n"
                self.api(f"repos/{ORIGIN}/issues/{int(issue['number'])}",
                         {"body": prior + note, "state": "closed"}, method="PATCH")
        return self.api(f"repos/{ORIGIN}/issues", {
            "title": title, "body": body, "labels": labels})

    def update_journal(self, issue, observation, *, close=False):
        if issue.get("state") != "open" and not close:
            return issue
        if not observation.get("journal"):
            update_observation_history(observation, issue)
        labels = issue_labels(issue, observation, self.labels())
        payload = {"title": (priority_title(observation["priority"])
                   if observation.get("episode_id") else "Upstream integration journal"),
                   "body": issue_body(observation),
                   "labels": labels}
        if close:
            payload["state"] = "closed"
        return self.api(f"repos/{ORIGIN}/issues/{int(issue['number'])}", payload, method="PATCH")

    def blocked_issue(self, observation):
        """Legacy test/exception compatibility; new publication uses journal_issue."""
        return self.journal_issue(observation)["html_url"]


def finalize_merged_episode(github, pr_number):
    """Close the exact linked journal after its downstream candidate PR is merged."""
    pr = github.api(f"repos/{ORIGIN}/pulls/{int(pr_number)}")
    head = pr.get("head") or {}
    base = pr.get("base") or {}
    head_repo = (head.get("repo") or {}).get("full_name")
    base_repo = (base.get("repo") or {}).get("full_name")
    episode = pull_episode(pr)
    branch = head.get("ref") or ""
    merge_sha = pr.get("merge_commit_sha") or ""
    if (int(pr.get("number") or 0) != int(pr_number)
            or pr.get("state") != "closed" or not pr.get("merged_at")
            or base.get("ref") != "main" or base_repo != ORIGIN
            or head_repo != ORIGIN or not BRANCH.fullmatch(branch)
            or not episode or not re.fullmatch(r"[0-9a-f]{40}", merge_sha)):
        raise Blocked("Merged PR does not authenticate as the exact downstream I06 candidate.")

    marker_text = f"<!-- wholphin-upstream-episode:{episode} -->"
    issues = [issue for issue in github.issues() if marker_text in (issue.get("body") or "")]
    if len(issues) != 1:
        raise Blocked(f"Expected exactly one journal for merged I06 episode; found {len(issues)}.")
    issue = issues[0]
    terminal = {
        "episodeId": episode,
        "issueNumber": int(issue["number"]),
        "mergeCommitSha": merge_sha,
        "mergedAt": pr["merged_at"],
        "prNumber": int(pr_number),
        "schemaVersion": 1,
    }
    existing = TERMINAL_MARKER.search(issue.get("body") or "")
    if existing:
        try:
            recorded = json.loads(existing.group(1))
        except ValueError as exc:
            raise Blocked("Merged journal contains unreadable terminal identity.") from exc
        if recorded != terminal or issue.get("state") != "closed":
            raise Blocked("Merged journal terminal identity differs from the current PR event.")
        return {**terminal, "outcome": "journal_already_closed"}
    if issue.get("state") != "open":
        raise Blocked("Linked journal was already closed without this merged-PR terminal record.")

    prior_body = issue.get("body") or ""
    pr_url = f"https://github.com/{ORIGIN}/pull/{int(pr_number)}"
    commit_url = f"https://github.com/{ORIGIN}/commit/{merge_sha}"
    body = (
        "## Resolved upstream integration\n\n"
        "Status: **Merged**\n\n"
        f"- Downstream PR: [#{int(pr_number)}]({pr_url})\n"
        f"- Downstream merge: [`{merge_sha[:12]}`]({commit_url})\n"
        f"- Merged at: `{pr['merged_at']}`\n\n"
        "## Observation history\n\n" + prior_body.rstrip() + "\n\n"
        f"<!-- wholphin-upstream-terminal:{json.dumps(terminal, sort_keys=True, separators=(',', ':'))} -->\n"
    )
    current_labels = {
        label.get("name") if isinstance(label, dict) else label
        for label in issue.get("labels", [])
    }
    github.api(
        f"repos/{ORIGIN}/issues/{int(issue['number'])}",
        {
            "title": "Resolved · merged upstream integration",
            "body": body,
            "labels": sorted(current_labels - MANAGED_LABELS),
            "state": "closed",
            "state_reason": "completed",
        },
        method="PATCH",
    )
    return {**terminal, "outcome": "journal_closed_merged"}


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


def blocked_workspace_matches(git, candidate, upstream, downstream, policy_version):
    parents = git.text("show", "-s", "--format=%P", candidate).split()
    context = git.run("show", candidate + ":.upstream-sync/blocked-context.json", check=False)
    if parents != [downstream] or context.returncode:
        return False
    try:
        record = json.loads(context.stdout)
    except (TypeError, ValueError):
        return False
    return (record.get("schemaVersion") == 1
            and record.get("upstream") == upstream
            and record.get("downstream") == downstream
            and record.get("policyVersion") == policy_version
            and isinstance(record.get("conflicts"), list)
            and bool(record["conflicts"]))


def existing_candidate(pulls, observation, candidate):
    same = [pull for pull in pulls if pull["head"]["ref"] == observation["branch"]]
    if len(same) > 1 or (same and same[0]["state"] != "open"):
        raise Blocked("This exact SHA pair has a closed or ambiguous PR decision; do not automatically reopen or recreate it.")
    if same:
        if same[0]["head"]["sha"] != candidate:
            raise Blocked("Existing PR head differs from the deterministic candidate; preserve human changes.")
        if observation.get("episode_id") and not same[0].get("draft"):
            raise Blocked("Attention-required candidate is no longer Draft; preserve the human PR decision.")
        observation.update(outcome="existing_draft_pr" if same[0].get("draft") else "existing_pr",
                           pr_url=same[0]["html_url"], pr_number=same[0]["number"])
        return True
    if observation.get("episode_id"):
        episode = [pull for pull in pulls if pull_episode(pull) == observation["episode_id"]]
        open_episode = [pull for pull in episode if pull["state"] == "open"]
        if len(open_episode) > 1:
            raise Blocked("Multiple Draft PRs represent one unresolved upstream episode; inspect without mutation.")
        if open_episode:
            pull = open_episode[0]
            if not pull.get("draft"):
                raise Blocked("The unresolved episode PR is no longer Draft; preserve the human PR decision.")
            observation.update(outcome="existing_draft_pr", pr_url=pull["html_url"],
                               pr_number=pull["number"], existing_branch=pull["head"]["ref"])
            return True
        if episode:
            raise Blocked("The unresolved episode has a closed PR decision; do not automatically reopen or recreate it.")
    others = [pull for pull in pulls if pull["state"] == "open"]
    if others:
        observation["existing_pr_url"] = others[0]["html_url"]
        raise Blocked("Another sync PR is open; review/merge or deliberately close it before a new proposal. History was not overwritten.")
    return False


def inspect(git, github, observation, anchor=INITIAL_ANCHOR):
    git.identities()
    git.fetch("origin", "refs/heads/main", "refs/remotes/origin/main")
    git.fetch("upstream", "refs/heads/main", "refs/remotes/upstream/main")
    down = git.text("rev-parse", "refs/remotes/origin/main")
    up = git.text("rev-parse", "refs/remotes/upstream/main")
    policy = load_policy()
    observation.update(upstream_sha=up, downstream_sha=down, branch=branch_name(up, down),
                       ownership_policy_version=policy["schemaVersion"])
    if not git.ancestor(anchor, down):
        raise Blocked("Downstream no longer contains the reviewed initial upstream anchor; inspect main history.")
    # Native ancestry is the canonical accepted-range fact. Historical candidate
    # branches and journal records are irrelevant once current upstream is
    # already contained by current downstream main.
    if git.ancestor(up, down):
        observation.update(outcome="no_delta", comparison_baseline=up, upstream_base_sha=up,
                           incoming_count=0, incoming_commits=[], changed_paths=[], conflict_paths=[])
        observation["ancestry_validated"] = True
        return
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
            try:
                verify_native_merge_candidate(git, destination, match[2], match[1])
                normal = True
            except Blocked:
                normal = False
            blocked = blocked_workspace_matches(git, destination, match[1], match[2], policy["schemaVersion"])
            if not normal and not blocked:
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
    bases = git.text("merge-base", "--all", down, up).splitlines()
    if len(bases) != 1:
        raise Blocked("Expected one common comparison baseline; inspect unrelated/criss-cross history.")
    base = bases[0]
    observation.update(comparison_baseline=base, upstream_base_sha=base)
    commits = git.text("rev-list", "--reverse", f"{down}..{up}").splitlines()
    observation["incoming_commits"] = []
    for sha in commits:
        subject = git.text("show", "-s", "--format=%s", sha)
        numbers = pull_reference_numbers(subject)
        observation["incoming_commits"].append({
            "sha": sha,
            "subject": subject,
            "url": f"https://github.com/{UPSTREAM}/commit/{sha}",
            "pull_request_numbers": numbers,
            "pull_request_urls": [f"https://github.com/{UPSTREAM}/pull/{number}" for number in numbers],
        })
    observation["automation_changes"] = classify_changes(git, base, up, policy, down)
    classified_range = verify_complete_classification(
        git, base, up, observation["automation_changes"]
    )
    observation["classification_range_count"] = len(classified_range)
    for change in observation["automation_changes"]:
        path = change["path"]
        counterpart = change.get("counterpart")
        change["upstream_url"] = blob_url(UPSTREAM, up, path) if change.get("new_blob") else None
        change["downstream_url"] = blob_url(ORIGIN, down, path) if change.get("downstream_blob") else None
        change["downstream_old_url"] = (blob_url(ORIGIN, down, counterpart)
                                         if counterpart and change.get("downstream_old_blob") else None)
    observation["changed_paths"] = [row["path"] for row in observation["automation_changes"]]
    observation["incoming_count"] = len(commits)
    counts = {name: sum(row["ownership"] == name for row in observation["automation_changes"])
              for name in sorted(OWNERSHIP)}
    observation["ownership_counts"] = counts
    if observation["automation_changes"] and all(not row["affects_candidate"] for row in observation["automation_changes"]):
        observation.update(outcome="observed_excluded", conflict_paths=[], textual_conflicts=False,
                           reason="All changed paths were observed and explicitly preserved as downstream-owned.")
        return
    # Merge occurs only in this process-owned temporary checkout. No hooks,
    # filters, application scripts, local actions, or builds are invoked.
    git.run("checkout", "--quiet", "--detach", down)
    git.env.update(GIT_AUTHOR_NAME="github-actions[bot]", GIT_COMMITTER_NAME="github-actions[bot]",
                   GIT_AUTHOR_EMAIL="41898282+github-actions[bot]@users.noreply.github.com",
                   GIT_COMMITTER_EMAIL="41898282+github-actions[bot]@users.noreply.github.com")
    merge = git.run("merge", "--no-ff", "--no-commit", up, check=False)
    preserve_downstream_owned(git, down, observation["automation_changes"])
    conflicts = git.run("diff", "--name-only", "--diff-filter=U", "-z").stdout.rstrip("\0")
    observation["conflict_paths"] = conflicts.split("\0") if conflicts else []
    observation["textual_conflicts"] = bool(conflicts)
    if conflicts:
        # Produce a reviewable, single-parent workspace: retain downstream bytes for
        # every unresolved path and add deterministic context. Never claim upstream ancestry.
        for path in observation["conflict_paths"]:
            if git.run("cat-file", "-e", f"{down}:{path}", check=False).returncode == 0:
                git.run("checkout", down, "--", path)
                git.run("add", "--", path)
            else:
                git.run("rm", "-f", "--ignore-unmatch", "--", path)
        context_path = git.path / ".upstream-sync" / "blocked-context.json"
        context_path.parent.mkdir(parents=True, exist_ok=True)
        context_path.write_text(json.dumps({"schemaVersion": 1, "upstream": up,
            "downstream": down, "mergeBase": base, "conflicts": observation["conflict_paths"],
            "policyVersion": policy["schemaVersion"]}, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        git.run("add", "--", ".upstream-sync/blocked-context.json")
        tree = git.text("write-tree")
        timestamp = max(int(git.text("show", "-s", "--format=%ct", s)) for s in (up, down))
        git.env.update(GIT_AUTHOR_DATE=f"{timestamp} +0000", GIT_COMMITTER_DATE=f"{timestamp} +0000")
        message = f"Prepare semantic upstream review {up} against {down}\n\nNo upstream ancestry accepted.\n"
        candidate = git.run("commit-tree", tree, "-p", down, input=message).stdout.strip()
        observation.update(candidate_sha=candidate, candidate_tree=tree,
                           outcome="semantic_conflict",
                           status="Blocked — semantic integration required",
                           reason="Textual conflicts require human semantic resolution; upstream ancestry was not accepted.")
        observation["review_paths"] = sorted(set(observation["conflict_paths"]) | {
            row["path"] for row in observation["automation_changes"] if row["ownership"] == "REVIEW"})
        finalize_attention(git, observation, base, up)
        description(observation)
        existing_candidate(pulls, observation, candidate)
        return
    if merge.returncode:
        raise Blocked("Normal integration failed before publication.")
    git.run("diff", "--cached", "--check")
    tree = git.text("write-tree")
    review = [row["path"] for row in observation["automation_changes"] if row["ownership"] == "REVIEW"]
    owned = [row["path"] for row in observation["automation_changes"] if row["ownership"] == "DOWNSTREAM-OWNED"]
    followed_automation = [row["path"] for row in observation["automation_changes"]
                           if row["ownership"] == "FOLLOW" and row["path"].startswith(".github/")]
    if owned and followed_automation:
        review += followed_automation
        observation["cross_file_review"] = "FOLLOW automation changed beside preserved downstream-owned automation; inspect dependencies."
    review = sorted(set(review))
    observation["review_paths"] = review
    timestamp = max(int(git.text("show", "-s", "--format=%ct", s)) for s in (up, down))
    git.env.update(GIT_AUTHOR_DATE=f"{timestamp} +0000", GIT_COMMITTER_DATE=f"{timestamp} +0000")
    message = f"Merge official upstream {up} into downstream {down}\n\nWholphin-Upstream: {up}\nWholphin-Downstream: {down}\n"
    candidate = native_merge_candidate(git, down, up, tree, message)
    observation.update(candidate_sha=candidate, candidate_tree=tree,
                       candidate_parents=[down, up],
                       outcome="review_required" if review else "ready",
                       status="Review required" if review else "Candidate ready")
    finalize_attention(git, observation, base, up)
    description(observation)  # Check durable PR metadata fits before any push.
    existing_candidate(pulls, observation, candidate)


def publish(git, github, observation, expected_up, expected_down):
    if (observation.get("upstream_sha"), observation.get("downstream_sha")) != (expected_up, expected_down):
        raise Blocked("Refs changed between read and publish jobs; rerun to observe current inputs.")
    if observation["outcome"] in {"no_delta", "observed_excluded"}:
        return
    journal = None
    try:
        journal = github.journal_issue(observation)
        observation["journal_issue_url"] = journal["html_url"]
    except (Blocked, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        observation["journal_warning"] = "Durable journal update failed; candidate processing continued. " + str(exc)
    if observation.get("human_disposition"):
        raise Blocked(observation["human_disposition"])
    if observation.get("journal_closed"):
        if observation["outcome"] == "existing_pr":
            return
        raise Blocked("The matching journal is closed and will not be reopened automatically.")
    if observation["outcome"] in {"existing_pr", "existing_draft_pr"}:
        if journal and observation["outcome"] == "existing_pr":
            try:
                github.update_journal(journal, observation, close=observation["outcome"] == "existing_pr")
            except (Blocked, OSError, ValueError, subprocess.TimeoutExpired) as exc:
                observation["journal_warning"] = "Candidate PR exists, but journal closure failed. " + str(exc)
        return
    if observation["outcome"] not in {"ready", "review_required", "semantic_conflict"}:
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
            observation.update(outcome="existing_draft_pr" if matching[0].get("draft") else "existing_pr",
                               pr_url=matching[0]["html_url"])
            if journal:
                try:
                    github.update_journal(journal, observation, close=not matching[0].get("draft"))
                except (Blocked, OSError, ValueError, subprocess.TimeoutExpired) as exc:
                    observation["journal_warning"] = "Candidate PR exists, but journal closure failed. " + str(exc)
            return
        raise Blocked("PR decision changed before publication; human review required.")
    episode_matching = [p for p in pulls if p["state"] == "open"
                        and observation.get("episode_id")
                        and pull_episode(p) == observation["episode_id"]]
    if episode_matching:
        if len(episode_matching) == 1 and episode_matching[0].get("draft"):
            observation.update(outcome="existing_draft_pr", pr_url=episode_matching[0]["html_url"],
                               pr_number=episode_matching[0]["number"])
            if journal:
                github.update_journal(journal, observation, close=False)
            return
        raise Blocked("The unresolved episode PR changed before publication; human review required.")
    if any(p["state"] == "open" for p in pulls):
        raise Blocked("Another sync PR appeared before publication; rerun after review.")
    if not current:
        git.push(branch, candidate)
    published = git.text("ls-remote", "--refs", "origin", "refs/heads/" + branch).split()
    if not published or published[0] != candidate:
        raise Blocked("Published branch identity could not be verified; preserve it and inspect the remote.")
    prior_outcome = observation["outcome"]
    draft = prior_outcome in {"review_required", "semantic_conflict"}
    observation["pr_url"] = github.create_pr(
        branch, description(observation), draft=draft,
        title=candidate_title(observation, draft))
    observation["pr_number"] = str(observation["pr_url"]).rstrip("/").split("/")[-1]
    observation["outcome"] = ("blocked" if prior_outcome == "semantic_conflict"
                              else "review_pr_created" if draft else "pr_created")
    if journal:
        try:
            github.update_journal(journal, observation, close=not draft)
        except (Blocked, OSError, ValueError, subprocess.TimeoutExpired) as exc:
            observation["journal_warning"] = "Candidate PR was created, but journal update failed. " + str(exc)


def description(o):
    heading = ("## Draft upstream integration requiring semantic review" if attention_paths(o)
               else "## Official upstream integration")
    lines = [heading, "", human_evidence(o).rstrip(), "",
             "Human review and merge/reject remain required. No automatic semantic resolution or merge is performed."]
    body = "\n".join(lines)
    # Full structured evidence remains in the retained observation artifact. The
    # bounded technical section keeps durable identity without making it the
    # primary human view; oversized proposals still fail closed.
    if len(body.encode("utf-8")) > 55000:
        raise Blocked("Evidence exceeds one durable GitHub body; split/review this integration manually.")
    return body + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--expected-upstream", default="")
    parser.add_argument("--expected-downstream", default="")
    parser.add_argument("--finalize-merged-pr", action="store_true")
    parser.add_argument("--pr-number", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.finalize_merged_pr:
        result = {"schema_version": 1, "downstream_repo": ORIGIN,
                  "pr_number": args.pr_number, "outcome": "blocked"}
        failed = False
        try:
            if (os.environ.get("GITHUB_ACTIONS") != "true"
                    or os.environ.get("GITHUB_REPOSITORY") != ORIGIN
                    or os.environ.get("GITHUB_REF") != "refs/heads/main"
                    or os.environ.get("GITHUB_EVENT_NAME") != "pull_request"
                    or not args.pr_number or args.pr_number <= 0):
                raise IdentityError("Merged-journal finalization requires the canonical downstream pull_request event on main.")
            result.update(finalize_merged_episode(GitHub(), args.pr_number))
        except (Blocked, OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
            failed = True
            result.update(outcome="blocked", reason=str(exc))
        finally:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
            if os.environ.get("GITHUB_STEP_SUMMARY"):
                with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as stream:
                    if failed:
                        stream.write("## Merged upstream journal finalization blocked\n\n" +
                                     html.escape(result.get("reason", "Unknown refusal")) + "\n")
                    else:
                        stream.write(f"## Upstream episode resolved\n\nPR #{args.pr_number}: {result['outcome']}.\n")
        return 1 if failed else 0
    o = {"schema_version": 1, "upstream_repo": UPSTREAM, "upstream_ref": "refs/heads/main",
         "downstream_repo": ORIGIN, "downstream_ref": "refs/heads/main",
         "observed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
         "configured_schedule_utc": os.environ.get("CONFIGURED_SCHEDULE") or "manual",
         "workflow": os.environ.get("GITHUB_WORKFLOW"), "run_id": os.environ.get("GITHUB_RUN_ID"),
         "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
         "run_url": f"https://github.com/{ORIGIN}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}",
         "outcome": "blocked", "textual_conflicts": None}
    github = GitHub()
    identity_valid = False
    operation_error = False
    failed = False
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
        failed = True
        operation_error = isinstance(exc, OperationError) or not isinstance(exc, Blocked)
        outcome = ("publication_error" if args.publish else "infrastructure_error") if operation_error else "blocked"
        o.update(outcome=outcome, reason=str(exc) if isinstance(exc, Blocked) else f"{type(exc).__name__}: hosted operation failed; inspect permissions/input and rerun.")
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
        if failed or o.get("record_failure"):
            detail = o.get("record_failure") or o.get("reason") or "Unknown hosted refusal"
            print(f"hosted-upstream: {o.get('outcome', 'blocked')}: {detail}", file=sys.stderr)
    return 1 if failed or o.get("record_failure") else 0


if __name__ == "__main__":
    raise SystemExit(main())
