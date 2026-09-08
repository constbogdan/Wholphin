"""Source-derived Mosaic versions; publication eligibility is opt-in and fail-closed."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

EPOCH = "bc13bf8fdb360c90b44ca0cc85802fa796d3bd08"
UPSTREAM_BASELINE = "1778bdb34caa699c0590232a7de709a889839765"


def git(root, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    result = subprocess.run(["git", *args], cwd=root, env=env, text=True,
                            capture_output=True, encoding="utf-8", timeout=60)
    if result.returncode:
        raise ValueError("Mosaic version requires complete Git history: git " + args[0] + " failed")
    return result.stdout.strip()


def allocate(root, publication=False, epoch=EPOCH):
    if git(root, "rev-parse", "--is-shallow-repository") != "false":
        raise ValueError("Mosaic version requires full Git history; use fetch-depth: 0")
    source = git(root, "rev-parse", "HEAD")
    chain = git(root, "rev-list", "--first-parent", "HEAD").splitlines()
    if epoch not in chain:
        raise ValueError("Mosaic epoch is missing from the first-parent chain; do not reset the epoch")
    number = chain.index(epoch)
    if number > 2100000000:
        raise ValueError("Mosaic versionCode exhausted")
    dirty = bool(git(root, "status", "--porcelain", "--untracked-files=normal"))
    if publication:
        expected = {"GITHUB_ACTIONS": "true", "GITHUB_REPOSITORY": "constbogdan/Wholphin",
                    "GITHUB_REF": "refs/heads/main", "GITHUB_EVENT_NAME": "push",
                    "GITHUB_SHA": source}
        if any(os.environ.get(k) != v for k, v in expected.items()) or dirty or number < 1:
            raise ValueError("Publishable Mosaic version requires a clean exact GitHub push/main checkout after the epoch")
    # The epoch itself is a development bootstrap, never a publishable code 1.
    return {"versionCode": max(1, number), "versionName": f"1.0.{number}",
            "sourceSha": source, "sourceTree": git(root, "rev-parse", "HEAD^{tree}"),
            "buildTime": int(git(root, "show", "-s", "--format=%ct", "HEAD")) * 1000,
            "dirty": dirty, "publication": publication, "epoch": epoch,
            "upstreamBaseline": UPSTREAM_BASELINE}


def artifact_record(identity, apk):
    if not identity["publication"] or identity["dirty"]:
        raise ValueError("Artifact identity requires a publishable source identity")
    return {**identity, "apkSha256": hashlib.sha256(Path(apk).read_bytes()).hexdigest()}


def verify_record(candidate, published):
    if candidate != published:
        raise ValueError("Published Mosaic identity cannot be reused for different bytes or provenance")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publication", action="store_true")
    parser.add_argument("--apk", type=Path)
    parser.add_argument("--published-record", type=Path)
    args = parser.parse_args()
    try:
        identity = allocate(Path(__file__).resolve().parent.parent, args.publication)
        if args.published_record and not args.apk:
            raise ValueError("--published-record requires --apk")
        if args.apk:
            identity = artifact_record(identity, args.apk)
        if args.published_record:
            verify_record(identity, json.loads(args.published_record.read_text()))
        print(json.dumps(identity, sort_keys=True))
    except ValueError as error:
        parser.exit(1, str(error) + "\n")
