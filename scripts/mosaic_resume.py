"""Manual artifact recovery using current protected-main tooling, never old source execution."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re

from mosaic_version import EPOCH, UPSTREAM_BASELINE, git
from mosaic_signing_exercise import artifact_name, payload, validate_record
from mosaic_development_release import (GitHub, REPOSITORY, WORKFLOW, MANIFEST_NAME,
                                        canonical, trusted_ci, verified_manifest, publish)

RESUME_WORKFLOW = '.github/workflows/mosaic-development-resume.yml'


def guard(env):
    for key, value in dict(GITHUB_ACTIONS='true', GITHUB_REPOSITORY=REPOSITORY,
                          GITHUB_REF='refs/heads/main', GITHUB_REF_PROTECTED='true',
                          GITHUB_EVENT_NAME='workflow_dispatch').items():
        if env.get(key) != value:
            raise ValueError('Recovery requires a protected-main manual dispatch')
    if (not re.fullmatch('[0-9a-f]{40}', env.get('GITHUB_SHA', ''))
            or env.get('MOSAIC_EXERCISE_SHA') != env['GITHUB_SHA']
            or env.get('GITHUB_WORKFLOW_REF') != f'{REPOSITORY}/{RESUME_WORKFLOW}@refs/heads/main'
            or not re.fullmatch('[0-9a-f]{40}', env.get('MOSAIC_SOURCE_SHA', ''))
            or not re.fullmatch('[1-9][0-9]*', env.get('MOSAIC_ARTIFACT_ID', ''))
            or env.get('MOSAIC_CHECKPOINT') not in ('unsigned', 'signed')):
        raise ValueError('Invalid exact recovery authorization')


def historical_identity(root, source, execution_sha):
    if git(root, 'rev-parse', '--is-shallow-repository') != 'false':
        raise ValueError('Recovery requires full history')
    if git(root, 'rev-parse', 'HEAD') != execution_sha or git(root, 'status', '--porcelain', '--untracked-files=normal'):
        raise ValueError('Recovery tooling checkout must be clean and exact')
    chain = git(root, 'rev-list', '--first-parent', 'HEAD').splitlines()
    if source not in chain or EPOCH not in chain or chain.index(source) >= chain.index(EPOCH):
        raise ValueError('Source is not a publishable protected-main first-parent ancestor')
    number = chain.index(EPOCH) - chain.index(source)
    if not 1 <= number <= 2100000000:
        raise ValueError('Invalid historical version allocation')
    return dict(versionCode=number, versionName=f'1.0.{number}', sourceSha=source,
                sourceTree=git(root, 'rev-parse', source + '^{tree}'),
                buildTime=int(git(root, 'show', '-s', '--format=%ct', source)) * 1000,
                dirty=False, publication=True, epoch=EPOCH, upstreamBaseline=UPSTREAM_BASELINE)


def run_identity(run, sha, workflow):
    if (run.get('repository', {}).get('full_name') != REPOSITORY
            or run.get('head_repository', {}).get('full_name') != REPOSITORY
            or run.get('event') not in (('workflow_dispatch', 'workflow_run') if workflow == WORKFLOW else ('workflow_dispatch',))
            or run.get('head_branch') != 'main'
            or run.get('head_sha') != sha or run.get('path') != workflow
            or run.get('status') != 'completed'):
        raise ValueError('Untrusted artifact-producing workflow/run')


def successful_job(api, run, attempt, names):
    jobs = api.pages(f"actions/runs/{run}/attempts/{attempt}/jobs", 'jobs')
    matches = [j for j in jobs if j.get('name') in names]
    if len(matches) != 1 or matches[0].get('status') != 'completed' or matches[0].get('conclusion') != 'success':
        raise ValueError('Artifact-producing job did not succeed in the original attempt')
    return matches[0]


def artifact_metadata(api, artifact_id, identity, checkpoint, chain):
    a = api.call('GET', f'actions/artifacts/{artifact_id}')
    owner = a.get('workflow_run', {})
    if (str(a.get('id')) != str(artifact_id) or a.get('expired') is not False
            or not re.fullmatch('sha256:[0-9a-f]{64}', str(a.get('digest', '')))
            or owner.get('repository_id') != owner.get('head_repository_id')
            or owner.get('head_branch') != 'main'):
        raise ValueError('Artifact missing, expired, foreign or without a digest')
    run_id = str(owner['id'])
    run = api.call('GET', f'actions/runs/{run_id}')
    if owner.get('head_sha') != run.get('head_sha'):
        raise ValueError('Artifact/run source mismatch')
    match = re.search(r'-attempt-([1-9][0-9]*)$', a.get('name', ''))
    if not match:
        raise ValueError('Missing original artifact attempt')
    attempt = match[1]
    if int(attempt) > run.get('run_attempt', 0):
        raise ValueError('Invalid artifact attempt')
    if run.get('path') == WORKFLOW:
        run_identity(run, identity['sourceSha'], WORKFLOW)
        expected = checkpoint + '-' + artifact_name(identity, run_id, attempt)
        names = ['build'] if checkpoint == 'unsigned' else ['sign', 'sign / sign']
    elif checkpoint == 'signed' and run.get('path') == RESUME_WORKFLOW and run.get('head_sha') in chain:
        run_identity(run, run['head_sha'], RESUME_WORKFLOW)
        expected = f"signed-mosaic-resume-{identity['sourceSha']}-run-{run_id}-attempt-{attempt}"
        names = ['sign']
    else:
        raise ValueError('Artifact is not from an approved development build/sign checkpoint')
    if a['name'] != expected:
        raise ValueError('Artifact name/source/run identity mismatch')
    job = successful_job(api, run_id, attempt, names)
    if not (datetime.fromisoformat(job['started_at']) <= datetime.fromisoformat(a['created_at']) <= datetime.fromisoformat(job['completed_at'])):
        raise ValueError('Artifact was not created during the successful producing job')
    return a


def validate_original_source(api, record, identity):
    run, attempt = record.get('runId', ''), record.get('runAttempt', '')
    if not all(re.fullmatch('[1-9][0-9]*', str(v)) for v in (run, attempt)):
        raise ValueError('Missing original build identity')
    original = api.call('GET', f'actions/runs/{run}')
    run_identity(original, identity['sourceSha'], WORKFLOW)
    successful_job(api, run, attempt, ['build'])
    expected = dict(identity, apkSha256=record.get('apkSha256'), runId=run, runAttempt=attempt)
    if record != expected or not re.fullmatch('[0-9a-f]{64}', record.get('apkSha256', '')):
        raise ValueError('Original source provenance mismatch')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['metadata', 'check', 'manifest', 'publish'])
    parser.add_argument('--directory', type=Path)
    args = parser.parse_args()
    try:
        env = os.environ
        guard(env)
        root = Path(__file__).resolve().parent.parent
        identity = historical_identity(root, env['MOSAIC_SOURCE_SHA'], env['GITHUB_SHA'])
        api = GitHub()
        # Current trusted orchestration and original source both require authoritative CI.
        trusted_ci(api, env['GITHUB_SHA'])
        trusted_ci(api, identity['sourceSha'], require_tip=False)
        chain = git(root, 'rev-list', '--first-parent', 'HEAD').splitlines()
        a = artifact_metadata(api, env['MOSAIC_ARTIFACT_ID'], identity, env['MOSAIC_CHECKPOINT'], chain)
        if args.mode == 'metadata':
            with open(env['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
                output.write(f"run_id={a['workflow_run']['id']}\n")
            print(json.dumps(dict(artifactId=a['id'], digest=a['digest'], originalRun=a['workflow_run']['id']), sort_keys=True))
            return
        directory = args.directory
        if args.mode == 'check':
            if env['MOSAIC_CHECKPOINT'] == 'unsigned':
                record = json.loads((directory / 'provenance.json').read_text())
                validate_original_source(api, record, identity)
                if str(a['workflow_run']['id']) != record['runId'] or not a['name'].endswith('-attempt-' + record['runAttempt']):
                    raise ValueError('Unsigned record differs from producing artifact run/attempt')
                validate_record(record, identity, directory / 'unsigned.apk', record['runId'], record['runAttempt'])
                if b'APK Sig Block 42' in (directory / 'unsigned.apk').read_bytes():
                    raise ValueError('Expected unsigned APK')
                payload(directory / 'unsigned.apk')
            else:
                record = json.loads((directory / 'verification.json').read_text())
                validate_original_source(api, record['source'], identity)
                if a['name'].startswith('signed-mosaic-signing-exercise-') and (
                        str(a['workflow_run']['id']) != record['source']['runId']
                        or not a['name'].endswith('-attempt-' + record['source']['runAttempt'])):
                    raise ValueError('Signed record differs from original artifact run/attempt')
                # SDK verification follows in a separate public workflow step.
                (directory / 'provenance.json').write_bytes(canonical(record['source']))
            return
        record = json.loads((directory / 'verification.json').read_text())
        validate_original_source(api, record['source'], identity)
        apk = (directory / 'Mosaic-release.apk').read_bytes()
        m = verified_manifest(record, apk, identity, record['source']['runId'], record['source']['runAttempt'],
                              json.loads((root / 'scripts/mosaic-signing.json').read_text()))
        if args.mode == 'manifest':
            if env['MOSAIC_CHECKPOINT'] == 'signed':
                checked = json.loads((directory / 'reverified.json').read_text())
                if checked != record:
                    raise ValueError('Fresh SDK verification differs from stored acceptance')
            (directory / MANIFEST_NAME).write_bytes(canonical(m))
            # Recovery execution is evidence, not a rewrite of permanent build identity.
            (directory / 'recovery.json').write_bytes(canonical(dict(schemaVersion=1, artifactId=a['id'],
                artifactDigest=a['digest'], checkpoint=env['MOSAIC_CHECKPOINT'], sourceSha=identity['sourceSha'],
                executionSha=env['GITHUB_SHA'], runId=env['GITHUB_RUN_ID'], runAttempt=env['GITHUB_RUN_ATTEMPT'])))
        else:
            if (directory / MANIFEST_NAME).read_bytes() != canonical(m):
                raise ValueError('Recovery manifest mismatch')
            publish(api, m, apk)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
