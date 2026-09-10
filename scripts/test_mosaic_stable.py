"""Offline stable byte-promotion and workflow boundary fixtures; no network or keys."""
import copy
import unittest
from pathlib import Path
from unittest.mock import patch

import mosaic_stable as stable
from mosaic_development_release import publish, canonical
from test_mosaic_development_release import FakeGitHub
import test_mosaic_development_release as development_tests

ROOT = Path(__file__).resolve().parent.parent


class StableGitHub(FakeGitHub):
    def call(self, method, path, data=None, missing=False, upload=False):
        if method == 'GET' and path == 'releases/latest':
            self.calls.append((method, path, data))
            return next(r for r in self.releases.values() if not r['draft'] and not r['prerelease'] and r['make_latest'] == 'true')
        if method == 'PATCH' and path.startswith('releases/') and data.get('make_latest') == 'true':
            for r in self.releases.values():
                r['make_latest'] = 'false'
        return super().call(method, path, data, missing, upload)


class StableTests(unittest.TestCase):
    def setUp(self):
        fixture = development_tests.PublisherTests()
        fixture.setUp()
        self.m, self.apk, self.record, self.identity, self.policy = fixture.m, fixture.apk, fixture.record, fixture.identity, fixture.policy
        self.api = StableGitHub()
        publish(self.api, self.m, self.apk)

    def test_source_requires_exact_build_source_hash_and_annotated_ledger(self):
        m, items = stable.source_assets(self.api, 'downstream-build-5', self.m['sourceSha'], self.m['signedApkSha256'])
        self.assertEqual(m, self.m)
        self.assertEqual(set(items), {'Wholphin-release.apk', 'mosaic-release.json'})
        for source, digest in [('f' * 40, self.m['signedApkSha256']), (self.m['sourceSha'], '0' * 64)]:
            with self.assertRaises(ValueError):
                stable.source_assets(self.api, 'downstream-build-5', source, digest)
        self.api.tags['1' * 40]['message'] = '{}'
        with self.assertRaises((ValueError, KeyError)):
            stable.source_assets(self.api, 'downstream-build-5', self.m['sourceSha'], self.m['signedApkSha256'])

    def test_stable_exact_bytes_latest_and_idempotency_leave_develop_unchanged(self):
        develop = copy.deepcopy(next(r for r in self.api.releases.values() if r['tag_name'] == 'develop'))
        self.api.refs['v1.0.5'] = dict(object=dict(type='commit', sha='e' * 40))
        with patch.object(self.api, 'pages', wraps=self.api.pages) as pages:
            stable.promote(self.api, self.m, self.apk)
        self.assertEqual(1, sum(call.args[0] == 'releases' for call in pages.call_args_list))
        self.assertEqual(self.api.refs['v1.0.5']['object']['sha'], 'e' * 40)
        latest = self.api.call('GET', 'releases/latest')
        self.assertEqual(latest['tag_name'], 'mosaic-v1.0.5')
        self.assertEqual(latest['name'], 'v1.0.5')
        self.assertFalse(latest['prerelease'])
        self.assertEqual(self.api.releases[develop['id']], develop)
        source_assets = self.api.pages('releases/1/assets')
        stable_assets = self.api.pages(f"releases/{latest['id']}/assets")
        self.assertEqual({a['name']: a['digest'] for a in source_assets}, {a['name']: a['digest'] for a in stable_assets})
        count = len(self.api.calls)
        stable.promote(self.api, self.m, self.apk)
        self.assertTrue(all(method == 'GET' for method, _, _ in self.api.calls[count:]))

    def test_conflicting_stable_never_overwritten(self):
        stable.promote(self.api, self.m, self.apk)
        count = len(self.api.calls)
        with self.assertRaises(ValueError):
            stable.promote(self.api, dict(self.m, signedApkSha256='0' * 64), self.apk)
        self.assertTrue(all(method == 'GET' for method, _, _ in self.api.calls[count:]))
        latest = self.api.call('GET', 'releases/latest')
        next(a for a in self.api.uploads.values() if a['release'] == latest['id'])['digest'] = 'sha256:' + '0' * 64
        with self.assertRaises(ValueError):
            stable.promote(self.api, self.m, self.apk)

    def test_interrupted_stable_upload_retries_exact_existing_signed_input(self):
        self.api.fail_upload = True
        with self.assertRaises(ValueError):
            stable.promote(self.api, self.m, self.apk)
        self.assertIn('mosaic-v1.0.5', self.api.refs)
        self.api.fail_upload = False
        stable.promote(self.api, self.m, self.apk)
        self.assertFalse(self.api.call('GET', 'releases/latest')['draft'])

    def test_no_latest_rollback_or_unknown_stable_ownership(self):
        self.api.releases[99] = dict(id=99, tag_name='mosaic-v1.0.6', draft=False, prerelease=False)
        with self.assertRaises(ValueError):
            stable.promote(self.api, self.m, self.apk)
        self.api.releases[99]['tag_name'] = 'unrelated'
        with self.assertRaises(ValueError):
            stable.promote(self.api, self.m, self.apk)

    def test_verified_manifest_binds_package_version_source_hash_and_signer(self):
        stable.verify_manifest(self.m, self.apk, self.record, self.identity, self.policy)
        for field, value in [('applicationId', 'other'), ('certificateSha256', '0' * 64), ('signedApkSha256', '0' * 64)]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                stable.verify_manifest(self.m, self.apk, dict(self.record, **{field: value}), self.identity, self.policy)
        for field, value in [('versionCode', 6), ('sourceTree', 'f' * 40), ('upstreamBaseline', 'f' * 40)]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                stable.verify_manifest(dict(self.m, **{field: value}), self.apk, self.record, self.identity, self.policy)
        with self.assertRaises(ValueError):
            stable.verify_manifest(self.m, self.apk + b'changed', self.record, self.identity, self.policy)

    def test_manual_authorization_and_workflow_isolation(self):
        env = dict(GITHUB_ACTIONS='true', GITHUB_REPOSITORY=stable.REPOSITORY, GITHUB_REF='refs/heads/main',
                   GITHUB_REF_PROTECTED='true', GITHUB_EVENT_NAME='workflow_dispatch', GITHUB_SHA='b' * 40,
                   MOSAIC_EXPECTED_SHA='b' * 40, MOSAIC_BUILD='downstream-build-5', MOSAIC_SOURCE_SHA='a' * 40,
                   MOSAIC_APK_SHA256='f' * 64, GITHUB_WORKFLOW_REF=f'{stable.REPOSITORY}/{stable.WORKFLOW}@refs/heads/main')
        stable.authorization(env)
        for field, value in [('GITHUB_EVENT_NAME', 'pull_request'), ('GITHUB_REF', 'refs/heads/feature'),
                             ('GITHUB_REPOSITORY', 'fork/Wholphin'), ('MOSAIC_BUILD', 'develop'),
                             ('MOSAIC_BUILD', 'downstream-build-0'), ('MOSAIC_EXPECTED_SHA', 'f' * 40), ('MOSAIC_APK_SHA256', '')]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                stable.authorization(dict(env, **{field: value}))
        workflow = (ROOT / stable.WORKFLOW).read_text()
        verify, publisher = workflow.split('\n  publish:\n')
        for forbidden in ('gradlew', 'mosaic-sign-apk', 'secrets.', 'environment:', 'SYNC_BOT', 'push:', 'pull_request:', 'schedule:'):
            self.assertNotIn(forbidden, workflow)
        self.assertNotIn('contents: write', verify)
        self.assertIn('contents: write', publisher)
        self.assertIn('verify_mosaic_apk.py', verify)
        self.assertIn('artifact-ids: ${{ needs.verify.outputs.artifact_id }}', publisher)
        self.assertIn('digest-mismatch: error', publisher)
        self.assertEqual(workflow.count('inputs.expected_sha == github.sha'), 2)


if __name__ == '__main__':
    unittest.main()
