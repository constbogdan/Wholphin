"""Offline Hold Release authentication, mutation and workflow-boundary fixtures."""

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import mosaic_hold_release as hold
import mosaic_stable as stable
from mosaic_development_release import assets, canonical, publish, release_fields
from test_mosaic_development_release import PublisherTests
from test_mosaic_stable import StableGitHub


ROOT = Path(__file__).resolve().parent.parent


class HoldGitHub(StableGitHub):
    def __init__(self):
        super().__init__()
        self.latest_override = None

    def call(self, method, path, data=None, missing=False, upload=False):
        if method == 'GET' and path == 'releases/latest':
            self.calls.append((method, path, copy.deepcopy(data)))
            if self.latest_override is not None:
                return self.releases.get(self.latest_override)
            candidates = [
                release for release in self.releases.values()
                if not release.get('draft') and not release.get('prerelease')
            ]
            if not candidates:
                return None if missing else (_ for _ in ()).throw(ValueError('missing latest'))
            preferred = [release for release in candidates if release.get('make_latest') == 'true']
            return max(preferred or candidates, key=lambda release: hold.stable_number(release) or -1)
        if method == 'GET' and path.startswith('releases/') and path.count('/') == 1:
            self.calls.append((method, path, copy.deepcopy(data)))
            return self.releases.get(int(path.split('/')[1]))
        return super().call(method, path, data, missing, upload)


