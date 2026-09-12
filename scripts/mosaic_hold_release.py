"""Authenticate and hold only the exact Stable release currently advertised by GitHub."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess

from mosaic_development_release import (
    APK_NAME,
    MANIFEST_NAME,
    GitHub,
    REPOSITORY,
    canonical,
    check_asset,
    digest,
    historical_identity,
    trusted_ci,
    validate_original_source,
)
from mosaic_stable import authenticated_stable_release, download_asset, verify_manifest


WORKFLOW = '.github/workflows/hold-release.yml'
EVIDENCE_NAME = 'hold-release.json'


def authorization(env):
    expected = {
        'GITHUB_ACTIONS': 'true',
        'GITHUB_REPOSITORY': REPOSITORY,
        'GITHUB_REF': 'refs/heads/main',
        'GITHUB_REF_PROTECTED': 'true',
        'GITHUB_EVENT_NAME': 'workflow_dispatch',
    }
    sha = env.get('GITHUB_SHA', '')
    if (any(env.get(key) != value for key, value in expected.items())
            or not re.fullmatch(r'[0-9a-f]{40}', sha)
            or env.get('GITHUB_WORKFLOW_REF') != f'{REPOSITORY}/{WORKFLOW}@refs/heads/main'):
        raise ValueError('Hold Release requires a manual run from exact protected main')
    return sha


def stable_number(release):
    match = re.fullmatch(r'mosaic-v1\.0\.([1-9][0-9]*)', str(release.get('tag_name', '')))
    return int(match[1]) if match else None


def latest(api):
    return api.call('GET', 'releases/latest', missing=True)


def refuse_cascading_hold(api, current):
    current_number = stable_number(current)
    if current_number is None:
        raise ValueError('Current Stable tag is malformed')
    for release in api.pages('releases'):
        number = stable_number(release)
        if (number is not None and number > current_number and not release.get('draft')
                and release.get('prerelease') is True):
            raise ValueError(
                f'Refusing cascading hold: newer Stable v1.0.{number} is already held; '
                'forward-fix instead',
            )


def _write_outputs(values, env):
    if not env.get('GITHUB_OUTPUT'):
        return
    with Path(env['GITHUB_OUTPUT']).open('a', encoding='utf-8') as output:
        for key, value in values.items():
            output.write(f'{key}={value}\n')


def apk_url(inventory):
    url = inventory.get(APK_NAME, {}).get('browser_download_url', '')
    if not re.fullmatch(
            rf'https://github\.com/{re.escape(REPOSITORY)}/releases/download/[^\s]+/{APK_NAME}',
            str(url)):
        raise ValueError('Authenticated Stable APK URL is missing or malformed')
    return url


def release_link(name, url):
    return f'[{name}]({url})'


def append_summary(env, text):
    path = env.get('GITHUB_STEP_SUMMARY')
    if path:
        with Path(path).open('a', encoding='utf-8') as summary:
            summary.write(text.rstrip() + '\n')


def _read(directory, name):
    return json.loads((directory / name).read_text(encoding='utf-8'))


def verify_local(directory, root, execution_sha):
    evidence = _read(directory, EVIDENCE_NAME)
    manifest = _read(directory, MANIFEST_NAME)
    apk = (directory / APK_NAME).read_bytes()
    if (evidence.get('toolingSha') != execution_sha
            or evidence.get('tagName') != f"mosaic-v{manifest.get('versionName')}"
            or evidence.get('versionName') != manifest.get('versionName')
            or evidence.get('sourceSha') != manifest.get('sourceSha')
            or evidence.get('signedApkSha256') != digest(apk)):
        raise ValueError('Transferred Hold Release evidence is inconsistent')
    identity = historical_identity(root, manifest['sourceSha'], execution_sha)
    acceptance = _read(directory, 'verification.json')
    policy = json.loads((root / 'scripts/mosaic-signing.json').read_text(encoding='utf-8'))
    verify_manifest(manifest, apk, acceptance, identity, policy)
    return evidence, manifest, apk


def get_release(api, root, env, directory):
    execution_sha = authorization(env)
    trusted_ci(api, execution_sha)
    current = latest(api)
    if current is None:
        raise ValueError('No Stable release is currently advertised; nothing was changed')
    refuse_cascading_hold(api, current)
    manifest, inventory = authenticated_stable_release(api, current)
    identity = historical_identity(root, manifest['sourceSha'], execution_sha)
    trusted_ci(api, manifest['sourceSha'], require_tip=False)
    validate_original_source(api, manifest['source'], identity)
    stable_ref = api.call('GET', f"git/ref/tags/{current['tag_name']}", missing=True)
    if not stable_ref or stable_ref.get('object', {}).get('type') != 'tag':
        raise ValueError('Stable provenance tag ref is missing or malformed')

    directory.mkdir(parents=True, exist_ok=False)
    for name, item in inventory.items():
        data = download_asset(item['id'])
        check_asset(item, name, data)
        if name == MANIFEST_NAME and data != canonical(manifest):
            raise ValueError('Downloaded Stable manifest differs from its provenance tag')
        (directory / name).write_bytes(data)
    evidence = {
        'schemaVersion': 1,
        'toolingSha': execution_sha,
        'releaseId': current['id'],
        'tagName': current['tag_name'],
        'tagObjectSha': stable_ref['object']['sha'],
        'versionName': manifest['versionName'],
        'sourceSha': manifest['sourceSha'],
        'signedApkSha256': manifest['signedApkSha256'],
        'apkUrl': apk_url(inventory),
    }
    (directory / EVIDENCE_NAME).write_bytes(canonical(evidence))
    (directory / 'provenance.json').write_bytes(canonical(manifest['source']))
    _write_outputs({
        'version': 'v' + manifest['versionName'],
        'release_id': current['id'],
        'apk_url': evidence['apkUrl'],
    }, env)
    return evidence


def hold(api, root, env, directory):
    execution_sha = authorization(env)
    trusted_ci(api, execution_sha)
    evidence, manifest, _ = verify_local(directory, root, execution_sha)
    current = latest(api)
    if (current is None or current.get('id') != evidence['releaseId']
            or current.get('tag_name') != evidence['tagName'] or current.get('draft')
            or current.get('prerelease') is not False):
        prepared = release_link('v' + evidence['versionName'], evidence['apkUrl'])
        current_text = 'no Stable release is currently advertised'
        if current is not None:
            try:
                current_manifest, current_inventory = authenticated_stable_release(api, current)
                current_text = release_link(
                    'v' + current_manifest['versionName'], apk_url(current_inventory),
                )
            except (ValueError, KeyError, TypeError):
                current_text = 'the current Stable identity could not be authenticated'
        append_summary(
            env,
            f'## Hold Release\n\nRefused: {prepared} → current Stable is {current_text}\n\n'
            'No changes made.',
        )
        raise ValueError('Advertised Stable changed after authentication; nothing was modified')
    refuse_cascading_hold(api, current)
    remote_manifest, _ = authenticated_stable_release(api, current)
    if remote_manifest != manifest:
        raise ValueError('Advertised Stable provenance changed after authentication')
    ref = api.call('GET', f"git/ref/tags/{evidence['tagName']}", missing=True)
    if not ref or ref.get('object', {}).get('sha') != evidence['tagObjectSha']:
        raise ValueError('Stable tag changed after authentication')
    before_assets = api.pages(f"releases/{current['id']}/assets")
    result = api.call(
        'PATCH',
        f"releases/{current['id']}",
        {'prerelease': True, 'make_latest': 'false'},
    )
    if (result.get('id') != current['id'] or result.get('draft')
            or result.get('prerelease') is not True or result.get('tag_name') != evidence['tagName']):
        raise ValueError('Hold mutation did not produce the required Release state')
    after_ref = api.call('GET', f"git/ref/tags/{evidence['tagName']}", missing=True)
    after_assets = api.pages(f"releases/{current['id']}/assets")
    if after_ref != ref or after_assets != before_assets:
        raise ValueError('Hold unexpectedly changed Stable tag or assets')
    return confirm(api, env, directory)


def confirm(api, env, directory):
    authorization(env)
    evidence = _read(directory, EVIDENCE_NAME)
    held = api.call('GET', f"releases/{evidence['releaseId']}")
    if (held.get('id') != evidence['releaseId'] or held.get('draft')
            or held.get('prerelease') is not True or held.get('tag_name') != evidence['tagName']):
        raise ValueError('Held Stable release state is missing or inconsistent')
    current = latest(api)
    if current is not None and current.get('id') == evidence['releaseId']:
        raise ValueError('Held Stable release is still advertised by /releases/latest')
    if current is not None and (current.get('draft') or current.get('prerelease')
                                or stable_number(current) is None):
        raise ValueError('GitHub returned an invalid fallback Stable release')
    if current is None:
        advertised = 'none'
        current_url = ''
    else:
        current_manifest, inventory = authenticated_stable_release(api, current)
        advertised = 'v' + current_manifest['versionName']
        current_url = apk_url(inventory)
    _write_outputs({
        'held': held['name'],
        'held_url': evidence['apkUrl'],
        'current': advertised,
        'current_url': current_url,
    }, env)
    return advertised


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['get', 'verify', 'hold'])
    parser.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args()
    try:
        env = os.environ
        root = Path(__file__).resolve().parent.parent
        api = GitHub()
        if args.mode == 'get':
            get_release(api, root, env, args.directory)
        elif args.mode == 'verify':
            execution_sha = authorization(env)
            trusted_ci(api, execution_sha)
            verify_local(args.directory, root, execution_sha)
        else:
            hold(api, root, env, args.directory)
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
