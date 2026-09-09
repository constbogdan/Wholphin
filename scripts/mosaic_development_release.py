"""Fail-closed Mosaic development publisher. No signing keys or build commands."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

from mosaic_version import allocate
from verify_mosaic_apk import fingerprint

REPOSITORY = 'constbogdan/Wholphin'
WORKFLOW = '.github/workflows/mosaic-development-release.yml'
APK_NAME = 'Wholphin-release.apk'
MANIFEST_NAME = 'mosaic-release.json'


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode('utf-8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def guard(env):
    expected = dict(GITHUB_ACTIONS='true', GITHUB_REPOSITORY=REPOSITORY,
                    GITHUB_REF='refs/heads/main', GITHUB_REF_PROTECTED='true',
                    GITHUB_EVENT_NAME='workflow_dispatch')
    sha = env.get('GITHUB_SHA', '')
    if (any(env.get(k) != v for k, v in expected.items())
            or not re.fullmatch('[0-9a-f]{40}', sha)
            or env.get('MOSAIC_EXERCISE_SHA') != sha
            or env.get('GITHUB_WORKFLOW_REF') != f'{REPOSITORY}/{WORKFLOW}@refs/heads/main'):
        raise ValueError('Requires explicitly authorized exact protected-main development workflow')
    return sha


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
    full = [j for j in jobs if j.get('name') == 'Full validation']
    if len(full) != 1 or full[0].get('conclusion') != 'success' or full[0].get('status') != 'completed' or full[0].get('head_sha') != sha:
        raise ValueError('Required exact-SHA Full validation did not succeed')
    return {'workflow': '.github/workflows/ci.yml', 'runId': str(run['id']), 'runAttempt': str(run['run_attempt'])}


def manifest(record, apk, identity, env, policy):
    sha = guard(env)
    if identity.get('sourceSha') != sha:
        raise ValueError('Signed artifact source differs from authorized main')
    return verified_manifest(record, apk, identity, env['GITHUB_RUN_ID'], env['GITHUB_RUN_ATTEMPT'], policy)


def verified_manifest(record, apk, identity, run, attempt, policy):
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
                buildWorkflow=WORKFLOW, buildRunId=source['runId'], buildRunAttempt=source['runAttempt'],
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
    parser.add_argument('mode', choices=['trust', 'manifest', 'publish'])
    parser.add_argument('--directory', type=Path)
    args = parser.parse_args()
    try:
        sha = guard(os.environ)
        api = GitHub()
        if args.mode == 'trust':
            print(json.dumps(trusted_ci(api, sha), sort_keys=True))
            return
        root = Path(__file__).resolve().parent.parent
        directory = args.directory
        apk = (directory / 'Mosaic-release.apk').read_bytes()
        m = manifest(json.loads((directory / 'verification.json').read_text(encoding='utf-8')), apk,
                     allocate(root, publication=True), os.environ,
                     json.loads((root / 'scripts/mosaic-signing.json').read_text(encoding='utf-8')))
        path = directory / MANIFEST_NAME
        if args.mode == 'manifest':
            path.write_bytes(canonical(m))
        else:
            if path.read_bytes() != canonical(m):
                raise ValueError('Prepared publication manifest changed')
            ci = trusted_ci(api, sha)
            publish(api, m, apk)
            with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as output:
                output.write(f"Mosaic development release verified: {m['immutableIdentity']} / v{m['versionName']}\n\n"
                             f"Source: {sha}\n\nSigned SHA-256: {m['signedApkSha256']}\n\n"
                             f"Authoritative CI: {json.dumps(ci, sort_keys=True)}\n")
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
