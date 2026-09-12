"""Human delivery presentation; never authorizes, builds, signs or publishes."""
import json
import os
from pathlib import Path


REPOSITORY_URL = 'https://github.com/constbogdan/Wholphin'


def append_summary(text, env=None):
    env = os.environ if env is None else env
    if env.get('GITHUB_STEP_SUMMARY'):
        with Path(env['GITHUB_STEP_SUMMARY']).open('a', encoding='utf-8') as output:
            output.write(text.rstrip() + '\n')


def release_body(m, channel, *, archive=False):
    version, build, source = m['versionName'], m['immutableIdentity'], m['sourceSha']
    title = f'Mosaic v{version} — {channel}'
    if archive:
        title += f" Build {m['versionCode']}"
        purpose = f'Immutable archive/provenance record for {build}.'
        guidance = 'Use the rolling Development channel for normal updates.'
    elif channel == 'Stable':
        purpose = f'Stable Mosaic release.\n\nPromoted unchanged from {build}.'
        guidance = 'Choose Stable in the app update channel for stable updates.'
    else:
        purpose = 'Current rolling Development release.'
        guidance = 'Development preview; may contain recently merged changes. Choose Development in the app update channel.'
    tag = 'mosaic-v' + version if channel == 'Stable' else build if archive else 'develop'
    return (f'# {title}\n\n{purpose}\n\nVersion: v{version}\n\nBuild: {build}\n\n'
            f'Source: [{source}]({REPOSITORY_URL}/commit/{source})\n\n'
            f"APK SHA-256: {m['signedApkSha256']}\n\n{guidance}\n\n"
            f'[Download the Release APK]({REPOSITORY_URL}/releases/download/{tag}/Wholphin-release.apk) '
            '(Wholphin-release.apk is the compatible Mosaic installer). Install over your existing Mosaic Release installation.\n\n'
            'Public provenance: mosaic-release.json.\n')


def publication_summary(m, operation, env, ci=None):
    version, build, source = m['versionName'], m['immutableIdentity'], m['sourceSha']
    if operation == 'promote':
        heading = f'Promoted · Mosaic v{version}'
        details = [f'From: {build}', 'Channel: Stable', 'Exact Development bytes reused',
                   f'Stable release: {REPOSITORY_URL}/releases/tag/mosaic-v{version}']
    elif operation == 'publish':
        heading = f'Published · Mosaic v{version}'
        details = ['Channel: Development', f'Build: {build}',
                   f'Development release: {REPOSITORY_URL}/releases/tag/develop']
    else:
        raise ValueError('Unknown presentation operation')
    details += [f'Source: [{source}]({REPOSITORY_URL}/commit/{source})',
                f"APK SHA-256: {m['signedApkSha256']}",
                f'Immutable build: {REPOSITORY_URL}/releases/tag/{build}',
                f"Original build run: {m['buildRunId']} / attempt {m['buildRunAttempt']}"]
    if ci:
        details.append('Authoritative CI: ' + json.dumps(ci, sort_keys=True))
    return '## ' + heading + '\n\n' + '\n\n'.join(details) + '\n'