class HoldReleaseTests(unittest.TestCase):
    def setUp(self):
        fixture = PublisherTests()
        fixture.setUp()
        self.m = fixture.m
        self.apk = fixture.apk
        self.record = fixture.record
        self.identity = fixture.identity
        self.api = HoldGitHub()
        publish(self.api, self.m, self.apk)
        stable.promote(self.api, self.m, self.apk)
        self.current = self.api.call('GET', 'releases/latest')
        self.add_asset_urls()
        self.env = {
            'GITHUB_ACTIONS': 'true',
            'GITHUB_REPOSITORY': hold.REPOSITORY,
            'GITHUB_REF': 'refs/heads/main',
            'GITHUB_REF_PROTECTED': 'true',
            'GITHUB_EVENT_NAME': 'workflow_dispatch',
            'GITHUB_SHA': 'f' * 40,
            'GITHUB_WORKFLOW_REF': f'{hold.REPOSITORY}/{hold.WORKFLOW}@refs/heads/main',
        }
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name) / 'hold'

    def tearDown(self):
        self.temp.cleanup()

    def content(self, asset_id):
        item = self.api.uploads[asset_id]
        return self.apk if item['name'] == hold.APK_NAME else canonical(self.m)

    def add_asset_urls(self):
        for item in self.api.uploads.values():
            release = self.api.releases[item['release']]
            item['browser_download_url'] = (
                f"https://github.com/{hold.REPOSITORY}/releases/download/"
                f"{release['tag_name']}/{item['name']}"
            )

    def manifest(self, number):
        result = copy.deepcopy(self.m)
        source_sha = format(number, 'x') * 40
        source_sha = source_sha[:40]
        result.update(
            versionCode=number,
            versionName=f'1.0.{number}',
            sourceSha=source_sha,
            sourceTree=('e' + format(number, 'x') * 39)[:40],
            immutableIdentity=f'downstream-build-{number}',
        )
        result['source'].update(
            versionCode=number,
            versionName=f'1.0.{number}',
            sourceSha=result['sourceSha'],
            sourceTree=result['sourceTree'],
        )
        return result

    def trusted(self):
        return (
            patch.object(hold, 'trusted_ci'),
            patch.object(hold, 'historical_identity', return_value=self.identity),
            patch.object(hold, 'validate_original_source'),
            patch.object(hold, 'download_asset', side_effect=self.content),
        )

    def prepare(self):
        trusted, history, producer, download = self.trusted()
        with trusted, history, producer, download:
            evidence = hold.get_release(self.api, ROOT, self.env, self.directory)
        (self.directory / 'verification.json').write_bytes(canonical(self.record))
        return evidence

    def perform_hold(self):
        trusted, history, producer, download = self.trusted()
        with trusted, history, producer, download:
            return hold.hold(self.api, ROOT, self.env, self.directory)

    def add_previous_stable(self):
        previous = self.manifest(4)
        development_tag = previous['immutableIdentity']
        development_object = self.api.call('POST', 'git/tags', {
            'tag': development_tag,
            'message': canonical(previous).decode(),
            'object': previous['sourceSha'],
            'type': 'commit',
        })
        self.api.call('POST', 'git/refs', {
            'ref': 'refs/tags/' + development_tag,
            'sha': development_object['sha'],
        })
        development = self.api.call('POST', 'releases', {
            'tag_name': development_tag,
            'target_commitish': previous['sourceSha'],
            **release_fields(previous, False, archive=True),
        })
        assets(self.api, development, {
            hold.APK_NAME: self.apk,
            hold.MANIFEST_NAME: canonical(previous),
        }, allow_upload=True)

        stable_tag = 'mosaic-v' + previous['versionName']
        stable_object = self.api.call('POST', 'git/tags', {
            'tag': stable_tag,
            'message': canonical(previous).decode(),
            'object': previous['sourceSha'],
            'type': 'commit',
        })
        self.api.call('POST', 'git/refs', {
            'ref': 'refs/tags/' + stable_tag,
            'sha': stable_object['sha'],
        })
        prior = self.api.call('POST', 'releases', {
            'tag_name': stable_tag,
            'target_commitish': previous['sourceSha'],
            **stable.fields(previous, False),
        })
        assets(self.api, prior, {
            hold.APK_NAME: self.apk,
            hold.MANIFEST_NAME: canonical(previous),
        }, allow_upload=True)
        self.add_asset_urls()
        return prior

    def add_newer_stable(self):
        newer = self.manifest(6)
        publish(self.api, newer, self.apk)
        stable.promote(self.api, newer, self.apk)
        self.add_asset_urls()
        return self.api.call('GET', 'releases/latest')

    def test_valid_current_stable_can_be_held_without_changing_tag_or_assets(self):
        evidence = self.prepare()
        ref_before = copy.deepcopy(self.api.refs[self.current['tag_name']])
        assets_before = copy.deepcopy(self.api.pages(f"releases/{self.current['id']}/assets"))
        self.perform_hold()
        held = self.api.releases[self.current['id']]
        self.assertTrue(held['prerelease'])
        self.assertFalse(held['draft'])
        self.assertEqual('false', held['make_latest'])
        self.assertEqual(ref_before, self.api.refs[self.current['tag_name']])
        self.assertEqual(assets_before, self.api.pages(f"releases/{self.current['id']}/assets"))
        patches = [call for call in self.api.calls if call[0] == 'PATCH']
        self.assertEqual(('PATCH', f"releases/{self.current['id']}", {
            'prerelease': True, 'make_latest': 'false',
        }), patches[-1])
        self.assertEqual(
            next(item['browser_download_url'] for item in assets_before
                 if item['name'] == hold.APK_NAME),
            evidence['apkUrl'],
        )

    def test_no_latest_refuses_without_mutation(self):
        self.current['prerelease'] = True
        count = len(self.api.calls)
        trusted, history, producer, download = self.trusted()
        with trusted, history, producer, download, self.assertRaisesRegex(ValueError, 'No Stable'):
            hold.get_release(self.api, ROOT, self.env, self.directory)
        self.assertTrue(all(method == 'GET' for method, _, _ in self.api.calls[count:]))

    def test_malformed_current_release_refuses(self):
        self.current['tag_name'] = 'v1.0.5'
        trusted, history, producer, download = self.trusted()
        with trusted, history, producer, download, self.assertRaisesRegex(ValueError, 'malformed'):
            hold.get_release(self.api, ROOT, self.env, self.directory)

    def test_immutable_current_release_refuses_before_mutation(self):
        self.current['immutable'] = True
        count = len(self.api.calls)
        trusted, history, producer, download = self.trusted()
        with trusted, history, producer, download, self.assertRaisesRegex(ValueError, 'published'):
            hold.get_release(self.api, ROOT, self.env, self.directory)
        self.assertFalse(any(method == 'PATCH' for method, _, _ in self.api.calls[count:]))

    def test_missing_or_ambiguous_assets_refuse(self):
        stable_assets = [
            asset for asset in self.api.uploads.values() if asset['release'] == self.current['id']
        ]
        del self.api.uploads[stable_assets[0]['id']]
        trusted, history, producer, download = self.trusted()
        with trusted, history, producer, download, self.assertRaisesRegex(ValueError, 'asset'):
            hold.get_release(self.api, ROOT, self.env, self.directory)

        duplicate = copy.deepcopy(stable_assets[1])
        duplicate['id'] = max(self.api.uploads) + 1
        self.api.uploads[duplicate['id']] = duplicate
        trusted, history, producer, download = self.trusted()
        with trusted, history, producer, download, self.assertRaisesRegex(ValueError, 'asset'):
            hold.get_release(self.api, ROOT, self.env, self.directory)

    def test_digest_provenance_and_signer_mismatches_refuse(self):
        stable_apk = next(
            asset for asset in self.api.uploads.values()
            if asset['release'] == self.current['id'] and asset['name'] == hold.APK_NAME
        )
        stable_apk['digest'] = 'sha256:' + '0' * 64
        trusted, history, producer, download = self.trusted()
        with trusted, history, producer, download, self.assertRaisesRegex(ValueError, 'differ'):
            hold.get_release(self.api, ROOT, self.env, self.directory)

        stable_apk['digest'] = 'sha256:' + self.m['signedApkSha256']
        self.prepare()
        bad = dict(self.record, certificateSha256='0' * 64)
        (self.directory / 'verification.json').write_bytes(canonical(bad))
        trusted, history, producer, download = self.trusted()
        with trusted, history, producer, download, self.assertRaisesRegex(ValueError, 'certificate'):
            hold.hold(self.api, ROOT, self.env, self.directory)

    def test_foreign_or_changed_provenance_refuses(self):
        annotation = self.api.tags[self.api.refs[self.current['tag_name']]['object']['sha']]
        annotation['message'] = canonical(dict(self.m, sourceSha='0' * 40)).decode()
        trusted, history, producer, download = self.trusted()
        with trusted, history, producer, download, self.assertRaises(ValueError):
            hold.get_release(self.api, ROOT, self.env, self.directory)

    def test_latest_change_between_get_and_hold_refuses_without_mutation(self):
        self.prepare()
        replacement = self.add_newer_stable()
        count = len(self.api.calls)
        with patch.object(hold, 'trusted_ci'), patch.object(
            hold, 'historical_identity', return_value=self.identity,
        ), self.assertRaisesRegex(ValueError, 'changed after authentication'):
            hold.hold(self.api, ROOT, self.env, self.directory)
        self.assertTrue(all(method == 'GET' for method, _, _ in self.api.calls[count:]))

    def test_hold_confirms_no_current_stable(self):
        self.prepare()
        self.assertEqual('none', self.perform_hold())

    def test_hold_confirms_authenticated_fallback_with_exact_apk_url(self):
        previous = self.add_previous_stable()
        self.prepare()
        with tempfile.TemporaryDirectory() as output_directory:
            output = Path(output_directory) / 'github-output'
            env = dict(self.env, GITHUB_OUTPUT=str(output))
            trusted, history, producer, download = self.trusted()
            with trusted, history, producer, download:
                self.assertEqual('v1.0.4', hold.hold(self.api, ROOT, env, self.directory))
            values = dict(line.split('=', 1) for line in output.read_text().splitlines())
        expected_url = next(
            item['browser_download_url'] for item in self.api.uploads.values()
            if item['release'] == previous['id'] and item['name'] == hold.APK_NAME
        )
        self.assertEqual(expected_url, values['current_url'])

    def test_hold_fails_when_final_confirmation_still_returns_held_release(self):
        self.prepare()
        self.api.latest_override = self.current['id']
        with self.assertRaisesRegex(ValueError, 'still advertised'):
            self.perform_hold()
        self.api.latest_override = None

    def test_confirmation_helper_accepts_fallback(self):
        self.prepare()
        self.perform_hold()
        previous = self.add_previous_stable()
        self.assertEqual('v1.0.4', hold.confirm(self.api, self.env, self.directory))
        self.assertEqual(previous['id'], self.api.call('GET', 'releases/latest')['id'])

    def test_second_run_cannot_cascade_to_previous_stable(self):
        self.prepare()
        self.perform_hold()
        previous = self.add_previous_stable()
        other = Path(self.temp.name) / 'second'
        count = len(self.api.calls)
        trusted, history, producer, download = self.trusted()
        with trusted, history, producer, download, self.assertRaisesRegex(ValueError, 'cascading hold'):
            hold.get_release(self.api, ROOT, self.env, other)
        self.assertFalse(previous['prerelease'])
        self.assertTrue(all(method == 'GET' for method, _, _ in self.api.calls[count:]))

    def test_workflow_is_zero_input_and_has_narrow_write_boundary(self):
        workflow = (ROOT / hold.WORKFLOW).read_text(encoding='utf-8')
        prepare, mutation = workflow.split('\n  hold:\n', 1)
        self.assertIn('workflow_dispatch:\n', workflow)
        self.assertNotIn('inputs:', workflow)
        self.assertIn('group: mosaic-development-release', workflow)
        self.assertIn('name: Prepare', prepare)
        self.assertNotIn('contents: write', prepare)
        self.assertIn('contents: write', mutation)
        self.assertIn('environment: release-hold', mutation)
        self.assertNotIn('environment:', prepare)
        self.assertNotIn('\n  confirm:\n', workflow)
        self.assertEqual(1, workflow.count('digest-mismatch: error'))
        self.assertIn('Ready to hold: [%s](%s) · ✓ Authenticated', prepare)
        self.assertIn('Held: ✕ [%s](%s) → ✓ [%s](%s)', mutation)
        self.assertIn('Held: ✕ [%s](%s) → No release available', mutation)
        for forbidden in ('gradlew', 'mosaic-sign-apk', 'secrets.', 'git/refs/tags/develop', 'DELETE'):
            self.assertNotIn(forbidden, workflow)
        self.assertEqual(1, workflow.count('mosaic_hold_release.py hold'))
        self.assertNotIn('mosaic_hold_release.py confirm', workflow)


if __name__ == '__main__':
    unittest.main()
