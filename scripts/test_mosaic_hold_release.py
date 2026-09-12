"""Offline Hold Release authentication, mutation and workflow-boundary fixtures."""

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import mosaic_hold_release as hold
import mosaic_stable as stable
from mosaic_development_release import canonical, publish
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
            hold.get_release(self.api, ROOT, self.env, self.directory)
        (self.directory / 'verification.json').write_bytes(canonical(self.record))

    def perform_hold(self):
        trusted, history, producer, download = self.trusted()
        with trusted, history, producer, download:
            hold.hold(self.api, ROOT, self.env, self.directory)

    def add_previous_stable(self):
        rid = max(self.api.releases) + 1
        self.api.releases[rid] = {
            'id': rid,
            'tag_name': 'mosaic-v1.0.4',
            'name': 'v1.0.4',
            'draft': False,
            'prerelease': False,
            'make_latest': 'true',
            'immutable': False,
        }
        return self.api.releases[rid]

    def test_valid_current_stable_can_be_held_without_changing_tag_or_assets(self):
        self.prepare()
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
        replacement = self.add_previous_stable()
        replacement.update(tag_name='mosaic-v1.0.6', name='v1.0.6')
        self.current['make_latest'] = 'false'
        count = len(self.api.calls)
        with patch.object(hold, 'trusted_ci'), patch.object(
            hold, 'historical_identity', return_value=self.identity,
        ), self.assertRaisesRegex(ValueError, 'changed after authentication'):
            hold.hold(self.api, ROOT, self.env, self.directory)
        self.assertTrue(all(method == 'GET' for method, _, _ in self.api.calls[count:]))

    def test_confirm_accepts_fallback_or_none_and_rejects_held_latest(self):
        self.prepare()
        self.perform_hold()
        self.assertEqual('none', hold.confirm(self.api, self.env, self.directory))
        previous = self.add_previous_stable()
        self.assertEqual('v1.0.4', hold.confirm(self.api, self.env, self.directory))
        self.api.latest_override = self.current['id']
        with self.assertRaisesRegex(ValueError, 'still advertised'):
            hold.confirm(self.api, self.env, self.directory)
        self.api.latest_override = None
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
        get_job, remainder = workflow.split('\n  hold:\n', 1)
        mutation, confirmation = remainder.split('\n  confirm:\n', 1)
        self.assertIn('workflow_dispatch:\n', workflow)
        self.assertNotIn('inputs:', workflow)
        self.assertIn('group: mosaic-development-release', workflow)
        self.assertNotIn('contents: write', get_job)
        self.assertIn('contents: write', mutation)
        self.assertIn('environment: release-hold', mutation)
        self.assertNotIn('environment:', get_job)
        self.assertNotIn('environment:', confirmation)
        self.assertIn('needs: [get-release, hold]', confirmation)
        self.assertEqual(2, workflow.count('digest-mismatch: error'))
        for forbidden in ('gradlew', 'mosaic-sign-apk', 'secrets.', 'git/refs/tags/develop', 'DELETE'):
            self.assertNotIn(forbidden, workflow)
        self.assertEqual(1, workflow.count('mosaic_hold_release.py hold'))
        self.assertEqual(1, workflow.count('mosaic_hold_release.py confirm'))


if __name__ == '__main__':
    unittest.main()
