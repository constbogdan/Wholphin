"""Fail-closed Mosaic development publisher. No signing keys or build commands."""

import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

import mosaic_change_classification as change_classification
from mosaic_version import allocate
from mosaic_signing_exercise import artifact_name, payload, validate_record
from verify_mosaic_apk import fingerprint

REPOSITORY = 'constbogdan/Wholphin'
WORKFLOW = '.github/workflows/mosaic-development-release.yml'
CI_WORKFLOW = '.github/workflows/ci.yml'
CI_JOB = 'Full validation'
APK_NAME = 'Wholphin-release.apk'
MANIFEST_NAME = 'mosaic-release.json'


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode('utf-8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def guard(env):
    expected = dict(GITHUB_ACTIONS='true', GITHUB_REPOSITORY=REPOSITORY,
                    GITHUB_REF='refs/heads/main', GITHUB_REF_PROTECTED='true')
    sha = env.get('GITHUB_SHA', '')
    if (any(env.get(k) != v for k, v in expected.items())
            or not re.fullmatch('[0-9a-f]{40}', sha)
            or env.get('MOSAIC_EXERCISE_SHA') != sha
            or env.get('GITHUB_EVENT_NAME') not in ('workflow_dispatch', 'workflow_run')
            or env.get('GITHUB_WORKFLOW_REF') != f'{REPOSITORY}/{WORKFLOW}@refs/heads/main'):
        raise ValueError('Requires authorized exact protected-main development workflow')
    if env['GITHUB_EVENT_NAME'] == 'workflow_run':
        triggering_ci(env, sha)
    return sha


def ci_guard(env):
    expected = dict(GITHUB_ACTIONS='true', GITHUB_REPOSITORY=REPOSITORY,
                    GITHUB_REF='refs/heads/main', GITHUB_REF_PROTECTED='true',
                    GITHUB_EVENT_NAME='push')
    sha = env.get('GITHUB_SHA', '')
    if (any(env.get(k) != v for k, v in expected.items())
            or not re.fullmatch('[0-9a-f]{40}', sha)
            or env.get('GITHUB_WORKFLOW_REF') != f'{REPOSITORY}/{CI_WORKFLOW}@refs/heads/main'):
        raise ValueError('Release classification requires exact protected-main push CI')
    return sha


def triggering_ci(env, sha):
    """Validate GitHub's event payload, never an input-selected SHA or artifact."""
    event = json.loads(Path(env['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))
    run = event.get('workflow_run', {})
    if (event.get('action') != 'completed'
            or event.get('repository', {}).get('full_name') != REPOSITORY
            or run.get('head_repository', {}).get('full_name') != REPOSITORY
            or run.get('event') != 'push' or run.get('head_branch') != 'main'
            or run.get('head_sha') != sha or run.get('path') != '.github/workflows/ci.yml'
            or run.get('status') != 'completed' or run.get('conclusion') != 'success'
            or any(type(run.get(k)) is not int or run[k] < 1 for k in ('id', 'run_attempt', 'workflow_id'))):
        raise ValueError('Automatic development requires successful exact-main push CI event')
    return run


def authorized_ci(api, sha, env):
    ci = trusted_ci(api, sha)
    if env['GITHUB_EVENT_NAME'] == 'workflow_run':
        run = triggering_ci(env, sha)
        workflow = api.call('GET', 'actions/workflows/ci.yml')
        if (run['workflow_id'] != workflow['id'] or str(run['id']) != ci['runId']
                or str(run['run_attempt']) != ci['runAttempt']):
            raise ValueError('Triggering CI differs from latest authoritative successful run/attempt')
    return ci


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class GitHub:
    """Fixed repository/hosts only; credentials and response bodies never enter errors."""
    def call(self, method, path, data=None, missing=False, upload=False):
        host = 'uploads.github.com' if upload else 'api.github.com'
        url = f'https://{host}/repos/{REPOSITORY}/{path}'
        body = data if upload else (canonical(data) if data is not None else None)
        request = urllib.request.Request(url, data=body, method=method, headers={
            'Authorization': 'Bearer ' + os.environ['GH_TOKEN'],
            'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28',
            'Content-Type': 'application/octet-stream' if upload else 'application/json',
            'User-Agent': 'mosaic-development-publisher'})
        try:
            with urllib.request.build_opener(NoRedirect).open(request, timeout=180) as response:
                raw = response.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as error:
            if missing and error.code == 404:
                return None
            raise ValueError(f'GitHub {method} failed (HTTP {error.code}); stopped without fallback') from None
        except OSError:
            raise ValueError('GitHub transport failed; inspect public state before retry') from None

    def pages(self, path, key=None):
        result = []
        for page in range(1, 101):
            data = self.call('GET', path + ('&' if '?' in path else '?') + f'per_page=100&page={page}')
            entries = data[key] if key else data
            result.extend(entries)
            if len(entries) < 100:
                return result
        raise ValueError('Pagination limit reached; refusing incomplete inspection')


def trusted_ci(api, sha, *, require_tip=True):
    branch = api.call('GET', 'branches/main')
    if branch.get('protected') is not True or (require_tip and branch['commit']['sha'] != sha):
        raise ValueError('Approved SHA is no longer protected main tip')
    workflow = api.call('GET', 'actions/workflows/ci.yml')
    runs = api.pages(f'actions/workflows/ci.yml/runs?head_sha={sha}&event=push', 'workflow_runs')
    candidates = [r for r in runs if r.get('head_sha') == sha and r.get('head_branch') == 'main'
                  and r.get('event') == 'push' and r.get('workflow_id') == workflow['id']
                  and r.get('head_repository', {}).get('full_name') == REPOSITORY]
    if not candidates:
        raise ValueError('No authoritative push CI for exact main SHA; wait for CI, then authorize again')
    run = max(candidates, key=lambda r: r['id'])
    if run.get('status') != 'completed' or run.get('conclusion') != 'success':
        raise ValueError('Latest exact-main push CI has not completed successfully')
    jobs = api.pages(f"actions/runs/{run['id']}/attempts/{run['run_attempt']}/jobs", 'jobs')
    full = [j for j in jobs if j.get('name') == CI_JOB]
    if len(full) != 1 or full[0].get('conclusion') != 'success' or full[0].get('status') != 'completed' or full[0].get('head_sha') != sha:
        raise ValueError('Required exact-SHA Full validation did not succeed')
    return {'workflow': CI_WORKFLOW, 'runId': str(run['id']), 'runAttempt': str(run['run_attempt'])}


def ci_artifact_name(identity, run, attempt):
    return 'unsigned-' + artifact_name(identity, run, attempt, 'mosaic-main-ci')


def trusted_ci_artifact(api, identity, ci):
    """Resolve exactly one unexpired unsigned artifact from the trusted CI attempt."""
    run, attempt = ci['runId'], ci['runAttempt']
    expected_name = ci_artifact_name(identity, run, attempt)
    artifacts = api.pages(f'actions/runs/{run}/artifacts', 'artifacts')
    matches = [artifact for artifact in artifacts if artifact.get('name') == expected_name]
    if len(matches) != 1:
        raise ValueError('Expected exactly one authoritative unsigned main-CI artifact')
    artifact = matches[0]
    owner = artifact.get('workflow_run', {})
    if (not re.fullmatch('[1-9][0-9]*', str(artifact.get('id', '')))
            or artifact.get('expired') is not False
            or not re.fullmatch(r'sha256:[0-9a-f]{64}', str(artifact.get('digest', '')))
            or str(owner.get('id')) != run
            or owner.get('head_sha') != identity['sourceSha']
            or owner.get('head_branch') != 'main'
            or owner.get('repository_id') != owner.get('head_repository_id')):
        raise ValueError('Unsigned main-CI artifact identity is missing, expired or untrusted')
    jobs = api.pages(f'actions/runs/{run}/attempts/{attempt}/jobs', 'jobs')
    full = [job for job in jobs if job.get('name') == CI_JOB]
    if (len(full) != 1 or full[0].get('status') != 'completed'
            or full[0].get('conclusion') != 'success'
            or full[0].get('head_sha') != identity['sourceSha']):
        raise ValueError('Unsigned artifact does not belong to successful exact-SHA Full validation')
    try:
        created = datetime.fromisoformat(artifact['created_at'])
        started = datetime.fromisoformat(full[0]['started_at'])
        completed = datetime.fromisoformat(full[0]['completed_at'])
    except (KeyError, TypeError, ValueError):
        raise ValueError('Unsigned artifact timing identity is incomplete') from None
    if not started <= created <= completed:
        raise ValueError('Unsigned artifact was not created by the successful CI job attempt')
    return {
        'artifactId': str(artifact['id']),
        'artifactName': expected_name,
        'artifactDigest': artifact['digest'],
        'runId': run,
        'runAttempt': attempt,
        'versionName': identity['versionName'],
    }


def verify_ci_artifact_directory(directory, identity, artifact):
    record = json.loads((directory / 'provenance.json').read_text(encoding='utf-8'))
    validate_record(record, identity, directory / 'unsigned.apk', artifact['runId'], artifact['runAttempt'])
    if b'APK Sig Block 42' in (directory / 'unsigned.apk').read_bytes():
        raise ValueError('Expected unsigned APK')
    payload(directory / 'unsigned.apk')
    return record


def require_ci_artifact_selection(env, artifact):
    expected = {
        'artifactId': env.get('MOSAIC_ARTIFACT_ID'),
        'artifactName': env.get('MOSAIC_ARTIFACT_NAME'),
        'runId': env.get('MOSAIC_BUILD_RUN_ID'),
        'runAttempt': env.get('MOSAIC_BUILD_RUN_ATTEMPT'),
    }
    if any(expected[field] != artifact[field] for field in expected):
        raise ValueError('Downloaded artifact selection differs from authoritative CI identity')


def ci_identity_from_env(env):
    ci = {
        'workflow': CI_WORKFLOW,
        'runId': env.get('MOSAIC_BUILD_RUN_ID'),
        'runAttempt': env.get('MOSAIC_BUILD_RUN_ATTEMPT'),
    }
    if any(not re.fullmatch('[1-9][0-9]*', str(ci[field] or '')) for field in ('runId', 'runAttempt')):
        raise ValueError('Missing authoritative CI run identity')
    return ci


def manifest(record, apk, identity, env, policy, ci=None):
    sha = guard(env)
    if identity.get('sourceSha') != sha:
        raise ValueError('Signed artifact source differs from authorized main')
    if ci is None:
        run, attempt, workflow = env['GITHUB_RUN_ID'], env['GITHUB_RUN_ATTEMPT'], WORKFLOW
    else:
        run, attempt, workflow = ci['runId'], ci['runAttempt'], CI_WORKFLOW
    return verified_manifest(record, apk, identity, run, attempt, policy, workflow)


def verified_manifest(record, apk, identity, run, attempt, policy, build_workflow=WORKFLOW):
    """Pure byte/provenance validation shared after normal or recovery trust gates."""
    sha = identity['sourceSha']
    source = record.get('source', {})
    expected = dict(identity, apkSha256=source.get('apkSha256'),
                    runId=run, runAttempt=attempt)
    if source != expected or identity.get('sourceSha') != sha or identity.get('publication') is not True or identity.get('dirty') is not False:
        raise ValueError('Signed artifact source/version/run provenance mismatch')
    for field in ('sourceSha', 'sourceTree', 'upstreamBaseline', 'epoch'):
        if not re.fullmatch('[0-9a-f]{40}', str(source.get(field, ''))):
            raise ValueError('Invalid source provenance')
    code = source.get('versionCode')
    if type(code) is not int or not 1 <= code <= 2100000000 or source.get('versionName') != f'1.0.{code}':
        raise ValueError('Invalid version identity')
    for field in ('runId', 'runAttempt'):
        if not re.fullmatch('[1-9][0-9]*', source[field]):
            raise ValueError('Invalid run identity')
    if not re.fullmatch('[0-9a-f]{64}', str(source.get('apkSha256', ''))):
        raise ValueError('Missing unsigned APK hash')
    cert = fingerprint(policy.get('expectedCertificateSha256'))
    if (policy.get('schemaVersion') != 1 or policy.get('applicationId') != 'io.github.constbogdan.mosaic'
            or record.get('schemaVersion') != 1 or record.get('applicationId') != policy['applicationId']
            or record.get('certificateSha256') != cert or record.get('signedApkSha256') != digest(apk)):
        raise ValueError('Signed APK hash/package/certificate mismatch')
    return dict(schemaVersion=1, applicationId=record['applicationId'], versionName=source['versionName'],
                versionCode=code, sourceSha=sha, sourceTree=source['sourceTree'], upstreamBaseline=source['upstreamBaseline'],
                buildWorkflow=build_workflow, buildRunId=source['runId'], buildRunAttempt=source['runAttempt'],
                publication=True, unsignedApkSha256=source['apkSha256'], signedApkSha256=digest(apk),
                signerSha256=cert, immutableIdentity=f'downstream-build-{code}', rollingChannel='develop',
                assetName=APK_NAME, source=source)


def release_fields(m, draft):
    return dict(name='v' + m['versionName'], draft=draft, prerelease=True, make_latest='false',
                body=f"Mosaic development build {m['immutableIdentity']}\n\nSource: {m['sourceSha']}\n\n"
                     f"Signed SHA-256: {m['signedApkSha256']}\n\n"
                     'Development preview, not a stable release. Public provenance: mosaic-release.json.\n')


def check_asset(asset, name, data):
    if (asset.get('name') != name or asset.get('state') != 'uploaded'
            or asset.get('size') != len(data) or asset.get('digest') != 'sha256:' + digest(data)):
        raise ValueError('Release asset differs from immutable recorded bytes')


def find_release(api, tag):
    # Listing includes drafts; GET by tag alone may not recover a partially created draft.
    matches = [r for r in api.pages('releases') if r['tag_name'] == tag]
    if len(matches) > 1:
        raise ValueError('Duplicate release identity')
    return matches[0] if matches else None


def _release_assets(api, release, manifest):
    found = api.pages(f"releases/{release['id']}/assets")
    if len(found) != 2 or {asset.get('name') for asset in found} != {APK_NAME, MANIFEST_NAME}:
        raise ValueError('Development release does not have the exact published asset set')
    result = {asset['name']: asset for asset in found}
    for asset in result.values():
        if (asset.get('state') != 'uploaded' or type(asset.get('size')) is not int
                or asset['size'] < 1 or not re.fullmatch(r'sha256:[0-9a-f]{64}', str(asset.get('digest', '')))):
            raise ValueError('Development release asset identity is incomplete')
    if result[MANIFEST_NAME]['digest'] != 'sha256:' + digest(canonical(manifest)):
        raise ValueError('Development manifest asset differs from immutable tag provenance')
    if result[APK_NAME]['digest'] != 'sha256:' + manifest.get('signedApkSha256', ''):
        raise ValueError('Development APK asset differs from immutable tag provenance')
    return {name: (asset['size'], asset['digest']) for name, asset in result.items()}


def published_development_source(api):
    """Authenticate the latest successfully exposed rolling Development source."""
    rolling = find_release(api, 'develop')
    if (rolling is None or rolling.get('tag_name') != 'develop' or rolling.get('draft')
            or rolling.get('prerelease') is not True or rolling.get('immutable')):
        raise ValueError('No trustworthy published rolling Development release')
    version = re.fullmatch(r'v1\.0\.([1-9][0-9]*)', str(rolling.get('name', '')))
    if not version:
        raise ValueError('Published rolling Development version is invalid')
    number = int(version[1])
    immutable_name = f'downstream-build-{number}'

    develop_ref = api.call('GET', 'git/ref/tags/develop', missing=True)
    immutable_ref = api.call('GET', f'git/ref/tags/{immutable_name}', missing=True)
    if (not develop_ref or develop_ref.get('object', {}).get('type') != 'commit'
            or not immutable_ref or immutable_ref.get('object', {}).get('type') != 'tag'):
        raise ValueError('Development release refs do not match the publication contract')
    source = develop_ref['object'].get('sha', '')
    if not re.fullmatch(r'[0-9a-f]{40}', source):
        raise ValueError('Development source SHA is invalid')

    annotation = api.call('GET', 'git/tags/' + immutable_ref['object']['sha']) or {}
    try:
        manifest = json.loads(annotation.get('message', ''))
    except (TypeError, json.JSONDecodeError):
        raise ValueError('Immutable Development provenance is not valid JSON') from None
    if (not isinstance(manifest, dict)
            or annotation.get('tag') != immutable_name
            or annotation.get('object', {}).get('type') != 'commit'
            or annotation.get('object', {}).get('sha') != source
            or manifest.get('schemaVersion') != 1
            or manifest.get('applicationId') != 'io.github.constbogdan.mosaic'
            or manifest.get('sourceSha') != source
            or manifest.get('versionCode') != number
            or manifest.get('versionName') != f'1.0.{number}'
            or manifest.get('immutableIdentity') != immutable_name
            or manifest.get('rollingChannel') != 'develop'
            or manifest.get('assetName') != APK_NAME):
        raise ValueError('Immutable Development provenance does not match rolling release identity')

    immutable = find_release(api, immutable_name)
    if (immutable is None or immutable.get('tag_name') != immutable_name or immutable.get('draft')
            or immutable.get('prerelease') is not True or immutable.get('name') != rolling.get('name')):
        raise ValueError('Immutable Development release is missing or inconsistent')
    if _release_assets(api, rolling, manifest) != _release_assets(api, immutable, manifest):
        raise ValueError('Rolling and immutable Development assets differ')
    return source


def release_eligibility(api, root, sha):
    """Classify the complete unpublished range; uncertainty always requires release."""
    try:
        baseline = published_development_source(api)
        result = change_classification.classify_range(root, baseline, sha)
    except (KeyError, OSError, TypeError, UnicodeError, ValueError) as error:
        return {
            'outcome': 'ready',
            'releaseRequired': True,
            'releaseRelevance': change_classification.UNKNOWN,
            'validationRisk': change_classification.HIGH,
            'baselineSha': None,
            'currentSha': sha,
            'paths': [],
            'reason': f'conservative fallback: {error}',
        }
    return {
        **result,
        'outcome': 'ready' if result['releaseRequired'] else 'skipped_non_apk',
        'reason': 'classified complete range from published Development source',
    }


def record_eligibility(result, ci, env, artifact=None):
    output_path = Path(env['GITHUB_OUTPUT'])
    with output_path.open('a', encoding='utf-8') as output:
        values = {
            'release_required': str(result['releaseRequired']).lower(),
            'outcome': result['outcome'],
            'release_relevance': result['releaseRelevance'],
            'validation_risk': result['validationRisk'],
            'baseline_sha': result.get('baselineSha') or 'unresolved',
        }
        if artifact:
            values.update(
                artifact_id=artifact['artifactId'],
                artifact_name=artifact['artifactName'],
                ci_run_id=artifact['runId'],
                ci_run_attempt=artifact['runAttempt'],
                version_name=artifact['versionName'],
            )
        for key, value in values.items():
            output.write(f'{key}={value}\n')
    paths = [entry['path'] for entry in result['paths']]
    summary = [
        '## Mosaic Development eligibility',
        f"Outcome: `{result['outcome']}`",
        f"Release relevance: `{result['releaseRelevance']}`",
        f"Validation risk: `{result['validationRisk']}`",
        f"Published baseline: `{result.get('baselineSha') or 'unresolved'}`",
        f"Current trusted main: `{result['currentSha']}`",
        f"Changed paths: {len(paths)}",
        f"Reason: {result['reason']}",
        f"Authoritative CI: `{json.dumps(ci, sort_keys=True) if ci else 'current main push run'}`",
    ]
    if artifact:
        summary.extend([
            f"Unsigned artifact ID: `{artifact['artifactId']}`",
            f"Unsigned artifact: `{artifact['artifactName']}`",
        ])
    if paths:
        summary.extend(['', 'Changed range:', *[f'- `{path}`' for path in paths]])
    with Path(env['GITHUB_STEP_SUMMARY']).open('a', encoding='utf-8') as output:
        output.write('\n\n'.join(summary[:8]) + '\n\n' + '\n'.join(summary[8:]) + '\n')


def assets(api, release, expected, allow_upload):
    actual = api.pages(f"releases/{release['id']}/assets")
    if len({a['name'] for a in actual}) != len(actual) or any(a['name'] not in expected for a in actual):
        raise ValueError('Unexpected or duplicate immutable release assets')
    by_name = {a['name']: a for a in actual}
    for name, data in expected.items():
        if name not in by_name:
            if not allow_upload:
                raise ValueError('Published immutable release is missing an asset')
            asset = api.call('POST', f"releases/{release['id']}/assets?name={urllib.parse.quote(name)}", data, upload=True)
        else:
            asset = by_name[name]
        check_asset(asset, name, data)


def publish(api, m, apk):
    """Never replace immutable records/assets; hide rolling metadata during replacement."""
    tag = m['immutableIdentity']
    record_bytes = canonical(m)
    expected = {APK_NAME: apk, MANIFEST_NAME: record_bytes}
    rolling = find_release(api, 'develop')
    if rolling:
        if rolling.get('immutable') or not rolling.get('prerelease'):
            raise ValueError('Existing develop is immutable or not a prerelease; no settings changes attempted')
        match = re.fullmatch(r'v1\.0\.([1-9][0-9]*)', rolling.get('name', ''))
        if not match or int(match[1]) > m['versionCode']:
            raise ValueError('Unknown or newer rolling release; refusing rollback')
    ref = api.call('GET', f'git/ref/tags/{tag}', missing=True)
    if ref:
        if ref['object']['type'] != 'tag':
            raise ValueError('Immutable identity is not an annotated provenance tag')
        annotation = api.call('GET', 'git/tags/' + ref['object']['sha'])
        if annotation.get('tag') != tag or annotation.get('object', {}).get('type') != 'commit' or annotation.get('object', {}).get('sha') != m['sourceSha']:
            raise ValueError('Immutable tag source mismatch')
        if annotation.get('message', '').rstrip('\n') != record_bytes.decode().rstrip('\n'):
            raise ValueError('Build identity already reserved for different bytes/provenance; never overwrite')
    else:
        if find_release(api, tag):
            raise ValueError('Release exists without its immutable provenance tag')
        annotation = api.call('POST', 'git/tags', dict(tag=tag, message=record_bytes.decode(), object=m['sourceSha'], type='commit'))
        # Atomic ref creation; conflict fails. Never update/delete downstream-build-N.
        api.call('POST', 'git/refs', dict(ref='refs/tags/' + tag, sha=annotation['sha']))
    archive = find_release(api, tag)
    if archive is None:
        archive = api.call('POST', 'releases', dict(tag_name=tag, target_commitish=m['sourceSha'], **release_fields(m, True)))
    if not archive.get('prerelease') or archive.get('name') != 'v' + m['versionName']:
        raise ValueError('Immutable archive release metadata mismatch')
    assets(api, archive, expected, allow_upload=archive['draft'])
    if archive['draft']:
        api.call('PATCH', f"releases/{archive['id']}", release_fields(m, False))
    develop_ref = api.call('GET', 'git/ref/tags/develop', missing=True)
    if rolling and rolling['name'] == 'v' + m['versionName'] and not rolling['draft']:
        if not develop_ref or develop_ref['object']['type'] != 'commit' or develop_ref['object']['sha'] != m['sourceSha']:
            raise ValueError('Existing rolling tag/source mismatch')
        assets(api, rolling, expected, allow_upload=False)
        return
    if rolling:
        api.call('PATCH', f"releases/{rolling['id']}", dict(draft=True, prerelease=True, make_latest='false'))
    elif develop_ref:
        raise ValueError('Orphan develop tag; explicit recovery review required')
    if develop_ref:
        # This is the ONLY mutable ref. Never push/force protected main or immutable tags.
        api.call('PATCH', 'git/refs/tags/develop', dict(sha=m['sourceSha'], force=True))
    else:
        api.call('POST', 'git/refs', dict(ref='refs/tags/develop', sha=m['sourceSha']))
    if rolling is None:
        rolling = api.call('POST', 'releases', dict(tag_name='develop', target_commitish=m['sourceSha'], **release_fields(m, True)))
    for asset in api.pages(f"releases/{rolling['id']}/assets"):
        if asset['name'] not in expected:
            raise ValueError('Unexpected rolling asset; explicit recovery review required')
        api.call('DELETE', f"releases/assets/{asset['id']}")
    assets(api, rolling, expected, allow_upload=True)
    result = api.call('PATCH', f"releases/{rolling['id']}", release_fields(m, False))
    if result.get('draft') or result.get('prerelease') is not True or result.get('tag_name') != 'develop':
        raise ValueError('Rolling release final verification failed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['ci-eligibility', 'eligibility', 'trust', 'artifact', 'manifest', 'publish'])
    parser.add_argument('--directory', type=Path)
    args = parser.parse_args()
    try:
        env = os.environ
        if args.mode == 'ci-eligibility':
            sha = ci_guard(env)
            api = GitHub()
            result = release_eligibility(api, Path(__file__).resolve().parent.parent, sha)
            record_eligibility(result, None, env)
            print(json.dumps(result, sort_keys=True))
            return
        sha = guard(env)
        if args.mode == 'eligibility':
            api = GitHub()
            ci = authorized_ci(api, sha, env)
            root = Path(__file__).resolve().parent.parent
            result = release_eligibility(api, root, sha)
            artifact = trusted_ci_artifact(api, allocate(root, publication=True), ci) if result['releaseRequired'] else None
            record_eligibility(result, ci, env, artifact)
            print(json.dumps(result, sort_keys=True))
            return
        if args.mode == 'trust':
            api = GitHub()
            print(json.dumps(authorized_ci(api, sha, env), sort_keys=True))
            return
        root = Path(__file__).resolve().parent.parent
        directory = args.directory
        identity = allocate(root, publication=True)
        if args.mode == 'artifact':
            api = GitHub()
            ci = authorized_ci(api, sha, env)
            artifact = trusted_ci_artifact(api, identity, ci)
            require_ci_artifact_selection(env, artifact)
            verify_ci_artifact_directory(directory, identity, artifact)
            return
        if args.mode == 'manifest':
            ci = ci_identity_from_env(env)
        else:
            api = GitHub()
            ci = authorized_ci(api, sha, env)
            trusted_ci_artifact(api, identity, ci)
        apk = (directory / 'Mosaic-release.apk').read_bytes()
        m = manifest(json.loads((directory / 'verification.json').read_text(encoding='utf-8')), apk, identity, env,
                     json.loads((root / 'scripts/mosaic-signing.json').read_text(encoding='utf-8')), ci)
        path = directory / MANIFEST_NAME
        if args.mode == 'manifest':
            path.write_bytes(canonical(m))
        else:
            if path.read_bytes() != canonical(m):
                raise ValueError('Prepared publication manifest changed')
            publish(api, m, apk)
            with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as output:
                output.write(f"Mosaic development release verified: {m['immutableIdentity']} / v{m['versionName']}\n\n"
                             f"Source: {sha}\n\nSigned SHA-256: {m['signedApkSha256']}\n\n"
                             f"Authoritative CI: {json.dumps(ci, sort_keys=True)}\n")
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
