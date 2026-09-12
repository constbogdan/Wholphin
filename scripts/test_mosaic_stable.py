"""Offline stable byte-promotion and workflow boundary fixtures; no network or keys."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import mosaic_stable as stable
from mosaic_development_release import (
    CI_JOB,
    CI_WORKFLOW,
    EPOCH,
    LEGACY_DEVELOPMENT_WORKFLOW,
    canonical,
    digest,
    historical_identity,
    publish,
    trusted_ci,
    validate_original_source,
)
from test_mosaic_development_release import FakeGitHub
import test_mosaic_development_release as development_tests

ROOT = Path(__file__).resolve().parent.parent


class StableGitHub(FakeGitHub):
    def pages(self, path, key=None):
        result = super().pages(path, key)
        if path.endswith('/assets'):
            release = self.releases[int(path.split('/')[1])]
            for item in result:
                item['browser_download_url'] = (
                    f'https://github.com/{stable.REPOSITORY}/releases/download/'
                    f"{release['tag_name']}/{item['name']}"
                )
        return result

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

    def stable_env(self, **changed):
        return {
            'GITHUB_ACTIONS': 'true',
            'GITHUB_REPOSITORY': stable.REPOSITORY,
            'GITHUB_REF': 'refs/heads/main',
            'GITHUB_REF_PROTECTED': 'true',
            'GITHUB_EVENT_NAME': 'workflow_dispatch',
            'GITHUB_SHA': 'b' * 40,
            'GITHUB_WORKFLOW_REF': f'{stable.REPOSITORY}/{stable.WORKFLOW}@refs/heads/main',
            **changed,
        }

    def downloaded_asset(self, asset_id):
        item = self.api.uploads[asset_id]
        return self.apk if item['name'] == stable.APK_NAME else canonical(self.m)

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

    def test_current_development_derives_former_inputs_from_rolling_and_immutable_state(self):
        manifest, inventory, evidence = stable.current_development_candidate(self.api)
        self.assertEqual(self.m, manifest)
        self.assertEqual('downstream-build-5', manifest['immutableIdentity'])
        self.assertEqual(self.identity['sourceSha'], manifest['sourceSha'])
        self.assertEqual(self.identity['sourceTree'], manifest['sourceTree'])
        self.assertEqual(digest(self.apk), manifest['signedApkSha256'])
        self.assertEqual({'Wholphin-release.apk', 'mosaic-release.json'}, set(inventory))
        self.assertEqual(1, evidence['immutableReleaseId'])
        self.assertEqual(2, evidence['rollingReleaseId'])
        self.assertEqual(
            f'https://github.com/{stable.REPOSITORY}/releases/download/'
            'downstream-build-5/Wholphin-release.apk',
            evidence['apkUrl'],
        )

    def test_prepare_records_exact_candidate_and_compact_summary_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / 'stable'
            output = Path(tmp) / 'output'
            env = self.stable_env(GITHUB_OUTPUT=str(output))
            with patch.object(stable, 'trusted_ci'), \
                    patch.object(stable, 'historical_identity', return_value=self.identity), \
                    patch.object(stable, 'validate_original_source'), \
                    patch.object(stable, 'download_asset', side_effect=self.downloaded_asset):
                evidence = stable.prepare(self.api, ROOT, env, directory)
            recorded = json.loads((directory / stable.EVIDENCE_NAME).read_text())
            self.assertEqual(evidence, recorded)
            self.assertEqual(env['GITHUB_SHA'], recorded['toolingSha'])
            self.assertEqual('downstream-build-5', recorded['immutableIdentity'])
            self.assertEqual(self.identity['sourceSha'], recorded['sourceSha'])
            self.assertEqual(self.identity['sourceTree'], recorded['sourceTree'])
            self.assertEqual(digest(self.apk), recorded['signedApkSha256'])
            self.assertEqual(self.m['buildRunId'], recorded['buildRunId'])
            self.assertEqual(self.m['buildRunAttempt'], recorded['buildRunAttempt'])
            outputs = output.read_text()
            self.assertIn('version=v1.0.5\n', outputs)
            self.assertIn('build=downstream-build-5\n', outputs)
            self.assertIn(f"apk_url={recorded['apkUrl']}\n", outputs)

    def prepared_directory(self, root):
        directory = root / 'stable'
        with patch.object(stable, 'trusted_ci'), \
                patch.object(stable, 'historical_identity', return_value=self.identity), \
                patch.object(stable, 'validate_original_source'), \
                patch.object(stable, 'download_asset', side_effect=self.downloaded_asset):
            stable.prepare(self.api, ROOT, self.stable_env(), directory)
        (directory / 'verification.json').write_text(json.dumps(self.record))
        return directory

    def test_release_reauthenticates_candidate_after_approval_before_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = self.prepared_directory(Path(tmp))
            rolling = next(r for r in self.api.releases.values() if r['tag_name'] == 'develop')
            rolling['name'] = 'v1.0.6'
            mutations = len([call for call in self.api.calls if call[0] in ('POST', 'PATCH', 'DELETE')])
            with patch.object(stable, 'trusted_ci'), \
                    patch.object(stable, 'historical_identity', return_value=self.identity), \
                    self.assertRaises(ValueError):
                stable.publish_prepared(self.api, ROOT, self.stable_env(), directory)
            self.assertEqual(
                mutations,
                len([call for call in self.api.calls if call[0] in ('POST', 'PATCH', 'DELETE')]),
            )

    def test_release_refuses_stale_protected_main_before_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = self.prepared_directory(Path(tmp))
            mutations = len([call for call in self.api.calls if call[0] in ('POST', 'PATCH', 'DELETE')])
            with patch.object(stable, 'trusted_ci', side_effect=ValueError('stale main')), \
                    self.assertRaises(ValueError):
                stable.publish_prepared(self.api, ROOT, self.stable_env(), directory)
            self.assertEqual(
                mutations,
                len([call for call in self.api.calls if call[0] in ('POST', 'PATCH', 'DELETE')]),
            )

    def test_prepared_candidate_promotes_exact_bytes_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = self.prepared_directory(Path(tmp))
            with patch.object(stable, 'trusted_ci'), \
                    patch.object(stable, 'historical_identity', return_value=self.identity):
                stable.publish_prepared(self.api, ROOT, self.stable_env(), directory)
                latest = self.api.call('GET', 'releases/latest')
                stable_assets = self.api.pages(f"releases/{latest['id']}/assets")
                self.assertEqual('mosaic-v1.0.5', latest['tag_name'])
                self.assertEqual(
                    'sha256:' + digest(self.apk),
                    next(item for item in stable_assets if item['name'] == stable.APK_NAME)['digest'],
                )
                count = len(self.api.calls)
                stable.publish_prepared(self.api, ROOT, self.stable_env(), directory)
            self.assertTrue(all(method == 'GET' for method, _, _ in self.api.calls[count:]))

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

    def test_historical_identity_reads_git_objects_without_checkout(self):
        execution = 'e' * 40
        source = self.identity['sourceSha']
        chain = [execution, source, '1' * 40, '2' * 40, '3' * 40, '4' * 40, EPOCH]
        with patch('mosaic_development_release.git',
                   side_effect=['false', execution, '', '\n'.join(chain), self.identity['sourceTree'],
                                str(self.identity['buildTime'] // 1000)]) as git:
            result = historical_identity(ROOT, source, execution)
        self.assertEqual(5, result['versionCode'])
        self.assertEqual(source, result['sourceSha'])
        self.assertEqual(self.identity['sourceTree'], result['sourceTree'])
        self.assertTrue(result['publication'])
        self.assertFalse(result['dirty'])
        self.assertFalse(any('checkout' in call.args or 'worktree' in call.args
                             for call in git.call_args_list))

    def test_stable_authenticates_current_and_historical_development_producers(self):
        record = dict(self.identity, apkSha256='f' * 64, runId='123', runAttempt='1')
        job = dict(name=CI_JOB, status='completed', conclusion='success')
        run = dict(path=CI_WORKFLOW, event='push', conclusion='success', head_branch='main',
                   head_sha=self.identity['sourceSha'], status='completed',
                   repository=dict(full_name=stable.REPOSITORY),
                   head_repository=dict(full_name=stable.REPOSITORY))
        api = Mock()
        api.call.return_value = run
        api.pages.return_value = [job]
        self.assertEqual(CI_WORKFLOW, validate_original_source(api, record, self.identity))

        api.call.return_value = dict(run, path=LEGACY_DEVELOPMENT_WORKFLOW,
                                     event='workflow_dispatch')
        api.pages.return_value = [dict(job, name='build')]
        self.assertEqual(LEGACY_DEVELOPMENT_WORKFLOW,
                         validate_original_source(api, record, self.identity))
        for changed in (dict(run, head_sha='0' * 40), dict(run, path='.github/workflows/other.yml')):
            api.call.return_value = changed
            with self.assertRaises(ValueError):
                validate_original_source(api, record, self.identity)

    def test_stable_ci_trust_requires_protected_main_exact_run_and_full_job(self):
        api = Mock()
        branch = dict(protected=True, commit=dict(sha='a' * 40))
        run = dict(id=100, run_attempt=2, head_sha='a' * 40, head_branch='main', event='push',
                   workflow_id=42, head_repository=dict(full_name=stable.REPOSITORY),
                   status='completed', conclusion='success')
        job = dict(name=CI_JOB, status='completed', conclusion='success', head_sha='a' * 40)
        api.call.side_effect = [branch, dict(id=42)]
        api.pages.side_effect = [[run], [job]]
        self.assertEqual('2', trusted_ci(api, 'a' * 40)['runAttempt'])
        for field, value in [('head_branch', 'feature'), ('event', 'pull_request'),
                             ('head_sha', 'f' * 40), ('status', 'in_progress'),
                             ('conclusion', 'failure')]:
            api.call.side_effect = [branch, dict(id=42)]
            api.pages.side_effect = [[dict(run, **{field: value})], [job]]
            with self.subTest(field=field), self.assertRaises(ValueError):
                trusted_ci(api, 'a' * 40)

    def test_zero_input_authorization_and_workflow_isolation(self):
        env = self.stable_env()
        self.assertEqual(env['GITHUB_SHA'], stable.authorization(env))
        for field, value in [('GITHUB_EVENT_NAME', 'pull_request'), ('GITHUB_REF', 'refs/heads/feature'),
                             ('GITHUB_REPOSITORY', 'fork/Wholphin'), ('GITHUB_SHA', 'not-a-sha'),
                             ('GITHUB_WORKFLOW_REF', 'other')]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                stable.authorization(dict(env, **{field: value}))
        workflow = (ROOT / stable.WORKFLOW).read_text(encoding='utf-8')
        verify, publisher = workflow.split('\n  publish:\n')
        for forbidden in ('gradlew', 'mosaic-sign-apk', 'secrets.', 'SYNC_BOT', 'push:', 'pull_request:', 'schedule:'):
            self.assertNotIn(forbidden, workflow)
        self.assertIn('name: Prepare', verify)
        self.assertNotIn('environment:', verify)
        self.assertIn('name: Release', publisher)
        self.assertIn('environment: release-promote', publisher)
        self.assertNotIn('contents: write', verify)
        self.assertIn('contents: write', publisher)
        self.assertIn('verify_mosaic_apk.py', verify)
        self.assertIn('artifact-ids: ${{ needs.verify.outputs.artifact_id }}', publisher)
        self.assertIn('digest-mismatch: error', publisher)
        self.assertIn('workflow_dispatch:\n', workflow)
        self.assertNotIn('inputs:', workflow)
        self.assertNotIn('inputs.', workflow)
        self.assertNotIn('MOSAIC_EXPECTED_SHA', workflow)
        self.assertNotIn('MOSAIC_BUILD', workflow)
        self.assertNotIn('MOSAIC_SOURCE_SHA', workflow)
        self.assertNotIn('MOSAIC_APK_SHA256', workflow)
        self.assertIn('Ready to release: [%s](%s) · ✓ Authenticated', verify)
        self.assertIn('environment: release-promote', publisher)
        self.assertIn('Reauthenticate current Development', publisher)


if __name__ == '__main__':
    unittest.main()
