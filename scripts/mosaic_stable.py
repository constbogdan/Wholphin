"""Manual stable promotion of existing authenticated development bytes; never builds/signs."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess

from mosaic_development_release import (GitHub, REPOSITORY, APK_NAME, MANIFEST_NAME, canonical,
    _release_assets, check_asset, assets, find_release, historical_identity, trusted_ci,
    validate_original_source, verified_manifest)
from mosaic_delivery_output import append_summary, publication_summary, release_body

WORKFLOW = '.github/workflows/mosaic-stable-promotion.yml'


def authorization(env):
    for key, value in dict(GITHUB_ACTIONS='true', GITHUB_REPOSITORY=REPOSITORY,
                          GITHUB_REF='refs/heads/main', GITHUB_REF_PROTECTED='true',
                          GITHUB_EVENT_NAME='workflow_dispatch').items():
        if env.get(key) != value:
            raise ValueError('Stable promotion requires protected-main manual authorization')
    if (not re.fullmatch('[0-9a-f]{40}', env.get('GITHUB_SHA', ''))
            or env.get('MOSAIC_EXPECTED_SHA') != env['GITHUB_SHA']
            or env.get('GITHUB_WORKFLOW_REF') != f'{REPOSITORY}/{WORKFLOW}@refs/heads/main'
            or not re.fullmatch('downstream-build-[1-9][0-9]*', env.get('MOSAIC_BUILD', ''))
            or not re.fullmatch('[0-9a-f]{40}', env.get('MOSAIC_SOURCE_SHA', ''))
            or not re.fullmatch('[0-9a-f]{64}', env.get('MOSAIC_APK_SHA256', ''))):
        raise ValueError('Exact tooling/source/build/hash authorization is required')


def download_asset(asset_id):
    # gh handles authenticated API asset redirects; never log response/error bodies or token.
    if type(asset_id) is not int or asset_id < 1:
        raise ValueError('Invalid immutable asset ID')
    result = subprocess.run(['gh', 'api', '--hostname', 'github.com', f'repos/{REPOSITORY}/releases/assets/{asset_id}',
                             '-H', 'Accept: application/octet-stream'], capture_output=True, timeout=180)
    if result.returncode:
        raise ValueError('Signed release asset download failed')
    return result.stdout


def annotation(api, tag):
    ref = api.call('GET', f'git/ref/tags/{tag}', missing=True)
    if ref is None:
        return None
    if ref.get('object', {}).get('type') != 'tag':
        raise ValueError('Expected an annotated immutable provenance tag')
    return api.call('GET', 'git/tags/' + ref['object']['sha'])


def check_annotation(a, tag, m):
    if (a.get('tag') != tag or a.get('object', {}).get('type') != 'commit'
            or a.get('object', {}).get('sha') != m['sourceSha']
            or a.get('message', '').rstrip('\n') != canonical(m).decode().rstrip('\n')):
        raise ValueError('Immutable provenance tag/manifest conflict')


def source_assets(api, tag, source, expected_hash):
    a = annotation(api, tag)
    if a is None:
        raise ValueError('Missing immutable development provenance identity')
    m = json.loads(a['message'])
    check_annotation(a, tag, m)
    if (m.get('immutableIdentity') != tag or m.get('sourceSha') != source
            or m.get('signedApkSha256') != expected_hash or tag != f"downstream-build-{m.get('versionCode')}"
            or m.get('versionName') != f"1.0.{m.get('versionCode')}"):
        raise ValueError('Development identity differs from explicit approval')
    release = find_release(api, tag)
    if not release or release.get('draft') or release.get('prerelease') is not True or release.get('name') != 'v' + m['versionName']:
        raise ValueError('Expected published immutable development prerelease')
    inventory = api.pages(f"releases/{release['id']}/assets")
    if len(inventory) != 2 or {a['name'] for a in inventory} != {APK_NAME, MANIFEST_NAME}:
        raise ValueError('Unexpected development release assets')
    return m, {a['name']: a for a in inventory}


def authenticated_stable_release(api, release):
    """Authenticate a published Stable release back to one immutable Development tuple."""
    if (not isinstance(release, dict) or type(release.get('id')) is not int or release['id'] < 1
            or release.get('draft') or release.get('prerelease') is not False
            or release.get('immutable') is not False):
        raise ValueError('Expected one published current Stable release')
    version = re.fullmatch(r'mosaic-v1\.0\.([1-9][0-9]*)', str(release.get('tag_name', '')))
    if not version or release.get('name') != f'v1.0.{version[1]}':
        raise ValueError('Current Stable release identity is malformed')
    stable_tag = release['tag_name']
    stable_annotation = annotation(api, stable_tag)
    if stable_annotation is None:
        raise ValueError('Missing immutable Stable provenance identity')
    try:
        manifest = json.loads(stable_annotation.get('message', ''))
    except (TypeError, json.JSONDecodeError):
        raise ValueError('Stable provenance is not valid JSON') from None
    check_annotation(stable_annotation, stable_tag, manifest)
    if (manifest.get('versionCode') != int(version[1])
            or manifest.get('versionName') != f'1.0.{version[1]}'):
        raise ValueError('Stable tag/version differs from its canonical manifest')
    development_manifest, _ = source_assets(
        api,
        manifest.get('immutableIdentity', ''),
        manifest.get('sourceSha', ''),
        manifest.get('signedApkSha256', ''),
    )
    if development_manifest != manifest:
        raise ValueError('Stable provenance differs from immutable Development provenance')
    development = find_release(api, manifest['immutableIdentity'])
    if _release_assets(api, release, manifest) != _release_assets(api, development, manifest):
        raise ValueError('Stable assets differ from immutable Development assets')
    return manifest, {item['name']: item for item in api.pages(f"releases/{release['id']}/assets")}


def verify_manifest(m, apk, acceptance, identity, policy):
    expected = verified_manifest(acceptance, apk, identity, m['source']['runId'],
                                 m['source']['runAttempt'], policy, m['buildWorkflow'])
    if m != expected:
        raise ValueError('Stable input differs from verified development manifest')


def fields(m, draft):
    return dict(name='v' + m['versionName'], draft=draft, prerelease=False,
                make_latest='false' if draft else 'true',
                body=release_body(m, 'Stable'))


def promote(api, m, apk, releases=None):
    tag = 'mosaic-v' + m['versionName']
    # Refuse numeric rollback and unknown stable ownership, even if GitHub ordering differs.
    releases = api.pages('releases') if releases is None else releases
    for existing in releases:
        if existing.get('draft') or existing.get('prerelease'):
            continue
        version = re.fullmatch(r'mosaic-v1\.0\.([1-9][0-9]*)', existing.get('tag_name', ''))
        if not version or int(version[1]) > m['versionCode']:
            raise ValueError('Unknown or newer stable release; refusing latest rollback')
    a = annotation(api, tag)
    stable = find_release(api, tag, releases)
    if a:
        check_annotation(a, tag, m)
    else:
        if stable:
            raise ValueError('Stable release exists without its immutable provenance tag')
        obj = api.call('POST', 'git/tags', dict(tag=tag, message=canonical(m).decode(), object=m['sourceSha'], type='commit'))
        api.call('POST', 'git/refs', dict(ref='refs/tags/' + tag, sha=obj['sha']))
    if stable is None:
        stable = api.call('POST', 'releases', dict(tag_name=tag, target_commitish=m['sourceSha'], **fields(m, True)))
    if stable.get('prerelease') is not False or stable.get('name') != 'v' + m['versionName']:
        raise ValueError('Stable release metadata conflict')
    assets(api, stable, {APK_NAME: apk, MANIFEST_NAME: canonical(m)}, allow_upload=stable['draft'])
    if stable['draft']:
        api.call('PATCH', f"releases/{stable['id']}", fields(m, False))
    # An already published stable is never edited or re-uploaded on retry.
    latest = api.call('GET', 'releases/latest')
    if latest.get('id') != stable['id'] or latest.get('draft') or latest.get('prerelease') or latest.get('tag_name') != tag:
        raise ValueError('Stable latest postcondition failed; existing bytes were not replaced')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['download', 'verify', 'publish'])
    parser.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args()
    try:
        env = os.environ
        authorization(env)
        root = Path(__file__).resolve().parent.parent
        identity = historical_identity(root, env['MOSAIC_SOURCE_SHA'], env['GITHUB_SHA'])
        api = GitHub()
        trusted_ci(api, env['GITHUB_SHA'])
        trusted_ci(api, env['MOSAIC_SOURCE_SHA'], require_tip=False)
        m, inventory = source_assets(api, env['MOSAIC_BUILD'], env['MOSAIC_SOURCE_SHA'], env['MOSAIC_APK_SHA256'])
        validate_original_source(api, m['source'], identity)
        directory = args.directory
        if args.mode == 'download':
            directory.mkdir(parents=True, exist_ok=False)
            for name, item in inventory.items():
                data = download_asset(item['id'])
                check_asset(item, name, data)
                if name == MANIFEST_NAME and data != canonical(m):
                    raise ValueError('Downloaded manifest differs from tag ledger')
                (directory / name).write_bytes(data)
            (directory / 'provenance.json').write_bytes(canonical(m['source']))
        else:
            if (directory / MANIFEST_NAME).read_bytes() != canonical(m):
                raise ValueError('Transferred manifest mismatch')
            apk = (directory / APK_NAME).read_bytes()
            for name, item in inventory.items():
                check_asset(item, name, (directory / name).read_bytes())
            acceptance = json.loads((directory / 'verification.json').read_text())
            verify_manifest(m, apk, acceptance, identity, json.loads((root / 'scripts/mosaic-signing.json').read_text()))
            if args.mode == 'publish':
                promote(api, m, apk)
                append_summary(publication_summary(m, 'promote', env), env)
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
